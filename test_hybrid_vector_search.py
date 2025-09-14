"""Test for hybrid vector search implementation.

This tests the new hybrid vector search functionality with multiple embedding dimensions.
"""

import asyncio
import tempfile
from pathlib import Path
import numpy as np

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from chatter.models.document import (
    DocumentChunk, 
    HybridVectorSearchHelper,
    normalize_embedding_to_fixed_dim
)


class TestHybridVectorSearch:
    """Test the hybrid vector search functionality."""
    
    def test_normalize_embedding_to_fixed_dim_same_size(self):
        """Test normalization when embedding is already the target size."""
        # Test with 1536-dimensional vector
        original = [0.1] * 1536
        normalized = normalize_embedding_to_fixed_dim(original, 1536)
        
        assert len(normalized) == 1536
        assert normalized == original
    
    def test_normalize_embedding_to_fixed_dim_padding(self):
        """Test normalization when embedding needs padding."""
        # Test with smaller vector
        original = [0.1, 0.2, 0.3]
        normalized = normalize_embedding_to_fixed_dim(original, 10)
        
        assert len(normalized) == 10
        assert normalized[:3] == [0.1, 0.2, 0.3]
        assert normalized[3:] == [0.0] * 7
    
    def test_normalize_embedding_to_fixed_dim_truncation(self):
        """Test normalization when embedding needs truncation."""
        # Test with larger vector
        original = [0.1] * 2000
        normalized = normalize_embedding_to_fixed_dim(original, 1536)
        
        assert len(normalized) == 1536
        assert normalized == [0.1] * 1536
    
    def test_normalize_embedding_empty(self):
        """Test normalization with empty embedding."""
        normalized = normalize_embedding_to_fixed_dim([], 1536)
        
        assert len(normalized) == 1536
        assert normalized == [0.0] * 1536


class TestHybridVectorSearchHelper:
    """Test the hybrid vector search helper."""
    
    def test_choose_search_column_exact_match(self):
        """Test column selection for exact 1536-dimensional match."""
        query_vector = [0.1] * 1536
        column = HybridVectorSearchHelper.choose_search_column(query_vector)
        
        assert column == 'embedding'
    
    def test_choose_search_column_prefer_exact(self):
        """Test column selection for non-1536 dimensions with exact match preference."""
        query_vector = [0.1] * 768  # Different dimension
        column = HybridVectorSearchHelper.choose_search_column(query_vector, prefer_exact_match=True)
        
        assert column == 'raw_embedding'
    
    def test_choose_search_column_computed(self):
        """Test column selection for non-1536 dimensions without exact match preference."""
        query_vector = [0.1] * 768
        column = HybridVectorSearchHelper.choose_search_column(query_vector, prefer_exact_match=False)
        
        assert column == 'computed_embedding'
    
    def test_prepare_query_vector_embedding_column(self):
        """Test query vector preparation for embedding column."""
        original = [0.1] * 768
        prepared = HybridVectorSearchHelper.prepare_query_vector(original, 'embedding')
        
        assert len(prepared) == 1536
        assert prepared[:768] == original
        assert prepared[768:] == [0.0] * (1536 - 768)
    
    def test_prepare_query_vector_computed_column(self):
        """Test query vector preparation for computed_embedding column."""
        original = [0.1] * 2000
        prepared = HybridVectorSearchHelper.prepare_query_vector(original, 'computed_embedding')
        
        assert len(prepared) == 1536
        assert prepared == [0.1] * 1536
    
    def test_prepare_query_vector_raw_column(self):
        """Test query vector preparation for raw_embedding column."""
        original = [0.1] * 768
        prepared = HybridVectorSearchHelper.prepare_query_vector(original, 'raw_embedding')
        
        assert len(prepared) == 768
        assert prepared == original
    
    def test_build_similarity_filter_exact_dim_only(self):
        """Test filter building for exact dimension matching."""
        query_vector = [0.1] * 768
        filters = HybridVectorSearchHelper.build_similarity_filter(query_vector, exact_dim_only=True)
        
        assert filters == {'raw_dim': 768}
    
    def test_build_similarity_filter_no_exact_dim(self):
        """Test filter building without exact dimension matching."""
        query_vector = [0.1] * 768
        filters = HybridVectorSearchHelper.build_similarity_filter(query_vector, exact_dim_only=False)
        
        assert filters == {}


class TestDocumentChunkHybridMethods:
    """Test the enhanced DocumentChunk methods."""
    
    def test_set_embedding_vector(self):
        """Test setting embedding vector with automatic normalization."""
        chunk = DocumentChunk(
            document_id="test-doc",
            content="Test content",
            chunk_index=0,
            content_hash="abcd1234"
        )
        
        # Test with 768-dimensional vector
        vector_768 = [0.1] * 768
        chunk.set_embedding_vector(vector_768, "openai", "text-embedding-3-small")
        
        assert chunk.raw_embedding == vector_768
        assert chunk.raw_dim == 768
        assert chunk.embedding_provider == "openai"
        assert chunk.embedding_model == "text-embedding-3-small"
        assert chunk.embedding_dimensions == 768
        assert chunk.embedding_created_at is not None
        
        # computed_embedding and embedding should be set by event listeners
        # In a real test with database, these would be populated
    
    def test_get_search_embedding_exact_match(self):
        """Test getting search embedding for exact dimension match."""
        chunk = DocumentChunk(
            document_id="test-doc",
            content="Test content",
            chunk_index=0,
            content_hash="abcd1234"
        )
        
        # Set up embeddings
        chunk.embedding = [0.1] * 1536
        chunk.raw_embedding = [0.2] * 768
        chunk.raw_dim = 768
        chunk.computed_embedding = [0.3] * 1536
        
        # Should return embedding for 1536 dimensions
        result = chunk.get_search_embedding(1536)
        assert result == chunk.embedding
        
        # Should return raw_embedding for 768 dimensions
        result = chunk.get_search_embedding(768)
        assert result == chunk.raw_embedding
        
        # Should return computed_embedding for other dimensions
        result = chunk.get_search_embedding(512)
        assert result == chunk.computed_embedding
    
    def test_has_embedding_for_dimension(self):
        """Test checking if chunk has embedding for specific dimension."""
        chunk = DocumentChunk(
            document_id="test-doc",
            content="Test content",
            chunk_index=0,
            content_hash="abcd1234"
        )
        
        # Set up embeddings
        chunk.embedding = [0.1] * 1536
        chunk.raw_embedding = [0.2] * 768
        chunk.raw_dim = 768
        chunk.computed_embedding = [0.3] * 1536
        
        # Should have embedding for 1536 dimensions
        assert chunk.has_embedding_for_dimension(1536) is True
        
        # Should have embedding for 768 dimensions (raw_dim)
        assert chunk.has_embedding_for_dimension(768) is True
        
        # Should have computed embedding for other dimensions
        assert chunk.has_embedding_for_dimension(512) is True


class TestVectorOperations:
    """Test vector operations and similarity calculations."""
    
    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity with identical vectors."""
        vector1 = np.array([1.0, 2.0, 3.0])
        vector2 = np.array([1.0, 2.0, 3.0])
        
        similarity = np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2)
        )
        
        assert abs(similarity - 1.0) < 1e-6
    
    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity with orthogonal vectors."""
        vector1 = np.array([1.0, 0.0])
        vector2 = np.array([0.0, 1.0])
        
        similarity = np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2)
        )
        
        assert abs(similarity - 0.0) < 1e-6
    
    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity with opposite vectors."""
        vector1 = np.array([1.0, 2.0, 3.0])
        vector2 = np.array([-1.0, -2.0, -3.0])
        
        similarity = np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2)
        )
        
        assert abs(similarity - (-1.0)) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__])