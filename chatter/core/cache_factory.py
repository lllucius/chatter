"""Cache factory for creating and managing cache instances."""

from enum import Enum
from typing import Any

from chatter.config import settings
from chatter.core.cache_interface import CacheConfig, CacheInterface
from chatter.core.enhanced_memory_cache import EnhancedInMemoryCache
from chatter.core.enhanced_redis_cache import EnhancedRedisCache
from chatter.core.multi_tier_cache import MultiTierCache
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class CacheType(Enum):
    """Cache types for different use cases."""

    MODEL_REGISTRY = "model_registry"
    WORKFLOW = "workflow"
    TOOL = "tool"
    GENERAL = "general"
    SESSION = "session"


class CacheFactory:
    """Simplified factory for creating cache instances."""

    def __init__(self):
        """Initialize cache factory."""
        self._cache_instances: dict[str, CacheInterface] = {}
        logger.debug("Cache factory initialized")

    def _get_config_for_type(self, cache_type: CacheType) -> CacheConfig:
        """Get configuration for cache type.

        Args:
            cache_type: Type of cache

        Returns:
            Cache configuration
        """
        configs = {
            CacheType.MODEL_REGISTRY: CacheConfig(
                default_ttl=settings.cache_model_registry_ttl,
                max_size=settings.cache_max_memory_size // 2,
                eviction_policy=settings.cache_eviction_policy,
                key_prefix="model_registry",
                enable_stats=True,
            ),
            CacheType.WORKFLOW: CacheConfig(
                default_ttl=settings.cache_workflow_ttl,
                max_size=100,
                eviction_policy=settings.cache_eviction_policy,
                key_prefix="workflow",
                enable_stats=True,
            ),
            CacheType.TOOL: CacheConfig(
                default_ttl=settings.cache_tool_ttl,
                max_size=200,
                eviction_policy=settings.cache_eviction_policy,
                key_prefix="tool",
                enable_stats=True,
            ),
            CacheType.GENERAL: CacheConfig(
                default_ttl=settings.cache_ttl,
                max_size=settings.cache_max_memory_size,
                eviction_policy=settings.cache_eviction_policy,
                key_prefix="general",
                enable_stats=True,
            ),
            CacheType.SESSION: CacheConfig(
                default_ttl=settings.cache_session_ttl,
                max_size=settings.cache_max_memory_size,
                eviction_policy="ttl",
                key_prefix="session",
                enable_stats=True,
            ),
        }
        return configs.get(cache_type, configs[CacheType.GENERAL])

    def create_cache(
        self,
        cache_type: CacheType,
        config: CacheConfig | None = None,
        **kwargs,
    ) -> CacheInterface:
        """Create a cache instance.

        Args:
            cache_type: Type of cache to create
            config: Custom cache configuration (uses default if None)
            **kwargs: Additional arguments for cache initialization

        Returns:
            Cache instance
        """
        # Use provided config or default for cache type
        using_default_config = config is None
        if config is None:
            config = self._get_config_for_type(cache_type)

        # Create instance key for reuse
        # For default configs, use cache type only to ensure reuse
        # For custom configs, include config id to allow multiple instances
        if using_default_config:
            instance_key = f"{cache_type.value}_default"
        else:
            instance_key = f"{cache_type.value}_{id(config)}"

        # Return existing instance if available
        if instance_key in self._cache_instances:
            logger.debug(
                "Reusing existing cache instance",
                cache_type=cache_type.value,
                is_default_config=using_default_config,
            )
            return self._cache_instances[instance_key]

        # Create multi-tier cache by default (best performance)
        redis_url = kwargs.get('redis_url')
        l1_config = kwargs.get('l1_config')
        l1_size_ratio = kwargs.get(
            'l1_size_ratio', settings.cache_l1_size_ratio
        )
        cache_instance = MultiTierCache(
            config, l1_config, redis_url, l1_size_ratio
        )

        # Store instance for reuse
        self._cache_instances[instance_key] = cache_instance

        logger.info(
            "Created cache instance",
            cache_type=cache_type.value,
            max_size=config.max_size,
            default_ttl=config.default_ttl,
            key_prefix=config.key_prefix,
        )

        return cache_instance

    def get_cache(self, cache_type: CacheType) -> CacheInterface | None:
        """Get existing cache instance if available.

        Args:
            cache_type: Type of cache to get

        Returns:
            Cache instance or None if not found
        """
        # First try to get the default instance for this cache type
        default_key = f"{cache_type.value}_default"
        if default_key in self._cache_instances:
            return self._cache_instances[default_key]
        
        # If no default instance, look for any instance of this cache type
        for key, instance in self._cache_instances.items():
            if key.startswith(f"{cache_type.value}_"):
                return instance

        return None

    def create_model_registry_cache(self, **kwargs) -> CacheInterface:
        """Create cache for model registry data.

        Args:
            **kwargs: Additional configuration options

        Returns:
            Model registry cache instance
        """
        return self.create_cache(CacheType.MODEL_REGISTRY, **kwargs)

    def create_workflow_cache(self, **kwargs) -> CacheInterface:
        """Create cache for workflow data.

        Args:
            **kwargs: Additional configuration options

        Returns:
            Workflow cache instance
        """
        return self.create_cache(CacheType.WORKFLOW, **kwargs)

    def create_tool_cache(self, **kwargs) -> CacheInterface:
        """Create cache for tool data.

        Args:
            **kwargs: Additional configuration options

        Returns:
            Tool cache instance
        """
        return self.create_cache(CacheType.TOOL, **kwargs)

    def create_session_cache(self, **kwargs) -> CacheInterface:
        """Create cache for session data.

        Args:
            **kwargs: Additional configuration options

        Returns:
            Session cache instance
        """
        return self.create_cache(CacheType.SESSION, **kwargs)

    def create_general_cache(self, **kwargs) -> CacheInterface:
        """Create general-purpose cache.

        Args:
            **kwargs: Additional configuration options

        Returns:
            General cache instance
        """
        return self.create_cache(CacheType.GENERAL, **kwargs)

    async def health_check_all(self) -> dict[str, Any]:
        """Perform health check on all cache instances.

        Returns:
            Health status for all cache instances
        """
        health_results = {}

        for (
            instance_key,
            cache_instance,
        ) in self._cache_instances.items():
            try:
                health_result = await cache_instance.health_check()
                health_results[instance_key] = health_result
            except Exception as e:
                health_results[instance_key] = {
                    "status": "unhealthy",
                    "error": str(e),
                }

        # Overall health summary
        all_healthy = all(
            result.get("status") == "healthy"
            for result in health_results.values()
        )

        overall_status = "healthy" if all_healthy else "degraded"
        if not health_results:
            overall_status = "no_caches"
        elif all(
            result.get("status") == "unhealthy"
            for result in health_results.values()
        ):
            overall_status = "unhealthy"

        return {
            "overall_status": overall_status,
            "cache_instances": health_results,
            "total_instances": len(self._cache_instances),
        }

    async def get_stats_all(self) -> dict[str, Any]:
        """Get statistics for all cache instances.

        Returns:
            Statistics for all cache instances
        """
        stats_results = {}

        for (
            instance_key,
            cache_instance,
        ) in self._cache_instances.items():
            try:
                stats = await cache_instance.get_stats()
                stats_results[instance_key] = {
                    "total_entries": stats.total_entries,
                    "cache_hits": stats.cache_hits,
                    "cache_misses": stats.cache_misses,
                    "hit_rate": stats.hit_rate,
                    "memory_usage": stats.memory_usage,
                    "evictions": stats.evictions,
                    "errors": stats.errors,
                }
            except Exception as e:
                stats_results[instance_key] = {"error": str(e)}

        # Calculate aggregate statistics
        total_entries = sum(
            stats.get("total_entries", 0)
            for stats in stats_results.values()
            if "error" not in stats
        )

        total_hits = sum(
            stats.get("cache_hits", 0)
            for stats in stats_results.values()
            if "error" not in stats
        )

        total_misses = sum(
            stats.get("cache_misses", 0)
            for stats in stats_results.values()
            if "error" not in stats
        )

        total_requests = total_hits + total_misses
        overall_hit_rate = (
            total_hits / total_requests if total_requests > 0 else 0
        )

        return {
            "aggregate": {
                "total_entries": total_entries,
                "total_hits": total_hits,
                "total_misses": total_misses,
                "overall_hit_rate": overall_hit_rate,
                "total_instances": len(self._cache_instances),
            },
            "instances": stats_results,
        }

    async def clear_all(self) -> dict[str, bool]:
        """Clear all cache instances.

        Returns:
            Dictionary of instance key to clear success status
        """
        clear_results = {}

        for (
            instance_key,
            cache_instance,
        ) in self._cache_instances.items():
            try:
                success = await cache_instance.clear()
                clear_results[instance_key] = success
            except Exception as e:
                logger.error(
                    f"Failed to clear cache {instance_key}",
                    error=str(e),
                )
                clear_results[instance_key] = False

        successful_clears = sum(
            1 for success in clear_results.values() if success
        )
        logger.info(
            f"Cleared {successful_clears}/{len(clear_results)} cache instances"
        )

        return clear_results

    def reset(self) -> None:
        """Reset factory by clearing all instances."""
        self._cache_instances.clear()
        logger.info("Cache factory reset, all instances cleared")


# Global factory instance
cache_factory = CacheFactory()


# Convenience functions for common cache types
def get_model_registry_cache(**kwargs) -> CacheInterface:
    """Get model registry cache instance."""
    return cache_factory.create_model_registry_cache(**kwargs)


def get_workflow_cache(**kwargs) -> CacheInterface:
    """Get workflow cache instance."""
    return cache_factory.create_workflow_cache(**kwargs)


def get_tool_cache(**kwargs) -> CacheInterface:
    """Get tool cache instance."""
    return cache_factory.create_tool_cache(**kwargs)


def get_session_cache(**kwargs) -> CacheInterface:
    """Get session cache instance."""
    return cache_factory.create_session_cache(**kwargs)


def get_general_cache(**kwargs) -> CacheInterface:
    """Get general cache instance."""
    return cache_factory.create_general_cache(**kwargs)
