"""Test to verify chat workflow response structure."""

import pytest
from httpx import AsyncClient

from chatter.schemas.workflows import ChatWorkflowRequest


@pytest.mark.asyncio
async def test_chat_workflow_returns_proper_structure(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Test that chat workflow returns proper response structure with message content."""
    # Simple chat workflow request
    request = ChatWorkflowRequest(
        message="What is 2+2?",
        enable_retrieval=False,
        enable_tools=False,
        enable_memory=True,
    )

    # Send request to chat workflow endpoint
    response = await client.post(
        "/api/v1/workflows/execute/chat",
        json=request.model_dump(),
        headers=auth_headers,
    )

    # Verify response status
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"

    # Parse response
    data = response.json()

    # Verify response structure
    assert (
        "conversation_id" in data
    ), "Response should have conversation_id"
    assert "message" in data, "Response should have message"
    assert "conversation" in data, "Response should have conversation"

    # Verify message structure
    message = data["message"]
    assert "role" in message, "Message should have role"
    assert "content" in message, "Message should have content"
    assert "id" in message, "Message should have id"
    assert (
        "conversation_id" in message
    ), "Message should have conversation_id"

    # Verify message content
    assert (
        message["role"] == "assistant"
    ), f"Expected role 'assistant', got '{message['role']}'"
    assert isinstance(
        message["content"], str
    ), f"Expected content to be string, got {type(message['content'])}"
    assert (
        len(message["content"]) > 0
    ), "Message content should not be empty"

    # Verify conversation ID matches
    assert (
        data["conversation_id"] == message["conversation_id"]
    ), "Conversation IDs should match"

    print("✓ Chat workflow response structure is correct")
    print(f"✓ Message content: {message['content'][:100]}...")


@pytest.mark.asyncio
async def test_chat_workflow_multiple_messages(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Test multiple messages in same conversation."""
    # First message
    request1 = ChatWorkflowRequest(
        message="Hello",
        enable_retrieval=False,
        enable_tools=False,
        enable_memory=True,
    )

    response1 = await client.post(
        "/api/v1/workflows/execute/chat",
        json=request1.model_dump(),
        headers=auth_headers,
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1["conversation_id"]

    # Verify first message
    assert data1["message"]["content"]
    assert len(data1["message"]["content"]) > 0

    # Second message in same conversation
    request2 = ChatWorkflowRequest(
        message="What did I just say?",
        conversation_id=conversation_id,
        enable_retrieval=False,
        enable_tools=False,
        enable_memory=True,
    )

    response2 = await client.post(
        "/api/v1/workflows/execute/chat",
        json=request2.model_dump(),
        headers=auth_headers,
    )

    assert response2.status_code == 200
    data2 = response2.json()

    # Verify second message
    assert data2["conversation_id"] == conversation_id
    assert data2["message"]["content"]
    assert len(data2["message"]["content"]) > 0

    print("✓ Multiple messages in conversation work correctly")
    print(f"✓ Conversation ID: {conversation_id}")
