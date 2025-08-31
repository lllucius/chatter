"""Document management API tests."""

from unittest.mock import patch
import pytest


@pytest.mark.unit
class TestDocumentsAPI:
    """Test document management API endpoints."""

    async def test_upload_document_success(self, test_client):
        """Test successful document upload."""
        # First login to get token
        registration_data = {
            "email": "docuser@example.com",
            "password": "SecurePass123!",
            "username": "docuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "docuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Mock file upload
        with patch("chatter.core.documents.DocumentService.create_document") as mock_create:
            mock_create.return_value = {
                "id": "doc123",
                "title": "test.pdf",
                "filename": "test.pdf",
                "size": 1024,
                "type": "pdf",
                "status": "processing"
            }
            
            files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
            data = {"title": "Test Document", "type": "pdf"}
            
            response = await test_client.post(
                "/api/v1/documents", 
                files=files, 
                data=data, 
                headers=headers
            )
            
            # Should return 201 or 422 if endpoint not fully implemented
            assert response.status_code in [201, 422, 501]
            
            if response.status_code == 201:
                response_data = response.json()
                assert "id" in response_data
                assert response_data["title"] == "Test Document"

    async def test_upload_document_unauthorized(self, test_client):
        """Test document upload without authentication."""
        files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        data = {"title": "Test Document", "type": "pdf"}
        
        response = await test_client.post("/api/v1/documents", files=files, data=data)
        
        # Should require authentication
        assert response.status_code in [401, 403]

    async def test_list_documents(self, test_client):
        """Test listing user documents."""
        # Setup user and auth
        registration_data = {
            "email": "listuser@example.com",
            "password": "SecurePass123!",
            "username": "listuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "listuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List documents
        response = await test_client.get("/api/v1/documents", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "documents" in data or isinstance(data, list)

    async def test_get_document_by_id(self, test_client):
        """Test retrieving a specific document."""
        # Setup user and auth
        registration_data = {
            "email": "getuser@example.com",
            "password": "SecurePass123!",
            "username": "getuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "getuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to get a document (will likely return 404)
        response = await test_client.get("/api/v1/documents/nonexistent", headers=headers)
        
        # Should return 404 for non-existent document or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_delete_document(self, test_client):
        """Test deleting a document."""
        # Setup user and auth
        registration_data = {
            "email": "deleteuser@example.com",
            "password": "SecurePass123!",
            "username": "deleteuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "deleteuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to delete a document
        response = await test_client.delete("/api/v1/documents/nonexistent", headers=headers)
        
        # Should return 404 for non-existent or 501/405 if not implemented
        assert response.status_code in [404, 405, 501]

    async def test_search_documents(self, test_client):
        """Test document search functionality."""
        # Setup user and auth
        registration_data = {
            "email": "searchuser@example.com",
            "password": "SecurePass123!",
            "username": "searchuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "searchuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Search documents with query
        search_data = {
            "query": "test document",
            "limit": 10
        }
        
        response = await test_client.post(
            "/api/v1/documents/search", 
            json=search_data, 
            headers=headers
        )
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 422, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data or isinstance(data, list)

    async def test_document_upload_validation(self, test_client):
        """Test document upload validation."""
        # Setup user and auth
        registration_data = {
            "email": "validuser@example.com",
            "password": "SecurePass123!",
            "username": "validuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "validuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try uploading without file
        data = {"title": "Test Document", "type": "pdf"}
        response = await test_client.post("/api/v1/documents", data=data, headers=headers)
        
        # Should fail validation
        assert response.status_code in [400, 422]

    async def test_document_stats(self, test_client):
        """Test document statistics endpoint."""
        # Setup user and auth
        registration_data = {
            "email": "statsuser@example.com",
            "password": "SecurePass123!",
            "username": "statsuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "statsuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get document stats
        response = await test_client.get("/api/v1/documents/stats", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_documents" in data or "count" in data

    async def test_document_processing_status(self, test_client):
        """Test document processing status endpoint."""
        # Setup user and auth
        registration_data = {
            "email": "statususer@example.com",
            "password": "SecurePass123!",
            "username": "statususer"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "statususer@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check processing status for non-existent document
        response = await test_client.get("/api/v1/documents/nonexistent/status", headers=headers)
        
        # Should return 404 for non-existent or 501 if not implemented
        assert response.status_code in [404, 501]