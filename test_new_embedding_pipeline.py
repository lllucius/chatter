"""Test for the new simplified document embedding pipeline.

This tests the core functionality of the rewritten pipeline.
"""

import asyncio
import tempfile
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from chatter.core.embedding_pipeline import (
    DocumentTextExtractor,
    DocumentChunker,
    EmbeddingPipelineError,
)
from chatter.models.document import Document, DocumentType


class TestDocumentTextExtractor:
    """Test the document text extractor."""
    
    @pytest.mark.asyncio
    async def test_extract_plain_text(self):
        """Test plain text extraction."""
        extractor = DocumentTextExtractor()
        
        # Create a mock document
        document = Document(
            id="test-doc",
            owner_id="test-user", 
            filename="test.txt",
            original_filename="test.txt",
            file_size=100,
            file_hash="abcd1234",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            chunk_size=1000,
            chunk_overlap=200
        )
        
        content = b"This is a test document with some content."
        
        result = await extractor.extract_text(document, content)
        assert result == "This is a test document with some content."
    
    @pytest.mark.asyncio
    async def test_extract_markdown(self):
        """Test markdown extraction."""
        extractor = DocumentTextExtractor()
        
        document = Document(
            id="test-doc",
            owner_id="test-user",
            filename="test.md",
            original_filename="test.md", 
            file_size=100,
            file_hash="abcd1234",
            mime_type="text/markdown",
            document_type=DocumentType.MARKDOWN,
            chunk_size=1000,
            chunk_overlap=200
        )
        
        content = b"# Test Document\n\nThis is a **markdown** document."
        
        result = await extractor.extract_text(document, content)
        assert "# Test Document" in result
        assert "markdown" in result
    
    @pytest.mark.asyncio
    async def test_extract_json(self):
        """Test JSON extraction."""
        extractor = DocumentTextExtractor()
        
        document = Document(
            id="test-doc",
            owner_id="test-user",
            filename="test.json",
            original_filename="test.json",
            file_size=100,
            file_hash="abcd1234", 
            mime_type="application/json",
            document_type=DocumentType.JSON,
            chunk_size=1000,
            chunk_overlap=200
        )
        
        content = b'{"title": "Test Document", "content": "This is test content"}'
        
        result = await extractor.extract_text(document, content)
        assert "Test Document" in result
        assert "This is test content" in result


class TestDocumentChunker:
    """Test the document chunker."""
    
    def test_create_chunks_basic(self):
        """Test basic chunk creation."""
        chunker = DocumentChunker()
        
        document = Document(
            id="test-doc",
            owner_id="test-user",
            filename="test.txt",
            original_filename="test.txt",
            file_size=100,
            file_hash="abcd1234",
            mime_type="text/plain",
            document_type=DocumentType.TEXT,
            chunk_size=100,
            chunk_overlap=20
        )
        
        text = "This is a test document. " * 20  # Long enough to create multiple chunks
        
        chunks = chunker.create_chunks(document, text)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 100 + 20 for chunk in chunks)  # Account for overlap
        assert all(len(chunk.strip()) >= 50 for chunk in chunks)  # Min length filter
    
    def test_create_chunks_markdown(self):
        """Test chunk creation for markdown."""
        chunker = DocumentChunker()
        
        document = Document(
            id="test-doc",
            owner_id="test-user",
            filename="test.md",
            original_filename="test.md",
            file_size=100,
            file_hash="abcd1234",
            mime_type="text/markdown",
            document_type=DocumentType.MARKDOWN,
            chunk_size=200,
            chunk_overlap=50
        )
        
        text = """# Chapter 1
This is the first chapter with some content.

## Section 1.1
This is a subsection with more content.

# Chapter 2
This is the second chapter with different content."""
        
        chunks = chunker.create_chunks(document, text)
        
        assert len(chunks) >= 1
        # Should split on markdown headers
        assert any("Chapter 1" in chunk for chunk in chunks)


class TestEmbeddingPipelineError:
    """Test the custom exception."""
    
    def test_embedding_pipeline_error(self):
        """Test custom exception creation."""
        error = EmbeddingPipelineError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)


@pytest.mark.asyncio
async def test_integration_text_extraction_and_chunking():
    """Integration test for text extraction and chunking."""
    extractor = DocumentTextExtractor()
    chunker = DocumentChunker()
    
    # Create test document
    document = Document(
        id="test-doc",
        owner_id="test-user",
        filename="test.txt",
        original_filename="test.txt",
        file_size=500,
        file_hash="abcd1234",
        mime_type="text/plain",
        document_type=DocumentType.TEXT,
        chunk_size=100,
        chunk_overlap=20
    )
    
    # Create test content
    content = b"This is a long test document. " * 50  # Create long content
    
    # Extract text
    extracted_text = await extractor.extract_text(document, content)
    assert len(extracted_text) > 0
    
    # Create chunks
    chunks = chunker.create_chunks(document, extracted_text)
    assert len(chunks) > 1
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk.strip()) > 0 for chunk in chunks)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])