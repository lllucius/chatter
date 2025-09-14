"""Simple integration test for the embedding pipeline without full database setup."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from chatter.core.embedding_pipeline import (
    DocumentTextExtractor,
    DocumentChunker,
    SimpleEmbeddingService,
    SimpleVectorStore,
    EmbeddingPipeline,
)
from chatter.models.document import Document, DocumentChunk, DocumentType, DocumentStatus


@pytest.mark.asyncio
async def test_embedding_pipeline_mock_integration():
    """Test the embedding pipeline with mocked dependencies."""
    
    # Create test document
    document = Document(
        id="test-doc-123",
        owner_id="test-user",
        filename="test.txt",
        original_filename="test.txt",
        file_size=100,
        file_hash="hash123",
        mime_type="text/plain",
        document_type=DocumentType.TEXT,
        chunk_size=200,
        chunk_overlap=50
    )
    
    # Mock session
    mock_session = AsyncMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = document
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()
    
    # Create pipeline with mocked components
    pipeline = EmbeddingPipeline(mock_session)
    
    # Mock the embedding service
    async def mock_generate_embeddings(texts):
        embeddings = [[0.1] * 1536 for _ in texts]
        metadata = {"provider": "mock", "model": "mock-model", "dimensions": 1536}
        return embeddings, metadata
    
    pipeline.embedding_service.generate_embeddings = mock_generate_embeddings
    
    # Test document processing
    file_content = b"This is a test document with some content to be processed and embedded."
    
    # Process document
    success = await pipeline.process_document(document.id, file_content)
    
    # Verify the process was called
    assert mock_session.execute.called
    assert mock_session.commit.called


@pytest.mark.asyncio  
async def test_text_extractor_integration():
    """Test text extractor with different document types."""
    extractor = DocumentTextExtractor()
    
    # Test plain text
    doc = Document(
        id="test", owner_id="user", filename="test.txt", original_filename="test.txt",
        file_size=50, file_hash="hash", mime_type="text/plain", 
        document_type=DocumentType.TEXT, chunk_size=100, chunk_overlap=20
    )
    
    content = b"Hello world! This is a test document."
    result = await extractor.extract_text(doc, content)
    assert result == "Hello world! This is a test document."
    
    # Test markdown
    doc.document_type = DocumentType.MARKDOWN
    doc.mime_type = "text/markdown"
    markdown_content = b"# Title\n\nThis is **bold** text."
    result = await extractor.extract_text(doc, markdown_content)
    assert "# Title" in result
    assert "bold" in result


def test_document_chunker_integration():
    """Test document chunker with different settings."""
    chunker = DocumentChunker()
    
    doc = Document(
        id="test", owner_id="user", filename="test.txt", original_filename="test.txt",
        file_size=200, file_hash="hash", mime_type="text/plain",
        document_type=DocumentType.TEXT, chunk_size=100, chunk_overlap=20
    )
    
    # Test with text that should create multiple chunks
    text = "This is sentence one. " * 20  # Long text
    
    chunks = chunker.create_chunks(doc, text)
    
    assert len(chunks) > 1
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk.strip()) > 0 for chunk in chunks)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])