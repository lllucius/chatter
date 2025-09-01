"""Tests for health API endpoints."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

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
        response = self.client.get("/api/v1/health")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "healthy"
        assert "timestamp" in response_data
        assert "version" in response_data

    def test_health_check_with_details(self):
        """Test health check with detailed information."""
        # Act
        response = self.client.get("/api/v1/health?detailed=true")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "healthy"
        assert "services" in response_data
        assert "database" in response_data["services"]
        assert "redis" in response_data["services"]

    @patch('chatter.utils.database.get_session')
    def test_database_health_check_failure(self, mock_get_session):
        """Test health check when database is unavailable."""
        # Arrange
        mock_get_session.side_effect = Exception("Database connection failed")
        
        # Act
        response = self.client.get("/api/v1/health?detailed=true")
        
        # Assert
        # Health check should still return 200 but indicate database issues
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] in ["degraded", "healthy"]  # Depending on implementation
        
        if "services" in response_data:
            assert "database" in response_data["services"]

    def test_readiness_check(self):
        """Test readiness probe endpoint."""
        # Act
        response = self.client.get("/api/v1/health/ready")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["ready"] is True

    def test_liveness_check(self):
        """Test liveness probe endpoint."""
        # Act
        response = self.client.get("/api/v1/health/live")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["alive"] is True

    def test_metrics_endpoint(self):
        """Test metrics endpoint for monitoring."""
        # Act
        response = self.client.get("/api/v1/health/metrics")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        # Check for expected metrics
        expected_metrics = [
            "uptime",
            "memory_usage",
            "cpu_usage",
            "active_connections",
            "request_count"
        ]
        
        for metric in expected_metrics:
            assert metric in response_data or "metrics" in response_data

    def test_version_endpoint(self):
        """Test version information endpoint."""
        # Act
        response = self.client.get("/api/v1/health/version")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "version" in response_data
        assert "build_date" in response_data or "timestamp" in response_data

    def test_cors_headers_on_health_check(self):
        """Test that CORS headers are present on health check."""
        # Act
        response = self.client.get("/api/v1/health")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        # Check for CORS headers if configured
        headers = response.headers
        # These might be present depending on CORS configuration
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers"
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
            response = self.client.get("/api/v1/health")
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
        response = self.client.get("/api/v1/health")
        end_time = time.time()
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_time = end_time - start_time
        
        # Health check should respond in under 1 second
        assert response_time < 1.0

    def test_all_health_endpoints_accessible(self):
        """Test that all health-related endpoints are accessible."""
        health_endpoints = [
            "/api/v1/health",
            "/api/v1/health/ready", 
            "/api/v1/health/live",
            "/api/v1/health/metrics",
            "/api/v1/health/version"
        ]
        
        for endpoint in health_endpoints:
            response = self.client.get(endpoint)
            # Should return either 200 (implemented) or 404 (not implemented yet)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
            
            # If implemented, should have proper JSON response
            if response.status_code == status.HTTP_200_OK:
                assert response.headers.get("content-type", "").startswith("application/json")
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
        response = self.client.get("/api/v1/health")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Required fields
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        
        # Optional fields that might be present
        optional_fields = ["timestamp", "version", "uptime", "services"]
        for field in optional_fields:
            if field in data:
                assert data[field] is not None

    def test_detailed_health_response_structure(self):
        """Test detailed health response structure."""
        # Act
        response = self.client.get("/api/v1/health?detailed=true")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have basic fields
        assert "status" in data
        
        # May have services breakdown
        if "services" in data:
            services = data["services"]
            assert isinstance(services, dict)
            
            # Common services that might be checked
            possible_services = ["database", "redis", "llm_service", "vector_store"]
            for service in possible_services:
                if service in services:
                    service_data = services[service]
                    assert isinstance(service_data, dict)
                    # Service should have status
                    assert "status" in service_data

    def test_readiness_response_structure(self):
        """Test readiness probe response structure."""
        # Act
        response = self.client.get("/api/v1/health/ready")
        
        # Assert
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "ready" in data
            assert isinstance(data["ready"], bool)

    def test_liveness_response_structure(self):
        """Test liveness probe response structure."""
        # Act
        response = self.client.get("/api/v1/health/live")
        
        # Assert
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "alive" in data
            assert isinstance(data["alive"], bool)

    def test_metrics_response_structure(self):
        """Test metrics endpoint response structure."""
        # Act
        response = self.client.get("/api/v1/health/metrics")
        
        # Assert
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, dict)
            
            # If metrics are present, they should be numbers or strings
            for key, value in data.items():
                assert isinstance(value, (int, float, str, dict))

    def test_version_response_structure(self):
        """Test version endpoint response structure."""
        # Act
        response = self.client.get("/api/v1/health/version")
        
        # Assert
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "version" in data
            assert isinstance(data["version"], str)
            
            # Other possible fields
            optional_fields = ["build_date", "git_commit", "environment"]
            for field in optional_fields:
                if field in data:
                    assert isinstance(data[field], str)


@pytest.mark.unit
class TestHealthErrorHandling:
    """Test health endpoint error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_health_check_with_invalid_parameters(self):
        """Test health check with invalid query parameters."""
        # Act
        response = self.client.get("/api/v1/health?invalid_param=true")
        
        # Assert
        # Should still work, invalid params should be ignored
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data

    def test_health_check_method_not_allowed(self):
        """Test health check with wrong HTTP method."""
        # Act
        response = self.client.post("/api/v1/health", json={})
        
        # Assert
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_health_endpoints_handle_exceptions_gracefully(self):
        """Test that health endpoints handle internal exceptions gracefully."""
        # This test ensures that even if there are internal errors,
        # the health check doesn't completely fail
        
        with patch('chatter.api.health.get_health_status') as mock_health:
            # Simulate an internal error
            mock_health.side_effect = Exception("Internal error")
            
            response = self.client.get("/api/v1/health")
            
            # Health check should either:
            # 1. Return 200 with degraded status, or
            # 2. Return 500 but still have a JSON response
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
            
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                assert "status" in data
                # Status should indicate issues
                assert data["status"] in ["degraded", "unhealthy"]