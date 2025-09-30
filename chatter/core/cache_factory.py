"""Simplified cache factory for creating cache instances."""

from enum import Enum
from typing import Any

from chatter.config import settings
from chatter.core.cache import (
    CacheConfig,
    CacheInterface,
    MemoryCache,
    MultiTierCache,
    RedisCache,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class CacheType(Enum):
    """Cache types for different use cases."""

    GENERAL = "general"  # General purpose caching
    SESSION = "session"  # Session-specific data
    PERSISTENT = "persistent"  # Long-term data caching


class SimplifiedCacheFactory:
    """Simplified factory for creating cache instances."""

    def __init__(self):
        """Initialize cache factory."""
        self._cache_instances: dict[str, CacheInterface] = {}
        logger.debug("Simplified cache factory initialized")

    def _get_config_for_type(
        self, cache_type: CacheType
    ) -> CacheConfig:
        """Get configuration for cache type."""
        configs = {
            CacheType.GENERAL: CacheConfig(
                default_ttl=settings.cache_ttl_default,
                max_size=settings.cache_max_size,
                eviction_policy=settings.cache_eviction_policy,
                key_prefix="general",
                enable_stats=True,
                disabled=settings.cache_disabled,
            ),
            CacheType.SESSION: CacheConfig(
                default_ttl=settings.cache_ttl_short,
                max_size=settings.cache_max_size // 2,
                eviction_policy="ttl",
                key_prefix="session",
                enable_stats=True,
                disabled=settings.cache_disabled,
            ),
            CacheType.PERSISTENT: CacheConfig(
                default_ttl=settings.cache_ttl_long,
                max_size=settings.cache_max_size * 2,
                eviction_policy=settings.cache_eviction_policy,
                key_prefix="persistent",
                enable_stats=True,
                disabled=settings.cache_disabled,
            ),
        }
        return configs.get(cache_type, configs[CacheType.GENERAL])

    def create_cache(
        self,
        cache_type: CacheType,
        config: CacheConfig | None = None,
        **kwargs,
    ) -> CacheInterface:
        """Create a cache instance."""
        # Use provided config or default for cache type
        using_default_config = config is None
        if config is None:
            config = self._get_config_for_type(cache_type)

        # Create instance key for reuse
        if using_default_config:
            instance_key = f"{cache_type.value}_default"
        else:
            instance_key = f"{cache_type.value}_{id(config)}"

        # Return existing instance if available
        if instance_key in self._cache_instances:
            logger.debug(
                "Reusing existing cache instance",
                cache_type=cache_type.value,
            )
            return self._cache_instances[instance_key]

        # Create cache based on backend configuration
        backend = settings.cache_backend
        redis_url = kwargs.get("redis_url")
        l1_size_ratio = kwargs.get("l1_size_ratio", 0.1)

        if backend == "memory":
            cache_instance = MemoryCache(config)
        elif backend == "redis":
            cache_instance = RedisCache(config, redis_url)
        else:  # multi_tier (default)
            cache_instance = MultiTierCache(
                config, None, redis_url, l1_size_ratio
            )

        # Store instance for reuse
        self._cache_instances[instance_key] = cache_instance

        logger.info(
            "Created cache instance",
            cache_type=cache_type.value,
            backend=backend,
            max_size=config.max_size,
            default_ttl=config.default_ttl,
        )

        return cache_instance

    def get_cache(self, cache_type: CacheType) -> CacheInterface | None:
        """Get existing cache instance if available."""
        instance_key = f"{cache_type.value}_default"
        return self._cache_instances.get(instance_key)

    def clear_all_caches(self) -> None:
        """Clear all cache instances."""
        for cache in self._cache_instances.values():
            try:
                import asyncio

                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule for later execution
                    asyncio.create_task(cache.clear())
                else:
                    loop.run_until_complete(cache.clear())
            except Exception as e:
                logger.warning(f"Failed to clear cache: {e}")

    def get_all_stats(self) -> dict[str, Any]:
        """Get statistics from all cache instances."""
        stats = {}
        for key, cache in self._cache_instances.items():
            try:
                import asyncio

                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Return placeholder for async context
                    stats[key] = {"status": "available"}
                else:
                    stats[key] = loop.run_until_complete(
                        cache.get_stats()
                    )
            except Exception as e:
                stats[key] = {"error": str(e)}
        return stats

    async def health_check_all(self) -> dict[str, Any]:
        """Get health status for all cache instances."""
        health_results = {}
        healthy_count = 0
        total_count = len(self._cache_instances)

        for key, cache in self._cache_instances.items():
            try:
                health = await cache.health_check()
                health_results[key] = health
                if health.get("status") == "healthy":
                    healthy_count += 1
            except Exception as e:
                health_results[key] = {
                    "status": "unhealthy",
                    "error": str(e),
                }

        # Determine overall status
        if total_count == 0:
            overall_status = "healthy"  # No caches to check
        elif healthy_count == total_count:
            overall_status = "healthy"
        elif healthy_count > 0:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        return {
            "overall_status": overall_status,
            "total_instances": total_count,
            "healthy_instances": healthy_count,
            "cache_instances": health_results,
        }

    async def get_stats_all(self) -> dict[str, Any]:
        """Get statistics for all cache instances."""
        stats_results = {}
        total_entries = 0
        total_hits = 0
        total_misses = 0

        for key, cache in self._cache_instances.items():
            try:
                stats = await cache.get_stats()
                stats_results[key] = stats
                # Aggregate some metrics
                if isinstance(stats, dict):
                    total_entries += stats.get("total_entries", 0)
                    total_hits += stats.get("cache_hits", 0)
                    total_misses += stats.get("cache_misses", 0)
            except Exception as e:
                stats_results[key] = {"error": str(e)}

        return {
            "aggregate": {
                "total_instances": len(self._cache_instances),
                "total_entries": total_entries,
                "total_hits": total_hits,
                "total_misses": total_misses,
                "overall_hit_rate": (
                    total_hits / max(1, total_hits + total_misses)
                )
                * 100,
            },
            "instances": stats_results,
        }


# Global factory instance
cache_factory = SimplifiedCacheFactory()


# Convenience functions for common cache types
def get_general_cache(**kwargs) -> CacheInterface:
    """Get general-purpose cache instance."""
    return cache_factory.create_cache(CacheType.GENERAL, **kwargs)


def get_session_cache(**kwargs) -> CacheInterface:
    """Get session cache instance."""
    return cache_factory.create_cache(CacheType.SESSION, **kwargs)


def get_persistent_cache(**kwargs) -> CacheInterface:
    """Get persistent cache instance."""
    return cache_factory.create_cache(CacheType.PERSISTENT, **kwargs)
