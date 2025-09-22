"""Streamlined performance monitoring for workflows.

This simplified version provides essential performance monitoring
without the complexity of the original system.
"""

import time
from typing import Any

from chatter.core.cache_factory import (
    get_general_cache,
    get_persistent_cache,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class StreamlinedPerformanceMonitor:
    """Simplified performance monitor for workflow execution."""

    def __init__(self):
        """Initialize performance monitor."""
        self.execution_times: list[float] = []
        self.workflow_modes: dict[str, int] = {}
        self.error_counts: dict[str, int] = {}
        self.start_times: dict[str, float] = {}

    def start_workflow(
        self, workflow_id: str, workflow_mode: str
    ) -> None:
        """Start timing a workflow execution."""
        self.start_times[workflow_id] = time.time()
        self.workflow_modes[workflow_mode] = (
            self.workflow_modes.get(workflow_mode, 0) + 1
        )

    def end_workflow(
        self,
        workflow_id: str,
        success: bool = True,
        error_type: str | None = None,
    ) -> float:
        """End timing a workflow execution."""
        if workflow_id not in self.start_times:
            return 0.0

        execution_time = time.time() - self.start_times[workflow_id]
        del self.start_times[workflow_id]

        if success:
            self.execution_times.append(execution_time)
        else:
            error_type = error_type or "unknown_error"
            self.error_counts[error_type] = (
                self.error_counts.get(error_type, 0) + 1
            )

        return execution_time

    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics."""
        if not self.execution_times:
            return {
                "total_executions": 0,
                "avg_execution_time_ms": 0,
                "min_execution_time_ms": 0,
                "max_execution_time_ms": 0,
                "workflow_modes": self.workflow_modes,
                "error_counts": self.error_counts,
            }

        avg_time = sum(self.execution_times) / len(self.execution_times)
        min_time = min(self.execution_times)
        max_time = max(self.execution_times)

        return {
            "total_executions": len(self.execution_times),
            "avg_execution_time_ms": int(avg_time * 1000),
            "min_execution_time_ms": int(min_time * 1000),
            "max_execution_time_ms": int(max_time * 1000),
            "workflow_modes": self.workflow_modes,
            "error_counts": self.error_counts,
        }


# Global instances - simplified version
performance_monitor = StreamlinedPerformanceMonitor()
workflow_cache = get_persistent_cache()
tool_cache = get_general_cache()


class SimpleWorkflowOptimizer:
    """Simple workflow optimizer for basic performance improvements."""

    @staticmethod
    def optimize_workflow_config(
        config: dict[str, Any], usage_stats: dict[str, Any]
    ) -> dict[str, Any]:
        """Optimize workflow configuration based on usage statistics."""
        optimized_config = config.copy()

        # Simple memory window optimization
        if (
            "avg_memory_used" in usage_stats
            and "memory_window" in config
        ):
            avg_used = usage_stats["avg_memory_used"]
            current_window = config["memory_window"]

            if avg_used < current_window * 0.5:
                optimized_config["memory_window"] = max(
                    10, int(avg_used * 1.2)
                )

        # Simple tool calls optimization
        if (
            "avg_tool_calls" in usage_stats
            and "max_tool_calls" in config
        ):
            avg_calls = usage_stats["avg_tool_calls"]
            current_max = config["max_tool_calls"]

            if avg_calls < current_max * 0.5:
                optimized_config["max_tool_calls"] = max(
                    3, int(avg_calls * 1.5)
                )

        return optimized_config

    @staticmethod
    def get_optimization_recommendations(
        stats: dict[str, Any],
    ) -> list[str]:
        """Get simple optimization recommendations."""
        recommendations = []

        if stats.get("avg_execution_time_ms", 0) > 5000:
            recommendations.append("Consider enabling workflow caching")
            recommendations.append(
                "Reduce memory window if not fully utilized"
            )

        error_rate = len(stats.get("error_counts", {}))
        if error_rate > 0:
            recommendations.append("Implement better error handling")

        return recommendations


# Global optimizer instance
workflow_optimizer = SimpleWorkflowOptimizer()
