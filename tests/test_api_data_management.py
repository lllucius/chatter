"""Tests for data management API endpoints."""

from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.api.auth import get_current_user
from chatter.main import app
from chatter.models.user import User
from chatter.schemas.data_management import (
    BackupType,
)
from chatter.services.data_management import data_manager


@pytest.mark.unit
class TestDataManagementEndpoints:
    """Test data management API endpoints."""

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

    def test_export_data_success(self):
        """Test successful data export."""
        # Arrange
        export_request = {
            "format": "json",
            "data_types": ["conversations", "documents"],
            "date_from": "2024-01-01T00:00:00Z",
            "date_to": "2024-12-31T23:59:59Z",
            "include_metadata": True
        }

        mock_export_id = "export-123"
        mock_export_info = {
            "status": "pending",
            "created_at": datetime.now(UTC),
            "record_count": 100
        }

        with patch.object(data_manager, 'export_data') as mock_export:
            mock_export.return_value = mock_export_id

            with patch.object(data_manager, 'get_export_status') as mock_status:
                mock_status.return_value = mock_export_info

                # Act
                response = self.client.post("/data/export", json=export_request)

                # Assert
                assert response.status_code == status.HTTP_202_ACCEPTED
                data = response.json()
                assert data["export_id"] == mock_export_id
                assert data["status"] == "pending"
                assert data["record_count"] == 100
                mock_export.assert_called_once()
                mock_status.assert_called_once_with(mock_export_id)

    def test_export_data_invalid_format(self):
        """Test data export with invalid format."""
        # Arrange
        export_request = {
            "format": "invalid_format",
            "data_types": ["conversations"]
        }

        # Act
        response = self.client.post("/data/export", json=export_request)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_backup_success(self):
        """Test successful backup creation."""
        # Arrange
        backup_request = {
            "name": "test-backup",
            "description": "Test backup for unit tests",
            "backup_type": "full",
            "encrypt": True,
            "compress": True,
            "include_user_data": True,
            "include_system_data": False
        }

        mock_backup_id = "backup-456"
        mock_backup_info = {
            "name": "test-backup",
            "status": "pending",
            "created_at": datetime.now(UTC),
            "record_count": 250,
            "encrypted": True,
            "compressed": True
        }

        with patch.object(data_manager, 'create_backup') as mock_backup:
            mock_backup.return_value = mock_backup_id

            with patch.object(data_manager, 'get_backup_info') as mock_info:
                mock_info.return_value = mock_backup_info

                # Act
                response = self.client.post("/data/backup", json=backup_request)

                # Assert
                assert response.status_code == status.HTTP_202_ACCEPTED
                data = response.json()
                assert data["id"] == mock_backup_id
                assert data["name"] == "test-backup"
                assert data["backup_type"] == "full"
                assert data["status"] == "pending"
                assert data["encrypted"] is True
                assert data["compressed"] is True
                mock_backup.assert_called_once()
                mock_info.assert_called_once_with(mock_backup_id)

    def test_create_backup_minimal_request(self):
        """Test backup creation with minimal required fields."""
        # Arrange
        backup_request = {
            "backup_type": "user_data"
        }

        mock_backup_id = "backup-789"
        mock_backup_info = {
            "status": "pending",
            "created_at": datetime.now(UTC)
        }

        with patch.object(data_manager, 'create_backup') as mock_backup:
            mock_backup.return_value = mock_backup_id

            with patch.object(data_manager, 'get_backup_info') as mock_info:
                mock_info.return_value = mock_backup_info

                # Act
                response = self.client.post("/data/backup", json=backup_request)

                # Assert
                assert response.status_code == status.HTTP_202_ACCEPTED
                data = response.json()
                assert data["id"] == mock_backup_id
                assert data["backup_type"] == "user_data"

    def test_list_backups_success(self):
        """Test successful backup listing."""
        # Arrange
        mock_backups = [
            {
                "id": "backup-1",
                "name": "Backup 1",
                "backup_type": "full",
                "status": "completed",
                "created_at": datetime.now(UTC),
                "file_size": 1024000,
                "record_count": 100
            },
            {
                "id": "backup-2",
                "name": "Backup 2",
                "backup_type": "user_data",
                "status": "pending",
                "created_at": datetime.now(UTC),
                "record_count": 50
            }
        ]

        mock_total = 2

        with patch.object(data_manager, 'list_backups') as mock_list:
            mock_list.return_value = (mock_backups, mock_total)

            # Act
            response = self.client.get("/data/backups?page=1&per_page=10")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["backups"]) == 2
            assert data["total"] == 2
            assert data["page"] == 1
            assert data["per_page"] == 10
            assert data["backups"][0]["id"] == "backup-1"
            assert data["backups"][1]["status"] == "pending"

    def test_list_backups_with_filters(self):
        """Test backup listing with filters."""
        # Arrange
        mock_backups = [
            {
                "id": "backup-full",
                "name": "Full Backup",
                "backup_type": "full",
                "status": "completed",
                "created_at": datetime.now(UTC)
            }
        ]

        with patch.object(data_manager, 'list_backups') as mock_list:
            mock_list.return_value = (mock_backups, 1)

            # Act
            response = self.client.get(
                "/data/backups?backup_type=full&status=completed&page=1&per_page=5"
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["backups"]) == 1
            assert data["backups"][0]["backup_type"] == "full"

            # Verify filter parameters were passed
            call_args = mock_list.call_args[0][0]  # First argument (BackupListRequest)
            assert call_args.backup_type == BackupType.FULL
            assert call_args.status == "completed"

    def test_restore_backup_success(self):
        """Test successful backup restoration."""
        # Arrange
        restore_request = {
            "backup_id": "backup-restore-123",
            "restore_type": "full",
            "verify_integrity": True,
            "overwrite_existing": False
        }

        mock_restore_id = "restore-456"
        mock_restore_info = {
            "status": "pending",
            "created_at": datetime.now(UTC),
            "estimated_completion": datetime.now(UTC)
        }

        with patch.object(data_manager, 'restore_backup') as mock_restore:
            mock_restore.return_value = mock_restore_id

            with patch.object(data_manager, 'get_restore_status') as mock_status:
                mock_status.return_value = mock_restore_info

                # Act
                response = self.client.post("/data/restore", json=restore_request)

                # Assert
                assert response.status_code == status.HTTP_202_ACCEPTED
                data = response.json()
                assert data["restore_id"] == mock_restore_id
                assert data["status"] == "pending"
                mock_restore.assert_called_once()
                mock_status.assert_called_once_with(mock_restore_id)

    def test_get_storage_stats_success(self):
        """Test successful storage statistics retrieval."""
        # Arrange
        mock_stats = {
            "total_size": 1024000000,  # 1GB
            "used_size": 512000000,    # 512MB
            "available_size": 512000000,  # 512MB
            "documents_count": 1500,
            "conversations_count": 300,
            "backups_count": 5,
            "exports_count": 10,
            "last_backup": datetime.now(UTC),
            "oldest_data": datetime(2024, 1, 1, tzinfo=UTC)
        }

        with patch.object(data_manager, 'get_storage_stats') as mock_stats_fn:
            mock_stats_fn.return_value = mock_stats

            # Act
            response = self.client.get("/data/stats")

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_size"] == 1024000000
            assert data["used_size"] == 512000000
            assert data["documents_count"] == 1500
            assert data["conversations_count"] == 300
            assert data["backups_count"] == 5

    def test_bulk_delete_documents_success(self):
        """Test successful bulk document deletion."""
        # Arrange
        delete_request = {
            "document_ids": ["doc-1", "doc-2", "doc-3"],
            "confirm_deletion": True
        }

        mock_result = {
            "deleted_count": 3,
            "failed_count": 0,
            "deleted_ids": ["doc-1", "doc-2", "doc-3"],
            "failed_ids": [],
            "total_size_freed": 1048576  # 1MB
        }

        with patch.object(data_manager, 'bulk_delete_documents') as mock_delete:
            mock_delete.return_value = mock_result

            # Act
            response = self.client.post("/data/bulk/delete-documents", json=delete_request)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted_count"] == 3
            assert data["failed_count"] == 0
            assert len(data["deleted_ids"]) == 3
            assert data["total_size_freed"] == 1048576

    def test_bulk_delete_conversations_success(self):
        """Test successful bulk conversation deletion."""
        # Arrange
        delete_request = {
            "conversation_ids": ["conv-1", "conv-2"],
            "confirm_deletion": True,
            "delete_associated_data": True
        }

        mock_result = {
            "deleted_count": 2,
            "failed_count": 0,
            "deleted_ids": ["conv-1", "conv-2"],
            "failed_ids": []
        }

        with patch.object(data_manager, 'bulk_delete_conversations') as mock_delete:
            mock_delete.return_value = mock_result

            # Act
            response = self.client.post("/data/bulk/delete-conversations", json=delete_request)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted_count"] == 2
            assert data["failed_count"] == 0

    def test_bulk_delete_prompts_success(self):
        """Test successful bulk prompt deletion."""
        # Arrange
        delete_request = {
            "prompt_ids": ["prompt-1", "prompt-2", "prompt-3"],
            "confirm_deletion": True
        }

        mock_result = {
            "deleted_count": 2,
            "failed_count": 1,
            "deleted_ids": ["prompt-1", "prompt-2"],
            "failed_ids": ["prompt-3"]  # Maybe in use
        }

        with patch.object(data_manager, 'bulk_delete_prompts') as mock_delete:
            mock_delete.return_value = mock_result

            # Act
            response = self.client.post("/data/bulk/delete-prompts", json=delete_request)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["deleted_count"] == 2
            assert data["failed_count"] == 1
            assert len(data["deleted_ids"]) == 2
            assert len(data["failed_ids"]) == 1


@pytest.mark.integration
class TestDataManagementIntegration:
    """Integration tests for data management workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="integration-user-id",
            email="integration@example.com",
            username="integrationuser",
            is_active=True
        )

        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_export_backup_restore_workflow(self):
        """Test complete export-backup-restore workflow."""
        # This would test the integration between export, backup, and restore
        # For now, we'll simulate the workflow with mocks

        export_id = "export-integration-123"
        backup_id = "backup-integration-456"
        restore_id = "restore-integration-789"

        # Step 1: Export data
        with patch.object(data_manager, 'export_data') as mock_export:
            mock_export.return_value = export_id

            with patch.object(data_manager, 'get_export_status') as mock_export_status:
                mock_export_status.return_value = {"status": "completed"}

                export_response = self.client.post("/data/export", json={
                    "format": "json",
                    "data_types": ["conversations"]
                })
                assert export_response.status_code == status.HTTP_202_ACCEPTED

        # Step 2: Create backup
        with patch.object(data_manager, 'create_backup') as mock_backup:
            mock_backup.return_value = backup_id

            with patch.object(data_manager, 'get_backup_info') as mock_backup_info:
                mock_backup_info.return_value = {"status": "completed"}

                backup_response = self.client.post("/data/backup", json={
                    "backup_type": "full"
                })
                assert backup_response.status_code == status.HTTP_202_ACCEPTED

        # Step 3: Restore from backup
        with patch.object(data_manager, 'restore_backup') as mock_restore:
            mock_restore.return_value = restore_id

            with patch.object(data_manager, 'get_restore_status') as mock_restore_status:
                mock_restore_status.return_value = {"status": "pending"}

                restore_response = self.client.post("/data/restore", json={
                    "backup_id": backup_id,
                    "restore_type": "full"
                })
                assert restore_response.status_code == status.HTTP_202_ACCEPTED

    def test_bulk_operations_integration(self):
        """Test integration of bulk operations with stats."""
        # Test bulk delete followed by stats check

        # First check initial stats
        with patch.object(data_manager, 'get_storage_stats') as mock_stats:
            mock_stats.return_value = {
                "documents_count": 100,
                "conversations_count": 50,
                "used_size": 1000000
            }

            stats_response = self.client.get("/data/stats")
            assert stats_response.status_code == status.HTTP_200_OK
            stats_response.json()["documents_count"]

        # Perform bulk delete
        with patch.object(data_manager, 'bulk_delete_documents') as mock_delete:
            mock_delete.return_value = {
                "deleted_count": 10,
                "failed_count": 0,
                "total_size_freed": 100000
            }

            delete_response = self.client.post("/data/bulk/delete-documents", json={
                "document_ids": ["doc-1", "doc-2", "doc-3"],
                "confirm_deletion": True
            })
            assert delete_response.status_code == status.HTTP_200_OK

        # Check updated stats
        with patch.object(data_manager, 'get_storage_stats') as mock_stats_after:
            mock_stats_after.return_value = {
                "documents_count": 90,  # 10 less
                "conversations_count": 50,
                "used_size": 900000  # 100000 less
            }

            updated_stats = self.client.get("/data/stats")
            assert updated_stats.status_code == status.HTTP_200_OK
            # In real integration, we'd verify the actual decrease
