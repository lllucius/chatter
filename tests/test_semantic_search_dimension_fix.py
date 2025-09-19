"""
Test for semantic search dimension mismatch fix.

This test validates the fix for the issue where hybrid vector search
fails with dimension mismatches when falling back from raw_embedding
to computed_embedding searches.
"""

import pytest
from chatter.models.document import HybridVectorSearchHelper, normalize_embedding_to_fixed_dim


class TestSemanticSearchDimensionFix:
    """Test the semantic search dimension mismatch fix."""

    def test_hybrid_search_helper_dimension_choices(self):
        """Test that the hybrid search helper chooses correct columns for different dimensions."""
        
        # Test 1536-dimension query (should use embedding)
        query_1536 = [0.1] * 1536
        column_1536 = HybridVectorSearchHelper.choose_search_column(query_1536, prefer_exact_match=True)
        assert column_1536 == 'embedding'
        
        # Test 3072-dimension query (should use raw_embedding for exact match)
        query_3072 = [0.1] * 3072
        column_3072 = HybridVectorSearchHelper.choose_search_column(query_3072, prefer_exact_match=True)
        assert column_3072 == 'raw_embedding'
        
        # Test 768-dimension query (should use raw_embedding for exact match)
        query_768 = [0.1] * 768
        column_768 = HybridVectorSearchHelper.choose_search_column(query_768, prefer_exact_match=True)
        assert column_768 == 'raw_embedding'
        
        # Test prefer_exact_match=False (should use computed_embedding for non-1536 queries)
        column_no_exact = HybridVectorSearchHelper.choose_search_column(query_3072, prefer_exact_match=False)
        assert column_no_exact == 'computed_embedding'

    def test_query_vector_preparation(self):
        """Test that query vectors are prepared correctly for different target columns."""
        
        query_3072 = [0.1] * 3072
        query_768 = [0.1] * 768
        query_1536 = [0.1] * 1536
        
        # Raw embedding should preserve original dimensions
        prepared_raw_3072 = HybridVectorSearchHelper.prepare_query_vector(query_3072, 'raw_embedding')
        assert len(prepared_raw_3072) == 3072
        assert prepared_raw_3072 == query_3072
        
        prepared_raw_768 = HybridVectorSearchHelper.prepare_query_vector(query_768, 'raw_embedding')
        assert len(prepared_raw_768) == 768
        assert prepared_raw_768 == query_768
        
        # Embedding and computed_embedding should normalize to 1536
        prepared_emb_3072 = HybridVectorSearchHelper.prepare_query_vector(query_3072, 'embedding')
        assert len(prepared_emb_3072) == 1536
        
        prepared_comp_3072 = HybridVectorSearchHelper.prepare_query_vector(query_3072, 'computed_embedding')
        assert len(prepared_comp_3072) == 1536
        
        prepared_comp_768 = HybridVectorSearchHelper.prepare_query_vector(query_768, 'computed_embedding')
        assert len(prepared_comp_768) == 1536
        
        # 1536-dimension queries should pass through unchanged for embedding columns
        prepared_emb_1536 = HybridVectorSearchHelper.prepare_query_vector(query_1536, 'embedding')
        assert len(prepared_emb_1536) == 1536
        assert prepared_emb_1536 == query_1536

    def test_fallback_scenario_fix(self):
        """Test the specific scenario that was failing: 3072-dim query falling back to computed_embedding."""
        
        # This tests the exact scenario from the error log
        query_embedding = [0.1] * 3072  # 3072-dimension query like in the error
        
        # Step 1: Initial column choice with prefer_exact_match=True
        search_column = HybridVectorSearchHelper.choose_search_column(
            query_embedding, prefer_exact_match=True
        )
        assert search_column == 'raw_embedding'
        
        # Step 2: Prepare query for raw_embedding (original behavior)
        prepared_for_raw = HybridVectorSearchHelper.prepare_query_vector(
            query_embedding, search_column
        )
        assert len(prepared_for_raw) == 3072
        
        # Step 3: Fallback to computed_embedding (the fix)
        # When raw_embedding search fails, we need to re-prepare for computed_embedding
        prepared_for_computed = HybridVectorSearchHelper.prepare_query_vector(
            query_embedding, 'computed_embedding'
        )
        assert len(prepared_for_computed) == 1536
        
        # This should resolve the "expected 1536 dimensions, not 3072" error
        # because we're now using a 1536-dimension vector for computed_embedding search

    def test_normalize_embedding_to_fixed_dim(self):
        """Test the underlying normalization function handles edge cases correctly."""
        
        # Test truncation (larger than target)
        large_embedding = list(range(3072))  # [0, 1, 2, ..., 3071]
        truncated = normalize_embedding_to_fixed_dim(large_embedding, 1536)
        assert len(truncated) == 1536
        assert truncated == list(range(1536))  # [0, 1, 2, ..., 1535]
        
        # Test padding (smaller than target)
        small_embedding = list(range(768))  # [0, 1, 2, ..., 767]
        padded = normalize_embedding_to_fixed_dim(small_embedding, 1536)
        assert len(padded) == 1536
        assert padded[:768] == list(range(768))  # Original values preserved
        assert padded[768:] == [0.0] * 768  # Padded with zeros
        
        # Test exact match (same as target)
        exact_embedding = list(range(1536))  # [0, 1, 2, ..., 1535]
        unchanged = normalize_embedding_to_fixed_dim(exact_embedding, 1536)
        assert len(unchanged) == 1536
        assert unchanged == exact_embedding
        assert unchanged is not exact_embedding  # Should be a copy
        
        # Test empty embedding
        empty_normalized = normalize_embedding_to_fixed_dim([], 1536)
        assert len(empty_normalized) == 1536
        assert empty_normalized == [0.0] * 1536
        
        # Test with different target dimension
        custom_target = normalize_embedding_to_fixed_dim([1, 2, 3], 5)
        assert len(custom_target) == 5
        assert custom_target == [1, 2, 3, 0.0, 0.0]

    def test_dimension_consistency_across_operations(self):
        """Test that dimension handling is consistent across all operations."""
        
        test_cases = [
            ([0.1] * 768, 'Anthropic/Google models'),
            ([0.1] * 1024, 'Cohere models'),
            ([0.1] * 1536, 'OpenAI models'),
            ([0.1] * 3072, 'OpenAI large models'),
            ([0.1] * 4096, 'Mistral models'),
        ]
        
        for query_vector, description in test_cases:
            # Test raw_embedding path
            raw_column = HybridVectorSearchHelper.choose_search_column(
                query_vector, prefer_exact_match=True
            )
            raw_prepared = HybridVectorSearchHelper.prepare_query_vector(
                query_vector, raw_column
            )
            
            # Test computed_embedding fallback path
            computed_prepared = HybridVectorSearchHelper.prepare_query_vector(
                query_vector, 'computed_embedding'
            )
            
            # Assertions
            if len(query_vector) == 1536:
                assert raw_column == 'embedding'
                assert len(raw_prepared) == 1536
            else:
                assert raw_column == 'raw_embedding'
                assert len(raw_prepared) == len(query_vector)
            
            # Computed embedding should always be 1536 dimensions
            assert len(computed_prepared) == 1536
            
            print(f"✓ {description}: {len(query_vector)} -> raw:{len(raw_prepared)}, computed:{len(computed_prepared)}")