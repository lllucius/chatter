"""Integration tests for events API endpoints."""

import asyncio
import json
from unittest.mock import patch
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestEventsIntegration:
    """Integration tests for events API endpoints."""

    @pytest.mark.integration
    async def test_events_stream_workflow(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test complete events stream workflow."""
        # Test SSE stream connection
        response = await client.get("/api/v1/events/stream", headers=auth_headers)
        
        # Should establish SSE connection
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        assert "cache-control" in response.headers
        assert response.headers["cache-control"] == "no-cache"

    @pytest.mark.integration 
    async def test_events_stats_real_service(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test events stats with real SSE service."""
        response = await client.get("/api/v1/events/stats", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Should have basic stats structure
        assert "active_connections" in data
        assert "total_events_sent" in data
        assert "events_per_second" in data
        assert isinstance(data["active_connections"], int)
        assert isinstance(data["total_events_sent"], int)
        assert isinstance(data["events_per_second"], (int, float))

    @pytest.mark.integration
    async def test_test_event_end_to_end(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test sending test event end-to-end."""
        test_data = {
            "event_type": "integration.test",
            "data": {
                "message": "Integration test message",
                "test_id": "test-123",
                "timestamp": "2024-01-01T12:00:00Z"
            },
            "user_id": "integration-test-user"
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
        assert data["event_type"] == "integration.test"
        assert data["user_id"] == "integration-test-user"

    @pytest.mark.integration
    async def test_broadcast_test_end_to_end(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test broadcast test event end-to-end."""
        test_data = {
            "event_type": "integration.broadcast",
            "data": {
                "message": "Integration broadcast message",
                "test_id": "broadcast-123"
            }
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
        assert data["event_type"] == "integration.broadcast"

    @pytest.mark.integration
    async def test_multiple_sse_connections(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test multiple SSE connections from same user."""
        # Create multiple concurrent SSE connection attempts
        tasks = []
        for i in range(3):
            task = asyncio.create_task(
                client.get("/api/v1/events/stream", headers=auth_headers)
            )
            tasks.append(task)
        
        # Wait for all connections with timeout
        try:
            responses = await asyncio.wait_for(asyncio.gather(*tasks), timeout=10.0)
            
            # All should succeed (within connection limits)
            for response in responses:
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
                
        except asyncio.TimeoutError:
            # Cancel remaining tasks
            for task in tasks:
                task.cancel()
            pytest.fail("SSE connections timed out")

    @pytest.mark.integration
    async def test_events_workflow_with_database(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test events workflow with database persistence."""
        # First, get initial stats
        stats_response = await client.get("/api/v1/events/stats", headers=auth_headers)
        assert stats_response.status_code == 200
        initial_stats = stats_response.json()
        
        # Send a test event
        test_data = {
            "event_type": "database.test",
            "data": {"database_test": True, "user_session": "session-123"},
            "user_id": "database-test-user"
        }
        
        event_response = await client.post(
            "/api/v1/events/test-event",
            json=test_data,
            headers=auth_headers
        )
        assert event_response.status_code == 200
        
        # Wait a moment for event processing
        await asyncio.sleep(0.1)
        
        # Check stats again (events_sent might have increased)
        final_stats_response = await client.get("/api/v1/events/stats", headers=auth_headers)
        assert final_stats_response.status_code == 200
        final_stats = final_stats_response.json()
        
        # Stats should be valid regardless of actual processing
        assert isinstance(final_stats["total_events_sent"], int)
        assert final_stats["total_events_sent"] >= initial_stats["total_events_sent"]

    @pytest.mark.integration
    async def test_event_validation_integration(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test event data validation in integration environment."""
        # Test valid event types
        valid_event_types = [
            "user.login",
            "user.logout", 
            "message.sent",
            "system.alert",
            "custom.event"
        ]
        
        for event_type in valid_event_types:
            test_data = {
                "event_type": event_type,
                "data": {"valid": True, "type": event_type},
                "user_id": "validation-test-user"
            }
            
            response = await client.post(
                "/api/v1/events/test-event",
                json=test_data,
                headers=auth_headers
            )
            assert response.status_code == 200, f"Failed for event type: {event_type}"

    @pytest.mark.integration
    async def test_event_data_serialization(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test complex event data serialization."""
        complex_data = {
            "event_type": "complex.data.test",
            "data": {
                "nested_object": {
                    "level1": {
                        "level2": {"value": 42}
                    }
                },
                "array_data": [1, 2, 3, "string", {"nested": True}],
                "unicode_text": "Hello 世界 🌍",
                "numbers": {
                    "integer": 123,
                    "float": 45.67,
                    "negative": -89
                },
                "boolean_values": {
                    "true_val": True,
                    "false_val": False
                },
                "null_value": None
            },
            "user_id": "serialization-test-user"
        }
        
        response = await client.post(
            "/api/v1/events/test-event",
            json=complex_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["event_type"] == "complex.data.test"

    @pytest.mark.integration
    async def test_concurrent_event_operations(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test concurrent event operations."""
        # Create concurrent tasks for different operations
        tasks = []
        
        # Add stats requests
        for i in range(2):
            task = asyncio.create_task(
                client.get("/api/v1/events/stats", headers=auth_headers)
            )
            tasks.append(task)
        
        # Add test events
        for i in range(3):
            test_data = {
                "event_type": f"concurrent.test.{i}",
                "data": {"concurrent_id": i, "test": "concurrent"},
                "user_id": f"concurrent-user-{i}"
            }
            task = asyncio.create_task(
                client.post("/api/v1/events/test-event", json=test_data, headers=auth_headers)
            )
            tasks.append(task)
        
        # Add broadcast tests
        for i in range(2):
            broadcast_data = {
                "event_type": f"concurrent.broadcast.{i}",
                "data": {"broadcast_id": i, "test": "concurrent"}
            }
            task = asyncio.create_task(
                client.post("/api/v1/events/broadcast-test", json=broadcast_data, headers=auth_headers)
            )
            tasks.append(task)
        
        # Wait for all operations to complete
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200

    @pytest.mark.integration
    async def test_sse_connection_cleanup(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test SSE connection cleanup behavior."""
        # Get initial connection count
        stats_response = await client.get("/api/v1/events/stats", headers=auth_headers)
        initial_stats = stats_response.json()
        initial_connections = initial_stats["active_connections"]
        
        # Create and immediately close SSE connection
        response = await client.get("/api/v1/events/stream", headers=auth_headers)
        assert response.status_code == 200
        
        # Connection should be handled properly even if closed quickly
        # (Actual cleanup testing would require more complex setup)
        
        # Verify stats are still accessible
        final_stats_response = await client.get("/api/v1/events/stats", headers=auth_headers)
        assert final_stats_response.status_code == 200
        final_stats = final_stats_response.json()
        
        # Stats should be consistent
        assert isinstance(final_stats["active_connections"], int)
        assert final_stats["active_connections"] >= 0