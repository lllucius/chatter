"""Health check API tests."""

import pytest


@pytest.mark.unit
class TestHealthAPI:
    """Test health check API endpoints."""

    async def test_health_check_endpoint(self, test_client):
        """Test basic health check endpoint."""
        response = await test_client.get("/api/v1/healthz")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "chatter"
        assert "version" in data
        assert "environment" in data

    async def test_health_check_no_auth_required(self, test_client):
        """Test that health check doesn't require authentication."""
        response = await test_client.get("/api/v1/healthz")
        
        # Should work without any auth headers
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_readiness_check_endpoint(self, test_client):
        """Test readiness check endpoint with database connectivity."""
        response = await test_client.get("/api/v1/readyz")
        
        # Should succeed if database is available (in-memory SQLite for tests)
        assert response.status_code in [200, 503]  # 503 if DB unavailable
        
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]

    async def test_readiness_database_check(self, test_client):
        """Test readiness check includes database status."""
        response = await test_client.get("/api/v1/readyz")
        
        data = response.json()
        assert "checks" in data
        assert "database" in data["checks"]
        
        # Database check should have status
        db_check = data["checks"]["database"]
        assert "status" in db_check
        assert db_check["status"] in ["healthy", "unhealthy"]

    async def test_readiness_no_auth_required(self, test_client):
        """Test that readiness check doesn't require authentication."""
        response = await test_client.get("/api/v1/readyz")
        
        # Should work without any auth headers
        assert response.status_code in [200, 503]
        assert "status" in response.json()

    async def test_health_response_format(self, test_client):
        """Test health check response format compliance."""
        response = await test_client.get("/api/v1/healthz")
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields for health check
        required_fields = ["status", "service", "version", "environment"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Status should be valid
        assert data["status"] in ["healthy", "unhealthy"]
        assert data["service"] == "chatter"

    async def test_readiness_response_format(self, test_client):
        """Test readiness check response format compliance."""
        response = await test_client.get("/api/v1/readyz")
        
        data = response.json()
        
        # Required fields for readiness check
        required_fields = ["status", "checks"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Status should be valid
        assert data["status"] in ["ready", "not ready", "healthy", "unhealthy"]
        
        # Checks should be a dict
        assert isinstance(data["checks"], dict)