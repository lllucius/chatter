"""Tests for dynamic embedding model factory and management."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import Column, Integer, String

from chatter.core.dynamic_embeddings import (
    DynamicEmbeddingService,
    EmbeddingModelManager,
    _to_name,
    embedding_models,
    get_embedding_model,
    list_embedding_models,
    make_embedding_model,
)
from chatter.core.exceptions import (
    DimensionMismatchError,
    EmbeddingModelError,
)


@pytest.mark.unit
class TestEmbeddingModelGeneration:
    """Test dynamic embedding model generation functionality."""

    def test_to_name_generation(self):
        """Test name generation for embedding models."""
        # Test cases with different inputs
        test_cases = [
            ("OpenAI", 1536, "openai_1536_embed"),
            (
                "sentence-transformers",
                384,
                "sentence_transformers_384_embed",
            ),
            (
                "text-embedding-ada-002",
                1536,
                "text_embedding_ada_002_1536_embed",
            ),
            ("BERT-base", 768, "bert_base_768_embed"),
            (
                "123invalid",
                512,
                "_123invalid_512_embed",
            ),  # Starts with number
            ("model with spaces", 256, "model_with_spaces_256_embed"),
            ("model/with/slashes", 128, "model_with_slashes_128_embed"),
        ]

        for input_name, dimension, expected in test_cases:
            result = _to_name(input_name, dimension)
            assert result == expected
            assert len(result) <= 63  # PostgreSQL identifier limit
            assert result.endswith(f"_{dimension}_embed")

    def test_to_name_truncation(self):
        """Test name truncation for very long model names."""
        # Arrange
        very_long_name = "a" * 100  # Very long name
        dimension = 1536

        # Act
        result = _to_name(very_long_name, dimension)

        # Assert
        assert len(result) <= 63
        assert result.endswith(f"_{dimension}_embed")
        assert result.startswith("a")

    def test_make_embedding_model_creation(self):
        """Test creating a new embedding model."""
        # Arrange
        model_name = "test_model"
        dimension = 512

        # Clear any existing models
        embedding_models.clear()

        # Act
        model_class = make_embedding_model(model_name, dimension)

        # Assert
        assert model_class is not None
        assert hasattr(model_class, '__tablename__')
        assert model_class.__tablename__ == "test_model_512_embed"

        # Check that model is registered
        table_name = _to_name(model_name, dimension)
        assert table_name in embedding_models
        assert embedding_models[table_name] == model_class

    def test_make_embedding_model_duplicate_creation(self):
        """Test creating duplicate embedding model returns existing one."""
        # Arrange
        model_name = "duplicate_model"
        dimension = 384

        # Clear any existing models
        embedding_models.clear()

        # Act
        model_class1 = make_embedding_model(model_name, dimension)
        model_class2 = make_embedding_model(model_name, dimension)

        # Assert
        assert model_class1 is model_class2  # Should return same class

    def test_make_embedding_model_different_dimensions(self):
        """Test creating models with same name but different dimensions."""
        # Arrange
        model_name = "multi_dim_model"
        dimension1 = 384
        dimension2 = 768

        # Clear any existing models
        embedding_models.clear()

        # Act
        model_class1 = make_embedding_model(model_name, dimension1)
        model_class2 = make_embedding_model(model_name, dimension2)

        # Assert
        assert model_class1 is not model_class2
        assert model_class1.__tablename__ != model_class2.__tablename__
        assert "384" in model_class1.__tablename__
        assert "768" in model_class2.__tablename__

    def test_get_embedding_model_existing(self):
        """Test getting an existing embedding model."""
        # Arrange
        model_name = "existing_model"
        dimension = 512

        # Clear and create model
        embedding_models.clear()
        created_model = make_embedding_model(model_name, dimension)

        # Act
        retrieved_model = get_embedding_model(model_name, dimension)

        # Assert
        assert retrieved_model is created_model

    def test_get_embedding_model_nonexistent(self):
        """Test getting a non-existent embedding model."""
        # Arrange
        embedding_models.clear()

        # Act & Assert
        with pytest.raises(EmbeddingModelError) as exc_info:
            get_embedding_model("nonexistent_model", 512)

        assert "not found" in str(exc_info.value)

    def test_list_embedding_models(self):
        """Test listing all registered embedding models."""
        # Arrange
        embedding_models.clear()

        # Create several models
        models = [("model_a", 384), ("model_b", 512), ("model_c", 768)]

        for name, dim in models:
            make_embedding_model(name, dim)

        # Act
        model_list = list_embedding_models()

        # Assert
        assert len(model_list) == 3
        assert all(isinstance(item, tuple) for item in model_list)
        assert all(
            len(item) == 3 for item in model_list
        )  # (name, dimension, class)

    def test_embedding_model_attributes(self):
        """Test that generated embedding models have correct attributes."""
        # Arrange
        model_name = "attribute_test"
        dimension = 256

        # Act
        model_class = make_embedding_model(model_name, dimension)

        # Assert
        # Check for required columns
        assert hasattr(model_class, 'id')
        assert hasattr(model_class, 'text')
        assert hasattr(model_class, 'embedding')
        assert hasattr(model_class, 'document_id')
        assert hasattr(model_class, 'chunk_index')

        # Check column types
        assert isinstance(
            model_class.id.type, type(Column(Integer).type)
        )
        assert isinstance(
            model_class.text.type, type(Column(String).type)
        )


@pytest.mark.integration
class TestEmbeddingModelManagerIntegration:
    """Integration tests for EmbeddingModelManager with real database."""

    def setup_method(self):
        """Set up test fixtures."""
        # Real database session will be injected via test_db_session fixture
        pass

    @pytest.mark.asyncio
    async def test_create_embedding_table(self, test_db_session):
        """Test creating embedding table in real database."""
        # Arrange
        manager = EmbeddingModelManager(test_db_session)
        model_name = "create_test"
        dimension = 512

        # Clear models and create new one
        embedding_models.clear()
        make_embedding_model(model_name, dimension)

        # Act
        result = await manager.create_embedding_table(
            model_name, dimension
        )

        # Assert
        assert result is True
        
        # Verify table was actually created by checking if it exists
        table_exists = await manager.table_exists(model_name, dimension)
        assert table_exists is True

    @pytest.mark.asyncio
    async def test_drop_embedding_table(self, test_db_session):
        """Test dropping embedding table from real database."""
        # Arrange
        manager = EmbeddingModelManager(test_db_session)
        model_name = "drop_test"
        dimension = 384
        
        # Clear models and create new one
        embedding_models.clear()
        make_embedding_model(model_name, dimension)
        
        # First create the table
        await manager.create_embedding_table(model_name, dimension)
        
        # Verify table exists before dropping
        assert await manager.table_exists(model_name, dimension) is True

        # Act
        result = await manager.drop_embedding_table(
            model_name, dimension
        )

        # Assert
        assert result is True
        
        # Verify table was actually dropped
        table_exists = await manager.table_exists(model_name, dimension)
        assert table_exists is False

    @pytest.mark.asyncio
    async def test_table_exists_check(self, test_db_session):
        """Test checking if embedding table exists in real database."""
        # Arrange
        manager = EmbeddingModelManager(test_db_session)
        model_name = "existence_test"
        dimension = 768

        # Clear models and create new one
        embedding_models.clear()
        make_embedding_model(model_name, dimension)
        
        # Create the table first
        await manager.create_embedding_table(model_name, dimension)

        # Act
        exists = await manager.table_exists(model_name, dimension)

        # Assert
        assert exists is True

    @pytest.mark.asyncio
    async def test_table_not_exists_check(self, test_db_session):
        """Test checking if embedding table doesn't exist in real database."""
        # Arrange
        manager = EmbeddingModelManager(test_db_session)
        model_name = "nonexistent_test"
        dimension = 512

        # Act - check for a table that was never created
        exists = await manager.table_exists(model_name, dimension)

        # Assert
        assert exists is False

    @pytest.mark.asyncio
    async def test_get_table_info(self, test_db_session):
        """Test getting table information from real database."""
        # Arrange
        manager = EmbeddingModelManager(test_db_session)
        model_name = "info_test"
        dimension = 256

        # Clear models and create new one
        embedding_models.clear()
        make_embedding_model(model_name, dimension)
        
        # Create the table first
        await manager.create_embedding_table(model_name, dimension)

        # Act
        table_info = await manager.get_table_info(
            model_name, dimension
        )

        # Assert
        assert len(table_info) >= 3  # Should have at least id, text, embedding columns
        
        # Check for expected columns (actual column info may vary by database)
        column_names = [col[0] for col in table_info]
        assert "id" in column_names
        assert "content" in column_names  # The column is actually named 'content', not 'text'
        assert "embedding" in column_names

    @pytest.mark.asyncio
    async def test_register_model_with_database(self, test_db_session):
        """Test registering model and creating database table in real database."""
        # Arrange
        manager = EmbeddingModelManager(test_db_session)
        model_name = "register_test"
        dimension = 512

        # Clear models first
        embedding_models.clear()

        # Act
        model_class = await manager.register_model(
            model_name, dimension
        )

        # Assert
        assert model_class is not None
        assert hasattr(model_class, '__tablename__')
        
        # Verify table was created in the database
        table_exists = await manager.table_exists(model_name, dimension)
        assert table_exists is True
        
        # Verify model is in the registry
        table_name = _to_name(model_name, dimension)
        assert table_name in embedding_models

    @pytest.mark.asyncio
    async def test_unregister_model_with_database(self, test_db_session):
        """Test unregistering model and dropping database table from real database."""
        # Arrange
        manager = EmbeddingModelManager(test_db_session)
        model_name = "unregister_test"
        dimension = 384

        # First register the model and create table
        embedding_models.clear()
        await manager.register_model(model_name, dimension)
        
        # Verify table exists before unregistering
        assert await manager.table_exists(model_name, dimension) is True

        # Act
        result = await manager.unregister_model(
            model_name, dimension
        )

        # Assert
        assert result is True
        
        # Model should be removed from registry
        table_name = _to_name(model_name, dimension)
        assert table_name not in embedding_models
        
        # Table should be dropped from database
        table_exists = await manager.table_exists(model_name, dimension)
        assert table_exists is False


@pytest.mark.unit
class TestDynamicEmbeddingService:
    """Test DynamicEmbeddingService functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.embedding_service = DynamicEmbeddingService(
            self.mock_session
        )

    @pytest.mark.asyncio
    async def test_store_embeddings(self):
        """Test storing embeddings in dynamic table."""
        # Arrange
        model_name = "store_test"
        dimension = 512

        embeddings_data = [
            {
                "text": "First text",
                "embedding": [0.1] * dimension,
                "document_id": "doc-1",
                "chunk_index": 0,
            },
            {
                "text": "Second text",
                "embedding": [0.2] * dimension,
                "document_id": "doc-1",
                "chunk_index": 1,
            },
        ]

        # Create model
        embedding_models.clear()
        make_embedding_model(model_name, dimension)

        # Act
        result = await self.embedding_service.store_embeddings(
            model_name, dimension, embeddings_data
        )

        # Assert
        assert result is True
        self.mock_session.execute.assert_called()
        self.mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_retrieve_embeddings(self):
        """Test retrieving embeddings from dynamic table."""
        # Arrange
        model_name = "retrieve_test"
        dimension = 384
        document_id = "doc-123"

        # Mock retrieved data
        mock_embeddings = [
            MagicMock(
                text="Text 1",
                embedding=[0.1] * dimension,
                chunk_index=0,
            ),
            MagicMock(
                text="Text 2",
                embedding=[0.2] * dimension,
                chunk_index=1,
            ),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = (
            mock_embeddings
        )
        self.mock_session.execute.return_value = mock_result

        # Create model
        embedding_models.clear()
        make_embedding_model(model_name, dimension)

        # Act
        embeddings = await self.embedding_service.retrieve_embeddings(
            model_name, dimension, document_id
        )

        # Assert
        assert len(embeddings) == 2
        assert embeddings[0].text == "Text 1"
        assert embeddings[1].text == "Text 2"

    @pytest.mark.asyncio
    async def test_search_similar_embeddings(self):
        """Test searching for similar embeddings."""
        # Arrange
        model_name = "search_test"
        dimension = 256
        query_embedding = [0.5] * dimension
        limit = 5

        # Mock search results
        mock_results = [
            MagicMock(text="Similar text 1", similarity=0.95),
            MagicMock(text="Similar text 2", similarity=0.87),
            MagicMock(text="Similar text 3", similarity=0.82),
        ]

        mock_result = MagicMock()
        mock_result.fetchall.return_value = mock_results
        self.mock_session.execute.return_value = mock_result

        # Create model
        embedding_models.clear()
        make_embedding_model(model_name, dimension)

        # Act
        similar_embeddings = (
            await self.embedding_service.search_similar_embeddings(
                model_name, dimension, query_embedding, limit
            )
        )

        # Assert
        assert len(similar_embeddings) == 3
        assert (
            similar_embeddings[0].similarity
            > similar_embeddings[1].similarity
        )
        self.mock_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_delete_embeddings(self):
        """Test deleting embeddings from dynamic table."""
        # Arrange
        model_name = "delete_test"
        dimension = 512
        document_id = "doc-to-delete"

        # Create model
        embedding_models.clear()
        make_embedding_model(model_name, dimension)

        # Act
        result = await self.embedding_service.delete_embeddings(
            model_name, dimension, document_id
        )

        # Assert
        assert result is True
        self.mock_session.execute.assert_called()
        self.mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_update_embeddings(self):
        """Test updating embeddings in dynamic table."""
        # Arrange
        model_name = "update_test"
        dimension = 384
        document_id = "doc-update"

        new_embeddings_data = [
            {
                "text": "Updated text",
                "embedding": [0.9] * dimension,
                "document_id": document_id,
                "chunk_index": 0,
            }
        ]

        # Create model
        embedding_models.clear()
        make_embedding_model(model_name, dimension)

        # Act
        result = await self.embedding_service.update_embeddings(
            model_name, dimension, document_id, new_embeddings_data
        )

        # Assert
        assert result is True
        # Should call delete then insert
        assert self.mock_session.execute.call_count >= 2
        self.mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_get_embedding_stats(self):
        """Test getting embedding statistics."""
        # Arrange
        model_name = "stats_test"
        dimension = 768

        # Mock statistics
        mock_stats = MagicMock()
        mock_stats.scalar.side_effect = [
            1000,  # total_embeddings
            50,  # unique_documents
            20.5,  # avg_embeddings_per_document
        ]
        self.mock_session.execute.return_value = mock_stats

        # Create model
        embedding_models.clear()
        make_embedding_model(model_name, dimension)

        # Act
        stats = await self.embedding_service.get_embedding_stats(
            model_name, dimension
        )

        # Assert
        assert stats["total_embeddings"] == 1000
        assert stats["unique_documents"] == 50
        assert stats["avg_embeddings_per_document"] == 20.5

    @pytest.mark.asyncio
    async def test_dimension_validation(self):
        """Test dimension validation for embeddings."""
        # Arrange
        model_name = "dimension_test"
        dimension = 512

        # Wrong dimension embeddings
        wrong_embeddings = [
            {
                "text": "Text",
                "embedding": [0.1] * 256,
                "document_id": "doc-1",
                "chunk_index": 0,
            }  # 256 instead of 512
        ]

        # Create model
        embedding_models.clear()
        make_embedding_model(model_name, dimension)

        # Act & Assert
        with pytest.raises(DimensionMismatchError):
            await self.embedding_service.store_embeddings(
                model_name, dimension, wrong_embeddings
            )


@pytest.mark.integration
class TestDynamicEmbeddingIntegration:
    """Integration tests for dynamic embedding system."""

    def setup_method(self):
        """Set up test fixtures."""
        # Real database session will be injected via test_db_session fixture
        pass

    @pytest.mark.asyncio
    async def test_complete_embedding_workflow(self, test_db_session):
        """Test complete embedding workflow with real database."""
        from chatter.models.user import User
        from chatter.models.document import Document, DocumentType
        from chatter.core.dynamic_embeddings import EmbeddingModelManager, DynamicEmbeddingService
        from sqlalchemy import text
        
        # Create a real user for testing
        user = User(
            email="embedding@example.com",
            username="embeddinguser",
            hashed_password="hashed_password_here",
            full_name="Embedding Test User",
            is_active=True,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        
        # Create a test document for embedding
        document = Document(
            owner_id=user.id,
            filename="embedding_test.txt",
            original_filename="embedding_test.txt",
            file_size=200,
            file_hash="embedhash123",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            title="Embedding Test Document",
            content="This is a test document for embedding integration testing.",
        )
        test_db_session.add(document)
        await test_db_session.commit()
        await test_db_session.refresh(document)
        
        # Verify document was created for embedding workflow
        assert document.id is not None
        assert document.content is not None
        assert len(document.content) > 0
        
        # Test that embedding data infrastructure works with real database
        # Verify we can query document content for embedding processing
        result = await test_db_session.execute(
            text("SELECT content FROM documents WHERE id = :doc_id"),
            {"doc_id": document.id}
        )
        doc_content = result.scalar()
        assert doc_content == "This is a test document for embedding integration testing."
        
        # Verify user-document relationship
        user_docs_result = await test_db_session.execute(
            text("SELECT COUNT(*) FROM documents WHERE owner_id = :owner_id"),
            {"owner_id": user.id}
        )
        doc_count = user_docs_result.scalar()
        assert doc_count == 1

        # Test embedding model management with real database
        manager = EmbeddingModelManager(test_db_session)
        embedding_service = DynamicEmbeddingService(test_db_session)
        
        # Test model registration
        model_name = "test_integration_model"
        dimension = 384
        
        model_class = await manager.register_model(model_name, dimension)
        assert model_class is not None
        assert hasattr(model_class, '__tablename__')
        
        # Test that model table was created
        table_exists = await manager.table_exists(model_name, dimension)
        assert table_exists is True
        
        # Test storing embeddings in the dynamic table
        embeddings_data = [
            {
                "text": "Integration test text chunk 1",
                "embedding": [0.1] * dimension,
                "document_id": document.id,
                "chunk_index": 0,
            },
            {
                "text": "Integration test text chunk 2", 
                "embedding": [0.2] * dimension,
                "document_id": document.id,
                "chunk_index": 1,
            },
        ]
        
        store_result = await embedding_service.store_embeddings(
            model_name, dimension, embeddings_data
        )
        assert store_result is True
        
        # Test retrieving embeddings
        retrieved_embeddings = await embedding_service.retrieve_embeddings(
            model_name, dimension, document.id
        )
        assert len(retrieved_embeddings) == 2
        assert retrieved_embeddings[0].text == "Integration test text chunk 1"
        
        # Cleanup: unregister the model
        cleanup_result = await manager.unregister_model(model_name, dimension)
        assert cleanup_result is True

    @pytest.mark.asyncio
    async def test_multiple_model_management(self):
        """Test managing multiple embedding models simultaneously."""
        # Arrange
        models = [
            ("openai_model", 1536),
            ("sentence_transformers", 384),
            ("bert_model", 768),
        ]

        # Clear models
        embedding_models.clear()

        # Act
        created_models = []
        for model_name, dimension in models:
            model_class = await self.manager.register_model(
                model_name, dimension
            )
            created_models.append((model_name, dimension, model_class))

        # Verify all models exist
        model_list = list_embedding_models()

        # Assert
        assert len(created_models) == 3
        assert len(model_list) == 3

        # Each model should have unique table name
        table_names = [
            model[2].__tablename__ for model in created_models
        ]
        assert len(set(table_names)) == 3  # All unique

    @pytest.mark.asyncio
    async def test_embedding_performance_with_large_dataset(self):
        """Test embedding operations with larger dataset."""
        # Arrange
        model_name = "performance_test"
        dimension = 512

        # Create model
        embedding_models.clear()
        await self.manager.register_model(model_name, dimension)

        # Generate large dataset
        large_dataset = []
        for i in range(100):
            large_dataset.append(
                {
                    "text": f"Performance test text {i}",
                    "embedding": [float(i % 10) / 10] * dimension,
                    "document_id": f"doc-{i // 10}",
                    "chunk_index": i % 10,
                }
            )

        # Act
        start_time = datetime.now()

        # Store large dataset
        store_result = await self.service.store_embeddings(
            model_name, dimension, large_dataset
        )

        end_time = datetime.now()
        storage_time = (end_time - start_time).total_seconds()

        # Assert
        assert store_result is True
        assert storage_time < 5.0  # Should complete within 5 seconds

        # Verify session operations were called
        assert self.mock_session.execute.call_count > 0
        assert self.mock_session.commit.call_count > 0

    @pytest.mark.asyncio
    async def test_model_lifecycle_management(self):
        """Test complete model lifecycle from creation to deletion."""
        # Arrange
        model_name = "lifecycle_test"
        dimension = 256

        # Clear models
        embedding_models.clear()

        # Act
        # Step 1: Create model
        model_class = await self.manager.register_model(
            model_name, dimension
        )
        table_name = _to_name(model_name, dimension)

        # Verify model is registered
        assert table_name in embedding_models

        # Step 2: Use model for some operations
        test_data = [
            {
                "text": "Lifecycle test",
                "embedding": [0.1] * dimension,
                "document_id": "doc-lifecycle",
                "chunk_index": 0,
            }
        ]
        await self.service.store_embeddings(
            model_name, dimension, test_data
        )

        # Step 3: Get model info
        mock_info = [
            ("id", "integer"),
            ("text", "text"),
            ("embedding", f"vector({dimension})"),
        ]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = mock_info
        self.mock_session.execute.return_value = mock_result

        table_info = await self.manager.get_table_info(
            model_name, dimension
        )

        # Step 4: Unregister model
        unregister_result = await self.manager.unregister_model(
            model_name, dimension
        )

        # Assert
        assert model_class is not None
        assert len(table_info) == 3
        assert unregister_result is True
        assert table_name not in embedding_models

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """Test error handling during embedding operations."""
        # Arrange
        model_name = "error_test"
        dimension = 128

        # Clear models
        embedding_models.clear()

        # Act & Assert
        # Test model creation with database error
        self.mock_session.execute.side_effect = Exception(
            "Database connection failed"
        )

        with pytest.raises(Exception):
            await self.manager.register_model(model_name, dimension)

        # Reset session for successful operation
        self.mock_session.execute.side_effect = None
        self.mock_session.execute.return_value = MagicMock()

        # Should succeed after error recovery
        model_class = await self.manager.register_model(
            model_name, dimension
        )
        assert model_class is not None
