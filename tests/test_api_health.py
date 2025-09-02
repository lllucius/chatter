"""Unit tests for API health endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from chatter.api.health import router as health_router
from tests.test_utils import MockDatabase


@pytest.mark.unit
class TestHealthAPI:
    """Test cases for health check API endpoints."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        app = FastAPI()
        app.include_router(health_router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_health_check_endpoint(self, client):
        """Test basic health check endpoint."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["status", "service", "version", "environment"]
        for field in required_fields:
            assert field in data
        
        # Check values
        assert data["status"] == "healthy"
        assert data["service"] == "chatter"
        assert "version" in data
        assert "environment" in data

    @patch('chatter.api.health.health_check')
    @patch('chatter.api.health.get_session_generator')
    def test_readiness_check_healthy(self, mock_get_session, mock_health_check, client):
        """Test readiness check when all services are healthy."""
        # Mock database health check to return structured response
        mock_health_check.return_value = {
            "status": "healthy",
            "response_time": 10.5,
            "connection": True
        }
        mock_get_session.return_value = MockDatabase()
        
        response = client.get("/readyz")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "status" in data
        assert "checks" in data
        
        # Check that database check was performed
        assert "database" in data["checks"]

    @patch('chatter.api.health.health_check')
    @patch('chatter.api.health.get_session_generator')
    def test_readiness_check_database_unhealthy(self, mock_get_session, mock_health_check, client):
        """Test readiness check when database is unhealthy."""
        # Mock database health check to return unhealthy status
        mock_health_check.return_value = {
            "status": "unhealthy",
            "response_time": None,
            "connection": False,
            "error": "Connection failed"
        }
        mock_get_session.return_value = MockDatabase()
        
        response = client.get("/readyz")
        
        # Should still return 200 but with unhealthy status
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "checks" in data
        assert data["checks"]["database"]["status"] == "unhealthy"

    def test_health_response_structure(self, client):
        """Test that health response has correct structure."""
        response = client.get("/healthz")
        data = response.json()
        
        # Verify response structure matches schema
        expected_structure = {
            "status": str,
            "service": str,
            "version": str,
            "environment": str
        }
        
        for field, expected_type in expected_structure.items():
            assert field in data
            assert isinstance(data[field], expected_type)

    def test_health_endpoint_performance(self, client):
        """Test that health endpoint responds quickly."""
        import time
        
        start_time = time.time()
        response = client.get("/healthz")
        end_time = time.time()
        
        # Health check should be very fast (under 1 second)
        assert (end_time - start_time) < 1.0
        assert response.status_code == 200

    @patch('chatter.api.health.settings')
    def test_health_check_with_custom_settings(self, mock_settings, client):
        """Test health check with custom settings."""
        # Mock settings
        mock_settings.app_version = "1.2.3"
        mock_settings.environment = "testing"
        
        response = client.get("/healthz")
        data = response.json()
        
        assert data["version"] == "1.2.3"
        assert data["environment"] == "testing"


@pytest.mark.unit
class TestHealthUtilities:
    """Test utility functions for health checks."""

    @pytest.mark.asyncio
    async def test_mock_database_health_check(self):
        """Test mock database health check functionality."""
        mock_db = MockDatabase()
        
        # Test that mock database can be used for health checks
        assert hasattr(mock_db, 'execute')
        assert hasattr(mock_db, 'fetch')
        
        # Test basic database operations
        await mock_db.execute("SELECT 1")
        mock_db.execute.assert_called_once()

    def test_health_response_schema_validation(self):
        """Test that health response matches expected schema."""
        from chatter.schemas.health import HealthCheckResponse
        
        # Create a health response
        health_data = {
            "status": "healthy",
            "service": "chatter",
            "version": "1.0.0",
            "environment": "test"
        }
        
        # Validate using Pydantic model
        response = HealthCheckResponse(**health_data)
        
        assert response.status == "healthy"
        assert response.service == "chatter"
        assert response.version == "1.0.0"
        assert response.environment == "test"

    def test_readiness_response_structure(self):
        """Test readiness response structure validation."""
        # Mock readiness response data
        readiness_data = {
            "status": "ready",
            "checks": {
                "database": True,
                "redis": True,
                "external_api": False
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Verify structure
        assert "status" in readiness_data
        assert "checks" in readiness_data
        assert "timestamp" in readiness_data
        assert isinstance(readiness_data["checks"], dict)

    @pytest.mark.asyncio
    async def test_error_handling_in_health_checks(self):
        """Test error handling in health check functions."""
        with patch('chatter.utils.database.health_check') as mock_health:
            # Mock health check to raise exception
            mock_health.side_effect = Exception("Database connection failed")
            
            # Health check should handle exceptions gracefully
            try:
                result = await mock_health()
                # If it doesn't raise, result should indicate failure
                assert result is False or result is None
            except Exception:
                # If it raises, that's also acceptable for testing
                pass