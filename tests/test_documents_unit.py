"""Unit tests for documents API."""

import pytest
from httpx import AsyncClient
from unittest.mock import Mock, patch, AsyncMock


class TestDocumentsUnit:
    """Unit tests for documents API endpoints."""
    
    @pytest.mark.unit
    async def test_upload_document_endpoint_exists(self, client: AsyncClient, auth_headers: dict):
        """Test that upload document endpoint exists and validates authentication."""
        # Test with missing auth header - should get 401
        response = await client.post("/api/v1/documents/upload")
        assert response.status_code == 401
        
        # Test with auth header but no file - should get 422 (validation error)
        response = await client.post("/api/v1/documents/upload", headers=auth_headers)
        assert response.status_code == 422
    
    @pytest.mark.unit
    async def test_list_documents_endpoint_exists(self, client: AsyncClient, auth_headers: dict):
        """Test that list documents endpoint exists."""
        # Test without auth - should get 401
        response = await client.get("/api/v1/documents")
        assert response.status_code == 401
        
        # Test with auth - should work (might return empty list)
        response = await client.get("/api/v1/documents", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    @pytest.mark.unit
    async def test_search_documents_endpoint_exists(self, client: AsyncClient, auth_headers: dict):
        """Test that search documents endpoint exists."""
        # Test without auth
        response = await client.post("/api/v1/documents/search", json={})
        assert response.status_code == 401
        
        # Test with auth but invalid data
        response = await client.post("/api/v1/documents/search", 
                                   headers=auth_headers, json={})
        assert response.status_code == 422  # Should require query field
    
    @pytest.mark.unit
    async def test_get_document_endpoint_exists(self, client: AsyncClient, auth_headers: dict):
        """Test that get document endpoint exists."""
        # Test without auth
        response = await client.get("/api/v1/documents/nonexistent-id")
        assert response.status_code == 401
        
        # Test with auth - should get 404 for nonexistent document
        response = await client.get("/api/v1/documents/nonexistent-id", 
                                  headers=auth_headers)
        assert response.status_code == 404
    
    @pytest.mark.unit
    async def test_delete_document_endpoint_exists(self, client: AsyncClient, auth_headers: dict):
        """Test that delete document endpoint exists."""
        # Test without auth
        response = await client.delete("/api/v1/documents/nonexistent-id")
        assert response.status_code == 401
        
        # Test with auth - should get 404 for nonexistent document
        response = await client.delete("/api/v1/documents/nonexistent-id", 
                                     headers=auth_headers)
        assert response.status_code == 404
    
    @pytest.mark.unit
    async def test_update_document_endpoint_exists(self, client: AsyncClient, auth_headers: dict):
        """Test that update document endpoint exists."""
        # Test without auth
        response = await client.put("/api/v1/documents/nonexistent-id", json={})
        assert response.status_code == 401
        
        # Test with auth - should get 404 for nonexistent document
        response = await client.put("/api/v1/documents/nonexistent-id", 
                                  headers=auth_headers, json={})
        assert response.status_code == 404
    
    @pytest.mark.unit
    async def test_get_document_chunks_endpoint_exists(self, client: AsyncClient, auth_headers: dict):
        """Test that get document chunks endpoint exists."""
        # Test without auth
        response = await client.get("/api/v1/documents/nonexistent-id/chunks")
        assert response.status_code == 401
        
        # Test with auth - should get 404 for nonexistent document
        response = await client.get("/api/v1/documents/nonexistent-id/chunks", 
                                  headers=auth_headers)
        assert response.status_code == 404
    
    @pytest.mark.unit
    async def test_process_document_endpoint_exists(self, client: AsyncClient, auth_headers: dict):
        """Test that process document endpoint exists."""
        # Test without auth
        response = await client.post("/api/v1/documents/nonexistent-id/process", json={})
        assert response.status_code == 401
        
        # Test with auth - should get 404 for nonexistent document
        response = await client.post("/api/v1/documents/nonexistent-id/process", 
                                   headers=auth_headers, json={})
        assert response.status_code == 404
    
    @pytest.mark.unit
    async def test_get_document_stats_endpoint_exists(self, client: AsyncClient, auth_headers: dict):
        """Test that get document stats endpoint exists."""
        # Test without auth
        response = await client.get("/api/v1/documents/stats/overview")
        assert response.status_code == 401
        
        # Test with auth - should work
        response = await client.get("/api/v1/documents/stats/overview", 
                                  headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    @pytest.mark.unit
    async def test_download_document_endpoint_exists(self, client: AsyncClient, auth_headers: dict):
        """Test that download document endpoint exists."""
        # Test without auth
        response = await client.get("/api/v1/documents/nonexistent-id/download")
        assert response.status_code == 401
        
        # Test with auth - should get 404 for nonexistent document
        response = await client.get("/api/v1/documents/nonexistent-id/download", 
                                  headers=auth_headers)
        assert response.status_code == 404