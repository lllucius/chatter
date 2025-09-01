"""Tests for document models."""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from chatter.models.document import (
    Document,
    DocumentChunk,
    DocumentStatus,
    DocumentType,
)
from chatter.models.user import User


@pytest.mark.unit
class TestDocumentModel:
    """Test Document model functionality."""

    def test_document_creation(self, test_user: User):
        """Test basic document creation."""
        # Arrange & Act
        document = Document(
            owner_id=test_user.id,
            filename="test.pdf",
            original_filename="test document.pdf",
            file_size=1024,
            file_hash="abc123def456",
            mime_type="application/pdf",
            document_type=DocumentType.PDF,
            title="Test Document",
            description="A test document",
        )

        # Assert
        assert document.owner_id == test_user.id
        assert document.filename == "test.pdf"
        assert document.original_filename == "test document.pdf"
        assert document.file_size == 1024
        assert document.file_hash == "abc123def456"
        assert document.mime_type == "application/pdf"
        assert document.document_type == DocumentType.PDF
        assert document.title == "Test Document"
        assert document.description == "A test document"
        assert document.status == DocumentStatus.PENDING
        assert document.chunk_size == 1000
        assert document.chunk_overlap == 200
        assert document.chunk_count == 0
        assert document.version == 1
        assert document.is_public is False
        assert document.view_count == 0
        assert document.search_count == 0

    def test_document_with_content(self, test_user: User):
        """Test document with content and processing details."""
        # Arrange & Act
        document = Document(
            owner_id=test_user.id,
            filename="content.txt",
            original_filename="content.txt",
            file_size=500,
            file_hash="hash123",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            content="This is the document content",
            extracted_text="This is the extracted text",
            status=DocumentStatus.PROCESSED,
            chunk_size=500,
            chunk_overlap=100,
            chunk_count=2,
        )

        # Assert
        assert document.content == "This is the document content"
        assert document.extracted_text == "This is the extracted text"
        assert document.status == DocumentStatus.PROCESSED
        assert document.chunk_size == 500
        assert document.chunk_overlap == 100
        assert document.chunk_count == 2

    def test_document_with_metadata(self, test_user: User):
        """Test document with tags and metadata."""
        # Arrange & Act
        document = Document(
            owner_id=test_user.id,
            filename="meta.pdf",
            original_filename="meta.pdf",
            file_size=2048,
            file_hash="meta123",
            mime_type="application/pdf",
            document_type=DocumentType.PDF,
            tags=["research", "important", "2023"],
            extra_metadata={
                "author": "John Doe",
                "subject": "Test Subject",
                "keywords": ["test", "document"]
            }
        )

        # Assert
        assert document.tags == ["research", "important", "2023"]
        assert document.extra_metadata["author"] == "John Doe"
        assert document.extra_metadata["subject"] == "Test Subject"
        assert document.extra_metadata["keywords"] == ["test", "document"]

    def test_document_processing_timestamps(self, test_user: User):
        """Test document with processing timestamps."""
        # Arrange
        start_time = datetime(2023, 1, 1, 12, 0, 0)
        end_time = datetime(2023, 1, 1, 12, 2, 30)
        
        # Act
        document = Document(
            owner_id=test_user.id,
            filename="timed.pdf",
            original_filename="timed.pdf",
            file_size=1024,
            file_hash="time123",
            mime_type="application/pdf",
            document_type=DocumentType.PDF,
            status=DocumentStatus.PROCESSED,
            processing_started_at=start_time,
            processing_completed_at=end_time,
        )

        # Assert
        assert document.processing_started_at == start_time
        assert document.processing_completed_at == end_time
        assert document.processing_duration == 150.0  # 2.5 minutes

    def test_document_version_control(self, test_user: User):
        """Test document version control."""
        # Arrange & Act
        parent_doc = Document(
            owner_id=test_user.id,
            filename="parent.pdf",
            original_filename="parent.pdf",
            file_size=1024,
            file_hash="parent123",
            mime_type="application/pdf",
            document_type=DocumentType.PDF,
            version=1,
        )
        
        child_doc = Document(
            owner_id=test_user.id,
            filename="child.pdf",
            original_filename="child.pdf",
            file_size=1024,
            file_hash="child123",
            mime_type="application/pdf",
            document_type=DocumentType.PDF,
            version=2,
            parent_document_id=parent_doc.id,
        )

        # Assert
        assert parent_doc.version == 1
        assert child_doc.version == 2
        assert child_doc.parent_document_id == parent_doc.id

    def test_document_properties(self, test_user: User):
        """Test document properties."""
        # Arrange
        # Processed document
        processed_doc = Document(
            owner_id=test_user.id,
            filename="processed.txt",
            original_filename="processed.txt",
            file_size=100,
            file_hash="proc123",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            status=DocumentStatus.PROCESSED,
        )
        
        # Pending document
        pending_doc = Document(
            owner_id=test_user.id,
            filename="pending.txt",
            original_filename="pending.txt",
            file_size=100,
            file_hash="pend123",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            status=DocumentStatus.PENDING,
        )

        # Assert
        assert processed_doc.is_processed is True
        assert pending_doc.is_processed is False

    def test_document_to_dict(self, test_user: User):
        """Test document to dictionary conversion."""
        # Arrange
        document = Document(
            owner_id=test_user.id,
            filename="dict.pdf",
            original_filename="dict test.pdf",
            file_size=1024,
            file_hash="dict123",
            mime_type="application/pdf",
            document_type=DocumentType.PDF,
            title="Dict Test",
            description="Test description",
            status=DocumentStatus.PROCESSED,
            tags=["test"],
            extra_metadata={"key": "value"},
            version=1,
            is_public=True,
            view_count=5,
            search_count=3,
        )
        
        # Mock timestamps
        document.created_at = datetime(2023, 1, 1, 12, 0, 0)
        document.updated_at = datetime(2023, 1, 1, 12, 30, 0)
        document.processing_started_at = datetime(2023, 1, 1, 12, 1, 0)
        document.processing_completed_at = datetime(2023, 1, 1, 12, 2, 0)
        document.last_accessed_at = datetime(2023, 1, 1, 12, 15, 0)

        # Act
        result = document.to_dict()

        # Assert
        assert result["id"] == document.id
        assert result["owner_id"] == test_user.id
        assert result["filename"] == "dict.pdf"
        assert result["original_filename"] == "dict test.pdf"
        assert result["file_size"] == 1024
        assert result["file_hash"] == "dict123"
        assert result["mime_type"] == "application/pdf"
        assert result["document_type"] == "pdf"
        assert result["title"] == "Dict Test"
        assert result["description"] == "Test description"
        assert result["status"] == "processed"
        assert result["tags"] == ["test"]
        assert result["extra_metadata"] == {"key": "value"}
        assert result["version"] == 1
        assert result["is_public"] is True
        assert result["view_count"] == 5
        assert result["search_count"] == 3
        assert "2023-01-01T12:00:00" in result["created_at"]
        assert "2023-01-01T12:30:00" in result["updated_at"]

    def test_document_repr(self, test_user: User):
        """Test document string representation."""
        # Arrange
        document = Document(
            owner_id=test_user.id,
            filename="repr.pdf",
            original_filename="repr.pdf",
            file_size=1024,
            file_hash="repr123",
            mime_type="application/pdf",
            document_type=DocumentType.PDF,
            status=DocumentStatus.PROCESSED,
        )

        # Act
        repr_str = repr(document)

        # Assert
        assert "Document" in repr_str
        assert document.id in repr_str
        assert "repr.pdf" in repr_str
        assert "processed" in repr_str


@pytest.mark.unit
class TestDocumentChunkModel:
    """Test DocumentChunk model functionality."""

    def test_chunk_creation(self, test_document: Document):
        """Test basic chunk creation."""
        # Arrange & Act
        chunk = DocumentChunk(
            document_id=test_document.id,
            content="This is a chunk of content",
            chunk_index=0,
            start_char=0,
            end_char=26,
            content_hash="chunk123",
        )

        # Assert
        assert chunk.document_id == test_document.id
        assert chunk.content == "This is a chunk of content"
        assert chunk.chunk_index == 0
        assert chunk.start_char == 0
        assert chunk.end_char == 26
        assert chunk.content_hash == "chunk123"

    def test_chunk_with_analysis(self, test_document: Document):
        """Test chunk with content analysis."""
        # Arrange & Act
        chunk = DocumentChunk(
            document_id=test_document.id,
            content="This is analyzed content",
            chunk_index=1,
            content_hash="analysis123",
            token_count=25,
            language="en",
        )

        # Assert
        assert chunk.token_count == 25
        assert chunk.language == "en"

    def test_chunk_with_embeddings(self, test_document: Document):
        """Test chunk with embedding metadata."""
        # Arrange
        embedding_time = datetime(2023, 1, 1, 12, 0, 0)
        
        # Act
        chunk = DocumentChunk(
            document_id=test_document.id,
            content="Embedded content",
            chunk_index=0,
            content_hash="embed123",
            embedding_models=["openai-ada-002", "sentence-transformers"],
            primary_embedding_model="openai-ada-002",
            embedding_provider="openai",
            embedding_created_at=embedding_time,
        )

        # Assert
        assert chunk.embedding_models == ["openai-ada-002", "sentence-transformers"]
        assert chunk.primary_embedding_model == "openai-ada-002"
        assert chunk.embedding_provider == "openai"
        assert chunk.embedding_created_at == embedding_time
        assert chunk.has_dynamic_embeddings is True

    def test_chunk_embedding_management(self, test_document: Document):
        """Test chunk embedding model management."""
        # Arrange
        chunk = DocumentChunk(
            document_id=test_document.id,
            content="Test content",
            chunk_index=0,
            content_hash="mgmt123",
        )

        # Act & Assert - Add embedding models
        chunk.add_embedding_model("model1", set_as_primary=True)
        assert chunk.embedding_models == ["model1"]
        assert chunk.primary_embedding_model == "model1"

        chunk.add_embedding_model("model2")
        assert chunk.embedding_models == ["model1", "model2"]
        assert chunk.primary_embedding_model == "model1"  # Still primary

        chunk.add_embedding_model("model3", set_as_primary=True)
        assert chunk.embedding_models == ["model1", "model2", "model3"]
        assert chunk.primary_embedding_model == "model3"  # New primary

        # Remove non-primary model
        chunk.remove_embedding_model("model2")
        assert chunk.embedding_models == ["model1", "model3"]
        assert chunk.primary_embedding_model == "model3"

        # Remove primary model
        chunk.remove_embedding_model("model3")
        assert chunk.embedding_models == ["model1"]
        assert chunk.primary_embedding_model == "model1"  # Auto-updated

        # Remove last model
        chunk.remove_embedding_model("model1")
        assert chunk.embedding_models == []
        assert chunk.primary_embedding_model is None

    def test_chunk_with_metadata(self, test_document: Document):
        """Test chunk with extra metadata."""
        # Arrange & Act
        chunk = DocumentChunk(
            document_id=test_document.id,
            content="Metadata content",
            chunk_index=0,
            content_hash="meta123",
            extra_metadata={
                "section": "introduction",
                "page": 1,
                "confidence": 0.95
            }
        )

        # Assert
        assert chunk.extra_metadata["section"] == "introduction"
        assert chunk.extra_metadata["page"] == 1
        assert chunk.extra_metadata["confidence"] == 0.95

    def test_chunk_properties(self, test_document: Document):
        """Test chunk properties."""
        # Arrange
        # Chunk with embeddings
        chunk_with_embeddings = DocumentChunk(
            document_id=test_document.id,
            content="Embedded",
            chunk_index=0,
            content_hash="props1",
            embedding_models=["model1"],
        )
        
        # Chunk without embeddings
        chunk_without_embeddings = DocumentChunk(
            document_id=test_document.id,
            content="Not embedded",
            chunk_index=1,
            content_hash="props2",
        )

        # Assert
        assert chunk_with_embeddings.has_dynamic_embeddings is True
        assert chunk_without_embeddings.has_dynamic_embeddings is False

    def test_chunk_to_dict(self, test_document: Document):
        """Test chunk to dictionary conversion."""
        # Arrange
        chunk = DocumentChunk(
            document_id=test_document.id,
            content="Dict chunk content",
            chunk_index=0,
            start_char=0,
            end_char=18,
            content_hash="dict123",
            token_count=15,
            language="en",
            embedding_models=["model1"],
            primary_embedding_model="model1",
            embedding_provider="openai",
            extra_metadata={"key": "value"}
        )
        
        # Mock timestamps
        chunk.created_at = datetime(2023, 1, 1, 12, 0, 0)
        chunk.updated_at = datetime(2023, 1, 1, 12, 5, 0)
        chunk.embedding_created_at = datetime(2023, 1, 1, 12, 1, 0)

        # Act
        result = chunk.to_dict()

        # Assert
        assert result["id"] == chunk.id
        assert result["document_id"] == test_document.id
        assert result["content"] == "Dict chunk content"
        assert result["chunk_index"] == 0
        assert result["start_char"] == 0
        assert result["end_char"] == 18
        assert result["content_hash"] == "dict123"
        assert result["token_count"] == 15
        assert result["language"] == "en"
        assert result["embedding_models"] == ["model1"]
        assert result["primary_embedding_model"] == "model1"
        assert result["embedding_provider"] == "openai"
        assert result["extra_metadata"] == {"key": "value"}
        assert "2023-01-01T12:00:00" in result["created_at"]
        assert "2023-01-01T12:05:00" in result["updated_at"]
        assert "2023-01-01T12:01:00" in result["embedding_created_at"]

    def test_chunk_repr(self, test_document: Document):
        """Test chunk string representation."""
        # Arrange
        chunk = DocumentChunk(
            document_id=test_document.id,
            content="This is a very long chunk content that should be truncated in the repr",
            chunk_index=5,
            content_hash="repr123",
        )

        # Act
        repr_str = repr(chunk)

        # Assert
        assert "DocumentChunk" in repr_str
        assert chunk.id in repr_str
        assert test_document.id in repr_str
        assert "index=5" in repr_str
        assert "This is a very long chunk content that should be..." in repr_str

    def test_document_status_enum(self):
        """Test document status enumeration."""
        # Assert
        assert DocumentStatus.PENDING == "pending"
        assert DocumentStatus.PROCESSING == "processing"
        assert DocumentStatus.PROCESSED == "processed"
        assert DocumentStatus.FAILED == "failed"
        assert DocumentStatus.ARCHIVED == "archived"

    def test_document_type_enum(self):
        """Test document type enumeration."""
        # Assert
        assert DocumentType.PDF == "pdf"
        assert DocumentType.TEXT == "text"
        assert DocumentType.MARKDOWN == "markdown"
        assert DocumentType.HTML == "html"
        assert DocumentType.DOC == "doc"
        assert DocumentType.DOCX == "docx"
        assert DocumentType.CSV == "csv"
        assert DocumentType.JSON == "json"
        assert DocumentType.OTHER == "other"


@pytest.mark.integration
class TestDocumentModelIntegration:
    """Integration tests for document models."""

    def test_document_chunk_relationship(self, test_user: User, test_session):
        """Test document-chunk relationship."""
        # Arrange
        document = Document(
            owner_id=test_user.id,
            filename="test.txt",
            original_filename="test.txt",
            file_size=100,
            file_hash="test123",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
        )
        test_session.add(document)
        test_session.commit()

        # Act
        chunk1 = DocumentChunk(
            document_id=document.id,
            content="First chunk",
            chunk_index=0,
            content_hash="chunk1",
        )
        chunk2 = DocumentChunk(
            document_id=document.id,
            content="Second chunk",
            chunk_index=1,
            content_hash="chunk2",
        )
        
        test_session.add_all([chunk1, chunk2])
        test_session.commit()

        # Refresh to load relationships
        test_session.refresh(document)

        # Assert
        assert len(document.chunks) == 2
        assert document.chunks[0].content == "First chunk"
        assert document.chunks[1].content == "Second chunk"
        assert document.chunks[0].document == document
        assert document.chunks[1].document == document

    def test_document_user_relationship(self, test_user: User, test_session):
        """Test document-user relationship."""
        # Arrange & Act
        document = Document(
            owner_id=test_user.id,
            filename="user_doc.txt",
            original_filename="user_doc.txt",
            file_size=100,
            file_hash="user123",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
        )
        test_session.add(document)
        test_session.commit()

        # Refresh to load relationships
        test_session.refresh(document)
        test_session.refresh(test_user)

        # Assert
        assert document.owner == test_user
        assert document in test_user.documents

    def test_document_version_relationship(self, test_user: User, test_session):
        """Test document parent-child relationship."""
        # Arrange
        parent = Document(
            owner_id=test_user.id,
            filename="parent.txt",
            original_filename="parent.txt",
            file_size=100,
            file_hash="parent123",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            version=1,
        )
        test_session.add(parent)
        test_session.commit()

        # Act
        child = Document(
            owner_id=test_user.id,
            filename="child.txt",
            original_filename="child.txt",
            file_size=100,
            file_hash="child123",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            version=2,
            parent_document_id=parent.id,
        )
        test_session.add(child)
        test_session.commit()

        # Refresh to load relationships
        test_session.refresh(parent)
        test_session.refresh(child)

        # Assert
        assert child.parent_document == parent
        assert child in parent.child_documents