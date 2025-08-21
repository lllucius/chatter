"""Chat endpoints."""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.core.chat import ChatService, ConversationNotFoundError, ChatError
from chatter.models.user import User
from chatter.schemas.chat import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationWithMessages,
    ConversationSearchRequest,
    ConversationSearchResponse,
    ChatRequest,
    ChatResponse,
    MessageResponse,
)
from chatter.services.llm import LLMService
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


async def get_chat_service(session: AsyncSession = Depends(get_session)) -> ChatService:
    """Get chat service instance.
    
    Args:
        session: Database session
        
    Returns:
        ChatService instance
    """
    llm_service = LLMService()
    return ChatService(session, llm_service)


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
) -> ConversationResponse:
    """Create a new conversation.
    
    Args:
        conversation_data: Conversation creation data
        current_user: Current authenticated user
        chat_service: Chat service
        
    Returns:
        Created conversation
    """
    try:
        conversation = await chat_service.create_conversation(
            current_user.id,
            conversation_data
        )
        return ConversationResponse.model_validate(conversation)
    except ChatError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/conversations", response_model=ConversationSearchResponse)
async def list_conversations(
    search: ConversationSearchRequest = Depends(),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
) -> ConversationSearchResponse:
    """List user's conversations.
    
    Args:
        search: Search parameters
        current_user: Current authenticated user
        chat_service: Chat service
        
    Returns:
        List of conversations with pagination
    """
    conversations, total = await chat_service.list_conversations(
        current_user.id,
        limit=search.limit,
        offset=search.offset
    )
    
    return ConversationSearchResponse(
        conversations=[ConversationResponse.model_validate(c) for c in conversations],
        total=total,
        limit=search.limit,
        offset=search.offset
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
) -> ConversationWithMessages:
    """Get conversation details with messages.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        chat_service: Chat service
        
    Returns:
        Conversation with messages
    """
    conversation = await chat_service.get_conversation(
        conversation_id,
        current_user.id,
        include_messages=True
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Convert to response format
    conversation_response = ConversationResponse.model_validate(conversation)
    messages = [MessageResponse.model_validate(m) for m in conversation.messages]
    
    return ConversationWithMessages(
        **conversation_response.model_dump(),
        messages=messages
    )


@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
) -> ConversationResponse:
    """Update conversation.
    
    Args:
        conversation_id: Conversation ID
        update_data: Update data
        current_user: Current authenticated user
        chat_service: Chat service
        
    Returns:
        Updated conversation
    """
    try:
        conversation = await chat_service.update_conversation(
            conversation_id,
            current_user.id,
            update_data
        )
        return ConversationResponse.model_validate(conversation)
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
) -> dict:
    """Delete conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        chat_service: Chat service
        
    Returns:
        Success message
    """
    try:
        await chat_service.delete_conversation(conversation_id, current_user.id)
        return {"message": "Conversation deleted successfully"}
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
) -> List[MessageResponse]:
    """Get conversation messages.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        chat_service: Chat service
        
    Returns:
        List of messages
    """
    try:
        messages = await chat_service.get_conversation_messages(
            conversation_id,
            current_user.id
        )
        return [MessageResponse.model_validate(m) for m in messages]
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """Send a chat message and get response.
    
    Args:
        chat_request: Chat request data
        current_user: Current authenticated user
        chat_service: Chat service
        
    Returns:
        Chat response with assistant message
    """
    if chat_request.stream:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /chat/stream for streaming responses"
        )
    
    try:
        conversation, assistant_message = await chat_service.chat(
            current_user.id,
            chat_request
        )
        
        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse.model_validate(assistant_message),
            conversation=ConversationResponse.model_validate(conversation)
        )
    except (ConversationNotFoundError, ChatError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/chat/stream")
async def chat_stream(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
) -> StreamingResponse:
    """Send a chat message and get streaming response.
    
    Args:
        chat_request: Chat request data
        current_user: Current authenticated user
        chat_service: Chat service
        
    Returns:
        Streaming response with chat chunks
    """
    async def generate_stream():
        try:
            async for chunk in chat_service.chat_streaming(current_user.id, chat_request):
                yield f"data: {json.dumps(chunk)}\n\n"
        except (ConversationNotFoundError, ChatError) as e:
            error_chunk = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
        finally:
            # Send end-of-stream marker
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )