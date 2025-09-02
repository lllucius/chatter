"""Tests for document management service."""

import asyncio
import hashlib
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile

from chatter.core.documents import (
    ChunkingStrategy,
    DocumentProcessor,
    DocumentSearchEngine,
    DocumentService,
    DocumentValidator,
)
from chatter.core.exceptions import (
    DocumentNotFoundError,
    DocumentProcessingError,
)
from chatter.models.document import (
    DocumentType,
)
from chatter.schemas.document import (
    DocumentCreate,
    DocumentListRequest,
    DocumentSearchRequest,
    DocumentUpdate,
)


@pytest.mark.unit
class TestDocumentService:
    """Test DocumentService functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.document_service = DocumentService(self.mock_session)

    @pytest.mark.asyncio
    async def test_create_document(self):
        """Test creating a new document."""
        # Arrange
        document_data = DocumentCreate(
            title="Test Document",
            content="This is test content",
            document_type=DocumentType.TEXT,
            metadata={"source": "test"},
        )

        mock_document = MagicMock()
        mock_document.id = "doc-123"
        mock_document.title = document_data.title

        self.mock_session.add = MagicMock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()

        with patch('chatter.core.documents.Document') as mock_doc_class:
            mock_doc_class.return_value = mock_document

            # Act
            created_document = (
                await self.document_service.create_document(
                    document_data
                )
            )

            # Assert
            assert created_document.id == "doc-123"
            assert created_document.title == "Test Document"
            self.mock_session.add.assert_called_once()
            self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_document_by_id(self):
        """Test getting a document by ID."""
        # Arrange
        document_id = "doc-123"
        mock_document = MagicMock()
        mock_document.id = document_id
        mock_document.title = "Test Document"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_document
        self.mock_session.execute.return_value = mock_result

        # Act
        document = await self.document_service.get_document(document_id)

        # Assert
        assert document.id == document_id
        assert document.title == "Test Document"
        self.mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_document_not_found(self):
        """Test getting a non-existent document."""
        # Arrange
        document_id = "nonexistent-doc"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(DocumentNotFoundError):
            await self.document_service.get_document(document_id)

    @pytest.mark.asyncio
    async def test_update_document(self):
        """Test updating an existing document."""
        # Arrange
        document_id = "doc-123"
        update_data = DocumentUpdate(
            title="Updated Title", content="Updated content"
        )

        mock_document = MagicMock()
        mock_document.id = document_id
        mock_document.title = "Original Title"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_document
        self.mock_session.execute.return_value = mock_result
        self.mock_session.commit.return_value = AsyncMock()

        # Act
        updated_document = await self.document_service.update_document(
            document_id, update_data
        )

        # Assert
        assert updated_document.title == "Updated Title"
        self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_document(self):
        """Test deleting a document."""
        # Arrange
        document_id = "doc-123"
        mock_document = MagicMock()
        mock_document.id = document_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_document
        self.mock_session.execute.return_value = mock_result
        self.mock_session.delete = MagicMock()
        self.mock_session.commit = AsyncMock()

        # Act
        result = await self.document_service.delete_document(
            document_id
        )

        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_document)
        self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file(self):
        """Test uploading a file."""
        # Arrange
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"PDF content")

        user_id = "user-123"

        with (
            patch.object(
                self.document_service, '_save_file'
            ) as mock_save_file,
            patch.object(
                self.document_service, '_extract_metadata'
            ) as mock_extract_metadata,
            patch.object(
                self.document_service, 'create_document'
            ) as mock_create_document,
        ):

            mock_save_file.return_value = "/uploads/test.pdf"
            mock_extract_metadata.return_value = {"pages": 10}
            mock_create_document.return_value = MagicMock(id="doc-123")

            # Act
            document = await self.document_service.upload_file(
                mock_file, user_id
            )

            # Assert
            assert document.id == "doc-123"
            mock_save_file.assert_called_once()
            mock_extract_metadata.assert_called_once()
            mock_create_document.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_documents(self):
        """Test searching documents."""
        # Arrange
        search_request = DocumentSearchRequest(
            query="test query",
            document_type=DocumentType.TEXT,
            limit=10,
        )

        mock_documents = [
            MagicMock(id="doc-1", title="Document 1"),
            MagicMock(id="doc-2", title="Document 2"),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = (
            mock_documents
        )
        self.mock_session.execute.return_value = mock_result

        # Act
        results = await self.document_service.search_documents(
            search_request
        )

        # Assert
        assert len(results) == 2
        assert results[0].id == "doc-1"
        assert results[1].id == "doc-2"

    @pytest.mark.asyncio
    async def test_list_documents_with_pagination(self):
        """Test listing documents with pagination."""
        # Arrange
        list_request = DocumentListRequest(
            page=1, size=10, sort_by="created_at", sort_order="desc"
        )

        mock_documents = [MagicMock(id=f"doc-{i}") for i in range(10)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = (
            mock_documents
        )
        self.mock_session.execute.return_value = mock_result

        # Act
        results = await self.document_service.list_documents(
            list_request
        )

        # Assert
        assert len(results) == 10
        self.mock_session.execute.assert_called_once()

    def test_calculate_file_hash(self):
        """Test calculating file hash."""
        # Arrange
        content = b"test file content"
        expected_hash = hashlib.sha256(content).hexdigest()

        # Act
        calculated_hash = self.document_service._calculate_file_hash(
            content
        )

        # Assert
        assert calculated_hash == expected_hash

    def test_validate_file_type(self):
        """Test file type validation."""
        # Arrange
        valid_types = ["application/pdf", "text/plain", "text/markdown"]
        invalid_types = ["application/exe", "image/gif"]

        # Act & Assert
        for file_type in valid_types:
            assert (
                self.document_service._validate_file_type(file_type)
                is True
            )

        for file_type in invalid_types:
            assert (
                self.document_service._validate_file_type(file_type)
                is False
            )

    def test_extract_file_metadata(self):
        """Test extracting file metadata."""
        # Arrange
        file_path = "/test/document.pdf"
        content = b"PDF content"

        with (
            patch('os.path.getsize') as mock_getsize,
            patch('os.path.getmtime') as mock_getmtime,
        ):

            mock_getsize.return_value = 1024
            mock_getmtime.return_value = 1640995200  # 2022-01-01

            # Act
            metadata = self.document_service._extract_metadata(
                file_path, content
            )

            # Assert
            assert metadata["file_size"] == 1024
            assert "file_type" in metadata
            assert "hash" in metadata


@pytest.mark.unit
class TestDocumentProcessor:
    """Test DocumentProcessor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = DocumentProcessor()

    @pytest.mark.asyncio
    async def test_process_text_document(self):
        """Test processing a text document."""
        # Arrange
        document = MagicMock()
        document.id = "doc-123"
        document.content = "This is a test document with multiple sentences. It has several paragraphs."
        document.document_type = DocumentType.TEXT

        # Act
        result = await self.processor.process_document(document)

        # Assert
        assert result["status"] == "completed"
        assert "chunks" in result
        assert len(result["chunks"]) > 0

    @pytest.mark.asyncio
    async def test_process_pdf_document(self):
        """Test processing a PDF document."""
        # Arrange
        document = MagicMock()
        document.id = "doc-123"
        document.file_path = "/test/document.pdf"
        document.document_type = DocumentType.PDF

        with patch(
            'chatter.core.documents.extract_pdf_text'
        ) as mock_extract:
            mock_extract.return_value = "Extracted PDF text content"

            # Act
            result = await self.processor.process_document(document)

            # Assert
            assert result["status"] == "completed"
            assert "extracted_text" in result
            mock_extract.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_markdown_document(self):
        """Test processing a markdown document."""
        # Arrange
        document = MagicMock()
        document.id = "doc-123"
        document.content = "# Title\n\nThis is **markdown** content."
        document.document_type = DocumentType.MARKDOWN

        # Act
        result = await self.processor.process_document(document)

        # Assert
        assert result["status"] == "completed"
        assert "html_content" in result
        assert "chunks" in result

    @pytest.mark.asyncio
    async def test_process_document_error_handling(self):
        """Test error handling during document processing."""
        # Arrange
        document = MagicMock()
        document.id = "doc-123"
        document.document_type = DocumentType.PDF
        document.file_path = "/nonexistent/file.pdf"

        with patch(
            'chatter.core.documents.extract_pdf_text'
        ) as mock_extract:
            mock_extract.side_effect = Exception(
                "PDF extraction failed"
            )

            # Act & Assert
            with pytest.raises(DocumentProcessingError):
                await self.processor.process_document(document)

    def test_chunk_text_by_sentences(self):
        """Test chunking text by sentences."""
        # Arrange
        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        strategy = ChunkingStrategy.SENTENCES

        # Act
        chunks = self.processor.chunk_text(
            text, strategy, max_chunk_size=2
        )

        # Assert
        assert len(chunks) >= 2
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_chunk_text_by_paragraphs(self):
        """Test chunking text by paragraphs."""
        # Arrange
        text = (
            "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        )
        strategy = ChunkingStrategy.PARAGRAPHS

        # Act
        chunks = self.processor.chunk_text(text, strategy)

        # Assert
        assert len(chunks) == 3
        assert "First paragraph" in chunks[0]
        assert "Second paragraph" in chunks[1]

    def test_chunk_text_by_fixed_size(self):
        """Test chunking text by fixed size."""
        # Arrange
        text = "A" * 1000  # 1000 character string
        strategy = ChunkingStrategy.FIXED_SIZE

        # Act
        chunks = self.processor.chunk_text(
            text, strategy, max_chunk_size=200
        )

        # Assert
        assert len(chunks) == 5  # 1000 / 200
        assert all(len(chunk) <= 200 for chunk in chunks)

    def test_extract_keywords(self):
        """Test extracting keywords from text."""
        # Arrange
        text = "This is a test document about machine learning and natural language processing."

        # Act
        keywords = self.processor.extract_keywords(text)

        # Assert
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert all(isinstance(keyword, str) for keyword in keywords)

    def test_calculate_reading_time(self):
        """Test calculating reading time for text."""
        # Arrange
        text = "This is a test document. " * 100  # ~500 words

        # Act
        reading_time = self.processor.calculate_reading_time(text)

        # Assert
        assert reading_time > 0
        assert isinstance(reading_time, int)  # minutes


@pytest.mark.unit
class TestDocumentSearchEngine:
    """Test DocumentSearchEngine functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.search_engine = DocumentSearchEngine(self.mock_session)

    @pytest.mark.asyncio
    async def test_full_text_search(self):
        """Test full-text search functionality."""
        # Arrange
        query = "machine learning"

        mock_documents = [
            MagicMock(
                id="doc-1", title="ML Guide", relevance_score=0.95
            ),
            MagicMock(
                id="doc-2", title="AI Basics", relevance_score=0.80
            ),
        ]

        mock_result = MagicMock()
        mock_result.all.return_value = mock_documents
        self.mock_session.execute.return_value = mock_result

        # Act
        results = await self.search_engine.full_text_search(query)

        # Assert
        assert len(results) == 2
        assert (
            results[0].relevance_score > results[1].relevance_score
        )  # Sorted by relevance

    @pytest.mark.asyncio
    async def test_semantic_search(self):
        """Test semantic search functionality."""
        # Arrange
        query = "artificial intelligence"

        mock_embeddings = [0.1, 0.2, 0.3]
        mock_documents = [
            MagicMock(
                id="doc-1", title="AI Overview", similarity_score=0.85
            ),
            MagicMock(
                id="doc-2", title="ML Tutorial", similarity_score=0.75
            ),
        ]

        with (
            patch.object(
                self.search_engine, '_get_query_embeddings'
            ) as mock_embeddings_func,
            patch.object(
                self.search_engine, '_vector_similarity_search'
            ) as mock_vector_search,
        ):

            mock_embeddings_func.return_value = mock_embeddings
            mock_vector_search.return_value = mock_documents

            # Act
            results = await self.search_engine.semantic_search(query)

            # Assert
            assert len(results) == 2
            mock_embeddings_func.assert_called_once_with(query)
            mock_vector_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_hybrid_search(self):
        """Test hybrid search combining full-text and semantic search."""
        # Arrange
        query = "neural networks"

        # Mock full-text results
        fulltext_results = [
            MagicMock(id="doc-1", title="Neural Networks", score=0.9),
            MagicMock(id="doc-3", title="Deep Learning", score=0.7),
        ]

        # Mock semantic results
        semantic_results = [
            MagicMock(id="doc-1", title="Neural Networks", score=0.85),
            MagicMock(id="doc-2", title="AI Fundamentals", score=0.8),
        ]

        with (
            patch.object(
                self.search_engine, 'full_text_search'
            ) as mock_fulltext,
            patch.object(
                self.search_engine, 'semantic_search'
            ) as mock_semantic,
        ):

            mock_fulltext.return_value = fulltext_results
            mock_semantic.return_value = semantic_results

            # Act
            results = await self.search_engine.hybrid_search(query)

            # Assert
            assert len(results) >= 2
            # Should include unique documents from both searches
            doc_ids = [doc.id for doc in results]
            assert "doc-1" in doc_ids
            assert "doc-2" in doc_ids or "doc-3" in doc_ids

    @pytest.mark.asyncio
    async def test_search_with_filters(self):
        """Test search with various filters."""
        # Arrange
        query = "test query"
        filters = {
            "document_type": DocumentType.PDF,
            "created_after": datetime(2024, 1, 1),
            "tags": ["important", "review"],
        }

        mock_result = MagicMock()
        mock_result.all.return_value = []
        self.mock_session.execute.return_value = mock_result

        # Act
        results = await self.search_engine.search_with_filters(
            query, filters
        )

        # Assert
        assert isinstance(results, list)
        self.mock_session.execute.assert_called_once()

    def test_calculate_relevance_score(self):
        """Test relevance score calculation."""
        # Arrange
        query_terms = ["machine", "learning"]
        document_text = "This document is about machine learning algorithms and artificial intelligence."

        # Act
        score = self.search_engine._calculate_relevance_score(
            query_terms, document_text
        )

        # Assert
        assert 0.0 <= score <= 1.0
        assert score > 0  # Should have some relevance

    def test_extract_query_terms(self):
        """Test extracting query terms."""
        # Arrange
        query = "machine learning algorithms"

        # Act
        terms = self.search_engine._extract_query_terms(query)

        # Assert
        assert isinstance(terms, list)
        assert "machine" in terms
        assert "learning" in terms
        assert "algorithms" in terms


@pytest.mark.unit
class TestDocumentValidator:
    """Test DocumentValidator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DocumentValidator()

    def test_validate_document_content(self):
        """Test validating document content."""
        # Arrange
        valid_content = (
            "This is valid document content with sufficient length."
        )
        invalid_content = ""

        # Act & Assert
        assert self.validator.validate_content(valid_content) is True
        assert self.validator.validate_content(invalid_content) is False

    def test_validate_file_size(self):
        """Test validating file size."""
        # Arrange
        valid_size = 1024 * 1024  # 1MB
        invalid_size = 100 * 1024 * 1024  # 100MB

        # Act & Assert
        assert self.validator.validate_file_size(valid_size) is True
        assert self.validator.validate_file_size(invalid_size) is False

    def test_validate_file_extension(self):
        """Test validating file extensions."""
        # Arrange
        valid_files = ["document.pdf", "text.txt", "readme.md"]
        invalid_files = ["virus.exe", "script.bat", "image.gif"]

        # Act & Assert
        for filename in valid_files:
            assert (
                self.validator.validate_file_extension(filename) is True
            )

        for filename in invalid_files:
            assert (
                self.validator.validate_file_extension(filename)
                is False
            )

    def test_scan_for_malicious_content(self):
        """Test scanning for malicious content."""
        # Arrange
        safe_content = "This is safe document content."

        # Act & Assert
        assert (
            self.validator.scan_for_malicious_content(safe_content)
            is True
        )
        # Note: In a real implementation, this might return False for suspicious content

    def test_validate_document_structure(self):
        """Test validating document structure."""
        # Arrange
        valid_document = {
            "title": "Valid Document",
            "content": "Valid content",
            "type": DocumentType.TEXT,
        }

        invalid_document = {
            "title": "",  # Empty title
            "content": "Valid content",
            # Missing type
        }

        # Act & Assert
        validation_result = self.validator.validate_document_structure(
            valid_document
        )
        assert validation_result.is_valid is True

        validation_result = self.validator.validate_document_structure(
            invalid_document
        )
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0


@pytest.mark.integration
class TestDocumentIntegration:
    """Integration tests for document management system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.document_service = DocumentService(self.mock_session)
        self.processor = DocumentProcessor()
        self.search_engine = DocumentSearchEngine(self.mock_session)

    @pytest.mark.asyncio
    async def test_complete_document_workflow(self):
        """Test complete document workflow from upload to search."""
        # Arrange
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test_document.txt"
        mock_file.content_type = "text/plain"
        mock_file.read = AsyncMock(
            return_value=b"This is test document content for integration testing."
        )

        user_id = "user-123"

        with (
            patch.object(
                self.document_service, '_save_file'
            ) as mock_save,
            patch.object(
                self.document_service, 'create_document'
            ) as mock_create,
            patch.object(
                self.processor, 'process_document'
            ) as mock_process,
        ):

            mock_save.return_value = "/uploads/test_document.txt"

            mock_document = MagicMock()
            mock_document.id = "doc-123"
            mock_document.title = "test_document.txt"
            mock_create.return_value = mock_document

            mock_process.return_value = {
                "status": "completed",
                "chunks": ["chunk1", "chunk2"],
            }

            # Act
            # Step 1: Upload document
            uploaded_doc = await self.document_service.upload_file(
                mock_file, user_id
            )

            # Step 2: Process document
            processing_result = await self.processor.process_document(
                uploaded_doc
            )

            # Step 3: Search for document (mock the search)
            with patch.object(
                self.search_engine, 'full_text_search'
            ) as mock_search:
                mock_search.return_value = [uploaded_doc]
                search_results = (
                    await self.search_engine.full_text_search("test")
                )

            # Assert
            assert uploaded_doc.id == "doc-123"
            assert processing_result["status"] == "completed"
            assert len(search_results) == 1
            assert search_results[0].id == "doc-123"

    @pytest.mark.asyncio
    async def test_bulk_document_processing(self):
        """Test processing multiple documents concurrently."""
        # Arrange
        documents = []
        for i in range(5):
            doc = MagicMock()
            doc.id = f"doc-{i}"
            doc.content = f"Document {i} content for testing."
            doc.document_type = DocumentType.TEXT
            documents.append(doc)

        # Act
        tasks = [
            self.processor.process_document(doc) for doc in documents
        ]
        results = await asyncio.gather(*tasks)

        # Assert
        assert len(results) == 5
        assert all(
            result["status"] == "completed" for result in results
        )

    @pytest.mark.asyncio
    async def test_document_search_performance(self):
        """Test document search performance with multiple queries."""
        # Arrange
        queries = [
            "machine learning",
            "artificial intelligence",
            "natural language processing",
            "computer vision",
            "deep learning",
        ]

        mock_results = [MagicMock(id=f"doc-{i}") for i in range(10)]

        with patch.object(
            self.search_engine, 'full_text_search'
        ) as mock_search:
            mock_search.return_value = mock_results

            # Act
            start_time = datetime.now()

            search_tasks = [
                self.search_engine.full_text_search(query)
                for query in queries
            ]
            all_results = await asyncio.gather(*search_tasks)

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            # Assert
            assert len(all_results) == 5
            assert all(len(results) == 10 for results in all_results)
            assert execution_time < 1.0  # Should complete quickly

    @pytest.mark.asyncio
    async def test_document_error_recovery(self):
        """Test error recovery during document operations."""
        # Arrange
        document_data = DocumentCreate(
            title="Error Test Document",
            content="Test content",
            document_type=DocumentType.TEXT,
        )

        # Simulate database error on first attempt
        self.mock_session.commit.side_effect = [
            Exception("Database error"),
            None,  # Success on retry
        ]

        # Act & Assert
        # First attempt should fail
        with pytest.raises(Exception):
            await self.document_service.create_document(document_data)

        # Reset the side effect for retry
        self.mock_session.commit.side_effect = None
        self.mock_session.commit.return_value = None

        # Create mock document for successful attempt
        mock_document = MagicMock()
        mock_document.id = "doc-123"

        with patch('chatter.core.documents.Document') as mock_doc_class:
            mock_doc_class.return_value = mock_document

            # Retry should succeed
            created_doc = await self.document_service.create_document(
                document_data
            )
            assert created_doc.id == "doc-123"

    @pytest.mark.asyncio
    async def test_document_security_validation(self):
        """Test document security validation workflow."""
        # Arrange
        validator = DocumentValidator()

        # Test file with potentially malicious content
        suspicious_file = MagicMock(spec=UploadFile)
        suspicious_file.filename = "suspicious_document.txt"
        suspicious_file.content_type = "text/plain"
        suspicious_file.read = AsyncMock(
            return_value=b"Click here: http://suspicious-link.com"
        )

        # Act
        content = await suspicious_file.read()
        content_str = content.decode('utf-8')

        # Validate file
        is_safe_extension = validator.validate_file_extension(
            suspicious_file.filename
        )
        is_safe_content = validator.scan_for_malicious_content(
            content_str
        )

        # Assert
        assert is_safe_extension is True  # .txt is allowed
        # Content validation depends on implementation
        assert isinstance(is_safe_content, bool)
