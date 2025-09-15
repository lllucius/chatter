"""Tests for embedding service API key handling."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os

from chatter.services.embeddings import EmbeddingService
from chatter.models.registry import ProviderType


class TestEmbeddingServiceApiKeyHandling:
    """Test embedding service API key handling for providers with api_key_required flag."""

    @pytest.fixture
    def embedding_service(self):
        """Create embedding service instance for testing."""
        with patch('chatter.services.embeddings.get_session_maker'):
            return EmbeddingService()

    @pytest.fixture
    def openai_provider_no_key_required(self):
        """Mock OpenAI provider with api_key_required=False."""
        provider = Mock()
        provider.name = "openai"
        provider.provider_type = ProviderType.OPENAI
        provider.api_key_required = False
        provider.base_url = "https://api.custom-llm.com/v1"
        provider.default_config = {}
        return provider

    @pytest.fixture
    def openai_provider_key_required(self):
        """Mock OpenAI provider with api_key_required=True."""
        provider = Mock()
        provider.name = "openai"
        provider.provider_type = ProviderType.OPENAI
        provider.api_key_required = True
        provider.base_url = "https://api.openai.com/v1"
        provider.default_config = {}
        return provider

    @pytest.fixture
    def model_def(self):
        """Mock model definition."""
        model = Mock()
        model.model_name = "text-embedding-ada-002"
        model.chunk_size = 1000
        model.default_config = {}
        return model

    def clear_api_key_env_vars(self):
        """Clear API key environment variables."""
        for key in [
            'OPENAI_API_KEY',
            'GOOGLE_API_KEY',
            'COHERE_API_KEY',
        ]:
            if key in os.environ:
                del os.environ[key]

    def restore_env_vars(self, original_vars):
        """Restore environment variables."""
        for key, value in original_vars.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]

    @pytest.mark.asyncio
    async def test_openai_provider_no_api_key_required_succeeds(
        self,
        embedding_service,
        openai_provider_no_key_required,
        model_def,
    ):
        """Test OpenAI provider with api_key_required=False succeeds without API key."""
        # Save original environment
        original_vars = {
            key: os.environ.get(key) for key in ['OPENAI_API_KEY']
        }

        try:
            # Clear API key environment variables
            self.clear_api_key_env_vars()

            # This should succeed because api_key_required=False
            instance = await embedding_service._create_embedding_provider_instance(
                openai_provider_no_key_required, model_def
            )

            assert (
                instance is not None
            ), "Should create provider instance when api_key_required=False"

        finally:
            self.restore_env_vars(original_vars)

    @pytest.mark.asyncio
    async def test_openai_provider_api_key_required_fails_without_key(
        self, embedding_service, openai_provider_key_required, model_def
    ):
        """Test OpenAI provider with api_key_required=True fails without API key."""
        # Save original environment
        original_vars = {
            key: os.environ.get(key) for key in ['OPENAI_API_KEY']
        }

        try:
            # Clear API key environment variables
            self.clear_api_key_env_vars()

            # This should fail because api_key_required=True and no API key
            instance = await embedding_service._create_embedding_provider_instance(
                openai_provider_key_required, model_def
            )

            assert (
                instance is None
            ), "Should not create provider instance when api_key_required=True and no API key"

        finally:
            self.restore_env_vars(original_vars)

    @pytest.mark.asyncio
    async def test_openai_provider_api_key_required_succeeds_with_key(
        self, embedding_service, openai_provider_key_required, model_def
    ):
        """Test OpenAI provider with api_key_required=True succeeds with API key."""
        # Save original environment
        original_vars = {
            key: os.environ.get(key) for key in ['OPENAI_API_KEY']
        }

        try:
            # Set API key in environment
            os.environ['OPENAI_API_KEY'] = 'test-api-key'

            # This should succeed because api_key_required=True and API key is present
            instance = await embedding_service._create_embedding_provider_instance(
                openai_provider_key_required, model_def
            )

            assert (
                instance is not None
            ), "Should create provider instance when api_key_required=True and API key present"

        finally:
            self.restore_env_vars(original_vars)

    @pytest.mark.asyncio
    async def test_google_provider_no_api_key_required_succeeds(
        self, embedding_service, model_def
    ):
        """Test Google provider with api_key_required=False succeeds without API key."""
        # Skip if Google embeddings not available
        from chatter.services.embeddings import GOOGLE_AVAILABLE

        if not GOOGLE_AVAILABLE:
            pytest.skip("Google embeddings not available")

        # Mock Google provider with api_key_required=False
        provider = Mock()
        provider.name = "google"
        provider.provider_type = ProviderType.GOOGLE
        provider.api_key_required = False
        provider.base_url = None
        provider.default_config = {}

        # Save original environment
        original_vars = {
            key: os.environ.get(key) for key in ['GOOGLE_API_KEY']
        }

        try:
            # Clear API key environment variables
            self.clear_api_key_env_vars()

            # This should succeed because api_key_required=False
            instance = await embedding_service._create_embedding_provider_instance(
                provider, model_def
            )

            assert (
                instance is not None
            ), "Should create Google provider instance when api_key_required=False"

        finally:
            self.restore_env_vars(original_vars)

    @pytest.mark.asyncio
    async def test_cohere_provider_no_api_key_required_succeeds(
        self, embedding_service, model_def
    ):
        """Test Cohere provider with api_key_required=False succeeds without API key."""
        # Skip if Cohere embeddings not available
        from chatter.services.embeddings import COHERE_AVAILABLE

        if not COHERE_AVAILABLE:
            pytest.skip("Cohere embeddings not available")

        # Mock Cohere provider with api_key_required=False
        provider = Mock()
        provider.name = "cohere"
        provider.provider_type = ProviderType.COHERE
        provider.api_key_required = False
        provider.base_url = None
        provider.default_config = {}

        # Save original environment
        original_vars = {
            key: os.environ.get(key) for key in ['COHERE_API_KEY']
        }

        try:
            # Clear API key environment variables
            self.clear_api_key_env_vars()

            # This should succeed because api_key_required=False
            instance = await embedding_service._create_embedding_provider_instance(
                provider, model_def
            )

            assert (
                instance is not None
            ), "Should create Cohere provider instance when api_key_required=False"

        finally:
            self.restore_env_vars(original_vars)
