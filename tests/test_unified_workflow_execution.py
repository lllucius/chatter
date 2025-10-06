"""Tests for unified workflow execution service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chatter.services.unified_workflow_execution import (
    UnifiedWorkflowExecutionService,
)
from chatter.services.workflow_types import (
    ExecutionMode,
    WorkflowConfig,
    WorkflowInput,
    WorkflowSource,
    WorkflowSourceType,
)


@pytest.fixture
def mock_llm_service():
    """Mock LLM service."""
    return MagicMock()


@pytest.fixture
def mock_message_service():
    """Mock message service."""
    service = MagicMock()
    service.create_message = AsyncMock()
    service.get_messages = AsyncMock(return_value=[])
    return service


@pytest.fixture
def mock_session():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def unified_service(mock_llm_service, mock_message_service, mock_session):
    """Create unified workflow execution service."""
    return UnifiedWorkflowExecutionService(
        mock_llm_service, mock_message_service, mock_session
    )


@pytest.fixture
def sample_workflow_source():
    """Sample workflow source."""
    return WorkflowSource(
        source_type=WorkflowSourceType.TEMPLATE,
        source_id="test-template-id",
    )


@pytest.fixture
def sample_workflow_config():
    """Sample workflow configuration."""
    return WorkflowConfig(
        provider="openai",
        model="gpt-4",
        temperature=0.7,
        max_tokens=2000,
        debug_mode=False,
    )


@pytest.fixture
def sample_workflow_input():
    """Sample workflow input."""
    return WorkflowInput(
        message="Test message",
        conversation_id="test-conv-id",
    )


class TestUnifiedWorkflowExecutionService:
    """Test cases for UnifiedWorkflowExecutionService."""

    def test_init(self, unified_service):
        """Test service initialization."""
        assert unified_service.llm_service is not None
        assert unified_service.message_service is not None
        assert unified_service.session is not None
        assert unified_service.preparation_service is not None
        assert unified_service.result_processor is not None

    @pytest.mark.asyncio
    async def test_execute_workflow_with_template(
        self,
        unified_service,
        sample_workflow_source,
        sample_workflow_config,
        sample_workflow_input,
    ):
        """Test workflow execution with template source."""
        # Mock dependencies
        with patch.object(
            unified_service, "_get_or_create_conversation", AsyncMock()
        ) as mock_get_conv:
            mock_conversation = MagicMock()
            mock_conversation.id = "test-conv-id"
            mock_get_conv.return_value = mock_conversation

            with patch.object(
                unified_service.preparation_service,
                "prepare_workflow",
                AsyncMock(),
            ) as mock_prepare:
                mock_prepared = MagicMock()
                mock_prepared.workflow = MagicMock()
                mock_prepare.return_value = mock_prepared

                with patch.object(
                    unified_service, "_get_conversation_messages", AsyncMock()
                ) as mock_get_msgs:
                    mock_get_msgs.return_value = []

                    with patch(
                        "chatter.services.unified_workflow_execution.workflow_manager.run_workflow",
                        AsyncMock(),
                    ) as mock_run:
                        mock_run.return_value = {"messages": []}

                        with patch.object(
                            unified_service.result_processor,
                            "process_result",
                            AsyncMock(),
                        ) as mock_process:
                            mock_result = MagicMock()
                            mock_result.execution_time_ms = 100
                            mock_process.return_value = mock_result

                            # Execute
                            result = await unified_service.execute_workflow(
                                workflow_input=sample_workflow_input,
                                workflow_source=sample_workflow_source,
                                workflow_config=sample_workflow_config,
                                user_id="test-user-id",
                            )

                            # Verify
                            assert result is not None
                            mock_prepare.assert_called_once()
                            mock_run.assert_called_once()
                            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_workflow_streaming(
        self,
        unified_service,
        sample_workflow_source,
        sample_workflow_config,
        sample_workflow_input,
    ):
        """Test workflow streaming execution."""
        # Mock dependencies
        with patch.object(
            unified_service, "_get_or_create_conversation", AsyncMock()
        ) as mock_get_conv:
            mock_conversation = MagicMock()
            mock_conversation.id = "test-conv-id"
            mock_get_conv.return_value = mock_conversation

            with patch.object(
                unified_service.preparation_service,
                "prepare_workflow",
                AsyncMock(),
            ) as mock_prepare:
                mock_prepared = MagicMock()
                mock_prepared.workflow = MagicMock()
                mock_prepare.return_value = mock_prepared

                with patch.object(
                    unified_service, "_get_conversation_messages", AsyncMock()
                ) as mock_get_msgs:
                    mock_get_msgs.return_value = []

                    async def mock_stream(*args, **kwargs):
                        """Mock stream workflow."""
                        # Simulate streaming events
                        from langchain_core.messages import AIMessage

                        yield {"messages": [AIMessage(content="Hello")]}
                        yield {"messages": [AIMessage(content="Hello world")]}

                    with patch(
                        "chatter.services.unified_workflow_execution.workflow_manager.stream_workflow",
                        mock_stream,
                    ):
                        # Execute
                        chunks = []
                        async for chunk in unified_service.execute_workflow_streaming(
                            workflow_input=sample_workflow_input,
                            workflow_source=sample_workflow_source,
                            workflow_config=sample_workflow_config,
                            user_id="test-user-id",
                        ):
                            chunks.append(chunk)

                        # Verify
                        assert len(chunks) > 0
                        # Should have content chunks + done marker
                        assert any(chunk.type == "done" for chunk in chunks)

    @pytest.mark.asyncio
    async def test_execute_workflow_definition(
        self, unified_service
    ):
        """Test workflow definition execution."""
        # Mock definition
        mock_definition = MagicMock()
        mock_definition.id = "test-def-id"

        # Mock execute_workflow
        with patch.object(
            unified_service, "execute_workflow", AsyncMock()
        ) as mock_execute:
            mock_result = MagicMock()
            mock_result.to_execution_response.return_value = {
                "status": "completed"
            }
            mock_execute.return_value = mock_result

            # Execute
            result = await unified_service.execute_workflow_definition(
                definition=mock_definition,
                input_data={"message": "Test"},
                user_id="test-user-id",
                debug_mode=False,
            )

            # Verify
            assert result == {"status": "completed"}
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversation_messages(
        self, unified_service, mock_message_service
    ):
        """Test getting conversation messages."""
        # Mock conversation
        mock_conversation = MagicMock()
        mock_conversation.id = "test-conv-id"

        # Mock messages
        mock_msg1 = MagicMock()
        mock_msg1.role = "user"
        mock_msg1.content = "Hello"

        mock_msg2 = MagicMock()
        mock_msg2.role = "assistant"
        mock_msg2.content = "Hi there"

        mock_message_service.get_messages.return_value = [mock_msg1, mock_msg2]

        # Execute
        messages = await unified_service._get_conversation_messages(
            mock_conversation
        )

        # Verify
        assert len(messages) == 2
        mock_message_service.get_messages.assert_called_once_with(
            conversation_id="test-conv-id"
        )

    @pytest.mark.asyncio
    async def test_get_or_create_conversation_existing(
        self, unified_service
    ):
        """Test getting existing conversation."""
        with patch(
            "chatter.services.unified_workflow_execution.ConversationService"
        ) as mock_conv_service_class:
            mock_conv_service = MagicMock()
            mock_conversation = MagicMock()
            mock_conversation.id = "existing-conv-id"
            mock_conv_service.get_conversation = AsyncMock(
                return_value=mock_conversation
            )
            mock_conv_service_class.return_value = mock_conv_service

            # Execute
            result = await unified_service._get_or_create_conversation(
                user_id="test-user-id",
                conversation_id="existing-conv-id",
            )

            # Verify
            assert result.id == "existing-conv-id"

    @pytest.mark.asyncio
    async def test_get_or_create_conversation_new(
        self, unified_service
    ):
        """Test creating new conversation."""
        with patch(
            "chatter.services.unified_workflow_execution.ConversationService"
        ) as mock_conv_service_class:
            mock_conv_service = MagicMock()
            mock_conversation = MagicMock()
            mock_conversation.id = "new-conv-id"
            mock_conv_service.get_conversation = AsyncMock(return_value=None)
            mock_conv_service.create_conversation = AsyncMock(
                return_value=mock_conversation
            )
            mock_conv_service_class.return_value = mock_conv_service

            # Execute
            result = await unified_service._get_or_create_conversation(
                user_id="test-user-id",
                conversation_id=None,
            )

            # Verify
            assert result.id == "new-conv-id"
            mock_conv_service.create_conversation.assert_called_once()
