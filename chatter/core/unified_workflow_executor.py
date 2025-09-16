"""Unified workflow executor that consolidates all workflow types.

This replaces the multiple individual executors with a single configurable
executor that handles all workflow types (plain, rag, tools, full) while
eliminating code duplication.
"""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import AIMessage

from chatter.core.dependencies import get_workflow_manager
from chatter.core.langgraph import ConversationState
from chatter.core.monitoring import record_workflow_metrics
from chatter.core.workflow_limits import (
    WorkflowLimits,
    WorkflowResourceLimitError,
    workflow_limit_manager,
)
from chatter.core.workflow_performance import performance_monitor
from chatter.models.conversation import (
    Conversation,
    Message,
    MessageRole,
)
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowExecutionError(Exception):
    """Workflow execution error."""
    pass


class UnifiedWorkflowExecutor:
    """Unified workflow executor that handles all workflow types."""

    def __init__(
        self,
        llm_service: LLMService,
        message_service: MessageService,
        template_manager,
    ):
        """Initialize unified workflow executor."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.template_manager = template_manager
        self.limit_manager = workflow_limit_manager

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute workflow for any type."""
        workflow_type = chat_request.workflow_type or chat_request.workflow or "plain"
        start_time = time.time()
        workflow_id, limits = await self._setup_execution(
            conversation, chat_request, correlation_id, user_id, limits, workflow_type
        )

        try:
            performance_monitor.start_workflow(workflow_id, workflow_type)

            # Get workflow configuration based on type
            workflow_config = self._get_workflow_config(workflow_type, conversation, chat_request)
            
            # Create unified workflow
            workflow = await self.llm_service.create_langgraph_workflow(
                provider_name=chat_request.provider,
                workflow_type=workflow_type,
                **workflow_config,
                system_message=chat_request.system_prompt_override,
                temperature=chat_request.temperature,
                max_tokens=chat_request.max_tokens,
            )

            # Prepare conversation context
            user_id = user_id or conversation.user_id
            if user_id is None:
                raise WorkflowExecutionError(
                    "No user_id provided and conversation has no associated user_id"
                )

            messages = await self._prepare_messages(
                conversation, chat_request, user_id, workflow_config["memory_window"]
            )

            # Execute workflow
            state = ConversationState(messages=messages)
            result = await workflow.ainvoke(
                state, {"configurable": {"thread_id": conversation.id}}
            )

            # Extract response
            response_content = self._extract_response_content(result)

            # Create response message
            assistant_message = await self.message_service.add_message_to_conversation(
                conversation_id=conversation.id,
                user_id=user_id,
                role=MessageRole.ASSISTANT,
                content=response_content,
                metadata=(
                    {"correlation_id": correlation_id}
                    if correlation_id
                    else None
                ),
            )

            # Record success metrics
            await self._record_metrics(
                workflow_id, "execute", start_time, True, workflow_type, correlation_id=correlation_id
            )

            return assistant_message, {"usage": result.get("usage", {})}

        except Exception as e:
            # Record error metrics
            await self._record_metrics(
                workflow_id, "execute", start_time, False, workflow_type,
                error_type=type(e).__name__, correlation_id=correlation_id
            )
            raise WorkflowExecutionError(
                f"{workflow_type.title()} workflow execution failed: {str(e)}"
            ) from e
        finally:
            # Clean up resource tracking
            if user_id:
                self.limit_manager.end_workflow_tracking(workflow_id, user_id)

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute workflow with streaming for any type."""
        workflow_type = chat_request.workflow_type or chat_request.workflow or "plain"
        start_time = time.time()
        workflow_id, limits = await self._setup_execution(
            conversation, chat_request, correlation_id, user_id, limits, workflow_type
        )

        try:
            performance_monitor.start_workflow(workflow_id, workflow_type)

            # Get workflow configuration based on type
            workflow_config = self._get_workflow_config(workflow_type, conversation, chat_request)
            
            # Create unified streaming workflow
            workflow = await self.llm_service.create_langgraph_workflow(
                provider_name=chat_request.provider,
                workflow_type=workflow_type,
                **workflow_config,
                system_message=chat_request.system_prompt_override,
                temperature=chat_request.temperature,
                max_tokens=chat_request.max_tokens,
            )

            # Prepare conversation context
            user_id = user_id or conversation.user_id
            if user_id is None:
                raise WorkflowExecutionError(
                    "No user_id provided and conversation has no associated user_id"
                )

            messages = await self._prepare_messages(
                conversation, chat_request, user_id, workflow_config["memory_window"]
            )
            state = ConversationState(messages=messages)

            # Create message for streaming and send start chunk
            streaming_message = await self._create_streaming_message(
                conversation, user_id, correlation_id
            )
            yield await self._send_streaming_start_chunk(
                streaming_message, conversation, correlation_id
            )

            # Stream workflow execution
            content_buffer = ""
            async for event in workflow.astream(
                state, {"configurable": {"thread_id": conversation.id}}
            ):
                # Look for messages in any node's output
                messages_found = None
                for node_name, node_output in event.items():
                    if isinstance(node_output, dict) and "messages" in node_output:
                        messages_found = node_output["messages"]
                        break
                
                if messages_found:
                    message = messages_found[-1]
                    if hasattr(message, "content") and message.content:
                        # Extract new content since last chunk
                        if len(message.content) > len(content_buffer):
                            new_content = message.content[len(content_buffer):]
                            content_buffer = message.content

                            yield await self._send_streaming_token_chunk(
                                new_content, streaming_message, conversation, correlation_id
                            )

            # Finalize streaming message and send completion chunk
            yield await self._finalize_streaming_message(
                streaming_message, content_buffer, conversation, correlation_id
            )

            # Record success metrics
            await self._record_metrics(
                workflow_id, "stream", start_time, True, workflow_type, correlation_id=correlation_id
            )

        except Exception as e:
            # Record error metrics
            await self._record_metrics(
                workflow_id, "stream", start_time, False, workflow_type,
                error_type=type(e).__name__, correlation_id=correlation_id
            )
            raise WorkflowExecutionError(
                f"{workflow_type.title()} workflow streaming failed: {str(e)}"
            ) from e
        finally:
            # Clean up resource tracking
            if user_id:
                self.limit_manager.end_workflow_tracking(workflow_id, user_id)

    def _get_workflow_config(
        self, workflow_type: str, conversation: Conversation, chat_request: ChatRequest
    ) -> dict[str, Any]:
        """Get configuration for specific workflow type."""
        # Base configuration
        config = {
            "enable_memory": True,
            "tools": None,
            "retriever": None,
        }

        # Get workspace ID for tool and retriever lookup
        workspace_id = conversation.workspace_id or "default"
        workflow_manager = get_workflow_manager()

        # Configure based on workflow type
        if workflow_type == "plain":
            config.update({
                "memory_window": 20,
            })
        elif workflow_type == "rag":
            config.update({
                "memory_window": 30,
                "max_documents": 10,
            })
            # Only get retriever if retrieval is enabled
            if chat_request.enable_retrieval is not False:
                config["retriever"] = workflow_manager.get_retriever(
                    workspace_id, document_ids=chat_request.document_ids
                )
        elif workflow_type == "tools":
            config.update({
                "memory_window": 100,
                "max_tool_calls": 10,
                "tools": workflow_manager.get_tools(workspace_id),
            })
        elif workflow_type == "full":
            config.update({
                "memory_window": 50,
                "max_tool_calls": 5,
                "max_documents": 10,
                "tools": workflow_manager.get_tools(workspace_id),
            })
            # Only get retriever if retrieval is enabled
            if chat_request.enable_retrieval is not False:
                config["retriever"] = workflow_manager.get_retriever(
                    workspace_id, document_ids=chat_request.document_ids
                )
        else:
            # Unknown workflow type - use plain config as fallback
            logger.warning(f"Unknown workflow type '{workflow_type}', using plain config")
            config.update({
                "memory_window": 20,
            })

        return config

    async def _setup_execution(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None,
        limits: WorkflowLimits | None,
        workflow_type: str,
    ) -> tuple[str, WorkflowLimits]:
        """Common setup for workflow execution."""
        workflow_id = f"{correlation_id}_{workflow_type}"

        # Use provided limits or get defaults
        if limits is None:
            limits = self.limit_manager.get_default_limits()

        # Start resource tracking if user_id provided
        if user_id:
            try:
                self.limit_manager.start_workflow_tracking(workflow_id, user_id, limits)
            except WorkflowResourceLimitError as e:
                logger.warning(
                    "Workflow rejected due to resource limits",
                    extra={
                        "user_id": user_id,
                        "error": str(e),
                        "correlation_id": correlation_id,
                    },
                )
                raise WorkflowExecutionError(f"Resource limit exceeded: {e}") from e

        return workflow_id, limits

    async def _prepare_messages(
        self, conversation: Conversation, chat_request: ChatRequest, user_id: str, memory_window: int
    ) -> list[dict[str, str]]:
        """Prepare conversation messages for workflow execution."""
        messages = []

        recent_messages = await self.message_service.get_recent_messages(
            conversation.id, user_id, limit=memory_window
        )

        for msg in recent_messages:
            if msg.role == MessageRole.USER:
                messages.append({"role": "human", "content": msg.content})
            elif msg.role == MessageRole.ASSISTANT:
                messages.append({"role": "ai", "content": msg.content})

        # Add current message
        messages.append({"role": "human", "content": chat_request.message})
        return messages

    def _extract_response_content(self, result: dict[str, Any]) -> str:
        """Extract response content from workflow result."""
        if isinstance(result["messages"][-1], AIMessage):
            return result["messages"][-1].content
        else:
            return str(result["messages"][-1])

    async def _create_streaming_message(
        self, conversation: Conversation, user_id: str, correlation_id: str
    ) -> Message:
        """Create a placeholder message for streaming."""
        return await self.message_service.add_message_to_conversation(
            conversation_id=conversation.id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content="",  # Empty content initially
            metadata=(
                {"correlation_id": correlation_id} if correlation_id else None
            ),
        )

    async def _send_streaming_start_chunk(
        self, message: Message, conversation: Conversation, correlation_id: str
    ) -> StreamingChatChunk:
        """Send start chunk with proper message ID."""
        return StreamingChatChunk(
            type="start",
            content="",
            message_id=message.id,
            conversation_id=conversation.id,
            correlation_id=correlation_id,
        )

    async def _send_streaming_token_chunk(
        self, content: str, message: Message, conversation: Conversation, correlation_id: str
    ) -> StreamingChatChunk:
        """Send token chunk with proper message ID."""
        return StreamingChatChunk(
            type="token",
            content=content,
            message_id=message.id,
            conversation_id=conversation.id,
            correlation_id=correlation_id,
        )

    async def _finalize_streaming_message(
        self, message: Message, final_content: str, conversation: Conversation, correlation_id: str
    ) -> StreamingChatChunk:
        """Update message with final content and send completion chunk."""
        if final_content:
            await self.message_service.update_message_content(message.id, final_content)

        return StreamingChatChunk(
            type="complete",
            content="",
            message_id=message.id,
            conversation_id=conversation.id,
            correlation_id=correlation_id,
            metadata={
                "final_content": final_content,
                "message_complete": True
            }
        )

    async def _record_metrics(
        self,
        workflow_id: str,
        step: str,
        start_time: float,
        success: bool,
        workflow_type: str,
        error_type: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Record workflow execution metrics."""
        duration_ms = (time.time() - start_time) * 1000
        record_workflow_metrics(
            workflow_type=workflow_type,
            workflow_id=workflow_id,
            step=step,
            duration_ms=duration_ms,
            success=success,
            error_type=error_type,
            correlation_id=correlation_id or "",
        )

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported workflow types."""
        return ["plain", "basic", "rag", "tools", "full"]