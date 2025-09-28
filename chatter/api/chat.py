"""Chat API endpoints - dedicated endpoints for chat functionality."""

import json
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.chat import ChatResponse
from chatter.schemas.workflows import ChatWorkflowRequest
from chatter.services.workflow_execution import WorkflowExecutionService
from chatter.utils.logging import get_logger
from chatter.utils.problem import InternalServerProblem
from chatter.utils.unified_rate_limiter import rate_limit

logger = get_logger(__name__)
router = APIRouter()


def get_workflow_execution_service() -> WorkflowExecutionService:
    """Get workflow execution service instance."""
    # Import here to avoid circular dependencies
    from chatter.services.workflow_execution import WorkflowExecutionService
    from chatter.utils.database import get_session_maker
    
    async_session = get_session_maker()
    return WorkflowExecutionService(async_session)


@router.post("/chat", response_model=ChatResponse)
@rate_limit(max_requests=30, window_seconds=60)
async def chat_endpoint(
    request: ChatWorkflowRequest,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowExecutionService = Depends(
        get_workflow_execution_service
    ),
) -> ChatResponse:
    """Non-streaming chat endpoint using workflow execution."""
    try:
        (
            conversation,
            message,
        ) = await workflow_service.execute_chat_workflow(
            user_id=current_user.id, request=request
        )

        from chatter.schemas.chat import (
            ConversationResponse,
            MessageResponse,
        )

        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse.model_validate(message),
            conversation=ConversationResponse.model_validate(
                conversation
            ),
        )
    except Exception as e:
        logger.error(f"Failed to execute chat workflow: {e}")
        raise InternalServerProblem(
            detail=f"Failed to execute chat workflow: {str(e)}"
        ) from e


@router.post(
    "/streaming",
    responses={
        200: {
            "description": "Streaming chat response",
            "content": {
                "text/event-stream": {"schema": {"type": "string"}}
            },
        }
    },
)
@rate_limit(max_requests=20, window_seconds=60)
async def streaming_chat_endpoint(
    request: ChatWorkflowRequest,
    chat_request: Request,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowExecutionService = Depends(
        get_workflow_execution_service
    ),
):
    """Streaming chat endpoint using workflow execution."""

    async def generate_stream():
        try:
            async for (
                chunk
            ) in workflow_service.execute_chat_workflow_streaming(
                user_id=current_user.id, request=request
            ):
                if await chat_request.is_disconnected():
                    logger.info("Client disconnected during streaming")
                    break
                yield f"data: {json.dumps(chunk.model_dump())}\n\n"
        except Exception as e:
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