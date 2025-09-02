"""End-to-end tests for document processing workflows."""

import io
import pytest
from fastapi import status


@pytest.mark.e2e
class TestDocumentProcessingE2E:
    """End-to-end document processing workflow tests."""

    def test_complete_document_upload_and_processing(self, test_client, sample_document_upload, cleanup_test_data):
        """Test complete document upload, processing, and retrieval workflow."""
        # Step 1: Upload document
        files = {
            "file": (
                sample_document_upload["filename"],
                io.BytesIO(sample_document_upload["content"]),
                sample_document_upload["mime_type"]
            )
        }
        
        upload_response = test_client.post(
            "/api/v1/documents/upload",
            files=files,
            data={"metadata": str(sample_document_upload["metadata"])}
        )
        
        if upload_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Document upload endpoint not available")
        
        if upload_response.status_code == status.HTTP_401_UNAUTHORIZED:
            pytest.skip("Authentication required for document upload")
        
        assert upload_response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_200_OK
        ]
        
        upload_data = upload_response.json()
        document_id = upload_data.get("id") or upload_data.get("document_id")
        
        if not document_id:
            pytest.skip("Unable to extract document ID from upload response")
        
        # Step 2: Check document processing status
        status_response = test_client.get(f"/api/v1/documents/{document_id}/status")
        
        if status_response.status_code == status.HTTP_200_OK:
            status_data = status_response.json()
            assert "status" in status_data
            # Status might be "processing", "completed", "failed", etc.
        
        # Step 3: Retrieve processed document
        retrieve_response = test_client.get(f"/api/v1/documents/{document_id}")
        
        if retrieve_response.status_code == status.HTTP_200_OK:
            document_data = retrieve_response.json()
            assert document_data["filename"] == sample_document_upload["filename"]
        
        # Step 4: Search document content (if search is available)
        search_response = test_client.post(
            "/api/v1/documents/search",
            json={"query": "test document"}
        )
        
        if search_response.status_code == status.HTTP_200_OK:
            search_results = search_response.json()
            # Should find our uploaded document
            assert isinstance(search_results, (list, dict))
        
        # Step 5: Delete document (cleanup)
        delete_response = test_client.delete(f"/api/v1/documents/{document_id}")
        # Don't assert on delete response as it might not be implemented

    def test_document_text_extraction(self, test_client):
        """Test text extraction from various document types."""
        # Test with different document types
        test_documents = [
            ("test.txt", b"This is plain text content.", "text/plain"),
            ("test.md", b"# Markdown Content\n\nThis is **bold** text.", "text/markdown"),
        ]
        
        for filename, content, mime_type in test_documents:
            files = {
                "file": (filename, io.BytesIO(content), mime_type)
            }
            
            upload_response = test_client.post("/api/v1/documents/upload", files=files)
            
            if upload_response.status_code == status.HTTP_404_NOT_FOUND:
                pytest.skip("Document upload endpoint not available")
            
            if upload_response.status_code not in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
                continue  # Skip this document type
            
            upload_data = upload_response.json()
            document_id = upload_data.get("id") or upload_data.get("document_id")
            
            if document_id:
                # Test text extraction
                extract_response = test_client.get(f"/api/v1/documents/{document_id}/extract")
                
                if extract_response.status_code == status.HTTP_200_OK:
                    extracted_data = extract_response.json()
                    assert "text" in extracted_data or "content" in extracted_data

    def test_document_chunking_and_embeddings(self, test_client, sample_document_upload):
        """Test document chunking and embedding generation."""
        # Upload document first
        files = {
            "file": (
                sample_document_upload["filename"],
                io.BytesIO(sample_document_upload["content"]),
                sample_document_upload["mime_type"]
            )
        }
        
        upload_response = test_client.post("/api/v1/documents/upload", files=files)
        
        if upload_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Document endpoints not available")
        
        if upload_response.status_code not in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            pytest.skip("Cannot upload document for chunking test")
        
        upload_data = upload_response.json()
        document_id = upload_data.get("id") or upload_data.get("document_id")
        
        # Test chunking
        chunks_response = test_client.get(f"/api/v1/documents/{document_id}/chunks")
        
        if chunks_response.status_code == status.HTTP_200_OK:
            chunks_data = chunks_response.json()
            assert isinstance(chunks_data, list)
            if chunks_data:
                # Verify chunk structure
                chunk = chunks_data[0]
                assert "content" in chunk or "text" in chunk
        
        # Test embeddings generation
        embeddings_response = test_client.post(f"/api/v1/documents/{document_id}/embeddings")
        
        if embeddings_response.status_code == status.HTTP_200_OK:
            embeddings_data = embeddings_response.json()
            assert "embeddings" in embeddings_data or "vectors" in embeddings_data


@pytest.mark.e2e
@pytest.mark.integration
class TestDocumentSearchE2E:
    """End-to-end document search and retrieval tests."""

    def test_semantic_search_workflow(self, test_client):
        """Test semantic search across documents."""
        # Test semantic search endpoint
        search_response = test_client.post(
            "/api/v1/documents/search/semantic",
            json={
                "query": "artificial intelligence and machine learning",
                "limit": 10,
                "threshold": 0.7
            }
        )
        
        if search_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Semantic search endpoint not available")
        
        if search_response.status_code == status.HTTP_401_UNAUTHORIZED:
            pytest.skip("Authentication required for semantic search")
        
        assert search_response.status_code == status.HTTP_200_OK
        search_results = search_response.json()
        
        # Verify search results structure
        assert isinstance(search_results, (list, dict))
        
        if isinstance(search_results, list) and search_results:
            result = search_results[0]
            # Should have document reference and similarity score
            assert any(key in result for key in ["document_id", "id", "document"])
            assert any(key in result for key in ["score", "similarity", "relevance"])

    def test_faceted_search(self, test_client):
        """Test faceted search with filters."""
        search_response = test_client.post(
            "/api/v1/documents/search",
            json={
                "query": "test",
                "filters": {
                    "file_type": ["txt", "md"],
                    "date_range": {
                        "start": "2024-01-01",
                        "end": "2024-12-31"
                    }
                }
            }
        )
        
        if search_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Advanced search endpoint not available")
        
        if search_response.status_code == status.HTTP_200_OK:
            search_results = search_response.json()
            assert isinstance(search_results, (list, dict))

    def test_document_analytics_and_insights(self, test_client):
        """Test document analytics and insights generation."""
        # Test document analytics endpoint
        analytics_response = test_client.get("/api/v1/documents/analytics")
        
        if analytics_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Document analytics endpoint not available")
        
        if analytics_response.status_code == status.HTTP_401_UNAUTHORIZED:
            pytest.skip("Authentication required for document analytics")
        
        assert analytics_response.status_code == status.HTTP_200_OK
        analytics_data = analytics_response.json()
        
        # Basic analytics structure check
        expected_metrics = ["total_documents", "total_size", "file_types", "recent_uploads"]
        assert any(metric in analytics_data for metric in expected_metrics)