"""Tests for workflow execution timeouts and resource limits."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chatter.core.workflow_limits import (
    WorkflowLimitManager,
    WorkflowLimits,
    WorkflowResourceLimitError,
    WorkflowTimeoutError,
)
from chatter.models.conversation import Conversation, MessageRole
from chatter.schemas.chat import ChatRequest
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.services.workflow_execution import (
    WorkflowExecutionService as WorkflowExecutionService,
)


class TestWorkflowLimitManager:
    """Test workflow limit manager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.limit_manager = WorkflowLimitManager()
        # Clear any existing state from previous tests
        self.limit_manager.active_workflows.clear()
        self.limit_manager.user_workflow_counts.clear()

        self.user_id = "test_user"
        self.workflow_id = "test_workflow"
        self.limits = WorkflowLimits(
            execution_timeout=60,
            step_timeout=30,
            streaming_timeout=120,
            max_tokens=1000,
            max_memory_mb=512,
            max_concurrent=5,
        )

    def teardown_method(self):
        """Clean up after each test."""
        # Clear limit manager state to avoid interference between tests
        self.limit_manager.active_workflows.clear()
        self.limit_manager.user_workflow_counts.clear()

    def test_get_default_limits(self):
        """Test getting default limits from configuration."""
        limits = self.limit_manager.get_default_limits()
        assert isinstance(limits, WorkflowLimits)
        assert limits.execution_timeout > 0
        assert limits.max_tokens > 0

    def test_concurrent_limit_check(self):
        """Test concurrent workflow limit checking."""
        # Should pass initially
        self.limit_manager.check_concurrent_limit(
            self.user_id, self.limits
        )

        # Add workflows up to limit
        for i in range(self.limits.max_concurrent):
            self.limit_manager.user_workflow_counts[self.user_id] = (
                i + 1
            )

        # Should fail when limit reached
        with pytest.raises(WorkflowResourceLimitError) as exc_info:
            self.limit_manager.check_concurrent_limit(
                self.user_id, self.limits
            )
        assert exc_info.value.limit_type == "concurrent_workflows"

    def test_workflow_tracking_lifecycle(self):
        """Test complete workflow tracking lifecycle."""
        # Start tracking
        self.limit_manager.start_workflow_tracking(
            self.workflow_id, self.user_id, self.limits
        )

        assert self.workflow_id in self.limit_manager.active_workflows
        assert (
            self.limit_manager.user_workflow_counts[self.user_id] == 1
        )

        # Update usage
        self.limit_manager.update_workflow_usage(
            self.workflow_id, tokens_delta=100, steps_delta=1
        )

        usage = self.limit_manager.active_workflows[self.workflow_id]
        assert usage.tokens_used == 100
        assert usage.steps_completed == 1

        # End tracking
        final_usage = self.limit_manager.end_workflow_tracking(
            self.workflow_id, self.user_id
        )

        assert (
            self.workflow_id not in self.limit_manager.active_workflows
        )
        assert (
            self.limit_manager.user_workflow_counts[self.user_id] == 0
        )
        assert final_usage.tokens_used == 100

    def test_resource_limit_checking(self):
        """Test resource limit enforcement."""
        # Start tracking
        self.limit_manager.start_workflow_tracking(
            self.workflow_id, self.user_id, self.limits
        )

        # Test token limit
        self.limit_manager.update_workflow_usage(
            self.workflow_id, tokens_delta=self.limits.max_tokens + 1
        )

        with pytest.raises(WorkflowResourceLimitError) as exc_info:
            self.limit_manager.check_workflow_limits(
                self.workflow_id, self.limits
            )
        assert exc_info.value.limit_type == "max_tokens"

        # Reset for memory test
        self.limit_manager.active_workflows[
            self.workflow_id
        ].tokens_used = 0

        # Test memory limit
        self.limit_manager.update_workflow_usage(
            self.workflow_id,
            memory_delta_mb=self.limits.max_memory_mb + 1,
        )

        with pytest.raises(WorkflowResourceLimitError) as exc_info:
            self.limit_manager.check_workflow_limits(
                self.workflow_id, self.limits
            )
        assert exc_info.value.limit_type == "max_memory"

    @pytest.mark.asyncio
    async def test_timeout_context_manager(self):
        """Test workflow timeout context manager."""
        # Test successful operation within timeout
        async with self.limit_manager.workflow_timeout_context(
            self.workflow_id, timeout_seconds=1, timeout_type="test"
        ):
            await asyncio.sleep(0.1)  # Should complete successfully

        # Test timeout
        with pytest.raises(WorkflowTimeoutError) as exc_info:
            async with self.limit_manager.workflow_timeout_context(
                self.workflow_id,
                timeout_seconds=0.1,
                timeout_type="test",
            ):
                await asyncio.sleep(0.5)  # Should timeout
        assert exc_info.value.timeout_type == "test"

    def test_workflow_stats(self):
        """Test workflow statistics collection."""
        # Add some active workflows
        for i in range(3):
            workflow_id = f"workflow_{i}"
            self.limit_manager.start_workflow_tracking(
                workflow_id, f"user_{i}", self.limits
            )
            self.limit_manager.update_workflow_usage(
                workflow_id, tokens_delta=100 * (i + 1)
            )

        stats = self.limit_manager.get_workflow_stats()

        assert stats["active_workflows"] == 3
        assert stats["total_users_with_workflows"] == 3
        assert stats["total_tokens_in_use"] == 600  # 100 + 200 + 300


class TestWorkflowExecutionService:
    """Test workflow execution service with timeouts and streaming."""

    def setup_method(self):
        """Set up test fixtures."""
        self.llm_service = AsyncMock(spec=LLMService)
        self.message_service = AsyncMock(spec=MessageService)
        self.session = MagicMock()  # Mock database session

        # Add the missing add_message_to_conversation method to the mock
        mock_message = MagicMock()
        mock_message.id = "msg_123"
        mock_message.content = "Test response"
        self.message_service.add_message_to_conversation = AsyncMock(
            return_value=mock_message
        )
        self.message_service.get_recent_messages = AsyncMock(
            return_value=[]
        )

        self.workflow_service = WorkflowExecutionService(
            self.llm_service, self.message_service, self.session
        )

        # Mock conversation and request
        self.conversation = MagicMock(spec=Conversation)
        self.conversation.id = "conv_123"
        self.conversation.user_id = "user_123"
        self.conversation.workspace_id = "workspace_123"

        self.chat_request = ChatRequest(
            message="Test message",
            workflow="plain",
        )

        self.correlation_id = "corr_123"

    def teardown_method(self):
        """Clean up after each test."""
        # Clear any workflow state that might interfere with other tests
        if hasattr(self.workflow_service, "limit_manager"):
            self.workflow_service.limit_manager.active_workflows.clear()
            self.workflow_service.limit_manager.user_workflow_counts.clear()

    @pytest.mark.asyncio
    async def test_execute_workflow_with_limits(self):
        """Test workflow execution with resource limits."""
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = "Test response"

        mock_provider = AsyncMock()
        mock_provider.ainvoke.return_value = mock_response
        mock_provider.__class__.__name__ = "TestProvider"

        self.llm_service.get_default_provider.return_value = (
            mock_provider
        )
        self.llm_service.convert_conversation_to_messages.return_value = (
            []
        )

        # Mock message service
        self.workflow_service._get_conversation_messages = AsyncMock(
            return_value=[]
        )

        # Define custom limits
        limits = WorkflowLimits(
            execution_timeout=60,
            step_timeout=30,
            streaming_timeout=120,
            max_tokens=1000,
            max_memory_mb=512,
            max_concurrent=5,
        )

        # Execute workflow
        (
            result_message,
            usage_info,
        ) = await self.workflow_service.execute_workflow(
            self.conversation,
            self.chat_request,
            self.correlation_id,
            user_id="user_123",
            limits=limits,
        )

        # Verify result
        assert result_message.content == "Test response"
        assert result_message.role == MessageRole.ASSISTANT
        assert usage_info["tokens"] > 0

    @pytest.mark.asyncio
    async def test_execute_workflow_timeout(self):
        """Test workflow execution timeout."""

        # Mock slow LLM response
        async def slow_invoke(*args, **kwargs):
            await asyncio.sleep(2)  # Simulate slow response
            mock_response = MagicMock()
            mock_response.content = "Test response"
            return mock_response

        mock_provider = AsyncMock()
        mock_provider.ainvoke = slow_invoke
        mock_provider.__class__.__name__ = "TestProvider"

        self.llm_service.get_default_provider.return_value = (
            mock_provider
        )
        self.llm_service.convert_conversation_to_messages.return_value = (
            []
        )
        self.workflow_service._get_conversation_messages = AsyncMock(
            return_value=[]
        )

        # Define short timeout
        limits = WorkflowLimits(
            execution_timeout=1,  # 1 second timeout
            step_timeout=30,
            streaming_timeout=120,
            max_tokens=1000,
            max_memory_mb=512,
            max_concurrent=5,
        )

        # Should timeout
        with pytest.raises(WorkflowTimeoutError) as exc_info:
            await self.workflow_service.execute_workflow(
                self.conversation,
                self.chat_request,
                self.correlation_id,
                user_id="user_123",
                limits=limits,
            )
        assert exc_info.value.timeout_type == "execution_timeout"

    @pytest.mark.asyncio
    async def test_concurrent_workflow_limit(self):
        """Test concurrent workflow limit enforcement."""
        # Mock successful workflow
        mock_response = MagicMock()
        mock_response.content = "Test response"

        mock_provider = AsyncMock()
        mock_provider.ainvoke.return_value = mock_response
        mock_provider.__class__.__name__ = "TestProvider"

        self.llm_service.get_default_provider.return_value = (
            mock_provider
        )
        self.llm_service.convert_conversation_to_messages.return_value = (
            []
        )
        self.workflow_service._get_conversation_messages = AsyncMock(
            return_value=[]
        )

        # Set very low concurrent limit
        limits = WorkflowLimits(
            execution_timeout=60,
            step_timeout=30,
            streaming_timeout=120,
            max_tokens=1000,
            max_memory_mb=512,
            max_concurrent=1,
        )

        user_id = "user_123"

        # First workflow should succeed
        result1 = await self.workflow_service.execute_workflow(
            self.conversation,
            self.chat_request,
            "corr_1",
            user_id=user_id,
            limits=limits,
        )
        assert result1[0].content == "Test response"

        # Simulate the first workflow still running by manually setting count
        self.workflow_service.limit_manager.user_workflow_counts[
            user_id
        ] = 1

        # Second concurrent workflow should fail
        from chatter.core.exceptions import WorkflowExecutionError

        with pytest.raises(WorkflowExecutionError) as exc_info:
            await self.workflow_service.execute_workflow(
                self.conversation,
                self.chat_request,
                "corr_2",
                user_id=user_id,
                limits=limits,
            )
        assert "Resource limit exceeded" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_streaming_workflow_with_limits(self):
        """Test streaming workflow execution with resource limits."""
        # Mock streaming response
        mock_provider = AsyncMock()
        mock_provider.__class__.__name__ = "TestProvider"

        # Mock astream method for native streaming
        async def mock_astream(messages):
            chunks = [
                MagicMock(content="Hello"),
                MagicMock(content=" "),
                MagicMock(content="world"),
            ]
            for chunk in chunks:
                yield chunk

        mock_provider.astream = mock_astream

        self.llm_service.get_default_provider.return_value = (
            mock_provider
        )
        self.llm_service.convert_conversation_to_messages.return_value = (
            []
        )
        self.workflow_service._get_conversation_messages = AsyncMock(
            return_value=[]
        )

        # Mock the workflow manager to avoid the 'str' object astream issue
        with patch(
            "chatter.core.dependencies.get_workflow_manager"
        ) as mock_get_manager:
            mock_workflow_manager = AsyncMock()
            mock_get_manager.return_value = mock_workflow_manager

            # Mock stream_workflow to return proper streaming events
            async def mock_stream_workflow(workflow_type, state):
                events = [
                    {"type": "token", "content": "Hello"},
                    {"type": "token", "content": " "},
                    {"type": "token", "content": "world"},
                    {"type": "complete", "usage": {"tokens": 3}},
                ]
                for event in events:
                    yield event

            mock_workflow_manager.stream_workflow = mock_stream_workflow

            limits = WorkflowLimits(
                execution_timeout=60,
                step_timeout=30,
                streaming_timeout=120,
                max_tokens=1000,
                max_memory_mb=512,
                max_concurrent=5,
            )

            # Collect streaming results
            chunks = []
            async for (
                chunk
            ) in self.workflow_service.execute_workflow_streaming(
                self.conversation,
                self.chat_request,
                self.correlation_id,
                user_id="user_123",
                limits=limits,
            ):
                chunks.append(chunk)
                if chunk.type == "complete":
                    break

            # Verify streaming chunks
            token_chunks = [c for c in chunks if c.type == "token"]
            assert len(token_chunks) > 0

        # Verify completion
        complete_chunks = [c for c in chunks if c.type == "complete"]
        assert len(complete_chunks) == 1

    @pytest.mark.asyncio
    async def test_streaming_workflow_timeout(self):
        """Test streaming workflow timeout."""
        # Mock workflow manager to avoid the 'str' object astream issue
        with patch(
            "chatter.core.dependencies.get_workflow_manager"
        ) as mock_get_manager:
            mock_workflow_manager = AsyncMock()
            mock_get_manager.return_value = mock_workflow_manager

            # Mock slow streaming response
            async def slow_stream_workflow(workflow_type, state):
                await asyncio.sleep(2)  # Simulate slow start
                yield {"type": "token", "content": "slow"}
                yield {"type": "complete", "usage": {"tokens": 1}}

            mock_workflow_manager.stream_workflow = slow_stream_workflow

            self.llm_service.get_default_provider.return_value = (
                AsyncMock()
            )
            self.llm_service.convert_conversation_to_messages.return_value = (
                []
            )
            self.workflow_service._get_conversation_messages = (
                AsyncMock(return_value=[])
            )

            # Very short streaming timeout
            limits = WorkflowLimits(
                execution_timeout=60,
                step_timeout=30,
                streaming_timeout=1,  # 1 second timeout
                max_tokens=1000,
                max_memory_mb=512,
                max_concurrent=5,
            )

            # Collect chunks until timeout
            chunks = []
            async for (
                chunk
            ) in self.workflow_service.execute_workflow_streaming(
                self.conversation,
                self.chat_request,
                self.correlation_id,
                user_id="user_123",
                limits=limits,
            ):
                chunks.append(chunk)
                if chunk.type == "error":
                    break

            # Should get timeout error
            error_chunks = [c for c in chunks if c.type == "error"]
            assert len(error_chunks) > 0
            assert (
                "timed out" in error_chunks[0].content.lower()
                or "timeout" in error_chunks[0].content.lower()
            )

    @pytest.mark.asyncio
    async def test_enhanced_token_streaming_all_workflows(self):
        """Test enhanced token streaming for all workflow types."""
        # Mock workflow manager
        with patch(
            "chatter.core.dependencies.get_workflow_manager"
        ) as mock_get_manager:
            mock_workflow_manager = MagicMock()
            mock_get_manager.return_value = mock_workflow_manager

            # Mock streaming workflow response
            async def mock_stream_workflow(workflow_type, state):
                events = [
                    {"type": "thinking", "thought": "Processing..."},
                    {"type": "token", "content": "Test"},
                    {"type": "token", "content": " response"},
                    {"type": "complete", "usage": {"tokens": 2}},
                ]
                for event in events:
                    yield event

            mock_workflow_manager.stream_workflow = mock_stream_workflow

            self.workflow_service._get_conversation_messages = (
                AsyncMock(return_value=[])
            )

            limits = WorkflowLimits(
                execution_timeout=60,
                step_timeout=30,
                streaming_timeout=120,
                max_tokens=1000,
                max_memory_mb=512,
                max_concurrent=5,
            )

            # Test different workflow types
            for workflow_type in [
                "rag",
                "tools",
                "full",
            ]:
                self.chat_request.workflow = workflow_type

                chunks = []
                async for (
                    chunk
                ) in self.workflow_service.execute_workflow_streaming(
                    self.conversation,
                    self.chat_request,
                    self.correlation_id,
                    user_id="user_123",
                    limits=limits,
                ):
                    chunks.append(chunk)
                    if chunk.type == "complete":
                        break

                # Verify we got token chunks
                token_chunks = [c for c in chunks if c.type == "token"]
                assert (
                    len(token_chunks) > 0
                ), f"No token chunks for {workflow_type}"


if __name__ == "__main__":
    pytest.main([__file__])
