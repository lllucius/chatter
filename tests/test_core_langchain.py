"""Tests for LangChain integration and orchestration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

from chatter.core.langchain import LangChainOrchestrator, orchestrator


@pytest.mark.unit
class TestLangChainOrchestrator:
    """Test LangChainOrchestrator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = LangChainOrchestrator()
        self.mock_llm = MagicMock(spec=BaseChatModel)

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        # Act & Assert
        assert isinstance(self.orchestrator, LangChainOrchestrator)

    @patch.dict('os.environ', {}, clear=True)
    @patch('chatter.core.langchain.settings')
    def test_setup_tracing_enabled(self, mock_settings):
        """Test LangSmith tracing setup when enabled."""
        # Arrange
        mock_settings.langchain_tracing_v2 = True
        mock_settings.langchain_api_key = "test-api-key"
        mock_settings.langchain_project = "test-project"
        mock_settings.langchain_endpoint = "https://test-endpoint.com"

        import os

        # Act
        self.orchestrator.setup_tracing()

        # Assert
        assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"
        assert os.environ.get("LANGCHAIN_API_KEY") == "test-api-key"
        assert os.environ.get("LANGCHAIN_PROJECT") == "test-project"
        assert os.environ.get("LANGCHAIN_ENDPOINT") == "https://test-endpoint.com"

    @patch('chatter.core.langchain.settings')
    def test_setup_tracing_disabled(self, mock_settings):
        """Test LangSmith tracing setup when disabled."""
        # Arrange
        mock_settings.langchain_tracing_v2 = False

        # Act
        self.orchestrator.setup_tracing()

        # Assert - No environment variables should be set
        import os
        assert os.environ.get("LANGCHAIN_TRACING_V2") != "true"

    def test_create_chat_chain_basic(self):
        """Test creating basic chat chain."""
        # Act
        chain = self.orchestrator.create_chat_chain(self.mock_llm)

        # Assert
        assert isinstance(chain, Runnable)

    def test_create_chat_chain_with_system_message(self):
        """Test creating chat chain with system message."""
        # Arrange
        system_message = "You are a helpful assistant."

        # Act
        chain = self.orchestrator.create_chat_chain(
            self.mock_llm, system_message=system_message
        )

        # Assert
        assert isinstance(chain, Runnable)

    def test_create_chat_chain_without_history(self):
        """Test creating chat chain without history."""
        # Act
        chain = self.orchestrator.create_chat_chain(
            self.mock_llm, include_history=False
        )

        # Assert
        assert isinstance(chain, Runnable)

    def test_create_rag_chain(self):
        """Test creating RAG chain."""
        # Arrange
        mock_retriever = MagicMock()

        # Act
        chain = self.orchestrator.create_rag_chain(
            self.mock_llm, mock_retriever
        )

        # Assert
        assert isinstance(chain, Runnable)

    def test_create_rag_chain_custom_system_message(self):
        """Test creating RAG chain with custom system message."""
        # Arrange
        mock_retriever = MagicMock()
        custom_system = "You are a specialized AI assistant. {context}"

        # Act
        chain = self.orchestrator.create_rag_chain(
            self.mock_llm, mock_retriever, system_message=custom_system
        )

        # Assert
        assert isinstance(chain, Runnable)

    def test_create_conversational_rag_chain(self):
        """Test creating conversational RAG chain."""
        # Arrange
        mock_retriever = MagicMock()

        # Act
        chain = self.orchestrator.create_conversational_rag_chain(
            self.mock_llm, mock_retriever
        )

        # Assert
        assert isinstance(chain, Runnable)

    def test_create_conversational_rag_chain_custom_system_message(self):
        """Test creating conversational RAG chain with custom system message."""
        # Arrange
        mock_retriever = MagicMock()
        custom_system = "Custom contextualization prompt."

        # Act
        chain = self.orchestrator.create_conversational_rag_chain(
            self.mock_llm, mock_retriever, system_message=custom_system
        )

        # Assert
        assert isinstance(chain, Runnable)

    @pytest.mark.asyncio
    async def test_run_chain_with_callback_openai(self):
        """Test running chain with OpenAI callback tracking."""
        # Arrange
        mock_chain = AsyncMock(spec=Runnable)
        mock_chain.ainvoke.return_value = "Test response"
        inputs = {"input": "Test input"}

        with patch('chatter.core.langchain.get_openai_callback') as mock_callback:
            mock_cb = MagicMock()
            mock_cb.total_tokens = 100
            mock_cb.prompt_tokens = 80
            mock_cb.completion_tokens = 20
            mock_cb.total_cost = 0.05
            mock_callback.return_value.__enter__.return_value = mock_cb

            # Act
            result = await self.orchestrator.run_chain_with_callback(
                mock_chain, inputs, provider_name="openai"
            )

            # Assert
            assert result["response"] == "Test response"
            assert result["usage"]["total_tokens"] == 100
            assert result["usage"]["prompt_tokens"] == 80
            assert result["usage"]["completion_tokens"] == 20
            assert result["usage"]["total_cost"] == 0.05
            mock_chain.ainvoke.assert_called_once_with(inputs)

    @pytest.mark.asyncio
    async def test_run_chain_with_callback_other_provider(self):
        """Test running chain with other provider (no specific callback)."""
        # Arrange
        mock_chain = AsyncMock(spec=Runnable)
        mock_chain.ainvoke.return_value = "Test response"
        inputs = {"input": "Test input"}

        # Act
        result = await self.orchestrator.run_chain_with_callback(
            mock_chain, inputs, provider_name="anthropic"
        )

        # Assert
        assert result["response"] == "Test response"
        assert result["usage"]["provider"] == "anthropic"
        mock_chain.ainvoke.assert_called_once_with(inputs)

    @pytest.mark.asyncio
    async def test_run_chain_with_callback_error(self):
        """Test error handling in chain execution."""
        # Arrange
        mock_chain = AsyncMock(spec=Runnable)
        mock_chain.ainvoke.side_effect = Exception("Chain execution failed")
        inputs = {"input": "Test input"}

        # Act & Assert
        with pytest.raises(Exception, match="Chain execution failed"):
            await self.orchestrator.run_chain_with_callback(
                mock_chain, inputs, provider_name="openai"
            )

    def test_convert_messages_to_langchain(self):
        """Test converting API messages to LangChain format."""
        # Arrange
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]

        # Act
        langchain_messages = self.orchestrator.convert_messages_to_langchain(messages)

        # Assert
        assert len(langchain_messages) == 4
        assert isinstance(langchain_messages[0], SystemMessage)
        assert langchain_messages[0].content == "You are helpful."
        assert isinstance(langchain_messages[1], HumanMessage)
        assert langchain_messages[1].content == "Hello"
        assert isinstance(langchain_messages[2], AIMessage)
        assert langchain_messages[2].content == "Hi there!"
        assert isinstance(langchain_messages[3], HumanMessage)
        assert langchain_messages[3].content == "How are you?"

    def test_convert_messages_to_langchain_empty_content(self):
        """Test converting messages with empty content."""
        # Arrange
        messages = [
            {"role": "user"},  # Missing content
            {"role": "assistant", "content": ""}  # Empty content
        ]

        # Act
        langchain_messages = self.orchestrator.convert_messages_to_langchain(messages)

        # Assert
        assert len(langchain_messages) == 2
        assert isinstance(langchain_messages[0], HumanMessage)
        assert langchain_messages[0].content == ""
        assert isinstance(langchain_messages[1], AIMessage)
        assert langchain_messages[1].content == ""

    def test_convert_messages_to_langchain_unknown_role(self):
        """Test converting messages with unknown role defaults to human."""
        # Arrange
        messages = [
            {"role": "unknown", "content": "Test message"},
            {"role": "", "content": "Empty role message"}
        ]

        # Act
        langchain_messages = self.orchestrator.convert_messages_to_langchain(messages)

        # Assert
        assert len(langchain_messages) == 2
        assert isinstance(langchain_messages[0], HumanMessage)
        assert langchain_messages[0].content == "Test message"
        assert isinstance(langchain_messages[1], HumanMessage)
        assert langchain_messages[1].content == "Empty role message"

    def test_format_chat_history(self):
        """Test formatting chat history by filtering system messages."""
        # Arrange
        messages = [
            SystemMessage(content="You are helpful."),
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
            SystemMessage(content="Another system message"),
            HumanMessage(content="How are you?")
        ]

        # Act
        formatted_history = self.orchestrator.format_chat_history(messages)

        # Assert
        assert len(formatted_history) == 3  # Only non-system messages
        assert isinstance(formatted_history[0], HumanMessage)
        assert formatted_history[0].content == "Hello"
        assert isinstance(formatted_history[1], AIMessage)
        assert formatted_history[1].content == "Hi there!"
        assert isinstance(formatted_history[2], HumanMessage)
        assert formatted_history[2].content == "How are you?"

    def test_format_chat_history_empty(self):
        """Test formatting empty chat history."""
        # Arrange
        messages = []

        # Act
        formatted_history = self.orchestrator.format_chat_history(messages)

        # Assert
        assert len(formatted_history) == 0

    def test_format_chat_history_only_system_messages(self):
        """Test formatting chat history with only system messages."""
        # Arrange
        messages = [
            SystemMessage(content="System message 1"),
            SystemMessage(content="System message 2")
        ]

        # Act
        formatted_history = self.orchestrator.format_chat_history(messages)

        # Assert
        assert len(formatted_history) == 0


@pytest.mark.integration
class TestLangChainIntegration:
    """Integration tests for LangChain orchestrator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = LangChainOrchestrator()

    @pytest.mark.asyncio
    async def test_complete_rag_workflow(self):
        """Test complete RAG workflow with mocked components."""
        # Arrange
        mock_llm = AsyncMock(spec=BaseChatModel)
        mock_llm.ainvoke.return_value = MagicMock(content="RAG response")

        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Retrieved document content"
        mock_retriever.invoke.return_value = [mock_doc]

        # Create RAG chain
        rag_chain = self.orchestrator.create_rag_chain(mock_llm, mock_retriever)

        # Act
        with patch.object(mock_retriever, 'invoke', return_value=[mock_doc]):
            result = await self.orchestrator.run_chain_with_callback(
                rag_chain, {"input": "Test question"}, provider_name="test"
            )

        # Assert
        assert "response" in result
        assert "usage" in result
        assert result["usage"]["provider"] == "test"

    @pytest.mark.asyncio
    async def test_conversational_workflow(self):
        """Test conversational workflow with chat history."""
        # Arrange
        mock_llm = AsyncMock(spec=BaseChatModel)
        mock_llm.ainvoke.return_value = MagicMock(content="Conversational response")

        # Create chat chain
        chat_chain = self.orchestrator.create_chat_chain(
            mock_llm, 
            system_message="You are a helpful assistant.",
            include_history=True
        )

        # Prepare inputs with chat history
        inputs = {
            "input": "What did we discuss earlier?",
            "chat_history": [
                HumanMessage(content="Hello"),
                AIMessage(content="Hi there!")
            ]
        }

        # Act
        result = await self.orchestrator.run_chain_with_callback(
            chat_chain, inputs, provider_name="test"
        )

        # Assert
        assert "response" in result
        assert "usage" in result

    def test_message_conversion_round_trip(self):
        """Test converting messages to LangChain and formatting back."""
        # Arrange
        api_messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User message 1"},
            {"role": "assistant", "content": "Assistant response 1"},
            {"role": "user", "content": "User message 2"}
        ]

        # Act
        langchain_messages = self.orchestrator.convert_messages_to_langchain(api_messages)
        formatted_history = self.orchestrator.format_chat_history(langchain_messages)

        # Assert
        # Should have 3 messages after filtering out system message
        assert len(formatted_history) == 3
        assert formatted_history[0].content == "User message 1"
        assert formatted_history[1].content == "Assistant response 1"
        assert formatted_history[2].content == "User message 2"


def test_global_orchestrator_instance():
    """Test that global orchestrator instance is properly initialized."""
    # Assert
    assert isinstance(orchestrator, LangChainOrchestrator)
    assert orchestrator is not None