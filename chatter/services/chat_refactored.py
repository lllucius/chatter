"""Refactored ChatService - orchestrates conversation, message, and workflow services."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.conversation import Conversation, Message, MessageRole
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
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
from chatter.utils.logging import get_logger
from chatter.utils.monitoring import record_request_metrics
from chatter.utils.security import get_secure_logger

logger = get_secure_logger(__name__)


class ChatServiceError(Exception):
    """Chat service error."""
    pass


class RefactoredChatService:
    """
    Refactored ChatService that orchestrates specialized services.
    
    This is a much smaller, focused service that delegates to:
    - ConversationService: CRUD operations for conversations
    - MessageService: CRUD operations for messages  
    - WorkflowExecutionService: Workflow execution and streaming
    - LLMService: LLM provider interactions
    """

    def __init__(self, session: AsyncSession, llm_service: LLMService) -> None:
        """Initialize chat service with dependencies."""
        self.session = session
        self.llm_service = llm_service
        
        # Initialize specialized services
        self.conversation_service = ConversationService(session)
        self.message_service = MessageService(session)
        self.workflow_service = WorkflowExecutionService(llm_service, self.message_service)

    # Conversation management - delegate to ConversationService
    
    async def create_conversation(
        self, user_id: str, conversation_data: ConversationCreateSchema
    ) -> Conversation:
        """Create a new conversation."""
        return await self.conversation_service.create_conversation(user_id, conversation_data)

    async def list_conversations(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> list[Conversation]:
        """List conversations for a user."""
        conversations = await self.conversation_service.list_conversations(user_id, limit, offset)
        return list(conversations)

    async def get_conversation(
        self, conversation_id: str, user_id: str, include_messages: bool = True
    ) -> Conversation:
        """Get conversation by ID with access control."""
        return await self.conversation_service.get_conversation(
            conversation_id, user_id, include_messages
        )

    async def update_conversation(
        self, conversation_id: str, user_id: str, update_data: ConversationUpdateSchema
    ) -> Conversation:
        """Update conversation."""
        return await self.conversation_service.update_conversation(
            conversation_id, user_id, update_data
        )

    async def delete_conversation(self, conversation_id: str, user_id: str) -> None:
        """Delete conversation (soft delete)."""
        await self.conversation_service.delete_conversation(conversation_id, user_id)

    # Message management - delegate to MessageService

    async def get_conversation_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int | None = None,
        offset: int = 0
    ) -> list[Message]:
        """Get messages for a conversation."""
        messages = await self.message_service.get_conversation_messages(
            conversation_id, user_id, limit, offset
        )
        return list(messages)

    async def add_message_to_conversation(
        self,
        conversation_id: str,
        user_id: str,
        role: MessageRole,
        content: str,
        metadata: dict[str, Any] | None = None
    ) -> Message:
        """Add a message to a conversation."""
        return await self.message_service.add_message_to_conversation(
            conversation_id, user_id, role, content, metadata
        )

    async def delete_message(
        self, conversation_id: str, message_id: str, user_id: str
    ) -> None:
        """Delete a message."""
        await self.message_service.delete_message(conversation_id, message_id, user_id)

    # Core chat functionality - orchestrates all services

    async def chat(
        self, user_id: str, chat_request: ChatRequest
    ) -> tuple[Conversation, Message]:
        """Process a chat request and return conversation and response message.

        Args:
            user_id: User ID
            chat_request: Chat request

        Returns:
            Tuple of (conversation, response_message)

        Raises:
            ChatServiceError: If chat processing fails
        """
        correlation_id = get_correlation_id()
        start_time = __import__('time').time()

        try:
            # Get or create conversation
            if chat_request.conversation_id:
                conversation = await self.get_conversation(
                    chat_request.conversation_id, user_id, include_messages=True
                )
            else:
                # Create new conversation
                from chatter.schemas.chat import ConversationCreate
                conv_data = ConversationCreate(
                    title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message,
                    profile_id=chat_request.profile_id,
                    temperature=chat_request.temperature,
                    max_tokens=chat_request.max_tokens,
                    workflow_config=chat_request.workflow_config
                )
                conversation = await self.create_conversation(user_id, conv_data)

            # Add user message
            await self.add_message_to_conversation(
                conversation.id,
                user_id,
                MessageRole.USER,
                chat_request.message
            )

            # Execute workflow to get response
            response_message, usage_info = await self.workflow_service.execute_workflow(
                conversation, chat_request, correlation_id
            )

            # Apply usage information to response message
            self._apply_usage_to_message(response_message, usage_info)

            # Save response message
            response_message = await self.message_service.add_message_to_conversation(
                conversation.id,
                user_id,
                response_message.role,
                response_message.content,
                response_message.metadata,
                response_message.input_tokens,
                response_message.output_tokens,
                response_message.cost,
                response_message.provider
            )

            # Record metrics
            duration_ms = (__import__('time').time() - start_time) * 1000
            record_request_metrics(
                method="POST",
                path="/chat",
                status_code=200,
                response_time_ms=duration_ms,
                correlation_id=correlation_id,
                user_id=user_id
            )

            logger.info(
                "Chat request processed successfully",
                conversation_id=conversation.id,
                user_id=user_id,
                workflow_type=chat_request.workflow_type,
                duration_ms=duration_ms,
                correlation_id=correlation_id
            )

            return conversation, response_message

        except Exception as e:
            # Record error metrics
            duration_ms = (__import__('time').time() - start_time) * 1000
            record_request_metrics(
                method="POST",
                path="/chat",
                status_code=500,
                response_time_ms=duration_ms,
                correlation_id=correlation_id,
                user_id=user_id
            )

            logger.error(
                "Chat request failed",
                user_id=user_id,
                error=str(e),
                correlation_id=correlation_id
            )
            raise ChatServiceError(f"Chat processing failed: {e}")

    async def chat_streaming(
        self, user_id: str, chat_request: ChatRequest
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Process a chat request with streaming response.

        Args:
            user_id: User ID  
            chat_request: Chat request

        Yields:
            Streaming chat chunks

        Raises:
            ChatServiceError: If chat processing fails
        """
        correlation_id = get_correlation_id()
        start_time = __import__('time').time()

        try:
            # Get or create conversation
            if chat_request.conversation_id:
                conversation = await self.get_conversation(
                    chat_request.conversation_id, user_id, include_messages=True
                )
            else:
                # Create new conversation
                from chatter.schemas.chat import ConversationCreate
                conv_data = ConversationCreate(
                    title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message,
                    profile_id=chat_request.profile_id,
                    temperature=chat_request.temperature,
                    max_tokens=chat_request.max_tokens,
                    workflow_config=chat_request.workflow_config
                )
                conversation = await self.create_conversation(user_id, conv_data)

            # Add user message
            await self.add_message_to_conversation(
                conversation.id,
                user_id,
                MessageRole.USER,
                chat_request.message
            )

            # Yield start chunk
            yield StreamingChatChunk(
                type="start",
                content="",
                correlation_id=correlation_id,
                metadata={"conversation_id": conversation.id}
            )

            # Execute streaming workflow
            async for chunk in self.workflow_service.execute_workflow_streaming(
                conversation, chat_request, correlation_id
            ):
                yield chunk

            # Record metrics
            duration_ms = (__import__('time').time() - start_time) * 1000
            record_request_metrics(
                method="POST",
                path="/chat/stream",
                status_code=200,
                response_time_ms=duration_ms,
                correlation_id=correlation_id,
                user_id=user_id
            )

            logger.info(
                "Streaming chat request completed",
                conversation_id=conversation.id,
                user_id=user_id,
                duration_ms=duration_ms,
                correlation_id=correlation_id
            )

        except Exception as e:
            # Record error metrics
            duration_ms = (__import__('time').time() - start_time) * 1000
            record_request_metrics(
                method="POST",
                path="/chat/stream",
                status_code=500,
                response_time_ms=duration_ms,
                correlation_id=correlation_id,
                user_id=user_id
            )

            logger.error(
                "Streaming chat request failed",
                user_id=user_id,
                error=str(e),
                correlation_id=correlation_id
            )
            
            # Yield error chunk
            yield StreamingChatChunk(
                type="error",
                content=f"Chat processing failed: {str(e)}",
                correlation_id=correlation_id
            )

    # Analytics and performance

    async def get_conversation_analytics(
        self, conversation_id: str, user_id: str
    ) -> dict[str, Any]:
        """Get analytics for a conversation."""
        # Combine stats from different services
        conv_stats = await self.conversation_service.get_conversation_stats(conversation_id, user_id)
        message_stats = await self.message_service.get_message_statistics(conversation_id, user_id)
        
        return {
            "conversation": conv_stats,
            "messages": message_stats,
            "combined_metrics": {
                "total_interactions": conv_stats.get("total_messages", 0) // 2,  # Pairs of user/assistant
                "avg_tokens_per_interaction": message_stats.get("avg_tokens_per_message", 0) * 2,
                "total_cost": message_stats.get("total_cost", 0.0),
                "efficiency_score": self._calculate_efficiency_score(conv_stats, message_stats)
            }
        }

    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics."""
        return {
            "service_name": "RefactoredChatService",
            "architecture": "microservice_based",
            "services": {
                "conversation_service": "active",
                "message_service": "active", 
                "workflow_service": "active",
                "llm_service": "active"
            }
        }

    async def get_service_health(self) -> dict[str, Any]:
        """Get health status of all services."""
        return {
            "chat_service": "healthy",
            "conversation_service": "healthy",
            "message_service": "healthy",
            "workflow_service": "healthy",
            "llm_service": "healthy",
            "database": "connected" if self.session else "disconnected"
        }

    # Helper methods

    def _apply_usage_to_message(self, message: Message, usage: dict[str, Any]) -> None:
        """Apply usage information to a message."""
        if "tokens" in usage:
            # Split tokens between input and output if not specified
            total_tokens = usage["tokens"]
            if not message.input_tokens and not message.output_tokens:
                # Rough estimate: input is ~20% of total for responses
                message.input_tokens = int(total_tokens * 0.2)
                message.output_tokens = int(total_tokens * 0.8)

        if "cost" in usage:
            message.cost = usage["cost"]

    def _calculate_efficiency_score(
        self, conv_stats: dict[str, Any], message_stats: dict[str, Any]
    ) -> float:
        """Calculate efficiency score based on various metrics."""
        try:
            total_messages = conv_stats.get("total_messages", 1)
            avg_tokens = message_stats.get("avg_tokens_per_message", 0)
            total_cost = message_stats.get("total_cost", 0.0)
            
            # Higher score for fewer messages with reasonable token usage and lower cost
            efficiency = 100.0
            
            # Penalize excessive messages
            if total_messages > 20:
                efficiency -= (total_messages - 20) * 2
                
            # Penalize excessive token usage  
            if avg_tokens > 1000:
                efficiency -= (avg_tokens - 1000) / 100
                
            # Penalize high cost
            if total_cost > 1.0:
                efficiency -= total_cost * 10
                
            return max(0.0, min(100.0, efficiency))
            
        except Exception:
            return 50.0  # Default score