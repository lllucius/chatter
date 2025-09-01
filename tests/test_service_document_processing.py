"""Tests for document processing service."""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.document import Document, DocumentChunk, DocumentStatus, DocumentType
from chatter.services.document_processing import DocumentProcessingService


@pytest.mark.unit
class TestDocumentProcessingService:
    """Test DocumentProcessingService functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.service = DocumentProcessingService(self.mock_session)
        
        # Mock the dependent services
        self.service.embedding_service = MagicMock()
        self.service.vector_store_service = MagicMock()

    def test_service_initialization(self):
        """Test service initialization."""
        # Assert
        assert self.service.session == self.mock_session
        assert self.service.embedding_service is not None
        assert self.service.vector_store_service is not None
        assert isinstance(self.service.storage_path, Path)

    @pytest.mark.asyncio
    async def test_process_document_not_found(self):
        """Test processing non-existent document."""
        # Arrange
        document_id = "nonexistent-doc-id"
        file_content = b"test content"
        
        # Mock document not found
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # Act
        result = await self.service.process_document(document_id, file_content)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_process_document_already_processed(self):
        """Test processing already processed document."""
        # Arrange
        document_id = "processed-doc-id"
        file_content = b"test content"
        
        mock_document = Document(
            id=document_id,
            filename="test.txt",
            status=DocumentStatus.PROCESSED
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document

        # Act
        result = await self.service.process_document(document_id, file_content)

        # Assert
        assert result is True
        # Should not change status if already processed
        assert mock_document.status == DocumentStatus.PROCESSED

    @pytest.mark.asyncio
    async def test_process_document_force_reprocess(self):
        """Test force reprocessing already processed document."""
        # Arrange
        document_id = "processed-doc-id"
        file_content = b"test content"
        
        mock_document = Document(
            id=document_id,
            filename="test.txt",
            status=DocumentStatus.PROCESSED,
            owner_id="user-123"
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document
        self.mock_session.refresh = AsyncMock()

        # Mock the processing pipeline
        with patch.object(self.service, '_extract_text', return_value="extracted text"):
            with patch.object(self.service, '_create_chunks', return_value=["chunk1", "chunk2"]):
                with patch.object(self.service, '_store_chunks', return_value=[MagicMock(), MagicMock()]):
                    with patch.object(self.service, '_generate_embeddings', return_value=True):
                        # Act
                        result = await self.service.process_document(
                            document_id, file_content, force_reprocess=True
                        )

        # Assert
        assert result is True
        assert mock_document.status == DocumentStatus.PROCESSED
        assert mock_document.processing_started_at is not None
        self.mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_process_document_text_extraction_failure(self):
        """Test document processing when text extraction fails."""
        # Arrange
        document_id = "text-fail-doc-id"
        file_content = b"corrupted content"
        
        mock_document = Document(
            id=document_id,
            filename="corrupted.pdf",
            status=DocumentStatus.PENDING,
            owner_id="user-123"
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document
        self.mock_session.refresh = AsyncMock()

        # Mock text extraction failure
        with patch.object(self.service, '_extract_text', return_value=None):
            with patch.object(self.service, '_mark_processing_failed') as mock_mark_failed:
                # Act
                result = await self.service.process_document(document_id, file_content)

        # Assert
        assert result is False
        mock_mark_failed.assert_called_once_with(mock_document, "Failed to extract text from document")

    @pytest.mark.asyncio
    async def test_process_document_chunking_failure(self):
        """Test document processing when chunking fails."""
        # Arrange
        document_id = "chunk-fail-doc-id"
        file_content = b"test content"
        
        mock_document = Document(
            id=document_id,
            filename="test.txt",
            status=DocumentStatus.PENDING,
            owner_id="user-123"
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document
        self.mock_session.refresh = AsyncMock()

        # Mock successful text extraction but failed chunking
        with patch.object(self.service, '_extract_text', return_value="extracted text"):
            with patch.object(self.service, '_create_chunks', return_value=None):
                with patch.object(self.service, '_mark_processing_failed') as mock_mark_failed:
                    # Act
                    result = await self.service.process_document(document_id, file_content)

        # Assert
        assert result is False
        mock_mark_failed.assert_called_once_with(mock_document, "Failed to create chunks from text")

    @pytest.mark.asyncio
    async def test_process_document_storage_failure(self):
        """Test document processing when chunk storage fails."""
        # Arrange
        document_id = "storage-fail-doc-id"
        file_content = b"test content"
        
        mock_document = Document(
            id=document_id,
            filename="test.txt",
            status=DocumentStatus.PENDING,
            owner_id="user-123"
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document
        self.mock_session.refresh = AsyncMock()

        # Mock successful text extraction and chunking but failed storage
        with patch.object(self.service, '_extract_text', return_value="extracted text"):
            with patch.object(self.service, '_create_chunks', return_value=["chunk1", "chunk2"]):
                with patch.object(self.service, '_store_chunks', return_value=None):
                    with patch.object(self.service, '_mark_processing_failed') as mock_mark_failed:
                        # Act
                        result = await self.service.process_document(document_id, file_content)

        # Assert
        assert result is False
        mock_mark_failed.assert_called_once_with(mock_document, "Failed to store chunks")

    @pytest.mark.asyncio
    async def test_process_document_embedding_failure_no_providers(self):
        """Test document processing when embedding fails due to no providers."""
        # Arrange
        document_id = "embedding-fail-doc-id"
        file_content = b"test content"
        
        mock_document = Document(
            id=document_id,
            filename="test.txt",
            status=DocumentStatus.PENDING,
            owner_id="user-123"
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document
        self.mock_session.refresh = AsyncMock()

        # Mock successful pipeline until embeddings
        mock_chunks = [MagicMock(), MagicMock()]
        with patch.object(self.service, '_extract_text', return_value="extracted text"):
            with patch.object(self.service, '_create_chunks', return_value=["chunk1", "chunk2"]):
                with patch.object(self.service, '_store_chunks', return_value=mock_chunks):
                    with patch.object(self.service, '_generate_embeddings', return_value=False):
                        # Mock no embedding providers available
                        self.service.embedding_service.list_available_providers.return_value = []
                        with patch.object(self.service, '_mark_processing_failed') as mock_mark_failed:
                            # Act
                            result = await self.service.process_document(document_id, file_content)

        # Assert
        assert result is False
        mock_mark_failed.assert_called_once_with(mock_document, "No embedding providers available")

    @pytest.mark.asyncio
    async def test_process_document_successful_complete_pipeline(self):
        """Test successful complete document processing pipeline."""
        # Arrange
        document_id = "success-doc-id"
        file_content = b"test content"
        
        mock_document = Document(
            id=document_id,
            filename="test.txt",
            status=DocumentStatus.PENDING,
            owner_id="user-123"
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document
        self.mock_session.refresh = AsyncMock()

        # Mock successful complete pipeline
        mock_chunks = [
            MagicMock(id="chunk-1"),
            MagicMock(id="chunk-2")
        ]
        
        with patch.object(self.service, '_extract_text', return_value="extracted text"):
            with patch.object(self.service, '_create_chunks', return_value=["chunk1", "chunk2"]):
                with patch.object(self.service, '_store_chunks', return_value=mock_chunks):
                    with patch.object(self.service, '_generate_embeddings', return_value=True):
                        # Act
                        result = await self.service.process_document(document_id, file_content)

        # Assert
        assert result is True
        assert mock_document.status == DocumentStatus.PROCESSED
        assert mock_document.extracted_text == "extracted text"
        assert mock_document.processing_started_at is not None
        assert mock_document.processing_completed_at is not None
        self.mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_process_document_with_sse_event_failure(self):
        """Test document processing when SSE event triggering fails."""
        # Arrange
        document_id = "sse-fail-doc-id"
        file_content = b"test content"
        
        mock_document = Document(
            id=document_id,
            filename="test.txt",
            status=DocumentStatus.PENDING,
            owner_id="user-123"
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document
        self.mock_session.refresh = AsyncMock()

        # Mock SSE service import failure
        with patch('chatter.services.document_processing.sse_service', side_effect=ImportError("SSE not available")):
            with patch.object(self.service, '_extract_text', return_value="extracted text"):
                with patch.object(self.service, '_create_chunks', return_value=["chunk1"]):
                    with patch.object(self.service, '_store_chunks', return_value=[MagicMock()]):
                        with patch.object(self.service, '_generate_embeddings', return_value=True):
                            # Act
                            result = await self.service.process_document(document_id, file_content)

        # Assert - Should still succeed even if SSE fails
        assert result is True
        assert mock_document.status == DocumentStatus.PROCESSED


@pytest.mark.unit
class TestDocumentProcessingPrivateMethods:
    """Test private methods of DocumentProcessingService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.service = DocumentProcessingService(self.mock_session)
        self.service.embedding_service = MagicMock()
        self.service.vector_store_service = MagicMock()

    @pytest.mark.asyncio
    async def test_mark_processing_failed(self):
        """Test marking document processing as failed."""
        # Arrange
        mock_document = Document(
            id="doc-id",
            status=DocumentStatus.PROCESSING
        )
        error_message = "Test error message"

        # Act
        await self.service._mark_processing_failed(mock_document, error_message)

        # Assert
        assert mock_document.status == DocumentStatus.FAILED
        assert mock_document.processing_error == error_message
        assert mock_document.processing_completed_at is not None
        self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_text_unsupported_format(self):
        """Test text extraction with unsupported file format."""
        # Arrange
        mock_document = Document(
            filename="test.unknown",
            document_type=DocumentType.UNKNOWN
        )
        file_content = b"test content"

        # Act
        result = await self.service._extract_text(mock_document, file_content)

        # Assert
        assert result is None

    @pytest.mark.asyncio 
    async def test_extract_text_plain_text(self):
        """Test text extraction from plain text file."""
        # Arrange
        mock_document = Document(
            filename="test.txt",
            document_type=DocumentType.TXT
        )
        file_content = b"This is plain text content"

        # Act
        result = await self.service._extract_text(mock_document, file_content)

        # Assert
        assert result == "This is plain text content"

    @pytest.mark.asyncio
    async def test_extract_text_with_encoding_detection(self):
        """Test text extraction with encoding detection."""
        # Arrange
        mock_document = Document(
            filename="test.txt",
            document_type=DocumentType.TXT
        )
        # Use UTF-8 encoded content with special characters
        file_content = "Héllo wörld 🌍".encode('utf-8')

        # Act
        result = await self.service._extract_text(mock_document, file_content)

        # Assert
        assert result == "Héllo wörld 🌍"

    @pytest.mark.asyncio
    async def test_create_chunks_empty_text(self):
        """Test chunk creation with empty text."""
        # Arrange
        mock_document = Document(id="doc-id", filename="test.txt")
        text = ""

        # Act
        result = await self.service._create_chunks(mock_document, text)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_create_chunks_normal_text(self):
        """Test chunk creation with normal text."""
        # Arrange
        mock_document = Document(id="doc-id", filename="test.txt")
        text = "This is a test document. " * 100  # Long enough to create multiple chunks

        # Act
        result = await self.service._create_chunks(mock_document, text)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(chunk, str) for chunk in result)

    @pytest.mark.asyncio
    async def test_store_chunks_success(self):
        """Test successful chunk storage."""
        # Arrange
        mock_document = Document(id="doc-id", filename="test.txt")
        chunks = ["chunk 1 content", "chunk 2 content", "chunk 3 content"]

        self.mock_session.flush = AsyncMock()
        self.mock_session.refresh = AsyncMock()

        # Act
        result = await self.service._store_chunks(mock_document, chunks)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 3
        # Verify session operations
        assert self.mock_session.add.call_count == 3  # One for each chunk
        self.mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_chunks_database_error(self):
        """Test chunk storage with database error."""
        # Arrange
        mock_document = Document(id="doc-id", filename="test.txt")
        chunks = ["chunk 1", "chunk 2"]

        # Mock database error
        self.mock_session.flush.side_effect = Exception("Database error")

        # Act
        result = await self.service._store_chunks(mock_document, chunks)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self):
        """Test successful embedding generation."""
        # Arrange
        mock_document = Document(id="doc-id", filename="test.txt")
        mock_chunks = [
            MagicMock(id="chunk-1", content="content 1"),
            MagicMock(id="chunk-2", content="content 2")
        ]

        # Mock successful embedding generation
        self.service.embedding_service.generate_embeddings.return_value = [
            [0.1, 0.2, 0.3],  # Embedding for chunk 1
            [0.4, 0.5, 0.6]   # Embedding for chunk 2
        ]
        self.service.vector_store_service.add_chunks = AsyncMock(return_value=True)

        # Act
        result = await self.service._generate_embeddings(mock_document, mock_chunks)

        # Assert
        assert result is True
        self.service.embedding_service.generate_embeddings.assert_called_once()
        self.service.vector_store_service.add_chunks.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_embeddings_embedding_service_failure(self):
        """Test embedding generation when embedding service fails."""
        # Arrange
        mock_document = Document(id="doc-id", filename="test.txt")
        mock_chunks = [MagicMock(id="chunk-1", content="content 1")]

        # Mock embedding service failure
        from chatter.services.embeddings import EmbeddingError
        self.service.embedding_service.generate_embeddings.side_effect = EmbeddingError("Service failed")

        # Act
        result = await self.service._generate_embeddings(mock_document, mock_chunks)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_generate_embeddings_vector_store_failure(self):
        """Test embedding generation when vector store fails."""
        # Arrange
        mock_document = Document(id="doc-id", filename="test.txt")
        mock_chunks = [MagicMock(id="chunk-1", content="content 1")]

        # Mock successful embeddings but vector store failure
        self.service.embedding_service.generate_embeddings.return_value = [[0.1, 0.2, 0.3]]
        self.service.vector_store_service.add_chunks = AsyncMock(return_value=False)

        # Act
        result = await self.service._generate_embeddings(mock_document, mock_chunks)

        # Assert
        assert result is False


@pytest.mark.integration
class TestDocumentProcessingServiceIntegration:
    """Integration tests for DocumentProcessingService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.service = DocumentProcessingService(self.mock_session)

    @pytest.mark.asyncio
    async def test_complete_document_processing_workflow(self):
        """Test complete document processing workflow."""
        # Arrange
        document_id = "integration-doc-id"
        file_content = b"This is a comprehensive test document with multiple sentences. " * 50
        
        mock_document = Document(
            id=document_id,
            filename="integration_test.txt",
            document_type=DocumentType.TXT,
            status=DocumentStatus.PENDING,
            owner_id="user-123"
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document
        self.mock_session.refresh = AsyncMock()
        self.mock_session.flush = AsyncMock()

        # Mock all dependent services
        self.service.embedding_service = MagicMock()
        self.service.embedding_service.generate_embeddings.return_value = [
            [0.1, 0.2, 0.3, 0.4, 0.5]  # Mock embedding vector
        ]
        
        self.service.vector_store_service = MagicMock()
        self.service.vector_store_service.add_chunks = AsyncMock(return_value=True)

        # Act
        result = await self.service.process_document(document_id, file_content)

        # Assert
        assert result is True
        assert mock_document.status == DocumentStatus.PROCESSED
        assert mock_document.extracted_text is not None
        assert len(mock_document.extracted_text) > 0
        assert mock_document.processing_started_at is not None
        assert mock_document.processing_completed_at is not None
        assert mock_document.processing_error is None

        # Verify session interactions
        self.mock_session.commit.assert_called()
        self.mock_session.refresh.assert_called()

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery in document processing."""
        # Arrange
        document_id = "error-recovery-doc-id"
        file_content = b"test content"
        
        mock_document = Document(
            id=document_id,
            filename="error_test.txt",
            status=DocumentStatus.PENDING,
            owner_id="user-123"
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document
        self.mock_session.refresh = AsyncMock()

        # Mock partial failure scenario
        with patch.object(self.service, '_extract_text', return_value="extracted text"):
            with patch.object(self.service, '_create_chunks', return_value=["chunk1", "chunk2"]):
                with patch.object(self.service, '_store_chunks', side_effect=Exception("Storage failed")):
                    with patch.object(self.service, '_mark_processing_failed') as mock_mark_failed:
                        # Act
                        result = await self.service.process_document(document_id, file_content)

        # Assert
        assert result is False
        mock_mark_failed.assert_called_once()
        # Verify the document state reflects the failure
        args, kwargs = mock_mark_failed.call_args
        assert args[0] == mock_document
        assert "Failed to store chunks" in args[1]

    @pytest.mark.asyncio
    async def test_concurrent_document_processing(self):
        """Test concurrent processing of multiple documents."""
        # Arrange
        documents_data = [
            ("doc-1", b"Content for document 1"),
            ("doc-2", b"Content for document 2"),
            ("doc-3", b"Content for document 3")
        ]
        
        mock_documents = []
        for doc_id, _ in documents_data:
            mock_doc = Document(
                id=doc_id,
                filename=f"{doc_id}.txt",
                status=DocumentStatus.PENDING,
                owner_id="user-123"
            )
            mock_documents.append(mock_doc)
        
        # Mock session to return different documents for different calls
        def mock_execute_side_effect(*args, **kwargs):
            # Extract document ID from the query (simplified for test)
            mock_result = MagicMock()
            # Return different documents based on call order
            if not hasattr(mock_execute_side_effect, 'call_count'):
                mock_execute_side_effect.call_count = 0
            
            if mock_execute_side_effect.call_count < len(mock_documents):
                mock_result.scalar_one_or_none.return_value = mock_documents[mock_execute_side_effect.call_count]
            else:
                mock_result.scalar_one_or_none.return_value = None
            
            mock_execute_side_effect.call_count += 1
            return mock_result

        self.mock_session.execute.side_effect = mock_execute_side_effect
        self.mock_session.refresh = AsyncMock()
        self.mock_session.flush = AsyncMock()

        # Mock all services for successful processing
        self.service.embedding_service = MagicMock()
        self.service.embedding_service.generate_embeddings.return_value = [[0.1, 0.2, 0.3]]
        self.service.vector_store_service = MagicMock()
        self.service.vector_store_service.add_chunks = AsyncMock(return_value=True)

        # Act - Process documents concurrently
        tasks = [
            self.service.process_document(doc_id, content)
            for doc_id, content in documents_data
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Assert
        assert len(results) == 3
        assert all(result is True for result in results)
        
        # Verify all documents were processed
        for mock_doc in mock_documents:
            assert mock_doc.status == DocumentStatus.PROCESSED

    @pytest.mark.asyncio
    async def test_large_document_processing(self):
        """Test processing of large documents."""
        # Arrange
        document_id = "large-doc-id"
        # Create large content (simulate 1MB text file)
        large_content = ("This is a large document content. " * 1000).encode('utf-8')
        
        mock_document = Document(
            id=document_id,
            filename="large_document.txt",
            document_type=DocumentType.TXT,
            status=DocumentStatus.PENDING,
            owner_id="user-123"
        )
        
        self.mock_session.execute.return_value.scalar_one_or_none.return_value = mock_document
        self.mock_session.refresh = AsyncMock()
        self.mock_session.flush = AsyncMock()

        # Mock services for large document
        self.service.embedding_service = MagicMock()
        # Mock multiple embeddings for multiple chunks
        self.service.embedding_service.generate_embeddings.return_value = [
            [0.1, 0.2, 0.3] for _ in range(10)  # Simulate 10 chunks
        ]
        self.service.vector_store_service = MagicMock()
        self.service.vector_store_service.add_chunks = AsyncMock(return_value=True)

        # Act
        result = await self.service.process_document(document_id, large_content)

        # Assert
        assert result is True
        assert mock_document.status == DocumentStatus.PROCESSED
        assert len(mock_document.extracted_text) > 30000  # Should be substantial
        
        # Verify embedding service was called with multiple chunks
        self.service.embedding_service.generate_embeddings.assert_called_once()
        call_args = self.service.embedding_service.generate_embeddings.call_args[0]
        texts = call_args[0]  # First argument should be list of texts
        assert isinstance(texts, list)
        assert len(texts) > 1  # Should have multiple chunks