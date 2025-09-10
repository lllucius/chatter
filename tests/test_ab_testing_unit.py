"""Unit tests for AB testing API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from chatter.schemas.ab_testing import ABTestResponse, TestStatus


class TestABTestingUnit:
    """Unit tests for AB testing API endpoints."""

    @pytest.mark.unit
    async def test_create_ab_test_requires_auth(
        self, client: AsyncClient
    ):
        """Test that creating AB test requires authentication."""
        test_data = {
            "name": "Test AB Test",
            "description": "Test description",
            "variants": [
                {"name": "control", "allocation": 50},
                {"name": "variant_a", "allocation": 50},
            ],
        }

        response = await client.post(
            "/api/v1/ab-tests/", json=test_data
        )
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_list_ab_tests_requires_auth(
        self, client: AsyncClient
    ):
        """Test that listing AB tests requires authentication."""
        response = await client.get("/api/v1/ab-tests/")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_ab_test_requires_auth(self, client: AsyncClient):
        """Test that getting specific AB test requires authentication."""
        response = await client.get("/api/v1/ab-tests/test-id")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_update_ab_test_requires_auth(
        self, client: AsyncClient
    ):
        """Test that updating AB test requires authentication."""
        response = await client.put("/api/v1/ab-tests/test-id", json={})
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_delete_ab_test_requires_auth(
        self, client: AsyncClient
    ):
        """Test that deleting AB test requires authentication."""
        response = await client.delete("/api/v1/ab-tests/test-id")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_start_ab_test_requires_auth(
        self, client: AsyncClient
    ):
        """Test that starting AB test requires authentication."""
        response = await client.post("/api/v1/ab-tests/test-id/start")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_pause_ab_test_requires_auth(
        self, client: AsyncClient
    ):
        """Test that pausing AB test requires authentication."""
        response = await client.post("/api/v1/ab-tests/test-id/pause")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_complete_ab_test_requires_auth(
        self, client: AsyncClient
    ):
        """Test that completing AB test requires authentication."""
        response = await client.post(
            "/api/v1/ab-tests/test-id/complete"
        )
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_results_requires_auth(self, client: AsyncClient):
        """Test that getting results requires authentication."""
        response = await client.get("/api/v1/ab-tests/test-id/results")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_metrics_requires_auth(self, client: AsyncClient):
        """Test that getting metrics requires authentication."""
        response = await client.get("/api/v1/ab-tests/test-id/metrics")
        assert response.status_code == 401

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_create_ab_test_success(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test successful AB test creation."""
        # Mock the manager
        mock_manager = AsyncMock()

        from datetime import UTC, datetime

        from chatter.schemas.ab_testing import TestVariant
        from chatter.services.ab_testing import (
            MetricType,
            TestType,
            VariantAllocation,
        )

        # Create proper test variants
        test_variants = [
            TestVariant(
                name="control",
                description="Control variant",
                configuration={},
                weight=1.0,
            ),
            TestVariant(
                name="variant_a",
                description="Variant A",
                configuration={},
                weight=1.0,
            ),
        ]

        mock_manager.create_test.return_value = ABTestResponse(
            id="test-123",
            name="Test AB Test",
            description="Test description",
            test_type=TestType.PROMPT,
            status=TestStatus.DRAFT,
            allocation_strategy=VariantAllocation.EQUAL,
            variants=test_variants,
            metrics=[MetricType.CUSTOM],
            duration_days=30,
            min_sample_size=100,
            confidence_level=0.95,
            traffic_percentage=100.0,
            tags=[],
            metadata={},
            created_by="testuser",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_get_manager.return_value = mock_manager

        test_data = {
            "name": "Test AB Test",
            "description": "Test description",
            "variants": [
                {"name": "control", "allocation": 50},
                {"name": "variant_a", "allocation": 50},
            ],
        }

        response = await client.post(
            "/api/v1/ab-tests/", json=test_data, headers=auth_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["id"] == "test-123"
        assert data["name"] == "Test AB Test"
        assert data["status"] == "draft"

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_create_ab_test_invalid_data(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test AB test creation with invalid data."""
        # Missing required fields
        test_data = {
            "name": "Test AB Test"
            # Missing description and variants
        }

        response = await client.post(
            "/api/v1/ab-tests/", json=test_data, headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_create_ab_test_invalid_allocation(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test AB test creation with invalid allocation percentages."""
        test_data = {
            "name": "Test AB Test",
            "description": "Test description",
            "variants": [
                {"name": "control", "allocation": 60},
                {"name": "variant_a", "allocation": 50},  # Total = 110%
            ],
        }

        # Mock manager to raise validation error
        mock_manager = AsyncMock()
        mock_manager.create_test.side_effect = ValueError(
            "Invalid allocation percentages"
        )
        mock_get_manager.return_value = mock_manager

        response = await client.post(
            "/api/v1/ab-tests/", json=test_data, headers=auth_headers
        )
        assert response.status_code == 400

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_list_ab_tests_success(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test successful AB test listing."""
        mock_manager = AsyncMock()
        mock_manager.list_tests.return_value = {
            "tests": [
                {
                    "id": "test-1",
                    "name": "Test 1",
                    "status": "running",
                    "created_at": "2024-01-01T12:00:00Z",
                },
                {
                    "id": "test-2",
                    "name": "Test 2",
                    "status": "draft",
                    "created_at": "2024-01-01T13:00:00Z",
                },
            ],
            "total": 2,
            "page": 1,
            "per_page": 10,
        }
        mock_get_manager.return_value = mock_manager

        response = await client.get(
            "/api/v1/ab-tests/", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["tests"]) == 2
        assert data["total"] == 2

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_get_ab_test_success(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test successful AB test retrieval."""
        mock_manager = AsyncMock()
        mock_test = ABTestResponse(
            id="test-123",
            name="Test AB Test",
            description="Test description",
            status=TestStatus.RUNNING,
            created_by="testuser",
            variants=[{"name": "control", "allocation": 50}],
            created_at="2024-01-01T12:00:00Z",
            updated_at="2024-01-01T12:00:00Z",
        )
        mock_manager.get_test.return_value = mock_test
        mock_get_manager.return_value = mock_manager

        response = await client.get(
            "/api/v1/ab-tests/test-123", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "test-123"
        assert data["name"] == "Test AB Test"
        assert data["status"] == "running"

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_get_ab_test_not_found(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test AB test retrieval for non-existent test."""
        mock_manager = AsyncMock()
        mock_manager.get_test.return_value = None
        mock_get_manager.return_value = mock_manager

        response = await client.get(
            "/api/v1/ab-tests/nonexistent", headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_start_ab_test_success(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test successful AB test start."""
        mock_manager = AsyncMock()
        mock_test = ABTestResponse(
            id="test-123",
            name="Test AB Test",
            description="Test description",
            status=TestStatus.DRAFT,
            created_by="testuser",
            variants=[{"name": "control", "allocation": 50}],
            created_at="2024-01-01T12:00:00Z",
            updated_at="2024-01-01T12:00:00Z",
        )
        mock_manager.get_test.return_value = mock_test
        mock_manager.start_test.return_value = True
        mock_get_manager.return_value = mock_manager

        response = await client.post(
            "/api/v1/ab-tests/test-123/start", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["action"] == "start"

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_start_ab_test_invalid_status(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test starting AB test with invalid status."""
        mock_manager = AsyncMock()
        mock_test = ABTestResponse(
            id="test-123",
            name="Test AB Test",
            description="Test description",
            status=TestStatus.RUNNING,  # Already running
            created_by="testuser",
            variants=[{"name": "control", "allocation": 50}],
            created_at="2024-01-01T12:00:00Z",
            updated_at="2024-01-01T12:00:00Z",
        )
        mock_manager.get_test.return_value = mock_test
        mock_get_manager.return_value = mock_manager

        response = await client.post(
            "/api/v1/ab-tests/test-123/start", headers=auth_headers
        )
        assert response.status_code == 400

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_delete_running_test_forbidden(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test that deleting running test is forbidden."""
        mock_manager = AsyncMock()
        mock_test = ABTestResponse(
            id="test-123",
            name="Test AB Test",
            description="Test description",
            status=TestStatus.RUNNING,  # Running test
            created_by="testuser",
            variants=[{"name": "control", "allocation": 50}],
            created_at="2024-01-01T12:00:00Z",
            updated_at="2024-01-01T12:00:00Z",
        )
        mock_manager.get_test.return_value = mock_test
        mock_get_manager.return_value = mock_manager

        response = await client.delete(
            "/api/v1/ab-tests/test-123", headers=auth_headers
        )
        assert response.status_code == 400

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_access_other_user_test_forbidden(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test that accessing other user's test is forbidden."""
        mock_manager = AsyncMock()
        mock_test = ABTestResponse(
            id="test-123",
            name="Test AB Test",
            description="Test description",
            status=TestStatus.DRAFT,
            created_by="otheruser",  # Different user
            variants=[{"name": "control", "allocation": 50}],
            created_at="2024-01-01T12:00:00Z",
            updated_at="2024-01-01T12:00:00Z",
        )
        mock_manager.get_test.return_value = mock_test
        mock_get_manager.return_value = mock_manager

        response = await client.get(
            "/api/v1/ab-tests/test-123", headers=auth_headers
        )
        assert response.status_code == 403

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_get_results_success(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test successful results retrieval."""
        mock_manager = AsyncMock()
        mock_test = ABTestResponse(
            id="test-123",
            name="Test AB Test",
            description="Test description",
            status=TestStatus.COMPLETED,
            created_by="testuser",
            variants=[{"name": "control", "allocation": 50}],
            created_at="2024-01-01T12:00:00Z",
            updated_at="2024-01-01T12:00:00Z",
        )
        mock_results = {
            "test_id": "test-123",
            "status": "completed",
            "results": {
                "control": {
                    "conversions": 100,
                    "conversion_rate": 10.0,
                },
                "variant_a": {
                    "conversions": 120,
                    "conversion_rate": 12.0,
                },
            },
            "winner": "variant_a",
            "confidence": 95.0,
        }
        mock_manager.get_test.return_value = mock_test
        mock_manager.get_test_results.return_value = mock_results
        mock_get_manager.return_value = mock_manager

        response = await client.get(
            "/api/v1/ab-tests/test-123/results", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["test_id"] == "test-123"
        assert data["winner"] == "variant_a"
        assert data["confidence"] == 95.0

    @pytest.mark.unit
    @patch("chatter.api.ab_testing.get_ab_test_manager")
    async def test_get_metrics_success(
        self, mock_get_manager, client: AsyncClient, auth_headers: dict
    ):
        """Test successful metrics retrieval."""
        mock_manager = AsyncMock()
        mock_test = ABTestResponse(
            id="test-123",
            name="Test AB Test",
            description="Test description",
            status=TestStatus.RUNNING,
            created_by="testuser",
            variants=[{"name": "control", "allocation": 50}],
            created_at="2024-01-01T12:00:00Z",
            updated_at="2024-01-01T12:00:00Z",
        )
        mock_metrics = {
            "test_id": "test-123",
            "participants": 1000,
            "conversion_metrics": {
                "control": {"participants": 500, "conversions": 50},
                "variant_a": {"participants": 500, "conversions": 60},
            },
            "statistical_significance": 0.85,
        }
        mock_manager.get_test.return_value = mock_test
        mock_manager.get_test_metrics.return_value = mock_metrics
        mock_get_manager.return_value = mock_manager

        response = await client.get(
            "/api/v1/ab-tests/test-123/metrics", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["test_id"] == "test-123"
        assert data["participants"] == 1000
        assert "conversion_metrics" in data
