"""Workflow execution service - handles chat workflows and streaming."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage

from chatter.core.dependencies import get_workflow_manager
from chatter.core.langgraph import ConversationState
from chatter.core.workflow_performance import (
    performance_monitor,
    workflow_cache,
)
from chatter.core.workflow_templates import WorkflowTemplateManager
from chatter.core.workflow_validation import WorkflowValidator
from chatter.models.conversation import Conversation, Message, MessageRole
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.utils.logging import get_logger
from chatter.utils.monitoring import record_workflow_metrics
from chatter.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


class WorkflowExecutionError(Exception):
    """Workflow execution error."""
    pass


class WorkflowExecutionService:
    """Service for executing chat workflows with various types and streaming."""

    def __init__(self, llm_service: LLMService, message_service: MessageService):
        """Initialize workflow execution service."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.template_manager = WorkflowTemplateManager()
        self.validator = WorkflowValidator()

    async def execute_workflow(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str
    ) -> tuple[Message, dict[str, Any]]:
        """Execute a workflow for a chat request.

        Args:
            conversation: Conversation context
            chat_request: Chat request
            correlation_id: Request correlation ID

        Returns:
            Tuple of (response_message, usage_info)

        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        start_time = time.time()
        workflow_type = chat_request.workflow_type or "plain"
        
        try:
            # Validate workflow configuration
            if not self.validator.validate_workflow_config(
                workflow_type, chat_request.workflow_config or {}
            ):
                raise WorkflowExecutionError(f"Invalid workflow configuration for {workflow_type}")

            # Check cache first
            cache_key = self._get_cache_key(conversation.id, chat_request)
            cached_result = await workflow_cache.get(cache_key)
            
            if cached_result:
                logger.debug(
                    "Workflow cache hit",
                    conversation_id=conversation.id,
                    workflow_type=workflow_type,
                    correlation_id=correlation_id
                )
                
                # Record metrics for cached result
                duration_ms = (time.time() - start_time) * 1000
                record_workflow_metrics(
                    workflow_type=workflow_type,
                    workflow_id=conversation.id,
                    step="cache_hit",
                    duration_ms=duration_ms,
                    success=True,
                    error_type=None,
                    correlation_id=correlation_id
                )
                
                return cached_result

            # Execute workflow based on type
            with performance_monitor.track_operation(f"workflow_{workflow_type}"):
                if workflow_type == "plain":
                    result = await self._execute_plain_workflow(
                        conversation, chat_request, correlation_id
                    )
                elif workflow_type == "rag":
                    result = await self._execute_rag_workflow(
                        conversation, chat_request, correlation_id
                    )
                elif workflow_type == "tools":
                    result = await self._execute_tools_workflow(
                        conversation, chat_request, correlation_id
                    )
                elif workflow_type == "full":
                    result = await self._execute_full_workflow(
                        conversation, chat_request, correlation_id
                    )
                else:
                    raise WorkflowExecutionError(f"Unknown workflow type: {workflow_type}")

            # Cache the result
            await workflow_cache.set(cache_key, result, ttl=300)  # 5 minutes

            # Record successful execution metrics
            duration_ms = (time.time() - start_time) * 1000
            record_workflow_metrics(
                workflow_type=workflow_type,
                workflow_id=conversation.id,
                step="complete",
                duration_ms=duration_ms,
                success=True,
                error_type=None,
                correlation_id=correlation_id
            )

            logger.info(
                "Workflow executed successfully",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                duration_ms=duration_ms,
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            # Record failed execution metrics
            duration_ms = (time.time() - start_time) * 1000
            record_workflow_metrics(
                workflow_type=workflow_type,
                workflow_id=conversation.id,
                step="error",
                duration_ms=duration_ms,
                success=False,
                error_type=type(e).__name__,
                correlation_id=correlation_id
            )

            logger.error(
                "Workflow execution failed",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                error=str(e),
                correlation_id=correlation_id
            )
            raise WorkflowExecutionError(f"Workflow execution failed: {e}")

    async def execute_workflow_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute a workflow with streaming response.

        Args:
            conversation: Conversation context
            chat_request: Chat request
            correlation_id: Request correlation ID

        Yields:
            Streaming chat chunks

        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        start_time = time.time()
        workflow_type = chat_request.workflow_type or "plain"
        
        try:
            # Validate workflow configuration
            if not self.validator.validate_workflow_config(
                workflow_type, chat_request.workflow_config or {}
            ):
                raise WorkflowExecutionError(f"Invalid workflow configuration for {workflow_type}")

            logger.info(
                "Starting streaming workflow execution",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                correlation_id=correlation_id
            )

            # Execute streaming workflow based on type
            async for chunk in self._execute_streaming_workflow(
                workflow_type, conversation, chat_request, correlation_id
            ):
                yield chunk

            # Record successful streaming metrics
            duration_ms = (time.time() - start_time) * 1000
            record_workflow_metrics(
                workflow_type=f"{workflow_type}_streaming",
                workflow_id=conversation.id,
                step="complete",
                duration_ms=duration_ms,
                success=True,
                error_type=None,
                correlation_id=correlation_id
            )

            logger.info(
                "Streaming workflow completed successfully",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                duration_ms=duration_ms,
                correlation_id=correlation_id
            )

        except Exception as e:
            # Record failed streaming metrics
            duration_ms = (time.time() - start_time) * 1000
            record_workflow_metrics(
                workflow_type=f"{workflow_type}_streaming",
                workflow_id=conversation.id,
                step="error",
                duration_ms=duration_ms,
                success=False,
                error_type=type(e).__name__,
                correlation_id=correlation_id
            )

            logger.error(
                "Streaming workflow execution failed",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                error=str(e),
                correlation_id=correlation_id
            )
            
            # Yield error chunk
            yield StreamingChatChunk(
                type="error",
                content=f"Workflow execution failed: {str(e)}",
                correlation_id=correlation_id
            )

    async def _execute_plain_workflow(
        self, conversation: Conversation, chat_request: ChatRequest, correlation_id: str
    ) -> tuple[Message, dict[str, Any]]:
        """Execute plain chat workflow."""
        messages = self.llm_service.convert_conversation_to_messages(
            conversation, await self._get_conversation_messages(conversation)
        )
        
        # Add user message
        messages.append(BaseMessage(content=chat_request.message, type="human"))
        
        # Get LLM provider
        provider = await self.llm_service.get_default_provider()
        
        # Generate response
        response = await provider.ainvoke(messages)
        
        # Create response message
        response_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=response.content,
            provider=provider.__class__.__name__,
            metadata={"workflow_type": "plain"}
        )
        
        usage_info = {"tokens": 0, "cost": 0.0}
        return response_message, usage_info

    async def _execute_rag_workflow(
        self, conversation: Conversation, chat_request: ChatRequest, correlation_id: str
    ) -> tuple[Message, dict[str, Any]]:
        """Execute RAG workflow."""
        workflow_manager = get_workflow_manager()
        
        # Prepare state
        state = ConversationState(
            conversation_id=conversation.id,
            messages=await self._get_conversation_messages(conversation),
            user_message=chat_request.message,
            workflow_config=chat_request.workflow_config or {},
            correlation_id=correlation_id
        )
        
        # Run RAG workflow
        result = await workflow_manager.run_workflow("rag", state)
        
        # Extract response
        ai_message = result.get("response")
        if not isinstance(ai_message, AIMessage):
            raise WorkflowExecutionError("Invalid RAG workflow response")
        
        response_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=ai_message.content,
            metadata={
                "workflow_type": "rag",
                "sources": result.get("sources", []),
                "documents_used": result.get("documents_used", 0)
            }
        )
        
        usage_info = result.get("usage", {"tokens": 0, "cost": 0.0})
        return response_message, usage_info

    async def _execute_tools_workflow(
        self, conversation: Conversation, chat_request: ChatRequest, correlation_id: str
    ) -> tuple[Message, dict[str, Any]]:
        """Execute tools workflow."""
        workflow_manager = get_workflow_manager()
        
        # Prepare state
        state = ConversationState(
            conversation_id=conversation.id,
            messages=await self._get_conversation_messages(conversation),
            user_message=chat_request.message,
            workflow_config=chat_request.workflow_config or {},
            correlation_id=correlation_id
        )
        
        # Run tools workflow
        result = await workflow_manager.run_workflow("tools", state)
        
        # Extract response
        ai_message = result.get("response")
        if not isinstance(ai_message, AIMessage):
            raise WorkflowExecutionError("Invalid tools workflow response")
        
        response_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=ai_message.content,
            metadata={
                "workflow_type": "tools",
                "tools_used": result.get("tools_used", []),
                "tool_calls": result.get("tool_calls", 0)
            }
        )
        
        usage_info = result.get("usage", {"tokens": 0, "cost": 0.0})
        return response_message, usage_info

    async def _execute_full_workflow(
        self, conversation: Conversation, chat_request: ChatRequest, correlation_id: str
    ) -> tuple[Message, dict[str, Any]]:
        """Execute full workflow (RAG + tools)."""
        workflow_manager = get_workflow_manager()
        
        # Prepare state
        state = ConversationState(
            conversation_id=conversation.id,
            messages=await self._get_conversation_messages(conversation),
            user_message=chat_request.message,
            workflow_config=chat_request.workflow_config or {},
            correlation_id=correlation_id
        )
        
        # Run full workflow
        result = await workflow_manager.run_workflow("full", state)
        
        # Extract response
        ai_message = result.get("response")
        if not isinstance(ai_message, AIMessage):
            raise WorkflowExecutionError("Invalid full workflow response")
        
        response_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=ai_message.content,
            metadata={
                "workflow_type": "full",
                "sources": result.get("sources", []),
                "tools_used": result.get("tools_used", []),
                "documents_used": result.get("documents_used", 0),
                "tool_calls": result.get("tool_calls", 0)
            }
        )
        
        usage_info = result.get("usage", {"tokens": 0, "cost": 0.0})
        return response_message, usage_info

    async def _execute_streaming_workflow(
        self,
        workflow_type: str,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute streaming workflow."""
        workflow_manager = get_workflow_manager()
        
        # Prepare state
        state = ConversationState(
            conversation_id=conversation.id,
            messages=await self._get_conversation_messages(conversation),
            user_message=chat_request.message,
            workflow_config=chat_request.workflow_config or {},
            correlation_id=correlation_id
        )
        
        # Stream workflow execution
        async for event in workflow_manager.stream_workflow(workflow_type, state):
            # Convert workflow events to streaming chunks
            if event.get("type") == "token":
                yield StreamingChatChunk(
                    type="token",
                    content=event.get("content", ""),
                    correlation_id=correlation_id
                )
            elif event.get("type") == "tool_call":
                yield StreamingChatChunk(
                    type="tool_call",
                    content=event.get("tool_name", ""),
                    correlation_id=correlation_id,
                    metadata={"tool_args": event.get("tool_args", {})}
                )
            elif event.get("type") == "source":
                yield StreamingChatChunk(
                    type="source",
                    content=event.get("source_title", ""),
                    correlation_id=correlation_id,
                    metadata={"source_url": event.get("source_url", "")}
                )
            elif event.get("type") == "complete":
                yield StreamingChatChunk(
                    type="done",
                    content="",
                    correlation_id=correlation_id,
                    metadata={
                        "usage": event.get("usage", {}),
                        "message_id": event.get("message_id")
                    }
                )

    async def _get_conversation_messages(self, conversation: Conversation) -> list[Message]:
        """Get messages for conversation in workflow format."""
        if hasattr(conversation, 'messages') and conversation.messages:
            return conversation.messages
        
        # Fallback to loading messages
        messages = await self.message_service.get_conversation_messages(
            conversation.id, conversation.user_id, limit=50
        )
        return list(messages)

    def _get_cache_key(self, conversation_id: str, chat_request: ChatRequest) -> str:
        """Generate cache key for workflow result."""
        import hashlib
        
        key_data = f"{conversation_id}:{chat_request.message}:{chat_request.workflow_type}:{chat_request.workflow_config}"
        return f"workflow:{hashlib.md5(key_data.encode()).hexdigest()}"

    async def get_workflow_performance_stats(self) -> dict[str, Any]:
        """Get workflow performance statistics."""
        return {
            "performance_monitor": performance_monitor.get_stats(),
            "cache_stats": await workflow_cache.get_stats() if hasattr(workflow_cache, 'get_stats') else {},
            "template_stats": self.template_manager.get_stats() if hasattr(self.template_manager, 'get_stats') else {}
        }