"""Tests for the new unified ExecutionEngine.

This module tests the new ExecutionEngine that consolidates all workflow
execution paths into a single, unified pipeline.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chatter.core.workflow_execution_context import (
    ExecutionConfig,
    ExecutionContext,
    WorkflowType,
)
from chatter.core.workflow_execution_engine import ExecutionEngine
from chatter.core.workflow_execution_result import ExecutionResult
from chatter.schemas.execution import ExecutionRequest


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    service = MagicMock()
    mock_llm = MagicMock()
    service.get_llm = AsyncMock(return_value=mock_llm)
    return service


@pytest.fixture
def execution_engine(mock_session, mock_llm_service):
    """Create an ExecutionEngine instance."""
    return ExecutionEngine(
        session=mock_session,
        llm_service=mock_llm_service,
    )


class TestExecutionContext:
    """Test ExecutionContext functionality."""

    def test_execution_context_creation(self):
        """Test creating an ExecutionContext."""
        context = ExecutionContext(
            execution_id="test_id",
            user_id="user_123",
            workflow_type=WorkflowType.CHAT,
        )

        assert context.execution_id == "test_id"
        assert context.user_id == "user_123"
        assert context.workflow_type == WorkflowType.CHAT
        assert context.thread_id == "test_id"

    def test_execution_context_with_conversation(self):
        """Test ExecutionContext with conversation_id."""
        context = ExecutionContext(
            execution_id="test_id",
            user_id="user_123",
            conversation_id="conv_456",
            workflow_type=WorkflowType.CHAT,
        )

        # Thread ID should be conversation_id when available
        assert context.thread_id == "conv_456"

    def test_to_execution_record(self):
        """Test converting context to execution record."""
        config = ExecutionConfig(
            provider="openai",
            model="gpt-4",
            enable_tools=True,
        )
        
        context = ExecutionContext(
            execution_id="test_id",
            user_id="user_123",
            workflow_type=WorkflowType.CHAT,
            config=config,
        )

        record = context.to_execution_record()

        assert record["id"] == "test_id"
        assert record["owner_id"] == "user_123"
        assert record["workflow_type"] == "chat"
        assert record["workflow_config"]["provider"] == "openai"
        assert record["workflow_config"]["model"] == "gpt-4"
        assert record["workflow_config"]["enable_tools"] is True


class TestExecutionResult:
    """Test ExecutionResult functionality."""

    def test_execution_result_from_raw(self):
        """Test creating ExecutionResult from raw workflow result."""
        from langchain_core.messages import AIMessage

        raw_result = {
            "messages": [AIMessage(content="Hello, world!")],
            "usage_metadata": {
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
            },
            "cost": 0.001,
            "tool_call_count": 2,
            "metadata": {"model": "gpt-4"},
        }

        result = ExecutionResult.from_raw(
            raw_result=raw_result,
            execution_id="exec_123",
            conversation_id="conv_456",
            workflow_type="chat",
        )

        assert result.response == "Hello, world!"
        assert result.tokens_used == 15
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 5
        assert result.cost == 0.001
        assert result.tool_calls == 2
        assert result.execution_id == "exec_123"
        assert result.conversation_id == "conv_456"
        assert result.workflow_type == "chat"

    def test_execution_result_to_dict(self):
        """Test converting ExecutionResult to dictionary."""
        result = ExecutionResult(
            response="Test response",
            tokens_used=100,
            cost=0.01,
            execution_id="exec_123",
        )

        result_dict = result.to_dict()

        assert result_dict["response"] == "Test response"
        assert result_dict["tokens_used"] == 100
        assert result_dict["cost"] == 0.01
        assert result_dict["execution_id"] == "exec_123"


class TestExecutionRequest:
    """Test ExecutionRequest schema."""

    def test_execution_request_chat(self):
        """Test creating an ExecutionRequest for chat."""
        request = ExecutionRequest(
            message="Hello!",
            provider="openai",
            model="gpt-4",
            enable_tools=True,
        )

        assert request.message == "Hello!"
        assert request.provider == "openai"
        assert request.model == "gpt-4"
        assert request.enable_tools is True
        assert request.streaming is False

    def test_execution_request_template(self):
        """Test creating an ExecutionRequest for template."""
        request = ExecutionRequest(
            template_id="template_123",
            message="Test message",
            template_params={"param1": "value1"},
        )

        assert request.template_id == "template_123"
        assert request.message == "Test message"
        assert request.template_params == {"param1": "value1"}


class TestExecutionEngine:
    """Test ExecutionEngine functionality."""

    @pytest.mark.asyncio
    async def test_determine_workflow_type(self, execution_engine):
        """Test workflow type determination."""
        # Template workflow
        request = ExecutionRequest(template_id="template_123")
        wf_type = execution_engine._determine_workflow_type(request)
        assert wf_type == WorkflowType.TEMPLATE

        # Definition workflow
        request = ExecutionRequest(definition_id="def_456")
        wf_type = execution_engine._determine_workflow_type(request)
        assert wf_type == WorkflowType.DEFINITION

        # Custom workflow
        request = ExecutionRequest(
            nodes=[{"id": "n1", "type": "model"}],
            edges=[{"source": "n1", "target": "END"}],
        )
        wf_type = execution_engine._determine_workflow_type(request)
        assert wf_type == WorkflowType.CUSTOM

        # Chat workflow (default)
        request = ExecutionRequest(message="Hello!")
        wf_type = execution_engine._determine_workflow_type(request)
        assert wf_type == WorkflowType.CHAT

    @pytest.mark.asyncio
    async def test_create_context(self, execution_engine):
        """Test creating ExecutionContext from request."""
        request = ExecutionRequest(
            message="Hello!",
            provider="openai",
            model="gpt-4",
            temperature=0.7,
            enable_tools=True,
            conversation_id="conv_123",
        )

        context = await execution_engine._create_context(
            request=request,
            user_id="user_456",
        )

        assert context.user_id == "user_456"
        assert context.conversation_id == "conv_123"
        assert context.workflow_type == WorkflowType.CHAT
        assert context.config.provider == "openai"
        assert context.config.model == "gpt-4"
        assert context.config.temperature == 0.7
        assert context.config.enable_tools is True
        assert context.llm is not None

    @pytest.mark.asyncio
    async def test_create_initial_state(self, execution_engine):
        """Test creating initial workflow state."""
        config = ExecutionConfig(
            input_data={"message": "Hello, world!"},
            provider="openai",
            model="gpt-4",
        )
        
        context = ExecutionContext(
            execution_id="exec_123",
            user_id="user_456",
            conversation_id="conv_789",
            workflow_type=WorkflowType.CHAT,
            config=config,
        )

        initial_state = execution_engine._create_initial_state(context)

        assert initial_state["user_id"] == "user_456"
        assert initial_state["conversation_id"] == "conv_789"
        assert len(initial_state["messages"]) == 1
        assert initial_state["messages"][0].content == "Hello, world!"
        assert initial_state["metadata"]["workflow_type"] == "chat"
        assert initial_state["metadata"]["provider"] == "openai"
        assert initial_state["metadata"]["model"] == "gpt-4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
