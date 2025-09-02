"""Workflow metrics and monitoring system for LangGraph workflows."""

# Simple logger fallback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class WorkflowMetrics:
    """Comprehensive metrics for workflow execution."""

    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    workflow_type: str = ""
    execution_time: float = 0.0
    token_usage: dict[str, int] = field(default_factory=dict)
    tool_calls: int = 0
    errors: list[str] = field(default_factory=list)
    user_satisfaction: float | None = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    user_id: str = ""
    conversation_id: str = ""
    provider_name: str = ""
    model_name: str = ""
    retrieval_context_size: int = 0
    memory_usage_mb: float = 0.0
    workflow_config: dict[str, Any] = field(default_factory=dict)
    success: bool = True

    def add_token_usage(self, provider: str, tokens: int) -> None:
        """Add token usage for a specific provider."""
        if provider in self.token_usage:
            self.token_usage[provider] += tokens
        else:
            self.token_usage[provider] = tokens

    def add_error(self, error_message: str) -> None:
        """Add an error to the metrics."""
        self.errors.append(error_message)
        self.success = False

    def finalize(self) -> None:
        """Finalize metrics by setting end time and calculating execution time."""
        self.end_time = datetime.now()
        self.execution_time = (
            self.end_time - self.start_time
        ).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "execution_time": self.execution_time,
            "token_usage": self.token_usage,
            "tool_calls": self.tool_calls,
            "errors": self.errors,
            "user_satisfaction": self.user_satisfaction,
            "start_time": self.start_time.isoformat(),
            "end_time": (
                self.end_time.isoformat() if self.end_time else None
            ),
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "retrieval_context_size": self.retrieval_context_size,
            "memory_usage_mb": self.memory_usage_mb,
            "workflow_config": self.workflow_config,
            "success": self.success,
        }


class WorkflowMetricsCollector:
    """Collector for workflow metrics with aggregation capabilities."""

    def __init__(self, max_history: int = 10000):
        """Initialize metrics collector.

        Args:
            max_history: Maximum number of workflow metrics to keep in memory
        """
        self.max_history = max_history
        self.metrics_history: list[WorkflowMetrics] = []
        self.active_workflows: dict[str, WorkflowMetrics] = {}

    def start_workflow_tracking(
        self,
        workflow_type: str,
        user_id: str,
        conversation_id: str,
        provider_name: str = "",
        model_name: str = "",
        workflow_config: dict[str, Any] | None = None,
    ) -> str:
        """Start tracking a new workflow execution.

        Args:
            workflow_type: Type of workflow being executed
            user_id: ID of the user initiating the workflow
            conversation_id: ID of the conversation
            provider_name: Name of the LLM provider
            model_name: Name of the model being used
            workflow_config: Configuration parameters for the workflow

        Returns:
            Workflow ID for tracking
        """
        metrics = WorkflowMetrics(
            workflow_type=workflow_type,
            user_id=user_id,
            conversation_id=conversation_id,
            provider_name=provider_name,
            model_name=model_name,
            workflow_config=workflow_config or {},
        )

        self.active_workflows[metrics.workflow_id] = metrics
        logger.info(
            "Started workflow tracking",
            workflow_id=metrics.workflow_id,
            workflow_type=workflow_type,
            user_id=user_id,
        )

        return metrics.workflow_id

    def update_workflow_metrics(
        self,
        workflow_id: str,
        token_usage: dict[str, int] | None = None,
        tool_calls: int | None = None,
        retrieval_context_size: int | None = None,
        memory_usage_mb: float | None = None,
        error: str | None = None,
    ) -> None:
        """Update metrics for an active workflow.

        Args:
            workflow_id: ID of the workflow to update
            token_usage: Token usage to add
            tool_calls: Number of tool calls to add
            retrieval_context_size: Size of retrieval context
            memory_usage_mb: Memory usage in MB
            error: Error message to add
        """
        if workflow_id not in self.active_workflows:
            logger.warning(
                "Attempted to update metrics for unknown workflow",
                workflow_id=workflow_id,
            )
            return

        metrics = self.active_workflows[workflow_id]

        if token_usage:
            for provider, tokens in token_usage.items():
                metrics.add_token_usage(provider, tokens)

        if tool_calls is not None:
            metrics.tool_calls += tool_calls

        if retrieval_context_size is not None:
            metrics.retrieval_context_size = retrieval_context_size

        if memory_usage_mb is not None:
            metrics.memory_usage_mb = memory_usage_mb

        if error:
            metrics.add_error(error)

    def finish_workflow_tracking(
        self, workflow_id: str, user_satisfaction: float | None = None
    ) -> WorkflowMetrics | None:
        """Finish tracking a workflow and move it to history.

        Args:
            workflow_id: ID of the workflow to finish
            user_satisfaction: Optional user satisfaction rating (0.0-1.0)

        Returns:
            Finalized workflow metrics or None if workflow not found
        """
        if workflow_id not in self.active_workflows:
            logger.warning(
                "Attempted to finish tracking for unknown workflow",
                workflow_id=workflow_id,
            )
            return None

        metrics = self.active_workflows.pop(workflow_id)

        if user_satisfaction is not None:
            metrics.user_satisfaction = user_satisfaction

        metrics.finalize()

        # Add to history and maintain max size
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)

        logger.info(
            "Finished workflow tracking",
            workflow_id=workflow_id,
            execution_time=metrics.execution_time,
            success=metrics.success,
        )

        return metrics

    def get_workflow_stats(
        self,
        workflow_type: str | None = None,
        user_id: str | None = None,
        hours: int = 24,
    ) -> dict[str, Any]:
        """Get aggregated workflow statistics.

        Args:
            workflow_type: Filter by workflow type
            user_id: Filter by user ID
            hours: Number of hours to look back

        Returns:
            Dictionary with aggregated statistics
        """
        # Filter metrics based on criteria
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        filtered_metrics = [
            m
            for m in self.metrics_history
            if m.start_time.timestamp() > cutoff_time
            and (not workflow_type or m.workflow_type == workflow_type)
            and (not user_id or m.user_id == user_id)
        ]

        if not filtered_metrics:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "total_tokens": 0,
                "total_tool_calls": 0,
                "error_count": 0,
                "workflow_types": {},
                "providers": {},
            }

        # Calculate statistics
        total_executions = len(filtered_metrics)
        successful_executions = sum(
            1 for m in filtered_metrics if m.success
        )
        success_rate = successful_executions / total_executions

        execution_times = [m.execution_time for m in filtered_metrics]
        avg_execution_time = sum(execution_times) / len(execution_times)

        total_tokens = sum(
            sum(usage.values())
            for m in filtered_metrics
            for usage in [m.token_usage]
            if usage
        )

        total_tool_calls = sum(m.tool_calls for m in filtered_metrics)
        error_count = sum(len(m.errors) for m in filtered_metrics)

        # Group by workflow type
        workflow_types = {}
        for m in filtered_metrics:
            if m.workflow_type not in workflow_types:
                workflow_types[m.workflow_type] = 0
            workflow_types[m.workflow_type] += 1

        # Group by provider
        providers = {}
        for m in filtered_metrics:
            if m.provider_name and m.provider_name not in providers:
                providers[m.provider_name] = 0
            if m.provider_name:
                providers[m.provider_name] += 1

        return {
            "total_executions": total_executions,
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time,
            "total_tokens": total_tokens,
            "total_tool_calls": total_tool_calls,
            "error_count": error_count,
            "workflow_types": workflow_types,
            "providers": providers,
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
        }

    def get_recent_errors(
        self, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get recent workflow errors.

        Args:
            limit: Maximum number of errors to return

        Returns:
            List of recent errors with context
        """
        errors = []
        for metrics in reversed(self.metrics_history):
            if metrics.errors:
                for error in metrics.errors:
                    errors.append(
                        {
                            "workflow_id": metrics.workflow_id,
                            "workflow_type": metrics.workflow_type,
                            "user_id": metrics.user_id,
                            "timestamp": metrics.start_time.isoformat(),
                            "error": error,
                            "provider": metrics.provider_name,
                            "model": metrics.model_name,
                        }
                    )

                    if len(errors) >= limit:
                        return errors

        return errors


# Global instance for easy access
workflow_metrics_collector = WorkflowMetricsCollector()
