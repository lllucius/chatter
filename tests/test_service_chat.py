"""Tests for chat service functionality."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.conversation import Conversation, ConversationStatus, Message, MessageRole
from chatter.models.user import User
from chatter.services.chat import ChatService


@pytest.mark.unit
class TestChatService:
    """Test chat service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.mock_llm_service = AsyncMock()
        self.chat_service = ChatService(self.mock_session, self.mock_llm_service)

        # Mock user
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True
        )

        # Mock agent using MagicMock instead of instantiating abstract class
        from unittest.mock import MagicMock
        self.mock_agent = MagicMock()
        self.mock_agent.id = "test-agent-id"
        self.mock_agent.name = "Test Agent"
        self.mock_agent.description = "A test agent"
        self.mock_agent.user_id = self.mock_user.id

    @pytest.mark.asyncio
    async def test_create_conversation_success(self):
        """Test successful conversation creation."""
        # Arrange
        conversation_data = {
            "title": "Test Conversation",
            "description": "A test conversation",
            "profile_id": "test-profile-id"
        }

        expected_conversation = Conversation(
            id="new-conv-id",
            title=conversation_data["title"],
            description=conversation_data["description"],
            user_id=self.mock_user.id,
            profile_id=conversation_data["profile_id"],
            status=ConversationStatus.ACTIVE
        )

        with patch.object(self.chat_service.conversation_service, 'create_conversation') as mock_create:
            mock_create.return_value = expected_conversation

            # Act
            from chatter.schemas.chat import ConversationCreate
            conversation_schema = ConversationCreate(**conversation_data)
            result = await self.chat_service.create_conversation(
                user_id=self.mock_user.id,
                conversation_data=conversation_schema
            )

            # Assert
            assert result.id == expected_conversation.id
            assert result.title == conversation_data["title"]
            assert result.user_id == self.mock_user.id
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_conversations(self):
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

        with patch.object(self.chat_service, '_fetch_user_conversations') as mock_fetch:
            mock_fetch.return_value = mock_conversations

            # Act
            result = await self.chat_service.get_user_conversations(
                user_id=self.mock_user.id
            )

            # Assert
            assert len(result) == 2
            assert result[0].title == "Conversation 1"
            assert result[1].title == "Conversation 2"

    @pytest.mark.asyncio
    async def test_get_conversation_by_id(self):
        """Test retrieving conversation by ID."""
        # Arrange
        conversation_id = "test-conv-id"
        mock_conversation = Conversation(
            id=conversation_id,
            title="Test Conversation",
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        with patch.object(self.chat_service, '_fetch_conversation_by_id') as mock_fetch:
            mock_fetch.return_value = mock_conversation

            # Act
            result = await self.chat_service.get_conversation(
                conversation_id=conversation_id,
                user_id=self.mock_user.id
            )

            # Assert
            assert result.id == conversation_id
            assert result.title == "Test Conversation"

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self):
        """Test retrieving non-existent conversation."""
        # Arrange
        conversation_id = "non-existent-id"

        with patch.object(self.chat_service, '_fetch_conversation_by_id') as mock_fetch:
            mock_fetch.return_value = None

            # Act & Assert
            from chatter.core.exceptions import NotFoundError
            with pytest.raises(NotFoundError):
                await self.chat_service.get_conversation(
                    conversation_id=conversation_id,
                    user_id=self.mock_user.id
                )

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending."""
        # Arrange
        conversation_id = "test-conv-id"
        message_content = "Hello, AI!"

        mock_conversation = Conversation(
            id=conversation_id,
            title="Test Conversation",
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        expected_user_message = Message(
            id="user-msg-id",
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message_content,
            user_id=self.mock_user.id
        )

        expected_assistant_message = Message(
            id="assistant-msg-id",
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Hello! How can I help you?",
            user_id=None
        )

        with patch.object(self.chat_service, 'get_conversation') as mock_get_conv:
            mock_get_conv.return_value = mock_conversation

            with patch.object(self.chat_service, '_create_user_message') as mock_create_user_msg:
                mock_create_user_msg.return_value = expected_user_message

                with patch.object(self.chat_service, '_generate_assistant_response') as mock_generate:
                    mock_generate.return_value = expected_assistant_message

                    # Act
                    user_msg, assistant_msg = await self.chat_service.send_message(
                        conversation_id=conversation_id,
                        content=message_content,
                        user_id=self.mock_user.id
                    )

                    # Assert
                    assert user_msg.content == message_content
                    assert user_msg.role == MessageRole.USER
                    assert assistant_msg.role == MessageRole.ASSISTANT
                    assert assistant_msg.content == "Hello! How can I help you?"

    @pytest.mark.asyncio
    async def test_send_message_to_inactive_conversation(self):
        """Test sending message to inactive conversation."""
        # Arrange
        conversation_id = "inactive-conv-id"

        mock_conversation = Conversation(
            id=conversation_id,
            title="Inactive Conversation",
            user_id=self.mock_user.id,
            status=ConversationStatus.ARCHIVED
        )

        with patch.object(self.chat_service, 'get_conversation') as mock_get_conv:
            mock_get_conv.return_value = mock_conversation

            # Act & Assert
            from chatter.core.exceptions import ConflictError
            with pytest.raises(ConflictError):
                await self.chat_service.send_message(
                    conversation_id=conversation_id,
                    content="Test message",
                    user_id=self.mock_user.id
                )

    @pytest.mark.asyncio
    async def test_get_conversation_messages(self):
        """Test retrieving conversation messages."""
        # Arrange
        conversation_id = "test-conv-id"

        mock_messages = [
            Message(
                id="msg-1",
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="Hello",
                user_id=self.mock_user.id,
                created_at=datetime(2024, 1, 1, 10, 0, 0)
            ),
            Message(
                id="msg-2",
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content="Hi there!",
                user_id=None,
                created_at=datetime(2024, 1, 1, 10, 0, 5)
            )
        ]

        with patch.object(self.chat_service, '_fetch_conversation_messages') as mock_fetch:
            mock_fetch.return_value = mock_messages

            # Act
            result = await self.chat_service.get_conversation_messages(
                conversation_id=conversation_id,
                user_id=self.mock_user.id
            )

            # Assert
            assert len(result) == 2
            assert result[0].role == MessageRole.USER
            assert result[1].role == MessageRole.ASSISTANT

    @pytest.mark.asyncio
    async def test_update_conversation_success(self):
        """Test successful conversation update."""
        # Arrange
        conversation_id = "test-conv-id"
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }

        mock_conversation = Conversation(
            id=conversation_id,
            title="Original Title",
            description="Original description",
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        updated_conversation = Conversation(
            id=conversation_id,
            title=update_data["title"],
            description=update_data["description"],
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        with patch.object(self.chat_service, 'get_conversation') as mock_get:
            mock_get.return_value = mock_conversation

            with patch.object(self.chat_service, '_update_conversation_record') as mock_update:
                mock_update.return_value = updated_conversation

                # Act
                result = await self.chat_service.update_conversation(
                    conversation_id=conversation_id,
                    user_id=self.mock_user.id,
                    **update_data
                )

                # Assert
                assert result.title == update_data["title"]
                assert result.description == update_data["description"]

    @pytest.mark.asyncio
    async def test_delete_conversation_success(self):
        """Test successful conversation deletion."""
        # Arrange
        conversation_id = "test-conv-id"

        mock_conversation = Conversation(
            id=conversation_id,
            title="Test Conversation",
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        with patch.object(self.chat_service, 'get_conversation') as mock_get:
            mock_get.return_value = mock_conversation

            with patch.object(self.chat_service, '_delete_conversation_record') as mock_delete:
                mock_delete.return_value = True

                # Act
                result = await self.chat_service.delete_conversation(
                    conversation_id=conversation_id,
                    user_id=self.mock_user.id
                )

                # Assert
                assert result is True
                mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_message_success(self):
        """Test successful message deletion."""
        # Arrange
        conversation_id = "test-conv-id"
        message_id = "test-msg-id"

        mock_message = Message(
            id=message_id,
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Test message",
            user_id=self.mock_user.id
        )

        with patch.object(self.chat_service, '_fetch_message_by_id') as mock_fetch:
            mock_fetch.return_value = mock_message

            with patch.object(self.chat_service, '_delete_message_record') as mock_delete:
                mock_delete.return_value = True

                # Act
                result = await self.chat_service.delete_message(
                    conversation_id=conversation_id,
                    message_id=message_id,
                    user_id=self.mock_user.id
                )

                # Assert
                assert result is True
                mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_with_agent_success(self):
        """Test chat with specific agent."""
        # Arrange
        message = "What's the weather like?"
        conversation_id = "test-conv-id"
        agent_id = "weather-agent"

        expected_response = {
            "message": "I'd be happy to help with weather information!",
            "conversation_id": conversation_id,
            "message_id": "response-msg-id",
            "metadata": {
                "agent_used": agent_id,
                "tokens_used": 25
            }
        }

        with patch.object(self.chat_service, '_process_agent_chat') as mock_process:
            mock_process.return_value = expected_response

            # Act
            result = await self.chat_service.chat_with_agent(
                message=message,
                conversation_id=conversation_id,
                agent_id=agent_id,
                user_id=self.mock_user.id
            )

            # Assert
            assert result["message"] == expected_response["message"]
            assert result["agent_used"] == agent_id

    @pytest.mark.asyncio
    async def test_search_conversations(self):
        """Test conversation search functionality."""
        # Arrange
        search_query = "weather"

        matching_conversations = [
            Conversation(
                id="conv-1",
                title="Weather Discussion",
                user_id=self.mock_user.id,
                status=ConversationStatus.ACTIVE
            )
        ]

        with patch.object(self.chat_service, '_search_conversations_by_query') as mock_search:
            mock_search.return_value = matching_conversations

            # Act
            result = await self.chat_service.search_conversations(
                user_id=self.mock_user.id,
                query=search_query
            )

            # Assert
            assert len(result) == 1
            assert "weather" in result[0].title.lower()

    @pytest.mark.asyncio
    async def test_get_available_tools(self):
        """Test retrieving available chat tools."""
        # Arrange
        expected_tools = [
            {
                "name": "calculator",
                "description": "Perform mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    }
                }
            },
            {
                "name": "web_search",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    }
                }
            }
        ]

        with patch.object(self.chat_service, '_fetch_available_tools') as mock_fetch:
            mock_fetch.return_value = expected_tools

            # Act
            result = await self.chat_service.get_available_tools()

            # Assert
            assert len(result) == 2
            assert result[0]["name"] == "calculator"
            assert result[1]["name"] == "web_search"

    @pytest.mark.asyncio
    async def test_get_workflow_templates(self):
        """Test retrieving workflow templates."""
        # Arrange
        expected_templates = [
            {
                "id": "data-analysis",
                "name": "Data Analysis Workflow",
                "description": "Analyze datasets and generate insights",
                "category": "analytics"
            }
        ]

        with patch.object(self.chat_service, '_fetch_workflow_templates') as mock_fetch:
            mock_fetch.return_value = expected_templates

            # Act
            result = await self.chat_service.get_workflow_templates()

            # Assert
            assert len(result) == 1
            assert result[0]["name"] == "Data Analysis Workflow"

    @pytest.mark.asyncio
    async def test_get_performance_stats(self):
        """Test retrieving chat performance statistics."""
        # Arrange
        expected_stats = {
            "total_conversations": 42,
            "total_messages": 256,
            "average_response_time": 1.2,
            "most_used_agent": "general-assistant",
            "success_rate": 0.98
        }

        with patch.object(self.chat_service, '_calculate_performance_stats') as mock_calc:
            mock_calc.return_value = expected_stats

            # Act
            result = await self.chat_service.get_performance_stats(
                user_id=self.mock_user.id
            )

            # Assert
            assert result["total_conversations"] == 42
            assert result["success_rate"] == 0.98


@pytest.mark.integration
class TestChatServiceIntegration:
    """Integration tests for chat service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.mock_llm_service = AsyncMock()
        self.chat_service = ChatService(self.mock_session, self.mock_llm_service)

        self.mock_user = User(
            id="integration-user-id",
            email="integration@example.com",
            username="integrationuser"
        )

    @pytest.mark.asyncio
    async def test_full_conversation_lifecycle(self):
        """Test complete conversation lifecycle."""
        # Mock all required service methods
        conversation_id = "integration-conv-id"

        # Mock conversation creation
        mock_conversation = Conversation(
            id=conversation_id,
            title="Integration Test Conversation",
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        with patch.object(self.chat_service, '_create_conversation_record') as mock_create_conv:
            mock_create_conv.return_value = mock_conversation

            # Create conversation
            conversation = await self.chat_service.create_conversation(
                user_id=self.mock_user.id,
                title="Integration Test Conversation"
            )

            assert conversation.title == "Integration Test Conversation"

            # Mock message sending
            with patch.object(self.chat_service, 'get_conversation') as mock_get_conv:
                mock_get_conv.return_value = mock_conversation

                with patch.object(self.chat_service, '_create_user_message') as mock_create_msg:
                    mock_create_msg.return_value = Message(
                        id="integration-user-msg",
                        conversation_id=conversation_id,
                        role=MessageRole.USER,
                        content="Hello integration!",
                        user_id=self.mock_user.id
                    )

                    with patch.object(self.chat_service, '_generate_assistant_response') as mock_generate:
                        mock_generate.return_value = Message(
                            id="integration-assistant-msg",
                            conversation_id=conversation_id,
                            role=MessageRole.ASSISTANT,
                            content="Hello! Integration test response.",
                            user_id=None
                        )

                        # Send message
                        user_msg, assistant_msg = await self.chat_service.send_message(
                            conversation_id=conversation_id,
                            content="Hello integration!",
                            user_id=self.mock_user.id
                        )

                        assert user_msg.content == "Hello integration!"
                        assert assistant_msg.role == MessageRole.ASSISTANT

                        # Mock conversation deletion
                        with patch.object(self.chat_service, '_delete_conversation_record') as mock_delete:
                            mock_delete.return_value = True

                            # Delete conversation
                            deleted = await self.chat_service.delete_conversation(
                                conversation_id=conversation_id,
                                user_id=self.mock_user.id
                            )

                            assert deleted is True

    @pytest.mark.asyncio
    async def test_concurrent_message_sending(self):
        """Test handling concurrent message sending."""
        conversation_id = "concurrent-test-conv"

        mock_conversation = Conversation(
            id=conversation_id,
            title="Concurrent Test",
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        # Mock the required methods
        with patch.object(self.chat_service, 'get_conversation') as mock_get_conv:
            mock_get_conv.return_value = mock_conversation

            with patch.object(self.chat_service, '_create_user_message') as mock_create_msg:
                with patch.object(self.chat_service, '_generate_assistant_response') as mock_generate:

                    # Setup side effects for multiple calls
                    mock_create_msg.side_effect = [
                        Message(id=f"user-msg-{i}", conversation_id=conversation_id,
                               role=MessageRole.USER, content=f"Message {i}",
                               user_id=self.mock_user.id)
                        for i in range(3)
                    ]

                    mock_generate.side_effect = [
                        Message(id=f"assistant-msg-{i}", conversation_id=conversation_id,
                               role=MessageRole.ASSISTANT, content=f"Response {i}",
                               user_id=None)
                        for i in range(3)
                    ]

                    # Send multiple messages concurrently
                    tasks = [
                        self.chat_service.send_message(
                            conversation_id=conversation_id,
                            content=f"Concurrent message {i}",
                            user_id=self.mock_user.id
                        )
                        for i in range(3)
                    ]

                    results = await asyncio.gather(*tasks)

                    # All messages should be processed successfully
                    assert len(results) == 3
                    for user_msg, assistant_msg in results:
                        assert user_msg.role == MessageRole.USER
                        assert assistant_msg.role == MessageRole.ASSISTANT


@pytest.mark.unit
class TestChatServiceErrorHandling:
    """Test chat service error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.mock_llm_service = AsyncMock()
        self.chat_service = ChatService(self.mock_session, self.mock_llm_service)

        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser"
        )

    @pytest.mark.asyncio
    async def test_handle_database_connection_error(self):
        """Test handling database connection errors."""
        # Arrange
        with patch.object(self.chat_service, '_create_conversation_record') as mock_create:
            mock_create.side_effect = Exception("Database connection failed")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await self.chat_service.create_conversation(
                    user_id=self.mock_user.id,
                    title="Test Conversation"
                )

            assert "Database connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_llm_service_unavailable(self):
        """Test handling LLM service unavailability."""
        conversation_id = "test-conv-id"

        mock_conversation = Conversation(
            id=conversation_id,
            title="Test Conversation",
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

        with patch.object(self.chat_service, 'get_conversation') as mock_get_conv:
            mock_get_conv.return_value = mock_conversation

            with patch.object(self.chat_service, '_create_user_message') as mock_create_msg:
                mock_create_msg.return_value = Message(
                    id="user-msg-id",
                    conversation_id=conversation_id,
                    role=MessageRole.USER,
                    content="Test message",
                    user_id=self.mock_user.id
                )

                with patch.object(self.chat_service, '_generate_assistant_response') as mock_generate:
                    mock_generate.side_effect = Exception("LLM service unavailable")

                    # Act & Assert
                    with pytest.raises(Exception) as exc_info:
                        await self.chat_service.send_message(
                            conversation_id=conversation_id,
                            content="Test message",
                            user_id=self.mock_user.id
                        )

                    assert "LLM service unavailable" in str(exc_info.value)
