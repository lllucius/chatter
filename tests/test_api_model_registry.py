"""Tests for model registry API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.api.auth import get_current_user
from chatter.core.model_registry import ModelRegistryService
from chatter.main import app
from chatter.models.registry import ModelType
from chatter.models.user import User
from chatter.utils.database import get_session


@pytest.mark.unit
class TestProviderEndpoints:
    """Test provider management API endpoints."""

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

    def test_list_providers_success(self):
        """Test successful provider listing."""
        # Arrange
        mock_providers = [
            {
                "id": "provider-1",
                "name": "OpenAI",
                "provider_type": "llm",
                "is_active": True,
                "config": {"api_base": "https://api.openai.com/v1"}
            },
            {
                "id": "provider-2",
                "name": "Anthropic",
                "provider_type": "llm",
                "is_active": True,
                "config": {"api_base": "https://api.anthropic.com"}
            }
        ]
        mock_total = 2

        with patch.object(ModelRegistryService, 'list_providers') as mock_list:
            mock_list.return_value = (mock_providers, mock_total)

            # Act
            response = self.client.get("/registry/providers?page=1&per_page=20")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["providers"]) == 2
            assert data["total"] == 2
            assert data["page"] == 1
            assert data["per_page"] == 20
            assert data["providers"][0]["name"] == "OpenAI"

    def test_list_providers_with_filters(self):
        """Test provider listing with active filter."""
        # Arrange
        mock_providers = [
            {
                "id": "provider-active",
                "name": "Active Provider",
                "provider_type": "llm",
                "is_active": True
            }
        ]

        with patch.object(ModelRegistryService, 'list_providers') as mock_list:
            mock_list.return_value = (mock_providers, 1)

            # Act
            response = self.client.get("/registry/providers?active_only=true")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["providers"]) == 1
            assert data["providers"][0]["is_active"] is True

    def test_get_provider_success(self):
        """Test successful provider retrieval."""
        # Arrange
        provider_id = "provider-123"
        mock_provider = {
            "id": provider_id,
            "name": "Test Provider",
            "provider_type": "llm",
            "is_active": True,
            "config": {"api_key": "***"}
        }

        with patch.object(ModelRegistryService, 'get_provider') as mock_get:
            mock_get.return_value = mock_provider

            # Act
            response = self.client.get(f"/registry/providers/{provider_id}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == provider_id
            assert data["name"] == "Test Provider"

    def test_get_provider_not_found(self):
        """Test provider retrieval when provider doesn't exist."""
        # Arrange
        provider_id = "nonexistent-provider"

        with patch.object(ModelRegistryService, 'get_provider') as mock_get:
            mock_get.return_value = None

            # Act
            response = self.client.get(f"/registry/providers/{provider_id}")

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Provider not found" in response.json()["detail"]

    def test_create_provider_success(self):
        """Test successful provider creation."""
        # Arrange
        provider_data = {
            "name": "New Provider",
            "provider_type": "llm",
            "description": "A test provider",
            "config": {"api_base": "https://api.example.com"},
            "is_active": True
        }

        mock_created_provider = {
            "id": "new-provider-123",
            "name": "New Provider",
            "provider_type": "llm",
            "description": "A test provider",
            "is_active": True,
            "config": {"api_base": "https://api.example.com"}
        }

        with patch.object(ModelRegistryService, 'get_provider_by_name') as mock_check:
            mock_check.return_value = None  # No existing provider

            with patch.object(ModelRegistryService, 'create_provider') as mock_create:
                mock_create.return_value = mock_created_provider

                # Act
                response = self.client.post("/registry/providers", json=provider_data)

                # Assert
                assert response.status_code == status.HTTP_201_CREATED
                data = response.json()
                assert data["id"] == "new-provider-123"
                assert data["name"] == "New Provider"
                mock_create.assert_called_once()

    def test_create_provider_duplicate_name(self):
        """Test provider creation with duplicate name."""
        # Arrange
        provider_data = {
            "name": "Existing Provider",
            "provider_type": "llm"
        }

        mock_existing_provider = {
            "id": "existing-provider",
            "name": "Existing Provider"
        }

        with patch.object(ModelRegistryService, 'get_provider_by_name') as mock_check:
            mock_check.return_value = mock_existing_provider

            # Act
            response = self.client.post("/registry/providers", json=provider_data)

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "already exists" in response.json()["detail"]

    def test_update_provider_success(self):
        """Test successful provider update."""
        # Arrange
        provider_id = "provider-update-123"
        update_data = {
            "name": "Updated Provider",
            "description": "Updated description",
            "is_active": False
        }

        mock_updated_provider = {
            "id": provider_id,
            "name": "Updated Provider",
            "description": "Updated description",
            "is_active": False
        }

        with patch.object(ModelRegistryService, 'update_provider') as mock_update:
            mock_update.return_value = mock_updated_provider

            # Act
            response = self.client.put(f"/registry/providers/{provider_id}", json=update_data)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Updated Provider"
            assert data["is_active"] is False

    def test_delete_provider_success(self):
        """Test successful provider deletion."""
        # Arrange
        provider_id = "provider-delete-123"

        with patch.object(ModelRegistryService, 'delete_provider') as mock_delete:
            mock_delete.return_value = True

            # Act
            response = self.client.delete(f"/registry/providers/{provider_id}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted"] is True
            assert data["provider_id"] == provider_id

    def test_set_default_provider_success(self):
        """Test successful default provider setting."""
        # Arrange
        provider_id = "provider-default-123"
        model_type = ModelType.CHAT

        with patch.object(ModelRegistryService, 'set_default_provider') as mock_set:
            mock_set.return_value = True

            # Act
            response = self.client.post(
                f"/registry/providers/{provider_id}/set-default",
                json={"model_type": model_type.value}
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["is_default"] is True
            assert data["provider_id"] == provider_id


@pytest.mark.unit
class TestModelEndpoints:
    """Test model definition API endpoints."""

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

    def test_list_models_success(self):
        """Test successful model listing."""
        # Arrange
        mock_models = [
            {
                "id": "model-1",
                "name": "gpt-4",
                "model_type": "chat",
                "provider_id": "openai-provider",
                "is_active": True,
                "config": {"max_tokens": 4096}
            },
            {
                "id": "model-2",
                "name": "claude-3",
                "model_type": "chat",
                "provider_id": "anthropic-provider",
                "is_active": True,
                "config": {"max_tokens": 8192}
            }
        ]
        mock_total = 2

        with patch.object(ModelRegistryService, 'list_models') as mock_list:
            mock_list.return_value = (mock_models, mock_total)

            # Act
            response = self.client.get("/registry/models")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["models"]) == 2
            assert data["total"] == 2
            assert data["models"][0]["name"] == "gpt-4"

    def test_get_model_success(self):
        """Test successful model retrieval."""
        # Arrange
        model_id = "model-123"
        mock_model = {
            "id": model_id,
            "name": "test-model",
            "model_type": "chat",
            "provider": {
                "id": "provider-123",
                "name": "Test Provider"
            },
            "config": {"temperature": 0.7}
        }

        with patch.object(ModelRegistryService, 'get_model_with_provider') as mock_get:
            mock_get.return_value = mock_model

            # Act
            response = self.client.get(f"/registry/models/{model_id}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == model_id
            assert data["name"] == "test-model"
            assert data["provider"]["name"] == "Test Provider"

    def test_create_model_success(self):
        """Test successful model creation."""
        # Arrange
        model_data = {
            "name": "new-model",
            "model_type": "chat",
            "provider_id": "provider-123",
            "description": "A new test model",
            "config": {"max_tokens": 2048},
            "is_active": True
        }

        mock_created_model = {
            "id": "new-model-123",
            "name": "new-model",
            "model_type": "chat",
            "provider_id": "provider-123",
            "description": "A new test model",
            "config": {"max_tokens": 2048},
            "is_active": True
        }

        with patch.object(ModelRegistryService, 'get_provider') as mock_check_provider:
            mock_check_provider.return_value = {"id": "provider-123", "name": "Test Provider"}

            with patch.object(ModelRegistryService, 'get_model_by_name_and_provider') as mock_check:
                mock_check.return_value = None

                with patch.object(ModelRegistryService, 'create_model') as mock_create:
                    mock_create.return_value = mock_created_model

                    # Act
                    response = self.client.post("/registry/models", json=model_data)

                    # Assert
                    assert response.status_code == status.HTTP_201_CREATED
                    data = response.json()
                    assert data["id"] == "new-model-123"
                    assert data["name"] == "new-model"

    def test_update_model_success(self):
        """Test successful model update."""
        # Arrange
        model_id = "model-update-123"
        update_data = {
            "name": "updated-model",
            "description": "Updated description",
            "config": {"max_tokens": 4096}
        }

        mock_updated_model = {
            "id": model_id,
            "name": "updated-model",
            "description": "Updated description",
            "config": {"max_tokens": 4096}
        }

        with patch.object(ModelRegistryService, 'update_model') as mock_update:
            mock_update.return_value = mock_updated_model

            # Act
            response = self.client.put(f"/registry/models/{model_id}", json=update_data)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "updated-model"
            assert data["config"]["max_tokens"] == 4096

    def test_delete_model_success(self):
        """Test successful model deletion."""
        # Arrange
        model_id = "model-delete-123"

        with patch.object(ModelRegistryService, 'delete_model') as mock_delete:
            mock_delete.return_value = True

            # Act
            response = self.client.delete(f"/registry/models/{model_id}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted"] is True
            assert data["model_id"] == model_id


@pytest.mark.unit
class TestEmbeddingSpaceEndpoints:
    """Test embedding space API endpoints."""

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

    def test_list_embedding_spaces_success(self):
        """Test successful embedding space listing."""
        # Arrange
        mock_spaces = [
            {
                "id": "space-1",
                "name": "openai-embeddings",
                "description": "OpenAI embedding space",
                "dimension": 1536,
                "model_id": "embedding-model-1",
                "is_active": True
            },
            {
                "id": "space-2",
                "name": "sentence-transformers",
                "description": "Sentence transformers space",
                "dimension": 384,
                "model_id": "embedding-model-2",
                "is_active": True
            }
        ]
        mock_total = 2

        with patch.object(ModelRegistryService, 'list_embedding_spaces') as mock_list:
            mock_list.return_value = (mock_spaces, mock_total)

            # Act
            response = self.client.get("/registry/embedding-spaces")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["embedding_spaces"]) == 2
            assert data["total"] == 2
            assert data["embedding_spaces"][0]["dimension"] == 1536

    def test_create_embedding_space_success(self):
        """Test successful embedding space creation."""
        # Arrange
        space_data = {
            "name": "new-embedding-space",
            "description": "A new embedding space",
            "dimension": 768,
            "model_id": "embedding-model-123",
            "distance_metric": "cosine",
            "is_active": True
        }

        mock_created_space = {
            "id": "new-space-123",
            "name": "new-embedding-space",
            "description": "A new embedding space",
            "dimension": 768,
            "model_id": "embedding-model-123",
            "distance_metric": "cosine",
            "is_active": True
        }

        with patch.object(ModelRegistryService, 'get_model') as mock_check_model:
            mock_check_model.return_value = {"id": "embedding-model-123", "model_type": "embedding"}

            with patch.object(ModelRegistryService, 'get_embedding_space_by_name') as mock_check:
                mock_check.return_value = None

                with patch.object(ModelRegistryService, 'create_embedding_space') as mock_create:
                    mock_create.return_value = mock_created_space

                    # Act
                    response = self.client.post("/registry/embedding-spaces", json=space_data)

                    # Assert
                    assert response.status_code == status.HTTP_201_CREATED
                    data = response.json()
                    assert data["id"] == "new-space-123"
                    assert data["dimension"] == 768

    def test_get_embedding_space_success(self):
        """Test successful embedding space retrieval."""
        # Arrange
        space_id = "space-123"
        mock_space = {
            "id": space_id,
            "name": "test-space",
            "dimension": 1536,
            "model": {
                "id": "model-123",
                "name": "embedding-model"
            }
        }

        with patch.object(ModelRegistryService, 'get_embedding_space_with_model') as mock_get:
            mock_get.return_value = mock_space

            # Act
            response = self.client.get(f"/registry/embedding-spaces/{space_id}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == space_id
            assert data["name"] == "test-space"
            assert data["model"]["name"] == "embedding-model"

    def test_update_embedding_space_success(self):
        """Test successful embedding space update."""
        # Arrange
        space_id = "space-update-123"
        update_data = {
            "name": "updated-space",
            "description": "Updated description",
            "is_active": False
        }

        mock_updated_space = {
            "id": space_id,
            "name": "updated-space",
            "description": "Updated description",
            "is_active": False
        }

        with patch.object(ModelRegistryService, 'update_embedding_space') as mock_update:
            mock_update.return_value = mock_updated_space

            # Act
            response = self.client.put(f"/registry/embedding-spaces/{space_id}", json=update_data)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "updated-space"
            assert data["is_active"] is False

    def test_delete_embedding_space_success(self):
        """Test successful embedding space deletion."""
        # Arrange
        space_id = "space-delete-123"

        with patch.object(ModelRegistryService, 'delete_embedding_space') as mock_delete:
            mock_delete.return_value = True

            # Act
            response = self.client.delete(f"/registry/embedding-spaces/{space_id}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted"] is True
            assert data["space_id"] == space_id


@pytest.mark.unit
class TestDefaultEndpoints:
    """Test default provider/model endpoints."""

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

    def test_get_default_provider_success(self):
        """Test successful default provider retrieval."""
        # Arrange
        model_type = ModelType.CHAT.value
        mock_provider = {
            "id": "default-provider-123",
            "name": "Default Chat Provider",
            "provider_type": "llm",
            "is_active": True,
            "is_default": True
        }

        with patch.object(ModelRegistryService, 'get_default_provider') as mock_get:
            mock_get.return_value = mock_provider

            # Act
            response = self.client.get(f"/registry/defaults/provider/{model_type}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == "default-provider-123"
            assert data["is_default"] is True

    def test_get_default_model_success(self):
        """Test successful default model retrieval."""
        # Arrange
        model_type = ModelType.CHAT.value
        mock_model = {
            "id": "default-model-123",
            "name": "gpt-4",
            "model_type": "chat",
            "is_default": True,
            "provider": {
                "id": "openai-provider",
                "name": "OpenAI"
            }
        }

        with patch.object(ModelRegistryService, 'get_default_model') as mock_get:
            mock_get.return_value = mock_model

            # Act
            response = self.client.get(f"/registry/defaults/model/{model_type}")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == "default-model-123"
            assert data["is_default"] is True
            assert data["provider"]["name"] == "OpenAI"

    def test_get_default_embedding_space_success(self):
        """Test successful default embedding space retrieval."""
        # Arrange
        mock_space = {
            "id": "default-space-123",
            "name": "default-embeddings",
            "dimension": 1536,
            "is_default": True,
            "model": {
                "id": "embedding-model-123",
                "name": "text-embedding-ada-002"
            }
        }

        with patch.object(ModelRegistryService, 'get_default_embedding_space') as mock_get:
            mock_get.return_value = mock_space

            # Act
            response = self.client.get("/registry/defaults/embedding-space")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == "default-space-123"
            assert data["is_default"] is True
            assert data["model"]["name"] == "text-embedding-ada-002"


@pytest.mark.integration
class TestModelRegistryIntegration:
    """Integration tests for model registry workflows."""

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

    def test_provider_model_creation_workflow(self):
        """Test complete provider and model creation workflow."""
        # Step 1: Create provider
        provider_data = {
            "name": "Integration Provider",
            "provider_type": "llm",
            "config": {"api_base": "https://api.example.com"}
        }

        mock_provider = {
            "id": "integration-provider-123",
            "name": "Integration Provider",
            "provider_type": "llm"
        }

        with patch.object(ModelRegistryService, 'get_provider_by_name') as mock_check_provider:
            mock_check_provider.return_value = None

            with patch.object(ModelRegistryService, 'create_provider') as mock_create_provider:
                mock_create_provider.return_value = mock_provider

                provider_response = self.client.post("/registry/providers", json=provider_data)
                assert provider_response.status_code == status.HTTP_201_CREATED
                provider_id = provider_response.json()["id"]

        # Step 2: Create model for that provider
        model_data = {
            "name": "integration-model",
            "model_type": "chat",
            "provider_id": provider_id,
            "config": {"max_tokens": 4096}
        }

        mock_model = {
            "id": "integration-model-123",
            "name": "integration-model",
            "provider_id": provider_id
        }

        with patch.object(ModelRegistryService, 'get_provider') as mock_get_provider:
            mock_get_provider.return_value = mock_provider

            with patch.object(ModelRegistryService, 'get_model_by_name_and_provider') as mock_check_model:
                mock_check_model.return_value = None

                with patch.object(ModelRegistryService, 'create_model') as mock_create_model:
                    mock_create_model.return_value = mock_model

                    model_response = self.client.post("/registry/models", json=model_data)
                    assert model_response.status_code == status.HTTP_201_CREATED
                    assert model_response.json()["provider_id"] == provider_id

    def test_embedding_workflow(self):
        """Test complete embedding space creation workflow."""
        # Step 1: Create embedding provider
        provider_data = {
            "name": "Embedding Provider",
            "provider_type": "embedding"
        }

        mock_provider = {
            "id": "embedding-provider-123",
            "name": "Embedding Provider"
        }

        with patch.object(ModelRegistryService, 'get_provider_by_name') as mock_check:
            mock_check.return_value = None

            with patch.object(ModelRegistryService, 'create_provider') as mock_create:
                mock_create.return_value = mock_provider

                provider_response = self.client.post("/registry/providers", json=provider_data)
                provider_id = provider_response.json()["id"]

        # Step 2: Create embedding model
        model_data = {
            "name": "embedding-model",
            "model_type": "embedding",
            "provider_id": provider_id
        }

        mock_model = {
            "id": "embedding-model-123",
            "name": "embedding-model",
            "model_type": "embedding"
        }

        with patch.object(ModelRegistryService, 'get_provider'):
            with patch.object(ModelRegistryService, 'get_model_by_name_and_provider') as mock_check:
                mock_check.return_value = None

                with patch.object(ModelRegistryService, 'create_model') as mock_create:
                    mock_create.return_value = mock_model

                    model_response = self.client.post("/registry/models", json=model_data)
                    model_id = model_response.json()["id"]

        # Step 3: Create embedding space
        space_data = {
            "name": "test-embedding-space",
            "dimension": 1536,
            "model_id": model_id
        }

        mock_space = {
            "id": "embedding-space-123",
            "name": "test-embedding-space",
            "model_id": model_id
        }

        with patch.object(ModelRegistryService, 'get_model') as mock_get_model:
            mock_get_model.return_value = mock_model

            with patch.object(ModelRegistryService, 'get_embedding_space_by_name') as mock_check_space:
                mock_check_space.return_value = None

                with patch.object(ModelRegistryService, 'create_embedding_space') as mock_create_space:
                    mock_create_space.return_value = mock_space

                    space_response = self.client.post("/registry/embedding-spaces", json=space_data)
                    assert space_response.status_code == status.HTTP_201_CREATED
                    assert space_response.json()["model_id"] == model_id

    def test_default_setting_workflow(self):
        """Test setting and retrieving defaults workflow."""
        # Set up existing provider and model
        provider_id = "default-test-provider"
        model_id = "default-test-model"

        # Step 1: Set default provider
        with patch.object(ModelRegistryService, 'set_default_provider') as mock_set_provider:
            mock_set_provider.return_value = True

            set_response = self.client.post(
                f"/registry/providers/{provider_id}/set-default",
                json={"model_type": "chat"}
            )
            assert set_response.status_code == status.HTTP_200_OK

        # Step 2: Set default model
        with patch.object(ModelRegistryService, 'set_default_model') as mock_set_model:
            mock_set_model.return_value = True

            set_model_response = self.client.post(
                f"/registry/models/{model_id}/set-default",
                json={"model_type": "chat"}
            )
            assert set_model_response.status_code == status.HTTP_200_OK

        # Step 3: Retrieve defaults
        mock_default_provider = {
            "id": provider_id,
            "name": "Default Provider",
            "is_default": True
        }

        mock_default_model = {
            "id": model_id,
            "name": "Default Model",
            "is_default": True,
            "provider": mock_default_provider
        }

        with patch.object(ModelRegistryService, 'get_default_provider') as mock_get_provider:
            mock_get_provider.return_value = mock_default_provider

            with patch.object(ModelRegistryService, 'get_default_model') as mock_get_model:
                mock_get_model.return_value = mock_default_model

                provider_response = self.client.get("/registry/defaults/provider/chat")
                model_response = self.client.get("/registry/defaults/model/chat")

                assert provider_response.status_code == status.HTTP_200_OK
                assert model_response.status_code == status.HTTP_200_OK
                assert provider_response.json()["is_default"] is True
                assert model_response.json()["is_default"] is True
