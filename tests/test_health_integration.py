"""Integration tests for health API endpoints."""

import asyncio
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestHealthIntegration:
    """Integration tests for health API endpoints."""

    @pytest.mark.integration
    async def test_readiness_check_with_database(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test readiness check endpoint with real database connection."""
        response = await client.get("/readyz")

        # Should return 200 when database is available
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "chatter"
        assert "version" in data
        assert "environment" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert data["checks"]["database"]["status"] == "healthy"
        assert data["checks"]["database"]["connected"] is True

    @pytest.mark.integration
    async def test_readiness_check_database_timeout(
        self, client: AsyncClient
    ):
        """Test readiness check with database timeout simulation."""
        # Patch the health_check function to simulate timeout
        with patch(
            "chatter.api.health.health_check"
        ) as mock_health_check:
            mock_health_check.side_effect = TimeoutError(
                "Database timeout"
            )

            response = await client.get("/readyz")
            assert response.status_code == 503  # Service Unavailable

            data = response.json()
            assert data["status"] == "not_ready"
            assert data["service"] == "chatter"
            assert data["checks"]["database"]["status"] == "unhealthy"
            assert data["checks"]["database"]["connected"] is False
            assert "timeout" in data["checks"]["database"]["error"]

    @pytest.mark.integration
    async def test_readiness_check_database_error(
        self, client: AsyncClient
    ):
        """Test readiness check with database connection error."""
        # Patch the health_check function to simulate error
        with patch(
            "chatter.api.health.health_check"
        ) as mock_health_check:
            mock_health_check.side_effect = Exception(
                "Connection failed"
            )

            response = await client.get("/readyz")
            assert response.status_code == 503  # Service Unavailable

            data = response.json()
            assert data["status"] == "not_ready"
            assert data["service"] == "chatter"
            assert data["checks"]["database"]["status"] == "unhealthy"
            assert data["checks"]["database"]["connected"] is False
            assert (
                "Connection failed"
                in data["checks"]["database"]["error"]
            )

    @pytest.mark.integration
    async def test_health_endpoints_response_consistency(
        self, client: AsyncClient
    ):
        """Test that all health endpoints return consistent service information."""
        # Get responses from all health endpoints
        health_response = await client.get("/healthz")
        liveness_response = await client.get("/live")
        readiness_response = await client.get("/readyz")
        metrics_response = await client.get("/metrics")

        # All should return 200 (readiness might be 503 but that's ok for this test)
        assert health_response.status_code == 200
        assert liveness_response.status_code == 200
        assert readiness_response.status_code in [200, 503]
        assert metrics_response.status_code == 200

        # Extract data
        health_data = health_response.json()
        liveness_data = liveness_response.json()
        readiness_data = readiness_response.json()
        metrics_data = metrics_response.json()

        # All should have consistent service information
        expected_service = "chatter"
        assert health_data["service"] == expected_service
        assert liveness_data["service"] == expected_service
        assert readiness_data["service"] == expected_service
        assert metrics_data["service"] == expected_service

        # Versions should match
        version = health_data["version"]
        assert liveness_data["version"] == version
        assert readiness_data["version"] == version
        assert metrics_data["version"] == version

        # Environments should match
        environment = health_data["environment"]
        assert liveness_data["environment"] == environment
        assert readiness_data["environment"] == environment
        assert metrics_data["environment"] == environment

    @pytest.mark.integration
    async def test_readiness_check_performance(
        self, client: AsyncClient
    ):
        """Test that readiness check completes within reasonable time."""
        import time

        start_time = time.time()
        response = await client.get("/readyz")
        end_time = time.time()

        # Should complete within 10 seconds (including 5s timeout buffer)
        response_time = end_time - start_time
        assert response_time < 10.0

        # Response should be valid regardless of status
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "checks" in data

    @pytest.mark.integration
    async def test_correlation_trace_nonexistent_id(
        self, client: AsyncClient
    ):
        """Test correlation trace for non-existent correlation ID."""
        correlation_id = "nonexistent-correlation-id-12345"
        response = await client.get(f"/trace/{correlation_id}")

        # Should return 200 even for non-existent IDs
        assert response.status_code == 200

        data = response.json()
        assert data["correlation_id"] == correlation_id
        assert data["trace_length"] == 0
        assert data["requests"] == []

    @pytest.mark.integration
    async def test_metrics_endpoint_structure(
        self, client: AsyncClient
    ):
        """Test that metrics endpoint returns proper data structure."""
        response = await client.get("/metrics")
        assert response.status_code == 200

        data = response.json()

        # Required fields
        required_fields = [
            "timestamp",
            "service",
            "version",
            "environment",
            "health",
            "performance",
            "endpoints",
        ]
        for field in required_fields:
            assert (
                field in data
            ), f"Required field '{field}' missing from metrics response"

        # Health section should have status
        assert "status" in data["health"]

        # Performance section should have basic metrics
        assert isinstance(data["performance"], dict)

        # Endpoints section should be a dictionary
        assert isinstance(data["endpoints"], dict)

    @pytest.mark.integration
    async def test_multiple_readiness_checks_isolation(
        self, client: AsyncClient
    ):
        """Test that multiple readiness checks don't interfere with each other."""
        # Make multiple concurrent requests
        tasks = []
        for _ in range(5):
            task = asyncio.create_task(client.get("/readyz"))
            tasks.append(task)

        # Wait for all to complete
        responses = await asyncio.gather(*tasks)

        # All should return valid responses
        for response in responses:
            assert response.status_code in [200, 503]
            data = response.json()
            assert "status" in data
            assert "checks" in data
            assert "database" in data["checks"]

    @pytest.mark.integration
    async def test_health_endpoints_concurrent_access(
        self, client: AsyncClient
    ):
        """Test concurrent access to all health endpoints."""
        # Create tasks for each endpoint
        tasks = [
            asyncio.create_task(client.get("/healthz")),
            asyncio.create_task(client.get("/live")),
            asyncio.create_task(client.get("/readyz")),
            asyncio.create_task(client.get("/metrics")),
            asyncio.create_task(
                client.get("/trace/concurrent-test-123")
            ),
        ]

        # Wait for all to complete
        responses = await asyncio.gather(*tasks)

        # All should return valid responses
        assert responses[0].status_code == 200  # healthz
        assert responses[1].status_code == 200  # live
        assert responses[2].status_code in [200, 503]  # readyz
        assert responses[3].status_code == 200  # metrics
        assert responses[4].status_code == 200  # trace

        # Verify response data structure
        for _i, response in enumerate(responses):
            data = response.json()
            assert (
                "service" in data or "correlation_id" in data
            )  # All should have one of these
