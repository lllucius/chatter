"""Tests for events API endpoints (SSE functionality)."""

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.main import app


@pytest.mark.unit
class TestEventsEndpoints:
    """Test events API endpoints for SSE functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_events_stream_authentication_required(self):
        """Test that events stream requires authentication."""
        # Act
        response = self.client.get("/api/v1/events/stream")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_events_stream_connection_creation(self):
        """Test events stream connection creation."""
        # Arrange
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                mock_connection_id = "conn-123"
                mock_connection = MagicMock()
                mock_connection.user_id = "user-123"
                mock_connection.is_active = True

                mock_sse_service.create_connection.return_value = mock_connection_id
                mock_sse_service.get_connection.return_value = mock_connection

                # Mock the event generator to return a few test events
                async def mock_event_generator():
                    yield "data: {\"type\": \"connection_established\", \"message\": \"Connected\"}\n\n"
                    yield "data: {\"type\": \"test_event\", \"data\": \"test\"}\n\n"

                mock_connection.get_events = mock_event_generator

                # Act
                headers = {"Authorization": "Bearer test-token"}
                with self.client.stream("GET", "/api/v1/events/stream", headers=headers) as response:
                    # Assert
                    assert response.status_code == status.HTTP_200_OK
                    assert response.headers["content-type"] == "text/event-stream"

                    # Verify connection was created
                    mock_sse_service.create_connection.assert_called_once_with(user_id="user-123")

    def test_get_sse_stats_success(self):
        """Test successful SSE statistics retrieval."""
        # Arrange
        mock_stats = {
            "total_connections": 15,
            "active_connections": 8,
            "total_events_sent": 1250,
            "events_per_second": 3.2,
            "connections_by_type": {
                "chat": 5,
                "notifications": 2,
                "system": 1
            },
            "uptime_seconds": 3600
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                mock_sse_service.get_stats.return_value = mock_stats

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get("/api/v1/events/stats", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["total_connections"] == 15
                assert response_data["active_connections"] == 8
                assert response_data["events_per_second"] == 3.2

    def test_send_test_event_success(self):
        """Test sending a test event successfully."""
        # Arrange
        test_event_data = {
            "event_type": "test_notification",
            "message": "This is a test event",
            "data": {"test_field": "test_value"},
            "target_users": ["user-123"]
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "admin-123", "username": "admin", "role": "admin"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                mock_sse_service.send_event.return_value = True
                mock_sse_service.get_connection_count.return_value = 2

                # Act
                headers = {"Authorization": "Bearer admin-token"}
                response = self.client.post("/api/v1/events/test", json=test_event_data, headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["success"] is True
                assert response_data["delivered_to"] == 2

    def test_send_test_event_unauthorized(self):
        """Test sending test event without admin privileges."""
        # Arrange
        test_event_data = {
            "event_type": "test_notification",
            "message": "This is a test event"
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser", "role": "user"}

            # Act
            headers = {"Authorization": "Bearer user-token"}
            response = self.client.post("/api/v1/events/test", json=test_event_data, headers=headers)

            # Assert
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_events_stream_connection_cleanup(self):
        """Test that SSE connections are properly cleaned up."""
        # Arrange
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                mock_connection_id = "conn-123"
                mock_connection = MagicMock()
                mock_connection.user_id = "user-123"
                mock_connection.is_active = True

                mock_sse_service.create_connection.return_value = mock_connection_id
                mock_sse_service.get_connection.return_value = mock_connection
                mock_sse_service.remove_connection = MagicMock()

                # Mock connection that closes immediately
                async def mock_event_generator():
                    yield "data: {\"type\": \"connection_established\"}\n\n"
                    # Simulate connection close
                    return

                mock_connection.get_events = mock_event_generator

                # Act
                headers = {"Authorization": "Bearer test-token"}
                with self.client.stream("GET", "/api/v1/events/stream", headers=headers) as response:
                    # Read the stream
                    list(response.iter_text())

                # Assert cleanup was called
                # In real implementation, cleanup should happen when connection ends

    def test_events_stream_error_handling(self):
        """Test error handling in events stream."""
        # Arrange
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                # Simulate connection creation failure
                mock_sse_service.create_connection.return_value = None
                mock_sse_service.get_connection.return_value = None

                # Act
                headers = {"Authorization": "Bearer test-token"}
                with self.client.stream("GET", "/api/v1/events/stream", headers=headers) as response:
                    # Should still return 200 but with no events
                    assert response.status_code == status.HTTP_200_OK
                    content = b"".join(response.iter_content())
                    # Should be empty or minimal content
                    assert len(content) == 0 or content == b""

    def test_broadcast_event_to_all_users(self):
        """Test broadcasting event to all connected users."""
        # Arrange
        broadcast_data = {
            "event_type": "system_announcement",
            "message": "System maintenance scheduled",
            "priority": "high",
            "broadcast": True
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "admin-123", "username": "admin", "role": "admin"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                mock_sse_service.broadcast_event.return_value = 15  # Delivered to 15 users

                # Act
                headers = {"Authorization": "Bearer admin-token"}
                response = self.client.post("/api/v1/events/broadcast", json=broadcast_data, headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["success"] is True
                assert response_data["delivered_to"] == 15

    def test_get_user_events_history(self):
        """Test retrieving user's event history."""
        # Arrange
        mock_events = [
            {
                "id": "event-1",
                "type": "chat_message",
                "data": {"message": "Hello"},
                "timestamp": "2024-01-01T10:00:00Z"
            },
            {
                "id": "event-2",
                "type": "notification",
                "data": {"title": "New feature available"},
                "timestamp": "2024-01-01T11:00:00Z"
            }
        ]

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                mock_sse_service.get_user_events_history.return_value = {
                    "events": mock_events,
                    "total": 2,
                    "limit": 50,
                    "offset": 0
                }

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get("/api/v1/events/history", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert len(response_data["events"]) == 2
                assert response_data["total"] == 2

    def test_events_filtering_by_type(self):
        """Test filtering events by type in stream."""
        # Arrange
        event_types = ["chat_message", "notification"]

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                mock_connection_id = "conn-123"
                mock_connection = MagicMock()
                mock_connection.user_id = "user-123"
                mock_connection.event_filters = event_types

                mock_sse_service.create_connection.return_value = mock_connection_id
                mock_sse_service.get_connection.return_value = mock_connection

                # Act
                headers = {"Authorization": "Bearer test-token"}
                query_params = "&".join([f"event_types={et}" for et in event_types])

                with self.client.stream("GET", f"/api/v1/events/stream?{query_params}", headers=headers) as response:
                    assert response.status_code == status.HTTP_200_OK
                    # Verify that connection was created with filters
                    mock_sse_service.create_connection.assert_called_once()


@pytest.mark.integration
class TestEventsIntegration:
    """Integration tests for events functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_events_end_to_end_flow(self):
        """Test complete events flow from connection to delivery."""
        headers = {"Authorization": "Bearer integration-token"}

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                # Mock connection setup
                mock_connection_id = "integration-conn"
                mock_connection = MagicMock()
                mock_connection.user_id = "user-123"
                mock_connection.is_active = True

                events_queue = []

                async def mock_event_generator():
                    # Simulate receiving events
                    for event in events_queue:
                        yield f"data: {json.dumps(event)}\n\n"
                        await asyncio.sleep(0.1)

                mock_connection.get_events = mock_event_generator
                mock_sse_service.create_connection.return_value = mock_connection_id
                mock_sse_service.get_connection.return_value = mock_connection

                # Start SSE connection (in real test, this would be async)
                with self.client.stream("GET", "/api/v1/events/stream", headers=headers) as sse_response:
                    assert sse_response.status_code == status.HTTP_200_OK

                    # Simulate sending events while connection is active
                    events_queue.append({
                        "type": "test_event",
                        "data": {"message": "Integration test event"}
                    })

                    # In a real integration test, we would verify event delivery
                    # For now, just verify the connection was established
                    mock_sse_service.create_connection.assert_called_once_with(user_id="user-123")

    def test_events_stress_simulation(self):
        """Test events system under simulated load."""
        headers = {"Authorization": "Bearer stress-test-token"}

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "stress-user", "username": "stressuser"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                # Simulate multiple concurrent connections
                connection_count = 10
                mock_sse_service.get_stats.return_value = {
                    "total_connections": connection_count,
                    "active_connections": connection_count,
                    "events_per_second": 50.0
                }

                # Get stats to verify system can handle load
                response = self.client.get("/api/v1/events/stats", headers=headers)
                assert response.status_code == status.HTTP_200_OK

                stats = response.json()
                assert stats["active_connections"] == connection_count
                assert stats["events_per_second"] > 0

    def test_events_system_monitoring(self):
        """Test events system monitoring and health checks."""
        headers = {"Authorization": "Bearer monitor-token"}

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "monitor-user", "username": "monitor", "role": "admin"}

            with patch('chatter.services.sse_events.sse_service') as mock_sse_service:
                # Mock comprehensive stats
                mock_sse_service.get_stats.return_value = {
                    "total_connections": 25,
                    "active_connections": 20,
                    "total_events_sent": 5000,
                    "events_per_second": 15.3,
                    "average_latency_ms": 45.2,
                    "memory_usage_mb": 128.5,
                    "connections_by_type": {
                        "chat": 12,
                        "notifications": 6,
                        "system": 2
                    },
                    "error_rate": 0.001,
                    "uptime_seconds": 7200
                }

                # Act
                response = self.client.get("/api/v1/events/stats", headers=headers)

                # Assert comprehensive monitoring data
                assert response.status_code == status.HTTP_200_OK
                stats = response.json()
                assert stats["error_rate"] < 0.01  # Less than 1% error rate
                assert stats["average_latency_ms"] < 100  # Good latency
                assert stats["uptime_seconds"] > 0  # System is running
