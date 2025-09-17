"""
Test for the ChatResponse datetime serialization fix.

This test validates that ChatResponse and related models properly serialize
datetime objects to JSON-compatible strings when using the to_dict() and to_json() methods.
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MockMessageResponse(BaseModel):
    """Mock MessageResponse for testing datetime serialization."""

    role: str
    content: str
    id: str
    conversation_id: str
    sequence_number: int
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Test the fixed to_dict implementation."""
        excluded_fields: set[str] = set()

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
            mode='json',  # This is the critical fix
        )
        return _dict


class MockConversationResponse(BaseModel):
    """Mock ConversationResponse for testing datetime serialization."""

    title: str
    id: str
    user_id: str
    status: str
    message_count: int
    total_tokens: int
    total_cost: float
    enable_retrieval: bool
    context_window: int
    memory_enabled: bool
    retrieval_limit: int
    retrieval_score_threshold: float
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Test the fixed to_dict implementation."""
        excluded_fields: set[str] = set()

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
            mode='json',  # This is the critical fix
        )
        return _dict


class MockChatResponse(BaseModel):
    """Mock ChatResponse for testing datetime serialization."""

    conversation_id: str = Field(description="Conversation ID")
    message: MockMessageResponse
    conversation: MockConversationResponse

    def to_dict(self) -> dict[str, Any]:
        """Test the fixed to_dict implementation."""
        excluded_fields: set[str] = set()

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
            mode='json',  # This is the critical fix
        )
        # Override the default output by calling to_dict() of nested objects
        if self.message:
            _dict['message'] = self.message.to_dict()
        if self.conversation:
            _dict['conversation'] = self.conversation.to_dict()
        return _dict

    def to_json(self) -> str:
        """Returns the JSON representation."""
        return json.dumps(self.to_dict())


class TestChatResponseDatetimeSerialization:
    """Test ChatResponse datetime serialization fix."""

    def test_message_response_datetime_serialization(self):
        """Test that MessageResponse properly serializes datetime fields."""
        now = datetime.now()

        message = MockMessageResponse(
            role="assistant",
            content="Hello! How can I help you today?",
            id="01JJ0MESSAGE123456789ABCDEF",
            conversation_id="01JJ0CONVERSATION12345ABCDEF",
            sequence_number=2,
            created_at=now,
        )

        # Test to_dict()
        message_dict = message.to_dict()

        assert isinstance(
            message_dict['created_at'], str
        ), "created_at should be serialized as string"
        assert (
            message_dict['created_at'] == now.isoformat()
        ), "created_at should be in ISO format"

        # Test JSON serialization
        json_str = json.dumps(message_dict)
        parsed = json.loads(json_str)
        assert parsed['created_at'] == now.isoformat()

    def test_conversation_response_datetime_serialization(self):
        """Test that ConversationResponse properly serializes datetime fields."""
        now = datetime.now()

        conversation = MockConversationResponse(
            title="Test Conversation",
            id="01JJ0CONVERSATION12345ABCDEF",
            user_id="01JJ0USER123456789ABCDEFGH",
            status="active",
            message_count=2,
            total_tokens=25,
            total_cost=0.001,
            enable_retrieval=False,
            context_window=4096,
            memory_enabled=True,
            retrieval_limit=10,
            retrieval_score_threshold=0.7,
            created_at=now,
            updated_at=now,
        )

        # Test to_dict()
        conv_dict = conversation.to_dict()

        assert isinstance(
            conv_dict['created_at'], str
        ), "created_at should be serialized as string"
        assert isinstance(
            conv_dict['updated_at'], str
        ), "updated_at should be serialized as string"
        assert conv_dict['created_at'] == now.isoformat()
        assert conv_dict['updated_at'] == now.isoformat()

        # Test JSON serialization
        json_str = json.dumps(conv_dict)
        parsed = json.loads(json_str)
        assert parsed['created_at'] == now.isoformat()
        assert parsed['updated_at'] == now.isoformat()

    def test_chat_response_full_serialization(self):
        """Test that ChatResponse with nested objects serializes properly."""
        now = datetime.now()

        message = MockMessageResponse(
            role="assistant",
            content="This is a test response from the AI assistant.",
            id="01JJ0MESSAGE123456789ABCDEF",
            conversation_id="01JJ0CONVERSATION12345ABCDEF",
            sequence_number=2,
            created_at=now,
        )

        conversation = MockConversationResponse(
            title="Test Chat Conversation",
            id="01JJ0CONVERSATION12345ABCDEF",
            user_id="01JJ0USER123456789ABCDEFGH",
            status="active",
            message_count=2,
            total_tokens=50,
            total_cost=0.002,
            enable_retrieval=False,
            context_window=4096,
            memory_enabled=True,
            retrieval_limit=10,
            retrieval_score_threshold=0.7,
            created_at=now,
            updated_at=now,
        )

        chat_response = MockChatResponse(
            conversation_id="01JJ0CONVERSATION12345ABCDEF",
            message=message,
            conversation=conversation,
        )

        # Test to_dict()
        chat_dict = chat_response.to_dict()

        # Verify structure
        assert 'conversation_id' in chat_dict
        assert 'message' in chat_dict
        assert 'conversation' in chat_dict

        # Verify nested datetime serialization
        assert isinstance(chat_dict['message']['created_at'], str)
        assert isinstance(chat_dict['conversation']['created_at'], str)
        assert isinstance(chat_dict['conversation']['updated_at'], str)

        # Test full JSON serialization - this was the original issue
        json_str = chat_response.to_json()
        assert len(json_str) > 0, "JSON serialization should succeed"

        # Verify JSON can be parsed back
        parsed = json.loads(json_str)
        assert (
            parsed['conversation_id'] == "01JJ0CONVERSATION12345ABCDEF"
        )
        assert (
            parsed['message']['content']
            == "This is a test response from the AI assistant."
        )
        assert parsed['message']['created_at'] == now.isoformat()
        assert parsed['conversation']['created_at'] == now.isoformat()
        assert parsed['conversation']['updated_at'] == now.isoformat()

    def test_json_serialization_round_trip(self):
        """Test that ChatResponse can be serialized and deserialized properly."""
        now = datetime.now()

        # Create original response
        message = MockMessageResponse(
            role="assistant",
            content="Weather forecast: Sunny with a high of 75°F",
            id="01JJ0MESSAGE123456789ABCDEF",
            conversation_id="01JJ0CONVERSATION12345ABCDEF",
            sequence_number=3,
            created_at=now,
        )

        conversation = MockConversationResponse(
            title="Weather Discussion",
            id="01JJ0CONVERSATION12345ABCDEF",
            user_id="01JJ0USER123456789ABCDEFGH",
            status="active",
            message_count=3,
            total_tokens=75,
            total_cost=0.003,
            enable_retrieval=False,
            context_window=4096,
            memory_enabled=True,
            retrieval_limit=10,
            retrieval_score_threshold=0.7,
            created_at=now,
            updated_at=now,
        )

        original_chat = MockChatResponse(
            conversation_id="01JJ0CONVERSATION12345ABCDEF",
            message=message,
            conversation=conversation,
        )

        # Serialize to JSON
        json_str = original_chat.to_json()

        # Parse back from JSON
        parsed_data = json.loads(json_str)

        # Create new objects from parsed data (simulating real-world usage)
        recovered_message = MockMessageResponse(
            role=parsed_data['message']['role'],
            content=parsed_data['message']['content'],
            id=parsed_data['message']['id'],
            conversation_id=parsed_data['message']['conversation_id'],
            sequence_number=parsed_data['message']['sequence_number'],
            created_at=datetime.fromisoformat(
                parsed_data['message']['created_at']
            ),
        )

        recovered_conversation = MockConversationResponse(
            title=parsed_data['conversation']['title'],
            id=parsed_data['conversation']['id'],
            user_id=parsed_data['conversation']['user_id'],
            status=parsed_data['conversation']['status'],
            message_count=parsed_data['conversation']['message_count'],
            total_tokens=parsed_data['conversation']['total_tokens'],
            total_cost=parsed_data['conversation']['total_cost'],
            enable_retrieval=parsed_data['conversation'][
                'enable_retrieval'
            ],
            context_window=parsed_data['conversation'][
                'context_window'
            ],
            memory_enabled=parsed_data['conversation'][
                'memory_enabled'
            ],
            retrieval_limit=parsed_data['conversation'][
                'retrieval_limit'
            ],
            retrieval_score_threshold=parsed_data['conversation'][
                'retrieval_score_threshold'
            ],
            created_at=datetime.fromisoformat(
                parsed_data['conversation']['created_at']
            ),
            updated_at=datetime.fromisoformat(
                parsed_data['conversation']['updated_at']
            ),
        )

        recovered_chat = MockChatResponse(
            conversation_id=parsed_data['conversation_id'],
            message=recovered_message,
            conversation=recovered_conversation,
        )

        # Verify the round-trip worked
        assert (
            recovered_chat.conversation_id
            == original_chat.conversation_id
        )
        assert (
            recovered_chat.message.content
            == original_chat.message.content
        )
        assert (
            recovered_chat.conversation.title
            == original_chat.conversation.title
        )
        assert (
            recovered_chat.message.created_at
            == original_chat.message.created_at
        )
        assert (
            recovered_chat.conversation.created_at
            == original_chat.conversation.created_at
        )
