"""Conversations API endpoints - Direct access to conversations without /chat prefix."""

from typing import Union

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.api.dependencies import (
    ConversationId,
    MessageId,
    PaginationLimit,
    PaginationOffset,
)
from chatter.api.resources import (
    ConversationResourceHandler,
    MessageResourceHandler,
)
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
from chatter.services.llm import LLMService
from chatter.utils.database import get_session_generator

router = APIRouter()


async def get_chat_service(
    session: AsyncSession = Depends(get_session_generator),
) -> ChatService:
    """Get chat service instance."""
    llm_service = LLMService()
    return ChatService(session, llm_service)


async def get_conversation_handler(
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationResourceHandler:
    """Get conversation resource handler."""
    return ConversationResourceHandler(chat_service)


async def get_message_handler(
    chat_service: ChatService = Depends(get_chat_service),
) -> MessageResourceHandler:
    """Get message resource handler."""
    return MessageResourceHandler(chat_service)


# Conversation Resource Endpoints


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    handler: ConversationResourceHandler = Depends(
        get_conversation_handler
    ),
) -> ConversationResponse:
    """Create a new conversation."""
    return await handler.create_conversation(
        conversation_data, current_user
    )


@router.get(
    "/",
    response_model=ConversationListResponse,
)
async def list_conversations(
    status: Union[ConversationStatus, None] = Query(
        None, description="Filter by conversation status"
    ),
    llm_provider: Union[str, None] = Query(
        None, description="Filter by LLM provider"
    ),
    llm_model: Union[str, None] = Query(
        None, description="Filter by LLM model"
    ),
    tags: Union[list[str], None] = Query(None, description="Filter by tags"),
    enable_retrieval: Union[bool, None] = Query(
        None, description="Filter by retrieval enabled status"
    ),
    limit: int = Query(
        50, ge=1, description="Maximum number of results"
    ),
    offset: int = Query(
        0, ge=0, description="Number of results to skip"
    ),
    sort_by: str = Query("updated_at", description="Sort field"),
    sort_order: str = Query(
        "desc", pattern="^(asc|desc)$", description="Sort order"
    ),
    current_user: User = Depends(get_current_user),
    handler: ConversationResourceHandler = Depends(
        get_conversation_handler
    ),
) -> ConversationListResponse:
    """List conversations for the current user."""
    return await handler.list_conversations(
        current_user=current_user,
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


@router.get(
    "/{conversation_id}",
    response_model=ConversationWithMessages,
)
async def get_conversation(
    conversation_id: ConversationId,
    include_messages: bool = Query(
        True, description="Include messages in response"
    ),
    current_user: User = Depends(get_current_user),
    handler: ConversationResourceHandler = Depends(
        get_conversation_handler
    ),
) -> ConversationWithMessages:
    """Get conversation details with optional messages."""
    return await handler.get_conversation(
        conversation_id, current_user, include_messages
    )


@router.put(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
async def update_conversation(
    conversation_id: ConversationId,
    update_data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    handler: ConversationResourceHandler = Depends(
        get_conversation_handler
    ),
) -> ConversationResponse:
    """Update conversation."""
    return await handler.update_conversation(
        conversation_id, update_data, current_user
    )


@router.delete(
    "/{conversation_id}",
    response_model=ConversationDeleteResponse,
)
async def delete_conversation(
    conversation_id: ConversationId,
    current_user: User = Depends(get_current_user),
    handler: ConversationResourceHandler = Depends(
        get_conversation_handler
    ),
) -> ConversationDeleteResponse:
    """Delete conversation."""
    return await handler.delete_conversation(
        conversation_id, current_user
    )


# Message Resource Endpoints


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
async def get_conversation_messages(
    conversation_id: ConversationId,
    limit: PaginationLimit = 50,
    offset: PaginationOffset = 0,
    current_user: User = Depends(get_current_user),
    handler: MessageResourceHandler = Depends(get_message_handler),
) -> list[MessageResponse]:
    """Get messages from a conversation."""
    return await handler.get_conversation_messages(
        conversation_id, current_user, limit, offset
    )


@router.delete(
    "/{conversation_id}/messages/{message_id}",
    response_model=MessageDeleteResponse,
)
async def delete_message(
    conversation_id: ConversationId,
    message_id: MessageId,
    current_user: User = Depends(get_current_user),
    handler: MessageResourceHandler = Depends(get_message_handler),
) -> MessageDeleteResponse:
    """Delete a message from a conversation."""
    return await handler.delete_message(
        conversation_id, message_id, current_user
    )


@router.patch(
    "/{conversation_id}/messages/{message_id}/rating",
    response_model=MessageRatingResponse,
)
async def update_message_rating(
    conversation_id: ConversationId,
    message_id: MessageId,
    rating_update: MessageRatingUpdate,
    current_user: User = Depends(get_current_user),
    handler: MessageResourceHandler = Depends(get_message_handler),
) -> MessageRatingResponse:
    """Update the rating for a message."""
    return await handler.update_message_rating(
        conversation_id, message_id, rating_update, current_user
    )