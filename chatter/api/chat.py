"""Chat endpoints."""

import json

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.core.chat import (
    ChatError,
    ChatService,
    ConversationNotFoundError,
)
from chatter.models.conversation import ConversationStatus
from chatter.models.user import User
from chatter.schemas.chat import (
    AvailableToolResponse,
    AvailableToolsResponse,
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationDeleteRequest,
    ConversationDeleteResponse,
    ConversationGetRequest,
    ConversationResponse,
    ConversationSearchResponse,
    ConversationUpdate,
    ConversationWithMessages,
    McpStatusResponse,
    MessageCreate,
    MessageResponse,
)
from chatter.services.llm import LLMService
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    InternalServerProblem,
    NotFoundProblem,
)

logger = get_logger(__name__)
router = APIRouter()


async def get_chat_service(
    session: AsyncSession = Depends(get_session)
) -> ChatService:
    """Get chat service instance.

    Args:
        session: Database session

    Returns:
        ChatService instance
    """
    llm_service = LLMService()
    return ChatService(session, llm_service)


def _map_workflow_type(workflow: str) -> str:
    """Map API workflow to internal workflow types.

    - plain -> basic (legacy name used internally)
    - rag -> rag
    - tools -> tools
    - full -> full (rag + tools)
    """
    mapping = {
        "plain": "basic",
        "rag": "rag",
        "tools": "tools",
        "full": "full",
    }
    return mapping.get(workflow, "basic")


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
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
            current_user.id, conversation_data
        )
        return ConversationResponse.model_validate(conversation)
    except ChatError as e:
        raise BadRequestProblem(detail=str(e)) from e


@router.get(
    "/conversations",
    response_model=ConversationSearchResponse,
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
        403: {"description": "Forbidden - User lacks permission to access conversations"},
        422: {"description": "Validation Error"},
    },
)
async def list_conversations(
    query: str | None = Query(None, description="Search query"),
    status: ConversationStatus | None = Query(
        None, description="Filter by status"
    ),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationSearchResponse:
    """List user's conversations.

    Note: Filters may be ignored if not supported by the service implementation.
    """
    conversations, total = await chat_service.list_conversations(
        current_user.id, limit, offset
    )

    return ConversationSearchResponse(
        conversations=[
            ConversationResponse.model_validate(c) for c in conversations
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationWithMessages,
)
async def get_conversation(
    conversation_id: str,
    request: ConversationGetRequest = Depends(),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationWithMessages:
    """Get conversation details with messages."""
    conversation = await chat_service.get_conversation(
        conversation_id, current_user.id, include_messages=True
    )

    if not conversation:
        raise NotFoundProblem(
            detail="Conversation not found",
            resource_type="conversation",
        ) from None

    # Convert to response format
    conversation_response = ConversationResponse.model_validate(conversation)
    messages = [
        MessageResponse.model_validate(m) for m in conversation.messages
    ]

    return ConversationWithMessages(
        **conversation_response.model_dump(), messages=messages
    )


@router.put(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
async def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationResponse:
    """Update conversation."""
    try:
        conversation = await chat_service.update_conversation(
            conversation_id, current_user.id, update_data
        )
        return ConversationResponse.model_validate(conversation)
    except ConversationNotFoundError:
        raise NotFoundProblem(
            detail="Conversation not found",
            resource_type="conversation",
        ) from None


@router.delete(
    "/conversations/{conversation_id}",
    response_model=ConversationDeleteResponse,
)
async def delete_conversation(
    conversation_id: str,
    request: ConversationDeleteRequest = Depends(),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationDeleteResponse:
    """Delete conversation."""
    try:
        await chat_service.delete_conversation(
            conversation_id, current_user.id
        )
        return ConversationDeleteResponse(
            message="Conversation deleted successfully"
        )
    except ConversationNotFoundError:
        raise NotFoundProblem(
            detail="Conversation not found",
            resource_type="conversation",
        ) from None


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
    responses={
        401: {"description": "Unauthorized - Invalid or missing authentication token"},
        403: {"description": "Forbidden - User lacks permission to access this conversation"},
        404: {"description": "Not Found - Conversation does not exist"},
        422: {"description": "Validation Error"},
    },
)
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> list[MessageResponse]:
    """Get conversation messages."""
    try:
        messages = await chat_service.get_conversation_messages(
            conversation_id, current_user.id
        )
        return [MessageResponse.model_validate(m) for m in messages]
    except ConversationNotFoundError:
        raise NotFoundProblem(
            detail="Conversation not found",
            resource_type="conversation",
        ) from None


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
)
async def add_message_to_conversation(
    conversation_id: str,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> MessageResponse:
    """Add a new message to existing conversation."""
    try:
        created_message = await chat_service.add_message_to_conversation(
            conversation_id, current_user.id, message.content
        )
        return MessageResponse.model_validate(created_message)
    except ConversationNotFoundError:
        raise NotFoundProblem(
            detail="Conversation not found",
            resource_type="conversation",
        ) from None


@router.delete("/conversations/{conversation_id}/messages/{message_id}")
async def delete_message(
    conversation_id: str,
    message_id: str,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> dict:
    """Delete a message from conversation."""
    try:
        await chat_service.delete_message(
            conversation_id, message_id, current_user.id
        )
        return {"message": "Message deleted successfully"}
    except ConversationNotFoundError:
        raise NotFoundProblem(
            detail="Conversation not found",
            resource_type="conversation",
        ) from None


@router.post(
    "/chat",
    response_model=None,  # Important: disable response model generation to support JSON or SSE
    responses={
        200: {
            "content": {
                "application/json": {"schema": ChatResponse.model_json_schema()},
                "text/event-stream": {"schema": {"type": "string"}},
            },
            "description": "Chat response as JSON or streaming SSE when stream=true",
        }
    },
)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Single chat endpoint supporting plain, rag, tools, and full workflows.

    - If chat_request.stream is True, returns SSE stream.
    - Otherwise returns ChatResponse JSON.
    """
    workflow_type = _map_workflow_type(chat_request.workflow)

    if chat_request.stream:
        # Streaming mode
        async def generate_stream():
            """Generate streaming chat response chunks."""
            try:
                if workflow_type == "basic":
                    # Use existing streaming for plain/basic
                    async for chunk in chat_service.chat_streaming(
                        current_user.id, chat_request
                    ):
                        yield f"data: {json.dumps(chunk)}\n\n"
                else:
                    # For workflow-based streaming
                    if not hasattr(chat_service, "chat_workflow_streaming"):
                        error_chunk = {
                            "type": "error",
                            "error": f"Streaming is not yet supported for workflow '{chat_request.workflow}'.",
                        }
                        yield f"data: {json.dumps(error_chunk)}\n\n"
                    else:
                        async for chunk in chat_service.chat_workflow_streaming(
                            current_user.id, chat_request, workflow_type=workflow_type
                        ):
                            yield f"data: {json.dumps(chunk)}\n\n"
            except (ConversationNotFoundError, ChatError) as e:
                error_chunk = {"type": "error", "error": str(e)}
                yield f"data: {json.dumps(error_chunk)}\n\n"
            finally:
                # End-of-stream marker
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    # Non-streaming mode
    try:
        if workflow_type == "basic":
            conversation, assistant_message = await chat_service.chat(
                current_user.id, chat_request
            )
        else:
            conversation, assistant_message = await chat_service.chat_with_workflow(
                current_user.id, chat_request, workflow_type=workflow_type
            )

        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse.model_validate(assistant_message),
            conversation=ConversationResponse.model_validate(conversation),
        )
    except (ConversationNotFoundError, ChatError) as e:
        raise BadRequestProblem(detail=str(e)) from None


@router.get("/tools/available", response_model=AvailableToolsResponse)
async def get_available_tools(
    current_user: User = Depends(get_current_user),
) -> AvailableToolsResponse:
    """Get list of available MCP tools."""
    from chatter.services.mcp import BuiltInTools, mcp_service

    try:
        # Get MCP tools
        mcp_tools = await mcp_service.get_tools()

        # Get built-in tools
        builtin_tools = BuiltInTools.create_builtin_tools()

        all_tools = []

        # Add MCP tools
        for tool in mcp_tools:
            all_tools.append(
                AvailableToolResponse(
                    name=tool.name,
                    description=tool.description,
                    type="mcp",
                    args_schema=getattr(tool, "args_schema", {}),
                )
            )

        # Add built-in tools
        for tool in builtin_tools:
            all_tools.append(
                AvailableToolResponse(
                    name=tool.name,
                    description=tool.description,
                    type="builtin",
                    args_schema=getattr(tool, "args_schema", {}),
                )
            )

        return AvailableToolsResponse(tools=all_tools)
    except Exception as e:
        raise InternalServerProblem(
            detail=f"Failed to get available tools: {str(e)}"
        ) from None


@router.get("/mcp/status", response_model=McpStatusResponse)
async def get_mcp_status(
    current_user: User = Depends(get_current_user),
) -> McpStatusResponse:
    """Get MCP service status."""
    from chatter.services.mcp import mcp_service

    try:
        result = await mcp_service.health_check()
        return McpStatusResponse(**result)
    except Exception as e:
        raise InternalServerProblem(
            detail=f"Failed to get MCP status: {str(e)}"
        ) from None
