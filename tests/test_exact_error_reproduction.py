"""Test to specifically reproduce the exact error from the logs."""

import pytest
from unittest.mock import Mock, AsyncMock
import logging

from chatter.services.embeddings import SafeOpenAIEmbeddings

# Set up logging to see debug output
logging.basicConfig(level=logging.DEBUG)


class TestExactErrorReproduction:
    """Test that reproduces the exact error scenario from the problem statement."""

    @pytest.mark.asyncio
    async def test_exact_error_list_object_has_no_attribute_data(self):
        """Test the exact scenario: 'list' object has no attribute 'data'."""
        
        # Create a mock client that simulates the exact problematic response
        # that causes "'list' object has no attribute 'data'"
        class MockProblematicListClient:
            async def create(self, input, **kwargs):
                # Return a list directly - this is what causes the original error
                # when LangChain code tries to access .data attribute on a list
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
        embeddings.async_client = MockProblematicListClient()
        
        # This should trigger the fallback and handle the error gracefully
        texts = ['hello', 'world', 'test']  # 3 texts, matching the original log
        
        # This should work without the "'list' object has no attribute 'data'" error
        result = await embeddings.aembed_documents(texts)
        
        # Verify we got the correct results
        assert len(result) == 3
        assert all(isinstance(emb, list) for emb in result)
        assert all(len(emb) == 3 for emb in result)
        assert result[0] == [0.1, 0.2, 0.3]
        assert result[1] == [0.4, 0.5, 0.6]
        assert result[2] == [0.7, 0.8, 0.9]

    @pytest.mark.asyncio 
    async def test_exact_error_with_single_query(self):
        """Test the exact scenario with aembed_query."""
        
        class MockProblematicListClient:
            async def create(self, input, **kwargs):
                # Return a list for single input
                return [{"embedding": [0.1, 0.2, 0.3]}]
        
        # Create SafeOpenAIEmbeddings instance
        embeddings = SafeOpenAIEmbeddings(
            api_key='test-key',
            model='text-embedding-ada-002'
        )
        
        # Replace client with the problematic one
        embeddings.async_client = MockProblematicListClient()
        
        # This should work without the error
        result = await embeddings.aembed_query("test query")
        
        # Verify we got the correct result
        assert isinstance(result, list)
        assert len(result) == 3
        assert result == [0.1, 0.2, 0.3]

    @pytest.mark.asyncio
    async def test_batch_size_3_exact_match_to_logs(self):
        """Test with batch size 3 to exactly match the original error logs."""
        
        class MockBatchSizeThreeClient:
            def __init__(self):
                self.call_count = 0
                
            async def create(self, input, **kwargs):
                self.call_count += 1
                # Ensure we get exactly 3 inputs like in the logs
                assert len(input) == 3, f"Expected 3 inputs, got {len(input)}"
                
                # Return list format that causes the original issue
                return [
                    {"embedding": [0.1 * i, 0.2 * i, 0.3 * i]}
                    for i in range(1, len(input) + 1)
                ]
        
        # Create SafeOpenAIEmbeddings instance
        embeddings = SafeOpenAIEmbeddings(
            api_key='test-key',
            model='text-embedding-ada-002'
        )
        
        mock_client = MockBatchSizeThreeClient()
        embeddings.async_client = mock_client
        
        # Use exactly 3 texts as in the original error log: text_count=3
        texts = ['first text', 'second text', 'third text']
        
        # This should work without the "'list' object has no attribute 'data'" error
        result = await embeddings.aembed_documents(texts)
        
        # Verify results
        assert len(result) == 3
        # LangChain may use different batching logic, so just ensure we get reasonable results
        assert mock_client.call_count >= 1  # At least one call was made
        assert all(isinstance(emb, list) for emb in result)
        assert all(len(emb) == 3 for emb in result)