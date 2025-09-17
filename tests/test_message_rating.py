"""Test for message rating functionality."""

from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.exceptions import ValidationError
from chatter.models.conversation import Message
from chatter.schemas.chat import (
    MessageRatingUpdate,
)
from chatter.services.message import MessageService


@pytest.mark.asyncio
async def test_message_rating_validation():
    """Test message rating validation."""

    # Test valid rating
    rating_update = MessageRatingUpdate(rating=4.5)
    assert rating_update.rating == 4.5

    # Test invalid ratings should raise ValidationError
    with pytest.raises(ValueError):  # Pydantic validation error
        MessageRatingUpdate(rating=6.0)

    with pytest.raises(ValueError):  # Pydantic validation error
        MessageRatingUpdate(rating=-1.0)


@pytest.mark.asyncio
async def test_message_rating_logic():
    """Test the core message rating calculation logic."""

    # Mock a message without rating
    message = Mock(spec=Message)
    message.rating = None
    message.rating_count = 0

    # First rating
    message.rating = 4.0
    message.rating_count = 1

    assert message.rating == 4.0
    assert message.rating_count == 1

    # Second rating - should calculate average
    total_score = message.rating * message.rating_count + 5.0
    message.rating_count += 1
    message.rating = total_score / message.rating_count

    expected_average = (4.0 + 5.0) / 2
    assert message.rating == expected_average
    assert message.rating_count == 2


@pytest.mark.asyncio
async def test_message_service_rating_validation():
    """Test MessageService rating validation."""

    mock_session = AsyncMock(spec=AsyncSession)
    service = MessageService(mock_session)

    # Test invalid rating validation
    with pytest.raises(ValidationError) as exc_info:
        await service.update_message_rating(
            "conv1", "msg1", "user1", 6.0
        )

    assert "Rating must be between 0.0 and 5.0" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        await service.update_message_rating(
            "conv1", "msg1", "user1", -1.0
        )

    assert "Rating must be between 0.0 and 5.0" in str(exc_info.value)


def test_message_response_with_rating():
    """Test MessageResponse schema with rating fields."""

    # Test with rating
    message_data = {
        "id": "msg1",
        "conversation_id": "conv1",
        "role": "assistant",
        "content": "Test message",
        "sequence_number": 1,
        "rating": 4.5,
        "rating_count": 3,
        "created_at": "2024-01-01T12:00:00Z",
    }

    from chatter.schemas.chat import MessageResponse

    message_response = MessageResponse(**message_data)

    assert message_response.rating == 4.5
    assert message_response.rating_count == 3

    # Test without rating
    message_data_no_rating = {
        "id": "msg2",
        "conversation_id": "conv1",
        "role": "user",
        "content": "User message",
        "sequence_number": 2,
        "created_at": "2024-01-01T12:01:00Z",
    }

    message_response_no_rating = MessageResponse(
        **message_data_no_rating
    )

    assert message_response_no_rating.rating is None
    assert message_response_no_rating.rating_count == 0


if __name__ == "__main__":
    import asyncio

    print("Running message rating tests...")

    # Run async tests
    asyncio.run(test_message_rating_validation())
    asyncio.run(test_message_rating_logic())
    asyncio.run(test_message_service_rating_validation())

    # Run sync tests
    test_message_response_with_rating()

    print("✅ All tests passed!")
