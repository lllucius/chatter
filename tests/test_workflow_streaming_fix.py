"""Test to verify the workflow streaming fix."""

from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage

from chatter.core.workflow_executors import (
    FullWorkflowExecutor,
    PlainWorkflowExecutor,
    RAGWorkflowExecutor,
    ToolsWorkflowExecutor,
)
from chatter.models.conversation import Conversation
from chatter.schemas.chat import ChatRequest


class MockWorkflow:
    """Mock workflow that simulates proper LangGraph event structure."""

    def __init__(self, response_content="Hello world!"):
        self.response_content = response_content

    async def astream(self, state, config):
        """Simulate LangGraph streaming with proper event structure."""
        # First event: memory management node (returns None)
        yield {'manage_memory': None}

        # Second event: call_model node (returns messages)
        yield {
            'call_model': {
                'messages': [AIMessage(content=self.response_content)]
            }
        }


@pytest.fixture
def mock_services():
    """Create mock services for testing."""
    llm_service = AsyncMock()
    message_service = AsyncMock()
    template_manager = MagicMock()

    # Mock message service
    mock_message = MagicMock()
    mock_message.id = "msg_123"
    message_service.add_message_to_conversation = AsyncMock(
        return_value=mock_message
    )
    message_service.get_recent_messages = AsyncMock(return_value=[])
    message_service.update_message_content = AsyncMock()

    return llm_service, message_service, template_manager


@pytest.fixture
def conversation():
    """Create test conversation."""
    conv = MagicMock(spec=Conversation)
    conv.id = "conv_123"
    conv.user_id = "user_123"
    conv.workspace_id = (
        "workspace_123"  # Add workspace_id for RAG/Tools/Full workflows
    )
    return conv


@pytest.fixture
def chat_request():
    """Create test chat request."""
    return ChatRequest(
        message="Hello test",
        workflow="plain",
    )


class TestWorkflowStreamingFix:
    """Test that workflow streaming now processes all event types correctly."""

    @pytest.mark.asyncio
    async def test_plain_workflow_streaming_processes_all_events(
        self, mock_services, conversation, chat_request
    ):
        """Test PlainWorkflowExecutor processes both manage_memory and call_model events."""
        llm_service, message_service, template_manager = mock_services

        # Mock workflow creation
        llm_service.create_langgraph_workflow = AsyncMock(
            return_value=MockWorkflow("Test response")
        )

        # Create executor
        executor = PlainWorkflowExecutor(
            llm_service, message_service, template_manager
        )

        # Execute streaming
        chunks = []
        async for chunk in executor.execute_streaming(
            conversation, chat_request, "corr_123", "user_123"
        ):
            chunks.append(chunk)

        # Verify we got the expected chunks
        start_chunks = [c for c in chunks if c.type == "start"]
        token_chunks = [c for c in chunks if c.type == "token"]
        complete_chunks = [c for c in chunks if c.type == "complete"]

        assert (
            len(start_chunks) == 1
        ), "Should have exactly one start chunk"
        assert (
            len(token_chunks) >= 1
        ), "Should have at least one token chunk"
        assert (
            len(complete_chunks) == 1
        ), "Should have exactly one complete chunk"

        # Verify content
        all_content = ''.join(c.content for c in token_chunks)
        assert (
            "Test response" in all_content
        ), "Should contain the response content"

    @pytest.mark.asyncio
    async def test_rag_workflow_streaming_processes_all_events(
        self, mock_services, conversation, chat_request
    ):
        """Test RAGWorkflowExecutor processes events correctly."""
        llm_service, message_service, template_manager = mock_services

        # Mock workflow creation
        llm_service.create_langgraph_workflow = AsyncMock(
            return_value=MockWorkflow("RAG response")
        )

        # Create executor
        executor = RAGWorkflowExecutor(
            llm_service, message_service, template_manager
        )

        # Mock the workflow manager dependency
        with mock.patch(
            'chatter.core.dependencies.get_workflow_manager'
        ) as mock_get_manager:
            mock_workflow_manager = MagicMock()
            mock_workflow_manager.get_retriever.return_value = (
                None  # No retriever for this test
            )
            mock_get_manager.return_value = mock_workflow_manager

            # Execute streaming
            chunks = []
            async for chunk in executor.execute_streaming(
                conversation, chat_request, "corr_123", "user_123"
            ):
                chunks.append(chunk)

            # Verify we got streaming chunks
            token_chunks = [c for c in chunks if c.type == "token"]
            assert (
                len(token_chunks) >= 1
            ), "RAG executor should produce token chunks"

            # Verify content
            all_content = ''.join(c.content for c in token_chunks)
            assert (
                "RAG response" in all_content
            ), "Should contain the RAG response content"

    @pytest.mark.asyncio
    async def test_tools_workflow_streaming_processes_all_events(
        self, mock_services, conversation, chat_request
    ):
        """Test ToolsWorkflowExecutor processes events correctly."""
        llm_service, message_service, template_manager = mock_services

        # Mock workflow creation
        llm_service.create_langgraph_workflow = AsyncMock(
            return_value=MockWorkflow("Tools response")
        )

        # Create executor
        executor = ToolsWorkflowExecutor(
            llm_service, message_service, template_manager
        )

        # Mock the workflow manager dependency
        with mock.patch(
            'chatter.core.dependencies.get_workflow_manager'
        ) as mock_get_manager:
            mock_workflow_manager = MagicMock()
            mock_workflow_manager.get_tools.return_value = (
                []
            )  # No tools for this test
            mock_get_manager.return_value = mock_workflow_manager

            # Execute streaming
            chunks = []
            async for chunk in executor.execute_streaming(
                conversation, chat_request, "corr_123", "user_123"
            ):
                chunks.append(chunk)

            # Verify we got streaming chunks
            token_chunks = [c for c in chunks if c.type == "token"]
            assert (
                len(token_chunks) >= 1
            ), "Tools executor should produce token chunks"

            # Verify content
            all_content = ''.join(c.content for c in token_chunks)
            assert (
                "Tools response" in all_content
            ), "Should contain the tools response content"

    @pytest.mark.asyncio
    async def test_full_workflow_streaming_processes_all_events(
        self, mock_services, conversation, chat_request
    ):
        """Test FullWorkflowExecutor processes events correctly."""
        llm_service, message_service, template_manager = mock_services

        # Mock workflow creation
        llm_service.create_langgraph_workflow = AsyncMock(
            return_value=MockWorkflow("Full response")
        )

        # Create executor
        executor = FullWorkflowExecutor(
            llm_service, message_service, template_manager
        )

        # Mock the workflow manager dependency
        with mock.patch(
            'chatter.core.dependencies.get_workflow_manager'
        ) as mock_get_manager:
            mock_workflow_manager = MagicMock()
            mock_workflow_manager.get_tools.return_value = (
                []
            )  # No tools for this test
            mock_workflow_manager.get_retriever.return_value = (
                None  # No retriever for this test
            )
            mock_get_manager.return_value = mock_workflow_manager

            # Execute streaming
            chunks = []
            async for chunk in executor.execute_streaming(
                conversation, chat_request, "corr_123", "user_123"
            ):
                chunks.append(chunk)

            # Verify we got streaming chunks
            token_chunks = [c for c in chunks if c.type == "token"]
            assert (
                len(token_chunks) >= 1
            ), "Full executor should produce token chunks"

            # Verify content
            all_content = ''.join(c.content for c in token_chunks)
            assert (
                "Full response" in all_content
            ), "Should contain the full response content"

    @pytest.mark.asyncio
    async def test_workflow_handles_multiple_message_events(
        self, mock_services, conversation, chat_request
    ):
        """Test that workflow handles multiple message events correctly."""
        llm_service, message_service, template_manager = mock_services

        class MultiMessageWorkflow:
            async def astream(self, state, config):
                yield {'manage_memory': None}
                yield {
                    'call_model': {
                        'messages': [AIMessage(content="First part")]
                    }
                }
                yield {
                    'call_model': {
                        'messages': [
                            AIMessage(content="First part Second part")
                        ]
                    }
                }
                yield {
                    'call_model': {
                        'messages': [
                            AIMessage(
                                content="First part Second part Third part"
                            )
                        ]
                    }
                }

        llm_service.create_langgraph_workflow = AsyncMock(
            return_value=MultiMessageWorkflow()
        )

        # Create executor
        executor = PlainWorkflowExecutor(
            llm_service, message_service, template_manager
        )

        # Execute streaming
        chunks = []
        async for chunk in executor.execute_streaming(
            conversation, chat_request, "corr_123", "user_123"
        ):
            chunks.append(chunk)

        # Should get incremental token chunks
        token_chunks = [c for c in chunks if c.type == "token"]
        assert (
            len(token_chunks) >= 2
        ), "Should get multiple token chunks for incremental content"

        # Verify incremental content
        token_contents = [c.content for c in token_chunks]
        assert (
            "First part" in token_contents[0]
            or " Second part" in token_contents
        ), "Should get incremental content"

    @pytest.mark.asyncio
    async def test_workflow_ignores_non_message_events(
        self, mock_services, conversation, chat_request
    ):
        """Test that workflow correctly ignores events without messages."""
        llm_service, message_service, template_manager = mock_services

        class MixedEventWorkflow:
            async def astream(self, state, config):
                yield {'manage_memory': None}
                yield {'retrieve_context': {'context': 'Some context'}}
                yield {'other_node': {'some_data': 'data'}}
                yield {
                    'call_model': {
                        'messages': [
                            AIMessage(content="Final response")
                        ]
                    }
                }

        llm_service.create_langgraph_workflow = AsyncMock(
            return_value=MixedEventWorkflow()
        )

        # Create executor
        executor = PlainWorkflowExecutor(
            llm_service, message_service, template_manager
        )

        # Execute streaming
        chunks = []
        async for chunk in executor.execute_streaming(
            conversation, chat_request, "corr_123", "user_123"
        ):
            chunks.append(chunk)

        # Should only get chunks from the call_model event
        token_chunks = [c for c in chunks if c.type == "token"]
        assert (
            len(token_chunks) >= 1
        ), "Should get token chunks from call_model event"

        # Verify only the call_model content is streamed
        all_content = ''.join(c.content for c in token_chunks)
        assert (
            "Final response" in all_content
        ), "Should contain content from call_model event"
        assert (
            "Some context" not in all_content
        ), "Should not contain content from other events"
