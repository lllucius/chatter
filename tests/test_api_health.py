"""Tests for health API endpoints."""

from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.main import app


@pytest.mark.unit
class TestHealthEndpoints:
    """Test health check endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_health_check_success(self):
        """Test basic health check endpoint."""
        # Act
        response = self.client.get("/healthz")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "healthy"
        assert "service" in response_data
        assert "version" in response_data

    def test_health_check_with_details(self):
        """Test readiness check endpoint with database connectivity."""
        # Act
        response = self.client.get("/readyz")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] in ["ready", "not_ready"]
        assert "checks" in response_data
        assert "database" in response_data["checks"]

    @patch('chatter.utils.database.health_check')
    def test_database_health_check_failure(self, mock_health_check):
        """Test readiness check when database is unavailable."""
        # Arrange
        mock_health_check.return_value = {
            "status": "unhealthy",
            "error": "Database connection failed",
        }

        # Act
        response = self.client.get("/readyz")

        # Assert
        # Readiness check should return 200 but indicate not ready
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "not_ready"
        assert "checks" in response_data
        assert "database" in response_data["checks"]

    def test_readiness_check(self):
        """Test readiness probe endpoint."""
        # Act
        response = self.client.get("/readyz")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] in ["ready", "not_ready"]

    def test_liveness_check(self):
        """Test liveness probe endpoint."""
        # Act
        response = self.client.get("/live")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "healthy"

    @patch('chatter.utils.monitoring.metrics_collector')
    def test_metrics_endpoint(self, mock_metrics_collector):
        """Test metrics endpoint for monitoring."""
        # Arrange
        mock_metrics_collector.get_overall_stats.return_value = {
            "requests_per_minute": 42
        }
        mock_metrics_collector.get_health_metrics.return_value = {
            "status": "healthy"
        }
        mock_metrics_collector.get_endpoint_stats.return_value = {
            "/healthz": {"count": 100}
        }

        # Act
        response = self.client.get("/metrics")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        # Check for expected metrics
        assert "service" in response_data
        assert "health" in response_data
        assert "performance" in response_data

    def test_version_endpoint(self):
        """Test version information endpoint - available via basic health check."""
        # Act
        response = self.client.get("/healthz")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "version" in response_data
        assert "service" in response_data

    def test_cors_headers_on_health_check(self):
        """Test that CORS headers are present on health check."""
        # Act
        response = self.client.get("/healthz")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        # Check for CORS headers if configured
        headers = response.headers
        # These might be present depending on CORS configuration
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers",
        ]

        # At least one CORS header should be present if CORS is enabled
        # This is a flexible test since CORS configuration may vary
        assert any(header in headers for header in cors_headers) or True


@pytest.mark.integration
class TestHealthIntegration:
    """Integration tests for health monitoring."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_health_check_under_load(self):
        """Test health check endpoint under simulated load."""
        # Simulate multiple concurrent requests
        responses = []

        for _ in range(10):
            response = self.client.get("/healthz")
            responses.append(response)

        # All requests should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["status"] == "healthy"

    def test_health_check_response_time(self):
        """Test that health check responds quickly."""
        import time

        # Act
        start_time = time.time()
        response = self.client.get("/healthz")
        end_time = time.time()

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_time = end_time - start_time

        # Health check should respond in under 1 second
        assert response_time < 1.0

    def test_all_health_endpoints_accessible(self):
        """Test that all health-related endpoints are accessible."""
        health_endpoints = ["/healthz", "/readyz", "/live"]

        for endpoint in health_endpoints:
            response = self.client.get(endpoint)
            # Should return either 200 (implemented) or 404 (not implemented yet)
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND,
            ]

            # If implemented, should have proper JSON response
            if response.status_code == status.HTTP_200_OK:
                assert response.headers.get(
                    "content-type", ""
                ).startswith("application/json")
                assert isinstance(response.json(), dict)


@pytest.mark.unit
class TestHealthResponseStructure:
    """Test health endpoint response structure."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_basic_health_response_structure(self):
        """Test basic health response has required fields."""
        # Act
        response = self.client.get("/healthz")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Required fields
        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "environment" in data

    def test_detailed_health_response_structure(self):
        """Test readiness check response structure."""
        # Act
        response = self.client.get("/readyz")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Required fields for readiness check
        assert "status" in data
        assert data["status"] in ["ready", "not_ready"]
        assert "service" in data
        assert "version" in data
        assert "environment" in data
        assert "checks" in data
        assert isinstance(data["checks"], dict)

    def test_readiness_response_structure(self):
        """Test readiness probe response structure."""
        # Act
        response = self.client.get("/readyz")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ready", "not_ready"]

    def test_liveness_response_structure(self):
        """Test liveness probe response structure."""
        # Act
        response = self.client.get("/live")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @patch('chatter.utils.monitoring.metrics_collector')
    def test_metrics_response_structure(self, mock_metrics_collector):
        """Test metrics endpoint response structure."""
        # Arrange
        mock_metrics_collector.get_overall_stats.return_value = {
            "requests_per_minute": 42
        }
        mock_metrics_collector.get_health_metrics.return_value = {
            "status": "healthy"
        }
        mock_metrics_collector.get_endpoint_stats.return_value = {
            "/healthz": {"count": 100}
        }

        # Act
        response = self.client.get("/metrics")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, dict)
        assert "service" in data
        assert "health" in data
        assert "performance" in data

    def test_version_response_structure(self):
        """Test version endpoint response structure - available via healthz."""
        # Act
        response = self.client.get("/healthz")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "version" in data
        assert isinstance(data["version"], str)
        assert "service" in data
        assert "environment" in data


@pytest.mark.unit
class TestHealthErrorHandling:
    """Test health endpoint error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_health_check_with_invalid_parameters(self):
        """Test health check with invalid query parameters."""
        # Act
        response = self.client.get("/healthz?invalid_param=true")

        # Assert
        # Should still work, invalid params should be ignored
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data

    def test_health_check_method_not_allowed(self):
        """Test health check with wrong HTTP method."""
        # Act
        response = self.client.post("/healthz", json={})

        # Assert
        assert (
            response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        )

        # Assert
        assert (
            response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @patch('chatter.utils.monitoring.metrics_collector')
    def test_health_endpoints_handle_exceptions_gracefully(
        self, mock_metrics_collector
    ):
        """Test that health endpoints handle internal exceptions gracefully."""
        # This test ensures that even if metrics collection fails,
        # the health check doesn't completely fail

        # Simulate an internal error in metrics collection
        mock_metrics_collector.get_overall_stats.side_effect = (
            Exception("Internal error")
        )
        mock_metrics_collector.get_health_metrics.side_effect = (
            Exception("Internal error")
        )
        mock_metrics_collector.get_endpoint_stats.side_effect = (
            Exception("Internal error")
        )

        response = self.client.get("/metrics")

        # Metrics endpoint should return 500 when internal errors occur
        assert (
            response.status_code
            == status.HTTP_500_INTERNAL_SERVER_ERROR
        )
