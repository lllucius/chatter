"""Profile management endpoints."""


from fastapi import APIRouter, Depends, HTTPException, status
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
)
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger

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
        return ProfileResponse.from_profile(profile)

    except ProfileError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Profile creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create profile"
        )


@router.get("/", response_model=ProfileListResponse)
async def list_profiles(
    profile_type: str = None,
    llm_provider: str = None,
    tags: str = None,  # Comma-separated
    is_public: bool = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> ProfileListResponse:
    """List user's profiles.

    Args:
        profile_type: Filter by profile type
        llm_provider: Filter by LLM provider
        tags: Filter by tags (comma-separated)
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
        # Parse tags
        parsed_tags = None
        if tags:
            parsed_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Create list request
        list_request = ProfileListRequest(
            profile_type=profile_type,
            llm_provider=llm_provider,
            tags=parsed_tags,
            is_public=is_public,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Get profiles
        profiles, total_count = await profile_service.list_profiles(
            current_user.id, list_request
        )

        return ProfileListResponse(
            profiles=[ProfileResponse.from_profile(profile) for profile in profiles],
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error("Failed to list profiles", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list profiles"
        )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
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
        profile = await profile_service.get_profile(profile_id, current_user.id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        return ProfileResponse.from_profile(profile)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get profile", profile_id=profile_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        return ProfileResponse.from_profile(profile)

    except ProfileError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update profile", profile_id=profile_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> dict:
    """Delete profile.

    Args:
        profile_id: Profile ID
        current_user: Current authenticated user
        profile_service: Profile service

    Returns:
        Success message
    """
    try:
        success = await profile_service.delete_profile(profile_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        return {"message": "Profile deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete profile", profile_id=profile_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Profile test failed", profile_id=profile_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Profile cloning failed", profile_id=profile_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile cloning failed"
        )


@router.get("/stats/overview", response_model=ProfileStatsResponse)
async def get_profile_stats(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
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
                ProfileResponse.from_profile(profile)
                for profile in stats.get("most_used_profiles", [])
            ],
            recent_profiles=[
                ProfileResponse.from_profile(profile)
                for profile in stats.get("recent_profiles", [])
            ],
            usage_stats=stats.get("usage_stats", {}),
        )

    except Exception as e:
        logger.error("Failed to get profile stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile stats"
        )


@router.get("/providers/available")
async def get_available_providers(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> dict:
    """Get available LLM providers.

    Args:
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available providers"
        )
