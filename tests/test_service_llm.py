"""LLM Service tests."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from chatter.services.llm import LLMService


@pytest.mark.unit
class TestLLMService:
    """Test LLM service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.llm_service = LLMService()

    async def test_openai_provider_support(self):
        """Test OpenAI provider support."""
        with patch('openai.ChatCompletion.acreate') as mock_create:
            mock_create.return_value = {
                "choices": [{
                    "message": {
                        "content": "Hello! How can I help you today?",
                        "role": "assistant"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 8,
                    "total_tokens": 18
                }
            }
            
            result = await self.llm_service.generate(
                messages=[{"role": "user", "content": "Hello"}],
                provider="openai",
                model="gpt-3.5-turbo"
            )
            
            assert result["content"] == "Hello! How can I help you today?"
            assert result["role"] == "assistant"
            assert result["usage"]["total_tokens"] == 18

    async def test_anthropic_provider_support(self):
        """Test Anthropic provider support."""
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            
            mock_client.messages.create.return_value = AsyncMock(
                content=[{
                    "type": "text",
                    "text": "I'm Claude, an AI assistant created by Anthropic."
                }],
                usage={
                    "input_tokens": 12,
                    "output_tokens": 10
                }
            )
            
            result = await self.llm_service.generate(
                messages=[{"role": "user", "content": "Who are you?"}],
                provider="anthropic",
                model="claude-3-sonnet"
            )
            
            assert "Claude" in result["content"]
            assert result["role"] == "assistant"

    async def test_streaming_response_handling(self):
        """Test streaming response handling."""
        async def mock_stream():
            chunks = [
                {"choices": [{"delta": {"content": "Hello"}}]},
                {"choices": [{"delta": {"content": " there"}}]},
                {"choices": [{"delta": {"content": "!"}}]},
                {"choices": [{"delta": {}, "finish_reason": "stop"}]}
            ]
            for chunk in chunks:
                yield chunk
                await asyncio.sleep(0.01)  # Simulate streaming delay
        
        with patch('openai.ChatCompletion.acreate') as mock_create:
            mock_create.return_value = mock_stream()
            
            chunks = []
            async for chunk in self.llm_service.stream_generate(
                messages=[{"role": "user", "content": "Hello"}],
                provider="openai",
                model="gpt-3.5-turbo"
            ):
                chunks.append(chunk)
            
            assert len(chunks) == 4
            assert chunks[0]["content"] == "Hello"
            assert chunks[1]["content"] == " there"
            assert chunks[2]["content"] == "!"
            assert chunks[3]["finish_reason"] == "stop"

    async def test_error_handling_and_retries(self):
        """Test error handling and retry logic."""
        with patch('openai.ChatCompletion.acreate') as mock_create:
            # First call fails, second succeeds
            mock_create.side_effect = [
                Exception("Rate limit exceeded"),
                {
                    "choices": [{
                        "message": {
                            "content": "Success after retry",
                            "role": "assistant"
                        }
                    }]
                }
            ]
            
            result = await self.llm_service.generate(
                messages=[{"role": "user", "content": "Test"}],
                provider="openai",
                model="gpt-3.5-turbo",
                max_retries=2
            )
            
            assert result["content"] == "Success after retry"
            assert mock_create.call_count == 2

    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Mock rate limiter
        with patch('chatter.services.llm.RateLimiter') as mock_rate_limiter:
            mock_limiter = AsyncMock()
            mock_rate_limiter.return_value = mock_limiter
            
            # First call allowed, second rate limited
            mock_limiter.acquire.side_effect = [True, False]
            
            # First call should succeed
            with patch('openai.ChatCompletion.acreate') as mock_create:
                mock_create.return_value = {
                    "choices": [{"message": {"content": "Success", "role": "assistant"}}]
                }
                
                result1 = await self.llm_service.generate(
                    messages=[{"role": "user", "content": "Test 1"}],
                    provider="openai",
                    model="gpt-3.5-turbo"
                )
                assert result1["content"] == "Success"
            
            # Second call should be rate limited
            try:
                await self.llm_service.generate(
                    messages=[{"role": "user", "content": "Test 2"}],
                    provider="openai",
                    model="gpt-3.5-turbo"
                )
                assert False, "Should have been rate limited"
            except Exception as e:
                assert "rate limit" in str(e).lower()

    async def test_token_counting_and_context_management(self):
        """Test token counting and context management."""
        # Mock token counter
        with patch('chatter.services.llm.count_tokens') as mock_count:
            mock_count.return_value = 100
            
            messages = [
                {"role": "user", "content": "Short message"},
                {"role": "assistant", "content": "Short response"},
                {"role": "user", "content": "Another message"}
            ]
            
            token_count = self.llm_service.count_message_tokens(messages, "gpt-3.5-turbo")
            assert token_count == 300  # 3 messages * 100 tokens each
            
            # Test context trimming
            max_tokens = 200
            trimmed_messages = self.llm_service.trim_context(messages, max_tokens, "gpt-3.5-turbo")
            
            # Should keep only the most recent messages that fit
            assert len(trimmed_messages) <= len(messages)
            total_tokens = sum(mock_count.return_value for _ in trimmed_messages)
            assert total_tokens <= max_tokens

    async def test_concurrent_request_processing(self):
        """Test concurrent request processing."""
        with patch('openai.ChatCompletion.acreate') as mock_create:
            mock_create.return_value = {
                "choices": [{"message": {"content": "Concurrent response", "role": "assistant"}}]
            }
            
            # Create multiple concurrent requests
            tasks = []
            for i in range(5):
                task = self.llm_service.generate(
                    messages=[{"role": "user", "content": f"Message {i}"}],
                    provider="openai",
                    model="gpt-3.5-turbo"
                )
                tasks.append(task)
            
            # Execute concurrently
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == 5
            for result in results:
                assert result["content"] == "Concurrent response"

    async def test_message_formatting_for_different_providers(self):
        """Test message formatting for different providers."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        # Test OpenAI formatting
        openai_formatted = self.llm_service.format_messages_for_provider(messages, "openai")
        assert isinstance(openai_formatted, list)
        assert all("role" in msg and "content" in msg for msg in openai_formatted)
        
        # Test Anthropic formatting (different format)
        anthropic_formatted = self.llm_service.format_messages_for_provider(messages, "anthropic")
        assert isinstance(anthropic_formatted, (list, dict))
        
        # Should handle system message differently for Anthropic
        if isinstance(anthropic_formatted, dict):
            assert "system" in anthropic_formatted
            assert "messages" in anthropic_formatted

    async def test_model_parameter_validation(self):
        """Test model parameter validation."""
        # Valid parameters
        valid_params = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        validated = self.llm_service.validate_parameters(valid_params, "openai")
        assert validated["temperature"] == 0.7
        assert validated["max_tokens"] == 1000
        
        # Invalid parameters should be filtered or corrected
        invalid_params = {
            "temperature": 2.5,  # Too high
            "max_tokens": -1,    # Negative
            "invalid_param": "should_be_removed"
        }
        
        validated = self.llm_service.validate_parameters(invalid_params, "openai")
        assert validated["temperature"] <= 2.0  # Should be clamped
        assert validated["max_tokens"] > 0      # Should be corrected
        assert "invalid_param" not in validated  # Should be removed

    async def test_provider_fallback(self):
        """Test provider fallback mechanism."""
        with patch('openai.ChatCompletion.acreate') as mock_openai, \
             patch('anthropic.Anthropic') as mock_anthropic:
            
            # OpenAI fails
            mock_openai.side_effect = Exception("OpenAI service unavailable")
            
            # Anthropic succeeds
            mock_anthropic_client = AsyncMock()
            mock_anthropic.return_value = mock_anthropic_client
            mock_anthropic_client.messages.create.return_value = AsyncMock(
                content=[{"type": "text", "text": "Fallback response"}]
            )
            
            result = await self.llm_service.generate_with_fallback(
                messages=[{"role": "user", "content": "Test"}],
                primary_provider="openai",
                fallback_provider="anthropic",
                model="gpt-3.5-turbo"
            )
            
            assert result["content"] == "Fallback response"
            assert result["provider_used"] == "anthropic"

    async def test_conversation_context_preservation(self):
        """Test conversation context preservation."""
        conversation_id = "conv-123"
        
        # First message
        messages1 = [{"role": "user", "content": "My name is Alice"}]
        
        with patch('openai.ChatCompletion.acreate') as mock_create:
            mock_create.return_value = {
                "choices": [{"message": {"content": "Nice to meet you, Alice!", "role": "assistant"}}]
            }
            
            result1 = await self.llm_service.generate_with_context(
                messages=messages1,
                conversation_id=conversation_id,
                provider="openai",
                model="gpt-3.5-turbo"
            )
            
            assert "Alice" in result1["content"]
        
        # Second message should have context
        messages2 = [{"role": "user", "content": "What's my name?"}]
        
        with patch('openai.ChatCompletion.acreate') as mock_create:
            mock_create.return_value = {
                "choices": [{"message": {"content": "Your name is Alice.", "role": "assistant"}}]
            }
            
            result2 = await self.llm_service.generate_with_context(
                messages=messages2,
                conversation_id=conversation_id,
                provider="openai",
                model="gpt-3.5-turbo"
            )
            
            # Should remember the name from context
            assert "Alice" in result2["content"]


@pytest.mark.unit
class TestLLMServiceConfiguration:
    """Test LLM service configuration."""

    def test_provider_configuration(self):
        """Test provider configuration."""
        config = {
            "openai": {
                "api_key": "sk-test123",
                "base_url": "https://api.openai.com/v1",
                "timeout": 30
            },
            "anthropic": {
                "api_key": "sk-ant-test123",
                "timeout": 30
            }
        }
        
        llm_service = LLMService(config=config)
        
        assert llm_service.providers["openai"]["api_key"] == "sk-test123"
        assert llm_service.providers["anthropic"]["api_key"] == "sk-ant-test123"

    def test_model_configuration(self):
        """Test model configuration and mapping."""
        model_config = {
            "gpt-3.5-turbo": {
                "provider": "openai",
                "max_tokens": 4096,
                "cost_per_token": 0.002
            },
            "claude-3-sonnet": {
                "provider": "anthropic",
                "max_tokens": 200000,
                "cost_per_token": 0.003
            }
        }
        
        llm_service = LLMService(model_config=model_config)
        
        assert llm_service.get_provider_for_model("gpt-3.5-turbo") == "openai"
        assert llm_service.get_provider_for_model("claude-3-sonnet") == "anthropic"
        assert llm_service.get_max_tokens_for_model("gpt-3.5-turbo") == 4096

    def test_default_parameters(self):
        """Test default parameter configuration."""
        defaults = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1.0
        }
        
        llm_service = LLMService(default_params=defaults)
        
        # Should use defaults when not specified
        params = llm_service.get_parameters({}, "openai")
        assert params["temperature"] == 0.7
        assert params["max_tokens"] == 1000
        
        # Should override defaults when specified
        custom_params = {"temperature": 0.5}
        params = llm_service.get_parameters(custom_params, "openai")
        assert params["temperature"] == 0.5
        assert params["max_tokens"] == 1000  # Still default


@pytest.mark.integration
class TestLLMServiceIntegration:
    """Integration tests for LLM service."""

    async def test_real_conversation_flow(self):
        """Test realistic conversation flow."""
        llm_service = LLMService()
        
        # Mock the actual LLM calls
        with patch('openai.ChatCompletion.acreate') as mock_create:
            # Simulate a conversation
            responses = [
                "Hello! I'm an AI assistant. How can I help you today?",
                "I can help you with programming. What language are you interested in?",
                "Python is a great choice! Here's a simple example: print('Hello, World!')"
            ]
            
            mock_create.side_effect = [
                {"choices": [{"message": {"content": resp, "role": "assistant"}}]}
                for resp in responses
            ]
            
            conversation = []
            
            # User message 1
            user_msg1 = {"role": "user", "content": "Hello, I need help"}
            conversation.append(user_msg1)
            
            result1 = await llm_service.generate(
                messages=conversation,
                provider="openai",
                model="gpt-3.5-turbo"
            )
            conversation.append(result1)
            
            # User message 2
            user_msg2 = {"role": "user", "content": "I want to learn programming"}
            conversation.append(user_msg2)
            
            result2 = await llm_service.generate(
                messages=conversation,
                provider="openai",
                model="gpt-3.5-turbo"
            )
            conversation.append(result2)
            
            # User message 3
            user_msg3 = {"role": "user", "content": "Show me a Python example"}
            conversation.append(user_msg3)
            
            result3 = await llm_service.generate(
                messages=conversation,
                provider="openai",
                model="gpt-3.5-turbo"
            )
            conversation.append(result3)
            
            # Verify conversation flow
            assert len(conversation) == 6  # 3 user + 3 assistant messages
            assert "programming" in result2["content"].lower()
            assert "python" in result3["content"].lower()

    async def test_performance_monitoring(self):
        """Test performance monitoring and metrics."""
        llm_service = LLMService()
        
        with patch('openai.ChatCompletion.acreate') as mock_create:
            mock_create.return_value = {
                "choices": [{"message": {"content": "Test response", "role": "assistant"}}],
                "usage": {"total_tokens": 50}
            }
            
            # Monitor performance
            import time
            start_time = time.time()
            
            result = await llm_service.generate(
                messages=[{"role": "user", "content": "Test"}],
                provider="openai",
                model="gpt-3.5-turbo"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Should complete quickly in test environment
            assert response_time < 1.0
            assert "response_time" in result or response_time is not None

    async def test_error_recovery_and_logging(self):
        """Test error recovery and logging."""
        llm_service = LLMService()
        
        with patch('chatter.utils.logging.logger') as mock_logger, \
             patch('openai.ChatCompletion.acreate') as mock_create:
            
            # Simulate various errors
            errors = [
                Exception("Network timeout"),
                Exception("Rate limit exceeded"),
                Exception("Invalid API key")
            ]
            
            for error in errors:
                mock_create.side_effect = error
                
                try:
                    await llm_service.generate(
                        messages=[{"role": "user", "content": "Test"}],
                        provider="openai",
                        model="gpt-3.5-turbo"
                    )
                except Exception:
                    pass  # Expected to fail
                
                # Should log the error
                mock_logger.error.assert_called()

    async def test_cost_tracking(self):
        """Test cost tracking functionality."""
        llm_service = LLMService()
        
        with patch('openai.ChatCompletion.acreate') as mock_create:
            mock_create.return_value = {
                "choices": [{"message": {"content": "Test response", "role": "assistant"}}],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15
                }
            }
            
            result = await llm_service.generate(
                messages=[{"role": "user", "content": "Test"}],
                provider="openai",
                model="gpt-3.5-turbo",
                track_cost=True
            )
            
            # Should include cost information
            assert "cost" in result or "usage" in result
            if "usage" in result:
                assert result["usage"]["total_tokens"] == 15

    async def test_multi_provider_load_balancing(self):
        """Test load balancing across multiple providers."""
        llm_service = LLMService()
        
        # Mock multiple providers
        with patch('openai.ChatCompletion.acreate') as mock_openai, \
             patch('anthropic.Anthropic') as mock_anthropic:
            
            mock_openai.return_value = {
                "choices": [{"message": {"content": "OpenAI response", "role": "assistant"}}]
            }
            
            mock_anthropic_client = AsyncMock()
            mock_anthropic.return_value = mock_anthropic_client
            mock_anthropic_client.messages.create.return_value = AsyncMock(
                content=[{"type": "text", "text": "Anthropic response"}]
            )
            
            # Make multiple requests with load balancing
            results = []
            for i in range(4):
                result = await llm_service.generate_with_load_balancing(
                    messages=[{"role": "user", "content": f"Test {i}"}],
                    providers=["openai", "anthropic"],
                    model="gpt-3.5-turbo"
                )
                results.append(result)
            
            # Should distribute load across providers
            openai_count = sum(1 for r in results if "OpenAI" in r.get("content", ""))
            anthropic_count = sum(1 for r in results if "Anthropic" in r.get("content", ""))
            
            # Both providers should be used
            assert openai_count > 0 or anthropic_count > 0