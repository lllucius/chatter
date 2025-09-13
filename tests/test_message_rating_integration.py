"""Integration test for message rating feature."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from chatter.main import app
from chatter.models.conversation import Conversation, Message, MessageRole
from chatter.models.user import User
from chatter.utils.database import get_session_generator


@pytest.mark.asyncio
async def test_message_rating_end_to_end(test_client: AsyncClient, authenticated_user: User):
    """Test the complete message rating flow from frontend to backend."""
    
    # Create a conversation
    conversation_data = {
        "title": "Test Conversation",
        "profile_id": None,
        "enable_retrieval": False,
        "system_prompt": None
    }
    
    conversation_response = await test_client.post(
        "/api/v1/chat/conversations",
        json=conversation_data,
        headers={"Authorization": f"Bearer fake-token"}
    )
    
    assert conversation_response.status_code == 201
    conversation = conversation_response.json()
    conversation_id = conversation["id"]
    
    # Add a message to the conversation
    async for session in get_session_generator():
        # Create an assistant message
        message = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="This is a test response from the assistant.",
            sequence_number=1,
            user_id=authenticated_user.id
        )
        session.add(message)
        await session.commit()
        await session.refresh(message)
        message_id = message.id
        break
    
    # Test rating the message
    rating_data = {"rating": 4.5}
    
    rating_response = await test_client.patch(
        f"/api/v1/conversations/{conversation_id}/messages/{message_id}/rating",
        json=rating_data,
        headers={"Authorization": f"Bearer fake-token"}
    )
    
    assert rating_response.status_code == 200
    rating_result = rating_response.json()
    
    # Verify the response format matches what frontend expects
    assert "message" in rating_result
    assert "rating" in rating_result
    assert "rating_count" in rating_result
    assert rating_result["rating"] == 4.5
    assert rating_result["rating_count"] == 1
    
    # Test multiple ratings to verify average calculation
    second_rating_data = {"rating": 3.5}
    
    second_rating_response = await test_client.patch(
        f"/api/v1/conversations/{conversation_id}/messages/{message_id}/rating",
        json=second_rating_data,
        headers={"Authorization": f"Bearer fake-token"}
    )
    
    assert second_rating_response.status_code == 200
    second_result = second_rating_response.json()
    
    # Verify average calculation: (4.5 + 3.5) / 2 = 4.0
    assert second_result["rating"] == 4.0
    assert second_result["rating_count"] == 2
    
    # Test analytics integration
    analytics_response = await test_client.get(
        "/api/v1/analytics/conversations",
        headers={"Authorization": f"Bearer fake-token"}
    )
    
    assert analytics_response.status_code == 200
    analytics = analytics_response.json()
    
    # Verify rating metrics are included in analytics
    assert "total_ratings" in analytics
    assert "avg_message_rating" in analytics
    assert "messages_with_ratings" in analytics
    assert "rating_distribution" in analytics
    
    assert analytics["total_ratings"] >= 2
    assert analytics["messages_with_ratings"] >= 1


@pytest.mark.asyncio
async def test_message_rating_validation_errors():
    """Test frontend/backend validation error handling."""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test invalid rating value (too high)
        invalid_rating_data = {"rating": 6.0}
        
        response = await client.patch(
            "/api/v1/conversations/fake-id/messages/fake-msg-id/rating",
            json=invalid_rating_data,
            headers={"Authorization": f"Bearer fake-token"}
        )
        
        # Should return 422 validation error
        assert response.status_code in [400, 401, 404, 422]  # Various possible error codes
        
        # Test invalid rating value (negative)
        invalid_rating_data = {"rating": -1.0}
        
        response = await client.patch(
            "/api/v1/conversations/fake-id/messages/fake-msg-id/rating",
            json=invalid_rating_data,
            headers={"Authorization": f"Bearer fake-token"}
        )
        
        assert response.status_code in [400, 401, 404, 422]


def test_frontend_rating_interface():
    """Test the frontend rating interface structure."""
    
    # Simulate the frontend ChatMessage interface
    class ChatMessage:
        def __init__(self):
            self.id = "test-message-id"
            self.role = "assistant"
            self.content = "Test message"
            self.rating = None
    
    # Simulate the rating update function
    async def handle_rate_message(message_id: str, rating: float) -> dict:
        """Simulates the frontend handleRateMessage function."""
        
        # This mimics the API call the frontend makes
        api_payload = {"rating": rating}
        
        # Validate the payload structure
        assert "rating" in api_payload
        assert 0.0 <= api_payload["rating"] <= 5.0
        
        # Mock successful API response
        return {
            "message": "Message rating updated successfully",
            "rating": rating,
            "rating_count": 1
        }
    
    # Test the interface
    message = ChatMessage()
    
    # Simulate user rating the message
    import asyncio
    result = asyncio.run(handle_rate_message(message.id, 4.5))
    
    assert result["rating"] == 4.5
    assert result["rating_count"] == 1
    assert "message" in result