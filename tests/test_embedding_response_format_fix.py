"""Test for embedding response format handling fix."""

from unittest.mock import AsyncMock, Mock

import pytest

from chatter.models.registry import ProviderType
from chatter.services.embeddings import (
    EmbeddingService,
    SafeOpenAIEmbeddings,
)


class TestEmbeddingResponseFormatFix:
    """Test the SafeOpenAIEmbeddings fix for response format issues."""

    @pytest.mark.asyncio
    async def test_safe_embeddings_handles_problematic_response_format(
        self,
    ):
        """Test that SafeOpenAIEmbeddings handles problematic response formats."""

        # Create mock client that returns problematic format that causes:
        # "'list' object has no attribute 'data'" or "'list' object has no attribute 'model_dump'"
        class MockProblematicClient:
            async def create(self, input, **kwargs):
                # Return list directly (causes the original issue)
                return [{"embedding": [0.1, 0.2, 0.3]} for _ in input]

        # Create SafeOpenAIEmbeddings instance
        embeddings = SafeOpenAIEmbeddings(
            api_key='test-key', model='text-embedding-ada-002'
        )

        # Replace client with problematic one
        embeddings.async_client = MockProblematicClient()

        # Test multiple documents - this should trigger the fallback
        texts = ['hello', 'world', 'test']
        result = await embeddings.aembed_documents(texts)

        # Verify correct format
        assert len(result) == 3
        assert all(isinstance(emb, list) for emb in result)
        assert all(len(emb) == 3 for emb in result)
        assert all(
            all(isinstance(val, (int, float)) for val in emb)
            for emb in result
        )

        # Test single query
        query_result = await embeddings.aembed_query("test query")
        assert isinstance(query_result, list)
        assert len(query_result) == 3
        assert all(
            isinstance(val, (int, float)) for val in query_result
        )

    @pytest.mark.asyncio
    async def test_safe_embeddings_preserves_standard_behavior(self):
        """Test that SafeOpenAIEmbeddings still works with standard responses."""

        # Create mock client that returns standard format
        class MockStandardClient:
            async def create(self, input, **kwargs):
                # Return standard OpenAI response format
                class MockResponse:
                    def __init__(self):
                        self.data = [
                            Mock(embedding=[0.4, 0.5, 0.6])
                            for _ in input
                        ]

                return MockResponse()

        # Create SafeOpenAIEmbeddings instance
        embeddings = SafeOpenAIEmbeddings(
            api_key='test-key', model='text-embedding-ada-002'
        )

        # Replace client with standard one
        embeddings.async_client = MockStandardClient()

        # Test - should work normally without fallback
        texts = ['hello', 'world']
        result = await embeddings.aembed_documents(texts)

        # Verify correct format
        assert len(result) == 2
        assert all(isinstance(emb, list) for emb in result)
        assert all(len(emb) == 3 for emb in result)
        assert result[0] == [0.4, 0.5, 0.6]
        assert result[1] == [0.4, 0.5, 0.6]

    @pytest.mark.asyncio
    async def test_embedding_service_creates_safe_openai_embeddings(
        self,
    ):
        """Test that EmbeddingService creates SafeOpenAIEmbeddings instances."""

        # Mock database session
        session_mock = AsyncMock()

        # Create service
        embedding_service = EmbeddingService(session_mock)

        # Mock provider and model
        provider = Mock()
        provider.provider_type = ProviderType.OPENAI
        provider.api_key_required = (
            True  # Set to True but we have the env var
        )
        provider.base_url = "https://api.openai.com/v1"
        provider.name = "openai"

        model_def = Mock()
        model_def.model_name = "text-embedding-ada-002"
        model_def.chunk_size = 1000
        model_def.default_config = {}

        # Create provider instance
        instance = (
            await embedding_service._create_embedding_provider_instance(
                provider, model_def
            )
        )

        # Verify it's SafeOpenAIEmbeddings
        assert isinstance(instance, SafeOpenAIEmbeddings)

        # Verify provider name detection works
        provider_name = embedding_service._get_provider_name(instance)
        assert provider_name == "openai"
