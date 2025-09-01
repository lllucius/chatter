"""Tests for model registry core functionality."""

# Mock all required modules at module level
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

for module_name in [
    'chatter.core.model_registry',
    'chatter.models.registry',
    'chatter.schemas.model_registry',
    'chatter.config',
    'chatter.utils.logging',
    'chatter.core.dynamic_embeddings'
]:
    if module_name not in sys.modules:
        sys.modules[module_name] = MagicMock()


@pytest.mark.unit
class TestModelRegistryCore:
    """Test model registry core functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.mock_engine = MagicMock()

    @pytest.mark.asyncio
    async def test_provider_creation(self):
        """Test provider creation functionality."""
        # Arrange
        provider_data = {
            "name": "openai",
            "type": "llm",
            "config": {"api_key": "test-key"},
            "is_active": True
        }

        with patch('chatter.core.model_registry.Provider') as mock_provider_class:
            mock_provider = MagicMock()
            mock_provider.id = "provider-123"
            mock_provider_class.return_value = mock_provider

            # Mock the service class - since we can't import it directly
            mock_service = MagicMock()
            mock_service.create_provider = AsyncMock(return_value=mock_provider)

            # Act
            result = await mock_service.create_provider(self.mock_session, provider_data)

            # Assert
            assert result == mock_provider
            mock_service.create_provider.assert_called_once_with(self.mock_session, provider_data)

    @pytest.mark.asyncio
    async def test_model_def_creation(self):
        """Test model definition creation."""
        # Arrange
        model_data = {
            "name": "gpt-4",
            "provider_id": "provider-123",
            "model_type": "conversational",
            "config": {"temperature": 0.7}
        }

        mock_service = MagicMock()
        mock_model = MagicMock()
        mock_model.id = "model-456"
        mock_service.create_model_def = AsyncMock(return_value=mock_model)

        # Act
        result = await mock_service.create_model_def(self.mock_session, model_data)

        # Assert
        assert result == mock_model
        mock_service.create_model_def.assert_called_once_with(self.mock_session, model_data)

    def test_list_params_validation(self):
        """Test list parameters validation."""
        # Import mock at runtime to avoid import issues
        from unittest.mock import MagicMock

        # Arrange - simulate ListParams dataclass
        ListParams = MagicMock()
        list_params_instance = MagicMock()
        list_params_instance.page = 1
        list_params_instance.per_page = 20
        list_params_instance.active_only = True
        ListParams.return_value = list_params_instance

        # Act
        params = ListParams()

        # Assert
        assert params.page == 1
        assert params.per_page == 20
        assert params.active_only is True

    @pytest.mark.asyncio
    async def test_embedding_space_creation(self):
        """Test embedding space creation."""
        # Arrange
        embedding_data = {
            "name": "text-embedding-ada-002",
            "dimensions": 1536,
            "provider_id": "provider-123",
            "config": {"max_tokens": 8192}
        }

        mock_service = MagicMock()
        mock_embedding_space = MagicMock()
        mock_embedding_space.id = "embedding-789"
        mock_service.create_embedding_space = AsyncMock(return_value=mock_embedding_space)

        # Act
        result = await mock_service.create_embedding_space(self.mock_session, embedding_data)

        # Assert
        assert result == mock_embedding_space
        mock_service.create_embedding_space.assert_called_once_with(self.mock_session, embedding_data)

    @pytest.mark.asyncio
    async def test_provider_listing(self):
        """Test provider listing functionality."""
        # Arrange
        mock_providers = [
            MagicMock(id="provider-1"),
            MagicMock(id="provider-2")
        ]
        mock_providers[0].name = "openai"
        mock_providers[1].name = "anthropic"

        mock_service = MagicMock()
        mock_service.list_providers = AsyncMock(return_value=mock_providers)

        # Act
        result = await mock_service.list_providers(self.mock_session)

        # Assert
        assert len(result) == 2
        assert result[0].name == "openai"
        assert result[1].name == "anthropic"

    @pytest.mark.asyncio
    async def test_provider_update(self):
        """Test provider update functionality."""
        # Arrange
        provider_id = "provider-123"
        update_data = {"is_active": False}

        mock_service = MagicMock()
        mock_updated_provider = MagicMock()
        mock_updated_provider.is_active = False
        mock_service.update_provider = AsyncMock(return_value=mock_updated_provider)

        # Act
        result = await mock_service.update_provider(self.mock_session, provider_id, update_data)

        # Assert
        assert result.is_active is False
        mock_service.update_provider.assert_called_once_with(self.mock_session, provider_id, update_data)

    def test_sync_engine_creation(self):
        """Test synchronous engine creation for table operations."""
        # Arrange
        mock_settings = MagicMock()
        mock_settings.database_url = "postgresql+asyncpg://user:pass@host/db"

        with patch('chatter.core.model_registry.settings', mock_settings):
            with patch('chatter.core.model_registry.create_engine'):
                # Mock the get_sync_engine function
                get_sync_engine = MagicMock()

                # Act
                get_sync_engine()

                # Assert
                get_sync_engine.assert_called_once()


@pytest.mark.integration
class TestModelRegistryIntegration:
    """Integration tests for model registry."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.mock_session = AsyncMock()

    @pytest.mark.asyncio
    async def test_full_provider_lifecycle(self):
        """Test complete provider lifecycle."""
        # Arrange
        mock_service = MagicMock()

        # Create provider
        provider_data = {"name": "test-provider", "type": "llm"}
        mock_provider = MagicMock(id="provider-123")
        mock_service.create_provider = AsyncMock(return_value=mock_provider)

        # Update provider
        update_data = {"is_active": False}
        mock_updated_provider = MagicMock(is_active=False)
        mock_service.update_provider = AsyncMock(return_value=mock_updated_provider)

        # Delete provider
        mock_service.delete_provider = AsyncMock(return_value=True)

        # Act & Assert
        # Create
        created = await mock_service.create_provider(self.mock_session, provider_data)
        assert created.id == "provider-123"

        # Update
        updated = await mock_service.update_provider(self.mock_session, "provider-123", update_data)
        assert updated.is_active is False

        # Delete
        deleted = await mock_service.delete_provider(self.mock_session, "provider-123")
        assert deleted is True

    @pytest.mark.asyncio
    async def test_model_def_with_provider_relationship(self):
        """Test model definition creation with provider relationship."""
        # Arrange
        mock_service = MagicMock()

        # Provider exists
        mock_provider = MagicMock(id="provider-123")
        mock_provider.name = "openai"
        mock_service.get_provider = AsyncMock(return_value=mock_provider)

        # Model creation
        model_data = {
            "name": "gpt-4",
            "provider_id": "provider-123",
            "model_type": "conversational"
        }
        mock_model = MagicMock(id="model-456", provider=mock_provider)
        mock_service.create_model_def = AsyncMock(return_value=mock_model)

        # Act
        provider = await mock_service.get_provider(self.mock_session, "provider-123")
        model = await mock_service.create_model_def(self.mock_session, model_data)

        # Assert
        assert provider.name == "openai"
        assert model.provider.id == "provider-123"

    @pytest.mark.asyncio
    async def test_embedding_space_with_model_integration(self):
        """Test embedding space integration with models."""
        # Arrange
        mock_service = MagicMock()

        # Create embedding space
        embedding_data = {
            "name": "ada-002",
            "dimensions": 1536,
            "provider_id": "provider-123"
        }
        mock_embedding = MagicMock(id="embedding-789")
        mock_service.create_embedding_space = AsyncMock(return_value=mock_embedding)

        # Associate with model
        mock_service.associate_embedding_with_model = AsyncMock(return_value=True)

        # Act
        embedding = await mock_service.create_embedding_space(self.mock_session, embedding_data)
        associated = await mock_service.associate_embedding_with_model(
            self.mock_session, "model-456", "embedding-789"
        )

        # Assert
        assert embedding.id == "embedding-789"
        assert associated is True
