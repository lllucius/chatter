"""Tests for workflow result processor."""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import AIMessage

from chatter.models.conversation import MessageRole
from chatter.services.workflow_result_processor import WorkflowResultProcessor
from chatter.services.workflow_types import ExecutionMode, WorkflowResult


@pytest.fixture
def mock_session():
    """Mock database session."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def result_processor(mock_session):
    """Create result processor with mock session."""
    return WorkflowResultProcessor(mock_session)


def test_extract_ai_response_with_message():
    """Test extracting AI response from workflow result."""
    processor = WorkflowResultProcessor(MagicMock())
    
    ai_msg = AIMessage(content="Test response")
    workflow_result = {
        "messages": [
            MagicMock(content="User message"),
            ai_msg,
        ]
    }
    
    result = processor._extract_ai_response(workflow_result)
    assert result == ai_msg
    assert result.content == "Test response"


def test_extract_ai_response_no_message():
    """Test extracting AI response when no messages present."""
    processor = WorkflowResultProcessor(MagicMock())
    
    workflow_result = {"messages": []}
    
    result = processor._extract_ai_response(workflow_result)
    assert isinstance(result, AIMessage)
    assert result.content == "No response generated"


def test_extract_ai_response_multiple_messages():
    """Test extracting last AI message from multiple messages."""
    processor = WorkflowResultProcessor(MagicMock())
    
    msg1 = AIMessage(content="First response")
    msg2 = AIMessage(content="Second response")
    workflow_result = {
        "messages": [msg1, MagicMock(content="User"), msg2]
    }
    
    result = processor._extract_ai_response(workflow_result)
    assert result == msg2
    assert result.content == "Second response"


@pytest.mark.asyncio
async def test_create_and_save_message(result_processor, mock_session):
    """Test creating and saving a message."""
    mock_conversation = MagicMock()
    mock_conversation.id = "conv_123"
    
    # Mock the count query
    mock_result = MagicMock()
    mock_result.scalar = MagicMock(return_value=5)
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    message = await result_processor._create_and_save_message(
        conversation=mock_conversation,
        content="Test message",
        role=MessageRole.ASSISTANT,
        metadata={"key": "value"},
        prompt_tokens=10,
        completion_tokens=20,
        cost=0.001,
        provider_used="openai",
        response_time_ms=150,
    )
    
    assert message.conversation_id == "conv_123"
    assert message.content == "Test message"
    assert message.role == MessageRole.ASSISTANT
    assert message.sequence_number == 6  # count + 1
    assert message.prompt_tokens == 10
    assert message.completion_tokens == 20
    assert message.total_tokens == 30
    assert message.cost == 0.001
    assert message.provider_used == "openai"
    assert message.response_time_ms == 150
    
    # Verify session operations
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_and_save_message_with_error(result_processor, mock_session):
    """Test message creation handles database errors gracefully."""
    mock_conversation = MagicMock()
    mock_conversation.id = "conv_123"
    
    # Mock query
    mock_result = MagicMock()
    mock_result.scalar = MagicMock(return_value=0)
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Make commit raise an error
    mock_session.commit = AsyncMock(side_effect=Exception("DB error"))
    
    # Should not raise - error is caught and logged
    message = await result_processor._create_and_save_message(
        conversation=mock_conversation,
        content="Test",
        role=MessageRole.ASSISTANT,
    )
    
    # Message should still be created
    assert message.content == "Test"
    
    # Rollback should be called
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_conversation_aggregates(result_processor, mock_session):
    """Test updating conversation aggregates."""
    mock_conversation = MagicMock()
    mock_conversation.id = "conv_123"
    
    # Import path is within the method, so we need to patch it at that location
    with patch('chatter.services.workflow_result_processor.ConversationService') as mock_service_class:
        mock_service = AsyncMock()
        mock_service.update_conversation_aggregates = AsyncMock()
        mock_service_class.return_value = mock_service
        
        await result_processor._update_conversation_aggregates(
            conversation=mock_conversation,
            user_id="user_123",
            tokens_delta=100,
            cost_delta=0.05,
        )
        
        # Verify ConversationService was instantiated with session
        mock_service_class.assert_called_once_with(mock_session)
        
        # Verify update was called with correct parameters
        mock_service.update_conversation_aggregates.assert_called_once_with(
            conversation_id="conv_123",
            user_id="user_123",
            tokens_delta=100,
            cost_delta=0.05,
            message_count_delta=1,
        )


@pytest.mark.asyncio
async def test_process_result_complete(result_processor, mock_session):
    """Test complete result processing."""
    mock_execution = MagicMock()
    mock_execution.id = "exec_123"
    mock_execution.owner_id = "user_123"
    
    mock_conversation = MagicMock()
    mock_conversation.id = "conv_456"
    
    raw_result = {
        "messages": [AIMessage(content="AI response")],
        "tokens_used": 100,
        "prompt_tokens": 50,
        "completion_tokens": 50,
        "cost": 0.01,
        "tool_call_count": 2,
        "metadata": {"provider": "openai"},
    }
    
    # Mock dependencies
    mock_result = MagicMock()
    mock_result.scalar = MagicMock(return_value=0)
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    with patch.object(
        result_processor,
        '_update_conversation_aggregates',
        AsyncMock()
    ):
        start_time = 1000.0
        with patch('time.time', return_value=1000.5):  # 500ms execution
            result = await result_processor.process_result(
                raw_result=raw_result,
                execution=mock_execution,
                conversation=mock_conversation,
                mode=ExecutionMode.STANDARD,
                start_time=start_time,
                provider="openai",
            )
    
    assert isinstance(result, WorkflowResult)
    assert result.execution_id == "exec_123"
    assert result.conversation.id == "conv_456"
    assert result.tokens_used == 100
    assert result.prompt_tokens == 50
    assert result.completion_tokens == 50
    assert result.cost == 0.01
    assert result.tool_calls == 2
    assert result.execution_time_ms == 500
    assert result.metadata == {"provider": "openai"}
    
    # Verify message was created
    assert result.message.content == "AI response"
    assert result.message.role == MessageRole.ASSISTANT
