"""Tests for chat API endpoints."""

import json
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.api.auth import get_current_user
from chatter.api.chat import get_chat_service
from chatter.main import app
from chatter.models.conversation import Conversation, ConversationStatus, Message, MessageRole
from chatter.models.user import User
from chatter.services.chat import ChatService
from chatter.services.llm import LLMService


@pytest.mark.unit
class TestChatEndpoints:
    """Test chat API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_chat_service = AsyncMock(spec=ChatService)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True
        )

        # Override dependencies
        app.dependency_overrides[get_chat_service] = lambda: self.mock_chat_service
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_create_conversation_success(self):
        """Test successful conversation creation."""
        # Arrange
        conversation_data = {
            "title": "Test Conversation",
            "description": "A test conversation"
        }

        mock_conversation = Conversation(
            id="test-conv-id",
            title=conversation_data["title"],
            description=conversation_data["description"],
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        self.mock_chat_service.create_conversation.return_value = mock_conversation

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.post(
            "/api/v1/chat/conversations",
            json=conversation_data,
            headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["title"] == conversation_data["title"]
        assert response_data["status"] == ConversationStatus.ACTIVE.value

    def test_get_conversations_success(self):
        """Test retrieving user conversations."""
        # Arrange
        mock_conversations = [
            Conversation(
                id="conv-1",
                title="Conversation 1",
                user_id=self.mock_user.id,
                status=ConversationStatus.ACTIVE
            ),
            Conversation(
                id="conv-2",
                title="Conversation 2",
                user_id=self.mock_user.id,
                status=ConversationStatus.ARCHIVED
            )
        ]

        self.mock_chat_service.get_user_conversations.return_value = mock_conversations

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.get("/api/v1/chat/conversations", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["conversations"]) == 2
        assert response_data["conversations"][0]["title"] == "Conversation 1"

    def test_get_conversation_by_id_success(self):
        """Test retrieving specific conversation."""
        # Arrange
        conversation_id = "test-conv-id"
        mock_conversation = Conversation(
            id=conversation_id,
            title="Test Conversation",
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        mock_messages = [
            Message(
                id="msg-1",
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="Hello, world!",
                user_id=self.mock_user.id
            ),
            Message(
                id="msg-2",
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content="Hello! How can I help you?",
                user_id=None
            )
        ]

        self.mock_chat_service.get_conversation.return_value = mock_conversation
        self.mock_chat_service.get_conversation_messages.return_value = mock_messages

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.get(f"/api/v1/chat/conversations/{conversation_id}", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == conversation_id
        assert len(response_data["messages"]) == 2

    def test_get_conversation_not_found(self):
        """Test retrieving non-existent conversation."""
        # Arrange
        conversation_id = "non-existent-id"

        from chatter.core.exceptions import NotFoundError
        self.mock_chat_service.get_conversation.side_effect = NotFoundError("Conversation not found")

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.get(f"/api/v1/chat/conversations/{conversation_id}", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_send_message_success(self):
        """Test successful message sending."""
        # Arrange
        conversation_id = "test-conv-id"
        message_data = {
            "content": "Hello, AI assistant!",
            "role": "user"
        }

        mock_user_message = Message(
            id="user-msg-id",
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message_data["content"],
            user_id=self.mock_user.id
        )

        mock_assistant_message = Message(
            id="assistant-msg-id",
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Hello! How can I help you today?",
            user_id=None
        )

        self.mock_chat_service.send_message.return_value = (mock_user_message, mock_assistant_message)

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json=message_data,
            headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["user_message"]["content"] == message_data["content"]
        assert response_data["assistant_message"]["role"] == MessageRole.ASSISTANT.value

    def test_chat_with_agent_success(self):
        """Test chat endpoint with agent."""
        # Arrange
        chat_data = {
            "message": "What's the weather like?",
            "conversation_id": "test-conv-id",
            "agent_id": "weather-agent",
            "stream": False
        }

        mock_response = {
            "message": "I'd be happy to help you with weather information!",
            "conversation_id": chat_data["conversation_id"],
            "message_id": "response-msg-id",
            "metadata": {
                "agent_used": chat_data["agent_id"],
                "tokens_used": 25
            }
        }

        self.mock_chat_service.chat_with_agent.return_value = mock_response

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.post("/api/v1/chat", json=chat_data, headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["message"] == mock_response["message"]
        assert response_data["conversation_id"] == chat_data["conversation_id"]

    def test_chat_streaming_response(self):
        """Test streaming chat response."""
        # Arrange
        chat_data = {
            "message": "Tell me a story",
            "conversation_id": "test-conv-id",
            "stream": True
        }

        # Mock streaming response
        async def mock_stream():
            chunks = [
                {"type": "start", "data": {"message_id": "stream-msg-id"}},
                {"type": "content", "data": {"content": "Once upon a time"}},
                {"type": "content", "data": {"content": " there was a"}},
                {"type": "content", "data": {"content": " brave knight."}},
                {"type": "end", "data": {"tokens_used": 15}}
            ]
            for chunk in chunks:
                yield f"data: {json.dumps(chunk)}\n\n"

        self.mock_chat_service.chat_with_agent_stream.return_value = mock_stream()

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.post("/api/v1/chat", json=chat_data, headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

    def test_update_conversation_success(self):
        """Test updating conversation details."""
        # Arrange
        conversation_id = "test-conv-id"
        update_data = {
            "title": "Updated Conversation Title",
            "description": "Updated description"
        }

        mock_updated_conversation = Conversation(
            id=conversation_id,
            title=update_data["title"],
            description=update_data["description"],
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        self.mock_chat_service.update_conversation.return_value = mock_updated_conversation

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.put(
            f"/api/v1/chat/conversations/{conversation_id}",
            json=update_data,
            headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["title"] == update_data["title"]
        assert response_data["description"] == update_data["description"]

    def test_delete_conversation_success(self):
        """Test deleting a conversation."""
        # Arrange
        conversation_id = "test-conv-id"
        self.mock_chat_service.delete_conversation.return_value = True

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.delete(f"/api/v1/chat/conversations/{conversation_id}", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["message"] == "Conversation deleted successfully"

    def test_delete_message_success(self):
        """Test deleting a message."""
        # Arrange
        conversation_id = "test-conv-id"
        message_id = "test-msg-id"
        self.mock_chat_service.delete_message.return_value = True

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.delete(
            f"/api/v1/chat/conversations/{conversation_id}/messages/{message_id}",
            headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["message"] == "Message deleted successfully"

    def test_get_available_tools_success(self):
        """Test retrieving available tools."""
        # Arrange
        mock_tools = [
            {
                "name": "calculator",
                "description": "Perform mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Mathematical expression"}
                    }
                }
            },
            {
                "name": "web_search",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    }
                }
            }
        ]

        self.mock_chat_service.get_available_tools.return_value = mock_tools

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.get("/api/v1/chat/tools", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["tools"]) == 2
        assert response_data["tools"][0]["name"] == "calculator"

    def test_search_conversations_success(self):
        """Test conversation search functionality."""
        # Arrange
        search_query = "weather"
        mock_conversations = [
            Conversation(
                id="conv-1",
                title="Weather Discussion",
                user_id=self.mock_user.id,
                status=ConversationStatus.ACTIVE
            )
        ]

        self.mock_chat_service.search_conversations.return_value = mock_conversations

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.get(f"/api/v1/chat/conversations/search?q={search_query}", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["conversations"]) == 1
        assert "weather" in response_data["conversations"][0]["title"].lower()

    def test_get_workflow_templates_success(self):
        """Test retrieving workflow templates."""
        # Arrange
        mock_templates = [
            {
                "id": "data-analysis",
                "name": "Data Analysis Workflow",
                "description": "Analyze datasets and generate insights",
                "category": "analytics"
            },
            {
                "id": "content-creation",
                "name": "Content Creation Workflow",
                "description": "Generate and refine content",
                "category": "writing"
            }
        ]

        self.mock_chat_service.get_workflow_templates.return_value = mock_templates

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.get("/api/v1/chat/workflow-templates", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["templates"]) == 2
        assert response_data["templates"][0]["name"] == "Data Analysis Workflow"

    def test_get_performance_stats_success(self):
        """Test retrieving chat performance statistics."""
        # Arrange
        mock_stats = {
            "total_conversations": 42,
            "total_messages": 256,
            "average_response_time": 1.2,
            "most_used_agent": "general-assistant",
            "success_rate": 0.98
        }

        self.mock_chat_service.get_performance_stats.return_value = mock_stats

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.get("/api/v1/chat/stats", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["total_conversations"] == 42
        assert response_data["success_rate"] == 0.98


@pytest.mark.integration
class TestChatIntegration:
    """Integration tests for chat functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="integration-user-id",
            email="integration@example.com",
            username="integrationuser",
            is_active=True
        )

        # Mock dependencies
        self.mock_chat_service = AsyncMock(spec=ChatService)
        app.dependency_overrides[get_chat_service] = lambda: self.mock_chat_service
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_full_conversation_flow(self):
        """Test complete conversation flow."""
        # Create conversation
        conversation_data = {
            "title": "Integration Test Conversation",
            "description": "Testing full conversation flow"
        }

        mock_conversation = Conversation(
            id="integration-conv-id",
            title=conversation_data["title"],
            description=conversation_data["description"],
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        self.mock_chat_service.create_conversation.return_value = mock_conversation

        headers = {"Authorization": "Bearer integration-token"}

        # Test conversation creation
        response = self.client.post(
            "/api/v1/chat/conversations",
            json=conversation_data,
            headers=headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        conv_data = response.json()
        conversation_id = conv_data["id"]

        # Test sending message
        message_data = {"content": "Hello integration test!", "role": "user"}

        mock_user_message = Message(
            id="integration-user-msg",
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message_data["content"],
            user_id=self.mock_user.id
        )

        mock_assistant_message = Message(
            id="integration-assistant-msg",
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Hello! This is an integration test response.",
            user_id=None
        )

        self.mock_chat_service.send_message.return_value = (mock_user_message, mock_assistant_message)

        response = self.client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json=message_data,
            headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        message_response = response.json()
        assert message_response["user_message"]["content"] == message_data["content"]

        # Test retrieving conversation with messages
        mock_messages = [mock_user_message, mock_assistant_message]
        self.mock_chat_service.get_conversation.return_value = mock_conversation
        self.mock_chat_service.get_conversation_messages.return_value = mock_messages

        response = self.client.get(f"/api/v1/chat/conversations/{conversation_id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        conv_with_messages = response.json()
        assert len(conv_with_messages["messages"]) == 2
        assert conv_with_messages["messages"][0]["role"] == "user"
        assert conv_with_messages["messages"][1]["role"] == "assistant"
