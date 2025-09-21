"""
Tests for the split chat endpoints.

Tests the new separate /chat (non-streaming) and /streaming endpoints.
"""

import pytest

from chatter.schemas.chat import ChatRequest


class TestSplitChatEndpoints:
    """Test the separated chat and streaming endpoints."""

    async def test_non_streaming_chat_endpoint_exists(self, client):
        """Test that the non-streaming chat endpoint exists."""
        # This just tests the endpoint is registered, not full functionality
        response = await client.post(
            "/api/v1/chat/chat",
            json={"message": "Hello", "workflow": "simple_chat"},
        )
        # We expect this to fail with auth or service errors, but not 404
        assert response.status_code != 404

    async def test_streaming_chat_endpoint_exists(self, client):
        """Test that the streaming chat endpoint exists."""
        # This just tests the endpoint is registered, not full functionality
        response = await client.post(
            "/api/v1/chat/streaming",
            json={"message": "Hello", "workflow": "simple_chat"},
            headers={"Accept": "text/event-stream"},
        )
        # We expect this to fail with auth or service errors, but not 404
        assert response.status_code != 404

    @pytest.mark.parametrize(
        "workflow", ["simple_chat", "rag_chat", "function_chat", "advanced_chat"]
    )
    def test_chat_request_workflow_types(self, workflow):
        """Test that all workflow types are supported."""
        request_data = {
            "message": "Hello, world!",
            "workflow": workflow,
        }

        chat_request = ChatRequest(**request_data)
        assert chat_request.workflow == workflow
