"""Unit tests for data management API."""

import pytest
from httpx import AsyncClient


class TestDataManagementUnit:
    """Unit tests for data management API endpoints."""

    @pytest.mark.unit
    async def test_export_data_endpoint_exists(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that export data endpoint exists and validates authentication."""
        # Test with missing auth header - should get 401
        response = await client.post(
            "/api/v1/data-management/export", json={}
        )
        assert response.status_code == 401

        # Test with auth header but invalid data - should get 422 (validation error)
        response = await client.post(
            "/api/v1/data-management/export",
            headers=auth_headers,
            json={},
        )
        assert response.status_code == 422

    @pytest.mark.unit
    async def test_create_backup_endpoint_exists(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that create backup endpoint exists."""
        # Test without auth - should get 401
        response = await client.post(
            "/api/v1/data-management/backup", json={}
        )
        assert response.status_code == 401

        # Test with auth but invalid data - should get 422
        response = await client.post(
            "/api/v1/data-management/backup",
            headers=auth_headers,
            json={},
        )
        assert response.status_code == 422

    @pytest.mark.unit
    async def test_list_backups_endpoint_exists(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that list backups endpoint exists."""
        # Test without auth
        response = await client.get("/api/v1/data-management/backups")
        assert response.status_code == 401

        # Test with auth - should work (might return empty list)
        response = await client.get(
            "/api/v1/data-management/backups", headers=auth_headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    @pytest.mark.unit
    async def test_restore_data_endpoint_exists(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that restore data endpoint exists."""
        # Test without auth
        response = await client.post(
            "/api/v1/data-management/restore", json={}
        )
        assert response.status_code == 401

        # Test with auth but invalid data
        response = await client.post(
            "/api/v1/data-management/restore",
            headers=auth_headers,
            json={},
        )
        assert response.status_code == 422

    @pytest.mark.unit
    async def test_get_storage_stats_endpoint_exists(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that get storage stats endpoint exists."""
        # Test without auth
        response = await client.get("/api/v1/data-management/stats")
        assert response.status_code == 401

        # Test with auth - should work
        response = await client.get(
            "/api/v1/data-management/stats", headers=auth_headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    @pytest.mark.unit
    async def test_bulk_delete_documents_endpoint_exists(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that bulk delete documents endpoint exists."""
        # Test without auth
        response = await client.post(
            "/api/v1/data-management/bulk/delete-documents", json={}
        )
        assert response.status_code == 401

        # Test with auth but invalid data
        response = await client.post(
            "/api/v1/data-management/bulk/delete-documents",
            headers=auth_headers,
            json={},
        )
        assert response.status_code == 422

    @pytest.mark.unit
    async def test_bulk_delete_conversations_endpoint_exists(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that bulk delete conversations endpoint exists."""
        # Test without auth
        response = await client.post(
            "/api/v1/data-management/bulk/delete-conversations", json={}
        )
        assert response.status_code == 401

        # Test with auth but invalid data
        response = await client.post(
            "/api/v1/data-management/bulk/delete-conversations",
            headers=auth_headers,
            json={},
        )
        assert response.status_code == 422

    @pytest.mark.unit
    async def test_bulk_delete_prompts_endpoint_exists(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that bulk delete prompts endpoint exists."""
        # Test without auth
        response = await client.post(
            "/api/v1/data-management/bulk/delete-prompts", json={}
        )
        assert response.status_code == 401

        # Test with auth but invalid data
        response = await client.post(
            "/api/v1/data-management/bulk/delete-prompts",
            headers=auth_headers,
            json={},
        )
        assert response.status_code == 422

    @pytest.mark.unit
    async def test_bulk_delete_response_structure(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that bulk delete endpoints return the expected response structure."""
        # Test with empty array to get a valid response without side effects
        empty_request = []

        endpoints = [
            "/api/v1/data-management/bulk/delete-documents",
            "/api/v1/data-management/bulk/delete-conversations",
            "/api/v1/data-management/bulk/delete-prompts",
        ]

        for endpoint in endpoints:
            response = await client.post(
                endpoint, headers=auth_headers, json=empty_request
            )

            # Should get 200 or 422, but if 200 check response structure
            if response.status_code == 200:
                data = response.json()
                # Verify the response has the correct field names for frontend
                assert "total_requested" in data
                assert "successful_deletions" in data
                assert "failed_deletions" in data
                assert "errors" in data

                # Verify field types
                assert isinstance(data["total_requested"], int)
                assert isinstance(data["successful_deletions"], int)
                assert isinstance(data["failed_deletions"], int)
                assert isinstance(data["errors"], list)
