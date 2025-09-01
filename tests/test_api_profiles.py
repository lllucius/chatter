"""Tests for profile management API endpoints."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from chatter.main import app
from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.models.profile import ProfileType
from chatter.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    ProfileCloneRequest,
    ProfileTestRequest,
    ProfileDeleteRequest,
)
from chatter.core.profiles import ProfileService, ProfileError
from chatter.utils.database import get_session


@pytest.mark.unit
class TestProfileEndpoints:
    """Test profile management API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True
        )
        
        self.mock_session = AsyncMock()
        
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
        app.dependency_overrides[get_session] = lambda: self.mock_session

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_create_profile_success(self):
        """Test successful profile creation."""
        # Arrange
        profile_data = {
            "name": "Test Profile",
            "description": "A test profile for API testing",
            "profile_type": "ai_assistant",
            "system_message": "You are a helpful assistant.",
            "temperature": 0.7,
            "max_tokens": 1000,
            "model_settings": {
                "provider": "openai",
                "model": "gpt-4"
            },
            "is_active": True,
            "is_public": False
        }
        
        mock_created_profile = {
            "id": "profile-123",
            "name": "Test Profile",
            "description": "A test profile for API testing",
            "profile_type": "ai_assistant",
            "system_message": "You are a helpful assistant.",
            "temperature": 0.7,
            "max_tokens": 1000,
            "model_settings": {
                "provider": "openai",
                "model": "gpt-4"
            },
            "is_active": True,
            "is_public": False,
            "user_id": self.mock_user.id,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(ProfileService, 'create_profile') as mock_create:
            mock_create.return_value = mock_created_profile
            
            # Act
            response = self.client.post("/profiles/", json=profile_data)
            
            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == "profile-123"
            assert data["name"] == "Test Profile"
            assert data["profile_type"] == "ai_assistant"
            assert data["user_id"] == self.mock_user.id
            mock_create.assert_called_once()

    def test_create_profile_validation_error(self):
        """Test profile creation with validation errors."""
        # Arrange
        invalid_profile_data = {
            "name": "",  # Empty name should fail validation
            "profile_type": "invalid_type",
            "temperature": 2.0  # Should be between 0 and 1
        }
        
        # Act
        response = self.client.post("/profiles/", json=invalid_profile_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_profiles_success(self):
        """Test successful profile listing."""
        # Arrange
        mock_profiles = [
            {
                "id": "profile-1",
                "name": "Profile 1",
                "description": "First test profile",
                "profile_type": "ai_assistant",
                "is_active": True,
                "is_public": False,
                "user_id": self.mock_user.id
            },
            {
                "id": "profile-2",
                "name": "Profile 2", 
                "description": "Second test profile",
                "profile_type": "workflow",
                "is_active": True,
                "is_public": True,
                "user_id": "other-user-id"
            }
        ]
        mock_total = 2
        
        with patch.object(ProfileService, 'list_profiles') as mock_list:
            mock_list.return_value = (mock_profiles, mock_total)
            
            # Act
            response = self.client.get("/profiles?page=1&per_page=10")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["profiles"]) == 2
            assert data["total"] == 2
            assert data["page"] == 1
            assert data["per_page"] == 10
            assert data["profiles"][0]["name"] == "Profile 1"

    def test_list_profiles_with_filters(self):
        """Test profile listing with filters."""
        # Arrange
        mock_profiles = [
            {
                "id": "profile-active",
                "name": "Active Profile",
                "profile_type": "ai_assistant",
                "is_active": True,
                "is_public": True
            }
        ]
        
        with patch.object(ProfileService, 'list_profiles') as mock_list:
            mock_list.return_value = (mock_profiles, 1)
            
            # Act
            response = self.client.get(
                "/profiles?profile_type=ai_assistant&is_active=true&is_public=true"
            )
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["profiles"]) == 1
            assert data["profiles"][0]["is_active"] is True
            assert data["profiles"][0]["is_public"] is True
            
            # Verify filters were passed to service
            call_args = mock_list.call_args
            args, kwargs = call_args
            # Check if filters were passed correctly

    def test_get_profile_success(self):
        """Test successful profile retrieval."""
        # Arrange
        profile_id = "profile-123"
        mock_profile = {
            "id": profile_id,
            "name": "Test Profile",
            "description": "A test profile",
            "profile_type": "ai_assistant",
            "system_message": "You are helpful.",
            "temperature": 0.7,
            "model_settings": {"provider": "openai"},
            "user_id": self.mock_user.id,
            "is_active": True
        }
        
        with patch.object(ProfileService, 'get_profile') as mock_get:
            mock_get.return_value = mock_profile
            
            # Act
            response = self.client.get(f"/profiles/{profile_id}")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == profile_id
            assert data["name"] == "Test Profile"
            assert data["temperature"] == 0.7

    def test_get_profile_not_found(self):
        """Test profile retrieval when profile doesn't exist."""
        # Arrange
        profile_id = "nonexistent-profile"
        
        with patch.object(ProfileService, 'get_profile') as mock_get:
            mock_get.side_effect = ProfileError("Profile not found")
            
            # Act
            response = self.client.get(f"/profiles/{profile_id}")
            
            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_profile_success(self):
        """Test successful profile update."""
        # Arrange
        profile_id = "profile-update-123"
        update_data = {
            "name": "Updated Profile",
            "description": "Updated description",
            "temperature": 0.8,
            "max_tokens": 2000,
            "is_active": False
        }
        
        mock_updated_profile = {
            "id": profile_id,
            "name": "Updated Profile",
            "description": "Updated description",
            "temperature": 0.8,
            "max_tokens": 2000,
            "is_active": False,
            "user_id": self.mock_user.id
        }
        
        with patch.object(ProfileService, 'update_profile') as mock_update:
            mock_update.return_value = mock_updated_profile
            
            # Act
            response = self.client.put(f"/profiles/{profile_id}", json=update_data)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Updated Profile"
            assert data["temperature"] == 0.8
            assert data["is_active"] is False

    def test_delete_profile_success(self):
        """Test successful profile deletion."""
        # Arrange
        profile_id = "profile-delete-123"
        delete_request = {
            "confirm_deletion": True,
            "delete_associated_data": False
        }
        
        with patch.object(ProfileService, 'delete_profile') as mock_delete:
            mock_delete.return_value = True
            
            # Act
            response = self.client.delete(f"/profiles/{profile_id}", json=delete_request)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted"] is True
            assert data["profile_id"] == profile_id

    def test_delete_profile_without_confirmation(self):
        """Test profile deletion without confirmation."""
        # Arrange
        profile_id = "profile-delete-456"
        delete_request = {
            "confirm_deletion": False
        }
        
        # Act
        response = self.client.delete(f"/profiles/{profile_id}", json=delete_request)
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "must confirm" in response.json()["detail"].lower()

    def test_test_profile_success(self):
        """Test successful profile testing."""
        # Arrange
        profile_id = "profile-test-123"
        test_request = {
            "test_input": "Hello, how are you?",
            "test_settings": {
                "temperature": 0.5,
                "max_tokens": 500
            }
        }
        
        mock_test_result = {
            "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
            "metadata": {
                "tokens_used": 25,
                "response_time": 1.2,
                "model_used": "gpt-4"
            },
            "success": True
        }
        
        with patch.object(ProfileService, 'test_profile') as mock_test:
            mock_test.return_value = mock_test_result
            
            # Act
            response = self.client.post(f"/profiles/{profile_id}/test", json=test_request)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert "response" in data
            assert data["metadata"]["tokens_used"] == 25

    def test_clone_profile_success(self):
        """Test successful profile cloning."""
        # Arrange
        profile_id = "profile-clone-123"
        clone_request = {
            "new_name": "Cloned Profile",
            "new_description": "A cloned profile",
            "copy_settings": True,
            "make_private": True
        }
        
        mock_cloned_profile = {
            "id": "profile-cloned-456",
            "name": "Cloned Profile",
            "description": "A cloned profile",
            "profile_type": "ai_assistant",
            "system_message": "You are helpful.",
            "is_public": False,
            "user_id": self.mock_user.id,
            "cloned_from": profile_id
        }
        
        with patch.object(ProfileService, 'clone_profile') as mock_clone:
            mock_clone.return_value = mock_cloned_profile
            
            # Act
            response = self.client.post(f"/profiles/{profile_id}/clone", json=clone_request)
            
            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == "profile-cloned-456"
            assert data["name"] == "Cloned Profile"
            assert data["is_public"] is False
            assert data["cloned_from"] == profile_id

    def test_get_profile_stats_success(self):
        """Test successful profile statistics retrieval."""
        # Arrange
        mock_stats = {
            "total_profiles": 15,
            "active_profiles": 12,
            "public_profiles": 8,
            "private_profiles": 7,
            "profiles_by_type": {
                "ai_assistant": 10,
                "workflow": 3,
                "custom": 2
            },
            "usage_stats": {
                "total_uses": 250,
                "avg_uses_per_profile": 16.7,
                "most_used_profile_id": "profile-popular-123"
            },
            "recent_activity": {
                "profiles_created_last_week": 3,
                "profiles_updated_last_week": 8
            }
        }
        
        with patch.object(ProfileService, 'get_profile_stats') as mock_stats_fn:
            mock_stats_fn.return_value = mock_stats
            
            # Act
            response = self.client.get("/profiles/stats/overview")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_profiles"] == 15
            assert data["active_profiles"] == 12
            assert data["profiles_by_type"]["ai_assistant"] == 10
            assert data["usage_stats"]["total_uses"] == 250

    def test_get_available_providers_success(self):
        """Test successful available providers retrieval."""
        # Arrange
        mock_providers = {
            "llm_providers": [
                {
                    "id": "openai",
                    "name": "OpenAI",
                    "models": ["gpt-4", "gpt-3.5-turbo"],
                    "is_available": True
                },
                {
                    "id": "anthropic",
                    "name": "Anthropic",
                    "models": ["claude-3-opus", "claude-3-sonnet"],
                    "is_available": True
                }
            ],
            "embedding_providers": [
                {
                    "id": "openai-embeddings",
                    "name": "OpenAI Embeddings",
                    "models": ["text-embedding-ada-002"],
                    "is_available": True
                }
            ],
            "tool_providers": [
                {
                    "id": "local-tools",
                    "name": "Local Tools",
                    "tools": ["calculator", "web_search"],
                    "is_available": True
                }
            ]
        }
        
        with patch.object(ProfileService, 'get_available_providers') as mock_providers_fn:
            mock_providers_fn.return_value = mock_providers
            
            # Act
            response = self.client.get("/profiles/providers/available")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["llm_providers"]) == 2
            assert len(data["embedding_providers"]) == 1
            assert data["llm_providers"][0]["name"] == "OpenAI"
            assert "gpt-4" in data["llm_providers"][0]["models"]


@pytest.mark.unit
class TestProfileValidation:
    """Test profile validation logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True
        )
        
        self.mock_session = AsyncMock()
        
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
        app.dependency_overrides[get_session] = lambda: self.mock_session

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_create_profile_invalid_temperature(self):
        """Test profile creation with invalid temperature."""
        # Arrange
        profile_data = {
            "name": "Invalid Temp Profile",
            "profile_type": "ai_assistant",
            "temperature": 2.5  # Should be between 0 and 1
        }
        
        # Act
        response = self.client.post("/profiles/", json=profile_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        temp_error = next((e for e in errors if "temperature" in e["loc"]), None)
        assert temp_error is not None

    def test_create_profile_invalid_max_tokens(self):
        """Test profile creation with invalid max_tokens."""
        # Arrange
        profile_data = {
            "name": "Invalid Tokens Profile",
            "profile_type": "ai_assistant",
            "max_tokens": -1  # Should be positive
        }
        
        # Act
        response = self.client.post("/profiles/", json=profile_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_profile_missing_required_fields(self):
        """Test profile creation missing required fields."""
        # Arrange
        profile_data = {
            # Missing name and profile_type
            "description": "Missing required fields"
        }
        
        # Act
        response = self.client.post("/profiles/", json=profile_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert len(errors) >= 2  # At least name and profile_type errors


@pytest.mark.integration
class TestProfileIntegration:
    """Integration tests for profile workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="integration-user-id",
            email="integration@example.com",
            username="integrationuser",
            is_active=True
        )
        
        self.mock_session = AsyncMock()
        
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
        app.dependency_overrides[get_session] = lambda: self.mock_session

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_profile_lifecycle_workflow(self):
        """Test complete profile lifecycle: create, update, test, clone, delete."""
        # Step 1: Create profile
        profile_data = {
            "name": "Lifecycle Test Profile",
            "description": "Testing profile lifecycle",
            "profile_type": "ai_assistant",
            "system_message": "You are a test assistant.",
            "temperature": 0.7
        }
        
        mock_created_profile = {
            "id": "lifecycle-profile-123",
            "name": "Lifecycle Test Profile",
            "description": "Testing profile lifecycle",
            "user_id": self.mock_user.id
        }
        
        with patch.object(ProfileService, 'create_profile') as mock_create:
            mock_create.return_value = mock_created_profile
            
            create_response = self.client.post("/profiles/", json=profile_data)
            assert create_response.status_code == status.HTTP_201_CREATED
            profile_id = create_response.json()["id"]
        
        # Step 2: Update profile
        update_data = {
            "name": "Updated Lifecycle Profile",
            "temperature": 0.8
        }
        
        mock_updated_profile = {
            "id": profile_id,
            "name": "Updated Lifecycle Profile",
            "temperature": 0.8
        }
        
        with patch.object(ProfileService, 'update_profile') as mock_update:
            mock_update.return_value = mock_updated_profile
            
            update_response = self.client.put(f"/profiles/{profile_id}", json=update_data)
            assert update_response.status_code == status.HTTP_200_OK
            assert update_response.json()["name"] == "Updated Lifecycle Profile"
        
        # Step 3: Test profile
        test_request = {
            "test_input": "Hello, test",
            "test_settings": {"temperature": 0.5}
        }
        
        mock_test_result = {
            "response": "Hello! This is a test response.",
            "success": True,
            "metadata": {"tokens_used": 10}
        }
        
        with patch.object(ProfileService, 'test_profile') as mock_test:
            mock_test.return_value = mock_test_result
            
            test_response = self.client.post(f"/profiles/{profile_id}/test", json=test_request)
            assert test_response.status_code == status.HTTP_200_OK
            assert test_response.json()["success"] is True
        
        # Step 4: Clone profile
        clone_request = {
            "new_name": "Cloned Lifecycle Profile",
            "copy_settings": True
        }
        
        mock_cloned_profile = {
            "id": "cloned-profile-456",
            "name": "Cloned Lifecycle Profile",
            "cloned_from": profile_id
        }
        
        with patch.object(ProfileService, 'clone_profile') as mock_clone:
            mock_clone.return_value = mock_cloned_profile
            
            clone_response = self.client.post(f"/profiles/{profile_id}/clone", json=clone_request)
            assert clone_response.status_code == status.HTTP_201_CREATED
            cloned_id = clone_response.json()["id"]
        
        # Step 5: Delete profiles
        delete_request = {
            "confirm_deletion": True
        }
        
        with patch.object(ProfileService, 'delete_profile') as mock_delete:
            mock_delete.return_value = True
            
            # Delete original
            delete_response = self.client.delete(f"/profiles/{profile_id}", json=delete_request)
            assert delete_response.status_code == status.HTTP_200_OK
            
            # Delete cloned
            delete_clone_response = self.client.delete(f"/profiles/{cloned_id}", json=delete_request)
            assert delete_clone_response.status_code == status.HTTP_200_OK

    def test_profile_sharing_workflow(self):
        """Test profile sharing and public access workflow."""
        # Step 1: Create private profile
        private_profile_data = {
            "name": "Private Profile",
            "profile_type": "ai_assistant",
            "is_public": False
        }
        
        mock_private_profile = {
            "id": "private-profile-123",
            "name": "Private Profile",
            "is_public": False,
            "user_id": self.mock_user.id
        }
        
        with patch.object(ProfileService, 'create_profile') as mock_create:
            mock_create.return_value = mock_private_profile
            
            create_response = self.client.post("/profiles/", json=private_profile_data)
            profile_id = create_response.json()["id"]
        
        # Step 2: Make profile public
        update_data = {
            "is_public": True
        }
        
        mock_public_profile = {
            "id": profile_id,
            "name": "Private Profile",
            "is_public": True
        }
        
        with patch.object(ProfileService, 'update_profile') as mock_update:
            mock_update.return_value = mock_public_profile
            
            update_response = self.client.put(f"/profiles/{profile_id}", json=update_data)
            assert update_response.status_code == status.HTTP_200_OK
            assert update_response.json()["is_public"] is True
        
        # Step 3: List public profiles (should include our profile)
        mock_public_profiles = [mock_public_profile]
        
        with patch.object(ProfileService, 'list_profiles') as mock_list:
            mock_list.return_value = (mock_public_profiles, 1)
            
            list_response = self.client.get("/profiles?is_public=true")
            assert list_response.status_code == status.HTTP_200_OK
            profiles = list_response.json()["profiles"]
            assert len(profiles) == 1
            assert profiles[0]["is_public"] is True

    def test_profile_stats_integration(self):
        """Test profile statistics integration."""
        # Create multiple profiles and check stats
        
        # Mock multiple profiles creation
        profiles_data = [
            {"name": "Profile 1", "profile_type": "ai_assistant"},
            {"name": "Profile 2", "profile_type": "workflow"},
            {"name": "Profile 3", "profile_type": "ai_assistant"}
        ]
        
        for i, profile_data in enumerate(profiles_data):
            mock_profile = {
                "id": f"stats-profile-{i+1}",
                "name": profile_data["name"],
                "profile_type": profile_data["profile_type"]
            }
            
            with patch.object(ProfileService, 'create_profile') as mock_create:
                mock_create.return_value = mock_profile
                
                response = self.client.post("/profiles/", json=profile_data)
                assert response.status_code == status.HTTP_201_CREATED
        
        # Check updated stats
        mock_stats = {
            "total_profiles": 3,
            "active_profiles": 3,
            "profiles_by_type": {
                "ai_assistant": 2,
                "workflow": 1
            }
        }
        
        with patch.object(ProfileService, 'get_profile_stats') as mock_stats_fn:
            mock_stats_fn.return_value = mock_stats
            
            stats_response = self.client.get("/profiles/stats/overview")
            assert stats_response.status_code == status.HTTP_200_OK
            data = stats_response.json()
            assert data["total_profiles"] == 3
            assert data["profiles_by_type"]["ai_assistant"] == 2