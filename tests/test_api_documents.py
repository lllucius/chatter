"""Tests for document processing API endpoints."""

from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.api.auth import get_current_user
from chatter.main import app
from chatter.models.document import Document
from chatter.models.user import User


@pytest.mark.unit
class TestDocumentEndpoints:
    """Test document processing API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True
        )

        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_upload_document_success(self):
        """Test successful document upload."""
        # Arrange
        file_content = b"This is a test document content."
        file_data = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

        mock_document = Document(
            id="doc-123",
            title="test.txt",
            content="This is a test document content.",
            user_id=self.mock_user.id,
            file_type="text/plain",
            file_size=len(file_content)
        )

        with patch('chatter.services.document_processing.DocumentProcessor.process_document') as mock_process:
            mock_process.return_value = mock_document

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post(
                "/api/v1/documents/upload",
                files=file_data,
                headers=headers
            )

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            response_data = response.json()
            assert response_data["id"] == "doc-123"
            assert response_data["title"] == "test.txt"

    def test_upload_document_invalid_file_type(self):
        """Test document upload with invalid file type."""
        # Arrange
        file_content = b"Binary content"
        file_data = {"file": ("test.exe", BytesIO(file_content), "application/x-executable")}

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.post(
            "/api/v1/documents/upload",
            files=file_data,
            headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_document_too_large(self):
        """Test document upload with file too large."""
        # Arrange
        large_content = b"x" * (10 * 1024 * 1024 + 1)  # > 10MB
        file_data = {"file": ("large.txt", BytesIO(large_content), "text/plain")}

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.post(
            "/api/v1/documents/upload",
            files=file_data,
            headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    def test_get_documents_success(self):
        """Test retrieving user documents."""
        # Arrange
        mock_documents = [
            Document(
                id="doc-1",
                title="Document 1",
                content="Content 1",
                user_id=self.mock_user.id
            ),
            Document(
                id="doc-2",
                title="Document 2",
                content="Content 2",
                user_id=self.mock_user.id
            )
        ]

        with patch('chatter.services.document_processing.DocumentProcessor.get_user_documents') as mock_get:
            mock_get.return_value = mock_documents

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get("/api/v1/documents", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert len(response_data["documents"]) == 2

    def test_get_document_by_id_success(self):
        """Test retrieving specific document."""
        # Arrange
        document_id = "doc-123"
        mock_document = Document(
            id=document_id,
            title="Test Document",
            content="Test content",
            user_id=self.mock_user.id
        )

        with patch('chatter.services.document_processing.DocumentProcessor.get_document') as mock_get:
            mock_get.return_value = mock_document

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/documents/{document_id}", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["id"] == document_id

    def test_get_document_not_found(self):
        """Test retrieving non-existent document."""
        # Arrange
        document_id = "non-existent"

        with patch('chatter.services.document_processing.DocumentProcessor.get_document') as mock_get:
            from chatter.core.exceptions import NotFoundError
            mock_get.side_effect = NotFoundError("Document not found")

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/documents/{document_id}", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_document_success(self):
        """Test updating document metadata."""
        # Arrange
        document_id = "doc-123"
        update_data = {
            "title": "Updated Title",
            "tags": ["updated", "test"]
        }

        mock_document = Document(
            id=document_id,
            title=update_data["title"],
            content="Original content",
            user_id=self.mock_user.id
        )

        with patch('chatter.services.document_processing.DocumentProcessor.update_document') as mock_update:
            mock_update.return_value = mock_document

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.put(
                f"/api/v1/documents/{document_id}",
                json=update_data,
                headers=headers
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["title"] == update_data["title"]

    def test_delete_document_success(self):
        """Test deleting a document."""
        # Arrange
        document_id = "doc-123"

        with patch('chatter.services.document_processing.DocumentProcessor.delete_document') as mock_delete:
            mock_delete.return_value = True

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.delete(f"/api/v1/documents/{document_id}", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["message"] == "Document deleted successfully"

    def test_search_documents_success(self):
        """Test document search functionality."""
        # Arrange
        search_query = "test content"

        mock_results = [
            Document(
                id="doc-1",
                title="Test Document",
                content="This contains test content",
                user_id=self.mock_user.id
            )
        ]

        with patch('chatter.services.document_processing.DocumentProcessor.search_documents') as mock_search:
            mock_search.return_value = mock_results

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(
                f"/api/v1/documents/search?q={search_query}",
                headers=headers
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert len(response_data["documents"]) == 1

    def test_process_document_with_chunking(self):
        """Test document processing with chunking."""
        # Arrange
        document_id = "doc-123"
        processing_options = {
            "chunk_size": 1000,
            "chunk_overlap": 100,
            "extract_metadata": True
        }

        mock_chunks = [
            {"id": "chunk-1", "content": "First chunk", "metadata": {}},
            {"id": "chunk-2", "content": "Second chunk", "metadata": {}}
        ]

        with patch('chatter.services.document_processing.DocumentProcessor.process_with_chunking') as mock_process:
            mock_process.return_value = mock_chunks

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post(
                f"/api/v1/documents/{document_id}/process",
                json=processing_options,
                headers=headers
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert len(response_data["chunks"]) == 2

    def test_extract_document_metadata(self):
        """Test extracting metadata from document."""
        # Arrange
        document_id = "doc-123"

        mock_metadata = {
            "author": "Test Author",
            "created_date": "2024-01-01",
            "word_count": 150,
            "language": "en",
            "topics": ["testing", "documents"]
        }

        with patch('chatter.services.document_processing.DocumentProcessor.extract_metadata') as mock_extract:
            mock_extract.return_value = mock_metadata

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/documents/{document_id}/metadata", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["author"] == "Test Author"
            assert response_data["word_count"] == 150

    def test_document_analytics(self):
        """Test getting document analytics."""
        # Arrange
        mock_analytics = {
            "total_documents": 25,
            "total_size": "15.7 MB",
            "file_types": {
                "pdf": 10,
                "txt": 8,
                "docx": 7
            },
            "processing_status": {
                "completed": 20,
                "processing": 3,
                "failed": 2
            }
        }

        with patch('chatter.services.document_processing.DocumentProcessor.get_analytics') as mock_analytics_func:
            mock_analytics_func.return_value = mock_analytics

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get("/api/v1/documents/analytics", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["total_documents"] == 25

    def test_bulk_document_upload(self):
        """Test bulk document upload."""
        # Arrange
        files = [
            ("files", ("doc1.txt", BytesIO(b"Content 1"), "text/plain")),
            ("files", ("doc2.txt", BytesIO(b"Content 2"), "text/plain")),
        ]

        mock_results = [
            {"id": "doc-1", "title": "doc1.txt", "status": "success"},
            {"id": "doc-2", "title": "doc2.txt", "status": "success"}
        ]

        with patch('chatter.services.document_processing.DocumentProcessor.bulk_upload') as mock_bulk:
            mock_bulk.return_value = mock_results

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post(
                "/api/v1/documents/bulk-upload",
                files=files,
                headers=headers
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert len(response_data["results"]) == 2


@pytest.mark.integration
class TestDocumentIntegration:
    """Integration tests for document processing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="integration-user-id",
            email="integration@example.com",
            username="integrationuser"
        )

        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_document_processing_workflow(self):
        """Test complete document processing workflow."""
        # Upload document
        file_content = b"This is a comprehensive test document for processing workflow."
        file_data = {"file": ("workflow_test.txt", BytesIO(file_content), "text/plain")}

        mock_document = Document(
            id="workflow-doc-id",
            title="workflow_test.txt",
            content=file_content.decode(),
            user_id=self.mock_user.id
        )

        with patch('chatter.services.document_processing.DocumentProcessor.process_document') as mock_process:
            mock_process.return_value = mock_document

            headers = {"Authorization": "Bearer integration-token"}

            # Upload
            upload_response = self.client.post(
                "/api/v1/documents/upload",
                files=file_data,
                headers=headers
            )

            assert upload_response.status_code == status.HTTP_201_CREATED
            doc_id = upload_response.json()["id"]

            # Process with chunking
            with patch('chatter.services.document_processing.DocumentProcessor.process_with_chunking') as mock_chunk:
                mock_chunk.return_value = [
                    {"id": "chunk-1", "content": "First part of document", "metadata": {}},
                    {"id": "chunk-2", "content": "Second part of document", "metadata": {}}
                ]

                process_response = self.client.post(
                    f"/api/v1/documents/{doc_id}/process",
                    json={"chunk_size": 1000},
                    headers=headers
                )

                assert process_response.status_code == status.HTTP_200_OK

                # Extract metadata
                with patch('chatter.services.document_processing.DocumentProcessor.extract_metadata') as mock_meta:
                    mock_meta.return_value = {"word_count": 50, "language": "en"}

                    metadata_response = self.client.get(
                        f"/api/v1/documents/{doc_id}/metadata",
                        headers=headers
                    )

                    assert metadata_response.status_code == status.HTTP_200_OK

                    # Search for document
                    with patch('chatter.services.document_processing.DocumentProcessor.search_documents') as mock_search:
                        mock_search.return_value = [mock_document]

                        search_response = self.client.get(
                            "/api/v1/documents/search?q=workflow",
                            headers=headers
                        )

                        assert search_response.status_code == status.HTTP_200_OK
                        assert len(search_response.json()["documents"]) == 1
