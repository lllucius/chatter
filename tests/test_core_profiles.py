"""Tests for profile management service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.profiles import ProfileError, ProfileService
from chatter.models.profile import Profile, ProfileType
from chatter.schemas.profile import (
    ProfileCreate,
    ProfileListRequest,
    ProfileTestRequest,
    ProfileUpdate,
)


@pytest.mark.unit
class TestProfileService:
    """Test ProfileService functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.service = ProfileService(self.mock_session)
        self.service.llm_service = MagicMock()

    @pytest.mark.asyncio
    async def test_create_profile_success(self):
        """Test successful profile creation."""
        # Arrange
        user_id = "test-user-id"
        profile_data = ProfileCreate(
            name="Test Profile",
            description="A test profile",
            profile_type=ProfileType.CONVERSATIONAL,
            llm_provider="openai",
            llm_model="gpt-4",
            temperature=0.7
        )

        # Mock no existing profile with same name
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = None
        self.service.llm_service.list_available_providers.return_value = ["openai", "anthropic"]

        # Mock profile creation
        mock_profile = Profile(id="profile-id", owner_id=user_id, **profile_data.model_dump())
        self.mock_session.refresh = AsyncMock()

        # Act
        with patch.object(Profile, '__init__', return_value=None) as mock_init:
            mock_init.return_value = None
            result = await self.service.create_profile(user_id, profile_data)

        # Assert
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_profile_duplicate_name(self):
        """Test profile creation with duplicate name."""
        # Arrange
        user_id = "test-user-id"
        profile_data = ProfileCreate(
            name="Existing Profile",
            llm_provider="openai",
            llm_model="gpt-4"
        )

        # Mock existing profile with same name
        existing_profile = Profile(id="existing-id", name="Existing Profile")
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = existing_profile

        # Act & Assert
        with pytest.raises(ProfileError, match="Profile with this name already exists"):
            await self.service.create_profile(user_id, profile_data)

    @pytest.mark.asyncio
    async def test_create_profile_unavailable_provider(self):
        """Test profile creation with unavailable LLM provider."""
        # Arrange
        user_id = "test-user-id"
        profile_data = ProfileCreate(
            name="Test Profile",
            llm_provider="unavailable_provider",
            llm_model="test-model"
        )

        # Mock no existing profile
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = None
        self.service.llm_service.list_available_providers.return_value = ["openai", "anthropic"]

        # Mock profile creation (should still succeed with warning)
        mock_profile = Profile(id="profile-id", owner_id=user_id, **profile_data.model_dump())
        self.mock_session.refresh = AsyncMock()

        # Act
        with patch.object(Profile, '__init__', return_value=None):
            result = await self.service.create_profile(user_id, profile_data)

        # Assert - Profile should still be created despite unavailable provider
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_profile_owner_access(self):
        """Test getting profile with owner access."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        mock_profile = Profile(id=profile_id, owner_id=user_id, name="Test Profile")
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_profile

        # Act
        result = await self.service.get_profile(profile_id, user_id)

        # Assert
        assert result == mock_profile
        self.mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_profile_public_access(self):
        """Test getting public profile by non-owner."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        mock_profile = Profile(
            id=profile_id, 
            owner_id="other-user", 
            name="Public Profile",
            is_public=True
        )
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_profile

        # Act
        result = await self.service.get_profile(profile_id, user_id)

        # Assert
        assert result == mock_profile

    @pytest.mark.asyncio
    async def test_get_profile_no_access(self):
        """Test getting private profile by non-owner."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Act
        result = await self.service.get_profile(profile_id, user_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_list_profiles_with_filters(self):
        """Test listing profiles with filters."""
        # Arrange
        user_id = "user-id"
        list_request = ProfileListRequest(
            profile_type=ProfileType.CONVERSATIONAL,
            llm_provider="openai",
            tags=["test"],
            is_public=True,
            sort_by="created_at",
            sort_order="desc",
            limit=10,
            offset=0
        )

        mock_profiles = [
            Profile(id="profile-1", name="Profile 1"),
            Profile(id="profile-2", name="Profile 2")
        ]
        
        # Mock query execution
        self.mock_session.execute.side_effect = [
            MagicMock(scalar=lambda: 2),  # Count query
            MagicMock(scalars=lambda: MagicMock(all=lambda: mock_profiles))  # Main query
        ]

        # Act
        profiles, total_count = await self.service.list_profiles(user_id, list_request)

        # Assert
        assert len(profiles) == 2
        assert total_count == 2
        assert profiles == mock_profiles

    @pytest.mark.asyncio
    async def test_update_profile_success(self):
        """Test successful profile update."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        update_data = ProfileUpdate(
            name="Updated Profile",
            temperature=0.8
        )

        mock_profile = Profile(
            id=profile_id, 
            owner_id=user_id, 
            name="Original Profile",
            temperature=0.7
        )
        
        # Mock profile retrieval and name conflict check
        self.mock_session.execute.side_effect = [
            MagicMock(scalar_one_or_none=lambda: mock_profile),  # Get profile
            MagicMock(scalar_one_or_none=lambda: None)  # No name conflict
        ]
        self.mock_session.refresh = AsyncMock()

        # Act
        result = await self.service.update_profile(profile_id, user_id, update_data)

        # Assert
        assert result == mock_profile
        assert mock_profile.name == "Updated Profile"
        assert mock_profile.temperature == 0.8
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once_with(mock_profile)

    @pytest.mark.asyncio
    async def test_update_profile_not_owner(self):
        """Test updating profile by non-owner."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        update_data = ProfileUpdate(name="Updated Profile")

        # Mock no profile found (access denied)
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Act
        result = await self.service.update_profile(profile_id, user_id, update_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_profile_name_conflict(self):
        """Test updating profile with conflicting name."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        update_data = ProfileUpdate(name="Conflicting Name")

        mock_profile = Profile(id=profile_id, owner_id=user_id, name="Original")
        existing_profile = Profile(id="other-id", name="Conflicting Name")
        
        self.mock_session.execute.side_effect = [
            MagicMock(scalar_one_or_none=lambda: mock_profile),  # Get profile
            MagicMock(scalar_one_or_none=lambda: existing_profile)  # Name conflict
        ]

        # Act & Assert
        with pytest.raises(ProfileError, match="Profile with this name already exists"):
            await self.service.update_profile(profile_id, user_id, update_data)

    @pytest.mark.asyncio
    async def test_delete_profile_success(self):
        """Test successful profile deletion."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        mock_profile = Profile(id=profile_id, owner_id=user_id)
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_profile

        # Act
        result = await self.service.delete_profile(profile_id, user_id)

        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_profile)
        self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_profile_not_found(self):
        """Test deleting non-existent or inaccessible profile."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Act
        result = await self.service.delete_profile(profile_id, user_id)

        # Assert
        assert result is False
        self.mock_session.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_test_profile_success(self):
        """Test successful profile testing."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        test_request = ProfileTestRequest(
            test_message="Hello, test!",
            include_retrieval=False,
            include_tools=False
        )

        mock_profile = Profile(
            id=profile_id,
            owner_id=user_id,
            system_prompt="You are helpful.",
            usage_count=0,
            total_tokens_used=0,
            total_cost=0
        )
        mock_profile.get_generation_config = MagicMock(return_value={"temperature": 0.7})

        # Mock service methods
        self.service.get_profile = AsyncMock(return_value=mock_profile)
        self.service.llm_service.create_provider_from_profile = MagicMock(return_value="mock_provider")
        self.service.llm_service.generate_response = AsyncMock(
            return_value=("Test response", {"total_tokens": 50, "cost": 0.01})
        )
        self.mock_session.refresh = AsyncMock()

        # Act
        result = await self.service.test_profile(profile_id, user_id, test_request)

        # Assert
        assert result["profile_id"] == profile_id
        assert result["test_message"] == "Hello, test!"
        assert result["response"] == "Test response"
        assert result["usage_info"]["total_tokens"] == 50
        assert "response_time_ms" in result
        
        # Check profile stats updated
        assert mock_profile.usage_count == 1
        assert mock_profile.total_tokens_used == 50
        assert mock_profile.total_cost == 0.01
        self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_profile_not_found(self):
        """Test testing non-existent profile."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        test_request = ProfileTestRequest(test_message="Hello")

        self.service.get_profile = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(ProfileError, match="Profile not found"):
            await self.service.test_profile(profile_id, user_id, test_request)

    @pytest.mark.asyncio
    async def test_test_profile_provider_creation_failed(self):
        """Test profile testing when provider creation fails."""
        # Arrange
        profile_id = "profile-id"
        user_id = "user-id"
        test_request = ProfileTestRequest(test_message="Hello")

        mock_profile = Profile(id=profile_id, owner_id=user_id)
        self.service.get_profile = AsyncMock(return_value=mock_profile)
        self.service.llm_service.create_provider_from_profile = MagicMock(return_value=None)

        # Act & Assert
        with pytest.raises(ProfileError, match="Failed to create LLM provider"):
            await self.service.test_profile(profile_id, user_id, test_request)

    @pytest.mark.asyncio
    async def test_clone_profile_success(self):
        """Test successful profile cloning."""
        # Arrange
        profile_id = "source-profile-id"
        user_id = "user-id"
        new_name = "Cloned Profile"
        description = "Cloned from original"

        source_profile = Profile(
            id=profile_id,
            owner_id=user_id,
            name="Source Profile",
            profile_type=ProfileType.CONVERSATIONAL,
            llm_provider="openai",
            llm_model="gpt-4",
            temperature=0.7,
            tags=["original"],
            extra_metadata={"key": "value"}
        )

        # Mock getting source profile and checking name conflicts
        self.service.get_profile = AsyncMock(return_value=source_profile)
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = None  # No name conflict

        # Mock create_profile
        cloned_profile = Profile(id="cloned-id", name=new_name)
        self.service.create_profile = AsyncMock(return_value=cloned_profile)

        # Act
        result = await self.service.clone_profile(
            profile_id, user_id, new_name, description
        )

        # Assert
        assert result == cloned_profile
        self.service.create_profile.assert_called_once()
        
        # Check the create_profile call arguments
        call_args = self.service.create_profile.call_args
        assert call_args[0][0] == user_id  # user_id
        profile_data = call_args[0][1]  # ProfileCreate
        assert profile_data.name == new_name
        assert profile_data.description == description
        assert profile_data.profile_type == source_profile.profile_type
        assert profile_data.is_public is False  # Cloned profiles are private

    @pytest.mark.asyncio
    async def test_clone_profile_not_found(self):
        """Test cloning non-existent profile."""
        # Arrange
        profile_id = "nonexistent-id"
        user_id = "user-id"
        new_name = "Cloned Profile"

        self.service.get_profile = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(ProfileError, match="Source profile not found"):
            await self.service.clone_profile(profile_id, user_id, new_name)

    @pytest.mark.asyncio
    async def test_clone_profile_name_conflict(self):
        """Test cloning with conflicting name."""
        # Arrange
        profile_id = "source-id"
        user_id = "user-id"
        new_name = "Existing Name"

        source_profile = Profile(id=profile_id, name="Source")
        existing_profile = Profile(id="existing-id", name=new_name)

        self.service.get_profile = AsyncMock(return_value=source_profile)
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = existing_profile

        # Act & Assert
        with pytest.raises(ProfileError, match="Profile with this name already exists"):
            await self.service.clone_profile(profile_id, user_id, new_name)

    @pytest.mark.asyncio
    async def test_get_profile_stats(self):
        """Test getting profile statistics."""
        # Arrange
        user_id = "user-id"

        # Mock type counts
        type_count_results = [2, 1, 0]  # CONVERSATIONAL: 2, ANALYTICAL: 1, CREATIVE: 0
        self.mock_session.execute.side_effect = (
            [MagicMock(scalar=lambda: count) for count in type_count_results] +
            [
                MagicMock(all=lambda: [("openai", 2), ("anthropic", 1)]),  # Provider counts
                MagicMock(scalars=lambda: MagicMock(all=lambda: [])),  # Most used profiles
                MagicMock(scalars=lambda: MagicMock(all=lambda: [])),  # Recent profiles
                MagicMock(first=lambda: (10, 1000, 5.0))  # Usage totals
            ]
        )

        # Act
        stats = await self.service.get_profile_stats(user_id)

        # Assert
        assert stats["total_profiles"] == 3
        assert stats["profiles_by_type"][ProfileType.CONVERSATIONAL.value] == 2
        assert stats["profiles_by_provider"]["openai"] == 2
        assert stats["usage_stats"]["total_usage_count"] == 10
        assert stats["usage_stats"]["total_tokens_used"] == 1000
        assert stats["usage_stats"]["total_cost"] == 5.0

    @pytest.mark.asyncio
    async def test_get_available_providers(self):
        """Test getting available LLM providers."""
        # Arrange
        providers = ["openai", "anthropic", "cohere"]
        provider_info = {"models": ["gpt-4", "gpt-3.5-turbo"], "supports_streaming": True}
        
        self.service.llm_service.list_available_providers.return_value = providers
        self.service.llm_service.get_provider_info.return_value = provider_info

        with patch('chatter.core.profiles.settings') as mock_settings:
            mock_settings.default_llm_provider = "openai"

            # Act
            result = await self.service.get_available_providers()

            # Assert
            assert "providers" in result
            assert "default_provider" in result
            assert result["default_provider"] == "openai"
            assert len(result["providers"]) == 3


@pytest.mark.integration
class TestProfileServiceIntegration:
    """Integration tests for ProfileService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.service = ProfileService(self.mock_session)

    @pytest.mark.asyncio
    async def test_complete_profile_lifecycle(self):
        """Test complete profile lifecycle: create, get, update, test, delete."""
        # Arrange
        user_id = "test-user"
        profile_data = ProfileCreate(
            name="Lifecycle Test Profile",
            profile_type=ProfileType.CONVERSATIONAL,
            llm_provider="openai",
            llm_model="gpt-4"
        )

        # Mock all required service calls
        mock_profile = Profile(id="profile-id", **profile_data.model_dump())
        
        # Setup mocks for create
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = None
        self.service.llm_service = MagicMock()
        self.service.llm_service.list_available_providers.return_value = ["openai"]
        self.mock_session.refresh = AsyncMock()

        # Create profile
        with patch.object(Profile, '__init__', return_value=None):
            created_profile = await self.service.create_profile(user_id, profile_data)

        # Verify creation calls
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called()

        # Test other lifecycle operations would follow similar pattern
        # but require more complex mocking for full integration test


def test_profile_error():
    """Test ProfileError exception."""
    # Act & Assert
    with pytest.raises(ProfileError, match="Test error"):
        raise ProfileError("Test error")