"""Tests for prompt management API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.api.auth import get_current_user
from chatter.core.prompts import PromptError, PromptService
from chatter.main import app
from chatter.models.user import User
from chatter.utils.database import get_session_generator


@pytest.mark.unit
class TestPromptEndpoints:
    """Test prompt management API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True,
        )

        self.mock_session = AsyncMock()

        # Override dependencies
        app.dependency_overrides[get_current_user] = (
            lambda: self.mock_user
        )
        app.dependency_overrides[get_session] = (
            lambda: self.mock_session
        )

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_create_prompt_success(self):
        """Test successful prompt creation."""
        # Arrange
        prompt_data = {
            "name": "Test Prompt",
            "description": "A test prompt for API testing",
            "content": "You are a helpful assistant. User query: {user_input}",
            "prompt_type": "system_message",
            "category": "general",
            "variables": ["user_input"],
            "tags": ["test", "api"],
            "is_active": True,
            "is_public": False,
            "version": "1.0.0",
        }

        mock_created_prompt = {
            "id": "prompt-123",
            "name": "Test Prompt",
            "description": "A test prompt for API testing",
            "content": "You are a helpful assistant. User query: {user_input}",
            "prompt_type": "system_message",
            "category": "general",
            "variables": ["user_input"],
            "tags": ["test", "api"],
            "is_active": True,
            "is_public": False,
            "version": "1.0.0",
            "user_id": self.mock_user.id,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        with patch.object(
            PromptService, 'create_prompt'
        ) as mock_create:
            mock_create.return_value = mock_created_prompt

            # Act
            response = self.client.post("/prompts/", json=prompt_data)

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == "prompt-123"
            assert data["name"] == "Test Prompt"
            assert data["prompt_type"] == "system_message"
            assert data["user_id"] == self.mock_user.id
            assert "user_input" in data["variables"]
            mock_create.assert_called_once()

    def test_create_prompt_validation_error(self):
        """Test prompt creation with validation errors."""
        # Arrange
        invalid_prompt_data = {
            "name": "",  # Empty name should fail validation
            "content": "",  # Empty content should fail validation
            "prompt_type": "invalid_type",
            "category": "invalid_category",
        }

        # Act
        response = self.client.post(
            "/prompts/", json=invalid_prompt_data
        )

        # Assert
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    def test_list_prompts_success(self):
        """Test successful prompt listing."""
        # Arrange
        mock_prompts = [
            {
                "id": "prompt-1",
                "name": "Prompt 1",
                "description": "First test prompt",
                "content": "You are helpful.",
                "prompt_type": "system_message",
                "category": "general",
                "is_active": True,
                "is_public": False,
                "user_id": self.mock_user.id,
                "tags": ["test"],
            },
            {
                "id": "prompt-2",
                "name": "Prompt 2",
                "description": "Second test prompt",
                "content": "Answer briefly: {question}",
                "prompt_type": "user_message",
                "category": "qa",
                "is_active": True,
                "is_public": True,
                "user_id": "other-user-id",
                "tags": ["qa", "brief"],
                "variables": ["question"],
            },
        ]
        mock_total = 2

        with patch.object(PromptService, 'list_prompts') as mock_list:
            mock_list.return_value = (mock_prompts, mock_total)

            # Act
            response = self.client.get("/prompts?page=1&per_page=10")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["prompts"]) == 2
            assert data["total"] == 2
            assert data["page"] == 1
            assert data["per_page"] == 10
            assert data["prompts"][0]["name"] == "Prompt 1"
            assert len(data["prompts"][1]["variables"]) == 1

    def test_list_prompts_with_filters(self):
        """Test prompt listing with filters."""
        # Arrange
        mock_prompts = [
            {
                "id": "prompt-qa",
                "name": "QA Prompt",
                "prompt_type": "user_message",
                "category": "qa",
                "is_active": True,
                "is_public": True,
                "tags": ["qa"],
            }
        ]

        with patch.object(PromptService, 'list_prompts') as mock_list:
            mock_list.return_value = (mock_prompts, 1)

            # Act
            response = self.client.get(
                "/prompts?prompt_type=user_message&category=qa&is_active=true&is_public=true&tag=qa"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["prompts"]) == 1
            assert data["prompts"][0]["category"] == "qa"
            assert data["prompts"][0]["is_active"] is True
            assert data["prompts"][0]["is_public"] is True

    def test_get_prompt_success(self):
        """Test successful prompt retrieval."""
        # Arrange
        prompt_id = "prompt-123"
        mock_prompt = {
            "id": prompt_id,
            "name": "Test Prompt",
            "description": "A test prompt",
            "content": "You are helpful. Question: {question}",
            "prompt_type": "system_message",
            "category": "general",
            "variables": ["question"],
            "tags": ["test", "helpful"],
            "user_id": self.mock_user.id,
            "is_active": True,
            "version": "1.0.0",
        }

        with patch.object(PromptService, 'get_prompt') as mock_get:
            mock_get.return_value = mock_prompt

            # Act
            response = self.client.get(f"/prompts/{prompt_id}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == prompt_id
            assert data["name"] == "Test Prompt"
            assert "question" in data["variables"]
            assert "test" in data["tags"]

    def test_get_prompt_not_found(self):
        """Test prompt retrieval when prompt doesn't exist."""
        # Arrange
        prompt_id = "nonexistent-prompt"

        with patch.object(PromptService, 'get_prompt') as mock_get:
            mock_get.side_effect = PromptError("Prompt not found")

            # Act
            response = self.client.get(f"/prompts/{prompt_id}")

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_prompt_success(self):
        """Test successful prompt update."""
        # Arrange
        prompt_id = "prompt-update-123"
        update_data = {
            "name": "Updated Prompt",
            "description": "Updated description",
            "content": "Updated content with {new_variable}",
            "variables": ["new_variable"],
            "tags": ["updated", "test"],
            "is_active": False,
            "version": "1.1.0",
        }

        mock_updated_prompt = {
            "id": prompt_id,
            "name": "Updated Prompt",
            "description": "Updated description",
            "content": "Updated content with {new_variable}",
            "variables": ["new_variable"],
            "tags": ["updated", "test"],
            "is_active": False,
            "version": "1.1.0",
            "user_id": self.mock_user.id,
        }

        with patch.object(
            PromptService, 'update_prompt'
        ) as mock_update:
            mock_update.return_value = mock_updated_prompt

            # Act
            response = self.client.put(
                f"/prompts/{prompt_id}", json=update_data
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Updated Prompt"
            assert data["version"] == "1.1.0"
            assert data["is_active"] is False
            assert "new_variable" in data["variables"]

    def test_delete_prompt_success(self):
        """Test successful prompt deletion."""
        # Arrange
        prompt_id = "prompt-delete-123"
        delete_request = {
            "confirm_deletion": True,
            "delete_versions": False,
        }

        with patch.object(
            PromptService, 'delete_prompt'
        ) as mock_delete:
            mock_delete.return_value = True

            # Act
            response = self.client.delete(
                f"/prompts/{prompt_id}", json=delete_request
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted"] is True
            assert data["prompt_id"] == prompt_id

    def test_delete_prompt_without_confirmation(self):
        """Test prompt deletion without confirmation."""
        # Arrange
        prompt_id = "prompt-delete-456"
        delete_request = {"confirm_deletion": False}

        # Act
        response = self.client.delete(
            f"/prompts/{prompt_id}", json=delete_request
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "must confirm" in response.json()["detail"].lower()

    def test_test_prompt_success(self):
        """Test successful prompt testing."""
        # Arrange
        prompt_id = "prompt-test-123"
        test_request = {
            "variables": {
                "user_input": "What is the weather like?",
                "context": "sunny day",
            },
            "test_settings": {"temperature": 0.5, "max_tokens": 100},
        }

        mock_test_result = {
            "rendered_prompt": "You are helpful. User says: What is the weather like? Context: sunny day",
            "response": "It's a beautiful sunny day! Perfect weather for outdoor activities.",
            "metadata": {
                "tokens_used": 18,
                "response_time": 0.8,
                "model_used": "gpt-3.5-turbo",
                "variables_resolved": {
                    "user_input": "What is the weather like?",
                    "context": "sunny day",
                },
            },
            "success": True,
            "validation_errors": [],
        }

        with patch.object(PromptService, 'test_prompt') as mock_test:
            mock_test.return_value = mock_test_result

            # Act
            response = self.client.post(
                f"/prompts/{prompt_id}/test", json=test_request
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert "rendered_prompt" in data
            assert data["metadata"]["tokens_used"] == 18
            assert len(data["validation_errors"]) == 0

    def test_test_prompt_with_validation_errors(self):
        """Test prompt testing with validation errors."""
        # Arrange
        prompt_id = "prompt-test-invalid"
        test_request = {
            "variables": {
                "missing_required_var": "value"
                # Missing other required variables
            }
        }

        mock_test_result = {
            "rendered_prompt": None,
            "response": None,
            "success": False,
            "validation_errors": [
                "Required variable 'user_input' not provided",
                "Variable 'context' is missing",
            ],
            "metadata": {},
        }

        with patch.object(PromptService, 'test_prompt') as mock_test:
            mock_test.return_value = mock_test_result

            # Act
            response = self.client.post(
                f"/prompts/{prompt_id}/test", json=test_request
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is False
            assert len(data["validation_errors"]) > 0
            assert "user_input" in data["validation_errors"][0]

    def test_clone_prompt_success(self):
        """Test successful prompt cloning."""
        # Arrange
        prompt_id = "prompt-clone-123"
        clone_request = {
            "new_name": "Cloned Prompt",
            "new_description": "A cloned prompt",
            "copy_tags": True,
            "make_private": True,
            "new_version": "1.0.0-clone",
        }

        mock_cloned_prompt = {
            "id": "prompt-cloned-456",
            "name": "Cloned Prompt",
            "description": "A cloned prompt",
            "content": "Original content",
            "prompt_type": "system_message",
            "category": "general",
            "tags": ["original", "cloned"],
            "is_public": False,
            "version": "1.0.0-clone",
            "user_id": self.mock_user.id,
            "cloned_from": prompt_id,
            "variables": ["user_input"],
        }

        with patch.object(PromptService, 'clone_prompt') as mock_clone:
            mock_clone.return_value = mock_cloned_prompt

            # Act
            response = self.client.post(
                f"/prompts/{prompt_id}/clone", json=clone_request
            )

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == "prompt-cloned-456"
            assert data["name"] == "Cloned Prompt"
            assert data["is_public"] is False
            assert data["version"] == "1.0.0-clone"
            assert data["cloned_from"] == prompt_id

    def test_get_prompt_stats_success(self):
        """Test successful prompt statistics retrieval."""
        # Arrange
        mock_stats = {
            "total_prompts": 25,
            "active_prompts": 20,
            "public_prompts": 15,
            "private_prompts": 10,
            "prompts_by_type": {
                "system_message": 12,
                "user_message": 8,
                "assistant_message": 3,
                "function_call": 2,
            },
            "prompts_by_category": {
                "general": 8,
                "qa": 6,
                "creative": 4,
                "technical": 4,
                "custom": 3,
            },
            "usage_stats": {
                "total_uses": 500,
                "avg_uses_per_prompt": 20.0,
                "most_used_prompt_id": "prompt-popular-123",
            },
            "tag_stats": {
                "most_common_tags": [
                    {"tag": "helpful", "count": 10},
                    {"tag": "qa", "count": 8},
                    {"tag": "creative", "count": 6},
                ]
            },
            "recent_activity": {
                "prompts_created_last_week": 5,
                "prompts_updated_last_week": 12,
                "prompts_tested_last_week": 35,
            },
        }

        with patch.object(
            PromptService, 'get_prompt_stats'
        ) as mock_stats_fn:
            mock_stats_fn.return_value = mock_stats

            # Act
            response = self.client.get("/prompts/stats/overview")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_prompts"] == 25
            assert data["active_prompts"] == 20
            assert data["prompts_by_type"]["system_message"] == 12
            assert data["prompts_by_category"]["general"] == 8
            assert data["usage_stats"]["total_uses"] == 500
            assert len(data["tag_stats"]["most_common_tags"]) == 3


@pytest.mark.unit
class TestPromptValidation:
    """Test prompt validation logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True,
        )

        self.mock_session = AsyncMock()

        app.dependency_overrides[get_current_user] = (
            lambda: self.mock_user
        )
        app.dependency_overrides[get_session] = (
            lambda: self.mock_session
        )

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_create_prompt_invalid_variables(self):
        """Test prompt creation with invalid variable format."""
        # Arrange
        prompt_data = {
            "name": "Invalid Variables Prompt",
            "content": "Hello {invalid variable name}",  # Spaces in variable names
            "prompt_type": "system_message",
            "variables": [
                "invalid variable name"
            ],  # Should not contain spaces
        }

        # Act
        response = self.client.post("/prompts/", json=prompt_data)

        # Assert
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    def test_create_prompt_mismatched_variables(self):
        """Test prompt creation where variables don't match content placeholders."""
        # Arrange
        prompt_data = {
            "name": "Mismatched Variables Prompt",
            "content": "Hello {name}, how is {weather}?",
            "prompt_type": "user_message",
            "variables": [
                "name",
                "location",
            ],  # 'weather' missing, 'location' extra
        }

        # This might be caught by service validation rather than request validation
        with patch.object(
            PromptService, 'create_prompt'
        ) as mock_create:
            mock_create.side_effect = PromptError(
                "Variables mismatch with content placeholders"
            )

            # Act
            response = self.client.post("/prompts/", json=prompt_data)

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_prompt_empty_content(self):
        """Test prompt creation with empty content."""
        # Arrange
        prompt_data = {
            "name": "Empty Content Prompt",
            "content": "",  # Empty content
            "prompt_type": "system_message",
        }

        # Act
        response = self.client.post("/prompts/", json=prompt_data)

        # Assert
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    def test_create_prompt_invalid_version_format(self):
        """Test prompt creation with invalid version format."""
        # Arrange
        prompt_data = {
            "name": "Invalid Version Prompt",
            "content": "Hello world",
            "prompt_type": "system_message",
            "version": "not-a-version",  # Invalid semantic version
        }

        # Act
        response = self.client.post("/prompts/", json=prompt_data)

        # Assert
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )


@pytest.mark.integration
class TestPromptIntegration:
    """Integration tests for prompt workflows using real database."""

    @pytest.mark.asyncio
    async def test_prompt_lifecycle_workflow(self, test_db_session):
        """Test complete prompt lifecycle: create, update with real database."""
        from chatter.core.prompts import PromptService
        from chatter.models.user import User
        from chatter.models.prompt import Prompt
        from chatter.schemas.prompt import PromptCreate, PromptUpdate
        from sqlalchemy import select
        
        # Create a real test user in the database
        test_user = User(
            email="integration@example.com",
            username="integrationuser",
            hashed_password="hashed_password_here",
            full_name="Integration Test User",
            is_active=True,
        )
        
        test_db_session.add(test_user)
        await test_db_session.commit()
        await test_db_session.refresh(test_user)

        # Create prompt service with real database session
        prompt_service = PromptService(test_db_session)

        # Step 1: Create prompt using real database service
        prompt_data = PromptCreate(
            name="Lifecycle Test Prompt",
            description="Testing prompt lifecycle",
            content="You are {role}. Answer this: {question}",
            prompt_type="system",
            category="general",
            variables=["role", "question"],
            tags=["test", "lifecycle"],
        )

        created_prompt = await prompt_service.create_prompt(test_user.id, prompt_data)
        assert created_prompt.id is not None
        assert created_prompt.name == "Lifecycle Test Prompt"
        assert created_prompt.owner_id == test_user.id
        
        # Verify prompt was actually created in database
        result = await test_db_session.execute(
            select(Prompt).where(Prompt.id == created_prompt.id)
        )
        db_prompt = result.scalar_one_or_none()
        assert db_prompt is not None
        assert db_prompt.name == "Lifecycle Test Prompt"

        # Step 2: Update prompt
        update_data = PromptUpdate(
            name="Updated Lifecycle Prompt",
            content="You are {role}. Please answer: {question} with {style}",
            variables=["role", "question", "style"],
        )

        updated_prompt = await prompt_service.update_prompt(created_prompt.id, test_user.id, update_data)
        assert updated_prompt.name == "Updated Lifecycle Prompt"
        assert len(updated_prompt.variables) == 3
        
        # Verify update in database
        await test_db_session.refresh(db_prompt)
        assert db_prompt.name == "Updated Lifecycle Prompt"
        assert len(db_prompt.variables) == 3

        # Step 3: Test reading prompt back
        retrieved_prompt = await prompt_service.get_prompt(created_prompt.id, test_user.id)
        assert retrieved_prompt is not None
        assert retrieved_prompt.name == "Updated Lifecycle Prompt"
        assert len(retrieved_prompt.variables) == 3
