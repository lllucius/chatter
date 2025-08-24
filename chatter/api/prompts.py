"""Prompt management endpoints."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.core.prompts import PromptError, PromptService
from chatter.models.prompt import PromptCategory, PromptType
from chatter.models.user import User
from chatter.schemas.prompt import (
    PromptCloneRequest,
    PromptCreate,
    PromptDeleteRequest,
    PromptDeleteResponse,
    PromptListResponse,
    PromptResponse,
    PromptStatsResponse,
    PromptTestRequest,
    PromptTestResponse,
    PromptUpdate,
)
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    InternalServerProblem,
    NotFoundProblem,
    ProblemException,
)

logger = get_logger(__name__)
router = APIRouter()


async def get_prompt_service(
    session: AsyncSession = Depends(get_session)
) -> PromptService:
    """Get prompt service instance."""
    return PromptService(session)


@router.post(
    "/",
    response_model=PromptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_prompt(
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptResponse:
    """Create a new prompt.

    Args:
        prompt_data: Prompt creation data
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Created prompt information
    """
    try:
        prompt = await prompt_service.create_prompt(
            current_user.id, prompt_data
        )
        return PromptResponse.model_validate(prompt)

    except PromptError as e:
        raise BadRequestProblem(detail=str(e)) from None
    except Exception as e:
        logger.error("Prompt creation failed", error=str(e))
        raise InternalServerProblem(
            detail="Failed to create prompt"
        ) from None


@router.get("", response_model=PromptListResponse)
async def list_prompts(
    prompt_type: PromptType | None = Query(None, description="Filter by prompt type"),
    category: PromptCategory | None = Query(None, description="Filter by category"),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    is_public: bool | None = Query(None, description="Filter by public status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptListResponse:
    """List user's prompts.

    Args:
        prompt_type: Filter by prompt type
        category: Filter by category
        tags: Filter by tags
        is_public: Filter by public status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        List of prompts with pagination info
    """
    try:
        # Create request object from query parameters
        from chatter.schemas.prompt import PromptListRequest
        merged_request = PromptListRequest(
            prompt_type=prompt_type,
            category=category,
            tags=tags,
            is_public=is_public,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Get prompts
        prompts, total_count = await prompt_service.list_prompts(
            current_user.id, merged_request
        )

        return PromptListResponse(
            prompts=[
                PromptResponse.model_validate(prompt)
                for prompt in prompts
            ],
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error("Failed to list prompts", error=str(e))
        raise InternalServerProblem(
            detail="Failed to list prompts"
        ) from None


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: str,
    current_user: User = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptResponse:
    """Get prompt details.

    Args:
        prompt_id: Prompt ID
        request: Get request parameters
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Prompt information
    """
    try:
        prompt = await prompt_service.get_prompt(
            prompt_id, current_user.id
        )

        if not prompt:
            raise NotFoundProblem(
                detail="Prompt not found",
                resource_type="prompt",
                resource_id=prompt_id,
            ) from None

        return PromptResponse.model_validate(prompt)

    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get prompt", prompt_id=prompt_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to get prompt"
        ) from None


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: str,
    update_data: PromptUpdate,
    current_user: User = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptResponse:
    """Update prompt.

    Args:
        prompt_id: Prompt ID
        update_data: Update data
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Updated prompt information
    """
    try:
        prompt = await prompt_service.update_prompt(
            prompt_id, current_user.id, update_data
        )

        if not prompt:
            raise NotFoundProblem(
                detail="Prompt not found",
                resource_type="prompt",
                resource_id=prompt_id,
            ) from None

        return PromptResponse.model_validate(prompt)

    except PromptError as e:
        raise BadRequestProblem(detail=str(e)) from None
    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update prompt", prompt_id=prompt_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to update prompt"
        ) from None


@router.delete("/{prompt_id}", response_model=PromptDeleteResponse)
async def delete_prompt(
    prompt_id: str,
    request: PromptDeleteRequest = Depends(),
    current_user: User = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptDeleteResponse:
    """Delete prompt.

    Args:
        prompt_id: Prompt ID
        request: Delete request parameters
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Success message
    """
    try:
        success = await prompt_service.delete_prompt(
            prompt_id, current_user.id
        )

        if not success:
            raise NotFoundProblem(
                detail="Prompt not found",
                resource_type="prompt",
                resource_id=prompt_id,
            ) from None

        return PromptDeleteResponse(
            message="Prompt deleted successfully"
        )

    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete prompt", prompt_id=prompt_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to delete prompt"
        ) from None


@router.post("/{prompt_id}/test", response_model=PromptTestResponse)
async def test_prompt(
    prompt_id: str,
    test_request: PromptTestRequest,
    current_user: User = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptTestResponse:
    """Test prompt with given variables.

    Args:
        prompt_id: Prompt ID
        test_request: Test request
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Test results
    """
    try:
        result = await prompt_service.test_prompt(
            prompt_id, current_user.id, test_request
        )

        return PromptTestResponse(**result)

    except PromptError as e:
        raise BadRequestProblem(detail=str(e)) from None
    except Exception as e:
        logger.error(
            "Prompt test failed", prompt_id=prompt_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Prompt test failed"
        ) from None


@router.post("/{prompt_id}/clone", response_model=PromptResponse)
async def clone_prompt(
    prompt_id: str,
    clone_request: PromptCloneRequest,
    current_user: User = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptResponse:
    """Clone an existing prompt.

    Args:
        prompt_id: Source prompt ID
        clone_request: Clone request
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Cloned prompt information
    """
    try:
        cloned_prompt = await prompt_service.clone_prompt(
            prompt_id,
            current_user.id,
            clone_request.name,
            clone_request.description,
            clone_request.modifications,
        )

        return PromptResponse.model_validate(cloned_prompt)

    except PromptError as e:
        raise BadRequestProblem(detail=str(e)) from None
    except Exception as e:
        logger.error(
            "Prompt cloning failed", prompt_id=prompt_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Prompt cloning failed"
        ) from None


@router.get("/stats/overview", response_model=PromptStatsResponse)
async def get_prompt_stats(
    current_user: User = Depends(get_current_user),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptStatsResponse:
    """Get prompt statistics.

    Args:
        request: Stats request parameters
        current_user: Current authenticated user
        prompt_service: Prompt service

    Returns:
        Prompt statistics
    """
    try:
        stats = await prompt_service.get_prompt_stats(current_user.id)

        return PromptStatsResponse(
            total_prompts=stats.get("total_prompts", 0),
            prompts_by_type=stats.get("prompts_by_type", {}),
            prompts_by_category=stats.get("prompts_by_category", {}),
            most_used_prompts=[
                PromptResponse.model_validate(prompt)
                for prompt in stats.get("most_used_prompts", [])
            ],
            recent_prompts=[
                PromptResponse.model_validate(prompt)
                for prompt in stats.get("recent_prompts", [])
            ],
            usage_stats=stats.get("usage_stats", {}),
        )

    except Exception as e:
        logger.error("Failed to get prompt stats", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get prompt stats"
        ) from None
