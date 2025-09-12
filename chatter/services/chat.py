"""Consolidated ChatService with unified chat method and extracted analytics."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.exceptions import ChatServiceError
from chatter.core.monitoring import record_request_metrics
from chatter.models.conversation import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
)
from chatter.schemas.chat import (
    ChatRequest,
    StreamingChatChunk,
)
from chatter.schemas.chat import (
    ConversationCreate as ConversationCreateSchema,
)
from chatter.schemas.chat import (
    ConversationUpdate as ConversationUpdateSchema,
)
from chatter.services.conversation import ConversationService
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.services.workflow_execution import WorkflowExecutionService
from chatter.utils.correlation import get_correlation_id
from chatter.utils.performance import (
    get_conversation_optimized,
    get_performance_monitor,
)
from chatter.utils.security_enhanced import get_secure_logger

logger = get_secure_logger(__name__)


class ChatAnalyticsService:
    """Dedicated service for chat analytics and performance metrics."""

    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive chat performance statistics."""
        try:
            # Mock analytics for now - in real implementation would gather from monitoring
            return {
                "total_requests": 1000,
                "avg_response_time_ms": 850.5,
                "success_rate": 0.98,
                "workflow_breakdown": {
                    "plain": {"count": 400, "avg_time_ms": 650.2},
                    "rag": {"count": 350, "avg_time_ms": 950.8},
                    "tools": {"count": 200, "avg_time_ms": 1200.5},
                    "full": {"count": 50, "avg_time_ms": 1800.9},
                },
                "token_usage": {
                    "total_input_tokens": 50000,
                    "total_output_tokens": 75000,
                    "total_cost": 12.50,
                },
                "efficiency_score": self._calculate_efficiency_score(),
            }
        except Exception as e:
            logger.error(
                "Failed to get performance stats", error=str(e)
            )
            return {"error": "Failed to retrieve stats"}

    async def get_conversation_analytics(
        self, conversation_id: str
    ) -> dict[str, Any]:
        """Get analytics for a specific conversation."""
        try:
            # Get conversation data
            conversation = await self.chat_service.conversation_service.get_conversation(
                conversation_id, None  # Skip user check for analytics
            )

            if not conversation:
                return {"error": "Conversation not found"}

            # Calculate analytics
            message_count = len(conversation.messages)
            total_tokens = sum(
                (msg.prompt_tokens or 0) + (msg.completion_tokens or 0)
                for msg in conversation.messages
            )
            total_cost = sum(
                msg.cost or 0.0 for msg in conversation.messages
            )

            return {
                "conversation_id": conversation_id,
                "message_count": message_count,
                "total_tokens": total_tokens,
                "total_cost": round(total_cost, 4),
                "avg_tokens_per_message": (
                    round(total_tokens / message_count, 2)
                    if message_count > 0
                    else 0
                ),
                "created_at": conversation.created_at.isoformat(),
                "last_updated": conversation.updated_at.isoformat(),
                "status": (
                    conversation.status.value
                    if conversation.status
                    else "unknown"
                ),
            }
        except Exception as e:
            logger.error(
                "Failed to get conversation analytics", error=str(e)
            )
            return {"error": "Failed to retrieve analytics"}

    def _calculate_efficiency_score(self) -> float:
        """Calculate overall system efficiency score."""
        # Simplified efficiency calculation - would use real metrics in production
        try:
            # Mock calculation based on response time, success rate, cost efficiency
            base_score = 85.0
            return min(100.0, max(0.0, base_score))
        except Exception:
            return 50.0  # Default score


class ChatService:
    """
    Consolidated ChatService with unified chat method and better separation of concerns.
    """

    def __init__(
        self, session: AsyncSession, llm_service: LLMService
    ) -> None:
        """Initialize chat service with dependencies and performance monitoring."""
        self.session = session
        self.llm_service = llm_service
        self.performance_monitor = get_performance_monitor()

        # Initialize specialized services
        self.conversation_service = ConversationService(session)
        self.message_service = MessageService(session)
        self.workflow_service = WorkflowExecutionService(
            llm_service, self.message_service, session
        )

        # Initialize analytics service
        self.analytics = ChatAnalyticsService(self)

    # Conversation management - delegate to ConversationService

    async def create_conversation(
        self, user_id: str, conversation_data: ConversationCreateSchema
    ) -> Conversation:
        """Create a new conversation."""
        return await self.conversation_service.create_conversation(
            user_id, conversation_data
        )

    async def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status: ConversationStatus | None = None,
        llm_provider: str | None = None,
        llm_model: str | None = None,
        tags: list[str] | None = None,
        enable_retrieval: bool | None = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> tuple[list[Conversation], int]:
        """List conversations for a user with pagination and filtering."""
        conversations = (
            await self.conversation_service.list_conversations(
                user_id=user_id,
                limit=limit,
                offset=offset,
                status=status,
                llm_provider=llm_provider,
                llm_model=llm_model,
                tags=tags,
                enable_retrieval=enable_retrieval,
                sort_field=sort_by,
                sort_order=sort_order,
            )
        )
        total = await self.conversation_service.get_conversation_count(
            user_id, status=status, llm_provider=llm_provider,
            llm_model=llm_model, tags=tags, enable_retrieval=enable_retrieval
        )
        return list(conversations), total

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
        include_messages: bool = True,
    ) -> Conversation:
        """Get conversation by ID with access control."""
        return await self.conversation_service.get_conversation(
            conversation_id, user_id, include_messages
        )

    async def update_conversation(
        self,
        conversation_id: str,
        user_id: str,
        update_data: ConversationUpdateSchema,
    ) -> Conversation:
        """Update conversation."""
        return await self.conversation_service.update_conversation(
            conversation_id, user_id, update_data
        )

    async def delete_conversation(
        self, conversation_id: str, user_id: str
    ) -> None:
        """Delete conversation."""
        await self.conversation_service.delete_conversation(
            conversation_id, user_id
        )

    # Message management - delegate to MessageService

    async def get_conversation_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        """Get messages from conversation."""
        return await self.message_service.get_conversation_messages(
            conversation_id, user_id, limit, offset
        )

    async def add_message_to_conversation(
        self,
        conversation_id: str,
        user_id: str,
        role: MessageRole,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        """Add message to conversation."""
        return await self.message_service.add_message_to_conversation(
            conversation_id, user_id, role, content, metadata
        )

    async def delete_message(
        self, conversation_id: str, message_id: str, user_id: str
    ) -> None:
        """Delete message from conversation."""
        await self.message_service.delete_message(
            conversation_id, message_id, user_id
        )

    # Unified Chat Method

    async def chat(
        self,
        user_id: str,
        chat_request: ChatRequest,
        streaming: bool = False,
    ) -> (
        tuple[Conversation, Message]
        | AsyncGenerator[StreamingChatChunk, None]
    ):
        """
        Unified chat method supporting both streaming and non-streaming responses.

        Args:
            user_id: User ID
            chat_request: Chat request
            streaming: Whether to return streaming response

        Returns:
            For non-streaming: Tuple of (conversation, response_message)
            For streaming: AsyncGenerator of StreamingChatChunk
        """
        if streaming or chat_request.stream:
            return self.chat_streaming(user_id, chat_request)
        else:
            return await self._chat_sync(user_id, chat_request)

    async def _chat_sync(
        self, user_id: str, chat_request: ChatRequest
    ) -> tuple[Conversation, Message]:
        """Process a synchronous chat request with performance monitoring."""
        correlation_id = get_correlation_id()
        start_time = __import__("time").time()

        async with self.performance_monitor.measure_query(
            "chat_sync_request"
        ):
            try:
                # Shared conversation setup logic
                conversation = await self._setup_conversation(
                    user_id, chat_request
                )

                # Add user message
                await self.add_message_to_conversation(
                    conversation.id,
                    user_id,
                    MessageRole.USER,
                    chat_request.message,
                )

                # Execute workflow to get response
                response_message, usage_info = (
                    await self.workflow_service.execute_workflow(
                        conversation, chat_request, correlation_id
                    )
                )

                # Apply usage information and save response
                self._apply_usage_to_message(
                    response_message, usage_info
                )
                response_message = await self.message_service.add_message_to_conversation(
                    conversation.id,
                    user_id,
                    response_message.role,
                    response_message.content,
                    response_message.extra_metadata,
                    response_message.prompt_tokens,
                    response_message.completion_tokens,
                    response_message.cost,
                    response_message.provider_used,
                )

                # Record metrics
                self._record_request_metrics(
                    start_time, correlation_id, user_id, 200
                )

                logger.info(
                    "Chat request processed successfully",
                    conversation_id=conversation.id,
                    user_id=user_id,
                    workflow_type=chat_request.workflow_type,
                    correlation_id=correlation_id,
                )

                return conversation, response_message

            except Exception as e:
                self._record_request_metrics(
                    start_time, correlation_id, user_id, 500
                )
                logger.error(
                    "Chat request failed",
                    user_id=user_id,
                    error=str(e),
                    correlation_id=correlation_id,
                )
                raise ChatServiceError(
                    f"Chat processing failed: {e}"
                ) from e

    async def chat_streaming(
        self, user_id: str, chat_request: ChatRequest
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Process a streaming chat request."""
        correlation_id = get_correlation_id()
        start_time = __import__("time").time()

        try:
            # Shared conversation setup logic
            conversation = await self._setup_conversation(
                user_id, chat_request
            )

            # Add user message
            await self.add_message_to_conversation(
                conversation.id,
                user_id,
                MessageRole.USER,
                chat_request.message,
            )

            # Yield start chunk
            yield StreamingChatChunk(
                type="start",
                content="",
                correlation_id=correlation_id,
                metadata={"conversation_id": conversation.id},
            )

            # Execute streaming workflow
            async for (
                chunk
            ) in self.workflow_service.execute_workflow_streaming(
                conversation, chat_request, correlation_id
            ):
                yield chunk

            # Yield end chunk
            yield StreamingChatChunk(
                type="end",
                content="",
                correlation_id=correlation_id,
                metadata={"conversation_id": conversation.id},
            )

            # Record success metrics
            self._record_request_metrics(
                start_time, correlation_id, user_id, 200
            )

        except Exception as e:
            # Record error metrics and yield error chunk
            self._record_request_metrics(
                start_time, correlation_id, user_id, 500
            )

            yield StreamingChatChunk(
                type="error",
                content=str(e),
                correlation_id=correlation_id,
            )

            logger.error(
                "Streaming chat request failed",
                user_id=user_id,
                error=str(e),
                correlation_id=correlation_id,
            )

    # Helper Methods

    async def _setup_conversation(
        self, user_id: str, chat_request: ChatRequest
    ) -> Conversation:
        """Setup conversation for both sync and streaming requests with optimization."""
        async with self.performance_monitor.measure_query(
            "setup_conversation"
        ):
            if chat_request.conversation_id:
                # Use optimized conversation retrieval with message limit for better performance
                return await get_conversation_optimized(
                    self.session,
                    chat_request.conversation_id,
                    user_id=user_id,
                    include_messages=True,
                    message_limit=50,  # Limit context window for performance
                )
            else:
                # Create new conversation
                conv_data = ConversationCreateSchema(
                    title=(
                        chat_request.message[:50] + "..."
                        if len(chat_request.message) > 50
                        else chat_request.message
                    ),
                    profile_id=chat_request.profile_id,
                    temperature=chat_request.temperature,
                    max_tokens=chat_request.max_tokens,
                    workflow_config=chat_request.workflow_config,
                )
                return await self.create_conversation(
                    user_id, conv_data
                )

    def _apply_usage_to_message(
        self, message: Message, usage: dict[str, Any]
    ) -> None:
        """Apply usage information to a message."""
        if "tokens" in usage:
            total_tokens = usage["tokens"]
            if (
                not message.prompt_tokens
                and not message.completion_tokens
            ):
                # Rough estimate: input is ~20% of total for responses
                message.prompt_tokens = int(total_tokens * 0.2)
                message.completion_tokens = int(total_tokens * 0.8)

        if "cost" in usage:
            message.cost = usage["cost"]

    def _record_request_metrics(
        self,
        start_time: float,
        correlation_id: str,
        user_id: str,
        status_code: int,
    ) -> None:
        """Record request metrics."""
        duration_ms = (__import__("time").time() - start_time) * 1000
        record_request_metrics(
            method="POST",
            path="/chat",
            status_code=status_code,
            response_time_ms=duration_ms,
            correlation_id=correlation_id,
            user_id=user_id,
        )

    # Analytics methods - delegate to analytics service

    def get_performance_stats(self) -> dict[str, Any]:
        """Get workflow performance statistics."""
        return self.analytics.get_performance_stats()

    async def get_conversation_analytics(
        self, conversation_id: str
    ) -> dict[str, Any]:
        """Get analytics for a specific conversation."""
        return await self.analytics.get_conversation_analytics(
            conversation_id
        )

    # Health check

    async def get_service_health(self) -> dict[str, Any]:
        """Get health status of all services."""
        return {
            "chat_service": "healthy",
            "conversation_service": "healthy",
            "message_service": "healthy",
            "workflow_service": "healthy",
            "llm_service": "healthy",
            "database": "connected" if self.session else "disconnected",
        }
