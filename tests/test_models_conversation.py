"""Tests for conversation and message models."""

from datetime import datetime

import pytest

from chatter.models.conversation import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
)
from chatter.models.user import User


@pytest.mark.unit
class TestConversationModel:
    """Test Conversation model functionality."""

    def test_conversation_creation(self, test_user: User):
        """Test basic conversation creation."""
        # Arrange & Act
        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation",
            description="A test conversation",
        )

        # Assert
        assert conversation.user_id == test_user.id
        assert conversation.title == "Test Conversation"
        assert conversation.description == "A test conversation"
        assert conversation.status == ConversationStatus.ACTIVE
        assert conversation.message_count == 0
        assert conversation.total_tokens == 0
        assert conversation.total_cost == 0.0
        assert conversation.context_window == 4096
        assert conversation.memory_enabled is True
        assert conversation.enable_retrieval is False
        assert conversation.retrieval_limit == 5
        assert conversation.retrieval_score_threshold == 0.7

    def test_conversation_with_configuration(self, test_user: User):
        """Test conversation with custom configuration."""
        # Arrange & Act
        conversation = Conversation(
            user_id=test_user.id,
            title="Configured Conversation",
            llm_provider="openai",
            llm_model="gpt-4",
            temperature=0.8,
            max_tokens=2048,
            system_prompt="You are a helpful assistant",
            context_window=8192,
            memory_strategy="summary",
            enable_retrieval=True,
            retrieval_limit=10,
            retrieval_score_threshold=0.8,
        )

        # Assert
        assert conversation.llm_provider == "openai"
        assert conversation.llm_model == "gpt-4"
        assert conversation.temperature == 0.8
        assert conversation.max_tokens == 2048
        assert (
            conversation.system_prompt == "You are a helpful assistant"
        )
        assert conversation.context_window == 8192
        assert conversation.memory_strategy == "summary"
        assert conversation.enable_retrieval is True
        assert conversation.retrieval_limit == 10
        assert conversation.retrieval_score_threshold == 0.8

    def test_conversation_with_metadata(self, test_user: User):
        """Test conversation with tags and metadata."""
        # Arrange & Act
        conversation = Conversation(
            user_id=test_user.id,
            title="Tagged Conversation",
            tags=["python", "coding", "help"],
            extra_metadata={
                "source": "api",
                "priority": "high",
                "custom_field": "value",
            },
        )

        # Assert
        assert conversation.tags == ["python", "coding", "help"]
        assert conversation.extra_metadata["source"] == "api"
        assert conversation.extra_metadata["priority"] == "high"
        assert conversation.extra_metadata["custom_field"] == "value"

    def test_conversation_to_dict(self, test_user: User):
        """Test conversation to dictionary conversion."""
        # Arrange
        conversation = Conversation(
            user_id=test_user.id,
            title="Dict Test",
            description="Test description",
            llm_provider="openai",
            temperature=0.7,
            tags=["test"],
            extra_metadata={"key": "value"},
        )

        # Mock timestamps for consistent testing
        conversation.created_at = datetime(2023, 1, 1, 12, 0, 0)
        conversation.updated_at = datetime(2023, 1, 1, 12, 30, 0)

        # Act
        result = conversation.to_dict()

        # Assert
        assert result["id"] == conversation.id
        assert result["user_id"] == test_user.id
        assert result["title"] == "Dict Test"
        assert result["description"] == "Test description"
        assert result["status"] == "active"
        assert result["llm_provider"] == "openai"
        assert result["temperature"] == 0.7
        assert result["tags"] == ["test"]
        assert result["extra_metadata"] == {"key": "value"}
        assert "2023-01-01T12:00:00" in result["created_at"]
        assert "2023-01-01T12:30:00" in result["updated_at"]

    def test_conversation_repr(self, test_user: User):
        """Test conversation string representation."""
        # Arrange
        conversation = Conversation(
            user_id=test_user.id,
            title="Repr Test",
        )

        # Act
        repr_str = repr(conversation)

        # Assert
        assert "Conversation" in repr_str
        assert conversation.id in repr_str
        assert "Repr Test" in repr_str
        assert test_user.id in repr_str


@pytest.mark.unit
class TestMessageModel:
    """Test Message model functionality."""

    def test_message_creation(self, test_conversation: Conversation):
        """Test basic message creation."""
        # Arrange & Act
        message = Message(
            conversation_id=test_conversation.id,
            role=MessageRole.USER,
            content="Hello, world!",
            sequence_number=1,
        )

        # Assert
        assert message.conversation_id == test_conversation.id
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"
        assert message.sequence_number == 1
        assert message.retry_count == 0

    def test_message_with_tool_calls(
        self, test_conversation: Conversation
    ):
        """Test message with tool calls."""
        # Arrange & Act
        tool_calls = [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "New York"}',
                },
            }
        ]

        message = Message(
            conversation_id=test_conversation.id,
            role=MessageRole.ASSISTANT,
            content="I'll get the weather for you.",
            tool_calls=tool_calls,
            sequence_number=2,
        )

        # Assert
        assert message.tool_calls == tool_calls
        assert len(message.tool_calls) == 1
        assert (
            message.tool_calls[0]["function"]["name"] == "get_weather"
        )

    def test_message_with_token_usage(
        self, test_conversation: Conversation
    ):
        """Test message with token usage information."""
        # Arrange & Act
        message = Message(
            conversation_id=test_conversation.id,
            role=MessageRole.ASSISTANT,
            content="Response with tokens",
            sequence_number=1,
            prompt_tokens=50,
            completion_tokens=25,
            total_tokens=75,
            model_used="gpt-4",
            provider_used="openai",
            finish_reason="stop",
            response_time_ms=1500,
            cost=0.0045,
        )

        # Assert
        assert message.prompt_tokens == 50
        assert message.completion_tokens == 25
        assert message.total_tokens == 75
        assert message.model_used == "gpt-4"
        assert message.provider_used == "openai"
        assert message.finish_reason == "stop"
        assert message.response_time_ms == 1500
        assert message.cost == 0.0045

    def test_message_with_retrieval_context(
        self, test_conversation: Conversation
    ):
        """Test message with retrieved documents and context."""
        # Arrange & Act
        message = Message(
            conversation_id=test_conversation.id,
            role=MessageRole.ASSISTANT,
            content="Based on the documents...",
            sequence_number=1,
            retrieved_documents=["doc1", "doc2", "doc3"],
            context_used="Relevant context from documents",
        )

        # Assert
        assert message.retrieved_documents == ["doc1", "doc2", "doc3"]
        assert message.context_used == "Relevant context from documents"

    def test_message_with_error(self, test_conversation: Conversation):
        """Test message with error information."""
        # Arrange & Act
        message = Message(
            conversation_id=test_conversation.id,
            role=MessageRole.ASSISTANT,
            content="Error occurred",
            sequence_number=1,
            error_message="API rate limit exceeded",
            retry_count=3,
        )

        # Assert
        assert message.error_message == "API rate limit exceeded"
        assert message.retry_count == 3

    def test_message_with_metadata(
        self, test_conversation: Conversation
    ):
        """Test message with extra metadata."""
        # Arrange & Act
        message = Message(
            conversation_id=test_conversation.id,
            role=MessageRole.SYSTEM,
            content="System message",
            sequence_number=0,
            extra_metadata={
                "custom_field": "value",
                "priority": "high",
                "source": "automated",
            },
        )

        # Assert
        assert message.extra_metadata["custom_field"] == "value"
        assert message.extra_metadata["priority"] == "high"
        assert message.extra_metadata["source"] == "automated"

    def test_message_to_dict(self, test_conversation: Conversation):
        """Test message to dictionary conversion."""
        # Arrange
        message = Message(
            conversation_id=test_conversation.id,
            role=MessageRole.USER,
            content="Test message",
            sequence_number=1,
            tool_calls=[{"id": "call_1"}],
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            extra_metadata={"key": "value"},
        )

        # Mock timestamps
        message.created_at = datetime(2023, 1, 1, 12, 0, 0)
        message.updated_at = datetime(2023, 1, 1, 12, 0, 5)

        # Act
        result = message.to_dict()

        # Assert
        assert result["id"] == message.id
        assert result["conversation_id"] == test_conversation.id
        assert result["role"] == "user"
        assert result["content"] == "Test message"
        assert result["sequence_number"] == 1
        assert result["tool_calls"] == [{"id": "call_1"}]
        assert result["prompt_tokens"] == 10
        assert result["completion_tokens"] == 5
        assert result["total_tokens"] == 15
        assert result["extra_metadata"] == {"key": "value"}
        assert "2023-01-01T12:00:00" in result["created_at"]
        assert "2023-01-01T12:00:05" in result["updated_at"]

    def test_message_repr(self, test_conversation: Conversation):
        """Test message string representation."""
        # Arrange
        message = Message(
            conversation_id=test_conversation.id,
            role=MessageRole.USER,
            content="This is a test message with content that is longer than fifty characters",
            sequence_number=1,
        )

        # Act
        repr_str = repr(message)

        # Assert
        assert "Message" in repr_str
        assert message.id in repr_str
        assert "user" in repr_str
        assert (
            "This is a test message with content that is longe..."
            in repr_str
        )

    def test_message_role_enum(self):
        """Test message role enumeration."""
        # Assert
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.TOOL == "tool"

    def test_conversation_status_enum(self):
        """Test conversation status enumeration."""
        # Assert
        assert ConversationStatus.ACTIVE == "active"
        assert ConversationStatus.ARCHIVED == "archived"
        assert ConversationStatus.DELETED == "deleted"


@pytest.mark.integration
class TestConversationModelIntegration:
    """Integration tests for conversation models."""

    def test_conversation_message_relationship(
        self, test_user: User, test_session
    ):
        """Test conversation-message relationship."""
        # Arrange
        conversation = Conversation(
            user_id=test_user.id,
            title="Relationship Test",
        )
        test_session.add(conversation)
        test_session.commit()

        # Act
        message1 = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="First message",
            sequence_number=1,
        )
        message2 = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content="Second message",
            sequence_number=2,
        )

        test_session.add_all([message1, message2])
        test_session.commit()

        # Refresh to load relationships
        test_session.refresh(conversation)

        # Assert
        assert len(conversation.messages) == 2
        assert conversation.messages[0].content == "First message"
        assert conversation.messages[1].content == "Second message"
        assert conversation.messages[0].conversation == conversation
        assert conversation.messages[1].conversation == conversation

    def test_conversation_user_relationship(
        self, test_user: User, test_session
    ):
        """Test conversation-user relationship."""
        # Arrange & Act
        conversation = Conversation(
            user_id=test_user.id,
            title="User Relationship Test",
        )
        test_session.add(conversation)
        test_session.commit()

        # Refresh to load relationships
        test_session.refresh(conversation)
        test_session.refresh(test_user)

        # Assert
        assert conversation.user == test_user
        assert conversation in test_user.conversations
