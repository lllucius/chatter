"""Unit tests for profiles API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from chatter.core.profiles import ProfileError


class TestProfilesUnit:
    """Unit tests for profiles API endpoints."""

    @pytest.mark.unit
    async def test_create_profile_requires_auth(
        self, client: AsyncClient
    ):
        """Test that creating profile requires authentication."""
        profile_data = {
            "name": "Test Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-4",
        }

        response = await client.post(
            "/api/v1/profiles/", json=profile_data
        )
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_list_profiles_requires_auth(
        self, client: AsyncClient
    ):
        """Test that listing profiles requires authentication."""
        response = await client.get("/api/v1/profiles")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_profile_requires_auth(self, client: AsyncClient):
        """Test that getting specific profile requires authentication."""
        response = await client.get("/api/v1/profiles/profile-id")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_update_profile_requires_auth(
        self, client: AsyncClient
    ):
        """Test that updating profile requires authentication."""
        response = await client.put(
            "/api/v1/profiles/profile-id", json={}
        )
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_delete_profile_requires_auth(
        self, client: AsyncClient
    ):
        """Test that deleting profile requires authentication."""
        response = await client.delete("/api/v1/profiles/profile-id")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_test_profile_requires_auth(
        self, client: AsyncClient
    ):
        """Test that testing profile requires authentication."""
        response = await client.post(
            "/api/v1/profiles/profile-id/test", json={}
        )
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_clone_profile_requires_auth(
        self, client: AsyncClient
    ):
        """Test that cloning profile requires authentication."""
        response = await client.post(
            "/api/v1/profiles/profile-id/clone", json={}
        )
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_profile_stats_requires_auth(
        self, client: AsyncClient
    ):
        """Test that getting profile stats requires authentication."""
        response = await client.get("/api/v1/profiles/stats/overview")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_available_providers_requires_auth(
        self, client: AsyncClient
    ):
        """Test that getting available providers requires authentication."""
        response = await client.get(
            "/api/v1/profiles/providers/available"
        )
        assert response.status_code == 401

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_create_profile_success(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test successful profile creation."""
        # Mock the profile service
        mock_service = AsyncMock()
        mock_profile = {
            "id": "profile-123",
            "name": "Test Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-4",
            "created_by": "testuser",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }
        mock_service.create_profile.return_value = mock_profile
        mock_get_service.return_value = mock_service

        profile_data = {
            "name": "Test Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-4",
            "description": "Test profile description",
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        response = await client.post(
            "/api/v1/profiles/", json=profile_data, headers=auth_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["id"] == "profile-123"
        assert data["name"] == "Test Profile"
        assert data["llm_provider"] == "openai"

    @pytest.mark.unit
    async def test_create_profile_invalid_data(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test profile creation with invalid data."""
        # Missing required fields
        profile_data = {
            "name": "Test Profile"
            # Missing llm_provider and llm_model
        }

        response = await client.post(
            "/api/v1/profiles/", json=profile_data, headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_unified_rate_limiter')
    async def test_create_profile_rate_limit(
        self,
        mock_get_rate_limiter,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test profile creation rate limiting."""
        from chatter.utils.unified_rate_limiter import RateLimitExceeded

        # Mock rate limiter to raise exception
        mock_rate_limiter = AsyncMock()
        mock_rate_limiter.check_rate_limit.side_effect = (
            RateLimitExceeded(
                message="Rate limit exceeded",
                limit=5,
                window=300,
                remaining=0,
            )
        )
        mock_get_rate_limiter.return_value = mock_rate_limiter

        profile_data = {
            "name": "Test Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-4",
        }

        response = await client.post(
            "/api/v1/profiles/", json=profile_data, headers=auth_headers
        )
        assert response.status_code == 429  # Rate limit exceeded

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_list_profiles_success(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test successful profile listing."""
        mock_service = AsyncMock()
        mock_profiles = [
            {
                "id": "profile-1",
                "name": "Profile 1",
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "created_at": "2024-01-01T12:00:00Z",
            },
            {
                "id": "profile-2",
                "name": "Profile 2",
                "llm_provider": "anthropic",
                "llm_model": "claude-3-opus",
                "created_at": "2024-01-01T13:00:00Z",
            },
        ]

        mock_service.list_profiles.return_value = {
            "profiles": mock_profiles,
            "total": 2,
            "page": 1,
            "per_page": 10,
        }
        mock_get_service.return_value = mock_service

        response = await client.get(
            "/api/v1/profiles", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["profiles"]) == 2
        assert data["total"] == 2

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_get_profile_success(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test successful profile retrieval."""
        mock_service = AsyncMock()
        mock_profile = {
            "id": "profile-123",
            "name": "Test Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000,
            "created_at": "2024-01-01T12:00:00Z",
        }

        mock_service.get_profile.return_value = mock_profile
        mock_get_service.return_value = mock_service

        response = await client.get(
            "/api/v1/profiles/profile-123", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "profile-123"
        assert data["name"] == "Test Profile"
        assert data["temperature"] == 0.7

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_get_profile_not_found(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test profile retrieval for non-existent profile."""
        mock_service = AsyncMock()
        mock_service.get_profile.side_effect = ProfileError(
            "Profile not found"
        )
        mock_get_service.return_value = mock_service

        response = await client.get(
            "/api/v1/profiles/nonexistent", headers=auth_headers
        )
        assert (
            response.status_code == 400
        )  # ProfileError maps to BadRequest

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_update_profile_success(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test successful profile update."""
        mock_service = AsyncMock()
        mock_updated_profile = {
            "id": "profile-123",
            "name": "Updated Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-4",
            "temperature": 0.8,
            "updated_at": "2024-01-01T13:00:00Z",
        }

        mock_service.update_profile.return_value = mock_updated_profile
        mock_get_service.return_value = mock_service

        update_data = {"name": "Updated Profile", "temperature": 0.8}

        response = await client.put(
            "/api/v1/profiles/profile-123",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Profile"
        assert data["temperature"] == 0.8

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_delete_profile_success(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test successful profile deletion."""
        mock_service = AsyncMock()
        mock_service.delete_profile.return_value = True
        mock_get_service.return_value = mock_service

        response = await client.delete(
            "/api/v1/profiles/profile-123", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["profile_id"] == "profile-123"

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_test_profile_success(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test successful profile testing."""
        mock_service = AsyncMock()
        mock_test_result = {
            "profile_id": "profile-123",
            "test_message": "Hello, World!",
            "response": "Hello! How can I assist you today?",
            "response_time": 1.25,
            "success": True,
        }

        mock_service.test_profile.return_value = mock_test_result
        mock_get_service.return_value = mock_service

        test_data = {
            "message": "Hello, World!",
            "include_metrics": True,
        }

        response = await client.post(
            "/api/v1/profiles/profile-123/test",
            json=test_data,
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["response_time"] == 1.25

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_clone_profile_success(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test successful profile cloning."""
        mock_service = AsyncMock()
        mock_cloned_profile = {
            "id": "cloned-profile-456",
            "name": "Cloned Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-4",
            "created_at": "2024-01-01T14:00:00Z",
        }

        mock_service.clone_profile.return_value = mock_cloned_profile
        mock_get_service.return_value = mock_service

        clone_data = {
            "name": "Cloned Profile",
            "include_settings": True,
        }

        response = await client.post(
            "/api/v1/profiles/profile-123/clone",
            json=clone_data,
            headers=auth_headers,
        )
        assert response.status_code == 201

        data = response.json()
        assert data["id"] == "cloned-profile-456"
        assert data["name"] == "Cloned Profile"

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_get_profile_stats_success(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test successful profile stats retrieval."""
        mock_service = AsyncMock()
        mock_stats = {
            "total_profiles": 25,
            "profiles_by_provider": {
                "openai": 15,
                "anthropic": 8,
                "google": 2,
            },
            "active_profiles": 20,
            "average_usage_per_profile": 45.5,
        }

        mock_service.get_profile_stats.return_value = mock_stats
        mock_get_service.return_value = mock_service

        response = await client.get(
            "/api/v1/profiles/stats/overview", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total_profiles"] == 25
        assert data["active_profiles"] == 20
        assert "profiles_by_provider" in data

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_get_available_providers_success(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test successful available providers retrieval."""
        mock_service = AsyncMock()
        mock_providers = {
            "openai": {
                "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
                "supports_streaming": True,
                "max_tokens": 4096,
            },
            "anthropic": {
                "models": [
                    "claude-3-opus",
                    "claude-3-sonnet",
                    "claude-3-haiku",
                ],
                "supports_streaming": True,
                "max_tokens": 8192,
            },
        }

        mock_service.get_available_providers.return_value = (
            mock_providers
        )
        mock_get_service.return_value = mock_service

        response = await client.get(
            "/api/v1/profiles/providers/available", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "openai" in data
        assert "anthropic" in data
        assert len(data["openai"]["models"]) == 3

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_profile_service_error_handling(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test profile service error handling."""
        mock_service = AsyncMock()
        mock_service.create_profile.side_effect = Exception(
            "Database error"
        )
        mock_get_service.return_value = mock_service

        profile_data = {
            "name": "Test Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-4",
        }

        response = await client.post(
            "/api/v1/profiles/", json=profile_data, headers=auth_headers
        )
        assert response.status_code == 500

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_profile_validation_errors(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test profile data validation errors."""
        # Test invalid provider
        invalid_profile_data = {
            "name": "Test Profile",
            "llm_provider": "invalid_provider",
            "llm_model": "gpt-4",
        }

        response = await client.post(
            "/api/v1/profiles/",
            json=invalid_profile_data,
            headers=auth_headers,
        )
        assert response.status_code == 422  # Validation error

        # Test invalid model for provider
        invalid_model_data = {
            "name": "Test Profile",
            "llm_provider": "openai",
            "llm_model": "invalid_model_12345",
        }

        response = await client.post(
            "/api/v1/profiles/",
            json=invalid_model_data,
            headers=auth_headers,
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_list_profiles_filtering(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test profile listing with filters."""
        mock_service = AsyncMock()
        mock_service.list_profiles.return_value = {
            "profiles": [],
            "total": 0,
            "page": 1,
            "per_page": 10,
        }
        mock_get_service.return_value = mock_service

        # Test with provider filter
        response = await client.get(
            "/api/v1/profiles?provider=openai", headers=auth_headers
        )
        assert response.status_code == 200

        # Verify filter was passed to service
        mock_service.list_profiles.assert_called()
        call_kwargs = mock_service.list_profiles.call_args[1]
        assert "provider" in call_kwargs

    @pytest.mark.unit
    @patch('chatter.api.profiles.get_profile_service')
    async def test_test_profile_rate_limit(
        self, mock_get_service, client: AsyncClient, auth_headers: dict
    ):
        """Test profile testing rate limiting."""
        # This would test rate limiting on profile testing if implemented
        mock_service = AsyncMock()
        mock_service.test_profile.return_value = {
            "success": True,
            "response": "Test response",
        }
        mock_get_service.return_value = mock_service

        test_data = {"message": "Test message"}

        response = await client.post(
            "/api/v1/profiles/profile-123/test",
            json=test_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
