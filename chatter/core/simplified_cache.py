"""Simplified cache utilities to replace complex wrapper classes."""

import hashlib
import time
from typing import Any

from chatter.core.cache_factory import (
    get_general_cache,
    get_persistent_cache,
)
from chatter.core.cache_interface import CacheInterface
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class SimplifiedWorkflowCache:
    """Simplified workflow cache using the core cache interface directly.

    Replaces UnifiedWorkflowCache with a much simpler implementation.
    """

    def __init__(self, cache: CacheInterface | None = None):
        """Initialize simplified workflow cache.

        Args:
            cache: Cache implementation to use (auto-created if None)
        """
        self.cache = cache or get_persistent_cache()
        logger.debug("Simplified workflow cache initialized")

    def _make_key(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any],
    ) -> str:
        """Generate cache key for workflow configuration."""
        # Create deterministic string representation
        config_items = sorted(config.items()) if config else []
        config_str = f"{provider_name}:{workflow_type}:{config_items}"

        # Hash for consistent key length
        key_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]

        # Use the cache's key generation for consistency
        return self.cache.make_key("workflow", key_hash)

    async def get(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any],
    ) -> Any | None:
        """Get cached workflow if available."""
        cache_key = self._make_key(provider_name, workflow_type, config)
        value = await self.cache.get(cache_key)

        if value is not None:
            logger.debug(
                "Workflow cache hit",
                provider=provider_name,
                workflow_type=workflow_type,
            )
        else:
            logger.debug(
                "Workflow cache miss",
                provider=provider_name,
                workflow_type=workflow_type,
            )

        return value

    async def put(
        self,
        provider_name: str,
        workflow_type: str,
        config: dict[str, Any],
        workflow: Any,
    ) -> bool:
        """Cache compiled workflow."""
        cache_key = self._make_key(provider_name, workflow_type, config)
        success = await self.cache.set(cache_key, workflow)

        if success:
            logger.debug(
                "Workflow cached",
                provider=provider_name,
                workflow_type=workflow_type,
            )

        return success

    async def clear(self) -> bool:
        """Clear all cached workflows."""
        return await self.cache.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        stats = await self.cache.get_stats()
        return {
            "cache_size": stats.total_entries,
            "cache_hits": stats.cache_hits,
            "cache_misses": stats.cache_misses,
            "hit_rate": stats.hit_rate,
            "memory_usage": stats.memory_usage,
            "evictions": stats.evictions,
            "errors": stats.errors,
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on cache."""
        return await self.cache.health_check()


class SimplifiedToolLoader:
    """Simplified tool loader using the core cache interface directly.

    Replaces UnifiedLazyToolLoader with a much simpler implementation.
    """

    def __init__(self, cache: CacheInterface | None = None):
        """Initialize simplified tool loader.

        Args:
            cache: Cache implementation to use (auto-created if None)
        """
        self.cache = cache or get_general_cache()
        logger.debug("Simplified tool loader initialized")

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
            return await self._load_all_tools()

        tools = []
        start_time = time.time()

        for tool_name in required_tools:
            tool_key = self.cache.make_key("tool", tool_name)
            tool = await self.cache.get(tool_key)

            if tool is not None:
                tools.append(tool)
            else:
                # Load and cache the tool
                tool = await self._load_specific_tool(tool_name)
                if tool:
                    tools.append(tool)
                    await self.cache.set(tool_key, tool)

        load_time = time.time() - start_time
        logger.debug(
            "Loaded required tools",
            required_tools=required_tools,
            loaded_count=len(tools),
            load_time_ms=int(load_time * 1000),
        )

        return tools

    async def _load_all_tools(self) -> list[Any]:
        """Load all available tools."""
        all_tools_key = self.cache.make_key("all_tools")
        cached_tools = await self.cache.get(all_tools_key)

        if cached_tools is not None:
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
            await self.cache.set(all_tools_key, all_tools)

            load_time = time.time() - start_time
            logger.info(
                "All tools loaded and cached",
                tool_count=len(all_tools),
                load_time_ms=int(load_time * 1000),
            )

            return all_tools

        except Exception as e:
            logger.error("Failed to load all tools", error=str(e))
            return []

    async def _load_specific_tool(self, tool_name: str) -> Any | None:
        """Load a specific tool by name."""
        # For now, load all tools and extract the specific one
        # A more optimized implementation could selectively load tools
        all_tools = await self._load_all_tools()

        for tool in all_tools:
            if (
                getattr(tool, "name", getattr(tool, "__name__", ""))
                == tool_name
            ):
                return tool

        return None

    async def clear_cache(self) -> bool:
        """Clear tool cache."""
        return await self.cache.clear()

    async def get_stats(self) -> dict[str, Any]:
        """Get tool loading statistics."""
        stats = await self.cache.get_stats()
        return {
            "total_cache_entries": stats.total_entries,
            "cache_hit_rate": stats.hit_rate,
            "memory_usage": stats.memory_usage,
        }


# Global instances for easy access (maintaining compatibility)
_workflow_cache: SimplifiedWorkflowCache | None = None
_tool_loader: SimplifiedToolLoader | None = None


def get_workflow_cache() -> SimplifiedWorkflowCache:
    """Get global simplified workflow cache instance."""
    global _workflow_cache
    if _workflow_cache is None:
        _workflow_cache = SimplifiedWorkflowCache()
    return _workflow_cache


def get_tool_loader() -> SimplifiedToolLoader:
    """Get global simplified tool loader instance."""
    global _tool_loader
    if _tool_loader is None:
        _tool_loader = SimplifiedToolLoader()
    return _tool_loader


# For backward compatibility
workflow_cache = get_workflow_cache()
lazy_tool_loader = get_tool_loader()
