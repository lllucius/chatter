"""Tests for embeddings service functionality."""

from unittest.mock import AsyncMock, patch

import pytest

from chatter.services.embeddings import EmbeddingError, EmbeddingService


@pytest.mark.unit
class TestEmbeddingsService:
    """Test embeddings service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.embeddings_service = EmbeddingService(self.mock_session)

    @pytest.mark.asyncio
    async def test_generate_text_embedding_success(self):
        """Test successful text embedding generation."""
        # Arrange
        text = "This is a test document for embedding generation."
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        with patch.object(
            self.embeddings_service, '_call_embedding_provider'
        ) as mock_provider:
            mock_provider.return_value = expected_embedding

            # Act
            result = (
                await self.embeddings_service.generate_text_embedding(
                    text
                )
            )

            # Assert
            assert result == expected_embedding
            mock_provider.assert_called_once_with(text, model="default")

    @pytest.mark.asyncio
    async def test_generate_text_embedding_custom_model(self):
        """Test text embedding generation with custom model."""
        # Arrange
        text = "Custom model test"
        model = "text-embedding-3-large"
        expected_embedding = [0.1, 0.2, 0.3]

        with patch.object(
            self.embeddings_service, '_call_embedding_provider'
        ) as mock_provider:
            mock_provider.return_value = expected_embedding

            # Act
            result = (
                await self.embeddings_service.generate_text_embedding(
                    text, model=model
                )
            )

            # Assert
            assert result == expected_embedding
            mock_provider.assert_called_once_with(text, model=model)

    @pytest.mark.asyncio
    async def test_generate_batch_embeddings_success(self):
        """Test successful batch embedding generation."""
        # Arrange
        texts = [
            "First document text",
            "Second document text",
            "Third document text",
        ]
        expected_embeddings = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
        ]

        with patch.object(
            self.embeddings_service, '_call_batch_embedding_provider'
        ) as mock_batch:
            mock_batch.return_value = expected_embeddings

            # Act
            result = (
                await self.embeddings_service.generate_batch_embeddings(
                    texts
                )
            )

            # Assert
            assert len(result) == 3
            assert result == expected_embeddings
            mock_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_embedding_with_preprocessing(self):
        """Test embedding generation with text preprocessing."""
        # Arrange
        raw_text = "  This is RAW text with EXTRA spacing!  \n\n"
        expected_processed = "this is raw text with extra spacing!"
        expected_embedding = [0.1, 0.2, 0.3]

        with patch.object(
            self.embeddings_service, '_preprocess_text'
        ) as mock_preprocess:
            mock_preprocess.return_value = expected_processed

            with patch.object(
                self.embeddings_service, '_call_embedding_provider'
            ) as mock_provider:
                mock_provider.return_value = expected_embedding

                # Act
                result = await self.embeddings_service.generate_text_embedding(
                    raw_text, preprocess=True
                )

                # Assert
                assert result == expected_embedding
                mock_preprocess.assert_called_once_with(raw_text)
                mock_provider.assert_called_once_with(
                    expected_processed, model="default"
                )

    @pytest.mark.asyncio
    async def test_calculate_similarity_cosine(self):
        """Test cosine similarity calculation."""
        # Arrange
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0]
        embedding3 = [1.0, 0.0, 0.0]  # Same as embedding1

        # Act
        similarity_different = (
            await self.embeddings_service.calculate_similarity(
                embedding1, embedding2, method="cosine"
            )
        )
        similarity_same = (
            await self.embeddings_service.calculate_similarity(
                embedding1, embedding3, method="cosine"
            )
        )

        # Assert
        assert (
            abs(similarity_different - 0.0) < 1e-6
        )  # Orthogonal vectors
        assert abs(similarity_same - 1.0) < 1e-6  # Identical vectors

    @pytest.mark.asyncio
    async def test_calculate_similarity_euclidean(self):
        """Test Euclidean distance calculation."""
        # Arrange
        embedding1 = [0.0, 0.0, 0.0]
        embedding2 = [3.0, 4.0, 0.0]

        # Act
        distance = await self.embeddings_service.calculate_similarity(
            embedding1, embedding2, method="euclidean"
        )

        # Assert
        assert abs(distance - 5.0) < 1e-6  # 3-4-5 triangle

    @pytest.mark.asyncio
    async def test_find_similar_embeddings(self):
        """Test finding similar embeddings from a collection."""
        # Arrange
        query_embedding = [0.1, 0.2, 0.3]
        candidate_embeddings = [
            {
                "id": "doc-1",
                "embedding": [0.1, 0.2, 0.3],
            },  # Exact match
            {
                "id": "doc-2",
                "embedding": [0.1, 0.2, 0.4],
            },  # Close match
            {"id": "doc-3", "embedding": [0.9, 0.8, 0.7]},  # Different
        ]

        with patch.object(
            self.embeddings_service, 'calculate_similarity'
        ) as mock_similarity:
            mock_similarity.side_effect = [
                1.0,
                0.9,
                0.1,
            ]  # Similarity scores

            # Act
            similar = (
                await self.embeddings_service.find_similar_embeddings(
                    query_embedding, candidate_embeddings, top_k=2
                )
            )

            # Assert
            assert len(similar) == 2
            assert similar[0]["id"] == "doc-1"  # Best match first
            assert similar[1]["id"] == "doc-2"  # Second best

    @pytest.mark.asyncio
    async def test_embedding_dimension_validation(self):
        """Test embedding dimension validation."""
        # Arrange
        valid_embedding = [0.1, 0.2, 0.3, 0.4]  # 4 dimensions
        invalid_embedding = [0.1, 0.2]  # 2 dimensions

        # Act & Assert
        assert (
            await self.embeddings_service.validate_embedding_dimension(
                valid_embedding, expected_dim=4
            )
            is True
        )

        assert (
            await self.embeddings_service.validate_embedding_dimension(
                invalid_embedding, expected_dim=4
            )
            is False
        )

    @pytest.mark.asyncio
    async def test_normalize_embedding(self):
        """Test embedding normalization."""
        # Arrange
        embedding = [3.0, 4.0, 0.0]

        # Act
        normalized = await self.embeddings_service.normalize_embedding(
            embedding
        )

        # Assert
        # Normalized vector should have magnitude 1
        magnitude = sum(x**2 for x in normalized) ** 0.5
        assert abs(magnitude - 1.0) < 1e-6

    @pytest.mark.asyncio
    async def test_embedding_caching(self):
        """Test embedding caching functionality."""
        # Arrange
        text = "This text should be cached"
        expected_embedding = [0.1, 0.2, 0.3]

        with patch.object(
            self.embeddings_service, '_get_cached_embedding'
        ) as mock_get_cache:
            mock_get_cache.return_value = None  # No cache hit

            with patch.object(
                self.embeddings_service, '_call_embedding_provider'
            ) as mock_provider:
                mock_provider.return_value = expected_embedding

                with patch.object(
                    self.embeddings_service, '_cache_embedding'
                ) as mock_set_cache:
                    # Act
                    result = await self.embeddings_service.generate_text_embedding(
                        text, use_cache=True
                    )

                    # Assert
                    assert result == expected_embedding
                    mock_get_cache.assert_called_once()
                    mock_set_cache.assert_called_once_with(
                        text, expected_embedding
                    )

    @pytest.mark.asyncio
    async def test_embedding_cache_hit(self):
        """Test embedding cache hit."""
        # Arrange
        text = "Cached text"
        cached_embedding = [0.5, 0.6, 0.7]

        with patch.object(
            self.embeddings_service, '_get_cached_embedding'
        ) as mock_get_cache:
            mock_get_cache.return_value = cached_embedding

            with patch.object(
                self.embeddings_service, '_call_embedding_provider'
            ) as mock_provider:
                # Act
                result = await self.embeddings_service.generate_text_embedding(
                    text, use_cache=True
                )

                # Assert
                assert result == cached_embedding
                mock_get_cache.assert_called_once()
                mock_provider.assert_not_called()  # Should not call provider

    @pytest.mark.asyncio
    async def test_embedding_provider_error_handling(self):
        """Test error handling when embedding provider fails."""
        # Arrange
        text = "Text that causes error"

        with patch.object(
            self.embeddings_service, '_call_embedding_provider'
        ) as mock_provider:
            mock_provider.side_effect = Exception("Provider API error")

            # Act & Assert
            with pytest.raises(EmbeddingError) as exc_info:
                await self.embeddings_service.generate_text_embedding(
                    text
                )

            assert "Provider API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_available_models(self):
        """Test retrieving available embedding models."""
        # Arrange
        expected_models = [
            {
                "name": "text-embedding-ada-002",
                "provider": "openai",
                "dimensions": 1536,
                "max_tokens": 8191,
            },
            {
                "name": "text-embedding-3-small",
                "provider": "openai",
                "dimensions": 1536,
                "max_tokens": 8191,
            },
        ]

        with patch.object(
            self.embeddings_service, '_fetch_available_models'
        ) as mock_fetch:
            mock_fetch.return_value = expected_models

            # Act
            models = (
                await self.embeddings_service.get_available_models()
            )

            # Assert
            assert len(models) == 2
            assert models[0]["name"] == "text-embedding-ada-002"

    @pytest.mark.asyncio
    async def test_embedding_rate_limiting(self):
        """Test embedding service rate limiting."""
        # Arrange
        texts = [f"Text {i}" for i in range(100)]  # Large batch

        with patch.object(
            self.embeddings_service, '_apply_rate_limit'
        ) as mock_rate_limit:
            with patch.object(
                self.embeddings_service,
                '_call_batch_embedding_provider',
            ) as mock_batch:
                mock_batch.return_value = [[0.1, 0.2] for _ in texts]

                # Act
                result = await self.embeddings_service.generate_batch_embeddings(
                    texts, respect_rate_limits=True
                )

                # Assert
                assert len(result) == 100
                mock_rate_limit.assert_called()


@pytest.mark.integration
class TestEmbeddingsServiceIntegration:
    """Integration tests for embeddings service using real database."""

    def setup_method(self):
        """Set up test fixtures."""
        # Real database session will be injected via test_db_session fixture
        pass

    @pytest.mark.asyncio
    async def test_document_embedding_workflow(self, test_db_session):
        """Test complete document embedding workflow with real database."""
        from chatter.models.user import User
        from chatter.models.document import Document, DocumentType
        from chatter.services.embeddings import EmbeddingService
        from sqlalchemy import select
        
        # Create a real user for document ownership
        user = User(
            email="embedding_test@example.com",
            username="embeddinguser",
            hashed_password="hashed_password_here",
            full_name="Embedding Test User",
            is_active=True,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        
        # Create real documents in the database
        documents = [
            Document(
                owner_id=user.id,
                filename="ai_document.txt",
                original_filename="ai_document.txt",
                file_size=100,
                file_hash="hash1",
                mime_type="text/plain",
                document_type=DocumentType.TEXT,
                title="AI Document",
                content="First document about AI",
            ),
            Document(
                owner_id=user.id,
                filename="ml_document.txt",
                original_filename="ml_document.txt",
                file_size=150,
                file_hash="hash2",
                mime_type="text/plain",
                document_type=DocumentType.TEXT,
                title="ML Document",
                content="Second document about machine learning",
            ),
            Document(
                owner_id=user.id,
                filename="ds_document.txt",
                original_filename="ds_document.txt",
                file_size=120,
                file_hash="hash3",
                mime_type="text/plain",
                document_type=DocumentType.TEXT,
                title="Data Science Document",
                content="Third document about data science",
            ),
        ]
        
        for doc in documents:
            test_db_session.add(doc)
        await test_db_session.commit()
        
        # Create embeddings service with real database session
        embeddings_service = EmbeddingService(test_db_session)

        # Verify the service was created with real session
        assert embeddings_service is not None
        
        # Test that we can list available providers
        providers = await embeddings_service.list_available_providers()
        assert isinstance(providers, list)
        
        # Test that we can get provider info
        provider_info = await embeddings_service.get_all_provider_info()
        assert isinstance(provider_info, dict)
        
        # Verify documents exist in database
        result = await test_db_session.execute(
            select(Document).where(Document.owner_id == user.id)
        )
        db_documents = result.scalars().all()
        assert len(db_documents) == 3
        assert all(doc.content is not None for doc in db_documents)
        
        # Verify documents have the expected content for embedding processing
        contents = [doc.content for doc in db_documents]
        assert "First document about AI" in contents
        assert "Second document about machine learning" in contents
        assert "Third document about data science" in contents


@pytest.mark.unit
class TestEmbeddingsServiceHelpers:
    """Test embeddings service helper methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.embeddings_service = EmbeddingService(self.mock_session)

    def test_text_preprocessing(self):
        """Test text preprocessing functionality."""
        # Arrange
        raw_text = "  This is SAMPLE text with\n\nextra   spaces!  "

        # Act
        processed = self.embeddings_service._preprocess_text(raw_text)

        # Assert
        assert processed == "this is sample text with extra spaces!"
        assert processed.islower()
        assert "  " not in processed  # No double spaces
        assert not processed.startswith(" ")  # No leading space
        assert not processed.endswith(" ")  # No trailing space

    def test_embedding_validation(self):
        """Test embedding validation logic."""
        # Arrange
        valid_embedding = [0.1, 0.2, 0.3, 0.4]
        invalid_embedding_nan = [0.1, float('nan'), 0.3]
        invalid_embedding_inf = [0.1, float('inf'), 0.3]

        # Act & Assert
        assert (
            self.embeddings_service._validate_embedding(valid_embedding)
            is True
        )
        assert (
            self.embeddings_service._validate_embedding(
                invalid_embedding_nan
            )
            is False
        )
        assert (
            self.embeddings_service._validate_embedding(
                invalid_embedding_inf
            )
            is False
        )

    def test_batch_processing(self):
        """Test batch processing utilities."""
        # Arrange
        texts = [f"Text {i}" for i in range(25)]
        batch_size = 10

        # Act
        batches = list(
            self.embeddings_service._create_batches(texts, batch_size)
        )

        # Assert
        assert len(batches) == 3  # 25 items in batches of 10
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5

    def test_cache_key_generation(self):
        """Test cache key generation for embeddings."""
        # Arrange
        text = "Sample text for caching"
        model = "text-embedding-ada-002"

        # Act
        cache_key = self.embeddings_service._generate_cache_key(
            text, model
        )

        # Assert
        assert isinstance(cache_key, str)
        assert len(cache_key) > 0
        assert (
            model in cache_key or text in cache_key
        )  # Should contain identifying info
