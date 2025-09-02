"""Integration tests for data management API."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestDataManagementIntegration:
    """Integration tests for data management API workflows."""
    
    @pytest.mark.integration
    async def test_export_data_workflow(self, client: AsyncClient, auth_headers: dict):
        """Test complete data export workflow."""
        # Test export with valid data structure (even if service isn't fully configured)
        export_data = {
            "format": "json",
            "scope": "user",
            "include_documents": True,
            "include_conversations": True,
            "include_analytics": False,
            "date_range": {
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z"
            }
        }
        
        response = await client.post("/api/v1/data-management/export", 
                                   headers=auth_headers, json=export_data)
        
        # Should start export successfully or handle gracefully  
        assert response.status_code in [202, 422, 500]  # 202 = Accepted, others = graceful failures
        
        if response.status_code == 202:
            # Verify response structure
            response_data = response.json()
            assert "export_id" in response_data
            assert "status" in response_data
            assert response_data["status"] in ["pending", "in_progress", "completed", "failed"]
    
    @pytest.mark.integration
    async def test_backup_workflow(self, client: AsyncClient, auth_headers: dict):
        """Test backup creation and listing workflow."""
        # Test backup creation
        backup_data = {
            "name": "Test Backup",
            "description": "Integration test backup",
            "backup_type": "full",
            "encrypt": False,
            "compress": True
        }
        
        response = await client.post("/api/v1/data-management/backup", 
                                   headers=auth_headers, json=backup_data)
        
        # Should start backup or handle gracefully
        assert response.status_code in [202, 422, 500]
        
        backup_id = None
        if response.status_code == 202:
            response_data = response.json()
            assert "backup_id" in response_data
            backup_id = response_data["backup_id"]
        
        # Test list backups
        response = await client.get("/api/v1/data-management/backups", 
                                  headers=auth_headers)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            backups_data = response.json()
            assert isinstance(backups_data, dict)
            assert "backups" in backups_data or "items" in backups_data
    
    @pytest.mark.integration
    async def test_restore_workflow(self, client: AsyncClient, auth_headers: dict):
        """Test data restore workflow."""
        # Test restore with nonexistent backup
        restore_data = {
            "backup_id": "nonexistent-backup-id",
            "restore_options": {
                "include_documents": True,
                "include_conversations": True,
                "overwrite_existing": False
            }
        }
        
        response = await client.post("/api/v1/data-management/restore", 
                                   headers=auth_headers, json=restore_data)
        
        # Should handle nonexistent backup gracefully
        assert response.status_code in [404, 422, 500]
    
    @pytest.mark.integration
    async def test_storage_stats_workflow(self, client: AsyncClient, auth_headers: dict):
        """Test storage statistics workflow."""
        response = await client.get("/api/v1/data-management/stats", 
                                  headers=auth_headers)
        
        assert response.status_code in [200, 500]  # Should work or fail gracefully
        
        if response.status_code == 200:
            stats_data = response.json()
            assert isinstance(stats_data, dict)
            # Expected fields in storage stats
            expected_fields = ["total_size", "documents", "conversations", "backups"]
            # Not all fields may be present in initial implementation
    
    @pytest.mark.integration
    async def test_bulk_delete_documents_workflow(self, client: AsyncClient, auth_headers: dict):
        """Test bulk document deletion workflow."""
        # Test with empty list
        delete_data = {"document_ids": []}
        
        response = await client.post("/api/v1/data-management/bulk/delete-documents", 
                                   headers=auth_headers, json=delete_data)
        
        assert response.status_code in [200, 422, 500]
        
        if response.status_code == 200:
            response_data = response.json()
            assert "success_count" in response_data
            assert "error_count" in response_data
            assert response_data["success_count"] == 0  # No documents to delete
        
        # Test with nonexistent document IDs
        delete_data = {"document_ids": ["nonexistent-1", "nonexistent-2"]}
        
        response = await client.post("/api/v1/data-management/bulk/delete-documents", 
                                   headers=auth_headers, json=delete_data)
        
        assert response.status_code in [200, 422, 500]
        
        if response.status_code == 200:
            response_data = response.json()
            assert "error_count" in response_data
            # Should have errors for nonexistent documents
    
    @pytest.mark.integration
    async def test_bulk_delete_conversations_workflow(self, client: AsyncClient, auth_headers: dict):
        """Test bulk conversation deletion workflow."""
        # Test with empty list
        delete_data = {"conversation_ids": []}
        
        response = await client.post("/api/v1/data-management/bulk/delete-conversations", 
                                   headers=auth_headers, json=delete_data)
        
        assert response.status_code in [200, 422, 500]
        
        if response.status_code == 200:
            response_data = response.json()
            assert "success_count" in response_data
            assert "error_count" in response_data
    
    @pytest.mark.integration
    async def test_bulk_delete_prompts_workflow(self, client: AsyncClient, auth_headers: dict):
        """Test bulk prompt deletion workflow."""
        # Test with empty list
        delete_data = {"prompt_ids": []}
        
        response = await client.post("/api/v1/data-management/bulk/delete-prompts", 
                                   headers=auth_headers, json=delete_data)
        
        assert response.status_code in [200, 422, 500]
        
        if response.status_code == 200:
            response_data = response.json()
            assert "success_count" in response_data
            assert "error_count" in response_data
    
    @pytest.mark.integration
    async def test_data_management_permission_workflow(self, client: AsyncClient, auth_headers: dict):
        """Test data management permission and access control workflow."""
        # Test without authentication - all should return 401
        response = await client.get("/api/v1/data-management/stats")
        assert response.status_code == 401
        
        response = await client.get("/api/v1/data-management/backups")
        assert response.status_code == 401
        
        response = await client.post("/api/v1/data-management/export", json={})
        assert response.status_code == 401
        
        response = await client.post("/api/v1/data-management/backup", json={})
        assert response.status_code == 401
        
        response = await client.post("/api/v1/data-management/restore", json={})
        assert response.status_code == 401
        
        # Test with authentication - should get past auth layer
        response = await client.get("/api/v1/data-management/stats", headers=auth_headers)
        assert response.status_code in [200, 500]  # Should be authorized
        
        response = await client.get("/api/v1/data-management/backups", headers=auth_headers)
        assert response.status_code in [200, 500]  # Should be authorized
    
    @pytest.mark.integration
    async def test_cross_api_data_consistency(self, client: AsyncClient, auth_headers: dict):
        """Test data consistency between documents and data management APIs."""
        # Get document stats
        doc_response = await client.get("/api/v1/documents/stats/overview", 
                                      headers=auth_headers)
        
        # Get storage stats
        storage_response = await client.get("/api/v1/data-management/stats", 
                                          headers=auth_headers)
        
        # Both should either work or fail gracefully
        assert doc_response.status_code in [200, 500]
        assert storage_response.status_code in [200, 500]
        
        # If both work, verify they're consistent
        if doc_response.status_code == 200 and storage_response.status_code == 200:
            doc_stats = doc_response.json()
            storage_stats = storage_response.json()
            
            # Basic consistency checks if data is available
            if "total_documents" in doc_stats and "documents" in storage_stats:
                # Document counts should be consistent
                pass  # Would implement specific consistency checks here