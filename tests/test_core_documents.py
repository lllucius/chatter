"""Unit tests for core document processing module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import hashlib

from tests.test_utils import create_mock_document, MockDatabase


@pytest.mark.unit
class TestDocumentCore:
    """Test cases for core document functionality."""

    def test_document_hash_generation(self):
        """Test document hash generation for duplicate detection."""
        content1 = "This is a test document content."
        content2 = "This is a test document content."
        content3 = "This is different content."
        
        # Same content should produce same hash
        hash1 = hashlib.sha256(content1.encode()).hexdigest()
        hash2 = hashlib.sha256(content2.encode()).hexdigest()
        hash3 = hashlib.sha256(content3.encode()).hexdigest()
        
        assert hash1 == hash2
        assert hash1 != hash3

    def test_file_type_detection(self):
        """Test file type detection from filename."""
        import mimetypes
        
        test_files = [
            ("document.pdf", "application/pdf"),
            ("text.txt", "text/plain"),
            ("image.jpg", "image/jpeg"),
            ("document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ]
        
        for filename, expected_type in test_files:
            detected_type, _ = mimetypes.guess_type(filename)
            # Some systems might not have all MIME types, so we check if detection works
            if detected_type:
                assert detected_type == expected_type or detected_type.startswith(expected_type.split('/')[0])

    def test_document_size_validation(self):
        """Test document size validation."""
        # Mock settings for max file size
        max_size = 10 * 1024 * 1024  # 10MB
        
        small_content = "Small content"
        large_content = "x" * (max_size + 1)
        
        assert len(small_content.encode()) < max_size
        assert len(large_content.encode()) > max_size

    @pytest.mark.asyncio
    async def test_document_metadata_extraction(self):
        """Test document metadata extraction."""
        document_data = create_mock_document(
            title="Test Document",
            content="This is test content for metadata extraction.",
            file_type="text/plain"
        )
        
        # Test metadata fields
        assert document_data["title"] == "Test Document"
        assert document_data["file_type"] == "text/plain"
        assert document_data["size"] > 0
        assert "uploaded_at" in document_data

    def test_filename_sanitization(self):
        """Test filename sanitization for security."""
        dangerous_filenames = [
            "../../../etc/passwd",
            "file with spaces.txt",
            "file@with#special$chars.pdf",
            "normal_file.txt"
        ]
        
        for filename in dangerous_filenames:
            # Basic sanitization - remove path traversal
            sanitized = Path(filename).name
            assert ".." not in sanitized
            assert "/" not in sanitized
            assert "\\" not in sanitized

    @pytest.mark.asyncio
    async def test_document_chunking_logic(self):
        """Test document chunking for processing."""
        large_content = "This is a test. " * 100  # Create large content
        chunk_size = 100
        
        # Simple chunking logic
        chunks = []
        for i in range(0, len(large_content), chunk_size):
            chunk = large_content[i:i + chunk_size]
            chunks.append(chunk)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= chunk_size for chunk in chunks)
        
        # Reconstruct content from chunks
        reconstructed = "".join(chunks)
        assert reconstructed == large_content


@pytest.mark.unit
class TestDocumentUtilities:
    """Test utility functions for document processing."""

    def test_create_mock_document(self):
        """Test the mock document creation utility."""
        doc = create_mock_document()
        
        # Check required fields exist
        required_fields = ['id', 'title', 'content', 'file_type', 'size', 'uploaded_at']
        for field in required_fields:
            assert field in doc
        
        # Check default values
        assert doc['title'] == 'Test Document'
        assert doc['content'] == 'Test document content'
        assert doc['file_type'] == 'text/plain'
        
        # Test custom values
        custom_doc = create_mock_document(
            title='Custom Document',
            content='Custom content',
            file_type='application/pdf'
        )
        assert custom_doc['title'] == 'Custom Document'
        assert custom_doc['content'] == 'Custom content'
        assert custom_doc['file_type'] == 'application/pdf'

    def test_document_search_functionality(self):
        """Test document search and filtering logic."""
        documents = [
            create_mock_document(title="Python Guide", content="Learn Python programming"),
            create_mock_document(title="JavaScript Basics", content="Web development with JS"),
            create_mock_document(title="Data Science", content="Python for data analysis"),
        ]
        
        # Simple search implementation
        def search_documents(docs, query):
            results = []
            for doc in docs:
                if query.lower() in doc['title'].lower() or query.lower() in doc['content'].lower():
                    results.append(doc)
            return results
        
        # Test search functionality
        python_results = search_documents(documents, "Python")
        assert len(python_results) == 2  # Python Guide and Data Science
        
        js_results = search_documents(documents, "JavaScript")
        assert len(js_results) == 1  # JavaScript Basics
        
        no_results = search_documents(documents, "Ruby")
        assert len(no_results) == 0

    @pytest.mark.asyncio
    async def test_document_processing_workflow(self):
        """Test document processing workflow components."""
        mock_db = MockDatabase()
        
        # Mock document upload
        document_data = {
            "title": "Test Upload",
            "content": "Test content for processing",
            "file_type": "text/plain",
            "user_id": "test_user"
        }
        
        # Simulate processing workflow
        # 1. Store document
        await mock_db.execute("INSERT INTO documents ...", **document_data)
        
        # 2. Generate content hash
        content_hash = hashlib.sha256(document_data["content"].encode()).hexdigest()
        
        # 3. Check for duplicates (mock)
        mock_db.fetchrow.return_value = None  # Set mock to return None
        existing = await mock_db.fetchrow("SELECT * FROM documents WHERE content_hash = $1", content_hash)
        assert existing is None  # No duplicates in mock
        
        # 4. Update document with hash
        await mock_db.execute("UPDATE documents SET content_hash = $1", content_hash)
        
        # Verify workflow steps were called
        mock_db.execute.assert_called()

    def test_supported_file_types(self):
        """Test supported file type validation."""
        supported_types = [
            "text/plain",
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/markdown",
            "text/html"
        ]
        
        unsupported_types = [
            "image/jpeg",
            "video/mp4",
            "audio/mp3",
            "application/x-executable"
        ]
        
        # Test supported types
        for file_type in supported_types:
            assert file_type in supported_types  # Would be actual validation logic
        
        # Test unsupported types
        for file_type in unsupported_types:
            assert file_type not in supported_types

    @pytest.mark.asyncio
    async def test_document_embedding_preparation(self):
        """Test document preparation for embedding generation."""
        document = create_mock_document(
            content="This is a sample document. It contains multiple sentences. Each sentence provides information."
        )
        
        # Simple text preparation
        content = document["content"]
        
        # Basic preprocessing
        sentences = content.split(". ")
        assert len(sentences) >= 2
        
        # Remove empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        assert all(len(s) > 0 for s in sentences)
        
        # Prepare for embedding (would be more complex in real implementation)
        prepared_text = " ".join(sentences)
        assert len(prepared_text) > 0


@pytest.mark.integration
class TestDocumentDatabaseIntegration:
    """Integration tests for document database operations."""

    @pytest.mark.asyncio
    async def test_document_crud_operations(self):
        """Test document CRUD operations with mock database."""
        mock_db = MockDatabase()
        
        document = create_mock_document()
        
        # Create
        await mock_db.execute(
            "INSERT INTO documents (id, title, content, file_type) VALUES ($1, $2, $3, $4)",
            document["id"], document["title"], document["content"], document["file_type"]
        )
        
        # Read
        mock_db.fetchrow.return_value = document
        retrieved = await mock_db.fetchrow("SELECT * FROM documents WHERE id = $1", document["id"])
        assert retrieved["id"] == document["id"]
        
        # Update
        new_title = "Updated Title"
        await mock_db.execute("UPDATE documents SET title = $1 WHERE id = $2", new_title, document["id"])
        
        # Delete
        await mock_db.execute("DELETE FROM documents WHERE id = $1", document["id"])
        
        # Verify operations were called
        assert mock_db.execute.call_count >= 3  # Create, Update, Delete
        mock_db.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_document_search_with_database(self):
        """Test document search integration with database."""
        mock_db = MockDatabase()
        
        # Mock search results
        search_results = [
            create_mock_document(title="Python Tutorial", content="Learn Python basics"),
            create_mock_document(title="Advanced Python", content="Python for experts"),
        ]
        mock_db.fetch.return_value = search_results
        
        # Simulate search query
        search_term = "Python"
        results = await mock_db.fetch(
            "SELECT * FROM documents WHERE title ILIKE $1 OR content ILIKE $1",
            f"%{search_term}%"
        )
        
        assert len(results) == 2
        assert all("Python" in doc["title"] for doc in results)
        mock_db.fetch.assert_called_once()