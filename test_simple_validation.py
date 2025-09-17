#!/usr/bin/env python3
"""Simple test to verify the validation logic works."""

from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from enum import Enum


class MessageRole(str, Enum):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MessageResponse(BaseModel):
    """Schema for message response."""
    role: MessageRole
    content: str = Field(..., min_length=1, description="Message content")
    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    sequence_number: int = Field(..., description="Message sequence number")
    created_at: datetime = Field(..., description="Creation timestamp")


def test_validation():
    """Test the validation logic."""
    print('Testing message validation fixes...')

    # Test empty content (should fail)
    try:
        MessageResponse(
            id='test', conversation_id='test', role=MessageRole.ASSISTANT,
            content='', sequence_number=1, created_at=datetime.now()
        )
        print('❌ Empty content validation FAILED - should have been rejected')
    except ValidationError as e:
        print('✅ Empty content validation PASSED - correctly rejected empty content')

    # Test placeholder content (should pass)
    try:
        msg = MessageResponse(
            id='test', conversation_id='test', role=MessageRole.ASSISTANT, 
            content='...', sequence_number=1, created_at=datetime.now()
        )
        print('✅ Placeholder content validation PASSED - content accepted')
    except ValidationError as e:
        print(f'❌ Placeholder content validation FAILED: {e}')

    # Test normal content (should pass)
    try:
        msg = MessageResponse(
            id='test', conversation_id='test', role=MessageRole.ASSISTANT, 
            content='Hello world!', sequence_number=1, created_at=datetime.now()
        )
        print('✅ Normal content validation PASSED - content accepted')
    except ValidationError as e:
        print(f'❌ Normal content validation FAILED: {e}')

    print('✅ All validation tests completed!')


if __name__ == "__main__":
    test_validation()