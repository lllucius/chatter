"""Profile management endpoints."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.core.profiles import ProfileError, ProfileService
from chatter.models.profile import ProfileType
from chatter.models.user import User
from chatter.schemas.profile import (
    AvailableProvidersResponse,
    ProfileCloneRequest,
    ProfileCreate,
    ProfileDeleteRequest,
    ProfileDeleteResponse,
    ProfileListResponse,
    ProfileResponse,
    ProfileStatsResponse,
    ProfileTestRequest,
    ProfileTestResponse,
    ProfileUpdate,
)
from chatter.utils.database import get_session_generator
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    InternalServerProblem,
    NotFoundProblem,
    ProblemException,
    RateLimitProblem,
    ValidationProblem,
)
from chatter.utils.unified_rate_limiter import get_unified_rate_limiter, RateLimitExceeded

logger = get_logger(__name__)
router = APIRouter()

# Rate limiter for expensive operations
rate_limiter = get_unified_rate_limiter()


async def get_profile_service(
    session: AsyncSession = Depends(get_session_generator),
) -> ProfileService:
    """Get profile service instance."""
    return ProfileService(session)


@router.post(
    "/",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Create a new LLM profile.

    Args:
        profile_data: Profile creation data
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Created profile information
    """
    try:
        # Rate limiting for profile creation to prevent spam
        rate_limit_key = f"profile_create:{current_user.id}"
        try:
            # Check hourly limit
            await rate_limiter.check_rate_limit(
                key=rate_limit_key,
                limit=10,  # Max 10 profile creations per hour
                window=3600,  # 1 hour in seconds
                identifier="profile_create_hourly",
            )
            # Check daily limit
            await rate_limiter.check_rate_limit(
                key=rate_limit_key,
                limit=50,    # Max 50 profile creations per day
                window=86400,  # 1 day in seconds
                identifier="profile_create_daily",
            )
        except RateLimitExceeded as e:
            logger.warning(
                "Rate limit exceeded for profile creation",
                user_id=current_user.id
            )
            raise RateLimitProblem(
                detail="Profile creation rate limit exceeded. You can create up to 10 profiles per hour and 50 per day.",
                retry_after=3600  # Suggest retry after 1 hour
            ) from e

        profile = await profile_service.create_profile(
            current_user.id, profile_data
        )
        return ProfileResponse.model_validate(profile)

    except ProfileError as e:
        raise ValidationProblem(
            detail=f"Profile creation failed: {str(e)}",
            validation_errors=[{"field": "profile", "message": str(e)}]
        ) from None
    except ProblemException:
        raise
    except Exception as e:
        logger.error("Profile creation failed", error=str(e))
        raise InternalServerProblem(
            detail="Failed to create profile"
        ) from None


@router.get("", response_model=ProfileListResponse)
async def list_profiles(
    profile_type: ProfileType | None = Query(
        None, description="Filter by profile type"
    ),
    llm_provider: str | None = Query(
        None, description="Filter by LLM provider"
    ),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    is_public: bool | None = Query(
        None, description="Filter by public status"
    ),
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of results"
    ),
    offset: int = Query(
        0, ge=0, description="Number of results to skip"
    ),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query(
        "desc", pattern="^(asc|desc)$", description="Sort order"
    ),
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileListResponse:
    """List user's profiles.

    Args:
        profile_type: Filter by profile type
        llm_provider: Filter by LLM provider
        tags: Filter by tags
        is_public: Filter by public status
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Sort field
        sort_order: Sort order (asc/desc)
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        List of profiles with pagination info
    """
    try:
        # Create request object from query parameters
        from chatter.schemas.profile import ProfileListRequest

        merged_request = ProfileListRequest(
            profile_type=profile_type,
            llm_provider=llm_provider,
            tags=tags,
            is_public=is_public,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Get profiles
        profiles, total_count = await profile_service.list_profiles(
            current_user.id, merged_request
        )

        return ProfileListResponse(
            profiles=[
                ProfileResponse.model_validate(profile)
                for profile in profiles
            ],
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error("Failed to list profiles", error=str(e))
        raise InternalServerProblem(
            detail="Failed to list profiles"
        ) from None


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Get profile details.

    Args:
        profile_id: Profile ID
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Profile information
    """
    try:
        profile = await profile_service.get_profile(
            profile_id, current_user.id
        )

        if not profile:
            raise NotFoundProblem(
                detail="Profile not found",
                resource_type="profile",
                resource_id=profile_id,
            ) from None

        return ProfileResponse.model_validate(profile)

    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get profile", profile_id=profile_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to get profile"
        ) from None


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    update_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Update profile.

    Args:
        profile_id: Profile ID
        update_data: Update data
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Updated profile information
    """
    try:
        profile = await profile_service.update_profile(
            profile_id, current_user.id, update_data
        )

        if not profile:
            raise NotFoundProblem(
                detail="Profile not found",
                resource_type="profile",
                resource_id=profile_id,
            ) from None

        return ProfileResponse.model_validate(profile)

    except ProfileError as e:
        raise ValidationProblem(
            detail=f"Profile update failed: {str(e)}",
            validation_errors=[{"field": "profile", "message": str(e)}]
        ) from None
    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update profile",
            profile_id=profile_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to update profile"
        ) from None


@router.delete("/{profile_id}", response_model=ProfileDeleteResponse)
async def delete_profile(
    profile_id: str,
    request: ProfileDeleteRequest = Depends(),
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileDeleteResponse:
    """Delete profile.

    Args:
        profile_id: Profile ID
        request: Delete request parameters
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Success message
    """
    try:
        success = await profile_service.delete_profile(
            profile_id, current_user.id
        )

        if not success:
            raise NotFoundProblem(
                detail="Profile not found",
                resource_type="profile",
                resource_id=profile_id,
            ) from None

        return ProfileDeleteResponse(
            message="Profile deleted successfully"
        )

    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete profile",
            profile_id=profile_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to delete profile"
        ) from None


@router.post("/{profile_id}/test", response_model=ProfileTestResponse)
async def test_profile(
    profile_id: str,
    test_request: ProfileTestRequest,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileTestResponse:
    """Test profile with a sample message.

    Args:
        profile_id: Profile ID
        test_request: Test request
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Test results
    """
    try:
        # Rate limiting for expensive LLM operations
        rate_limit_key = f"profile_test:{current_user.id}"
        try:
            # Check hourly limit
            await rate_limiter.check_rate_limit(
                key=rate_limit_key,
                limit=20,  # Max 20 tests per hour per user
                window=3600,  # 1 hour in seconds
                identifier="profile_test_hourly",
            )
            # Check daily limit
            await rate_limiter.check_rate_limit(
                key=rate_limit_key,
                limit=100,   # Max 100 tests per day per user
                window=86400,  # 1 day in seconds
                identifier="profile_test_daily",
            )
        except RateLimitExceeded as e:
            logger.warning(
                "Rate limit exceeded for profile test",
                user_id=current_user.id,
                profile_id=profile_id
            )
            raise RateLimitProblem(
                detail="Profile testing rate limit exceeded. You can test up to 20 profiles per hour and 100 per day.",
                retry_after=1800  # Suggest retry after 30 minutes
            ) from e

        result = await profile_service.test_profile(
            profile_id, current_user.id, test_request
        )

        return ProfileTestResponse(**result)

    except ProfileError as e:
        raise ValidationProblem(
            detail=f"Profile test failed: {str(e)}",
            validation_errors=[{"field": "profile", "message": str(e)}]
        ) from None
    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Profile test failed", profile_id=profile_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Profile test failed"
        ) from None


@router.post("/{profile_id}/clone", response_model=ProfileResponse)
async def clone_profile(
    profile_id: str,
    clone_request: ProfileCloneRequest,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Clone an existing profile.

    Args:
        profile_id: Source profile ID
        clone_request: Clone request
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Cloned profile information
    """
    try:
        cloned_profile = await profile_service.clone_profile(
            profile_id,
            current_user.id,
            clone_request.name,
            clone_request.description,
            clone_request.modifications,
        )

        return ProfileResponse.model_validate(cloned_profile)

    except ProfileError as e:
        raise ValidationProblem(
            detail=f"Profile cloning failed: {str(e)}",
            validation_errors=[{"field": "profile", "message": str(e)}]
        ) from None
    except Exception as e:
        logger.error(
            "Profile cloning failed",
            profile_id=profile_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Profile cloning failed"
        ) from None


@router.get("/stats/overview", response_model=ProfileStatsResponse)
async def get_profile_stats(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileStatsResponse:
    """Get profile statistics.

    Args:
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Profile statistics
    """
    try:
        stats = await profile_service.get_profile_stats(current_user.id)

        return ProfileStatsResponse(
            total_profiles=stats.get("total_profiles", 0),
            profiles_by_type=stats.get("profiles_by_type", {}),
            profiles_by_provider=stats.get("profiles_by_provider", {}),
            most_used_profiles=[
                ProfileResponse.model_validate(profile)
                for profile in stats.get("most_used_profiles", [])
            ],
            recent_profiles=[
                ProfileResponse.model_validate(profile)
                for profile in stats.get("recent_profiles", [])
            ],
            usage_stats=stats.get("usage_stats", {}),
        )

    except Exception as e:
        logger.error("Failed to get profile stats", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get profile stats"
        ) from None


@router.get(
    "/providers/available", response_model=AvailableProvidersResponse
)
async def get_available_providers(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> AvailableProvidersResponse:
    """Get available LLM providers.

    Args:
        request: Providers request parameters
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Available providers information
    """
    try:
        providers_info = await profile_service.get_available_providers()
        return AvailableProvidersResponse(
            providers=providers_info,
            total_providers=len(providers_info),
            supported_features=providers_info.get(
                "supported_features", {}
            ),
        )

    except Exception as e:
        logger.error("Failed to get available providers", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get available providers"
        ) from None
