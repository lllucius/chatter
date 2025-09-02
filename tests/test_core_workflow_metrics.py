"""Tests for workflow metrics and monitoring system."""

import asyncio
from datetime import datetime, timedelta

import pytest

from chatter.core.exceptions import WorkflowMetricsError
from chatter.core.workflow_metrics import (
    WorkflowMetrics,
    WorkflowMetricsCollector,
)


@pytest.mark.unit
class TestWorkflowMetrics:
    """Test WorkflowMetrics data class functionality."""

    def test_workflow_metrics_initialization(self):
        """Test WorkflowMetrics initialization with defaults."""
        # Act
        metrics = WorkflowMetrics()

        # Assert
        assert metrics.workflow_id is not None
        assert isinstance(metrics.workflow_id, str)
        assert metrics.execution_time == 0.0
        assert metrics.token_usage == {}
        assert metrics.tool_calls == 0
        assert metrics.errors == []
        assert metrics.success is True
        assert isinstance(metrics.start_time, datetime)
        assert metrics.end_time is None

    def test_workflow_metrics_custom_initialization(self):
        """Test WorkflowMetrics initialization with custom values."""
        # Arrange
        custom_id = "test-workflow-123"
        custom_type = "customer_support"
        custom_user_id = "user-456"

        # Act
        metrics = WorkflowMetrics(
            workflow_id=custom_id,
            workflow_type=custom_type,
            user_id=custom_user_id,
        )

        # Assert
        assert metrics.workflow_id == custom_id
        assert metrics.workflow_type == custom_type
        assert metrics.user_id == custom_user_id

    def test_add_token_usage_new_provider(self):
        """Test adding token usage for new provider."""
        # Arrange
        metrics = WorkflowMetrics()

        # Act
        metrics.add_token_usage("openai", 150)

        # Assert
        assert metrics.token_usage["openai"] == 150

    def test_add_token_usage_existing_provider(self):
        """Test adding token usage for existing provider."""
        # Arrange
        metrics = WorkflowMetrics()
        metrics.add_token_usage("openai", 100)

        # Act
        metrics.add_token_usage("openai", 50)

        # Assert
        assert metrics.token_usage["openai"] == 150

    def test_add_error(self):
        """Test adding errors to metrics."""
        # Arrange
        metrics = WorkflowMetrics()
        error_message = "API rate limit exceeded"

        # Act
        metrics.add_error(error_message)

        # Assert
        assert error_message in metrics.errors
        assert metrics.success is False

    def test_finalize_metrics(self):
        """Test finalizing metrics calculation."""
        # Arrange
        metrics = WorkflowMetrics()
        start_time = metrics.start_time

        # Act
        metrics.finalize()

        # Assert
        assert metrics.end_time is not None
        assert metrics.end_time > start_time
        assert metrics.execution_time > 0.0

    def test_total_tokens_calculation(self):
        """Test total token usage calculation."""
        # Arrange
        metrics = WorkflowMetrics()
        metrics.add_token_usage("openai", 100)
        metrics.add_token_usage("anthropic", 50)
        metrics.add_token_usage("openai", 25)

        # Act
        total_tokens = sum(metrics.token_usage.values())

        # Assert
        assert total_tokens == 175


@pytest.mark.unit
class TestWorkflowMetricsCollector:
    """Test WorkflowMetricsCollector functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.collector = WorkflowMetricsCollector()

    def test_start_workflow_tracking(self):
        """Test starting workflow metrics tracking."""
        # Arrange
        workflow_type = "customer_support"
        user_id = "user-123"
        conversation_id = "conv-456"

        # Act
        workflow_id = self.collector.start_workflow_tracking(
            workflow_type=workflow_type,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        # Assert
        assert workflow_id is not None
        assert workflow_id in self.collector.active_workflows
        metrics = self.collector.active_workflows[workflow_id]
        assert metrics.workflow_type == workflow_type
        assert metrics.user_id == user_id
        assert metrics.conversation_id == conversation_id

    def test_update_workflow_metrics(self):
        """Test updating workflow metrics."""
        # Arrange
        workflow_id = self.collector.start_workflow_tracking(
            "test_workflow"
        )

        # Act
        self.collector.update_workflow_metrics(
            workflow_id=workflow_id, tool_calls=3, memory_usage_mb=25.5
        )

        # Assert
        metrics = self.collector.active_workflows[workflow_id]
        assert metrics.tool_calls == 3
        assert metrics.memory_usage_mb == 25.5

    def test_add_token_usage_to_workflow(self):
        """Test adding token usage to specific workflow."""
        # Arrange
        workflow_id = self.collector.start_workflow_tracking(
            "test_workflow"
        )

        # Act
        self.collector.add_token_usage(workflow_id, "openai", 100)
        self.collector.add_token_usage(workflow_id, "openai", 50)

        # Assert
        metrics = self.collector.active_workflows[workflow_id]
        assert metrics.token_usage["openai"] == 150

    def test_add_error_to_workflow(self):
        """Test adding error to specific workflow."""
        # Arrange
        workflow_id = self.collector.start_workflow_tracking(
            "test_workflow"
        )
        error_message = "Tool execution failed"

        # Act
        self.collector.add_error(workflow_id, error_message)

        # Assert
        metrics = self.collector.active_workflows[workflow_id]
        assert error_message in metrics.errors
        assert metrics.success is False

    def test_finish_workflow_tracking(self):
        """Test finishing workflow tracking."""
        # Arrange
        workflow_id = self.collector.start_workflow_tracking(
            "test_workflow"
        )
        self.collector.update_workflow_metrics(
            workflow_id, tool_calls=2
        )

        # Act
        final_metrics = self.collector.finish_workflow_tracking(
            workflow_id
        )

        # Assert
        assert final_metrics is not None
        assert final_metrics.tool_calls == 2
        assert final_metrics.execution_time > 0.0
        assert final_metrics.end_time is not None
        assert workflow_id not in self.collector.active_workflows

    def test_finish_nonexistent_workflow(self):
        """Test finishing tracking for nonexistent workflow."""
        # Arrange
        nonexistent_id = "nonexistent-workflow"

        # Act & Assert
        with pytest.raises(WorkflowMetricsError) as exc_info:
            self.collector.finish_workflow_tracking(nonexistent_id)

        assert "not found" in str(exc_info.value)

    def test_get_workflow_stats(self):
        """Test getting overall workflow statistics."""
        # Arrange
        workflow_id1 = self.collector.start_workflow_tracking("type1")
        self.collector.start_workflow_tracking("type2")

        # Complete one workflow
        self.collector.finish_workflow_tracking(workflow_id1)

        # Act
        stats = self.collector.get_workflow_stats()

        # Assert
        assert stats["active_workflows"] == 1
        assert stats["total_completed"] == 1
        assert "type1" in stats["workflows_by_type"]
        assert "type2" in stats["workflows_by_type"]

    def test_get_performance_metrics(self):
        """Test getting performance metrics."""
        # Arrange
        workflow_id = self.collector.start_workflow_tracking(
            "performance_test"
        )
        self.collector.update_workflow_metrics(
            workflow_id, tool_calls=5, memory_usage_mb=100.0
        )
        self.collector.add_token_usage(workflow_id, "openai", 500)
        self.collector.finish_workflow_tracking(workflow_id)

        # Act
        perf_metrics = self.collector.get_performance_metrics()

        # Assert
        assert perf_metrics["total_workflows"] == 1
        assert perf_metrics["avg_execution_time"] > 0.0
        assert perf_metrics["total_token_usage"] == 500
        assert perf_metrics["avg_tool_calls_per_workflow"] == 5.0

    def test_cleanup_stale_workflows(self):
        """Test cleanup of stale workflows."""
        # Arrange
        workflow_id = self.collector.start_workflow_tracking(
            "stale_test"
        )

        # Manually set old start time to simulate stale workflow
        self.collector.active_workflows[workflow_id].start_time = (
            datetime.now() - timedelta(hours=2)
        )

        # Act
        cleaned_count = self.collector.cleanup_stale_workflows(
            max_age_hours=1
        )

        # Assert
        assert cleaned_count == 1
        assert workflow_id not in self.collector.active_workflows


@pytest.mark.integration
class TestWorkflowMetricsIntegration:
    """Integration tests for workflow metrics system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.collector = WorkflowMetricsCollector()

    @pytest.mark.asyncio
    async def test_complete_workflow_metrics_lifecycle(self):
        """Test complete workflow metrics collection lifecycle."""
        # Arrange
        workflow_type = "integration_test"
        user_id = "user-integration"

        # Act - Start tracking
        workflow_id = self.collector.start_workflow_tracking(
            workflow_type=workflow_type, user_id=user_id
        )

        # Simulate workflow execution
        await asyncio.sleep(0.01)  # Small delay for execution time

        # Update metrics during execution
        self.collector.update_workflow_metrics(
            workflow_id,
            tool_calls=3,
            memory_usage_mb=45.2,
            retrieval_context_size=1500,
        )

        # Add token usage
        self.collector.add_token_usage(workflow_id, "openai", 250)
        self.collector.add_token_usage(workflow_id, "openai", 100)

        # Finish tracking
        final_metrics = self.collector.finish_workflow_tracking(
            workflow_id
        )

        # Assert - Complete metrics
        assert final_metrics.workflow_type == workflow_type
        assert final_metrics.user_id == user_id
        assert final_metrics.execution_time > 0.0
        assert final_metrics.tool_calls == 3
        assert final_metrics.memory_usage_mb == 45.2
        assert final_metrics.retrieval_context_size == 1500
        assert final_metrics.token_usage["openai"] == 350
        assert final_metrics.success is True
        assert final_metrics.end_time is not None

    @pytest.mark.asyncio
    async def test_concurrent_workflow_tracking(self):
        """Test tracking multiple concurrent workflows."""
        # Arrange
        workflow_count = 5
        workflow_ids = []

        # Act - Start multiple workflows
        for i in range(workflow_count):
            workflow_id = self.collector.start_workflow_tracking(
                workflow_type=f"concurrent_test_{i}",
                user_id=f"user-{i}",
            )
            workflow_ids.append(workflow_id)

        # Update each workflow
        for i, workflow_id in enumerate(workflow_ids):
            self.collector.update_workflow_metrics(
                workflow_id,
                tool_calls=i + 1,
                memory_usage_mb=10.0 * (i + 1),
            )

        # Finish all workflows
        final_metrics_list = []
        for workflow_id in workflow_ids:
            final_metrics = self.collector.finish_workflow_tracking(
                workflow_id
            )
            final_metrics_list.append(final_metrics)

        # Assert - All workflows tracked correctly
        assert len(final_metrics_list) == workflow_count
        for i, metrics in enumerate(final_metrics_list):
            assert metrics.tool_calls == i + 1
            assert metrics.memory_usage_mb == 10.0 * (i + 1)
            assert metrics.success is True

    def test_workflow_metrics_aggregation(self):
        """Test metrics aggregation across multiple workflows."""
        # Arrange
        workflow_types = [
            "type_a",
            "type_b",
            "type_a",
            "type_b",
            "type_c",
        ]
        completed_workflows = []

        # Act - Execute multiple workflows
        for workflow_type in workflow_types:
            workflow_id = self.collector.start_workflow_tracking(
                workflow_type
            )
            self.collector.update_workflow_metrics(
                workflow_id, tool_calls=2, memory_usage_mb=20.0
            )
            self.collector.add_token_usage(workflow_id, "openai", 100)
            final_metrics = self.collector.finish_workflow_tracking(
                workflow_id
            )
            completed_workflows.append(final_metrics)

        # Get aggregated stats
        stats = self.collector.get_workflow_stats()
        perf_metrics = self.collector.get_performance_metrics()

        # Assert - Correct aggregation
        assert stats["total_completed"] == 5
        assert stats["workflows_by_type"]["type_a"] == 2
        assert stats["workflows_by_type"]["type_b"] == 2
        assert stats["workflows_by_type"]["type_c"] == 1
        assert perf_metrics["total_workflows"] == 5
        assert perf_metrics["total_token_usage"] == 500
        assert perf_metrics["avg_tool_calls_per_workflow"] == 2.0

    def test_error_handling_in_metrics_collection(self):
        """Test error handling during metrics collection."""
        # Arrange
        workflow_id = self.collector.start_workflow_tracking(
            "error_test"
        )

        # Act - Add multiple errors
        self.collector.add_error(workflow_id, "First error")
        self.collector.add_error(workflow_id, "Second error")

        # Update other metrics
        self.collector.update_workflow_metrics(
            workflow_id, tool_calls=1
        )

        # Finish workflow
        final_metrics = self.collector.finish_workflow_tracking(
            workflow_id
        )

        # Assert - Errors recorded correctly
        assert len(final_metrics.errors) == 2
        assert "First error" in final_metrics.errors
        assert "Second error" in final_metrics.errors
        assert final_metrics.success is False
        assert (
            final_metrics.tool_calls == 1
        )  # Other metrics still recorded
