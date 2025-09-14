"""Test for the specific OpenAI response format issue bug fix."""

import pytest
from unittest.mock import Mock, AsyncMock
import logging

from chatter.services.embeddings import SafeOpenAIEmbeddings

# Set up logging to see the debug output
logging.basicConfig(level=logging.DEBUG)


class TestOpenAIResponseFormatBugFix:
    """Test for the specific bug where list responses cause 'data' attribute errors."""

    @pytest.mark.asyncio
    async def test_list_response_format_handled_correctly(self):
        """Test that list responses don't cause 'data' attribute errors."""
        
        # Create a mock client that returns a direct list (this is the problematic case)
        class MockListResponseClient:
            async def create(self, input, **kwargs):
                # Return list directly - this causes the original issue
                return [
                    {"embedding": [0.1, 0.2, 0.3]},
                    {"embedding": [0.4, 0.5, 0.6]},
                    {"embedding": [0.7, 0.8, 0.9]}
                ]
        
        # Create SafeOpenAIEmbeddings instance
        embeddings = SafeOpenAIEmbeddings(
            api_key='test-key',
            model='text-embedding-ada-002'
        )
        
        # Replace client with the problematic one
        embeddings.async_client = MockListResponseClient()
        
        # This should work without errors
        texts = ['hello', 'world', 'test']
        result = await embeddings.aembed_documents(texts)
        
        # Verify correct results
        assert len(result) == 3
        assert all(isinstance(emb, list) for emb in result)
        assert all(len(emb) == 3 for emb in result)
        assert result[0] == [0.1, 0.2, 0.3]
        assert result[1] == [0.4, 0.5, 0.6]
        assert result[2] == [0.7, 0.8, 0.9]

    @pytest.mark.asyncio
    async def test_list_response_single_query_format(self):
        """Test that list responses work for single query embedding."""
        
        # Create a mock client that returns a direct list 
        class MockListResponseClient:
            async def create(self, input, **kwargs):
                # For single query, return single item list
                return [{"embedding": [0.1, 0.2, 0.3]}]
        
        # Create SafeOpenAIEmbeddings instance
        embeddings = SafeOpenAIEmbeddings(
            api_key='test-key',
            model='text-embedding-ada-002'
        )
        
        # Replace client with the problematic one
        embeddings.async_client = MockListResponseClient()
        
        # Test single query
        result = await embeddings.aembed_query("test query")
        
        # Verify correct results
        assert isinstance(result, list)
        assert len(result) == 3
        assert result == [0.1, 0.2, 0.3]

    @pytest.mark.asyncio
    async def test_error_propagation_in_fallback(self):
        """Test that actual errors are properly propagated from fallback method."""
        
        # Create a mock client that returns invalid format
        class MockInvalidResponseClient:
            async def create(self, input, **kwargs):
                # Return something that should cause an error
                return {"invalid": "format"}
        
        # Create SafeOpenAIEmbeddings instance
        embeddings = SafeOpenAIEmbeddings(
            api_key='test-key',
            model='text-embedding-ada-002'
        )
        
        # Replace client
        embeddings.async_client = MockInvalidResponseClient()
        
        # This should raise a proper error, not the 'data' attribute error
        texts = ['hello', 'world', 'test']
        with pytest.raises(ValueError, match="Unhandled OpenAI response format"):
            await embeddings.aembed_documents(texts)

    @pytest.mark.asyncio
    async def test_mixed_batch_sizes_with_list_responses(self):
        """Test that different batch sizes work with list responses."""
        
        # Create a mock client that tracks batches
        class MockBatchTrackingClient:
            def __init__(self):
                self.call_count = 0
                
            async def create(self, input, **kwargs):
                self.call_count += 1
                # Return embeddings matching the input size in proper OpenAI format
                class MockResponse:
                    def __init__(self, data):
                        self.data = data
                
                return MockResponse([
                    Mock(embedding=[0.1 * i, 0.2 * i, 0.3 * i])
                    for i in range(1, len(input) + 1)
                ])
        
        # Create SafeOpenAIEmbeddings instance with small batch size
        embeddings = SafeOpenAIEmbeddings(
            api_key='test-key',
            model='text-embedding-ada-002',
            chunk_size=2  # Force batching
        )
        
        mock_client = MockBatchTrackingClient()
        embeddings.async_client = mock_client
        
        # Test with 5 texts (should be 3 batches: 2, 2, 1)
        texts = ['text1', 'text2', 'text3', 'text4', 'text5']
        result = await embeddings.aembed_documents(texts)
        
        # Verify results
        assert len(result) == 5
        # The actual number of batches may vary based on LangChain's internal logic
        # What's important is that we got the right number of results
        assert mock_client.call_count >= 3  # At least 3 batches
        assert all(isinstance(emb, list) for emb in result)
        assert all(len(emb) == 3 for emb in result)