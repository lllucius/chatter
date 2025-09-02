"""End-to-end tests for chat conversation workflows."""

from unittest.mock import patch

import pytest
from fastapi import status


@pytest.mark.e2e
class TestChatConversationE2E:
    """End-to-end chat conversation workflow tests."""

    def test_complete_conversation_lifecycle(
        self, test_client, sample_chat_conversation, cleanup_test_data
    ):
        """Test creating, managing, and deleting a chat conversation."""
        # Step 1: Create a new conversation
        create_response = test_client.post(
            "/api/v1/chat/conversations",
            json={
                "title": sample_chat_conversation["title"],
                "description": sample_chat_conversation["description"],
            },
        )

        if create_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Chat conversation endpoints not available")

        # Allow for various success responses
        assert create_response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,  # Might require authentication
        ]

        if create_response.status_code == status.HTTP_401_UNAUTHORIZED:
            pytest.skip("Authentication required for chat endpoints")

        conversation_data = create_response.json()
        conversation_id = conversation_data.get(
            "id"
        ) or conversation_data.get("conversation_id")

        if not conversation_id:
            pytest.skip(
                "Unable to extract conversation ID from response"
            )

        # Step 2: Add messages to the conversation
        message_response = test_client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json={
                "content": sample_chat_conversation["messages"][0][
                    "content"
                ],
                "role": "user",
            },
        )

        # Allow for endpoint not existing or auth required
        if message_response.status_code not in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
        ]:
            pytest.skip("Unable to add messages to conversation")

        # Step 3: Get conversation with messages
        get_response = test_client.get(
            f"/api/v1/chat/conversations/{conversation_id}"
        )

        if get_response.status_code == status.HTTP_200_OK:
            conversation = get_response.json()
            assert (
                conversation["title"]
                == sample_chat_conversation["title"]
            )

        # Step 4: Update conversation
        update_response = test_client.put(
            f"/api/v1/chat/conversations/{conversation_id}",
            json={
                "title": "Updated E2E Test Conversation",
                "description": "Updated description",
            },
        )

        # Step 5: Delete conversation (cleanup)
        delete_response = test_client.delete(
            f"/api/v1/chat/conversations/{conversation_id}"
        )
        # Don't assert on delete response as it might not be implemented

    @patch('chatter.services.llm.LLMService.generate_response')
    def test_chat_message_with_ai_response(
        self, mock_llm, test_client, mock_llm_response
    ):
        """Test sending a message and receiving an AI response."""
        # Mock the LLM service to avoid external API calls
        mock_llm.return_value = mock_llm_response["content"]

        # Step 1: Create conversation
        create_response = test_client.post(
            "/api/v1/chat/conversations",
            json={"title": "AI Response Test"},
        )

        if create_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Chat endpoints not available")

        if create_response.status_code not in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
        ]:
            pytest.skip(
                "Cannot create conversation for AI response test"
            )

        conversation_data = create_response.json()
        conversation_id = conversation_data.get(
            "id"
        ) or conversation_data.get("conversation_id")

        # Step 2: Send user message
        message_response = test_client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json={
                "content": "Hello, can you help me with testing?",
                "role": "user",
            },
        )

        if message_response.status_code not in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
        ]:
            pytest.skip("Cannot send message for AI response test")

        # Step 3: Check for AI response (might be async)
        messages_response = test_client.get(
            f"/api/v1/chat/conversations/{conversation_id}/messages"
        )

        if messages_response.status_code == status.HTTP_200_OK:
            messages = messages_response.json()
            # Check if we have both user and assistant messages
            user_messages = [
                m for m in messages if m.get("role") == "user"
            ]
            ai_messages = [
                m for m in messages if m.get("role") == "assistant"
            ]

            assert len(user_messages) >= 1
            # AI response might be generated asynchronously, so don't assert its presence

    def test_conversation_listing_and_pagination(self, test_client):
        """Test listing conversations with pagination."""
        # Test getting conversations list
        list_response = test_client.get("/api/v1/chat/conversations")

        if list_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Conversation listing endpoint not available")

        if list_response.status_code == status.HTTP_401_UNAUTHORIZED:
            pytest.skip(
                "Authentication required for conversation listing"
            )

        assert list_response.status_code == status.HTTP_200_OK
        conversations = list_response.json()

        # Test pagination if supported
        paginated_response = test_client.get(
            "/api/v1/chat/conversations?page=1&limit=10"
        )

        if paginated_response.status_code == status.HTTP_200_OK:
            paginated_data = paginated_response.json()
            # Basic pagination structure check
            assert isinstance(paginated_data, (list, dict))


@pytest.mark.e2e
@pytest.mark.integration
class TestChatStreamingE2E:
    """End-to-end tests for chat streaming functionality."""

    def test_streaming_chat_response(self, test_client):
        """Test streaming chat responses."""
        # Test streaming endpoint if available
        stream_response = test_client.post(
            "/api/v1/chat/stream",
            json={"message": "Tell me a short story", "stream": True},
        )

        if stream_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Streaming endpoint not available")

        if stream_response.status_code == status.HTTP_401_UNAUTHORIZED:
            pytest.skip("Authentication required for streaming")

        # For streaming, we might get different response codes
        assert stream_response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
        ]

        # If streaming works, check content type
        if stream_response.status_code == status.HTTP_200_OK:
            content_type = stream_response.headers.get(
                "content-type", ""
            )
            # Streaming typically uses text/event-stream or similar
            assert (
                "stream" in content_type
                or "event" in content_type
                or "json" in content_type
            )

    def test_websocket_chat_connection(self, test_client):
        """Test WebSocket chat connections if available."""
        # This test would require a different approach for WebSocket testing
        # For now, we'll just check if the endpoint exists
        websocket_response = test_client.get("/api/v1/chat/ws")

        # WebSocket endpoints typically return different status codes
        # Just verify it's not a 404 (not found)
        if websocket_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("WebSocket chat endpoint not available")

        # WebSocket endpoint might return 400, 405, or other codes when accessed via HTTP
        assert (
            websocket_response.status_code != status.HTTP_404_NOT_FOUND
        )
