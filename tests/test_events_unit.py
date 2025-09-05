"""Unit tests for events API endpoints."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import AsyncClient

from chatter.schemas.events import EventType


class TestEventsUnit:
    """Unit tests for events API endpoints."""

    @pytest.mark.unit
    async def test_events_stream_requires_auth(self, client: AsyncClient):
        """Test that events stream requires authentication."""
        response = await client.get("/api/v1/events/stream")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_admin_stream_requires_auth(self, client: AsyncClient):
        """Test that admin events stream requires authentication."""
        response = await client.get("/api/v1/events/admin/stream")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_events_stats_requires_auth(self, client: AsyncClient):
        """Test that events stats endpoint requires authentication."""
        response = await client.get("/api/v1/events/stats")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_test_event_requires_auth(self, client: AsyncClient):
        """Test that test event endpoint requires authentication."""
        response = await client.post("/api/v1/events/test-event")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_broadcast_test_requires_auth(self, client: AsyncClient):
        """Test that broadcast test endpoint requires authentication."""
        response = await client.post("/api/v1/events/broadcast-test")
        assert response.status_code == 401

    @pytest.mark.unit
    @patch('chatter.api.events.sse_service')
    async def test_events_stats_success(self, mock_sse_service, client: AsyncClient, auth_headers: dict):
        """Test events stats endpoint with mocked SSE service."""
        # Mock SSE service stats
        mock_sse_service.get_stats.return_value = {
            "active_connections": 5,
            "total_events_sent": 100,
            "events_per_second": 2.5,
            "connections_by_user": {
                "user1": 2,
                "user2": 3
            }
        }
        
        response = await client.get("/api/v1/events/stats", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["active_connections"] == 5
        assert data["total_events_sent"] == 100
        assert data["events_per_second"] == 2.5
        assert "connections_by_user" in data

    @pytest.mark.unit
    @patch('chatter.api.events.sse_service')
    async def test_test_event_success(self, mock_sse_service, client: AsyncClient, auth_headers: dict):
        """Test test event endpoint success."""
        mock_sse_service.broadcast_to_user.return_value = True
        
        test_data = {
            "event_type": "test.message",
            "data": {"message": "Hello World"},
            "user_id": "test-user-123"
        }
        
        response = await client.post(
            "/api/v1/events/test-event", 
            json=test_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "event_id" in data
        assert data["event_type"] == "test.message"

    @pytest.mark.unit
    @patch('chatter.api.events.sse_service')
    async def test_broadcast_test_success(self, mock_sse_service, client: AsyncClient, auth_headers: dict):
        """Test broadcast test endpoint success."""
        mock_sse_service.broadcast.return_value = True
        
        test_data = {
            "event_type": "broadcast.test",
            "data": {"message": "Broadcast message"}
        }
        
        response = await client.post(
            "/api/v1/events/broadcast-test",
            json=test_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "event_id" in data
        assert data["event_type"] == "broadcast.test"

    @pytest.mark.unit
    async def test_test_event_invalid_data(self, client: AsyncClient, auth_headers: dict):
        """Test test event endpoint with invalid data."""
        # Missing required fields
        test_data = {
            "data": {"message": "Hello World"}
            # Missing event_type
        }
        
        response = await client.post(
            "/api/v1/events/test-event",
            json=test_data,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    async def test_broadcast_test_invalid_data(self, client: AsyncClient, auth_headers: dict):
        """Test broadcast test endpoint with invalid data."""
        # Missing required fields
        test_data = {
            "data": {"message": "Broadcast message"}
            # Missing event_type
        }
        
        response = await client.post(
            "/api/v1/events/broadcast-test",
            json=test_data,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    @patch('chatter.api.events.get_unified_rate_limiter')
    async def test_events_stream_rate_limit(self, mock_get_rate_limiter, client: AsyncClient, auth_headers: dict):
        """Test events stream rate limiting."""
        from chatter.utils.unified_rate_limiter import RateLimitExceeded
        
        # Mock rate limiter to raise exception
        mock_rate_limiter = AsyncMock()
        mock_rate_limiter.check_rate_limit.side_effect = RateLimitExceeded(
            message="Rate limit exceeded",
            limit=50,
            window=3600,
            remaining=0
        )
        mock_get_rate_limiter.return_value = mock_rate_limiter
        
        response = await client.get("/api/v1/events/stream", headers=auth_headers)
        assert response.status_code == 429  # Rate limit exceeded

    @pytest.mark.unit
    @patch('chatter.api.events.sse_service')
    async def test_events_stream_connection_limit(self, mock_sse_service, client: AsyncClient, auth_headers: dict):
        """Test events stream connection limit."""
        # Mock SSE service to raise connection limit error
        mock_sse_service.create_connection.side_effect = ValueError("Too many connections")
        
        response = await client.get("/api/v1/events/stream", headers=auth_headers)
        assert response.status_code == 503  # Service unavailable

    @pytest.mark.unit
    @patch('chatter.api.events.sse_service')
    async def test_events_stream_connection_not_found(self, mock_sse_service, client: AsyncClient, auth_headers: dict):
        """Test events stream when connection cannot be retrieved."""
        # Mock SSE service to return connection ID but fail on get_connection
        mock_sse_service.create_connection.return_value = "connection-123"
        mock_sse_service.get_connection.return_value = None
        
        response = await client.get("/api/v1/events/stream", headers=auth_headers)
        
        # Should still return 200 but with empty stream
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    @pytest.mark.unit
    @patch('chatter.api.events.sse_service')
    async def test_admin_stream_requires_admin(self, mock_sse_service, client: AsyncClient, auth_headers: dict):
        """Test that admin stream requires admin privileges."""
        # Regular user should get forbidden
        response = await client.get("/api/v1/events/admin/stream", headers=auth_headers)
        assert response.status_code == 403  # Forbidden

    @pytest.mark.unit
    @patch('chatter.api.events.sse_service')
    async def test_events_stats_sse_service_error(self, mock_sse_service, client: AsyncClient, auth_headers: dict):
        """Test events stats when SSE service has an error."""
        mock_sse_service.get_stats.side_effect = Exception("SSE service error")
        
        response = await client.get("/api/v1/events/stats", headers=auth_headers)
        assert response.status_code == 500  # Internal server error

    @pytest.mark.unit
    @patch('chatter.api.events.sse_service')
    async def test_test_event_sse_service_error(self, mock_sse_service, client: AsyncClient, auth_headers: dict):
        """Test test event when SSE service has an error."""
        mock_sse_service.broadcast_to_user.side_effect = Exception("SSE service error")
        
        test_data = {
            "event_type": "test.message",
            "data": {"message": "Hello World"},
            "user_id": "test-user-123"
        }
        
        response = await client.post(
            "/api/v1/events/test-event",
            json=test_data,
            headers=auth_headers
        )
        assert response.status_code == 500  # Internal server error

    @pytest.mark.unit
    @patch('chatter.api.events.sse_service')
    async def test_broadcast_test_sse_service_error(self, mock_sse_service, client: AsyncClient, auth_headers: dict):
        """Test broadcast test when SSE service has an error."""
        mock_sse_service.broadcast.side_effect = Exception("SSE service error")
        
        test_data = {
            "event_type": "broadcast.test",
            "data": {"message": "Broadcast message"}
        }
        
        response = await client.post(
            "/api/v1/events/broadcast-test",
            json=test_data,
            headers=auth_headers
        )
        assert response.status_code == 500  # Internal server error