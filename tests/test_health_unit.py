"""Unit tests for health API endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from httpx import AsyncClient

from chatter.schemas.health import HealthStatus, ReadinessStatus


class TestHealthUnit:
    """Unit tests for health API endpoints."""

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
        assert data["status"] == "alive"
        assert data["service"] == "chatter"
        assert "version" in data
        assert "environment" in data

    @pytest.mark.unit
    async def test_health_and_liveness_different_status(self, client: AsyncClient):
        """Test that health and liveness return different status values."""
        health_response = await client.get("/healthz")
        liveness_response = await client.get("/live")
        
        health_data = health_response.json()
        liveness_data = liveness_response.json()
        
        assert health_data["status"] == "healthy"
        assert liveness_data["status"] == "alive"
        assert health_data["service"] == liveness_data["service"]

    @pytest.mark.unit
    async def test_metrics_endpoint_without_monitoring(self, client: AsyncClient):
        """Test metrics endpoint when monitoring module is not available."""
        # This should work even without monitoring module
        response = await client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert data["service"] == "chatter"
        assert "version" in data
        assert "environment" in data
        assert "health" in data
        assert "performance" in data
        assert "endpoints" in data
        
        # Should have default values when monitoring unavailable
        assert data["health"]["status"] == "unknown"
        assert data["performance"]["requests"] == 0
        assert data["endpoints"] == {}

    @pytest.mark.unit
    async def test_correlation_trace_without_monitoring(self, client: AsyncClient):
        """Test correlation trace endpoint when monitoring is not available."""
        correlation_id = "test-correlation-123"
        response = await client.get(f"/trace/{correlation_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["correlation_id"] == correlation_id
        assert data["trace_length"] == 0
        assert data["requests"] == []

    @pytest.mark.unit
    @patch('chatter.core.monitoring.get_monitoring_service')
    async def test_metrics_endpoint_with_monitoring_success(self, mock_get_monitoring, client: AsyncClient):
        """Test metrics endpoint when monitoring service is available."""
        # Mock the monitoring service
        mock_service = AsyncMock()
        mock_service.get_system_health.return_value = {
            "status": "healthy",
            "checks_available": True,
            "cpu_usage": 15.2,
            "memory_usage": 45.8
        }
        mock_service.stats_by_endpoint = {
            "/healthz": {"requests": 100, "avg_response_time": 10.5},
            "/readyz": {"requests": 50, "avg_response_time": 25.3}
        }
        mock_get_monitoring.return_value = mock_service

        response = await client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["health"]["status"] == "healthy"
        assert data["health"]["checks_available"] is True
        assert "/healthz" in data["endpoints"]
        assert "/readyz" in data["endpoints"]

    @pytest.mark.unit
    @patch('chatter.core.monitoring.get_monitoring_service')
    async def test_metrics_endpoint_with_monitoring_error(self, mock_get_monitoring, client: AsyncClient):
        """Test metrics endpoint when monitoring service raises an exception."""
        mock_get_monitoring.side_effect = Exception("Monitoring service error")

        response = await client.get("/metrics")
        assert response.status_code == 500  # Internal server error
        
        data = response.json()
        assert data["type"] == "about:blank"
        assert "Metrics collection failed" in data["detail"]

    @pytest.mark.unit
    @patch('chatter.core.monitoring.get_monitoring_service')
    async def test_correlation_trace_with_monitoring_success(self, mock_get_monitoring, client: AsyncClient):
        """Test correlation trace endpoint when monitoring service is available."""
        correlation_id = "test-correlation-123"
        mock_requests = [
            {"timestamp": "2024-01-01T12:00:00Z", "method": "GET", "path": "/healthz"},
            {"timestamp": "2024-01-01T12:00:01Z", "method": "GET", "path": "/readyz"}
        ]
        
        mock_service = AsyncMock()
        mock_service.get_correlation_trace.return_value = mock_requests
        mock_get_monitoring.return_value = mock_service

        response = await client.get(f"/trace/{correlation_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["correlation_id"] == correlation_id
        assert data["trace_length"] == 2
        assert data["requests"] == mock_requests

    @pytest.mark.unit
    @patch('chatter.core.monitoring.get_monitoring_service')
    async def test_correlation_trace_with_monitoring_error(self, mock_get_monitoring, client: AsyncClient):
        """Test correlation trace endpoint when monitoring service raises an exception."""
        correlation_id = "test-correlation-123"
        mock_get_monitoring.side_effect = Exception("Monitoring service error")

        response = await client.get(f"/trace/{correlation_id}")
        assert response.status_code == 500  # Internal server error
        
        data = response.json()
        assert data["type"] == "about:blank"
        assert f"Failed to get trace for correlation ID: {correlation_id}" in data["detail"]

    @pytest.mark.unit
    async def test_metrics_timestamp_format(self, client: AsyncClient):
        """Test that metrics endpoint returns properly formatted timestamp."""
        response = await client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        timestamp_str = data["timestamp"]
        
        # Should be able to parse as ISO format datetime
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        assert timestamp.tzinfo is not None  # Should include timezone info
        
        # Should be recent (within last minute)
        now = datetime.now(timezone.utc)
        time_diff = abs((now - timestamp).total_seconds())
        assert time_diff < 60  # Should be within last minute