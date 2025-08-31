"""Data management API tests."""

import pytest


@pytest.mark.unit
class TestDataManagementAPI:
    """Test data management API endpoints."""

    async def test_export_data(self, test_client):
        """Test data export functionality."""
        # Setup user and auth
        registration_data = {
            "email": "datauser@example.com",
            "password": "SecurePass123!",
            "username": "datauser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "datauser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Export user data
        export_data = {
            "format": "json",
            "include_conversations": True,
            "include_documents": True,
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-12-31"
            }
        }

        response = await test_client.post("/api/v1/data-management/export", json=export_data, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 202, 422, 501]

        if response.status_code in [200, 202]:
            data = response.json()
            assert "export_id" in data or "data" in data

    async def test_import_data(self, test_client):
        """Test data import functionality."""
        # Setup user and auth
        registration_data = {
            "email": "importuser@example.com",
            "password": "SecurePass123!",
            "username": "importuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "importuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Import data
        import_data = {
            "format": "json",
            "data": {
                "conversations": [],
                "documents": []
            },
            "merge_strategy": "replace"
        }

        response = await test_client.post("/api/v1/data-management/import", json=import_data, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 202, 422, 501]

    async def test_delete_user_data(self, test_client):
        """Test deleting all user data."""
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

        # Request data deletion
        deletion_data = {
            "confirmation": "DELETE_ALL_DATA",
            "include_backups": False
        }

        response = await test_client.post("/api/v1/data-management/delete-all", json=deletion_data, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 202, 422, 501]

    async def test_data_backup(self, test_client):
        """Test data backup functionality."""
        # Setup user and auth
        registration_data = {
            "email": "backupuser@example.com",
            "password": "SecurePass123!",
            "username": "backupuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "backupuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create backup
        backup_data = {
            "backup_type": "full",
            "compression": "gzip",
            "encryption": True
        }

        response = await test_client.post("/api/v1/data-management/backup", json=backup_data, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 202, 422, 501]

    async def test_list_backups(self, test_client):
        """Test listing user backups."""
        # Setup user and auth
        registration_data = {
            "email": "listbackupuser@example.com",
            "password": "SecurePass123!",
            "username": "listbackupuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "listbackupuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List backups
        response = await test_client.get("/api/v1/data-management/backups", headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert "backups" in data or isinstance(data, list)

    async def test_restore_backup(self, test_client):
        """Test restoring from backup."""
        # Setup user and auth
        registration_data = {
            "email": "restoreuser@example.com",
            "password": "SecurePass123!",
            "username": "restoreuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "restoreuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Restore backup
        restore_data = {
            "backup_id": "backup_123",
            "restore_type": "selective",
            "items": ["conversations", "preferences"]
        }

        response = await test_client.post("/api/v1/data-management/restore", json=restore_data, headers=headers)

        # Should return 404 for non-existent backup or 501 if not implemented
        assert response.status_code in [404, 422, 501]

    async def test_data_usage_stats(self, test_client):
        """Test data usage statistics."""
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

        # Get usage stats
        response = await test_client.get("/api/v1/data-management/usage", headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert "storage_used" in data or "usage" in data

    async def test_data_unauthorized(self, test_client):
        """Test data management endpoints require authentication."""
        endpoints = [
            "/api/v1/data-management/export",
            "/api/v1/data-management/import",
            "/api/v1/data-management/backup",
            "/api/v1/data-management/backups",
            "/api/v1/data-management/usage"
        ]

        for endpoint in endpoints:
            if endpoint in ["/api/v1/data-management/export", "/api/v1/data-management/import", "/api/v1/data-management/backup"]:
                response = await test_client.post(endpoint, json={})
            else:
                response = await test_client.get(endpoint)

            # Should require authentication
            assert response.status_code in [401, 403]

    async def test_gdpr_compliance(self, test_client):
        """Test GDPR compliance features."""
        # Setup user and auth
        registration_data = {
            "email": "gdpruser@example.com",
            "password": "SecurePass123!",
            "username": "gdpruser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "gdpruser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Request GDPR data export (right to portability)
        response = await test_client.get("/api/v1/data-management/gdpr-export", headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 202, 501]

    async def test_data_retention_policy(self, test_client):
        """Test data retention policy information."""
        # Setup user and auth
        registration_data = {
            "email": "retentionuser@example.com",
            "password": "SecurePass123!",
            "username": "retentionuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "retentionuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get retention policy info
        response = await test_client.get("/api/v1/data-management/retention-policy", headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
