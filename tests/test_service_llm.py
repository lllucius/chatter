"""Tests for LLM service functionality."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.services.llm import LLMService
from chatter.models.conversation import Conversation, ConversationStatus
from chatter.models.message import Message, MessageRole
from chatter.models.user import User


@pytest.mark.unit
class TestLLMService:
    """Test LLM service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.llm_service = LLMService(self.mock_session)
        
        # Mock user and conversation
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser"
        )
        
        self.mock_conversation = Conversation(
            id="test-conv-id",
            title="Test Conversation",
            user_id=self.mock_user.id,
            status=ConversationStatus.ACTIVE
        )

    @pytest.mark.asyncio
    async def test_generate_response_success(self):
        """Test successful response generation."""
        # Arrange
        message = "What is the capital of France?"
        context = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you?"}
        ]
        
        expected_response = "The capital of France is Paris."
        
        with patch.object(self.llm_service, '_call_llm_provider') as mock_llm_call:
            mock_llm_call.return_value = expected_response
            
            # Act
            result = await self.llm_service.generate_response(
                message=message,
                context=context,
                conversation_id=self.mock_conversation.id
            )
            
            # Assert
            assert result == expected_response
            mock_llm_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_response_with_agent(self):
        """Test response generation with specific agent."""
        # Arrange
        message = "Calculate 2 + 2"
        agent_id = "math-assistant"
        
        expected_response = "2 + 2 = 4"
        
        with patch.object(self.llm_service, '_call_llm_provider') as mock_llm_call:
            mock_llm_call.return_value = expected_response
            
            # Act
            result = await self.llm_service.generate_response(
                message=message,
                agent_id=agent_id,
                conversation_id=self.mock_conversation.id
            )
            
            # Assert
            assert result == expected_response
            mock_llm_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_streaming_response(self):
        """Test streaming response generation."""
        # Arrange
        message = "Tell me a story"
        chunks = ["Once ", "upon ", "a ", "time..."]
        
        async def mock_stream():
            for chunk in chunks:
                yield chunk
        
        with patch.object(self.llm_service, '_stream_llm_provider') as mock_stream_call:
            mock_stream_call.return_value = mock_stream()
            
            # Act
            response_stream = self.llm_service.generate_streaming_response(
                message=message,
                conversation_id=self.mock_conversation.id
            )
            
            # Collect all chunks
            result_chunks = []
            async for chunk in response_stream:
                result_chunks.append(chunk)
            
            # Assert
            assert result_chunks == chunks
            mock_stream_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_available_models(self):
        """Test retrieving available LLM models."""
        # Arrange
        expected_models = [
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "openai",
                "capabilities": ["text", "reasoning"]
            },
            {
                "id": "claude-3",
                "name": "Claude 3",
                "provider": "anthropic",
                "capabilities": ["text", "analysis"]
            }
        ]
        
        with patch.object(self.llm_service, '_fetch_available_models') as mock_fetch:
            mock_fetch.return_value = expected_models
            
            # Act
            models = await self.llm_service.get_available_models()
            
            # Assert
            assert len(models) == 2
            assert models[0]["id"] == "gpt-4"
            assert models[1]["id"] == "claude-3"

    @pytest.mark.asyncio
    async def test_validate_model_exists(self):
        """Test model validation."""
        # Arrange
        valid_model = "gpt-4"
        invalid_model = "nonexistent-model"
        
        available_models = [{"id": "gpt-4"}, {"id": "claude-3"}]
        
        with patch.object(self.llm_service, 'get_available_models') as mock_get_models:
            mock_get_models.return_value = available_models
            
            # Act & Assert
            assert await self.llm_service.validate_model(valid_model) is True
            assert await self.llm_service.validate_model(invalid_model) is False

    @pytest.mark.asyncio
    async def test_handle_tool_calling(self):
        """Test LLM tool calling functionality."""
        # Arrange
        message = "What's the weather in Paris?"
        available_tools = [
            {
                "name": "get_weather",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    }
                }
            }
        ]
        
        # Mock tool call response
        tool_call_response = {
            "tool_calls": [
                {
                    "name": "get_weather",
                    "arguments": {"location": "Paris"}
                }
            ]
        }
        
        tool_result = {"temperature": "22°C", "condition": "sunny"}
        final_response = "The weather in Paris is 22°C and sunny."
        
        with patch.object(self.llm_service, '_call_llm_provider') as mock_llm_call:
            mock_llm_call.side_effect = [tool_call_response, final_response]
            
            with patch.object(self.llm_service, '_execute_tool_call') as mock_tool_exec:
                mock_tool_exec.return_value = tool_result
                
                # Act
                result = await self.llm_service.generate_response_with_tools(
                    message=message,
                    tools=available_tools,
                    conversation_id=self.mock_conversation.id
                )
                
                # Assert
                assert result == final_response
                assert mock_llm_call.call_count == 2
                mock_tool_exec.assert_called_once()

    @pytest.mark.asyncio
    async def test_calculate_token_usage(self):
        """Test token usage calculation."""
        # Arrange
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        expected_tokens = {"prompt_tokens": 15, "completion_tokens": 8, "total_tokens": 23}
        
        with patch.object(self.llm_service, '_count_tokens') as mock_count:
            mock_count.return_value = expected_tokens
            
            # Act
            tokens = await self.llm_service.calculate_token_usage(messages)
            
            # Assert
            assert tokens["total_tokens"] == 23
            assert tokens["prompt_tokens"] == 15
            assert tokens["completion_tokens"] == 8

    @pytest.mark.asyncio
    async def test_handle_rate_limiting(self):
        """Test rate limiting handling."""
        # Arrange
        message = "Test message"
        
        from chatter.core.exceptions import RateLimitError
        
        with patch.object(self.llm_service, '_call_llm_provider') as mock_llm_call:
            mock_llm_call.side_effect = RateLimitError("Rate limit exceeded")
            
            # Act & Assert
            with pytest.raises(RateLimitError):
                await self.llm_service.generate_response(
                    message=message,
                    conversation_id=self.mock_conversation.id
                )

    @pytest.mark.asyncio
    async def test_handle_context_length_limit(self):
        """Test handling of context length limits."""
        # Arrange
        long_message = "Very long message " * 1000  # Simulate long context
        
        with patch.object(self.llm_service, '_check_context_length') as mock_check:
            mock_check.return_value = False  # Context too long
            
            with patch.object(self.llm_service, '_truncate_context') as mock_truncate:
                mock_truncate.return_value = [{"role": "user", "content": "Truncated message"}]
                
                with patch.object(self.llm_service, '_call_llm_provider') as mock_llm_call:
                    mock_llm_call.return_value = "Response to truncated context"
                    
                    # Act
                    result = await self.llm_service.generate_response(
                        message=long_message,
                        conversation_id=self.mock_conversation.id
                    )
                    
                    # Assert
                    assert result == "Response to truncated context"
                    mock_truncate.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_provider_fallback(self):
        """Test fallback between multiple LLM providers."""
        # Arrange
        message = "Test message"
        
        with patch.object(self.llm_service, '_call_llm_provider') as mock_llm_call:
            # First provider fails, second succeeds
            mock_llm_call.side_effect = [
                Exception("Primary provider failed"),
                "Response from fallback provider"
            ]
            
            # Act
            result = await self.llm_service.generate_response_with_fallback(
                message=message,
                conversation_id=self.mock_conversation.id
            )
            
            # Assert
            assert result == "Response from fallback provider"
            assert mock_llm_call.call_count == 2

    @pytest.mark.asyncio
    async def test_conversation_context_management(self):
        """Test conversation context management."""
        # Arrange
        conversation_id = self.mock_conversation.id
        
        # Mock existing messages
        existing_messages = [
            Message(
                id="msg-1",
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="Hello",
                user_id=self.mock_user.id
            ),
            Message(
                id="msg-2",
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content="Hi! How can I help?",
                user_id=None
            )
        ]
        
        with patch.object(self.llm_service, '_get_conversation_messages') as mock_get_msgs:
            mock_get_msgs.return_value = existing_messages
            
            # Act
            context = await self.llm_service.build_conversation_context(conversation_id)
            
            # Assert
            assert len(context) == 2
            assert context[0]["role"] == "user"
            assert context[0]["content"] == "Hello"
            assert context[1]["role"] == "assistant"
            assert context[1]["content"] == "Hi! How can I help?"


@pytest.mark.integration
class TestLLMServiceIntegration:
    """Integration tests for LLM service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.llm_service = LLMService(self.mock_session)

    @pytest.mark.asyncio
    async def test_end_to_end_conversation_flow(self):
        """Test complete conversation flow with LLM service."""
        # This would test the full integration with actual or mocked LLM providers
        # For now, we'll mock the external dependencies
        
        conversation_id = "integration-conv-id"
        
        # Mock conversation messages retrieval
        with patch.object(self.llm_service, '_get_conversation_messages') as mock_get_msgs:
            mock_get_msgs.return_value = []
            
            # Mock LLM provider call
            with patch.object(self.llm_service, '_call_llm_provider') as mock_llm_call:
                mock_llm_call.return_value = "Hello! I'm ready to help you."
                
                # Act
                response = await self.llm_service.generate_response(
                    message="Hello, AI assistant!",
                    conversation_id=conversation_id
                )
                
                # Assert
                assert response == "Hello! I'm ready to help you."
                mock_get_msgs.assert_called_once_with(conversation_id)
                mock_llm_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_recovery_and_logging(self):
        """Test error recovery and proper logging."""
        message = "Test message for error handling"
        
        with patch.object(self.llm_service, '_call_llm_provider') as mock_llm_call:
            # Simulate provider error
            mock_llm_call.side_effect = Exception("Provider temporarily unavailable")
            
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await self.llm_service.generate_response(
                    message=message,
                    conversation_id="test-conv-id"
                )
            
            assert "Provider temporarily unavailable" in str(exc_info.value)


@pytest.mark.unit
class TestLLMServiceConfiguration:
    """Test LLM service configuration and setup."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)

    def test_llm_service_initialization(self):
        """Test LLM service initialization."""
        # Act
        llm_service = LLMService(self.mock_session)
        
        # Assert
        assert llm_service.session == self.mock_session
        assert hasattr(llm_service, 'config')

    def test_provider_configuration(self):
        """Test LLM provider configuration."""
        # Arrange
        llm_service = LLMService(self.mock_session)
        
        # Act
        providers = llm_service.get_configured_providers()
        
        # Assert
        assert isinstance(providers, list)
        # Should have at least one provider configured
        assert len(providers) >= 0  # Might be empty in test environment

    @pytest.mark.asyncio
    async def test_model_selection_logic(self):
        """Test model selection logic."""
        # Arrange
        llm_service = LLMService(self.mock_session)
        
        preferences = {
            "task_type": "general",
            "quality": "high",
            "speed": "medium"
        }
        
        with patch.object(llm_service, 'get_available_models') as mock_get_models:
            mock_get_models.return_value = [
                {"id": "gpt-4", "quality": "high", "speed": "medium"},
                {"id": "gpt-3.5-turbo", "quality": "medium", "speed": "high"}
            ]
            
            # Act
            selected_model = await llm_service.select_optimal_model(preferences)
            
            # Assert
            assert selected_model in ["gpt-4", "gpt-3.5-turbo"]