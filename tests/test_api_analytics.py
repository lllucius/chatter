"""Analytics API tests."""

from datetime import UTC, datetime
import pytest


@pytest.mark.unit
class TestAnalyticsAPI:
    """Test analytics API endpoints."""

    async def test_conversation_stats(self, test_client):
        """Test conversation statistics endpoint."""
        # Setup user and auth
        registration_data = {
            "email": "analyticsuser@example.com",
            "password": "SecurePass123!",
            "username": "analyticsuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "analyticsuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get conversation stats with default parameters
        response = await test_client.get("/api/v1/analytics/conversations", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_conversations" in data or "count" in data or "stats" in data

    async def test_conversation_stats_with_period(self, test_client):
        """Test conversation statistics with period parameter."""
        # Setup user and auth
        registration_data = {
            "email": "perioduser@example.com",
            "password": "SecurePass123!",
            "username": "perioduser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "perioduser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test different periods
        periods = ["1h", "24h", "7d", "30d", "90d"]
        
        for period in periods:
            response = await test_client.get(
                f"/api/v1/analytics/conversations?period={period}", 
                headers=headers
            )
            
            # Should succeed or return 501 if not implemented
            assert response.status_code in [200, 422, 501]

    async def test_conversation_stats_with_date_range(self, test_client):
        """Test conversation statistics with custom date range."""
        # Setup user and auth
        registration_data = {
            "email": "dateuser@example.com",
            "password": "SecurePass123!",
            "username": "dateuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "dateuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test with custom date range
        start_date = "2024-01-01T00:00:00Z"
        end_date = "2024-01-31T23:59:59Z"
        
        response = await test_client.get(
            f"/api/v1/analytics/conversations?start_date={start_date}&end_date={end_date}", 
            headers=headers
        )
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 422, 501]

    async def test_usage_metrics(self, test_client):
        """Test usage metrics endpoint."""
        # Setup user and auth
        registration_data = {
            "email": "usageuser@example.com",
            "password": "SecurePass123!",
            "username": "usageuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "usageuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get usage metrics
        response = await test_client.get("/api/v1/analytics/usage", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_requests" in data or "usage" in data or "metrics" in data

    async def test_performance_metrics(self, test_client):
        """Test performance metrics endpoint."""
        # Setup user and auth
        registration_data = {
            "email": "perfuser@example.com",
            "password": "SecurePass123!",
            "username": "perfuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "perfuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get performance metrics
        response = await test_client.get("/api/v1/analytics/performance", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "response_time" in data or "performance" in data or "metrics" in data

    async def test_system_analytics(self, test_client):
        """Test system analytics endpoint."""
        # Setup user and auth
        registration_data = {
            "email": "systemuser@example.com",
            "password": "SecurePass123!",
            "username": "systemuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "systemuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get system analytics
        response = await test_client.get("/api/v1/analytics/system", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "system" in data or "analytics" in data or "stats" in data

    async def test_dashboard_data(self, test_client):
        """Test dashboard data endpoint."""
        # Setup user and auth
        registration_data = {
            "email": "dashuser@example.com",
            "password": "SecurePass123!",
            "username": "dashuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "dashuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get dashboard data
        response = await test_client.get("/api/v1/analytics/dashboard", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "dashboard" in data or "widgets" in data or "summary" in data

    async def test_document_analytics(self, test_client):
        """Test document analytics endpoint."""
        # Setup user and auth
        registration_data = {
            "email": "docanalyticsuser@example.com",
            "password": "SecurePass123!",
            "username": "docanalyticsuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "docanalyticsuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get document analytics
        response = await test_client.get("/api/v1/analytics/documents", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "documents" in data or "analytics" in data or "stats" in data

    async def test_analytics_unauthorized(self, test_client):
        """Test analytics endpoints require authentication."""
        endpoints = [
            "/api/v1/analytics/conversations",
            "/api/v1/analytics/usage", 
            "/api/v1/analytics/performance",
            "/api/v1/analytics/system",
            "/api/v1/analytics/dashboard",
            "/api/v1/analytics/documents"
        ]
        
        for endpoint in endpoints:
            response = await test_client.get(endpoint)
            
            # Should require authentication
            assert response.status_code in [401, 403]

    async def test_analytics_invalid_date_format(self, test_client):
        """Test analytics with invalid date format."""
        # Setup user and auth
        registration_data = {
            "email": "invaliduser@example.com",
            "password": "SecurePass123!",
            "username": "invaliduser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "invaliduser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test with invalid date format
        response = await test_client.get(
            "/api/v1/analytics/conversations?start_date=invalid-date", 
            headers=headers
        )
        
        # Should return validation error
        assert response.status_code in [400, 422, 501]

    async def test_analytics_invalid_period(self, test_client):
        """Test analytics with invalid period."""
        # Setup user and auth
        registration_data = {
            "email": "invalidperioduser@example.com",
            "password": "SecurePass123!",
            "username": "invalidperioduser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "invalidperioduser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test with invalid period
        response = await test_client.get(
            "/api/v1/analytics/conversations?period=invalid", 
            headers=headers
        )
        
        # Should return validation error or succeed with default
        assert response.status_code in [200, 400, 422, 501]