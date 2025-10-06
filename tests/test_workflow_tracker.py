"""Tests for the unified WorkflowTracker.

This module tests the WorkflowTracker that consolidates all workflow
tracking systems into one unified interface.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC

from chatter.core.workflow_execution_context import (
    ExecutionConfig,
    ExecutionContext,
    WorkflowType,
)
from chatter.core.workflow_execution_result import ExecutionResult
from chatter.core.workflow_tracker import WorkflowTracker


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def workflow_tracker(mock_session):
    """Create a WorkflowTracker instance."""
    return WorkflowTracker(
        session=mock_session,
        debug_mode=True,
    )


@pytest.fixture
def execution_context():
    """Create a sample ExecutionContext."""
    config = ExecutionConfig(
        provider="openai",
        model="gpt-4",
        enable_tools=True,
        input_data={"message": "Hello!"},
    )
    
    return ExecutionContext(
        execution_id="exec_123",
        user_id="user_456",
        conversation_id="conv_789",
        workflow_type=WorkflowType.CHAT,
        source_definition_id="def_abc",
        config=config,
    )


@pytest.fixture
def execution_result():
    """Create a sample ExecutionResult."""
    return ExecutionResult(
        response="Hello, world!",
        execution_time_ms=1500,
        tokens_used=100,
        cost=0.01,
        prompt_tokens=50,
        completion_tokens=50,
        tool_calls=2,
        execution_id="exec_123",
        conversation_id="conv_789",
        workflow_type="chat",
    )


class TestWorkflowTracker:
    """Test WorkflowTracker functionality."""

    @pytest.mark.asyncio
    async def test_start_tracking(
        self, workflow_tracker, execution_context
    ):
        """Test starting workflow tracking."""
        with patch(
            "chatter.core.workflow_tracker.get_monitoring_service"
        ) as mock_get_monitoring:
            with patch(
                "chatter.core.workflow_tracker.emit_event"
            ) as mock_emit:
                # Setup mocks
                mock_monitoring = AsyncMock()
                mock_monitoring.start_workflow_tracking = MagicMock(
                    return_value="wf_123"
                )
                mock_get_monitoring.return_value = mock_monitoring
                mock_emit.return_value = True

                # Start tracking
                await workflow_tracker.start(execution_context)

                # Verify workflow_id was set
                assert execution_context.workflow_id == "wf_123"

                # Verify monitoring was called
                mock_monitoring.start_workflow_tracking.assert_called_once()

                # Verify event was emitted
                mock_emit.assert_called_once()
                event = mock_emit.call_args[0][0]
                assert event.event_type == "workflow_started"
                assert event.user_id == "user_456"

                # Verify performance monitor started
                assert (
                    "exec_123"
                    in workflow_tracker.performance_monitor.start_times
                )

    @pytest.mark.asyncio
    async def test_complete_tracking(
        self,
        workflow_tracker,
        execution_context,
        execution_result,
    ):
        """Test completing workflow tracking."""
        # Set workflow_id
        execution_context.workflow_id = "wf_123"

        with patch(
            "chatter.core.workflow_tracker.get_monitoring_service"
        ) as mock_get_monitoring:
            with patch(
                "chatter.core.workflow_tracker.emit_event"
            ) as mock_emit:
                # Setup mocks
                mock_monitoring = AsyncMock()
                mock_get_monitoring.return_value = mock_monitoring
                mock_emit.return_value = True

                # Start tracking first (to initialize performance monitor)
                workflow_tracker.performance_monitor.start_workflow(
                    "exec_123"
                )

                # Complete tracking
                await workflow_tracker.complete(
                    execution_context, execution_result
                )

                # Verify monitoring was updated
                mock_monitoring.update_workflow_metrics.assert_called_once()
                mock_monitoring.finish_workflow_tracking.assert_called_once_with(
                    "wf_123"
                )

                # Verify event was emitted
                mock_emit.assert_called_once()
                event = mock_emit.call_args[0][0]
                assert event.event_type == "workflow_completed"
                assert event.user_id == "user_456"
                assert "tokens_used" in event.data

    @pytest.mark.asyncio
    async def test_fail_tracking(
        self, workflow_tracker, execution_context
    ):
        """Test failing workflow tracking."""
        # Set workflow_id
        execution_context.workflow_id = "wf_123"

        with patch(
            "chatter.core.workflow_tracker.get_monitoring_service"
        ) as mock_get_monitoring:
            with patch(
                "chatter.core.workflow_tracker.emit_event"
            ) as mock_emit:
                # Setup mocks
                mock_monitoring = AsyncMock()
                mock_get_monitoring.return_value = mock_monitoring
                mock_emit.return_value = True

                # Start tracking first
                workflow_tracker.performance_monitor.start_workflow(
                    "exec_123"
                )

                # Fail tracking
                test_error = ValueError("Test error")
                await workflow_tracker.fail(
                    execution_context, test_error
                )

                # Verify monitoring was updated with error
                mock_monitoring.update_workflow_metrics.assert_called_once()
                call_args = (
                    mock_monitoring.update_workflow_metrics.call_args
                )
                assert "error" in call_args[1]

                # Verify event was emitted with high priority
                mock_emit.assert_called_once()
                event = mock_emit.call_args[0][0]
                assert event.event_type == "workflow_failed"
                assert event.priority.value == "high"
                assert "error" in event.data
                assert event.data["error_type"] == "ValueError"

    def test_checkpoint(self, workflow_tracker):
        """Test checkpoint logging."""
        # Log checkpoint
        workflow_tracker.checkpoint(
            "Test checkpoint", data={"step": 1}
        )

        # Verify log was created
        logs = workflow_tracker.get_logs()
        assert len(logs) == 1
        assert logs[0]["message"] == "Test checkpoint"
        assert logs[0]["data"]["step"] == 1

    def test_get_logs(self, workflow_tracker):
        """Test getting debug logs."""
        # Log some checkpoints
        workflow_tracker.checkpoint("Checkpoint 1")
        workflow_tracker.checkpoint("Checkpoint 2")
        workflow_tracker.checkpoint("Checkpoint 3")

        # Get logs
        logs = workflow_tracker.get_logs()
        assert len(logs) == 3
        assert logs[0]["message"] == "Checkpoint 1"
        assert logs[1]["message"] == "Checkpoint 2"
        assert logs[2]["message"] == "Checkpoint 3"

    @pytest.mark.asyncio
    async def test_tracking_without_definition(
        self, workflow_tracker
    ):
        """Test tracking without definition_id (chat workflow)."""
        # Create context without definition
        config = ExecutionConfig(
            provider="openai",
            model="gpt-4",
        )
        
        context = ExecutionContext(
            execution_id="exec_123",
            user_id="user_456",
            workflow_type=WorkflowType.CHAT,
            config=config,
        )

        with patch(
            "chatter.core.workflow_tracker.get_monitoring_service"
        ) as mock_get_monitoring:
            with patch(
                "chatter.core.workflow_tracker.emit_event"
            ) as mock_emit:
                mock_monitoring = AsyncMock()
                mock_monitoring.start_workflow_tracking = MagicMock(
                    return_value="wf_123"
                )
                mock_get_monitoring.return_value = mock_monitoring
                mock_emit.return_value = True

                # Start tracking
                await workflow_tracker.start(context)

                # Should still track via monitoring and events
                mock_monitoring.start_workflow_tracking.assert_called_once()
                mock_emit.assert_called_once()


class TestWorkflowTrackerIntegration:
    """Test WorkflowTracker integration with other components."""

    @pytest.mark.asyncio
    async def test_full_workflow_lifecycle(
        self, workflow_tracker, execution_context, execution_result
    ):
        """Test complete workflow lifecycle: start -> complete."""
        with patch(
            "chatter.core.workflow_tracker.get_monitoring_service"
        ) as mock_get_monitoring:
            with patch(
                "chatter.core.workflow_tracker.emit_event"
            ) as mock_emit:
                # Setup mocks
                mock_monitoring = AsyncMock()
                mock_monitoring.start_workflow_tracking = MagicMock(
                    return_value="wf_123"
                )
                mock_get_monitoring.return_value = mock_monitoring
                mock_emit.return_value = True

                # Start
                await workflow_tracker.start(execution_context)

                # Log checkpoints
                workflow_tracker.checkpoint("Step 1 complete")
                workflow_tracker.checkpoint("Step 2 complete")

                # Complete
                await workflow_tracker.complete(
                    execution_context, execution_result
                )

                # Verify full lifecycle
                assert len(workflow_tracker.get_logs()) >= 2
                assert mock_emit.call_count == 2  # start + complete


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
