"""Test for document retrieval fix."""
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from chatter.core.custom_retriever import DocumentChunkRetriever


@pytest.mark.asyncio
async def test_document_chunk_retriever_basic():
    """Test that DocumentChunkRetriever can be created."""
    # Mock embeddings
    mock_embeddings = AsyncMock()
    mock_embeddings.aembed_query = AsyncMock(return_value=[0.1] * 768)
    
    # Create retriever
    retriever = DocumentChunkRetriever(
        embeddings=mock_embeddings,
        user_id="test_user",
        document_ids=["doc1", "doc2"],
        k=5,
    )
    
    # Check initialization
    assert retriever.embeddings == mock_embeddings
    assert retriever.user_id == "test_user"
    assert retriever.document_ids == ["doc1", "doc2"]
    assert retriever.k == 5


@pytest.mark.asyncio
async def test_document_chunk_retriever_ainvoke():
    """Test that DocumentChunkRetriever.ainvoke works."""
    # Mock embeddings
    mock_embeddings = AsyncMock()
    query_embedding = [0.1] * 768
    mock_embeddings.aembed_query = AsyncMock(return_value=query_embedding)
    
    # Mock DocumentChunk
    mock_chunk = Mock()
    mock_chunk.content = "Test document content"
    mock_chunk.document_id = "doc1"
    mock_chunk.chunk_index = 0
    
    # Mock SimpleVectorStore
    mock_vector_store = AsyncMock()
    mock_vector_store.search_similar = AsyncMock(
        return_value=[(mock_chunk, 0.95)]
    )
    
    # Mock get_async_session
    async def mock_session_generator():
        yield AsyncMock()
    
    with patch(
        'chatter.core.custom_retriever.get_async_session',
        return_value=mock_session_generator()
    ), patch(
        'chatter.core.custom_retriever.SimpleVectorStore',
        return_value=mock_vector_store
    ):
        # Create retriever
        retriever = DocumentChunkRetriever(
            embeddings=mock_embeddings,
            user_id="test_user",
            document_ids=["doc1"],
            k=5,
        )
        
        # Call ainvoke
        results = await retriever.ainvoke("test query")
        
        # Check results
        assert len(results) == 1
        assert results[0].page_content == "Test document content"
        assert results[0].metadata["document_id"] == "doc1"
        assert results[0].metadata["chunk_index"] == 0
        assert results[0].metadata["score"] == 0.95
        
        # Check that embedding was created
        mock_embeddings.aembed_query.assert_called_once_with("test query")
        
        # Check that vector store was called
        mock_vector_store.search_similar.assert_called_once_with(
            query_embedding=query_embedding,
            limit=5,
            document_ids=["doc1"],
            prefer_exact_match=True,
        )


@pytest.mark.asyncio
async def test_document_chunk_retriever_handles_errors():
    """Test that DocumentChunkRetriever handles errors gracefully."""
    # Mock embeddings that raises an error
    mock_embeddings = AsyncMock()
    mock_embeddings.aembed_query = AsyncMock(
        side_effect=Exception("Embedding failed")
    )
    
    # Create retriever
    retriever = DocumentChunkRetriever(
        embeddings=mock_embeddings,
        user_id="test_user",
        k=5,
    )
    
    # Call ainvoke - should return empty list on error
    results = await retriever.ainvoke("test query")
    
    # Check that error was handled
    assert results == []
