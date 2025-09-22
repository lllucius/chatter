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
            json={"message": "Hello", "workflow": "plain"},
        )
        # We expect this to fail with auth or service errors, but not 404
        assert response.status_code != 404

    async def test_streaming_chat_endpoint_exists(self, client):
        """Test that the streaming chat endpoint exists."""
        # This just tests the endpoint is registered, not full functionality
        response = await client.post(
            "/api/v1/chat/streaming",
            json={"message": "Hello", "workflow": "plain"},
            headers={"Accept": "text/event-stream"},
        )
        # We expect this to fail with auth or service errors, but not 404
        assert response.status_code != 404

    @pytest.mark.parametrize(
        "enable_retrieval,enable_tools,enable_memory",
        [
            (False, False, True),  # Plain
            (True, False, True),   # RAG
            (False, True, True),   # Tools
            (True, True, True),    # Full
        ],
    )
    def test_chat_request_capabilities(self, enable_retrieval, enable_tools, enable_memory):
        """Test that all capability combinations are supported."""
        request_data = {
            "message": "Hello, world!",
            "enable_retrieval": enable_retrieval,
            "enable_tools": enable_tools,
            "enable_memory": enable_memory,
        }

        chat_request = ChatRequest(**request_data)
        assert chat_request.enable_retrieval == enable_retrieval
        assert chat_request.enable_tools == enable_tools
        assert chat_request.enable_memory == enable_memory
