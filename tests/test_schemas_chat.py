"""Tests for chat schemas."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from chatter.schemas.chat import (
    MessageBase,
    MessageCreate,
    MessageResponse,
    ConversationBase,
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    ConversationWithMessages,
    ChatRequest,
    ChatResponse,
    ConversationSearchRequest,
    ConversationSearchResponse,
)
from chatter.models.conversation import MessageRole, ConversationStatus


@pytest.mark.unit
class TestMessageSchemas:
    """Test message-related schemas."""

    def test_message_base_valid(self):
        """Test valid MessageBase creation."""
        # Arrange & Act
        message = MessageBase(
            role=MessageRole.USER,
            content="Hello, world!"
        )

        # Assert
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"

    def test_message_create_valid(self):
        """Test valid MessageCreate."""
        # Arrange & Act
        message = MessageCreate(
            role=MessageRole.ASSISTANT,
            content="How can I help you today?"
        )

        # Assert
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "How can I help you today?"

    def test_message_response_complete(self):
        """Test MessageResponse with all fields."""
        # Arrange & Act
        message = MessageResponse(
            id="msg-123",
            conversation_id="conv-456",
            role=MessageRole.ASSISTANT,
            content="Complete response message",
            sequence_number=1,
            prompt_tokens=50,
            completion_tokens=25,
            total_tokens=75,
            model_used="gpt-4",
            provider_used="openai",
            response_time_ms=1500,
            cost=0.0045,
            finish_reason="stop",
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 0, 5)
        )

        # Assert
        assert message.id == "msg-123"
        assert message.conversation_id == "conv-456"
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "Complete response message"
        assert message.sequence_number == 1
        assert message.prompt_tokens == 50
        assert message.completion_tokens == 25
        assert message.total_tokens == 75
        assert message.model_used == "gpt-4"
        assert message.provider_used == "openai"
        assert message.response_time_ms == 1500
        assert message.cost == 0.0045
        assert message.finish_reason == "stop"

    def test_message_response_minimal(self):
        """Test MessageResponse with minimal fields."""
        # Arrange & Act
        message = MessageResponse(
            id="msg-minimal",
            conversation_id="conv-minimal",
            role=MessageRole.USER,
            content="Minimal message",
            sequence_number=0,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 0, 0)
        )

        # Assert
        assert message.id == "msg-minimal"
        assert message.conversation_id == "conv-minimal"
        assert message.role == MessageRole.USER
        assert message.content == "Minimal message"
        assert message.sequence_number == 0
        assert message.prompt_tokens is None
        assert message.completion_tokens is None
        assert message.total_tokens is None

    def test_message_invalid_role(self):
        """Test message with invalid role."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            MessageBase(
                role="invalid_role",
                content="Test content"
            )

    def test_message_empty_content(self):
        """Test message with empty content."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            MessageBase(
                role=MessageRole.USER,
                content=""
            )


@pytest.mark.unit
class TestConversationSchemas:
    """Test conversation-related schemas."""

    def test_conversation_base_valid(self):
        """Test valid ConversationBase."""
        # Arrange & Act
        conversation = ConversationBase(
            title="Test Conversation",
            description="A test conversation"
        )

        # Assert
        assert conversation.title == "Test Conversation"
        assert conversation.description == "A test conversation"

    def test_conversation_create_complete(self):
        """Test ConversationCreate with all fields."""
        # Arrange & Act
        conversation = ConversationCreate(
            title="New Conversation",
            description="Creating a new conversation",
            profile_id="profile-123",
            system_prompt="You are a helpful assistant",
            enable_retrieval=True
        )

        # Assert
        assert conversation.title == "New Conversation"
        assert conversation.description == "Creating a new conversation"
        assert conversation.profile_id == "profile-123"
        assert conversation.system_prompt == "You are a helpful assistant"
        assert conversation.enable_retrieval is True

    def test_conversation_response_complete(self):
        """Test ConversationResponse with all fields."""
        # Arrange & Act
        conversation = ConversationResponse(
            id="conv-123",
            user_id="user-456",
            title="Response Conversation",
            description="A conversation response",
            status=ConversationStatus.ACTIVE,
            llm_provider="openai",
            llm_model="gpt-4",
            temperature=0.8,
            max_tokens=1024,
            enable_retrieval=True,
            message_count=5,
            total_tokens=1500,
            total_cost=0.025,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 13, 0, 0)
        )

        # Assert
        assert conversation.id == "conv-123"
        assert conversation.user_id == "user-456"
        assert conversation.title == "Response Conversation"
        assert conversation.status == ConversationStatus.ACTIVE
        assert conversation.enable_retrieval is True
        assert conversation.message_count == 5
        assert conversation.total_tokens == 1500
        assert conversation.total_cost == 0.025

    def test_conversation_update_partial(self):
        """Test ConversationUpdate with partial fields."""
        # Arrange & Act
        update = ConversationUpdate(
            title="Updated Title",
            status=ConversationStatus.ARCHIVED
        )

        # Assert
        assert update.title == "Updated Title"
        assert update.status == ConversationStatus.ARCHIVED
        assert update.description is None

    def test_conversation_search_request(self):
        """Test ConversationSearchRequest."""
        # Arrange & Act
        request = ConversationSearchRequest(
            limit=20,
            offset=10,
            search="test query"
        )

        # Assert
        assert request.limit == 20
        assert request.offset == 10
        assert request.search == "test query"

    def test_conversation_search_response(self):
        """Test ConversationSearchResponse."""
        # Arrange
        conversations = [
            ConversationResponse(
                id=f"conv-{i}",
                user_id="user-123",
                title=f"Conversation {i}",
                status=ConversationStatus.ACTIVE,
                enable_retrieval=False,
                message_count=0,
                total_tokens=0,
                total_cost=0.0,
                created_at=datetime(2023, 1, 1, 12, 0, 0),
                updated_at=datetime(2023, 1, 1, 12, 0, 0)
            ) for i in range(3)
        ]

        # Act
        response = ConversationSearchResponse(
            conversations=conversations,
            total=3,
            has_more=False
        )

        # Assert
        assert len(response.conversations) == 3
        assert response.total == 3
        assert response.has_more is False


@pytest.mark.unit
class TestChatSchemas:
    """Test chat interaction schemas."""

    def test_chat_request_basic(self):
        """Test basic ChatRequest."""
        # Arrange & Act
        request = ChatRequest(
            message="Hello, how are you?",
            conversation_id="conv-123"
        )

        # Assert
        assert request.message == "Hello, how are you?"
        assert request.conversation_id == "conv-123"
        assert request.stream is False
        assert request.context_limit is None

    def test_chat_request_with_options(self):
        """Test ChatRequest with options."""
        # Arrange & Act
        request = ChatRequest(
            message="Explain quantum physics",
            conversation_id="conv-456",
            stream=True,
            temperature=0.5,
            max_tokens=1500,
            context_limit=10,
            include_sources=True
        )

        # Assert
        assert request.message == "Explain quantum physics"
        assert request.conversation_id == "conv-456"
        assert request.stream is True
        assert request.temperature == 0.5
        assert request.max_tokens == 1500
        assert request.context_limit == 10
        assert request.include_sources is True

    def test_chat_response_complete(self):
        """Test complete ChatResponse."""
        # Arrange & Act
        response = ChatResponse(
            message_id="msg-789",
            conversation_id="conv-123",
            content="Here's my response to your question...",
            role=MessageRole.ASSISTANT,
            model_used="gpt-4",
            provider_used="openai",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost=0.0075,
            response_time_ms=2000,
            finish_reason="stop",
            sources=["doc-1", "doc-2"],
            metadata={"confidence": 0.95}
        )

        # Assert
        assert response.message_id == "msg-789"
        assert response.conversation_id == "conv-123"
        assert response.content == "Here's my response to your question..."
        assert response.role == MessageRole.ASSISTANT
        assert response.model_used == "gpt-4"
        assert response.provider_used == "openai"
        assert response.prompt_tokens == 100
        assert response.completion_tokens == 50
        assert response.total_tokens == 150
        assert response.cost == 0.0075
        assert response.response_time_ms == 2000
        assert response.finish_reason == "stop"
        assert response.sources == ["doc-1", "doc-2"]
        assert response.metadata == {"confidence": 0.95}


@pytest.mark.unit
class TestChatSchemaValidation:
    """Test chat schema validation."""

    def test_temperature_validation(self):
        """Test temperature range validation."""
        # Valid temperatures
        valid_temps = [0.0, 0.5, 1.0, 2.0]
        for temp in valid_temps:
            request = ChatRequest(
                message="Test",
                conversation_id="conv-123",
                temperature=temp
            )
            assert request.temperature == temp

        # Invalid temperatures should be handled by the application layer
        # Pydantic itself doesn't enforce the 0-2 range unless we add validators

    def test_max_tokens_validation(self):
        """Test max tokens validation."""
        # Valid max_tokens
        request = ChatRequest(
            message="Test",
            conversation_id="conv-123",
            max_tokens=1000
        )
        assert request.max_tokens == 1000

        # Zero or negative should be handled by application logic
        with pytest.raises(ValidationError):
            ChatRequest(
                message="Test",
                conversation_id="conv-123",
                max_tokens=-100
            )

    def test_message_content_validation(self):
        """Test message content validation."""
        # Empty message should fail
        with pytest.raises(ValidationError):
            ChatRequest(
                message="",
                conversation_id="conv-123"
            )

        # Very long message should be handled by application logic
        long_message = "x" * 10000
        request = ChatRequest(
            message=long_message,
            conversation_id="conv-123"
        )
        assert len(request.message) == 10000

    def test_schema_serialization(self):
        """Test schema serialization."""
        # Arrange
        request = ChatRequest(
            message="Test serialization",
            conversation_id="conv-serial",
            stream=True,
            temperature=0.7
        )

        # Act
        data = request.model_dump()

        # Assert
        assert data["message"] == "Test serialization"
        assert data["conversation_id"] == "conv-serial"
        assert data["stream"] is True
        assert data["temperature"] == 0.7

    def test_schema_json_serialization(self):
        """Test JSON serialization."""
        # Arrange
        response = ChatResponse(
            message_id="msg-json",
            conversation_id="conv-json",
            content="JSON test",
            role=MessageRole.ASSISTANT
        )

        # Act
        json_str = response.model_dump_json()

        # Assert
        assert '"message_id":"msg-json"' in json_str.replace(" ", "")
        assert '"content":"JSON test"' in json_str.replace(" ", "")
        assert '"role":"assistant"' in json_str.replace(" ", "")