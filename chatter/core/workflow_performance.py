"""Performance optimization utilities for workflows.

This module provides caching and lazy loading features to improve workflow
performance and reduce resource usage.
"""

import hashlib
import time
from typing import Any

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowCache:
    """LRU cache for compiled workflows to avoid repeated compilation."""

    def __init__(self, max_size: int = 100):
        """Initialize workflow cache.

        Args:
            max_size: Maximum number of workflows to cache
        """
        self.cache: dict[str, Any] = {}
        self.access_times: dict[str, float] = {}
        self.max_size = max_size
        self.cache_hits = 0
        self.cache_misses = 0

    def _generate_cache_key(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any]
    ) -> str:
        """Generate deterministic cache key for workflow configuration.

        Args:
            provider_name: LLM provider name
            workflow_type: Type of workflow
            config: Workflow configuration parameters

        Returns:
            Cache key string
        """
        # Create deterministic string representation
        config_items = sorted(config.items()) if config else []
        config_str = f"{provider_name}:{workflow_type}:{config_items}"

        # Hash for consistent key length
        return hashlib.md5(config_str.encode()).hexdigest()

    def get(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any]
    ) -> Any | None:
        """Get cached workflow if available.

        Args:
            provider_name: LLM provider name
            workflow_type: Type of workflow
            config: Workflow configuration parameters

        Returns:
            Cached workflow instance or None if not found
        """
        cache_key = self._generate_cache_key(provider_name, workflow_type, config)

        if cache_key in self.cache:
            # Update access time
            self.access_times[cache_key] = time.time()
            self.cache_hits += 1

            logger.debug(
                "Workflow cache hit",
                cache_key=cache_key,
                provider=provider_name,
                workflow_type=workflow_type
            )

            return self.cache[cache_key]

        self.cache_misses += 1
        logger.debug(
            "Workflow cache miss",
            cache_key=cache_key,
            provider=provider_name,
            workflow_type=workflow_type
        )

        return None

    def put(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any],
        workflow: Any
    ) -> None:
        """Cache compiled workflow.

        Args:
            provider_name: LLM provider name
            workflow_type: Type of workflow
            config: Workflow configuration parameters
            workflow: Compiled workflow instance to cache
        """
        cache_key = self._generate_cache_key(provider_name, workflow_type, config)

        # Evict least recently used if at capacity
        if len(self.cache) >= self.max_size and cache_key not in self.cache:
            self._evict_lru()

        self.cache[cache_key] = workflow
        self.access_times[cache_key] = time.time()

        logger.debug(
            "Workflow cached",
            cache_key=cache_key,
            provider=provider_name,
            workflow_type=workflow_type,
            cache_size=len(self.cache)
        )

    def _evict_lru(self) -> None:
        """Evict least recently used item from cache."""
        if not self.access_times:
            return

        # Find least recently used key
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])

        # Remove from cache
        del self.cache[lru_key]
        del self.access_times[lru_key]

        logger.debug("Evicted LRU workflow from cache", cache_key=lru_key)

    def clear(self) -> None:
        """Clear all cached workflows."""
        cache_size = len(self.cache)
        self.cache.clear()
        self.access_times.clear()
        self.cache_hits = 0
        self.cache_misses = 0

        logger.info("Workflow cache cleared", previous_size=cache_size)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache performance metrics
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests) if total_requests > 0 else 0

        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }


class LazyToolLoader:
    """Lazy loading for tools to improve performance by loading only required tools."""

    def __init__(self):
        """Initialize lazy tool loader."""
        self._tool_cache: dict[str, Any] = {}
        self._all_tools_loaded = False
        self._all_tools: list[Any] | None = None
        self.load_times: dict[str, float] = {}

    async def get_tools(self, required_tools: list[str] | None = None) -> list[Any]:
        """Get tools, loading only what's needed.

        Args:
            required_tools: List of specific tool names to load, or None for all tools

        Returns:
            List of tool instances
        """
        if not required_tools:
            # Load all tools (current behavior for backward compatibility)
            return await self._load_all_tools()

        # Load only required tools
        tools = []
        start_time = time.time()

        for tool_name in required_tools:
            tool = await self._get_cached_tool(tool_name)
            if tool:
                tools.append(tool)
            else:
                logger.warning(f"Tool '{tool_name}' not found", tool_name=tool_name)

        load_time = time.time() - start_time
        logger.debug(
            "Loaded required tools",
            required_tools=required_tools,
            loaded_count=len(tools),
            load_time_ms=int(load_time * 1000)
        )

        return tools

    async def _get_cached_tool(self, tool_name: str) -> Any | None:
        """Get tool from cache or load it.

        Args:
            tool_name: Name of the tool to load

        Returns:
            Tool instance or None if not found
        """
        if tool_name in self._tool_cache:
            return self._tool_cache[tool_name]

        # Load tool and cache it
        start_time = time.time()
        tool = await self._load_specific_tool(tool_name)

        if tool:
            self._tool_cache[tool_name] = tool
            self.load_times[tool_name] = time.time() - start_time

            logger.debug(
                "Tool loaded and cached",
                tool_name=tool_name,
                load_time_ms=int(self.load_times[tool_name] * 1000)
            )

        return tool

    async def _load_all_tools(self) -> list[Any]:
        """Load all available tools.

        Returns:
            List of all available tool instances
        """
        if self._all_tools_loaded and self._all_tools:
            return self._all_tools

        start_time = time.time()

        try:
            # Import here to avoid circular imports
            from chatter.services.mcp import BuiltInTools, mcp_service

            # Load MCP tools
            mcp_tools = await mcp_service.get_tools()

            # Load built-in tools
            builtin_tools = BuiltInTools.create_builtin_tools()

            # Combine all tools
            all_tools = mcp_tools + builtin_tools

            # Cache all tools for future use
            for tool in all_tools:
                tool_name = getattr(tool, "name", getattr(tool, "__name__", "unknown"))
                if tool_name != "unknown":
                    self._tool_cache[tool_name] = tool

            self._all_tools = all_tools
            self._all_tools_loaded = True

            load_time = time.time() - start_time
            logger.info(
                "All tools loaded",
                tool_count=len(all_tools),
                mcp_tools=len(mcp_tools),
                builtin_tools=len(builtin_tools),
                load_time_ms=int(load_time * 1000)
            )

            return all_tools

        except Exception as e:
            logger.error("Failed to load all tools", error=str(e))
            return []

    async def _load_specific_tool(self, tool_name: str) -> Any | None:
        """Load a specific tool by name.

        Args:
            tool_name: Name of the tool to load

        Returns:
            Tool instance or None if not found
        """
        # If we haven't loaded all tools yet, try to find the specific tool
        if not self._all_tools_loaded:
            await self._load_all_tools()

        # Look for tool in cache (populated by _load_all_tools)
        return self._tool_cache.get(tool_name)

    def get_cached_tool_names(self) -> list[str]:
        """Get names of currently cached tools.

        Returns:
            List of cached tool names
        """
        return list(self._tool_cache.keys())

    def clear_cache(self) -> None:
        """Clear tool cache."""
        cache_size = len(self._tool_cache)
        self._tool_cache.clear()
        self._all_tools_loaded = False
        self._all_tools = None
        self.load_times.clear()

        logger.info("Tool cache cleared", previous_size=cache_size)

    def get_stats(self) -> dict[str, Any]:
        """Get tool loading statistics.

        Returns:
            Dictionary with tool loading metrics
        """
        total_load_time = sum(self.load_times.values())
        avg_load_time = total_load_time / len(self.load_times) if self.load_times else 0

        return {
            "cached_tools": len(self._tool_cache),
            "all_tools_loaded": self._all_tools_loaded,
            "total_tools": len(self._all_tools) if self._all_tools else 0,
            "total_load_time_ms": int(total_load_time * 1000),
            "average_load_time_ms": int(avg_load_time * 1000),
            "tool_names": list(self._tool_cache.keys())
        }


# Global instances for easy access
workflow_cache = WorkflowCache()
lazy_tool_loader = LazyToolLoader()


class PerformanceMonitor:
    """Monitor and track workflow performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.execution_times: list[float] = []
        self.workflow_types: dict[str, int] = {}
        self.error_counts: dict[str, int] = {}
        self.start_times: dict[str, float] = {}

    def start_workflow(self, workflow_id: str, workflow_type: str) -> None:
        """Start timing a workflow execution.

        Args:
            workflow_id: Unique identifier for this workflow execution
            workflow_type: Type of workflow being executed
        """
        self.start_times[workflow_id] = time.time()
        self.workflow_types[workflow_type] = self.workflow_types.get(workflow_type, 0) + 1

    def end_workflow(self, workflow_id: str, success: bool = True, error_type: str | None = None) -> float:
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
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

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
                "tool_stats": lazy_tool_loader.get_stats()
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
            "tool_stats": lazy_tool_loader.get_stats()
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
        
        batch_items = self.pending_items[:self.batch_size]
        self.pending_items = self.pending_items[self.batch_size:]
        
        return await self.processor_func(batch_items)


class WorkflowOptimizer:
    """Workflow optimization utility for improving performance and efficiency."""
    
    def __init__(self):
        """Initialize workflow optimizer."""
        self.cache = workflow_cache
        self.tool_loader = lazy_tool_loader
        self.monitor = performance_monitor
        self.optimization_history = []
    
    def optimize_workflow_config(self, config: dict[str, Any], usage_stats: dict[str, Any]) -> dict[str, Any]:
        """Optimize workflow configuration based on usage statistics."""
        optimized_config = config.copy()
        
        # Optimize memory window based on actual usage
        if "avg_memory_used" in usage_stats and "memory_window" in config:
            avg_used = usage_stats["avg_memory_used"]
            current_window = config["memory_window"]
            
            # Reduce memory window if much less is being used
            if avg_used < current_window * 0.5:
                optimized_config["memory_window"] = max(10, int(avg_used * 1.2))
        
        # Optimize tool calls based on actual usage
        if "avg_tool_calls" in usage_stats and "max_tool_calls" in config:
            avg_calls = usage_stats["avg_tool_calls"]
            current_max = config["max_tool_calls"]
            
            # Reduce max tool calls if much less is being used
            if avg_calls < current_max * 0.5:
                optimized_config["max_tool_calls"] = max(3, int(avg_calls * 1.5))
        
        # Optimize tools list based on usage
        if "tool_usage" in usage_stats and "tools" in config:
            tool_usage = usage_stats["tool_usage"]
            current_tools = config["tools"]
            
            # Keep only frequently used tools (usage > 5% of total)
            total_usage = sum(tool_usage.values())
            threshold = total_usage * 0.05
            
            optimized_tools = [
                tool for tool in current_tools
                if tool_usage.get(tool, 0) > threshold
            ]
            
            if optimized_tools:  # Ensure we keep at least some tools
                optimized_config["tools"] = optimized_tools
        
        return optimized_config
    
    async def benchmark_workflow_variants(
        self, 
        base_config: dict[str, Any], 
        variants: list[dict[str, Any]],
        execute_func
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
                    logger.error(f"Benchmark failed for variant {variant}: {e}")
                    execution_times.append(float('inf'))
            
            avg_time = sum(execution_times) / len(execution_times)
            
            results.append({
                "config": test_config,
                "avg_execution_time": avg_time,
                "execution_times": execution_times,
                "variant": variant
            })
        
        # Sort by performance (fastest first)
        results.sort(key=lambda x: x["avg_execution_time"])
        
        return results
    
    def analyze_performance_bottlenecks(self, workflow_metrics: dict[str, Any]) -> dict[str, Any]:
        """Analyze workflow performance and identify bottlenecks."""
        bottlenecks = {}
        
        # Analyze tool usage patterns
        if "tool_execution_times" in workflow_metrics:
            tool_times = workflow_metrics["tool_execution_times"]
            if tool_times:
                avg_tool_time = sum(tool_times.values()) / len(tool_times)
                slow_tools = {
                    tool: time for tool, time in tool_times.items()
                    if time > avg_tool_time * 2
                }
                if slow_tools:
                    bottlenecks["slow_tools"] = slow_tools
        
        # Analyze memory usage
        if "memory_usage" in workflow_metrics:
            memory_stats = workflow_metrics["memory_usage"]
            if memory_stats.get("peak_usage", 0) > memory_stats.get("allocated", 0) * 0.9:
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
                        "count": len(exec_times)
                    }
        
        return bottlenecks
    
    def get_optimization_recommendations(self, analysis: dict[str, Any]) -> list[str]:
        """Get optimization recommendations based on performance analysis."""
        recommendations = []
        
        if "slow_tools" in analysis:
            recommendations.append("Consider caching or replacing slow tools")
            recommendations.append("Implement tool execution timeout")
        
        if "high_memory_usage" in analysis:
            recommendations.append("Reduce memory window size")
            recommendations.append("Implement memory cleanup between operations")
        
        if "slow_execution" in analysis:
            recommendations.append("Enable workflow caching")
            recommendations.append("Reduce maximum tool calls")
            recommendations.append("Implement async tool execution")
        
        return recommendations
