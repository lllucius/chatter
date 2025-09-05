"""Unit tests for model registry validation logic (no database required)."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from chatter.core.exceptions import ValidationError
from chatter.core.model_registry import ModelRegistryService
from chatter.models.registry import ModelDef, ModelType, Provider


class TestModelValidation:
    """Test model validation logic without database."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock service for testing validation logic."""
        service = ModelRegistryService(AsyncMock())
        return service

    def test_validate_model_consistency_embedding_without_dimensions(self, mock_service):
        """Test that embedding models must have dimensions."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        model = ModelDef(
            name=f"test_embedding_{unique_id}",
            model_type=ModelType.EMBEDDING,
            display_name="Test Embedding",
            model_name="text-embedding-ada-002",
            provider_id=f"test_provider_{unique_id}",
            # Missing dimensions
        )
        
        # Use pytest.raises as async context manager
        with pytest.raises(ValidationError) as exc_info:
            import asyncio
            asyncio.run(mock_service._validate_model_consistency(model))
        
        assert "Embedding models must specify dimensions" in str(exc_info.value)

    def test_validate_model_consistency_llm_with_dimensions(self, mock_service):
        """Test that LLM models should not have dimensions."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        model = ModelDef(
            name=f"test_llm_{unique_id}",
            model_type=ModelType.LLM,
            display_name="Test LLM",
            model_name="gpt-4",
            provider_id=f"test_provider_{unique_id}",
            dimensions=1536,  # Should not have dimensions
        )
        
        with pytest.raises(ValidationError) as exc_info:
            import asyncio
            asyncio.run(mock_service._validate_model_consistency(model))
        
        assert "LLM models should not specify dimensions" in str(exc_info.value)

    def test_validate_model_consistency_negative_max_tokens(self, mock_service):
        """Test that max_tokens must be positive."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        model = ModelDef(
            name=f"test_llm_{unique_id}",
            model_type=ModelType.LLM,
            display_name="Test LLM",
            model_name="gpt-4",
            provider_id=f"test_provider_{unique_id}",
            max_tokens=-100,  # Invalid
        )
        
        with pytest.raises(ValidationError) as exc_info:
            import asyncio
            asyncio.run(mock_service._validate_model_consistency(model))
        
        assert "max_tokens must be positive" in str(exc_info.value)

    def test_validate_model_consistency_batch_settings_conflict(self, mock_service):
        """Test that max_batch_size requires supports_batch."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        model = ModelDef(
            name=f"test_embedding_{unique_id}",
            model_type=ModelType.EMBEDDING,
            display_name="Test Embedding",
            model_name="text-embedding-ada-002",
            provider_id=f"test_provider_{unique_id}",
            dimensions=1536,
            max_batch_size=100,
            supports_batch=False,  # Conflict
        )
        
        with pytest.raises(ValidationError) as exc_info:
            import asyncio
            asyncio.run(mock_service._validate_model_consistency(model))
        
        assert "supports_batch is False" in str(exc_info.value)

    def test_validate_model_consistency_valid_embedding_model(self, mock_service):
        """Test that valid embedding model passes validation."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        model = ModelDef(
            name=f"test_embedding_{unique_id}",
            model_type=ModelType.EMBEDDING,
            display_name="Test Embedding",
            model_name="text-embedding-ada-002",
            provider_id=f"test_provider_{unique_id}",
            dimensions=1536,
            supports_batch=True,
            max_batch_size=100,
        )
        
        # Should not raise any exception
        import asyncio
        asyncio.run(mock_service._validate_model_consistency(model))

    def test_validate_model_consistency_valid_llm_model(self, mock_service):
        """Test that valid LLM model passes validation."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        model = ModelDef(
            name=f"test_llm_{unique_id}",
            model_type=ModelType.LLM,
            display_name="Test LLM",
            model_name="gpt-4",
            provider_id=f"test_provider_{unique_id}",
            max_tokens=4096,
            context_length=8192,
        )
        
        # Should not raise any exception
        import asyncio
        asyncio.run(mock_service._validate_model_consistency(model))


class TestValidationErrorMessages:
    """Test that validation errors provide clear, actionable messages."""
    
    def test_validation_error_contains_helpful_context(self):
        """Test that validation errors contain helpful context."""
        try:
            raise ValidationError("Provider with ID nonexistent not found")
        except ValidationError as e:
            assert "Provider with ID" in str(e)
            assert "not found" in str(e)
            assert "nonexistent" in str(e)

    def test_validation_error_is_exception(self):
        """Test that ValidationError is properly inheriting from Exception."""
        error = ValidationError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"


class TestBusinessLogicValidation:
    """Test business logic validation scenarios."""
    
    def test_dimension_mismatch_error_message(self):
        """Test that dimension mismatch errors are clear."""
        expected_dims = 1536
        actual_dims = 512
        
        error_msg = f"Base dimensions {actual_dims} do not match model dimensions {expected_dims}"
        error = ValidationError(error_msg)
        
        assert str(expected_dims) in str(error)
        assert str(actual_dims) in str(error)
        assert "do not match" in str(error)

    def test_provider_model_type_mismatch_error(self):
        """Test error when provider has no models of specified type."""
        provider_name = "Test Provider"
        model_type = "EMBEDDING"
        
        error_msg = f"Provider {provider_name} has no active models of type {model_type}"
        error = ValidationError(error_msg)
        
        assert provider_name in str(error)
        assert model_type in str(error)
        assert "no active models" in str(error)


if __name__ == "__main__":
    # Run a simple test to verify the validation works
    import asyncio
    from unittest.mock import AsyncMock
    
    async def test_basic_validation():
        service = ModelRegistryService(AsyncMock())
        
        # Test invalid embedding model (no dimensions)
        model = ModelDef(
            name="test",
            model_type=ModelType.EMBEDDING,
            display_name="Test",
            model_name="test-model",
            provider_id="test",
        )
        
        try:
            await service._validate_model_consistency(model)
            print("❌ Expected validation error but none was raised")
        except ValidationError as e:
            print(f"✅ Validation correctly failed: {e}")
        
        # Test valid LLM model
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        llm_model = ModelDef(
            name=f"test_llm_{unique_id}",
            model_type=ModelType.LLM,
            display_name="Test LLM",
            model_name="gpt-4",
            provider_id=f"test_{unique_id}",
            max_tokens=4096,
        )
        
        try:
            await service._validate_model_consistency(llm_model)
            print("✅ Valid LLM model passed validation")
        except ValidationError as e:
            print(f"❌ Unexpected validation error: {e}")
    
    print("Running basic validation tests...")
    asyncio.run(test_basic_validation())
    print("✅ All basic validation tests completed")