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
from chatter.core.workflow_performance import PerformanceMonitor
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


# Global event emitter (will be initialized on first use)
_event_emitter = None


async def _emit_event(event: UnifiedEvent) -> None:
    """Emit an event to the unified event system."""
    global _event_emitter
    if _event_emitter is None:
        try:
            from chatter.core.events import get_event_emitter

            _event_emitter = await get_event_emitter()
        except Exception as e:
            logger.warning(f"Could not initialize event emitter: {e}")
            return

    try:
        await _event_emitter.emit(event)
    except Exception as e:
        logger.warning(f"Could not emit event: {e}")


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

    async def execute_chat_workflow(
        self,
        user_id: str,
        request: Any,
    ) -> tuple[Conversation, Message]:
        """Execute chat workflow - API wrapper method."""
        # Get or create conversation
        conversation = await self._get_or_create_conversation(
            user_id, request
        )

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
        """Execute a chat workflow using the universal template system."""
        start_time = time.time()

        try:
            # Try to use universal template first, fallback to dynamic creation
            try:
                return await self._execute_with_universal_template(
                    conversation=conversation,
                    chat_request=chat_request,
                    user_id=user_id,
                    start_time=start_time,
                )
            except Exception as e:
                logger.warning(
                    f"Universal template execution failed, falling back to dynamic creation: {e}"
                )
                return await self._execute_with_dynamic_workflow(
                    conversation=conversation,
                    chat_request=chat_request,
                    user_id=user_id,
                    start_time=start_time,
                )

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

    async def _execute_with_universal_template(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        user_id: str,
        start_time: float,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute chat workflow using the universal template."""
        from chatter.services.workflow_management import (
            WorkflowManagementService,
        )

        # Create workflow management service
        workflow_mgmt = WorkflowManagementService(self.session)

        # Get the universal chat template
        templates = await workflow_mgmt.list_workflow_templates(
            owner_id=user_id
        )
        universal_template = None

        for template in templates:
            if (
                template.name == "universal_chat"
                and template.is_builtin
            ):
                universal_template = template
                break

        if not universal_template:
            raise Exception("Universal chat template not found")

        # Prepare template parameters from chat request
        template_params = {
            "provider": chat_request.provider,
            "model": chat_request.model,
            "temperature": chat_request.temperature,
            "max_tokens": chat_request.max_tokens,
            "system_message": chat_request.system_prompt_override,
            "enable_memory": chat_request.enable_memory,
            "enable_retrieval": chat_request.enable_retrieval,
            "enable_tools": chat_request.enable_tools,
            "memory_window": getattr(chat_request, 'memory_window', 10),
            "max_tool_calls": getattr(
                chat_request, 'max_tool_calls', 10
            ),
            "workflow_type": "universal_chat",
        }

        # Create workflow definition from template
        definition = await workflow_mgmt.create_workflow_definition_from_template(
            template_id=universal_template.id,
            owner_id=user_id,
            name_suffix="Execution",
            user_input=template_params,
            is_temporary=True,
        )

        # Create workflow execution record
        execution = await workflow_mgmt.create_workflow_execution(
            definition_id=definition.id,
            owner_id=user_id,
            input_data={
                "message": chat_request.message,
                "conversation_id": conversation.id,
                "provider": chat_request.provider,
                "model": chat_request.model,
            },
        )

        # Initialize performance monitor for tracking
        performance_monitor = PerformanceMonitor(debug_mode=True)
        performance_monitor.log_debug(
            "Started universal template execution",
            data={
                "execution_id": execution.id,
                "template_id": universal_template.id,
                "conversation_id": conversation.id,
            },
        )

        # Start workflow tracking with monitoring service
        monitoring = await get_monitoring_service()
        correlation_id = generate_ulid()
        workflow_id = monitoring.start_workflow_tracking(
            user_id=user_id,
            conversation_id=conversation.id,
            provider_name=chat_request.provider or "",
            model_name=chat_request.model or "",
            workflow_config={
                "template_id": universal_template.id,
                "enable_tools": chat_request.enable_tools,
                "enable_retrieval": chat_request.enable_retrieval,
                "enable_memory": chat_request.enable_memory,
            },
            correlation_id=correlation_id,
        )

        # Emit workflow started event
        await _emit_event(
            UnifiedEvent(
                category=EventCategory.WORKFLOW,
                event_type="workflow_started",
                user_id=user_id,
                session_id=conversation.id,
                correlation_id=correlation_id,
                data={
                    "workflow_id": workflow_id,
                    "execution_id": execution.id,
                    "template_id": universal_template.id,
                    "provider": chat_request.provider,
                    "model": chat_request.model,
                },
            )
        )

        try:
            # Update execution status to running
            execution = await workflow_mgmt.update_workflow_execution(
                execution_id=execution.id,
                owner_id=user_id,
                status="running",
                started_at=datetime.fromtimestamp(start_time, UTC),
            )

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
                        user_permissions=[],  # TODO: Add user permission system
                    )
                    logger.info(
                        f"Loaded {len(tools) if tools else 0} tools for universal template execution"
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not load tools from tool registry: {e}"
                    )
                    tools = []

            if chat_request.enable_retrieval:
                try:
                    from chatter.core.vector_store import (
                        get_vector_store_retriever,
                    )

                    retriever = await get_vector_store_retriever(
                        user_id=user_id
                    )
                    logger.info(
                        "Loaded retriever from vector store for universal template"
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not load retriever from vector store: {e}"
                    )
                    retriever = None

            # Create workflow from definition
            # Convert database WorkflowDefinition to graph builder WorkflowDefinition
            graph_definition = create_workflow_definition_from_model(
                definition
            )
            workflow = (
                await workflow_manager.create_workflow_from_definition(
                    definition=graph_definition,
                    llm=llm,
                    retriever=retriever,
                    tools=tools,
                    max_tool_calls=getattr(
                        chat_request, 'max_tool_calls', 10
                    ),
                    user_id=user_id,
                    conversation_id=conversation.id,
                )
            )

            performance_monitor.log_debug(
                "Workflow created from universal template",
                data={"definition_id": definition.id},
            )

            # Get conversation history
            messages = await self._get_conversation_messages(
                conversation
            )

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
                    "universal_template": True,
                    "template_id": universal_template.id,
                },
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
            }

            # Execute workflow
            performance_monitor.log_debug("Starting workflow execution")
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=initial_state,
                thread_id=conversation.id,
            )
            performance_monitor.log_debug(
                "Workflow execution completed"
            )

            # Extract AI response
            ai_message = self._extract_ai_response(result)

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Create and save message with token statistics
            message = await self._create_and_save_message(
                conversation=conversation,
                content=ai_message.content,
                role=MessageRole.ASSISTANT,
                metadata=result.get("metadata", {}),
                prompt_tokens=result.get("prompt_tokens"),
                completion_tokens=result.get("completion_tokens"),
                cost=result.get("cost"),
                provider_used=chat_request.provider,
                response_time_ms=execution_time_ms,
            )

            # Update conversation aggregates
            from chatter.services.conversation import (
                ConversationService,
            )

            conversation_service = ConversationService(self.session)
            await conversation_service.update_conversation_aggregates(
                conversation_id=conversation.id,
                user_id=user_id,
                tokens_delta=result.get("tokens_used", 0),
                cost_delta=result.get("cost", 0.0),
                message_count_delta=1,  # One new assistant message
            )

            # Calculate usage info
            usage_info = {
                "execution_time_ms": execution_time_ms,
                "tool_calls": result.get("tool_call_count", 0),
                "workflow_execution": True,
                "universal_template": True,
                "template_id": universal_template.id,
                **result.get("metadata", {}),
            }

            # Update execution with success
            await workflow_mgmt.update_workflow_execution(
                execution_id=execution.id,
                owner_id=user_id,
                status="completed",
                completed_at=datetime.now(UTC),
                execution_time_ms=execution_time_ms,
                output_data={
                    "response": ai_message.content,
                    "conversation_id": conversation.id,
                    "metadata": result.get("metadata", {}),
                },
                tokens_used=result.get("tokens_used", 0),
                cost=result.get("cost", 0.0),
                execution_log=performance_monitor.debug_logs,
            )

            # Update monitoring metrics
            monitoring.update_workflow_metrics(
                workflow_id=workflow_id,
                token_usage={
                    chat_request.provider
                    or "unknown": result.get("tokens_used", 0)
                },
                tool_calls=result.get("tool_call_count", 0),
            )

            # Finish workflow tracking
            monitoring.finish_workflow_tracking(workflow_id)

            # Emit workflow completed event
            await _emit_event(
                UnifiedEvent(
                    category=EventCategory.WORKFLOW,
                    event_type="workflow_completed",
                    user_id=user_id,
                    session_id=conversation.id,
                    correlation_id=correlation_id,
                    data={
                        "workflow_id": workflow_id,
                        "execution_id": execution.id,
                        "tokens_used": result.get("tokens_used", 0),
                        "cost": result.get("cost", 0.0),
                        "execution_time_ms": execution_time_ms,
                        "success": True,
                    },
                )
            )

            logger.info(
                f"Universal template execution {execution.id} completed successfully"
            )

            return message, usage_info

        except Exception as e:
            # Update monitoring metrics with error
            monitoring.update_workflow_metrics(
                workflow_id=workflow_id,
                error=str(e),
            )
            monitoring.finish_workflow_tracking(workflow_id)

            # Emit workflow failed event
            await _emit_event(
                UnifiedEvent(
                    category=EventCategory.WORKFLOW,
                    event_type="workflow_failed",
                    user_id=user_id,
                    session_id=conversation.id,
                    correlation_id=correlation_id,
                    priority=EventPriority.HIGH,
                    data={
                        "workflow_id": workflow_id,
                        "execution_id": execution.id,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )
            )

            # Update execution with failure
            execution_time_ms = int((time.time() - start_time) * 1000)
            performance_monitor.log_debug(
                f"Execution failed: {str(e)}",
                data={"error_type": type(e).__name__},
            )

            try:
                await workflow_mgmt.update_workflow_execution(
                    execution_id=execution.id,
                    owner_id=user_id,
                    status="failed",
                    completed_at=datetime.now(UTC),
                    execution_time_ms=execution_time_ms,
                    error=str(e),
                    execution_log=performance_monitor.debug_logs,
                )
            except Exception as update_error:
                logger.error(
                    f"Failed to update execution status: {update_error}"
                )

            raise

    async def _execute_with_dynamic_workflow(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        user_id: str,
        start_time: float,
    ) -> tuple[Message, dict[str, Any]]:
        """Fallback method using dynamic workflow creation."""
        from chatter.services.workflow_management import (
            WorkflowManagementService,
        )

        # Create workflow management service
        workflow_mgmt = WorkflowManagementService(self.session)

        # Create a simple workflow definition for tracking purposes
        # Since this is dynamic, we create a minimal definition
        definition = await workflow_mgmt.create_workflow_definition(
            owner_id=user_id,
            name="Dynamic Chat Workflow",
            description="Dynamically created chat workflow for execution tracking",
            nodes=[
                {
                    "id": "call_model",
                    "type": "model",
                    "config": {
                        "provider": chat_request.provider,
                        "model": chat_request.model,
                        "temperature": chat_request.temperature,
                        "max_tokens": chat_request.max_tokens,
                    },
                }
            ],
            edges=[{"source": "call_model", "target": "END"}],
            metadata={
                "dynamic": True,
                "execution_only": True,  # Mark as execution-only definition
                "enable_memory": chat_request.enable_memory,
                "enable_retrieval": chat_request.enable_retrieval,
                "enable_tools": chat_request.enable_tools,
            },
        )

        # Create workflow execution record
        execution = await workflow_mgmt.create_workflow_execution(
            definition_id=definition.id,
            owner_id=user_id,
            input_data={
                "message": chat_request.message,
                "conversation_id": conversation.id,
                "provider": chat_request.provider,
                "model": chat_request.model,
            },
        )

        # Initialize performance monitor for tracking
        performance_monitor = PerformanceMonitor(debug_mode=True)
        performance_monitor.log_debug(
            "Started dynamic workflow execution",
            data={
                "execution_id": execution.id,
                "conversation_id": conversation.id,
            },
        )

        # Start workflow tracking with monitoring service
        monitoring = await get_monitoring_service()
        correlation_id = generate_ulid()
        workflow_id = monitoring.start_workflow_tracking(
            user_id=user_id,
            conversation_id=conversation.id,
            provider_name=chat_request.provider or "",
            model_name=chat_request.model or "",
            workflow_config={
                "dynamic": True,
                "enable_tools": chat_request.enable_tools,
                "enable_retrieval": chat_request.enable_retrieval,
                "enable_memory": chat_request.enable_memory,
            },
            correlation_id=correlation_id,
        )

        # Emit workflow started event
        await _emit_event(
            UnifiedEvent(
                category=EventCategory.WORKFLOW,
                event_type="workflow_started",
                user_id=user_id,
                session_id=conversation.id,
                correlation_id=correlation_id,
                data={
                    "workflow_id": workflow_id,
                    "execution_id": execution.id,
                    "dynamic": True,
                    "provider": chat_request.provider,
                    "model": chat_request.model,
                },
            )
        )

        try:
            # Update execution status to running
            execution = await workflow_mgmt.update_workflow_execution(
                execution_id=execution.id,
                owner_id=user_id,
                status="running",
                started_at=datetime.fromtimestamp(start_time, UTC),
            )

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
                        user_permissions=[],  # TODO: Add user permission system
                    )
                    logger.info(
                        f"Loaded {len(tools) if tools else 0} tools for workflow execution"
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not load tools from tool registry: {e}"
                    )
                    tools = []

            if chat_request.enable_retrieval:
                try:
                    from chatter.core.vector_store import (
                        get_vector_store_retriever,
                    )

                    retriever = await get_vector_store_retriever(
                        user_id=user_id
                    )
                    logger.info("Loaded retriever from vector store")
                except Exception as e:
                    logger.warning(
                        f"Could not load retriever from vector store: {e}"
                    )
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
                memory_window=getattr(
                    chat_request, 'memory_window', 10
                ),
                max_tool_calls=getattr(
                    chat_request, 'max_tool_calls', 10
                ),
                user_id=user_id,
                conversation_id=conversation.id,
            )

            performance_monitor.log_debug(
                "Dynamic workflow created",
                data={"definition_id": definition.id},
            )

            # Get conversation history
            messages = await self._get_conversation_messages(
                conversation
            )

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
            performance_monitor.log_debug("Starting workflow execution")
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=initial_state,
                thread_id=conversation.id,
            )
            performance_monitor.log_debug(
                "Workflow execution completed"
            )

            # Extract AI response
            ai_message = self._extract_ai_response(result)

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Create and save message with token statistics
            message = await self._create_and_save_message(
                conversation=conversation,
                content=ai_message.content,
                role=MessageRole.ASSISTANT,
                metadata=result.get("metadata", {}),
                prompt_tokens=result.get("prompt_tokens"),
                completion_tokens=result.get("completion_tokens"),
                cost=result.get("cost"),
                provider_used=chat_request.provider,
                response_time_ms=execution_time_ms,
            )

            # Update conversation aggregates
            from chatter.services.conversation import (
                ConversationService,
            )

            conversation_service = ConversationService(self.session)
            await conversation_service.update_conversation_aggregates(
                conversation_id=conversation.id,
                user_id=user_id,
                tokens_delta=result.get("tokens_used", 0),
                cost_delta=result.get("cost", 0.0),
                message_count_delta=1,  # One new assistant message
            )

            # Calculate usage info
            usage_info = {
                "execution_time_ms": execution_time_ms,
                "tool_calls": result.get("tool_call_count", 0),
                "workflow_execution": True,
                "modern_system": True,
                **result.get("metadata", {}),
            }

            # Update execution with success
            await workflow_mgmt.update_workflow_execution(
                execution_id=execution.id,
                owner_id=user_id,
                status="completed",
                completed_at=datetime.now(UTC),
                execution_time_ms=execution_time_ms,
                output_data={
                    "response": ai_message.content,
                    "conversation_id": conversation.id,
                    "metadata": result.get("metadata", {}),
                },
                tokens_used=result.get("tokens_used", 0),
                cost=result.get("cost", 0.0),
                execution_log=performance_monitor.debug_logs,
            )

            # Update monitoring metrics
            monitoring.update_workflow_metrics(
                workflow_id=workflow_id,
                token_usage={
                    chat_request.provider
                    or "unknown": result.get("tokens_used", 0)
                },
                tool_calls=result.get("tool_call_count", 0),
            )

            # Finish workflow tracking
            monitoring.finish_workflow_tracking(workflow_id)

            # Emit workflow completed event
            await _emit_event(
                UnifiedEvent(
                    category=EventCategory.WORKFLOW,
                    event_type="workflow_completed",
                    user_id=user_id,
                    session_id=conversation.id,
                    correlation_id=correlation_id,
                    data={
                        "workflow_id": workflow_id,
                        "execution_id": execution.id,
                        "tokens_used": result.get("tokens_used", 0),
                        "cost": result.get("cost", 0.0),
                        "execution_time_ms": execution_time_ms,
                        "success": True,
                    },
                )
            )

            logger.info(
                f"Dynamic workflow execution {execution.id} completed successfully"
            )

            return message, usage_info

        except Exception as e:
            # Update monitoring metrics with error
            monitoring.update_workflow_metrics(
                workflow_id=workflow_id,
                error=str(e),
            )
            monitoring.finish_workflow_tracking(workflow_id)

            # Emit workflow failed event
            await _emit_event(
                UnifiedEvent(
                    category=EventCategory.WORKFLOW,
                    event_type="workflow_failed",
                    user_id=user_id,
                    session_id=conversation.id,
                    correlation_id=correlation_id,
                    priority=EventPriority.HIGH,
                    data={
                        "workflow_id": workflow_id,
                        "execution_id": execution.id,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )
            )

            # Update execution with failure
            execution_time_ms = int((time.time() - start_time) * 1000)
            performance_monitor.log_debug(
                f"Execution failed: {str(e)}",
                data={"error_type": type(e).__name__},
            )

            try:
                await workflow_mgmt.update_workflow_execution(
                    execution_id=execution.id,
                    owner_id=user_id,
                    status="failed",
                    completed_at=datetime.now(UTC),
                    execution_time_ms=execution_time_ms,
                    error=str(e),
                    execution_log=performance_monitor.debug_logs,
                )
            except Exception as update_error:
                logger.error(
                    f"Failed to update execution status: {update_error}"
                )

            raise

    async def execute_chat_workflow_streaming(
        self,
        user_id: str,
        request: Any,  # ChatWorkflowRequest
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute a chat workflow with streaming using the universal template system."""
        try:
            # Get or create conversation
            conversation = await self._get_or_create_conversation(
                user_id, request
            )

            # Convert to ChatRequest for compatibility
            chat_request = self._convert_to_chat_request(request)

            # Try universal template first, fallback to dynamic creation
            try:
                async for (
                    chunk
                ) in self._execute_streaming_with_universal_template(
                    conversation=conversation,
                    chat_request=chat_request,
                    user_id=user_id,
                    request=request,
                ):
                    yield chunk
            except Exception as e:
                logger.warning(
                    f"Universal template streaming failed, falling back to dynamic creation: {e}"
                )
                async for (
                    chunk
                ) in self._execute_streaming_with_dynamic_workflow(
                    conversation=conversation,
                    chat_request=chat_request,
                    user_id=user_id,
                    request=request,
                ):
                    yield chunk

        except Exception as e:
            logger.error(f"Streaming workflow execution failed: {e}")
            yield StreamingChatChunk(
                type="error",
                content=f"Error: {str(e)}",
                metadata={"error": True},
            )

    async def _execute_streaming_with_universal_template(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        user_id: str,
        request: Any,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute streaming chat workflow using the universal template."""
        from chatter.services.workflow_management import (
            WorkflowManagementService,
        )

        # Create workflow management service
        workflow_mgmt = WorkflowManagementService(self.session)

        # Get the universal chat template
        templates = await workflow_mgmt.list_workflow_templates(
            owner_id=user_id
        )
        universal_template = None

        for template in templates:
            if (
                template.name == "universal_chat"
                and template.is_builtin
            ):
                universal_template = template
                break

        if not universal_template:
            raise Exception("Universal chat template not found")

        # Prepare template parameters from chat request
        template_params = {
            "provider": chat_request.provider,
            "model": chat_request.model,
            "temperature": chat_request.temperature,
            "max_tokens": chat_request.max_tokens,
            "system_message": chat_request.system_prompt_override,
            "enable_memory": chat_request.enable_memory,
            "enable_retrieval": chat_request.enable_retrieval,
            "enable_tools": chat_request.enable_tools,
            "enable_streaming": True,
            "memory_window": getattr(chat_request, 'memory_window', 10),
            "max_tool_calls": getattr(
                chat_request, 'max_tool_calls', 10
            ),
            "workflow_type": "universal_chat",
        }

        # Create workflow definition from template
        definition = await workflow_mgmt.create_workflow_definition_from_template(
            template_id=universal_template.id,
            owner_id=user_id,
            name_suffix="Streaming Execution",
            user_input=template_params,
            is_temporary=True,
        )

        # Create workflow execution record
        execution = await workflow_mgmt.create_workflow_execution(
            definition_id=definition.id,
            owner_id=user_id,
            input_data={
                "message": chat_request.message,
                "conversation_id": conversation.id,
                "provider": chat_request.provider,
                "model": chat_request.model,
                "streaming": True,
            },
        )

        # Initialize performance monitor for tracking
        performance_monitor = PerformanceMonitor(debug_mode=True)
        performance_monitor.log_debug(
            "Started universal template streaming execution",
            data={
                "execution_id": execution.id,
                "template_id": universal_template.id,
                "conversation_id": conversation.id,
            },
        )

        start_time = time.time()
        try:
            # Update execution status to running
            execution = await workflow_mgmt.update_workflow_execution(
                execution_id=execution.id,
                owner_id=user_id,
                status="running",
                started_at=datetime.fromtimestamp(start_time, UTC),
            )

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
                        user_permissions=[],  # TODO: Add user permission system
                    )
                    logger.info(
                        f"Loaded {len(tools) if tools else 0} tools for universal template streaming"
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not load tools from tool registry: {e}"
                    )
                    tools = []

            if chat_request.enable_retrieval:
                try:
                    from chatter.core.vector_store import (
                        get_vector_store_retriever,
                    )

                    retriever = await get_vector_store_retriever(
                        user_id=user_id
                    )
                    logger.info(
                        "Loaded retriever from vector store for universal template streaming"
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not load retriever from vector store: {e}"
                    )
                    retriever = None

            # Create workflow from definition
            # Convert database WorkflowDefinition to graph builder WorkflowDefinition
            graph_definition = create_workflow_definition_from_model(
                definition
            )
            workflow = (
                await workflow_manager.create_workflow_from_definition(
                    definition=graph_definition,
                    llm=llm,
                    retriever=retriever,
                    tools=tools,
                    max_tool_calls=getattr(
                        chat_request, 'max_tool_calls', 10
                    ),
                    user_id=user_id,
                    conversation_id=conversation.id,
                )
            )

            performance_monitor.log_debug(
                "Workflow created from universal template for streaming",
                data={"definition_id": definition.id},
            )

            # Get conversation history and create initial state
            messages = await self._get_conversation_messages(
                conversation
            )
            messages.append(HumanMessage(content=request.message))

            initial_state: WorkflowNodeContext = {
                "messages": messages,
                "user_id": user_id,
                "conversation_id": conversation.id,
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": {
                    "universal_template": True,
                    "template_id": universal_template.id,
                },
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
            }

            # Stream workflow execution
            performance_monitor.log_debug(
                "Starting streaming workflow execution"
            )

            content_buffer = ""
            async for update in workflow_manager.stream_workflow(
                workflow=workflow,
                initial_state=initial_state,
                thread_id=conversation.id,
                enable_llm_streaming=True,
            ):
                # Handle LangGraph streaming events
                if isinstance(update, dict):
                    event_name = update.get("event", "")

                    # Handle chat model start event
                    if event_name == "on_chat_model_start":
                        # Extract metadata from the start event
                        metadata = update.get("metadata", {})
                        yield StreamingChatChunk(
                            type="start",
                            content="",
                            conversation_id=conversation.id,
                            metadata={
                                "universal_template": True,
                                "model_name": metadata.get(
                                    "ls_model_name"
                                ),
                                "temperature": metadata.get(
                                    "ls_temperature"
                                ),
                                "max_tokens": metadata.get(
                                    "ls_max_tokens"
                                ),
                            },
                        )

                    # Handle chat model and LLM streaming events
                    elif event_name in [
                        "on_chat_model_stream",
                        "on_llm_stream",
                    ]:
                        # Extract the chunk from the event data
                        data = update.get("data", {})
                        chunk = data.get("chunk", {})

                        # Get content from the chunk
                        if hasattr(chunk, "content"):
                            content = chunk.content
                        elif isinstance(chunk, dict):
                            content = chunk.get("content", "")
                        else:
                            content = str(chunk) if chunk else ""

                        if content:
                            content_buffer += content
                            yield StreamingChatChunk(
                                type="token",
                                content=content,
                                metadata={
                                    "universal_template": True,
                                    "event": event_name,
                                },
                            )

                    # Handle chat model end event
                    elif event_name == "on_chat_model_end":
                        # Extract usage metadata from the end event
                        data = update.get("data", {})
                        output = data.get("output", {})

                        # Get usage_metadata from the output
                        usage_metadata = {}
                        if hasattr(output, "usage_metadata"):
                            usage_metadata = output.usage_metadata or {}
                        elif isinstance(output, dict):
                            usage_metadata = output.get(
                                "usage_metadata", {}
                            )

                        # Get response_metadata for model info
                        response_metadata = {}
                        if hasattr(output, "response_metadata"):
                            response_metadata = (
                                output.response_metadata or {}
                            )
                        elif isinstance(output, dict):
                            response_metadata = output.get(
                                "response_metadata", {}
                            )

                        yield StreamingChatChunk(
                            type="complete",
                            content="",
                            metadata={
                                "streaming_complete": True,
                                "universal_template": True,
                                "total_tokens": (
                                    usage_metadata.get("total_tokens")
                                    if isinstance(usage_metadata, dict)
                                    else getattr(
                                        usage_metadata,
                                        "total_tokens",
                                        None,
                                    )
                                ),
                                "input_tokens": (
                                    usage_metadata.get("input_tokens")
                                    if isinstance(usage_metadata, dict)
                                    else getattr(
                                        usage_metadata,
                                        "input_tokens",
                                        None,
                                    )
                                ),
                                "output_tokens": (
                                    usage_metadata.get("output_tokens")
                                    if isinstance(usage_metadata, dict)
                                    else getattr(
                                        usage_metadata,
                                        "output_tokens",
                                        None,
                                    )
                                ),
                                "model_used": (
                                    response_metadata.get("model_name")
                                    if isinstance(
                                        response_metadata, dict
                                    )
                                    else getattr(
                                        response_metadata,
                                        "model_name",
                                        None,
                                    )
                                ),
                                "finish_reason": (
                                    response_metadata.get(
                                        "finish_reason"
                                    )
                                    if isinstance(
                                        response_metadata, dict
                                    )
                                    else getattr(
                                        response_metadata,
                                        "finish_reason",
                                        None,
                                    )
                                ),
                            },
                        )

            performance_monitor.log_debug(
                "Streaming workflow execution completed",
                data={"content_length": len(content_buffer)},
            )

            # Send done marker
            yield StreamingChatChunk(
                type="done",
                content="",
                metadata={},
            )

            # Update execution with success
            execution_time_ms = int((time.time() - start_time) * 1000)
            await workflow_mgmt.update_workflow_execution(
                execution_id=execution.id,
                owner_id=user_id,
                status="completed",
                completed_at=datetime.now(UTC),
                execution_time_ms=execution_time_ms,
                output_data={
                    "response": content_buffer,
                    "conversation_id": conversation.id,
                    "streaming": True,
                },
                execution_log=performance_monitor.debug_logs,
            )

            logger.info(
                f"Universal template streaming execution {execution.id} completed successfully"
            )

        except Exception as e:
            # Update execution with failure
            execution_time_ms = int((time.time() - start_time) * 1000)
            performance_monitor.log_debug(
                f"Streaming execution failed: {str(e)}",
                data={"error_type": type(e).__name__},
            )

            try:
                await workflow_mgmt.update_workflow_execution(
                    execution_id=execution.id,
                    owner_id=user_id,
                    status="failed",
                    completed_at=datetime.now(UTC),
                    execution_time_ms=execution_time_ms,
                    error=str(e),
                    execution_log=performance_monitor.debug_logs,
                )
            except Exception as update_error:
                logger.error(
                    f"Failed to update execution status: {update_error}"
                )

            raise

    async def _execute_streaming_with_dynamic_workflow(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        user_id: str,
        request: Any,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Fallback method using dynamic workflow creation for streaming."""
        from chatter.services.workflow_management import (
            WorkflowManagementService,
        )

        # Create workflow management service
        workflow_mgmt = WorkflowManagementService(self.session)

        # Create a simple workflow definition for tracking purposes
        # Since this is dynamic, we create a minimal definition
        definition = await workflow_mgmt.create_workflow_definition(
            owner_id=user_id,
            name="Dynamic Chat Workflow (Streaming)",
            description="Dynamically created chat workflow for streaming execution tracking",
            nodes=[
                {
                    "id": "call_model",
                    "type": "model",
                    "config": {
                        "provider": chat_request.provider,
                        "model": chat_request.model,
                        "temperature": chat_request.temperature,
                        "max_tokens": chat_request.max_tokens,
                    },
                }
            ],
            edges=[{"source": "call_model", "target": "END"}],
            metadata={
                "dynamic": True,
                "execution_only": True,  # Mark as execution-only definition
                "streaming": True,
                "enable_memory": chat_request.enable_memory,
                "enable_retrieval": chat_request.enable_retrieval,
                "enable_tools": chat_request.enable_tools,
            },
        )

        # Create workflow execution record
        execution = await workflow_mgmt.create_workflow_execution(
            definition_id=definition.id,
            owner_id=user_id,
            input_data={
                "message": chat_request.message,
                "conversation_id": conversation.id,
                "provider": chat_request.provider,
                "model": chat_request.model,
                "streaming": True,
            },
        )

        # Initialize performance monitor for tracking
        performance_monitor = PerformanceMonitor(debug_mode=True)
        performance_monitor.log_debug(
            "Started dynamic workflow streaming execution",
            data={
                "execution_id": execution.id,
                "conversation_id": conversation.id,
            },
        )

        start_time = time.time()

        try:
            # Update execution status to running
            execution = await workflow_mgmt.update_workflow_execution(
                execution_id=execution.id,
                owner_id=user_id,
                status="running",
                started_at=datetime.fromtimestamp(start_time, UTC),
            )

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

            performance_monitor.log_debug(
                "Dynamic workflow created for streaming",
                data={"definition_id": definition.id},
            )

            # Get conversation history and create initial state
            messages = await self._get_conversation_messages(
                conversation
            )
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
            performance_monitor.log_debug(
                "Starting streaming workflow execution"
            )

            content_buffer = ""
            async for update in workflow_manager.stream_workflow(
                workflow=workflow,
                initial_state=initial_state,
                thread_id=conversation.id,
                enable_llm_streaming=True,
            ):
                # Handle LangGraph streaming events
                if isinstance(update, dict):
                    event_name = update.get("event", "")

                    # Handle chat model start event
                    if event_name == "on_chat_model_start":
                        # Extract metadata from the start event
                        metadata = update.get("metadata", {})
                        yield StreamingChatChunk(
                            type="start",
                            content="",
                            conversation_id=conversation.id,
                            metadata={
                                "model_name": metadata.get(
                                    "ls_model_name"
                                ),
                                "temperature": metadata.get(
                                    "ls_temperature"
                                ),
                                "max_tokens": metadata.get(
                                    "ls_max_tokens"
                                ),
                            },
                        )

                    # Handle chat model and LLM streaming events
                    elif event_name in [
                        "on_chat_model_stream",
                        "on_llm_stream",
                    ]:
                        # Extract the chunk from the event data
                        data = update.get("data", {})
                        chunk = data.get("chunk", {})

                        # Get content from the chunk
                        if hasattr(chunk, "content"):
                            content = chunk.content
                        elif isinstance(chunk, dict):
                            content = chunk.get("content", "")
                        else:
                            content = str(chunk) if chunk else ""

                        if content:
                            content_buffer += content
                            yield StreamingChatChunk(
                                type="token",
                                content=content,
                                metadata={
                                    "event": event_name,
                                },
                            )

                    # Handle chat model end event
                    elif event_name == "on_chat_model_end":
                        # Extract usage metadata from the end event
                        data = update.get("data", {})
                        output = data.get("output", {})

                        # Get usage_metadata from the output
                        usage_metadata = {}
                        if hasattr(output, "usage_metadata"):
                            usage_metadata = output.usage_metadata or {}
                        elif isinstance(output, dict):
                            usage_metadata = output.get(
                                "usage_metadata", {}
                            )

                        # Get response_metadata for model info
                        response_metadata = {}
                        if hasattr(output, "response_metadata"):
                            response_metadata = (
                                output.response_metadata or {}
                            )
                        elif isinstance(output, dict):
                            response_metadata = output.get(
                                "response_metadata", {}
                            )

                        yield StreamingChatChunk(
                            type="complete",
                            content="",
                            metadata={
                                "streaming_complete": True,
                                "total_tokens": (
                                    usage_metadata.get("total_tokens")
                                    if isinstance(usage_metadata, dict)
                                    else getattr(
                                        usage_metadata,
                                        "total_tokens",
                                        None,
                                    )
                                ),
                                "input_tokens": (
                                    usage_metadata.get("input_tokens")
                                    if isinstance(usage_metadata, dict)
                                    else getattr(
                                        usage_metadata,
                                        "input_tokens",
                                        None,
                                    )
                                ),
                                "output_tokens": (
                                    usage_metadata.get("output_tokens")
                                    if isinstance(usage_metadata, dict)
                                    else getattr(
                                        usage_metadata,
                                        "output_tokens",
                                        None,
                                    )
                                ),
                                "model_used": (
                                    response_metadata.get("model_name")
                                    if isinstance(
                                        response_metadata, dict
                                    )
                                    else getattr(
                                        response_metadata,
                                        "model_name",
                                        None,
                                    )
                                ),
                                "finish_reason": (
                                    response_metadata.get(
                                        "finish_reason"
                                    )
                                    if isinstance(
                                        response_metadata, dict
                                    )
                                    else getattr(
                                        response_metadata,
                                        "finish_reason",
                                        None,
                                    )
                                ),
                            },
                        )

            performance_monitor.log_debug(
                "Streaming workflow execution completed",
                data={"content_length": len(content_buffer)},
            )

            # Send done marker
            yield StreamingChatChunk(
                type="done",
                content="",
                metadata={},
            )

            # Update execution with success
            execution_time_ms = int((time.time() - start_time) * 1000)
            await workflow_mgmt.update_workflow_execution(
                execution_id=execution.id,
                owner_id=user_id,
                status="completed",
                completed_at=datetime.now(UTC),
                execution_time_ms=execution_time_ms,
                output_data={
                    "response": content_buffer,
                    "conversation_id": conversation.id,
                    "streaming": True,
                },
                execution_log=performance_monitor.debug_logs,
            )

            logger.info(
                f"Dynamic workflow streaming execution {execution.id} completed successfully"
            )

        except Exception as e:
            # Update execution with failure
            execution_time_ms = int((time.time() - start_time) * 1000)
            performance_monitor.log_debug(
                f"Streaming execution failed: {str(e)}",
                data={"error_type": type(e).__name__},
            )

            try:
                await workflow_mgmt.update_workflow_execution(
                    execution_id=execution.id,
                    owner_id=user_id,
                    status="failed",
                    completed_at=datetime.now(UTC),
                    execution_time_ms=execution_time_ms,
                    error=str(e),
                    execution_log=performance_monitor.debug_logs,
                )
            except Exception as update_error:
                logger.error(
                    f"Failed to update execution status: {update_error}"
                )

            raise

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
            llm = await self.llm_service.get_llm(
                provider=provider, model=model
            )

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

        # Initialize performance monitor with debug logging
        performance_monitor = PerformanceMonitor(debug_mode=debug_mode)
        performance_monitor.log_debug(
            f"Started workflow execution for definition {definition_id}",
            data={"execution_id": execution.id, "user_id": user_id},
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
        self, user_id: str, request: Any
    ) -> Conversation:
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

    def _convert_to_chat_request(self, request: Any) -> ChatRequest:
        """Convert workflow request to ChatRequest for compatibility."""
        return ChatRequest(
            message=request.message,
            conversation_id=getattr(request, 'conversation_id', None),
            provider=getattr(
                request, 'provider', None
            ),  # Let system choose default
            model=getattr(
                request, 'model', None
            ),  # Let system choose default
            temperature=getattr(request, 'temperature', None),
            max_tokens=getattr(request, 'max_tokens', None),
            system_prompt_override=getattr(
                request, 'system_prompt_override', None
            ),
            enable_retrieval=getattr(
                request, 'enable_retrieval', False
            ),
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
