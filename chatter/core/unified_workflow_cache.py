"""Unified workflow cache using the new cache interface."""

import hashlib
import time
from typing import Any

from chatter.core.cache_factory import get_persistent_cache
from chatter.core.cache_interface import CacheInterface
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class UnifiedWorkflowCache:
    """Unified workflow cache using the new cache interface.

    This replaces the old WorkflowCache with a version that uses
    the unified cache system underneath while maintaining the same API.
    """

    def __init__(
        self, cache: CacheInterface | None = None, max_size: int = 100
    ):
        """Initialize unified workflow cache.

        Args:
            cache: Cache implementation to use (auto-created if None)
            max_size: Maximum number of workflows to cache (for compatibility)
        """
        self.cache = cache or get_persistent_cache()
        self.max_size = max_size

        # Statistics tracking (for compatibility with old API)
        self.cache_hits = 0
        self.cache_misses = 0

        logger.debug(
            "Unified workflow cache initialized", max_size=max_size
        )

    def _generate_cache_key(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any],
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

        # Hash for consistent key length (using SHA256 for security)
        key_hash = hashlib.sha256(config_str.encode()).hexdigest()

        # Use the cache's key generation for consistency
        return self.cache.make_key("workflow", key_hash)

    async def get(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any],
    ) -> Any | None:
        """Get cached workflow if available.

        Args:
            provider_name: LLM provider name
            workflow_type: Type of workflow
            config: Workflow configuration parameters

        Returns:
            Cached workflow instance or None if not found
        """
        cache_key = self._generate_cache_key(
            provider_name, workflow_type, config
        )

        value = await self.cache.get(cache_key)

        if value is not None:
            self.cache_hits += 1
            logger.debug(
                "Workflow cache hit",
                cache_key=cache_key,
                provider=provider_name,
                workflow_type=workflow_type,
            )
            return value

        self.cache_misses += 1
        logger.debug(
            "Workflow cache miss",
            cache_key=cache_key,
            provider=provider_name,
            workflow_type=workflow_type,
        )

        return None

    async def put(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any],
        workflow: Any,
    ) -> bool:
        """Cache compiled workflow.

        Args:
            provider_name: LLM provider name
            workflow_type: Type of workflow
            config: Workflow configuration parameters
            workflow: Compiled workflow instance to cache

        Returns:
            True if successful
        """
        cache_key = self._generate_cache_key(
            provider_name, workflow_type, config
        )

        # Use the cache's default TTL (configured for workflow cache type)
        success = await self.cache.set(cache_key, workflow)

        if success:
            logger.debug(
                "Workflow cached",
                cache_key=cache_key,
                provider=provider_name,
                workflow_type=workflow_type,
            )
        else:
            logger.warning(
                "Failed to cache workflow",
                cache_key=cache_key,
                provider=provider_name,
                workflow_type=workflow_type,
            )

        return success

    async def clear(self) -> bool:
        """Clear all cached workflows.

        Returns:
            True if successful
        """
        success = await self.cache.clear()

        if success:
            # Reset local statistics
            self.cache_hits = 0
            self.cache_misses = 0
            logger.info("Workflow cache cleared")

        return success

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache performance metrics
        """
        # Get stats from underlying cache
        cache_stats = await self.cache.get_stats()

        # Calculate metrics for compatibility with old API
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (
            (self.cache_hits / total_requests)
            if total_requests > 0
            else 0
        )

        return {
            "cache_size": cache_stats.total_entries,
            "max_size": self.max_size,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            # Additional stats from unified cache
            "memory_usage": cache_stats.memory_usage,
            "evictions": cache_stats.evictions,
            "errors": cache_stats.errors,
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on cache.

        Returns:
            Health status information
        """
        return await self.cache.health_check()

    # Additional methods for compatibility and enhanced functionality

    async def delete(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any],
    ) -> bool:
        """Delete specific workflow from cache.

        Args:
            provider_name: LLM provider name
            workflow_type: Type of workflow
            config: Workflow configuration parameters

        Returns:
            True if successful
        """
        cache_key = self._generate_cache_key(
            provider_name, workflow_type, config
        )
        success = await self.cache.delete(cache_key)

        if success:
            logger.debug(
                "Workflow deleted from cache",
                cache_key=cache_key,
                provider=provider_name,
                workflow_type=workflow_type,
            )

        return success

    async def exists(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any],
    ) -> bool:
        """Check if workflow exists in cache.

        Args:
            provider_name: LLM provider name
            workflow_type: Type of workflow
            config: Workflow configuration parameters

        Returns:
            True if workflow is cached
        """
        cache_key = self._generate_cache_key(
            provider_name, workflow_type, config
        )
        return await self.cache.exists(cache_key)

    async def get_cached_workflows(self) -> list[str]:
        """Get list of cached workflow keys.

        Returns:
            List of workflow cache keys
        """
        return await self.cache.keys("workflow")

    async def invalidate_provider(self, provider_name: str) -> int:
        """Invalidate all workflows for a specific provider.

        Args:
            provider_name: Provider name to invalidate

        Returns:
            Number of workflows invalidated
        """
        # Get all workflow keys
        workflow_keys = await self.cache.keys("workflow")

        # This is a simplified approach - in a real implementation,
        # you'd want to store provider info in the key or value
        # For now, we just clear all workflows when a provider changes
        invalidated_count = 0

        for key in workflow_keys:
            # Check if this workflow might be for the given provider
            # This is approximate since we hash the config
            if await self.cache.delete(key):
                invalidated_count += 1

        logger.info(
            "Invalidated workflows for provider",
            provider=provider_name,
            count=invalidated_count,
        )

        return invalidated_count


class UnifiedLazyToolLoader:
    """Unified lazy tool loader using the new cache interface."""

    def __init__(self, cache: CacheInterface | None = None):
        """Initialize unified lazy tool loader.

        Args:
            cache: Cache implementation to use (auto-created if None)
        """
        from chatter.core.cache_factory import get_general_cache

        self.cache = cache or get_general_cache()
        self._all_tools_loaded = False
        self._all_tools_cache_key = self.cache.make_key("all_tools")

        logger.debug("Unified lazy tool loader initialized")

    async def get_tools(
        self, required_tools: list[str] | None = None
    ) -> list[Any]:
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

        # Use mget for efficient batch retrieval
        tool_keys = [
            self.cache.make_key("tool", tool_name)
            for tool_name in required_tools
        ]
        cached_tools = await self.cache.mget(tool_keys)

        for tool_name in required_tools:
            tool_key = self.cache.make_key("tool", tool_name)

            if tool_key in cached_tools:
                tools.append(cached_tools[tool_key])
            else:
                # Load and cache the tool
                tool = await self._load_specific_tool(tool_name)
                if tool:
                    tools.append(tool)
                    await self.cache.set(tool_key, tool)
                else:
                    logger.warning(
                        f"Tool '{tool_name}' not found",
                        tool_name=tool_name,
                    )

        load_time = time.time() - start_time
        logger.debug(
            "Loaded required tools",
            required_tools=required_tools,
            loaded_count=len(tools),
            load_time_ms=int(load_time * 1000),
        )

        return tools

    async def _load_all_tools(self) -> list[Any]:
        """Load all available tools.

        Returns:
            List of all available tool instances
        """
        # Check if all tools are cached
        cached_tools = await self.cache.get(self._all_tools_cache_key)
        if cached_tools is not None and self._all_tools_loaded:
            return cached_tools

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
            tool_cache_items = {}
            for tool in all_tools:
                tool_name = getattr(
                    tool, "name", getattr(tool, "__name__", "unknown")
                )
                if tool_name != "unknown":
                    tool_key = self.cache.make_key("tool", tool_name)
                    tool_cache_items[tool_key] = tool

            # Batch cache individual tools
            if tool_cache_items:
                await self.cache.mset(tool_cache_items)

            # Cache the complete list
            await self.cache.set(self._all_tools_cache_key, all_tools)
            self._all_tools_loaded = True

            load_time = time.time() - start_time
            logger.info(
                "All tools loaded and cached",
                tool_count=len(all_tools),
                mcp_tools=len(mcp_tools),
                builtin_tools=len(builtin_tools),
                load_time_ms=int(load_time * 1000),
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

        # Look for tool in cache
        tool_key = self.cache.make_key("tool", tool_name)
        return await self.cache.get(tool_key)

    async def get_cached_tool_names(self) -> list[str]:
        """Get names of currently cached tools.

        Returns:
            List of cached tool names
        """
        tool_keys = await self.cache.keys("tool")

        # Extract tool names from keys (remove prefix)
        tool_names = []
        for key in tool_keys:
            # Skip the all_tools cache key
            if key == self._all_tools_cache_key:
                continue

            # Extract tool name from key
            if ":" in key:
                tool_name = key.split(":")[
                    -1
                ]  # Get last part after colon
                tool_names.append(tool_name)

        return tool_names

    async def clear_cache(self) -> bool:
        """Clear tool cache.

        Returns:
            True if successful
        """
        success = await self.cache.clear()

        if success:
            self._all_tools_loaded = False
            logger.info("Tool cache cleared")

        return success

    async def get_stats(self) -> dict[str, Any]:
        """Get tool loading statistics.

        Returns:
            Dictionary with tool loading metrics
        """
        cache_stats = await self.cache.get_stats()
        cached_tool_names = await self.get_cached_tool_names()

        return {
            "cached_tools": len(cached_tool_names),
            "all_tools_loaded": self._all_tools_loaded,
            "total_cache_entries": cache_stats.total_entries,
            "cache_hit_rate": cache_stats.hit_rate,
            "memory_usage": cache_stats.memory_usage,
            "tool_names": cached_tool_names,
        }


# Global instances for easy access (maintaining compatibility)
_workflow_cache: UnifiedWorkflowCache | None = None
_lazy_tool_loader: UnifiedLazyToolLoader | None = None


def get_unified_workflow_cache() -> UnifiedWorkflowCache:
    """Get global unified workflow cache instance."""
    global _workflow_cache
    if _workflow_cache is None:
        _workflow_cache = UnifiedWorkflowCache()
    return _workflow_cache


def get_unified_lazy_tool_loader() -> UnifiedLazyToolLoader:
    """Get global unified lazy tool loader instance."""
    global _lazy_tool_loader
    if _lazy_tool_loader is None:
        _lazy_tool_loader = UnifiedLazyToolLoader()
    return _lazy_tool_loader
