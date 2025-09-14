"""Integration tests for the new document embedding pipeline.

These tests validate the complete end-to-end workflow.
"""

import asyncio
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from chatter.config import settings
from chatter.core.embedding_pipeline import EmbeddingPipeline
from chatter.models.base import Base
from chatter.models.document import Document, DocumentChunk, DocumentStatus, DocumentType
from chatter.services.new_document_service import NewDocumentService
from chatter.schemas.document import DocumentCreate


@pytest.fixture
async def test_engine():
    """Create a test database engine."""
    # Use SQLite for testing to avoid external dependencies
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create a test database session."""
    session_maker = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with session_maker() as session:
        yield session


@pytest.fixture
def sample_text_file():
    """Create a sample text file for testing."""
    content = """
# Sample Document

This is a sample document for testing the embedding pipeline.

## Introduction

The document contains multiple paragraphs and sections to test chunking.

## Content

Here is some content that should be processed and embedded.
The content is long enough to create multiple chunks when processed.

## Conclusion

This concludes the sample document.
    """.strip()
    
    return content.encode('utf-8')


@pytest.fixture
def mock_embedding_service(monkeypatch):
    """Mock the embedding service to avoid external API calls."""
    async def mock_generate_embeddings(self, texts):
        # Return mock embeddings (1536 dimensions with random-ish values)
        embeddings = []
        for i, text in enumerate(texts):
            # Create a deterministic embedding based on text content
            embedding = [0.1 * (i + 1) + 0.01 * (ord(c) % 100) for c in text[:1536]]
            # Pad or truncate to exactly 1536 dimensions
            if len(embedding) < 1536:
                embedding.extend([0.0] * (1536 - len(embedding)))
            else:
                embedding = embedding[:1536]
            embeddings.append(embedding)
        
        metadata = {
            "provider": "mock",
            "model": "mock-embedding-model",
            "dimensions": 1536,
            "text_count": len(texts)
        }
        
        return embeddings, metadata
    
    # Mock the SimpleEmbeddingService
    from chatter.core.embedding_pipeline import SimpleEmbeddingService
    monkeypatch.setattr(
        SimpleEmbeddingService, 
        "generate_embeddings", 
        mock_generate_embeddings
    )


class TestEmbeddingPipelineIntegration:
    """Integration tests for the embedding pipeline."""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_text_document(
        self, test_session, sample_text_file, mock_embedding_service
    ):
        """Test complete pipeline with a text document."""
        # Create a document record
        document = Document(
            owner_id="test-user-123",
            filename="test.txt",
            original_filename="sample.txt",
            file_size=len(sample_text_file),
            file_hash="sample-hash",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            title="Sample Document",
            chunk_size=500,
            chunk_overlap=100
        )
        
        test_session.add(document)
        await test_session.commit()
        await test_session.refresh(document)
        
        # Process the document
        pipeline = EmbeddingPipeline(test_session)
        success = await pipeline.process_document(document.id, sample_text_file)
        
        assert success is True
        
        # Verify document status
        await test_session.refresh(document)
        assert document.status == DocumentStatus.PROCESSED
        assert document.extracted_text is not None
        assert document.chunk_count > 0
        
        # Verify chunks were created
        result = await test_session.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document.id)
        )
        chunks = result.scalars().all()
        
        assert len(chunks) > 0
        assert all(chunk.embedding is not None for chunk in chunks)
        assert all(chunk.embedding_provider == "mock" for chunk in chunks)
        assert all(chunk.embedding_model == "mock-embedding-model" for chunk in chunks)
        assert all(len(chunk.embedding) == 1536 for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_search_documents(
        self, test_session, sample_text_file, mock_embedding_service
    ):
        """Test document search functionality."""
        # Create and process a document
        document = Document(
            owner_id="test-user-123",
            filename="test.txt",
            original_filename="sample.txt",
            file_size=len(sample_text_file),
            file_hash="sample-hash",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            title="Sample Document",
            chunk_size=200,
            chunk_overlap=50
        )
        
        test_session.add(document)
        await test_session.commit()
        await test_session.refresh(document)
        
        # Process the document
        pipeline = EmbeddingPipeline(test_session)
        await pipeline.process_document(document.id, sample_text_file)
        
        # Perform search
        results = await pipeline.search_documents(
            query="sample document testing",
            limit=5,
            document_ids=[document.id]
        )
        
        assert len(results) > 0
        
        # Verify result structure
        for chunk, similarity_score in results:
            assert isinstance(chunk, DocumentChunk)
            assert isinstance(similarity_score, float)
            assert chunk.document_id == document.id
            assert chunk.embedding is not None


class TestNewDocumentService:
    """Integration tests for the new document service."""
    
    @pytest.mark.asyncio
    async def test_create_document_success(
        self, test_session, sample_text_file, mock_embedding_service
    ):
        """Test successful document creation."""
        # Mock upload file
        class MockUploadFile:
            filename = "test.txt"
            content_type = "text/plain"
            
            def __init__(self, content):
                self._content = content
                self._position = 0
            
            async def read(self, size=-1):
                if size == -1:
                    result = self._content[self._position:]
                    self._position = len(self._content)
                else:
                    result = self._content[self._position:self._position + size]
                    self._position += len(result)
                return result
            
            async def seek(self, position, whence=0):
                if whence == 0:  # SEEK_SET
                    self._position = position
                elif whence == 2:  # SEEK_END
                    self._position = len(self._content)
                return self._position
            
            async def tell(self):
                return self._position
        
        upload_file = MockUploadFile(sample_text_file)
        
        document_data = DocumentCreate(
            title="Test Document",
            description="A test document",
            tags=["test", "sample"],
            chunk_size=300,
            chunk_overlap=75,
            is_public=False
        )
        
        service = NewDocumentService(test_session)
        
        # Create document
        document = await service.create_document(
            user_id="test-user-123",
            upload_file=upload_file,
            document_data=document_data
        )
        
        assert document is not None
        assert document.title == "Test Document"
        assert document.description == "A test document"
        assert document.tags == ["test", "sample"]
        assert document.owner_id == "test-user-123"
        assert document.status in [DocumentStatus.PENDING, DocumentStatus.PROCESSING]
    
    @pytest.mark.asyncio
    async def test_get_document_with_access_control(
        self, test_session, sample_text_file
    ):
        """Test document retrieval with access control."""
        # Create a document
        document = Document(
            owner_id="test-user-123",
            filename="test.txt",
            original_filename="sample.txt",
            file_size=len(sample_text_file),
            file_hash="sample-hash",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            title="Sample Document",
            is_public=False
        )
        
        test_session.add(document)
        await test_session.commit()
        await test_session.refresh(document)
        
        service = NewDocumentService(test_session)
        
        # Owner should be able to access
        retrieved = await service.get_document(document.id, "test-user-123")
        assert retrieved is not None
        assert retrieved.id == document.id
        
        # Non-owner should not be able to access private document
        retrieved = await service.get_document(document.id, "other-user")
        assert retrieved is None
        
        # Make document public
        document.is_public = True
        await test_session.commit()
        
        # Non-owner should now be able to access public document
        retrieved = await service.get_document(document.id, "other-user")
        assert retrieved is not None
        assert retrieved.id == document.id
    
    @pytest.mark.asyncio
    async def test_delete_document(self, test_session):
        """Test document deletion."""
        # Create a document
        document = Document(
            owner_id="test-user-123",
            filename="test.txt",
            original_filename="sample.txt",
            file_size=100,
            file_hash="sample-hash",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            title="Sample Document"
        )
        
        test_session.add(document)
        await test_session.commit()
        await test_session.refresh(document)
        
        service = NewDocumentService(test_session)
        
        # Delete document
        success = await service.delete_document(document.id, "test-user-123")
        assert success is True
        
        # Verify document is deleted
        result = await test_session.execute(
            select(Document).where(Document.id == document.id)
        )
        deleted_document = result.scalar_one_or_none()
        assert deleted_document is None


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])