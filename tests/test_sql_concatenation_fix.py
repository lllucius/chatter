"""Test for the SQL concatenation fix in PGVector initialization."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from chatter.core.vector_store import PGVectorStore


class TestPGVectorSQLConcatenationFix:
    """Test that the SQL concatenation fix works correctly."""

    @pytest.mark.asyncio
    async def test_pgvector_initialization_prevents_sql_concatenation(self):
        """Test that PGVector is initialized with create_extension=False to prevent SQL concatenation issues."""
        
        # Mock the PGVector class to verify it's called with correct parameters
        with patch('chatter.core.vector_store.PGVector') as mock_pgvector:
            # Mock the PGVector instance
            mock_instance = MagicMock()
            mock_pgvector.return_value = mock_instance
            
            # Mock embeddings
            mock_embeddings = MagicMock()
            
            # Create the vector store
            store = PGVectorStore(
                embeddings=mock_embeddings,
                collection_name="test_collection",
                connection_string="postgresql+asyncpg://test:test@localhost:5432/test"
            )
            
            # Verify PGVector was called with create_extension=False
            mock_pgvector.assert_called_once()
            call_args = mock_pgvector.call_args
            
            # Check that create_extension=False was passed
            assert 'create_extension' in call_args.kwargs, "create_extension parameter should be present"
            assert call_args.kwargs['create_extension'] is False, "create_extension should be False to prevent SQL concatenation"
            
            # Verify other expected parameters
            assert call_args.kwargs['async_mode'] is True, "async_mode should be True"
            assert call_args.kwargs['use_jsonb'] is True, "use_jsonb should be True"
            assert call_args.kwargs['collection_name'] == "test_collection"

    @pytest.mark.asyncio 
    async def test_pgvector_store_initialization_with_extension_disabled(self):
        """Test that the vector store can be initialized without extension creation."""
        
        with patch('chatter.core.vector_store.PGVector') as mock_pgvector:
            mock_instance = MagicMock()
            mock_pgvector.return_value = mock_instance
            
            mock_embeddings = MagicMock()
            
            # This should not raise any exceptions
            store = PGVectorStore(
                embeddings=mock_embeddings,
                collection_name="test_docs", 
                connection_string="postgresql+asyncpg://user:pass@localhost:5432/db"
            )
            
            # Verify the store was created successfully
            assert store._store == mock_instance
            assert store.collection_name == "test_docs"
            
            # Verify PGVector was initialized with create_extension=False
            call_kwargs = mock_pgvector.call_args.kwargs
            assert call_kwargs['create_extension'] is False