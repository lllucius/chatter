"""Tests for model registry API fixes."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.exceptions import ValidationError
from chatter.core.model_registry import ModelRegistryService
from chatter.models.registry import ModelType, ProviderType
from chatter.schemas.model_registry import (
    EmbeddingSpaceCreate,
    ModelDefCreate,
    ProviderCreate,
)


@pytest.fixture
async def service(db_session: AsyncSession) -> ModelRegistryService:
    """Create a model registry service."""
    return ModelRegistryService(db_session)


@pytest.fixture
async def sample_provider(service: ModelRegistryService) -> str:
    """Create a sample provider."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    provider_data = ProviderCreate(
        name=f"test_provider_{unique_id}",
        provider_type=ProviderType.OPENAI,
        display_name="Test Provider",
        description="Test provider for unit tests",
    )
    provider = await service.create_provider(provider_data)
    return provider.id


@pytest.fixture
async def sample_llm_model(
    service: ModelRegistryService, sample_provider: str
) -> str:
    """Create a sample LLM model."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    model_data = ModelDefCreate(
        provider_id=sample_provider,
        name=f"test_llm_{unique_id}",
        model_type=ModelType.LLM,
        display_name="Test LLM",
        model_name="gpt-4",
        max_tokens=4096,
        context_length=8192,
    )
    model = await service.create_model(model_data)
    return model.id


@pytest.fixture
async def sample_embedding_model(
    service: ModelRegistryService, sample_provider: str
) -> str:
    """Create a sample embedding model."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    model_data = ModelDefCreate(
        provider_id=sample_provider,
        name=f"test_embedding_{unique_id}",
        model_type=ModelType.EMBEDDING,
        display_name="Test Embedding",
        model_name="text-embedding-ada-002",
        dimensions=1536,
        supports_batch=True,
        max_batch_size=100,
    )
    model = await service.create_model(model_data)
    return model.id


class TestDefaultProviderLogic:
    """Test default provider logic fixes."""

    async def test_set_default_provider_with_model_type(
        self,
        service: ModelRegistryService,
        sample_provider: str,
        sample_llm_model: str,
    ):
        """Test setting default provider for specific model type."""
        # Set as default for LLM
        success = await service.set_default_provider(
            sample_provider, ModelType.LLM
        )
        assert success

        # Verify it's set as default for LLM
        default_provider = await service.get_default_provider(
            ModelType.LLM
        )
        assert default_provider is not None
        assert default_provider.id == sample_provider

    async def test_set_default_provider_without_models_fails(
        self, service: ModelRegistryService, sample_provider: str
    ):
        """Test that setting default fails if provider has no models of that type."""
        # Try to set as default for EMBEDDING when it has no embedding models
        success = await service.set_default_provider(
            sample_provider, ModelType.EMBEDDING
        )
        assert not success

    async def test_set_default_provider_nonexistent_fails(
        self, service: ModelRegistryService
    ):
        """Test that setting default fails for nonexistent provider."""
        success = await service.set_default_provider(
            "nonexistent", ModelType.LLM
        )
        assert not success

    async def test_get_default_provider_by_model_type(
        self,
        service: ModelRegistryService,
        sample_provider: str,
        sample_llm_model: str,
        sample_embedding_model: str,
    ):
        """Test getting default provider filtered by model type."""
        # Set as default for LLM
        await service.set_default_provider(
            sample_provider, ModelType.LLM
        )

        # Should find default for LLM
        llm_default = await service.get_default_provider(ModelType.LLM)
        assert llm_default is not None
        assert llm_default.id == sample_provider

        # Should not find default for EMBEDDING (we haven't set one)
        embedding_default = await service.get_default_provider(
            ModelType.EMBEDDING
        )
        assert embedding_default is None


class TestValidationImprovements:
    """Test validation improvements."""

    async def test_create_model_validates_provider_exists(
        self, service: ModelRegistryService
    ):
        """Test that creating model validates provider exists."""
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        model_data = ModelDefCreate(
            provider_id="nonexistent",
            name=f"test_model_{unique_id}",
            model_type=ModelType.LLM,
            display_name="Test Model",
            model_name="gpt-4",
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.create_model(model_data)

        assert "Provider with ID nonexistent not found" in str(
            exc_info.value
        )

    async def test_create_model_validates_provider_active(
        self, service: ModelRegistryService, sample_provider: str
    ):
        """Test that creating model validates provider is active."""
        # Deactivate the provider
        provider = await service.get_provider(sample_provider)
        provider.is_active = False
        await service.session.commit()

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        model_data = ModelDefCreate(
            provider_id=sample_provider,
            name=f"test_model_{unique_id}",
            model_type=ModelType.LLM,
            display_name="Test Model",
            model_name="gpt-4",
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.create_model(model_data)

        assert "is not active" in str(exc_info.value)

    async def test_create_embedding_space_validates_model_exists(
        self, service: ModelRegistryService
    ):
        """Test that creating embedding space validates model exists."""
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        space_data = EmbeddingSpaceCreate(
            model_id="nonexistent",
            name=f"test_space_{unique_id}",
            display_name="Test Space",
            base_dimensions=1536,
            effective_dimensions=1536,
            table_name=f"test_embeddings_{unique_id}",
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.create_embedding_space(space_data)

        assert "Model with ID nonexistent not found" in str(
            exc_info.value
        )

    async def test_create_embedding_space_validates_model_type(
        self, service: ModelRegistryService, sample_llm_model: str
    ):
        """Test that creating embedding space validates model is embedding type."""
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        space_data = EmbeddingSpaceCreate(
            model_id=sample_llm_model,
            name=f"test_space_{unique_id}",
            display_name="Test Space",
            base_dimensions=1536,
            effective_dimensions=1536,
            table_name=f"test_embeddings_{unique_id}",
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.create_embedding_space(space_data)

        assert "is not an embedding model" in str(exc_info.value)

    async def test_create_embedding_space_validates_model_active(
        self, service: ModelRegistryService, sample_embedding_model: str
    ):
        """Test that creating embedding space validates model is active."""
        # Deactivate the model
        model = await service.get_model(sample_embedding_model)
        model.is_active = False
        await service.session.commit()

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        space_data = EmbeddingSpaceCreate(
            model_id=sample_embedding_model,
            name=f"test_space_{unique_id}",
            display_name="Test Space",
            base_dimensions=1536,
            effective_dimensions=1536,
            table_name=f"test_embeddings_{unique_id}",
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.create_embedding_space(space_data)

        assert "is not active" in str(exc_info.value)

    async def test_create_embedding_space_validates_dimensions(
        self, service: ModelRegistryService, sample_embedding_model: str
    ):
        """Test that creating embedding space validates dimensions match."""
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        space_data = EmbeddingSpaceCreate(
            model_id=sample_embedding_model,
            name=f"test_space_{unique_id}",
            display_name="Test Space",
            base_dimensions=512,  # Different from model's 1536
            effective_dimensions=512,
            table_name=f"test_embeddings_{unique_id}",
        )

        with pytest.raises(ValidationError) as exc_info:
            await service.create_embedding_space(space_data)

        assert "do not match model dimensions" in str(exc_info.value)


class TestBusinessLogicImprovements:
    """Test business logic improvements."""

    async def test_set_default_provider_sets_model_default(
        self,
        service: ModelRegistryService,
        sample_provider: str,
        sample_llm_model: str,
    ):
        """Test that setting default provider also sets a model as default."""
        # Set provider as default for LLM
        await service.set_default_provider(
            sample_provider, ModelType.LLM
        )

        # Verify the model is also set as default
        model = await service.get_model(sample_llm_model)
        assert model.is_default

    async def test_multiple_providers_different_model_types(
        self, service: ModelRegistryService
    ):
        """Test that different providers can be default for different model types."""
        import uuid

        unique_id = str(uuid.uuid4())[:8]

        # Create two providers
        provider1_data = ProviderCreate(
            name=f"provider1_{unique_id}",
            provider_type=ProviderType.OPENAI,
            display_name="Provider 1",
        )
        provider1 = await service.create_provider(provider1_data)

        provider2_data = ProviderCreate(
            name=f"provider2_{unique_id}",
            provider_type=ProviderType.ANTHROPIC,
            display_name="Provider 2",
        )
        provider2 = await service.create_provider(provider2_data)

        # Create LLM model for provider1
        llm_data = ModelDefCreate(
            provider_id=provider1.id,
            name=f"llm1_{unique_id}",
            model_type=ModelType.LLM,
            display_name="LLM 1",
            model_name="gpt-4",
        )
        await service.create_model(llm_data)

        # Create embedding model for provider2
        embedding_data = ModelDefCreate(
            provider_id=provider2.id,
            name=f"embedding1_{unique_id}",
            model_type=ModelType.EMBEDDING,
            display_name="Embedding 1",
            model_name="text-embedding-ada-002",
            dimensions=1536,
        )
        await service.create_model(embedding_data)

        # Set provider1 as default for LLM
        await service.set_default_provider(provider1.id, ModelType.LLM)

        # Set provider2 as default for EMBEDDING
        await service.set_default_provider(
            provider2.id, ModelType.EMBEDDING
        )

        # Verify both defaults are set correctly
        llm_default = await service.get_default_provider(ModelType.LLM)
        assert llm_default.id == provider1.id

        embedding_default = await service.get_default_provider(
            ModelType.EMBEDDING
        )
        assert embedding_default.id == provider2.id


class TestTransactionManagement:
    """Test transaction management improvements."""

    async def test_create_model_transaction_rollback_on_error(
        self, service: ModelRegistryService, sample_provider: str
    ):
        """Test that model creation rolls back properly on error."""
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        # Create a model with invalid data to trigger an error
        model_data = ModelDefCreate(
            provider_id=sample_provider,
            name=f"test_model_{unique_id}",
            model_type=ModelType.LLM,
            display_name="Test Model",
            model_name="gpt-4",
        )

        # First create should succeed
        model = await service.create_model(model_data)
        assert model is not None

        # Second create with same name should fail and not leave partial data
        with pytest.raises(
            (ValueError, IntegrityError)
        ):  # Could be IntegrityError or ValidationError
            await service.create_model(model_data)

        # Verify no partial data was left
        models = await service.list_models(provider_id=sample_provider)
        assert (
            len(models[0]) == 1
        )  # Should still be just the first model
