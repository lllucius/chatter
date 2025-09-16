"""Resource-based handlers for conversation and message operations."""

from chatter.api.dependencies import ConversationId, MessageId
from chatter.core.exceptions import NotFoundError
from chatter.models.conversation import ConversationStatus
from chatter.models.user import User
from chatter.schemas.chat import (
    ConversationCreate,
    ConversationDeleteResponse,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    ConversationWithMessages,
    MessageDeleteResponse,
    MessageRatingResponse,
    MessageRatingUpdate,
    MessageResponse,
)
from chatter.services.chat import ChatService
from chatter.utils.problem import NotFoundProblem


class ConversationResourceHandler:
    """Resource handler for conversation CRUD operations."""

    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    async def create_conversation(
        self,
        conversation_data: ConversationCreate,
        current_user: User,
    ) -> ConversationResponse:
        """Create a new conversation."""
        conversation = await self.chat_service.create_conversation(
            current_user.id, conversation_data
        )
        return ConversationResponse.model_validate(conversation)

    async def list_conversations(
        self,
        current_user: User,
        limit: int,
        offset: int,
        status: ConversationStatus | None = None,
        llm_provider: str | None = None,
        llm_model: str | None = None,
        tags: list[str] | None = None,
        enable_retrieval: bool | None = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> ConversationListResponse:
        """List conversations for current user with filters."""
        conversations, total = (
            await self.chat_service.list_conversations(
                user_id=current_user.id,
                limit=limit,
                offset=offset,
                status=status,
                llm_provider=llm_provider,
                llm_model=llm_model,
                tags=tags,
                enable_retrieval=enable_retrieval,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        )

        return ConversationListResponse(
            conversations=[
                ConversationResponse.model_validate(conv)
                for conv in conversations
            ],
            total_count=total,
            limit=limit,
            offset=offset,
        )

    async def get_conversation(
        self,
        conversation_id: ConversationId,
        current_user: User,
        include_messages: bool = True,
    ) -> ConversationWithMessages:
        """Get conversation details with optional messages."""
        conversation = await self.chat_service.get_conversation(
            conversation_id,
            current_user.id,
            include_messages=include_messages,
        )

        if not conversation:
            raise NotFoundProblem(
                detail="Conversation not found",
                resource_type="conversation",
            )

        # Convert to response format
        conversation_response = ConversationResponse.model_validate(
            conversation
        )
        messages = (
            [
                MessageResponse.model_validate(m)
                for m in conversation.messages
            ]
            if include_messages
            else []
        )

        return ConversationWithMessages(
            **conversation_response.model_dump(), messages=messages
        )

    async def update_conversation(
        self,
        conversation_id: ConversationId,
        update_data: ConversationUpdate,
        current_user: User,
    ) -> ConversationResponse:
        """Update a conversation."""
        try:
            conversation = await self.chat_service.update_conversation(
                conversation_id, current_user.id, update_data
            )
            return ConversationResponse.model_validate(conversation)
        except NotFoundError as e:
            raise NotFoundProblem(
                detail="Conversation not found",
                resource_type="conversation",
            ) from e

    async def delete_conversation(
        self,
        conversation_id: ConversationId,
        current_user: User,
    ) -> ConversationDeleteResponse:
        """Delete a conversation."""
        try:
            await self.chat_service.delete_conversation(
                conversation_id, current_user.id
            )
            return ConversationDeleteResponse(
                message="Conversation deleted successfully"
            )
        except NotFoundError as e:
            raise NotFoundProblem(
                detail="Conversation not found",
                resource_type="conversation",
            ) from e


class MessageResourceHandler:
    """Resource handler for message CRUD operations."""

    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    async def get_conversation_messages(
        self,
        conversation_id: ConversationId,
        current_user: User,
        limit: int,
        offset: int,
    ) -> list[MessageResponse]:
        """Get messages from a conversation."""
        messages = await self.chat_service.get_conversation_messages(
            conversation_id, current_user.id, limit, offset
        )
        return [MessageResponse.model_validate(msg) for msg in messages]

    async def delete_message(
        self,
        conversation_id: ConversationId,
        message_id: MessageId,
        current_user: User,
    ) -> MessageDeleteResponse:
        """Delete a message from a conversation."""
        try:
            await self.chat_service.delete_message(
                conversation_id, message_id, current_user.id
            )
            return MessageDeleteResponse(
                message="Message deleted successfully"
            )
        except NotFoundError as e:
            raise NotFoundProblem(
                detail="Message not found",
                resource_type="message",
            ) from e

    async def update_message_rating(
        self,
        conversation_id: ConversationId,
        message_id: MessageId,
        rating_update: MessageRatingUpdate,
        current_user: User,
    ) -> MessageRatingResponse:
        """Update the rating for a message."""
        # Check if this is a temporary stream ID
        if str(message_id).startswith("stream-"):
            raise NotFoundProblem(
                detail="Cannot rate message while it is still being streamed. Please wait for the message to complete.",
                resource_type="message",
            )
            
        try:
            updated_message = (
                await self.chat_service.update_message_rating(
                    conversation_id,
                    message_id,
                    current_user.id,
                    rating_update.rating,
                )
            )
            return MessageRatingResponse(
                message="Message rating updated successfully",
                rating=updated_message.rating or 0.0,
                rating_count=updated_message.rating_count,
            )
        except NotFoundError as e:
            raise NotFoundProblem(
                detail="Message not found",
                resource_type="message",
            ) from e
