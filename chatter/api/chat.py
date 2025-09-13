"""Consolidated chat endpoints using resource-based patterns."""

import json

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import StreamingResponse
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
from chatter.core.exceptions import ChatServiceError, NotFoundError
from chatter.models.conversation import ConversationStatus
from chatter.models.user import User
from chatter.schemas.chat import (
    AvailableToolResponse,
    AvailableToolsResponse,
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationDeleteResponse,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    ConversationWithMessages,
    McpStatusResponse,
    MessageDeleteResponse,
    MessageRatingResponse,
    MessageRatingUpdate,
    MessageResponse,
    PerformanceStatsResponse,
    WorkflowTemplateInfo,
    WorkflowTemplatesResponse,
)
from chatter.services.chat import ChatService
from chatter.services.llm import LLMService
from chatter.utils.database import get_session_generator
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    InternalServerProblem,
    NotFoundProblem,
)

logger = get_logger(__name__)
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


def _map_workflow_type(workflow: str | None) -> str:
    """Map API workflow to internal workflow types."""
    workflow_mapping = {
        "plain": "basic",
        "rag": "rag",
        "tools": "tools",
        "full": "full",
    }
    return workflow_mapping.get(workflow or "plain", "basic")


# Conversation Resource Endpoints


@router.post(
    "/conversations",
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
    "/conversations",
    response_model=ConversationListResponse,
)
async def list_conversations(
    status: ConversationStatus | None = Query(
        None, description="Filter by conversation status"
    ),
    llm_provider: str | None = Query(
        None, description="Filter by LLM provider"
    ),
    llm_model: str | None = Query(
        None, description="Filter by LLM model"
    ),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    enable_retrieval: bool | None = Query(
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
    """List conversations for the current user.

    Args:
        status: Filter by conversation status
        llm_provider: Filter by LLM provider
        llm_model: Filter by LLM model
        tags: Filter by tags
        enable_retrieval: Filter by retrieval enabled status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        handler: Conversation resource handler

    Returns:
        List of conversations with pagination info
    """
    # Create ConversationListRequest object to pass filters
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
    "/conversations/{conversation_id}",
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
    "/conversations/{conversation_id}",
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
    "/conversations/{conversation_id}",
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
    "/conversations/{conversation_id}/messages",
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
    "/conversations/{conversation_id}/messages/{message_id}",
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
    "/conversations/{conversation_id}/messages/{message_id}/rating",
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


# Core Chat Endpoint (Unified)


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Non-streaming chat endpoint supporting all workflow types."""
    workflow_type = _map_workflow_type(chat_request.workflow)
    chat_request.workflow_type = workflow_type

    try:
        conversation, assistant_message = await chat_service.chat(
            current_user.id, chat_request
        )
        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse.model_validate(assistant_message),
            conversation=ConversationResponse.model_validate(
                conversation
            ),
        )
    except (NotFoundError, ChatServiceError) as e:
        raise BadRequestProblem(detail=str(e)) from e


@router.post(
    "/streaming",
    response_model=None,  # Disable response model generation for SSE
    responses={
        200: {
            "content": {
                "text/event-stream": {"schema": {"type": "string"}},
            },
            "description": "Streaming chat response using Server-Sent Events",
        }
    },
)
async def streaming_chat(
    chat_request: ChatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Streaming chat endpoint supporting all workflow types."""
    workflow_type = _map_workflow_type(chat_request.workflow)
    chat_request.workflow_type = workflow_type

    # Streaming mode
    async def generate_stream():
        try:
            async for chunk in chat_service.chat_streaming(
                current_user.id, chat_request
            ):
                if await request.is_disconnected():
                    logger.info("Client disconnected during streaming")
                    break
                yield f"data: {json.dumps(chunk.model_dump())}\n\n"
        except (NotFoundError, ChatServiceError) as e:
            error_chunk = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error_chunk)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# Utility Endpoints


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
            args_schema = getattr(tool, "args_schema", {})
            # Convert Pydantic model to dict if needed
            if hasattr(args_schema, "model_json_schema"):
                args_schema = args_schema.model_json_schema()
            elif hasattr(args_schema, "__dict__") and not isinstance(
                args_schema, dict
            ):
                args_schema = {}

            all_tools.append(
                AvailableToolResponse(
                    name=tool.name,
                    description=tool.description,
                    type="mcp",
                    args_schema=args_schema,
                )
            )

        # Add built-in tools
        for tool in builtin_tools:
            args_schema = getattr(tool, "args_schema", {})
            # Convert Pydantic model to dict if needed
            if hasattr(args_schema, "model_json_schema"):
                args_schema = args_schema.model_json_schema()
            elif hasattr(args_schema, "__dict__") and not isinstance(
                args_schema, dict
            ):
                args_schema = {}

            all_tools.append(
                AvailableToolResponse(
                    name=tool.name,
                    description=tool.description,
                    type="builtin",
                    args_schema=args_schema,
                )
            )

        return AvailableToolsResponse(tools=all_tools)
    except Exception as e:
        raise InternalServerProblem(
            detail=f"Failed to get available tools: {str(e)}"
        ) from e


@router.get("/templates", response_model=WorkflowTemplatesResponse)
async def get_workflow_templates(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> WorkflowTemplatesResponse:
    """Get available workflow templates."""
    try:
        from chatter.core.unified_template_manager import (
            get_template_manager_with_session,
        )

        template_manager = get_template_manager_with_session(session)
        templates_data = await template_manager.get_template_info(
            owner_id=current_user.id
        )
        templates = {
            name: WorkflowTemplateInfo(**template_info)
            for name, template_info in templates_data.items()
        }

        return WorkflowTemplatesResponse(
            templates=templates, total_count=len(templates)
        )
    except Exception as e:
        raise InternalServerProblem(
            detail=f"Failed to get workflow templates: {str(e)}"
        ) from e


@router.post("/template/{template_name}")
async def chat_with_template(
    template_name: str,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Chat using a specific workflow template."""
    try:
        # Add template name to system prompt override
        template_instruction = f"[TEMPLATE:{template_name}]"
        if chat_request.system_prompt_override:
            chat_request.system_prompt_override = f"{template_instruction} {chat_request.system_prompt_override}"
        else:
            chat_request.system_prompt_override = template_instruction

        chat_request.workflow_type = "basic"
        conversation, assistant_message = await chat_service.chat(
            current_user.id, chat_request
        )

        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse.model_validate(assistant_message),
            conversation=ConversationResponse.model_validate(
                conversation
            ),
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundProblem(
                detail=f"Template '{template_name}' not found"
            ) from e
        raise BadRequestProblem(detail=str(e)) from e


@router.get(
    "/performance/stats", response_model=PerformanceStatsResponse
)
async def get_performance_stats(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> PerformanceStatsResponse:
    """Get workflow performance statistics."""
    try:
        stats = chat_service.get_performance_stats()
        return PerformanceStatsResponse(
            **stats, timestamp=__import__("time").time()
        )
    except Exception as e:
        raise InternalServerProblem(
            detail=f"Failed to get performance stats: {str(e)}"
        ) from e


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
        ) from e
