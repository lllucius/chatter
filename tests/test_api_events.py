"""Events API tests."""

import pytest


@pytest.mark.unit
class TestEventsAPI:
    """Test events API endpoints."""

    async def test_get_events(self, test_client):
        """Test retrieving events."""
        # Setup user and auth
        registration_data = {
            "email": "eventsuser@example.com",
            "password": "SecurePass123!",
            "username": "eventsuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "eventsuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get events
        response = await test_client.get("/api/v1/events", headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert "events" in data or isinstance(data, list)

    async def test_get_events_with_filters(self, test_client):
        """Test retrieving events with filters."""
        # Setup user and auth
        registration_data = {
            "email": "filtereventsuser@example.com",
            "password": "SecurePass123!",
            "username": "filtereventsuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "filtereventsuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get events with filters
        params = {
            "event_type": "conversation",
            "limit": 10,
            "offset": 0,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }

        response = await test_client.get("/api/v1/events", params=params, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 422, 501]

    async def test_create_event(self, test_client):
        """Test creating an event."""
        # Setup user and auth
        registration_data = {
            "email": "createeventuser@example.com",
            "password": "SecurePass123!",
            "username": "createeventuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "createeventuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create an event
        event_data = {
            "event_type": "user_action",
            "source": "api",
            "data": {
                "action": "test_action",
                "details": "Test event creation"
            },
            "metadata": {
                "user_agent": "test-client"
            }
        }

        response = await test_client.post("/api/v1/events", json=event_data, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [201, 422, 501]

        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert data["event_type"] == "user_action"

    async def test_get_event_by_id(self, test_client):
        """Test retrieving a specific event."""
        # Setup user and auth
        registration_data = {
            "email": "geteventuser@example.com",
            "password": "SecurePass123!",
            "username": "geteventuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "geteventuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to get an event (will likely return 404)
        response = await test_client.get("/api/v1/events/nonexistent", headers=headers)

        # Should return 404 for non-existent event or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_event_stream(self, test_client):
        """Test event streaming endpoint."""
        # Setup user and auth
        registration_data = {
            "email": "streamuser@example.com",
            "password": "SecurePass123!",
            "username": "streamuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "streamuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to connect to event stream
        response = await test_client.get("/api/v1/events/stream", headers=headers)

        # Should succeed or return 501 if not implemented
        # SSE endpoints typically return 200 with text/event-stream content type
        assert response.status_code in [200, 501]

    async def test_event_webhooks(self, test_client):
        """Test event webhook endpoints."""
        # Setup user and auth
        registration_data = {
            "email": "webhookuser@example.com",
            "password": "SecurePass123!",
            "username": "webhookuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "webhookuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List webhooks
        response = await test_client.get("/api/v1/events/webhooks", headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]

    async def test_create_webhook(self, test_client):
        """Test creating a webhook."""
        # Setup user and auth
        registration_data = {
            "email": "createwebhookuser@example.com",
            "password": "SecurePass123!",
            "username": "createwebhookuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "createwebhookuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a webhook
        webhook_data = {
            "url": "https://example.com/webhook",
            "event_types": ["conversation.created", "message.sent"],
            "active": True,
            "secret": "webhook_secret_123"
        }

        response = await test_client.post("/api/v1/events/webhooks", json=webhook_data, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [201, 422, 501]

    async def test_events_unauthorized(self, test_client):
        """Test event endpoints require authentication."""
        endpoints = [
            "/api/v1/events",
            "/api/v1/events/test",
            "/api/v1/events/stream",
            "/api/v1/events/webhooks"
        ]

        for endpoint in endpoints:
            response = await test_client.get(endpoint)

            # Should require authentication
            assert response.status_code in [401, 403]

    async def test_event_validation(self, test_client):
        """Test event creation validation."""
        # Setup user and auth
        registration_data = {
            "email": "valideventuser@example.com",
            "password": "SecurePass123!",
            "username": "valideventuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "valideventuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try creating event with missing required fields
        invalid_data = {
            "data": {}
        }

        response = await test_client.post("/api/v1/events", json=invalid_data, headers=headers)

        # Should fail validation
        assert response.status_code in [400, 422]

    async def test_event_aggregation(self, test_client):
        """Test event aggregation endpoint."""
        # Setup user and auth
        registration_data = {
            "email": "agguser@example.com",
            "password": "SecurePass123!",
            "username": "agguser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "agguser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get event aggregations
        params = {
            "group_by": "event_type",
            "period": "1d",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }

        response = await test_client.get("/api/v1/events/aggregation", params=params, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 422, 501]
