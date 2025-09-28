"""Modern workflow execution service.

This service provides the modern workflow execution system using the
new flexible architecture with support for all node types.
"""

from __future__ import annotations

import time
from typing import Any
from collections.abc import AsyncGenerator

from langchain_core.messages import BaseMessage, HumanMessage

from chatter.core.enhanced_memory_manager import EnhancedMemoryManager
from chatter.core.enhanced_tool_executor import EnhancedToolExecutor
from chatter.core.langgraph import workflow_manager
from chatter.core.workflow_graph_builder import create_simple_workflow_definition
from chatter.core.workflow_node_factory import WorkflowNodeContext
from chatter.models.base import generate_ulid
from chatter.models.conversation import Conversation, ConversationStatus, Message, MessageRole
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.utils.logging import get_logger
from datetime import UTC, datetime

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
        node_details.append({
            "id": node_id,
            "type": node_type,
            "config_keys": list(node_config.keys()) if isinstance(node_config, dict) else [],
            "has_config": bool(node_config),
        })
    
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
    entry_points = [node.get("id") for node in nodes if node.get("id") not in target_nodes]
    
    # Find exit points (nodes with edges to END or no outgoing edges)
    source_nodes = {edge.get("source") for edge in edges}
    exit_points = []
    for edge in edges:
        if edge.get("target") == "END" or edge.get("target") == "__end__":
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

    async def execute_chat_workflow(
        self,
        user_id: str,
        request: Any,
    ) -> tuple[Conversation, Message]:
        """Execute chat workflow - API wrapper method."""
        # Get or create conversation
        conversation = await self._get_or_create_conversation(user_id, request)

        # Convert request to ChatRequest
        chat_request = self._convert_to_chat_request(request)

        # Execute the actual workflow
        message, result = await self._execute_chat_workflow_internal(
            conversation=conversation,
            chat_request=chat_request,
            user_id=user_id,
        )

        return conversation, message

    async def _execute_chat_workflow_internal(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        user_id: str,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute a chat workflow using the modern system."""
        start_time = time.time()

        try:
            # Get LLM
            llm = await self.llm_service.get_llm(
                provider=chat_request.provider,
                model=chat_request.model,
                temperature=chat_request.temperature,
                max_tokens=chat_request.max_tokens,
            )

            # Get tools and retriever if needed
            tools = None
            retriever = None

            if chat_request.enable_tools:
                try:
                    from chatter.core.tool_registry import ToolRegistry
                    tool_registry = ToolRegistry()
                    tools = tool_registry.get_tools_for_workspace(
                        workspace_id=user_id,
                        user_permissions=[]  # TODO: Add user permission system
                    )
                    logger.info(f"Loaded {len(tools) if tools else 0} tools for workflow execution")
                except Exception as e:
                    logger.warning(f"Could not load tools from tool registry: {e}")
                    tools = []

            if chat_request.enable_retrieval:
                try:
                    from chatter.core.vector_store import get_vector_store_retriever
                    retriever = get_vector_store_retriever(user_id=user_id)
                    logger.info("Loaded retriever from vector store")
                except Exception as e:
                    logger.warning(f"Could not load retriever from vector store: {e}")
                    retriever = None

            # Create workflow using modern system
            workflow = await workflow_manager.create_workflow(
                llm=llm,
                enable_retrieval=chat_request.enable_retrieval,
                enable_tools=chat_request.enable_tools,
                enable_memory=chat_request.enable_memory,
                system_message=chat_request.system_prompt_override,
                retriever=retriever,
                tools=tools,
                memory_window=getattr(chat_request, 'memory_window', 10),
                max_tool_calls=getattr(chat_request, 'max_tool_calls', 10),
                user_id=user_id,
                conversation_id=conversation.id,
            )

            # Get conversation history
            messages = await self._get_conversation_messages(conversation)

            # Add new user message
            messages.append(HumanMessage(content=chat_request.message))

            # Create initial state
            initial_state: WorkflowNodeContext = {
                "messages": messages,
                "user_id": user_id,
                "conversation_id": conversation.id,
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": {
                    "provider": chat_request.provider,
                    "model": chat_request.model,
                    "temperature": chat_request.temperature,
                    "max_tokens": chat_request.max_tokens,
                },
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
            }

            # Execute workflow
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=initial_state,
                thread_id=conversation.id,
            )

            # Extract AI response
            ai_message = self._extract_ai_response(result)

            # Create and save message
            message = await self._create_and_save_message(
                conversation=conversation,
                content=ai_message.content,
                role=MessageRole.ASSISTANT,
                metadata=result.get("metadata", {}),
            )

            # Calculate usage info
            execution_time_ms = int((time.time() - start_time) * 1000)
            usage_info = {
                "execution_time_ms": execution_time_ms,
                "tool_calls": result.get("tool_call_count", 0),
                "workflow_execution": True,
                "modern_system": True,
                **result.get("metadata", {}),
            }

            return message, usage_info

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            # Create error message
            error_message = await self._create_and_save_message(
                conversation=conversation,
                content=f"I encountered an error: {str(e)}",
                role=MessageRole.ASSISTANT,
                metadata={"error": True, "error_message": str(e)},
            )

            execution_time_ms = int((time.time() - start_time) * 1000)
            usage_info = {
                "execution_time_ms": execution_time_ms,
                "error": True,
                "error_message": str(e),
            }

            return error_message, usage_info

    async def execute_chat_workflow_streaming(
        self,
        user_id: str,
        request: Any,  # ChatWorkflowRequest
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute a chat workflow with streaming using the modern system."""
        try:
            # Get or create conversation
            conversation = await self._get_or_create_conversation(user_id, request)

            # Convert to ChatRequest for compatibility
            chat_request = self._convert_to_chat_request(request)

            # Get LLM
            llm = await self.llm_service.get_llm(
                provider=chat_request.provider,
                model=chat_request.model,
                temperature=chat_request.temperature,
                max_tokens=chat_request.max_tokens,
            )

            # Create workflow
            workflow = await workflow_manager.create_workflow(
                llm=llm,
                enable_retrieval=chat_request.enable_retrieval,
                enable_tools=chat_request.enable_tools,
                enable_memory=chat_request.enable_memory,
                enable_streaming=True,
                system_message=chat_request.system_prompt_override,
                user_id=user_id,
                conversation_id=conversation.id,
            )

            # Get conversation history and create initial state
            messages = await self._get_conversation_messages(conversation)
            messages.append(HumanMessage(content=request.message))

            initial_state: WorkflowNodeContext = {
                "messages": messages,
                "user_id": user_id,
                "conversation_id": conversation.id,
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": {},
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
            }

            # Stream workflow execution
            content_buffer = ""
            async for update in workflow_manager.stream_workflow(
                workflow=workflow,
                initial_state=initial_state,
                thread_id=conversation.id,
                enable_llm_streaming=True,
            ):
                if isinstance(update, dict) and "messages" in update:
                    # Extract streaming content
                    messages = update["messages"]
                    if messages:
                        last_message = messages[-1]
                        if hasattr(last_message, "content"):
                            new_content = last_message.content[len(content_buffer):]
                            if new_content:
                                content_buffer += new_content
                                yield StreamingChatChunk(
                                    type="content",
                                    content=new_content,
                                    metadata=update.get("metadata", {}),
                                )

            # Send completion chunk
            yield StreamingChatChunk(
                type="done",
                content="",
                metadata={"streaming_complete": True},
            )

        except Exception as e:
            logger.error(f"Streaming workflow execution failed: {e}")
            yield StreamingChatChunk(
                type="error",
                content=f"Error: {str(e)}",
                metadata={"error": True},
            )

    async def execute_custom_workflow(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        message: str,
        user_id: str,
        provider: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Execute a custom workflow definition."""
        try:
            # Log workflow debugging information before execution
            _log_workflow_debug_info(
                nodes=nodes,
                edges=edges,
                execution_type="custom_workflow",
            )
            
            # Get LLM
            llm = await self.llm_service.get_llm(provider=provider, model=model)

            # Create custom workflow
            workflow = await workflow_manager.create_custom_workflow(
                nodes=nodes,
                edges=edges,
                llm=llm,
                **kwargs,
            )

            # Create initial state
            initial_state: WorkflowNodeContext = {
                "messages": [HumanMessage(content=message)],
                "user_id": user_id,
                "conversation_id": generate_ulid(),
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": {},
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
            }

            # Execute workflow
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=initial_state,
            )

            return result

        except Exception as e:
            logger.error(f"Custom workflow execution failed: {e}")
            raise

    async def execute_workflow_definition(
        self,
        definition: Any,
        input_data: dict[str, Any],
        user_id: str,
    ) -> dict[str, Any]:
        """Execute a workflow from a stored definition."""
        try:
            # Log stored definition structure if available
            definition_name = getattr(definition, 'name', None) or getattr(definition, 'id', 'unknown')
            
            # Try to extract nodes and edges from the definition
            nodes = []
            edges = []
            
            if hasattr(definition, 'nodes') and hasattr(definition, 'edges'):
                # If definition has nodes and edges attributes
                nodes = definition.nodes if hasattr(definition.nodes, '__iter__') else []
                edges = definition.edges if hasattr(definition.edges, '__iter__') else []
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
                        'config': getattr(node, 'config', {}) or getattr(node, 'data', {})
                    }
                elif isinstance(node, dict):
                    node_dict = node
                else:
                    node_dict = {'id': str(node), 'type': 'unknown', 'config': {}}
                nodes_dict.append(node_dict)
            
            for edge in edges:
                if hasattr(edge, '__dict__'):
                    # Convert object to dict
                    edge_dict = {
                        'source': getattr(edge, 'source', 'unknown'),
                        'target': getattr(edge, 'target', 'unknown'),
                        'type': getattr(edge, 'type', 'regular'),
                        'condition': getattr(edge, 'condition', None)
                    }
                elif isinstance(edge, dict):
                    edge_dict = edge
                else:
                    edge_dict = {'source': 'unknown', 'target': 'unknown', 'type': 'regular'}
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
                model=None,     # Use default model for the provider
                temperature=0.1,
                max_tokens=2048,
            )

            # Extract message from input data
            message = input_data.get("message", "")
            if not message:
                raise ValueError("No message provided in input_data")

            # Parse workflow definition with enhanced flexibility
            # Check if workflow_definition contains specific configuration
            enable_memory = True  # Default
            enable_retrieval = False  # Default
            enable_tools = False  # Default
            
            if isinstance(definition, dict):
                # Extract configuration from workflow definition if available
                config = definition.get("config", {})
                enable_memory = config.get("enable_memory", True)
                enable_retrieval = config.get("enable_retrieval", False) 
                enable_tools = config.get("enable_tools", False)
                
                logger.info(f"Parsed workflow definition config: memory={enable_memory}, retrieval={enable_retrieval}, tools={enable_tools}")
            
            workflow_def = create_simple_workflow_definition(
                enable_memory=enable_memory,
                enable_retrieval=enable_retrieval,
                enable_tools=enable_tools,
            )
            
            # Log the actual workflow definition that will be executed
            # Extract nodes and edges from the workflow definition
            actual_nodes = []
            actual_edges = []
            
            if hasattr(workflow_def, 'nodes') and hasattr(workflow_def, 'edges'):
                actual_nodes = [
                    {
                        'id': node.get('id', 'unknown'),
                        'type': node.get('type', 'unknown'), 
                        'config': node.get('config', {})
                    }
                    for node in workflow_def.nodes
                ]
                actual_edges = [
                    {
                        'source': edge.get('source', 'unknown'),
                        'target': edge.get('target', 'unknown'),
                        'type': edge.get('type', 'regular'),
                        'condition': edge.get('condition')
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
            workflow = await workflow_manager.create_workflow_from_definition(
                definition=workflow_def,
                llm=llm,
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
            }

            # Execute workflow
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=context,
                thread_id=generate_ulid(),
            )

            # Extract response
            ai_message = self._extract_ai_response(result)

            return {
                "response": ai_message.content,
                "conversation_id": context["conversation_id"],
                "user_id": user_id,
                "metadata": result.get("metadata", {}),
            }

        except Exception as e:
            logger.error(f"Workflow definition execution failed: {e}")
            raise

    async def _get_conversation_messages(self, conversation: Conversation) -> list[BaseMessage]:
        """Get conversation history as LangChain messages with pagination."""
        messages = []

        try:
            # Get recent messages from conversation with limit for performance
            from sqlalchemy import select, desc
            
            # Implement pagination and limits - get last 50 messages
            query = select(Message).where(
                Message.conversation_id == conversation.id
            ).order_by(desc(Message.created_at)).limit(50)
            
            result = await self.session.execute(query)
            conversation_messages = result.scalars().all()
            
            # Reverse to get chronological order
            conversation_messages = list(reversed(conversation_messages))
            
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

    def _extract_ai_response(self, workflow_result: dict[str, Any]) -> BaseMessage:
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
    ) -> Message:
        """Create and save a message to the conversation."""
        from datetime import datetime

        # Get proper sequence number from conversation message count
        query = select(func.count(Message.id)).where(
            Message.conversation_id == conversation.id
        )
        result = await self.session.execute(query)
        message_count = result.scalar() or 0
        sequence_number = message_count + 1

        # Create message object with all required fields
        # Note: Base class automatically sets id, created_at, updated_at, but we need to
        # ensure all the Message-specific required fields are set
        message = Message(
            id=generate_ulid(),
            conversation_id=conversation.id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            rating_count=0,  # Default value for required field
            extra_metadata=metadata or {},
        )

        # The Base class will automatically set created_at and updated_at
        # But to be safe, let's explicitly set created_at if it's not set
        if not hasattr(message, 'created_at') or message.created_at is None:
            message.created_at = datetime.now(UTC)

        # Save to database via session
        try:
            self.session.add(message)
            await self.session.commit()
            logger.debug(f"Saved message {message.id} to database")
        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")
            await self.session.rollback()
            # Don't fail the entire workflow execution for message saving issues
            
        return message

    async def _get_or_create_conversation(self, user_id: str, request: Any) -> Conversation:
        """Get existing conversation or create new one."""
        conversation_id = getattr(request, 'conversation_id', None)

        if conversation_id:
            # TODO: Get existing conversation
            # conversation = await self.conversation_service.get_conversation(conversation_id)
            pass

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
            logger.debug(f"Saved conversation {conversation.id} to database")
        except Exception as e:
            logger.error(f"Failed to save conversation to database: {e}")
            await self.session.rollback()
            # Don't fail the entire workflow for conversation saving issues

        return conversation

    def _convert_to_chat_request(self, request: Any) -> ChatRequest:
        """Convert workflow request to ChatRequest for compatibility."""
        return ChatRequest(
            message=request.message,
            conversation_id=getattr(request, 'conversation_id', None),
            provider=getattr(request, 'provider', None),  # Let system choose default
            model=getattr(request, 'model', None),  # Let system choose default
            temperature=getattr(request, 'temperature', None),
            max_tokens=getattr(request, 'max_tokens', None),
            system_prompt_override=getattr(request, 'system_prompt_override', None),
            enable_retrieval=getattr(request, 'enable_retrieval', False),
            enable_tools=getattr(request, 'enable_tools', False),
            enable_memory=getattr(request, 'enable_memory', True),
        )


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
