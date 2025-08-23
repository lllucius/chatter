"""Profile management endpoints."""


from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.core.profiles import ProfileError, ProfileService
from chatter.models.user import User
from chatter.schemas.profile import (
    ProfileCloneRequest,
    ProfileCreate,
    ProfileListRequest,
    ProfileListResponse,
    ProfileResponse,
    ProfileStatsResponse,
    ProfileTestRequest,
    ProfileTestResponse,
    ProfileUpdate,
    ProfileGetRequest,
    ProfileDeleteRequest,
    ProfileStatsRequest,
    ProfileProvidersRequest,
)
from chatter.schemas.common import PaginationRequest, SortingRequest
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger
from chatter.utils.problem import BadRequestProblem, NotFoundProblem, InternalServerProblem, ProblemException

logger = get_logger(__name__)
router = APIRouter()


async def get_profile_service(session: AsyncSession = Depends(get_session)) -> ProfileService:
    """Get profile service instance."""
    return ProfileService(session)


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
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
        profile = await profile_service.create_profile(current_user.id, profile_data)
        return ProfileResponse.model_validate(profile)

    except ProfileError as e:
        raise BadRequestProblem(
            detail=str(e)
        )
    except Exception as e:
        logger.error("Profile creation failed", error=str(e))
        raise InternalServerProblem(
            detail="Failed to create profile"
        )


@router.get("/", response_model=ProfileListResponse)
async def list_profiles(
    request: ProfileListRequest = Depends(),
    pagination: PaginationRequest = Depends(),
    sorting: SortingRequest = Depends(),
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> ProfileListResponse:
    """List user's profiles.

    Args:
        request: List request parameters
        pagination: Pagination parameters
        sorting: Sorting parameters
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        List of profiles with pagination info
    """
    try:
        # Get profiles
        profiles, total_count = await profile_service.list_profiles(
            current_user.id, request, pagination, sorting
        )

        return ProfileListResponse(
            profiles=[ProfileResponse.model_validate(profile) for profile in profiles],
            total_count=total_count,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    except Exception as e:
        logger.error("Failed to list profiles", error=str(e))
        raise InternalServerProblem(
            detail="Failed to list profiles"
        )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    request: ProfileGetRequest = Depends(),
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> ProfileResponse:
    """Get profile details.

    Args:
        profile_id: Profile ID
        request: Get request parameters
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Profile information
    """
    try:
        profile = await profile_service.get_profile(profile_id, current_user.id)

        if not profile:
            raise NotFoundProblem(
                detail="Profile not found",
                resource_type="profile",
                resource_id=profile_id
            )

        return ProfileResponse.model_validate(profile)

    except ProblemException:
        raise
    except Exception as e:
        logger.error("Failed to get profile", profile_id=profile_id, error=str(e))
        raise InternalServerProblem(
            detail="Failed to get profile"
        )


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    update_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
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
                resource_id=profile_id
            )

        return ProfileResponse.model_validate(profile)

    except ProfileError as e:
        raise BadRequestProblem(
            detail=str(e)
        )
    except ProblemException:
        raise
    except Exception as e:
        logger.error("Failed to update profile", profile_id=profile_id, error=str(e))
        raise InternalServerProblem(
            detail="Failed to update profile"
        )


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: str,
    request: ProfileDeleteRequest = Depends(),
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> dict:
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
        success = await profile_service.delete_profile(profile_id, current_user.id)

        if not success:
            raise NotFoundProblem(
                detail="Profile not found",
                resource_type="profile",
                resource_id=profile_id
            )

        return {"message": "Profile deleted successfully"}

    except ProblemException:
        raise
    except Exception as e:
        logger.error("Failed to delete profile", profile_id=profile_id, error=str(e))
        raise InternalServerProblem(
            detail="Failed to delete profile"
        )


@router.post("/{profile_id}/test", response_model=ProfileTestResponse)
async def test_profile(
    profile_id: str,
    test_request: ProfileTestRequest,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
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
        result = await profile_service.test_profile(
            profile_id, current_user.id, test_request
        )

        return ProfileTestResponse(**result)

    except ProfileError as e:
        raise BadRequestProblem(
            detail=str(e)
        )
    except Exception as e:
        logger.error("Profile test failed", profile_id=profile_id, error=str(e))
        raise InternalServerProblem(
            detail="Profile test failed"
        )


@router.post("/{profile_id}/clone", response_model=ProfileResponse)
async def clone_profile(
    profile_id: str,
    clone_request: ProfileCloneRequest,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
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
            clone_request.modifications
        )

        return ProfileResponse.model_validate(cloned_profile)

    except ProfileError as e:
        raise BadRequestProblem(
            detail=str(e)
        )
    except Exception as e:
        logger.error("Profile cloning failed", profile_id=profile_id, error=str(e))
        raise InternalServerProblem(
            detail="Profile cloning failed"
        )


@router.get("/stats/overview", response_model=ProfileStatsResponse)
async def get_profile_stats(
    request: ProfileStatsRequest = Depends(),
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> ProfileStatsResponse:
    """Get profile statistics.

    Args:
        request: Stats request parameters
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
        )


@router.get("/providers/available")
async def get_available_providers(
    request: ProfileProvidersRequest = Depends(),
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> dict:
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
        return providers_info

    except Exception as e:
        logger.error("Failed to get available providers", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get available providers"
        )
