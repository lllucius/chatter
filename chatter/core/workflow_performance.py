"""Performance optimization utilities for workflows.

This module provides caching and lazy loading features to improve workflow
performance and reduce resource usage.
"""

import asyncio
import time
from typing import Any

from chatter.core.cache_factory import (
    get_general_cache,
    get_persistent_cache,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


# Global instances for easy access - using core cache system directly
_workflow_cache = get_persistent_cache()
_tool_cache = get_general_cache()


def _get_cache_stats_sync(cache):
    """Get cache stats synchronously for monitoring purposes."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we can't run async code
            # Return default stats for monitoring
            return {
                "total_entries": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "hit_rate": 0.0,
                "memory_usage": 0,
                "evictions": 0,
                "errors": 0,
            }
        else:
            return loop.run_until_complete(cache.get_stats())
    except RuntimeError:
        # No event loop - can run async code
        return asyncio.run(cache.get_stats())
    except Exception as e:
        logger.warning(f"Failed to get cache stats: {e}")
        return {
            "total_entries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "hit_rate": 0.0,
            "memory_usage": 0,
            "evictions": 0,
            "errors": 1,
        }


class CacheWrapper:
    """Wrapper to provide sync interface for monitoring."""

    def __init__(self, cache):
        self._cache = cache

    def get_stats(self):
        """Get cache stats synchronously."""
        stats = _get_cache_stats_sync(self._cache)
        return {
            "total_entries": stats.total_entries,
            "cache_hits": stats.cache_hits,
            "cache_misses": stats.cache_misses,
            "hit_rate": stats.hit_rate,
            "memory_usage": stats.memory_usage,
            "evictions": stats.evictions,
            "errors": stats.errors,
        }


# Create sync wrappers for monitoring
workflow_cache = CacheWrapper(_workflow_cache)
lazy_tool_loader = CacheWrapper(_tool_cache)


class PerformanceMonitor:
    """Monitor and track workflow performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.execution_times: list[float] = []
        self.workflow_types: dict[str, int] = {}
        self.error_counts: dict[str, int] = {}
        self.start_times: dict[str, float] = {}

    def start_workflow(
        self, workflow_id: str, workflow_type: str
    ) -> None:
        """Start timing a workflow execution.

        Args:
            workflow_id: Unique identifier for this workflow execution
            workflow_type: Type of workflow being executed
        """
        self.start_times[workflow_id] = time.time()
        self.workflow_types[workflow_type] = (
            self.workflow_types.get(workflow_type, 0) + 1
        )

    def end_workflow(
        self,
        workflow_id: str,
        success: bool = True,
        error_type: str | None = None,
    ) -> float:
        """End timing a workflow execution.

        Args:
            workflow_id: Unique identifier for this workflow execution
            success: Whether the workflow completed successfully
            error_type: Type of error if workflow failed

        Returns:
            Execution time in seconds
        """
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
        """Get comprehensive performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        if not self.execution_times:
            return {
                "total_executions": 0,
                "avg_execution_time_ms": 0,
                "min_execution_time_ms": 0,
                "max_execution_time_ms": 0,
                "workflow_types": self.workflow_types,
                "error_counts": self.error_counts,
                "cache_stats": workflow_cache.get_stats(),
                "tool_stats": lazy_tool_loader.get_stats(),
            }

        avg_time = sum(self.execution_times) / len(self.execution_times)
        min_time = min(self.execution_times)
        max_time = max(self.execution_times)

        return {
            "total_executions": len(self.execution_times),
            "avg_execution_time_ms": int(avg_time * 1000),
            "min_execution_time_ms": int(min_time * 1000),
            "max_execution_time_ms": int(max_time * 1000),
            "workflow_types": self.workflow_types,
            "error_counts": self.error_counts,
            "cache_stats": workflow_cache.get_stats(),
            "tool_stats": lazy_tool_loader.get_stats(),
        }


# Global performance monitor
performance_monitor = PerformanceMonitor()


class BatchProcessor:
    """Batch processor for workflow operations."""

    def __init__(self, batch_size: int = 10, max_concurrent: int = 5):
        """Initialize batch processor."""
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.pending_items = []
        self.processor_func = None

    def set_processor(self, processor_func):
        """Set the processing function."""
        self.processor_func = processor_func

    async def add_item(self, item):
        """Add item to batch and process if batch is full."""
        self.pending_items.append(item)

        if len(self.pending_items) >= self.batch_size:
            return await self._process_batch()

        return None

    async def flush(self):
        """Process any remaining items."""
        if self.pending_items and self.processor_func:
            return await self._process_batch()
        return None

    async def _process_batch(self):
        """Process the current batch."""
        if not self.processor_func or not self.pending_items:
            return None

        batch_items = self.pending_items[: self.batch_size]
        self.pending_items = self.pending_items[self.batch_size :]

        return await self.processor_func(batch_items)


class WorkflowOptimizer:
    """Workflow optimization utility for improving performance and efficiency."""

    def __init__(self):
        """Initialize workflow optimizer."""
        self.cache = workflow_cache
        self.tool_loader = lazy_tool_loader
        self.monitor = performance_monitor
        self.optimization_history = []

    def optimize_workflow_config(
        self, config: dict[str, Any], usage_stats: dict[str, Any]
    ) -> dict[str, Any]:
        """Optimize workflow configuration based on usage statistics."""
        optimized_config = config.copy()

        # Optimize memory window based on actual usage
        if (
            "avg_memory_used" in usage_stats
            and "memory_window" in config
        ):
            avg_used = usage_stats["avg_memory_used"]
            current_window = config["memory_window"]

            # Reduce memory window if much less is being used
            if avg_used < current_window * 0.5:
                optimized_config["memory_window"] = max(
                    10, int(avg_used * 1.2)
                )

        # Optimize tool calls based on actual usage
        if (
            "avg_tool_calls" in usage_stats
            and "max_tool_calls" in config
        ):
            avg_calls = usage_stats["avg_tool_calls"]
            current_max = config["max_tool_calls"]

            # Reduce max tool calls if much less is being used
            if avg_calls < current_max * 0.5:
                optimized_config["max_tool_calls"] = max(
                    3, int(avg_calls * 1.5)
                )

        # Optimize tools list based on usage
        if "tool_usage" in usage_stats and "tools" in config:
            tool_usage = usage_stats["tool_usage"]
            current_tools = config["tools"]

            # Keep only frequently used tools (usage > 5% of total)
            total_usage = sum(tool_usage.values())
            threshold = total_usage * 0.05

            optimized_tools = [
                tool
                for tool in current_tools
                if tool_usage.get(tool, 0) > threshold
            ]

            if optimized_tools:  # Ensure we keep at least some tools
                optimized_config["tools"] = optimized_tools

        return optimized_config

    async def benchmark_workflow_variants(
        self,
        base_config: dict[str, Any],
        variants: list[dict[str, Any]],
        execute_func,
    ) -> list[dict[str, Any]]:
        """Benchmark different workflow variants and return results sorted by performance."""
        results = []

        for variant in variants:
            # Merge variant with base config
            test_config = base_config.copy()
            test_config.update(variant)

            # Run benchmark
            execution_times = []
            for _ in range(3):  # Run 3 times for average
                start_time = time.time()
                try:
                    await execute_func(test_config)
                    execution_time = time.time() - start_time
                    execution_times.append(execution_time)
                except Exception as e:
                    logger.error(
                        f"Benchmark failed for variant {variant}: {e}"
                    )
                    execution_times.append(float("inf"))

            avg_time = sum(execution_times) / len(execution_times)

            results.append(
                {
                    "config": test_config,
                    "avg_execution_time": avg_time,
                    "execution_times": execution_times,
                    "variant": variant,
                }
            )

        # Sort by performance (fastest first)
        results.sort(key=lambda x: x["avg_execution_time"])

        return results

    def analyze_performance_bottlenecks(
        self, workflow_metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze workflow performance and identify bottlenecks."""
        bottlenecks = {}

        # Analyze tool usage patterns
        if "tool_execution_times" in workflow_metrics:
            tool_times = workflow_metrics["tool_execution_times"]
            if tool_times:
                avg_tool_time = sum(tool_times.values()) / len(
                    tool_times
                )
                slow_tools = {
                    tool: time
                    for tool, time in tool_times.items()
                    if time > avg_tool_time * 2
                }
                if slow_tools:
                    bottlenecks["slow_tools"] = slow_tools

        # Analyze memory usage
        if "memory_usage" in workflow_metrics:
            memory_stats = workflow_metrics["memory_usage"]
            if (
                memory_stats.get("peak_usage", 0)
                > memory_stats.get("allocated", 0) * 0.9
            ):
                bottlenecks["high_memory_usage"] = memory_stats

        # Analyze execution times
        if "execution_times" in workflow_metrics:
            exec_times = workflow_metrics["execution_times"]
            if exec_times:
                avg_time = sum(exec_times) / len(exec_times)
                if avg_time > 5.0:  # 5 seconds threshold
                    bottlenecks["slow_execution"] = {
                        "avg_time": avg_time,
                        "max_time": max(exec_times),
                        "count": len(exec_times),
                    }

        return bottlenecks

    def get_optimization_recommendations(
        self, analysis: dict[str, Any]
    ) -> list[str]:
        """Get optimization recommendations based on performance analysis."""
        recommendations = []

        if "slow_tools" in analysis:
            recommendations.append(
                "Consider caching or replacing slow tools"
            )
            recommendations.append("Implement tool execution timeout")

        if "high_memory_usage" in analysis:
            recommendations.append("Reduce memory window size")
            recommendations.append(
                "Implement memory cleanup between operations"
            )

        if "slow_execution" in analysis:
            recommendations.append("Enable workflow caching")
            recommendations.append("Reduce maximum tool calls")
            recommendations.append("Implement async tool execution")

        return recommendations
