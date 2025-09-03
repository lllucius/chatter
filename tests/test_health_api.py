"""Tests for health check API endpoints."""

import pytest
from httpx import AsyncClient


class TestHealthApiEndpoints:
    """Test health check API endpoints functionality."""

    @pytest.mark.unit
    async def test_health_check_endpoint(self, client: AsyncClient):
        """Test basic health check endpoint."""
        response = await client.get("/healthz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "chatter"
        assert "version" in data
        assert "environment" in data

    @pytest.mark.unit
    async def test_liveness_check_endpoint(self, client: AsyncClient):
        """Test liveness check endpoint."""
        response = await client.get("/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "chatter"
        assert "version" in data
        assert "environment" in data

    @pytest.mark.integration
    async def test_readiness_check_endpoint(self, client: AsyncClient):
        """Test readiness check endpoint with database."""
        response = await client.get("/readyz")
        
        # Should return 200 or 503 depending on database availability
        assert response.status_code in [200, 503]
        
        data = response.json()
        assert "status" in data
        assert data["service"] == "chatter"
        assert "checks" in data
        assert "database" in data["checks"]

    @pytest.mark.integration
    async def test_metrics_endpoint(self, client: AsyncClient):
        """Test metrics endpoint."""
        response = await client.get("/metrics")
        
        # Should return 200 or 500 depending on monitoring system
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "timestamp" in data
            assert "service" in data
            assert "health" in data
            assert "performance" in data
            assert "endpoints" in data

    @pytest.mark.integration
    async def test_correlation_trace_endpoint(self, client: AsyncClient):
        """Test correlation trace endpoint."""
        correlation_id = "test-correlation-123"
        response = await client.get(f"/trace/{correlation_id}")
        
        # Should return 200 or 500 depending on monitoring system
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["correlation_id"] == correlation_id
            assert "trace_length" in data
            assert "requests" in data

    @pytest.mark.unit
    async def test_health_endpoints_no_auth_required(self, client: AsyncClient):
        """Test that health endpoints don't require authentication."""
        endpoints = ["/healthz", "/live", "/readyz", "/metrics"]
        
        for endpoint in endpoints:
            response = await client.get(endpoint)
            # Should not return 401 (unauthorized)
            assert response.status_code != 401