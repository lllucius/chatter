"""Simple tests for health check API endpoints without database dependencies."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from chatter.api.health import router as health_router
from chatter.schemas.health import HealthCheckResponse


@pytest.fixture
def app():
    """Create a simple FastAPI app with only health routes."""
    app = FastAPI()
    app.include_router(health_router)
    return app


@pytest.fixture  
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestHealthApiBasic:
    """Basic tests for health check API endpoints without database."""

    def test_health_check_endpoint_basic(self, client):
        """Test basic health check endpoint."""
        response = client.get("/healthz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "chatter"
        assert "version" in data
        assert "environment" in data

    def test_liveness_check_endpoint_basic(self, client):
        """Test liveness check endpoint."""
        response = client.get("/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "chatter"
        assert "version" in data
        assert "environment" in data
        
    def test_liveness_and_health_different(self, client):
        """Test that liveness and health endpoints return different responses."""
        health_response = client.get("/healthz")
        liveness_response = client.get("/live")
        
        assert health_response.status_code == 200
        assert liveness_response.status_code == 200
        
        health_data = health_response.json()
        liveness_data = liveness_response.json()
        
        # Status should be different
        assert health_data["status"] == "healthy"
        assert liveness_data["status"] == "alive"
        
        # Other fields should be the same
        assert health_data["service"] == liveness_data["service"]
        assert health_data["version"] == liveness_data["version"] 
        assert health_data["environment"] == liveness_data["environment"]

    @patch('chatter.api.health.health_check')
    def test_readiness_check_healthy_db(self, mock_health_check, client):
        """Test readiness check with healthy database."""
        async def mock_health_check_func(session=None):
            return {
                "status": "healthy",
                "connected": True,
                "response_time_ms": 10.5
            }
        
        mock_health_check.side_effect = mock_health_check_func
        
        response = client.get("/readyz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "chatter"
        assert "checks" in data
        assert data["checks"]["database"]["status"] == "healthy"

    @patch('chatter.api.health.health_check')
    def test_readiness_check_unhealthy_db(self, mock_health_check, client):
        """Test readiness check with unhealthy database."""
        async def mock_health_check_func(session=None):
            return {
                "status": "unhealthy",
                "connected": False,
                "error": "Connection refused"
            }
        
        mock_health_check.side_effect = mock_health_check_func
        
        response = client.get("/readyz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["service"] == "chatter"
    @patch('chatter.api.health.health_check')
    def test_readiness_check_timeout(self, mock_health_check, client):
        """Test readiness check with database timeout."""
        import asyncio
        
        async def mock_health_check_func(session=None):
            raise asyncio.TimeoutError("Database timeout")
        
        mock_health_check.side_effect = mock_health_check_func
        
        response = client.get("/readyz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["service"] == "chatter"
        assert "checks" in data
        assert data["checks"]["database"]["status"] == "unhealthy"
        assert "timeout" in data["checks"]["database"]["error"]

    @patch('chatter.utils.monitoring.metrics_collector')
    def test_metrics_endpoint_success(self, mock_metrics_collector, client):
        """Test metrics endpoint when monitoring is available."""
        mock_metrics_collector.get_overall_stats.return_value = {"request_count": 100}
        mock_metrics_collector.get_health_metrics.return_value = {"status": "healthy"}
        mock_metrics_collector.get_endpoint_stats.return_value = {"/test": {"count": 10}}
        
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert data["service"] == "chatter"
        assert "health" in data
        assert "performance" in data
        assert "endpoints" in data

    @patch('chatter.utils.monitoring.metrics_collector')  
    def test_metrics_endpoint_failure(self, mock_metrics_collector, client):
        """Test metrics endpoint when monitoring fails."""
        mock_metrics_collector.get_overall_stats.side_effect = Exception("Monitoring unavailable")
        
        response = client.get("/metrics")
        assert response.status_code == 500
        
        data = response.json()
        assert "detail" in data
        assert "Metrics collection failed" in data["detail"]

    @patch('chatter.utils.monitoring.metrics_collector')
    def test_correlation_trace_endpoint_success(self, mock_metrics_collector, client):
        """Test correlation trace endpoint success."""
        correlation_id = "test-123"
        mock_trace = [
            {"timestamp": "2024-01-01T12:00:00Z", "method": "GET", "path": "/test"}
        ]
        mock_metrics_collector.get_correlation_trace.return_value = mock_trace
        
        response = client.get(f"/trace/{correlation_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["correlation_id"] == correlation_id
        assert data["trace_length"] == 1
        assert data["requests"] == mock_trace

    @patch('chatter.utils.monitoring.metrics_collector')
    def test_correlation_trace_endpoint_failure(self, mock_metrics_collector, client):
        """Test correlation trace endpoint failure."""
        correlation_id = "test-123"
        mock_metrics_collector.get_correlation_trace.side_effect = Exception("Trace not found")
        
        response = client.get(f"/trace/{correlation_id}")
        assert response.status_code == 500
        
        data = response.json()
        assert "detail" in data
        assert "Failed to get trace" in data["detail"]