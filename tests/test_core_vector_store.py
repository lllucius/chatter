"""Tests for vector store core functionality."""

import asyncio
from unittest.mock import patch, MagicMock

import pytest

from chatter.core.vector_store import VectorSearchResult, VectorStore


@pytest.mark.unit
class TestVectorStore:
    """Test vector store core functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Use a mock since VectorStore is abstract
        self.vector_store = MagicMock(spec=VectorStore)

        # Sample vectors and documents
        self.sample_vectors = [
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
            [0.9, 0.1, 0.2, 0.3]
        ]

        self.sample_documents = [
            {
                "id": "doc-1",
                "content": "This is the first document about AI.",
                "metadata": {"category": "technology", "source": "web"}
            },
            {
                "id": "doc-2",
                "content": "Second document discusses machine learning.",
                "metadata": {"category": "technology", "source": "paper"}
            },
            {
                "id": "doc-3",
                "content": "Third document covers data science topics.",
                "metadata": {"category": "science", "source": "book"}
            }
        ]

    @pytest.mark.asyncio
    async def test_add_vectors_success(self):
        """Test successful vector addition."""
        # Arrange
        vectors = self.sample_vectors
        documents = self.sample_documents

        with patch.object(self.vector_store, '_validate_vectors') as mock_validate:
            mock_validate.return_value = True

            with patch.object(self.vector_store, '_store_vectors') as mock_store:
                mock_store.return_value = ["vec-1", "vec-2", "vec-3"]

                # Act
                result = await self.vector_store.add_vectors(vectors, documents)

                # Assert
                assert len(result) == 3
                assert all(id.startswith("vec-") for id in result)
                mock_validate.assert_called_once_with(vectors)
                mock_store.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_vectors_dimension_mismatch(self):
        """Test vector addition with dimension mismatch."""
        # Arrange
        mismatched_vectors = [
            [0.1, 0.2, 0.3],  # 3 dimensions
            [0.5, 0.6, 0.7, 0.8]  # 4 dimensions
        ]
        documents = self.sample_documents[:2]

        with patch.object(self.vector_store, '_validate_vectors') as mock_validate:
            mock_validate.side_effect = ValueError("Vector dimensions must be consistent")

            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                await self.vector_store.add_vectors(mismatched_vectors, documents)

            assert "dimensions must be consistent" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_vectors_success(self):
        """Test successful vector search."""
        # Arrange
        query_vector = [0.1, 0.2, 0.3, 0.4]
        k = 2

        expected_results = [
            VectorSearchResult(
                id="doc-1",
                score=0.95,
                document=self.sample_documents[0],
                vector=self.sample_vectors[0]
            ),
            VectorSearchResult(
                id="doc-2",
                score=0.87,
                document=self.sample_documents[1],
                vector=self.sample_vectors[1]
            )
        ]

        with patch.object(self.vector_store, '_perform_similarity_search') as mock_search:
            mock_search.return_value = expected_results

            # Act
            results = await self.vector_store.search_vectors(query_vector, k=k)

            # Assert
            assert len(results) == 2
            assert results[0].score >= results[1].score  # Results should be sorted by score
            assert results[0].id == "doc-1"
            mock_search.assert_called_once_with(query_vector, k, None)

    @pytest.mark.asyncio
    async def test_search_vectors_with_filter(self):
        """Test vector search with metadata filter."""
        # Arrange
        query_vector = [0.1, 0.2, 0.3, 0.4]
        filter_criteria = {"category": "technology"}
        k = 5

        expected_results = [
            VectorSearchResult(
                id="doc-1",
                score=0.95,
                document=self.sample_documents[0],
                vector=self.sample_vectors[0]
            ),
            VectorSearchResult(
                id="doc-2",
                score=0.87,
                document=self.sample_documents[1],
                vector=self.sample_vectors[1]
            )
        ]

        with patch.object(self.vector_store, '_perform_similarity_search') as mock_search:
            mock_search.return_value = expected_results

            # Act
            results = await self.vector_store.search_vectors(
                query_vector, k=k, filter=filter_criteria
            )

            # Assert
            assert len(results) == 2
            # All results should match the filter
            for result in results:
                assert result.document["metadata"]["category"] == "technology"
            mock_search.assert_called_once_with(query_vector, k, filter_criteria)

    @pytest.mark.asyncio
    async def test_search_vectors_empty_results(self):
        """Test vector search with no matching results."""
        # Arrange
        query_vector = [0.1, 0.2, 0.3, 0.4]

        with patch.object(self.vector_store, '_perform_similarity_search') as mock_search:
            mock_search.return_value = []

            # Act
            results = await self.vector_store.search_vectors(query_vector, k=5)

            # Assert
            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_update_vector_success(self):
        """Test successful vector update."""
        # Arrange
        vector_id = "doc-1"
        new_vector = [0.2, 0.3, 0.4, 0.5]
        new_document = {
            "id": vector_id,
            "content": "Updated document content about AI.",
            "metadata": {"category": "technology", "updated": True}
        }

        with patch.object(self.vector_store, '_check_vector_exists') as mock_check:
            mock_check.return_value = True

            with patch.object(self.vector_store, '_update_vector_record') as mock_update:
                mock_update.return_value = True

                # Act
                result = await self.vector_store.update_vector(
                    vector_id, new_vector, new_document
                )

                # Assert
                assert result is True
                mock_check.assert_called_once_with(vector_id)
                mock_update.assert_called_once_with(vector_id, new_vector, new_document)

    @pytest.mark.asyncio
    async def test_update_vector_not_found(self):
        """Test vector update when vector doesn't exist."""
        # Arrange
        vector_id = "non-existent-id"
        new_vector = [0.2, 0.3, 0.4, 0.5]
        new_document = {"id": vector_id, "content": "New content"}

        with patch.object(self.vector_store, '_check_vector_exists') as mock_check:
            mock_check.return_value = False

            # Act & Assert
            from chatter.core.exceptions import NotFoundError
            with pytest.raises(NotFoundError) as exc_info:
                await self.vector_store.update_vector(vector_id, new_vector, new_document)

            assert "Vector not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_vector_success(self):
        """Test successful vector deletion."""
        # Arrange
        vector_id = "doc-1"

        with patch.object(self.vector_store, '_check_vector_exists') as mock_check:
            mock_check.return_value = True

            with patch.object(self.vector_store, '_delete_vector_record') as mock_delete:
                mock_delete.return_value = True

                # Act
                result = await self.vector_store.delete_vector(vector_id)

                # Assert
                assert result is True
                mock_check.assert_called_once_with(vector_id)
                mock_delete.assert_called_once_with(vector_id)

    @pytest.mark.asyncio
    async def test_delete_vector_not_found(self):
        """Test vector deletion when vector doesn't exist."""
        # Arrange
        vector_id = "non-existent-id"

        with patch.object(self.vector_store, '_check_vector_exists') as mock_check:
            mock_check.return_value = False

            # Act & Assert
            from chatter.core.exceptions import NotFoundError
            with pytest.raises(NotFoundError) as exc_info:
                await self.vector_store.delete_vector(vector_id)

            assert "Vector not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_vector_by_id_success(self):
        """Test successful vector retrieval by ID."""
        # Arrange
        vector_id = "doc-1"
        expected_vector = self.sample_vectors[0]
        expected_document = self.sample_documents[0]

        with patch.object(self.vector_store, '_fetch_vector_by_id') as mock_fetch:
            mock_fetch.return_value = (expected_vector, expected_document)

            # Act
            vector, document = await self.vector_store.get_vector_by_id(vector_id)

            # Assert
            assert vector == expected_vector
            assert document == expected_document
            mock_fetch.assert_called_once_with(vector_id)

    @pytest.mark.asyncio
    async def test_get_vector_by_id_not_found(self):
        """Test vector retrieval when vector doesn't exist."""
        # Arrange
        vector_id = "non-existent-id"

        with patch.object(self.vector_store, '_fetch_vector_by_id') as mock_fetch:
            mock_fetch.return_value = (None, None)

            # Act & Assert
            from chatter.core.exceptions import NotFoundError
            with pytest.raises(NotFoundError) as exc_info:
                await self.vector_store.get_vector_by_id(vector_id)

            assert "Vector not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_bulk_operations_success(self):
        """Test bulk vector operations."""
        # Arrange
        vectors = self.sample_vectors
        documents = self.sample_documents

        with patch.object(self.vector_store, '_bulk_insert_vectors') as mock_bulk:
            mock_bulk.return_value = ["vec-1", "vec-2", "vec-3"]

            # Act
            result = await self.vector_store.bulk_add_vectors(vectors, documents)

            # Assert
            assert len(result) == 3
            mock_bulk.assert_called_once_with(vectors, documents)

    @pytest.mark.asyncio
    async def test_similarity_threshold_filtering(self):
        """Test filtering results by similarity threshold."""
        # Arrange
        query_vector = [0.1, 0.2, 0.3, 0.4]
        threshold = 0.9

        # Mock results with varying scores
        mock_results = [
            VectorSearchResult(
                id="doc-1", score=0.95, document=self.sample_documents[0], vector=self.sample_vectors[0]
            ),
            VectorSearchResult(
                id="doc-2", score=0.85, document=self.sample_documents[1], vector=self.sample_vectors[1]
            ),
            VectorSearchResult(
                id="doc-3", score=0.92, document=self.sample_documents[2], vector=self.sample_vectors[2]
            )
        ]

        with patch.object(self.vector_store, '_perform_similarity_search') as mock_search:
            mock_search.return_value = mock_results

            # Act
            results = await self.vector_store.search_vectors(
                query_vector, k=5, similarity_threshold=threshold
            )

            # Assert
            # Only results with score >= 0.9 should be returned
            assert len(results) == 2
            assert all(result.score >= threshold for result in results)

    @pytest.mark.asyncio
    async def test_vector_dimension_consistency(self):
        """Test vector dimension consistency checking."""
        # Arrange
        new_vector = [0.5, 0.6, 0.7]  # 3 dimensions (mismatch)

        with patch.object(self.vector_store, '_get_vector_dimension') as mock_get_dim:
            mock_get_dim.return_value = 4

            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                await self.vector_store._validate_vector_dimension(new_vector)

            assert "dimension mismatch" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_index_optimization(self):
        """Test vector index optimization."""
        # Arrange
        with patch.object(self.vector_store, '_rebuild_index') as mock_rebuild:
            mock_rebuild.return_value = True

            with patch.object(self.vector_store, '_get_index_stats') as mock_stats:
                mock_stats.return_value = {
                    "total_vectors": 1000,
                    "index_size": "50MB",
                    "last_optimized": "2024-01-01T00:00:00Z"
                }

                # Act
                result = await self.vector_store.optimize_index()

                # Assert
                assert result is True
                mock_rebuild.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent vector store operations."""
        # Arrange
        vectors_batch1 = self.sample_vectors[:2]
        vectors_batch2 = [self.sample_vectors[2]]
        documents_batch1 = self.sample_documents[:2]
        documents_batch2 = [self.sample_documents[2]]

        with patch.object(self.vector_store, '_store_vectors') as mock_store:
            mock_store.side_effect = [
                ["vec-1", "vec-2"],
                ["vec-3"]
            ]

            # Act
            tasks = [
                self.vector_store.add_vectors(vectors_batch1, documents_batch1),
                self.vector_store.add_vectors(vectors_batch2, documents_batch2)
            ]

            results = await asyncio.gather(*tasks)

            # Assert
            assert len(results) == 2
            assert len(results[0]) == 2
            assert len(results[1]) == 1


@pytest.mark.integration
class TestVectorStoreIntegration:
    """Integration tests for vector store."""

    def setup_method(self):
        """Set up test fixtures."""
        self.vector_store = MagicMock(spec=VectorStore)

    @pytest.mark.asyncio
    async def test_end_to_end_vector_lifecycle(self):
        """Test complete vector lifecycle."""
        # Mock all the required backend operations
        vectors = [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]
        documents = [
            {"id": "doc-1", "content": "First document", "metadata": {"type": "test"}},
            {"id": "doc-2", "content": "Second document", "metadata": {"type": "test"}}
        ]

        with patch.object(self.vector_store, '_validate_vectors') as mock_validate:
            mock_validate.return_value = True

            with patch.object(self.vector_store, '_store_vectors') as mock_store:
                mock_store.return_value = ["vec-1", "vec-2"]

                # Add vectors
                vector_ids = await self.vector_store.add_vectors(vectors, documents)
                assert len(vector_ids) == 2

                # Mock search operation
                with patch.object(self.vector_store, '_perform_similarity_search') as mock_search:
                    search_results = [
                        VectorSearchResult(
                            id="vec-1", score=0.95, document=documents[0], vector=vectors[0]
                        )
                    ]
                    mock_search.return_value = search_results

                    # Search vectors
                    query_vector = [0.1, 0.2, 0.3, 0.4]
                    results = await self.vector_store.search_vectors(query_vector, k=1)
                    assert len(results) == 1
                    assert results[0].score == 0.95

                    # Mock update operation
                    with patch.object(self.vector_store, '_check_vector_exists') as mock_check:
                        mock_check.return_value = True

                        with patch.object(self.vector_store, '_update_vector_record') as mock_update:
                            mock_update.return_value = True

                            # Update vector
                            new_vector = [0.2, 0.3, 0.4, 0.5]
                            new_document = {"id": "doc-1", "content": "Updated content"}

                            updated = await self.vector_store.update_vector(
                                "vec-1", new_vector, new_document
                            )
                            assert updated is True

                            # Mock delete operation
                            with patch.object(self.vector_store, '_delete_vector_record') as mock_delete:
                                mock_delete.return_value = True

                                # Delete vector
                                deleted = await self.vector_store.delete_vector("vec-1")
                                assert deleted is True

    @pytest.mark.asyncio
    async def test_large_scale_operations(self):
        """Test vector store with large number of vectors."""
        # Simulate large batch operations
        num_vectors = 1000
        vectors = [[i/1000, (i+1)/1000, (i+2)/1000, (i+3)/1000] for i in range(num_vectors)]
        documents = [
            {"id": f"doc-{i}", "content": f"Document {i}", "metadata": {"batch": "large"}}
            for i in range(num_vectors)
        ]

        with patch.object(self.vector_store, '_bulk_insert_vectors') as mock_bulk:
            vector_ids = [f"vec-{i}" for i in range(num_vectors)]
            mock_bulk.return_value = vector_ids

            # Act
            result = await self.vector_store.bulk_add_vectors(vectors, documents)

            # Assert
            assert len(result) == num_vectors
            mock_bulk.assert_called_once()


@pytest.mark.unit
class TestVectorStoreHelpers:
    """Test vector store helper methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.vector_store = MagicMock(spec=VectorStore)

    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation."""
        # Arrange
        vector1 = [1.0, 0.0, 0.0]
        vector2 = [0.0, 1.0, 0.0]
        vector3 = [1.0, 0.0, 0.0]  # Same as vector1

        # Act
        similarity_different = self.vector_store._calculate_cosine_similarity(vector1, vector2)
        similarity_same = self.vector_store._calculate_cosine_similarity(vector1, vector3)

        # Assert
        assert abs(similarity_different - 0.0) < 1e-6  # Orthogonal vectors
        assert abs(similarity_same - 1.0) < 1e-6      # Identical vectors

    def test_euclidean_distance_calculation(self):
        """Test Euclidean distance calculation."""
        # Arrange
        vector1 = [0.0, 0.0, 0.0]
        vector2 = [3.0, 4.0, 0.0]

        # Act
        distance = self.vector_store._calculate_euclidean_distance(vector1, vector2)

        # Assert
        assert abs(distance - 5.0) < 1e-6  # 3-4-5 triangle

    def test_vector_normalization(self):
        """Test vector normalization."""
        # Arrange
        vector = [3.0, 4.0, 0.0]

        # Act
        normalized = self.vector_store._normalize_vector(vector)

        # Assert
        # Normalized vector should have magnitude 1
        magnitude = sum(x**2 for x in normalized) ** 0.5
        assert abs(magnitude - 1.0) < 1e-6

    def test_metadata_filtering(self):
        """Test metadata filtering logic."""
        # Arrange
        documents = [
            {"metadata": {"category": "tech", "year": 2023}},
            {"metadata": {"category": "science", "year": 2023}},
            {"metadata": {"category": "tech", "year": 2024}}
        ]

        filter_criteria = {"category": "tech"}

        # Act
        filtered = self.vector_store._apply_metadata_filter(documents, filter_criteria)

        # Assert
        assert len(filtered) == 2
        for doc in filtered:
            assert doc["metadata"]["category"] == "tech"

    def test_batch_processing(self):
        """Test batch processing utilities."""
        # Arrange
        data = list(range(100))
        batch_size = 10

        # Act
        batches = list(self.vector_store._create_batches(data, batch_size))

        # Assert
        assert len(batches) == 10
        assert all(len(batch) == batch_size for batch in batches)
        assert sum(len(batch) for batch in batches) == len(data)
