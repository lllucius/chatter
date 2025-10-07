"""Modern workflow execution service.

This service provides the modern workflow execution system using the
new flexible architecture with support for all node types.
"""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage

from chatter.core.enhanced_memory_manager import EnhancedMemoryManager
from chatter.core.enhanced_tool_executor import EnhancedToolExecutor
from chatter.core.events import (
    EventCategory,
    EventPriority,
    UnifiedEvent,
)
from chatter.core.langgraph import workflow_manager
from chatter.core.monitoring import get_monitoring_service
from chatter.core.workflow_graph_builder import (
    create_simple_workflow_definition,
    create_workflow_definition_from_model,
)
from chatter.core.workflow_node_factory import WorkflowNodeContext
from chatter.models.base import generate_ulid
from chatter.models.conversation import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
)
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


def _log_workflow_debug_info(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    execution_type: str = "workflow",
    definition_name: str | None = None,
) -> None:
    """Log detailed debugging information about workflow shape and nodes prior to execution."""

    # Calculate workflow shape
    node_count = len(nodes)
    edge_count = len(edges)

    # Extract node types and their counts
    node_types = {}
    node_details = []

    for node in nodes:
        node_id = node.get("id", "unknown")
        node_type = node.get("type", "unknown")
        node_config = node.get("config", {})

        # Count node types
        node_types[node_type] = node_types.get(node_type, 0) + 1

        # Collect node details
        node_details.append(
            {
                "id": node_id,
                "type": node_type,
                "config_keys": (
                    list(node_config.keys())
                    if isinstance(node_config, dict)
                    else []
                ),
                "has_config": bool(node_config),
            }
        )

    # Extract edge information
    edge_details = []
    for edge in edges:
        edge_info = {
            "source": edge.get("source", "unknown"),
            "target": edge.get("target", "unknown"),
            "type": edge.get("type", "regular"),
            "has_condition": bool(edge.get("condition")),
        }
        if edge.get("condition"):
            edge_info["condition"] = edge["condition"]
        edge_details.append(edge_info)

    # Find entry points (nodes with no incoming edges)
    target_nodes = {edge.get("target") for edge in edges}
    entry_points = [
        node.get("id")
        for node in nodes
        if node.get("id") not in target_nodes
    ]

    # Find exit points (nodes with edges to END or no outgoing edges)
    source_nodes = {edge.get("source") for edge in edges}
    exit_points = []
    for edge in edges:
        if (
            edge.get("target") == "END"
            or edge.get("target") == "__end__"
        ):
            exit_points.append(edge.get("source"))
    # Also add nodes with no outgoing edges
    for node in nodes:
        node_id = node.get("id")
        if node_id not in source_nodes:
            exit_points.append(node_id)

    # Log comprehensive workflow information
    logger.info(
        f"Workflow execution starting - {execution_type} shape and configuration",
        execution_type=execution_type,
        definition_name=definition_name,
        workflow_shape={
            "node_count": node_count,
            "edge_count": edge_count,
            "node_types": node_types,
            "entry_points": entry_points,
            "exit_points": list(set(exit_points)),  # Remove duplicates
        },
        nodes=node_details,
        edges=edge_details,
    )


class WorkflowExecutionService:
    """Modern workflow execution service."""

    def __init__(
        self,
        llm_service: LLMService,
        message_service: MessageService,
        session,
    ):
        """Initialize the workflow execution service."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.session = session

        # Initialize enhanced components
        self.memory_manager = EnhancedMemoryManager()
        self.tool_executor = EnhancedToolExecutor()
        
        # Initialize new execution engine
        from chatter.core.workflow_execution_engine import ExecutionEngine
        self.execution_engine = ExecutionEngine(
            session=session,
            llm_service=llm_service,
        )

    def _extract_workflow_config_settings(
        self, chat_request: ChatRequest
    ) -> dict[str, Any]:
        """Extract and merge workflow configuration settings from ChatRequest.
        
        This method extracts settings from workflow_config if present and merges them
        with top-level request settings. The workflow_config settings take precedence.
        
        Args:
            chat_request: The chat request containing potential workflow_config
            
        Returns:
            Dictionary with extracted settings including:
            - enable_tools: Whether tools are enabled
            - allowed_tools: List of allowed tool names (if specified)
            - enable_retrieval: Whether retrieval is enabled
            - enable_memory: Whether memory is enabled
            - tool_config: Full tool configuration if present
        """
        settings = {
            'enable_tools': chat_request.enable_tools,
            'enable_retrieval': chat_request.enable_retrieval,
            'enable_memory': chat_request.enable_memory,
            'allowed_tools': None,
            'tool_config': None,
        }
        
        # Extract from workflow_config if present
        if chat_request.workflow_config:
            wf_config = chat_request.workflow_config
            
            # Extract tool configuration
            if 'tool_config' in wf_config:
                tool_config = wf_config['tool_config']
                settings['tool_config'] = tool_config
                
                # tool_config.enabled takes precedence over top-level enable_tools
                if 'enabled' in tool_config:
                    settings['enable_tools'] = tool_config['enabled']
                
                # Extract allowed_tools list
                if 'allowed_tools' in tool_config:
                    settings['allowed_tools'] = tool_config['allowed_tools']
            
            # Extract other configuration settings
            if 'enable_retrieval' in wf_config:
                settings['enable_retrieval'] = wf_config['enable_retrieval']
            
            if 'enable_memory' in wf_config:
                settings['enable_memory'] = wf_config['enable_memory']
        
        return settings

    async def execute_chat_workflow(
        self,
        user_id: str,
        request: ChatRequest,
    ) -> tuple[Conversation, Message]:
        """Execute chat workflow using the unified ExecutionEngine."""
        from chatter.schemas.execution import ExecutionRequest
        
        # Get or create conversation
        conversation = await self._get_or_create_conversation(
            user_id, request
        )
        
        # Convert ChatRequest to ExecutionRequest
        execution_request = ExecutionRequest(
            message=request.message,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt_override,
            enable_memory=request.enable_memory,
            enable_retrieval=request.enable_retrieval,
            enable_tools=request.enable_tools,
            streaming=False,
            memory_window=getattr(request, 'memory_window', 10),
            max_tool_calls=getattr(request, 'max_tool_calls', 10),
            document_ids=request.document_ids,
            conversation_id=conversation.id,
            workflow_config=request.workflow_config or {},
        )
        
        # Execute using the unified engine
        result = await self.execution_engine.execute(
            request=execution_request,
            user_id=user_id,
        )
        
        # Create and save message
        message = await self._create_and_save_message(
            conversation=conversation,
            content=result.response,
            role=MessageRole.ASSISTANT,
            metadata=result.metadata,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            cost=result.cost,
            provider_used=request.provider,
            response_time_ms=result.execution_time_ms,
        )
        
        # Update conversation aggregates
        from chatter.services.conversation import ConversationService
        conversation_service = ConversationService(self.session)
        await conversation_service.update_conversation_aggregates(
            conversation_id=conversation.id,
            user_id=user_id,
            tokens_delta=result.tokens_used,
            cost_delta=result.cost,
            message_count_delta=1,
        )
        
        return conversation, message

    async def execute_chat_workflow_streaming(
        self,
        user_id: str,
        request: ChatRequest,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute a chat workflow with streaming using the unified ExecutionEngine."""
        try:
            # Get or create conversation
            conversation = await self._get_or_create_conversation(
                user_id, request
            )

            # Use the new unified execution engine with streaming enabled
            from chatter.schemas.execution import ExecutionRequest
            
            # Convert ChatRequest to ExecutionRequest with streaming enabled
            execution_request = ExecutionRequest(
                message=request.message,
                provider=request.provider,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                system_prompt=request.system_prompt_override,
                enable_memory=request.enable_memory,
                enable_retrieval=request.enable_retrieval,
                enable_tools=request.enable_tools,
                streaming=True,  # Enable streaming
                memory_window=getattr(request, 'memory_window', 10),
                max_tool_calls=getattr(request, 'max_tool_calls', 10),
                document_ids=request.document_ids,
                conversation_id=conversation.id,
                workflow_config=request.workflow_config or {},
            )
            
            # Execute using the new engine - will return AsyncGenerator due to streaming=True
            result = await self.execution_engine.execute(
                request=execution_request,
                user_id=user_id,
            )
            
            # Stream the chunks
            async for chunk in result:
                yield chunk

        except Exception as e:
            logger.error(f"Streaming workflow execution failed: {e}")
            yield StreamingChatChunk(
                type="error",
                content=f"Error: {str(e)}",
                metadata={"error": True},
            )

    async def execute_workflow_definition(
        self,
        definition: Any,
        input_data: dict[str, Any],
        user_id: str,
        debug_mode: bool = False,
    ) -> dict[str, Any]:
        """Execute a workflow from a stored definition."""
        start_time = datetime.now(UTC)

        # Import WorkflowManagementService to create execution record
        from chatter.services.workflow_management import (
            WorkflowManagementService,
        )

        # Create workflow management service
        workflow_service = WorkflowManagementService(self.session)

        # Get definition_id from definition object
        definition_id = getattr(definition, 'id', 'unknown')

        # Create workflow execution record
        execution = await workflow_service.create_workflow_execution(
            definition_id=definition_id,
            owner_id=user_id,
            input_data=input_data,
        )

        # Log execution start
        logger.info(
            f"Started workflow execution for definition {definition_id}",
            extra={"execution_id": execution.id, "user_id": user_id},
        )

        try:
            # Update execution status to running
            execution = (
                await workflow_service.update_workflow_execution(
                    execution_id=execution.id,
                    owner_id=user_id,
                    status="running",
                    started_at=start_time,
                )
            )

            # Log stored definition structure if available
            definition_name = getattr(
                definition, 'name', None
            ) or getattr(definition, 'id', 'unknown')

            # Try to extract nodes and edges from the definition
            nodes = []
            edges = []

            if hasattr(definition, 'nodes') and hasattr(
                definition, 'edges'
            ):
                # If definition has nodes and edges attributes
                nodes = (
                    definition.nodes
                    if hasattr(definition.nodes, '__iter__')
                    else []
                )
                edges = (
                    definition.edges
                    if hasattr(definition.edges, '__iter__')
                    else []
                )
            elif isinstance(definition, dict):
                # If definition is a dictionary
                nodes = definition.get('nodes', [])
                edges = definition.get('edges', [])

            # Convert nodes and edges to dictionaries if they're not already
            nodes_dict = []
            edges_dict = []

            for node in nodes:
                if hasattr(node, '__dict__'):
                    # Convert object to dict
                    node_dict = {
                        'id': getattr(node, 'id', 'unknown'),
                        'type': getattr(node, 'type', 'unknown'),
                        'config': getattr(node, 'config', {})
                        or getattr(node, 'data', {}),
                    }
                elif isinstance(node, dict):
                    node_dict = node
                else:
                    node_dict = {
                        'id': str(node),
                        'type': 'unknown',
                        'config': {},
                    }
                nodes_dict.append(node_dict)

            for edge in edges:
                if hasattr(edge, '__dict__'):
                    # Convert object to dict
                    edge_dict = {
                        'source': getattr(edge, 'source', 'unknown'),
                        'target': getattr(edge, 'target', 'unknown'),
                        'type': getattr(edge, 'type', 'regular'),
                        'condition': getattr(edge, 'condition', None),
                    }
                elif isinstance(edge, dict):
                    edge_dict = edge
                else:
                    edge_dict = {
                        'source': 'unknown',
                        'target': 'unknown',
                        'type': 'regular',
                    }
                edges_dict.append(edge_dict)

            # Log workflow debugging information before execution
            _log_workflow_debug_info(
                nodes=nodes_dict,
                edges=edges_dict,
                execution_type="stored_definition",
                definition_name=definition_name,
            )

            # Get LLM using default provider and model
            llm = await self.llm_service.get_llm(
                provider=None,  # Use default provider
                model=None,  # Use default model for the provider
                temperature=0.1,
                max_tokens=2048,
            )

            # Extract message from input data
            message = input_data.get("message", "")
            if not message:
                raise ValueError("No message provided in input_data")

            # Parse workflow definition with enhanced flexibility
            # Check if definition contains specific configuration
            enable_memory = True  # Default
            enable_retrieval = False  # Default
            enable_tools = False  # Default

            if isinstance(definition, dict):
                # Extract configuration from workflow definition if available
                config = definition.get("config", {})
                enable_memory = config.get("enable_memory", True)
                enable_retrieval = config.get("enable_retrieval", False)
                enable_tools = config.get("enable_tools", False)

                logger.info(
                    f"Parsed workflow definition config: memory={enable_memory}, retrieval={enable_retrieval}, tools={enable_tools}"
                )

            workflow_def = create_simple_workflow_definition(
                enable_memory=enable_memory,
                enable_retrieval=enable_retrieval,
                enable_tools=enable_tools,
            )

            # Log the actual workflow definition that will be executed
            # Extract nodes and edges from the workflow definition
            actual_nodes = []
            actual_edges = []

            if hasattr(workflow_def, 'nodes') and hasattr(
                workflow_def, 'edges'
            ):
                actual_nodes = [
                    {
                        'id': node.get('id', 'unknown'),
                        'type': node.get('type', 'unknown'),
                        'config': node.get('config', {}),
                    }
                    for node in workflow_def.nodes
                ]
                actual_edges = [
                    {
                        'source': edge.get('source', 'unknown'),
                        'target': edge.get('target', 'unknown'),
                        'type': edge.get('type', 'regular'),
                        'condition': edge.get('condition'),
                    }
                    for edge in workflow_def.edges
                ]

                # Log the actual workflow that will be executed
                _log_workflow_debug_info(
                    nodes=actual_nodes,
                    edges=actual_edges,
                    execution_type="generated_simple_workflow",
                    definition_name=f"simple_workflow_for_{definition_name}",
                )

            # Create workflow from definition
            workflow = (
                await workflow_manager.create_workflow_from_definition(
                    definition=workflow_def,
                    llm=llm,
                )
            )

            # Create execution context
            context: WorkflowNodeContext = {
                "messages": [HumanMessage(content=message)],
                "user_id": user_id,
                "conversation_id": generate_ulid(),
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": input_data.get("metadata", {}),
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
                "usage_metadata": {},
            }

            # Log workflow structure for debugging
            performance_monitor.log_debug(
                f"Executing workflow with {len(actual_nodes)} nodes and {len(actual_edges)} edges",
                data={
                    "nodes": [n.get('id') for n in actual_nodes],
                    "edges": [
                        (e.get('source'), e.get('target'))
                        for e in actual_edges
                    ],
                    "enable_memory": enable_memory,
                    "enable_retrieval": enable_retrieval,
                    "enable_tools": enable_tools,
                },
            )

            # Execute workflow
            workflow_start_time = time.time()
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=context,
                thread_id=generate_ulid(),
            )
            workflow_execution_time = int(
                (time.time() - workflow_start_time) * 1000
            )

            performance_monitor.log_debug(
                f"Workflow execution completed in {workflow_execution_time}ms",
                data={"execution_time_ms": workflow_execution_time},
            )

            # Extract response
            ai_message = self._extract_ai_response(result)

            # Calculate execution time
            end_time = datetime.now(UTC)
            execution_time_ms = int(
                (end_time - start_time).total_seconds() * 1000
            )

            # Collect debug information if enabled
            debug_info = (
                {"debug_logs": performance_monitor.debug_logs}
                if debug_mode
                else {}
            )
            execution_log = performance_monitor.debug_logs

            # Update execution with success status and results
            updated_execution = (
                await workflow_service.update_workflow_execution(
                    execution_id=execution.id,
                    owner_id=user_id,
                    status="completed",
                    completed_at=end_time,
                    execution_time_ms=execution_time_ms,
                    output_data={
                        "response": ai_message.content,
                        "conversation_id": context["conversation_id"],
                        "metadata": result.get("metadata", {}),
                        "debug_info": debug_info,
                    },
                    tokens_used=result.get("tokens_used", 0),
                    cost=result.get("cost", 0.0),
                    execution_log=execution_log,
                )
            )

            if not updated_execution:
                logger.error(
                    "Failed to update workflow execution record"
                )
                raise RuntimeError(
                    "Failed to update workflow execution record"
                )

            execution = updated_execution

            logger.info(
                f"Workflow execution {execution.id} completed successfully"
            )

            # Return execution record as dictionary - ensure we return the complete execution record
            execution_dict = execution.to_dict()

            # Validate that the required fields are present to prevent schema validation errors
            required_fields = [
                'id',
                'definition_id',
                'owner_id',
                'status',
            ]
            for field in required_fields:
                if field not in execution_dict:
                    logger.error(
                        f"Missing required field '{field}' in execution dict"
                    )
                    raise ValueError(
                        f"Execution record missing required field: {field}"
                    )

            logger.debug(
                f"Returning execution record for {execution.id} with fields: {list(execution_dict.keys())}"
            )
            return execution_dict

        except Exception as e:
            # Calculate execution time even on failure
            end_time = datetime.now(UTC)
            execution_time_ms = int(
                (end_time - start_time).total_seconds() * 1000
            )

            # Log error for debugging
            performance_monitor.log_debug(
                f"Workflow execution failed: {str(e)}",
                data={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )

            # Collect debug information if enabled (even on failure)
            debug_info = (
                {"debug_logs": performance_monitor.debug_logs}
                if debug_mode
                else {}
            )
            execution_log = performance_monitor.debug_logs

            # Update execution with failed status
            try:
                updated_execution = (
                    await workflow_service.update_workflow_execution(
                        execution_id=execution.id,
                        owner_id=user_id,
                        status="failed",
                        completed_at=end_time,
                        execution_time_ms=execution_time_ms,
                        error_message=str(e),
                        execution_log=execution_log,
                    )
                )
                if updated_execution:
                    logger.error(
                        f"Workflow execution {updated_execution.id} failed: {e}"
                    )
                else:
                    logger.error(
                        f"Workflow execution {execution.id} failed: {e}"
                    )
            except Exception as update_error:
                logger.error(
                    f"Failed to update execution status after error: {update_error}"
                )
                # Continue to raise the original exception

            raise

    async def _get_conversation_messages(
        self, conversation: Conversation
    ) -> list[BaseMessage]:
        """Get conversation history as LangChain messages with pagination."""
        messages = []

        try:
            # Get recent messages from conversation with limit for performance
            from sqlalchemy import desc, select

            # Implement pagination and limits - get last 50 messages
            query = (
                select(Message)
                .where(Message.conversation_id == conversation.id)
                .order_by(desc(Message.created_at))
                .limit(50)
            )

            result = await self.session.execute(query)
            conversation_messages = result.scalars().all()

            # Reverse to get chronological order
            conversation_messages = list(
                reversed(conversation_messages)
            )

            for msg in conversation_messages:
                if msg.role == MessageRole.USER:
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == MessageRole.ASSISTANT:
                    from langchain_core.messages import AIMessage

                    messages.append(AIMessage(content=msg.content))

        except Exception as e:
            logger.warning(f"Could not get conversation messages: {e}")
            # Return empty list if retrieval fails
            messages = []

        return messages

    def _extract_ai_response(
        self, workflow_result: dict[str, Any]
    ) -> BaseMessage:
        """Extract AI response from workflow result."""
        messages = workflow_result.get("messages", [])

        # Find the last AI message
        for message in reversed(messages):
            if hasattr(message, "content") and message.content:
                return message

        # Fallback
        from langchain_core.messages import AIMessage

        return AIMessage(content="No response generated")

    async def _create_and_save_message(
        self,
        conversation: Conversation,
        content: str,
        role: MessageRole,
        metadata: dict[str, Any] | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        cost: float | None = None,
        provider_used: str | None = None,
        response_time_ms: int | None = None,
    ) -> Message:
        """Create and save a message to the conversation with token statistics."""
        from datetime import datetime

        from sqlalchemy import func, select

        # Get proper sequence number from conversation message count
        query = select(func.count(Message.id)).where(
            Message.conversation_id == conversation.id
        )
        result = await self.session.execute(query)
        message_count = result.scalar() or 0
        sequence_number = message_count + 1

        # Calculate total tokens
        total_tokens = None
        if prompt_tokens is not None or completion_tokens is not None:
            total_tokens = (prompt_tokens or 0) + (
                completion_tokens or 0
            )

        # Create message object with all fields including token statistics
        message = Message(
            id=generate_ulid(),
            conversation_id=conversation.id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            rating_count=0,
            extra_metadata=metadata or {},
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=cost,
            provider_used=provider_used,
            response_time_ms=response_time_ms,
        )

        # The Base class will automatically set created_at and updated_at
        # But to be safe, let's explicitly set created_at if it's not set
        if (
            not hasattr(message, 'created_at')
            or message.created_at is None
        ):
            message.created_at = datetime.now(UTC)

        # Save to database via session
        try:
            self.session.add(message)
            await self.session.commit()
            logger.debug(
                f"Saved message {message.id} to database with tokens: {total_tokens}"
            )
        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")
            await self.session.rollback()
            # Don't fail the entire workflow execution for message saving issues

        return message

    async def _get_or_create_conversation(
        self, user_id: str, request: ChatRequest
    ) -> Conversation:
        """Get existing conversation or create new one."""
        conversation_id = getattr(request, 'conversation_id', None)

        if conversation_id:
            # Get existing conversation
            try:
                from chatter.services.conversation import (
                    ConversationService,
                )

                conversation_service = ConversationService(self.session)
                conversation = await conversation_service.get_conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    include_messages=False,
                )
                logger.debug(
                    f"Retrieved existing conversation {conversation_id}"
                )
                return conversation
            except Exception as e:
                logger.warning(
                    f"Failed to retrieve conversation {conversation_id}: {e}. Creating new conversation."
                )
                # Fall through to create new conversation

        # Create new conversation with all required fields
        now = datetime.now(UTC)
        conversation = Conversation(
            id=generate_ulid(),
            user_id=user_id,
            title=getattr(request, 'title', 'New Conversation'),
            status=ConversationStatus.ACTIVE,
            enable_retrieval=False,
            message_count=0,
            total_tokens=0,
            total_cost=0.0,
            context_window=4096,
            memory_enabled=True,
            retrieval_limit=5,
            retrieval_score_threshold=0.7,
            created_at=now,
            updated_at=now,
        )

        # Save conversation to database
        try:
            self.session.add(conversation)
            await self.session.commit()
            logger.debug(
                f"Saved conversation {conversation.id} to database"
            )
        except Exception as e:
            logger.error(
                f"Failed to save conversation to database: {e}"
            )
            await self.session.rollback()
            # Don't fail the entire workflow for conversation saving issues

        return conversation




# Factory function for dependency injection
def create_workflow_execution_service(
    llm_service: LLMService,
    message_service: MessageService,
    session,
) -> WorkflowExecutionService:
    """Create modern workflow execution service."""
    return WorkflowExecutionService(
        llm_service=llm_service,
        message_service=message_service,
        session=session,
    )
