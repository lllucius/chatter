"""Tests for pipeline base classes and infrastructure."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from chatter.core.pipeline import (
    ExecutionContext,
    ExecutionContextBuilder,
    ExecutionResult,
    Executor,
    Middleware,
    WorkflowPipeline,
)


class TestExecutionContext:
    """Tests for ExecutionContext and builder."""

    def test_builder_pattern(self):
        """Test building ExecutionContext with builder."""
        context = (
            ExecutionContext.builder()
            .workflow_id("wf_123")
            .user_id("user_456")
            .conversation_id("conv_789")
            .with_state({"messages": []})
            .with_metadata({"provider": "openai"})
            .with_variables({"key": "value"})
            .build()
        )

        assert context.workflow_id == "wf_123"
        assert context.user_id == "user_456"
        assert context.conversation_id == "conv_789"
        assert context.initial_state == {"messages": []}
        assert context.metadata == {"provider": "openai"}
        assert context.variables == {"key": "value"}

    def test_builder_missing_workflow_id(self):
        """Test builder raises error without workflow_id."""
        with pytest.raises(ValueError, match="workflow_id is required"):
            ExecutionContext.builder().user_id("user_123").build()

    def test_builder_missing_user_id(self):
        """Test builder raises error without user_id."""
        with pytest.raises(ValueError, match="user_id is required"):
            ExecutionContext.builder().workflow_id("wf_123").build()

    def test_builder_optional_fields(self):
        """Test builder with only required fields."""
        context = (
            ExecutionContext.builder()
            .workflow_id("wf_123")
            .user_id("user_456")
            .build()
        )

        assert context.workflow_id == "wf_123"
        assert context.user_id == "user_456"
        assert context.conversation_id is None
        assert context.initial_state == {}
        assert context.metadata == {}
        assert context.variables == {}


class TestExecutionResult:
    """Tests for ExecutionResult."""

    def test_from_langgraph(self):
        """Test creating ExecutionResult from LangGraph result."""
        langgraph_result = {
            "messages": [
                MagicMock(content="Hello"),
                MagicMock(content="World"),
            ],
            "usage_metadata": {
                "total_tokens": 100,
                "input_tokens": 40,
                "output_tokens": 60,
            },
        }

        result = ExecutionResult.from_langgraph(langgraph_result)

        assert result.output["response"] == "World"
        assert len(result.output["messages"]) == 2
        assert result.metrics["tokens_used"] == 100
        assert result.metrics["prompt_tokens"] == 40
        assert result.metrics["completion_tokens"] == 60
        assert result.state == langgraph_result

    def test_from_langgraph_empty_messages(self):
        """Test creating ExecutionResult with no messages."""
        langgraph_result = {
            "messages": [],
            "usage_metadata": {},
        }

        result = ExecutionResult.from_langgraph(langgraph_result)

        assert result.output["response"] == ""
        assert result.output["messages"] == []
        assert result.metrics["tokens_used"] == 0


class TestWorkflowPipeline:
    """Tests for WorkflowPipeline."""

    @pytest.fixture
    def mock_executor(self):
        """Create a mock executor."""

        class MockExecutor:
            async def execute(self, workflow, context):
                return ExecutionResult(
                    output={"result": "success"},
                    state={"status": "completed"},
                    metrics={"tokens": 10},
                )

        return MockExecutor()

    @pytest.fixture
    def mock_context(self):
        """Create a mock execution context."""
        return (
            ExecutionContext.builder()
            .workflow_id("wf_123")
            .user_id("user_456")
            .with_state({"messages": []})
            .build()
        )

    @pytest.mark.asyncio
    async def test_execute_without_middleware(self, mock_executor, mock_context):
        """Test pipeline execution without middleware."""
        pipeline = WorkflowPipeline(mock_executor)
        mock_workflow = MagicMock()

        result = await pipeline.execute(mock_workflow, mock_context)

        assert result.output == {"result": "success"}
        assert result.state == {"status": "completed"}
        assert result.metrics == {"tokens": 10}

    @pytest.mark.asyncio
    async def test_execute_with_middleware(self, mock_executor, mock_context):
        """Test pipeline execution with middleware."""

        class TestMiddleware:
            def __init__(self):
                self.called = False

            async def __call__(self, workflow, context, next):
                self.called = True
                result = await next(workflow, context)
                result.metadata["middleware"] = "executed"
                return result

        middleware = TestMiddleware()
        pipeline = WorkflowPipeline(mock_executor).use(middleware)
        mock_workflow = MagicMock()

        result = await pipeline.execute(mock_workflow, mock_context)

        assert middleware.called
        assert result.metadata["middleware"] == "executed"

    @pytest.mark.asyncio
    async def test_middleware_chain_order(self, mock_executor, mock_context):
        """Test middleware executes in correct order."""
        execution_order = []

        class FirstMiddleware:
            async def __call__(self, workflow, context, next):
                execution_order.append("first_before")
                result = await next(workflow, context)
                execution_order.append("first_after")
                return result

        class SecondMiddleware:
            async def __call__(self, workflow, context, next):
                execution_order.append("second_before")
                result = await next(workflow, context)
                execution_order.append("second_after")
                return result

        pipeline = (
            WorkflowPipeline(mock_executor)
            .use(FirstMiddleware())
            .use(SecondMiddleware())
        )

        await pipeline.execute(MagicMock(), mock_context)

        # First middleware is outermost, so executes first
        assert execution_order == [
            "first_before",
            "second_before",
            "second_after",
            "first_after",
        ]

    @pytest.mark.asyncio
    async def test_middleware_can_modify_context(self, mock_executor, mock_context):
        """Test middleware can modify context."""

        class ContextModifyingMiddleware:
            async def __call__(self, workflow, context, next):
                # Modify context metadata
                context.metadata["modified"] = True
                return await next(workflow, context)

        pipeline = WorkflowPipeline(mock_executor).use(
            ContextModifyingMiddleware()
        )

        await pipeline.execute(MagicMock(), mock_context)

        assert mock_context.metadata["modified"] is True

    @pytest.mark.asyncio
    async def test_middleware_error_propagation(self, mock_executor, mock_context):
        """Test errors propagate through middleware chain."""

        class ErrorMiddleware:
            async def __call__(self, workflow, context, next):
                raise ValueError("Middleware error")

        pipeline = WorkflowPipeline(mock_executor).use(ErrorMiddleware())

        with pytest.raises(ValueError, match="Middleware error"):
            await pipeline.execute(MagicMock(), mock_context)

    @pytest.mark.asyncio
    async def test_middleware_can_catch_errors(self, mock_context):
        """Test middleware can catch and handle errors."""

        class FailingExecutor:
            async def execute(self, workflow, context):
                raise RuntimeError("Execution failed")

        class ErrorHandlingMiddleware:
            async def __call__(self, workflow, context, next):
                try:
                    return await next(workflow, context)
                except RuntimeError:
                    # Return fallback result
                    return ExecutionResult(
                        output={"error": "handled"},
                        state={},
                        errors=[{"type": "RuntimeError"}],
                    )

        pipeline = WorkflowPipeline(FailingExecutor()).use(
            ErrorHandlingMiddleware()
        )

        result = await pipeline.execute(MagicMock(), mock_context)

        assert result.output == {"error": "handled"}
        assert len(result.errors) == 1

    @pytest.mark.asyncio
    async def test_multiple_middleware_composition(self, mock_executor, mock_context):
        """Test composing multiple middleware."""

        class LoggingMiddleware:
            async def __call__(self, workflow, context, next):
                result = await next(workflow, context)
                result.metadata["logged"] = True
                return result

        class MetricsMiddleware:
            async def __call__(self, workflow, context, next):
                result = await next(workflow, context)
                result.metadata["metrics_collected"] = True
                return result

        class CachingMiddleware:
            async def __call__(self, workflow, context, next):
                result = await next(workflow, context)
                result.metadata["cached"] = True
                return result

        pipeline = (
            WorkflowPipeline(mock_executor)
            .use(LoggingMiddleware())
            .use(MetricsMiddleware())
            .use(CachingMiddleware())
        )

        result = await pipeline.execute(MagicMock(), mock_context)

        assert result.metadata["logged"] is True
        assert result.metadata["metrics_collected"] is True
        assert result.metadata["cached"] is True
