"""Multi-tier cache implementation combining in-memory and Redis caching."""

from typing import Any

from chatter.core.cache_interface import (
    CacheConfig,
    CacheInterface,
    CacheStats,
)
from chatter.core.enhanced_memory_cache import EnhancedInMemoryCache
from chatter.core.enhanced_redis_cache import EnhancedRedisCache
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class MultiTierCache(CacheInterface):
    """Multi-tier cache combining in-memory (L1) and Redis (L2) caching.

    This provides the best of both worlds:
    - Fast access for frequently used data (in-memory)
    - Shared cache across instances (Redis)
    - Automatic fallback if Redis is unavailable
    """

    def __init__(
        self,
        config: CacheConfig | None = None,
        l1_config: CacheConfig | None = None,
        redis_url: str | None = None,
        l1_size_ratio: float = 0.1,
    ):
        """Initialize multi-tier cache.

        Args:
            config: Main cache configuration
            l1_config: L1 (memory) cache specific configuration
            redis_url: Redis connection URL
            l1_size_ratio: Ratio of L1 to L2 size (0.1 = L1 is 10% of L2)
        """
        super().__init__(config)

        # Create L1 (memory) cache configuration
        if l1_config is None:
            l1_config = CacheConfig(
                default_ttl=min(
                    300, self.config.default_ttl
                ),  # Shorter TTL for L1
                max_size=int(
                    (self.config.max_size or 1000) * l1_size_ratio
                ),
                eviction_policy="lru",
                key_prefix=(
                    f"{self.config.key_prefix}:l1"
                    if self.config.key_prefix
                    else "l1"
                ),
                enable_stats=self.config.enable_stats,
            )

        # Create L2 (Redis) cache configuration
        l2_config = CacheConfig(
            default_ttl=self.config.default_ttl,
            max_size=self.config.max_size,
            eviction_policy=self.config.eviction_policy,
            key_prefix=(
                f"{self.config.key_prefix}:l2"
                if self.config.key_prefix
                else "l2"
            ),
            enable_stats=self.config.enable_stats,
        )

        # Initialize cache layers
        self.l1_cache = EnhancedInMemoryCache(l1_config)
        self.l2_cache = EnhancedRedisCache(l2_config, redis_url)

        # Configuration
        self.l1_size_ratio = l1_size_ratio
        self._promote_threshold = (
            2  # Promote to L1 after this many L2 hits
        )
        self._promotion_counts: dict[str, int] = {}

        logger.info(
            "Multi-tier cache initialized",
            l1_max_size=l1_config.max_size,
            l2_enabled=True,
            l1_ttl=l1_config.default_ttl,
            l2_ttl=l2_config.default_ttl,
        )

    async def connect(self) -> bool:
        """Connect to Redis (L2 cache).

        Returns:
            True if L2 connected or L1-only mode enabled
        """
        l2_connected = await self.l2_cache.connect()
        if not l2_connected:
            logger.warning(
                "L2 (Redis) cache unavailable, operating in L1-only mode"
            )
        return True  # We can always operate with L1 only

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        await self.l2_cache.disconnect()

    async def get(self, key: str) -> Any:
        """Get value from cache, checking L1 first, then L2.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.is_valid_key(key):
            self._update_stats(error=True)
            return None

        # Try L1 first (fastest)
        value = await self.l1_cache.get(key)
        if value is not None:
            logger.debug("Multi-tier cache L1 hit", key=key)
            self._update_stats(hit=True)
            return value

        # Try L2 (Redis)
        value = await self.l2_cache.get(key)
        if value is not None:
            logger.debug("Multi-tier cache L2 hit", key=key)
            self._update_stats(hit=True)

            # Consider promoting to L1
            await self._consider_promotion(key, value)
            return value

        # Not found in either cache
        logger.debug("Multi-tier cache miss", key=key)
        self._update_stats(miss=True)
        return None

    async def set(
        self, key: str, value: Any, ttl: int | None = None
    ) -> bool:
        """Set value in both cache layers.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds

        Returns:
            True if at least one cache layer succeeded
        """
        if not self.is_valid_key(key):
            self._update_stats(error=True)
            return False

        # Set in both layers
        l1_success = await self.l1_cache.set(key, value, ttl)
        l2_success = await self.l2_cache.set(key, value, ttl)

        success = l1_success or l2_success

        if success:
            logger.debug(
                "Multi-tier cache set",
                key=key,
                l1_success=l1_success,
                l2_success=l2_success,
                ttl=ttl,
            )
        else:
            logger.warning(
                "Multi-tier cache set failed on both layers", key=key
            )
            self._update_stats(error=True)

        return success

    async def delete(self, key: str) -> bool:
        """Delete value from both cache layers.

        Args:
            key: Cache key

        Returns:
            True if successful in at least one layer
        """
        if not self.is_valid_key(key):
            return False

        # Delete from both layers
        l1_success = await self.l1_cache.delete(key)
        l2_success = await self.l2_cache.delete(key)

        # Remove from promotion tracking
        self._promotion_counts.pop(key, None)

        success = l1_success or l2_success

        if success:
            logger.debug(
                "Multi-tier cache delete",
                key=key,
                l1_success=l1_success,
                l2_success=l2_success,
            )

        return success

    async def clear(self) -> bool:
        """Clear both cache layers.

        Returns:
            True if successful in at least one layer
        """
        l1_success = await self.l1_cache.clear()
        l2_success = await self.l2_cache.clear()

        # Clear promotion tracking
        self._promotion_counts.clear()

        success = l1_success or l2_success

        if success:
            logger.info(
                "Multi-tier cache cleared",
                l1_success=l1_success,
                l2_success=l2_success,
            )

        return success

    async def exists(self, key: str) -> bool:
        """Check if key exists in either cache layer.

        Args:
            key: Cache key

        Returns:
            True if key exists in either layer
        """
        if not self.is_valid_key(key):
            return False

        # Check L1 first (faster)
        if await self.l1_cache.exists(key):
            return True

        # Check L2
        return await self.l2_cache.exists(key)

    async def keys(self, pattern: str | None = None) -> list[str]:
        """Get list of cache keys from both layers.

        Args:
            pattern: Key pattern to match

        Returns:
            List of unique matching keys from both layers
        """
        # Get keys from both layers
        l1_keys = await self.l1_cache.keys(pattern)
        l2_keys = await self.l2_cache.keys(pattern)

        # Combine and deduplicate
        all_keys = set(l1_keys + l2_keys)
        return list(all_keys)

    async def mget(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key-value pairs for found keys
        """
        result = {}
        remaining_keys = []

        # Try L1 first for all keys
        l1_results = await self.l1_cache.mget(keys)
        result.update(l1_results)

        # Find keys not found in L1
        remaining_keys = [key for key in keys if key not in l1_results]

        if remaining_keys:
            # Try L2 for remaining keys
            l2_results = await self.l2_cache.mget(remaining_keys)
            result.update(l2_results)

            # Consider promoting L2 hits to L1
            for key, value in l2_results.items():
                await self._consider_promotion(key, value)

        return result

    async def mset(
        self, items: dict[str, Any], ttl: int | None = None
    ) -> bool:
        """Set multiple values in both cache layers.

        Args:
            items: Dictionary of key-value pairs
            ttl: Time-to-live in seconds

        Returns:
            True if successful in at least one layer
        """
        # Set in both layers
        l1_success = await self.l1_cache.mset(items, ttl)
        l2_success = await self.l2_cache.mset(items, ttl)

        success = l1_success or l2_success

        if success:
            logger.debug(
                f"Multi-tier cache mset completed for {len(items)} items",
                l1_success=l1_success,
                l2_success=l2_success,
            )

        return success

    async def increment(self, key: str, delta: int = 1) -> int:
        """Increment a numeric value in both cache layers.

        Args:
            key: Cache key
            delta: Increment amount

        Returns:
            New value after increment
        """
        if not self.is_valid_key(key):
            raise ValueError("Invalid cache key")

        # Try L2 first (authoritative for atomic operations)
        try:
            new_value = await self.l2_cache.increment(key, delta)

            # Update L1 if present
            if await self.l1_cache.exists(key):
                await self.l1_cache.set(key, new_value)

            return new_value

        except Exception:
            # Fallback to L1 only
            return await self.l1_cache.increment(key, delta)

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key in both layers.

        Args:
            key: Cache key
            ttl: Time-to-live in seconds

        Returns:
            True if successful in at least one layer
        """
        if not self.is_valid_key(key):
            return False

        l1_success = await self.l1_cache.expire(key, ttl)
        l2_success = await self.l2_cache.expire(key, ttl)

        return l1_success or l2_success

    async def ttl(self, key: str) -> int | None:
        """Get time-to-live for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds or None if key doesn't exist
        """
        if not self.is_valid_key(key):
            return None

        # Check L1 first
        l1_ttl = await self.l1_cache.ttl(key)
        if l1_ttl is not None:
            return l1_ttl

        # Check L2
        return await self.l2_cache.ttl(key)

    async def get_stats(self) -> CacheStats:
        """Get combined cache statistics.

        Returns:
            Cache statistics object combining both layers
        """
        l1_stats = await self.l1_cache.get_stats()
        l2_stats = await self.l2_cache.get_stats()

        # Combine statistics
        combined_stats = CacheStats(
            total_entries=l1_stats.total_entries
            + l2_stats.total_entries,
            cache_hits=self._stats.cache_hits
            + l1_stats.cache_hits
            + l2_stats.cache_hits,
            cache_misses=self._stats.cache_misses
            + l1_stats.cache_misses
            + l2_stats.cache_misses,
            memory_usage=l1_stats.memory_usage + l2_stats.memory_usage,
            evictions=l1_stats.evictions + l2_stats.evictions,
            errors=self._stats.errors
            + l1_stats.errors
            + l2_stats.errors,
        )

        # Recalculate hit rate
        if combined_stats.total_requests > 0:
            combined_stats.hit_rate = (
                combined_stats.cache_hits
                / combined_stats.total_requests
            )

        return combined_stats

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on both cache layers.

        Returns:
            Health status information for both layers
        """
        l1_health = await self.l1_cache.health_check()
        l2_health = await self.l2_cache.health_check()

        # Overall status is healthy if at least L1 is healthy
        overall_status = (
            "healthy"
            if l1_health.get("status") == "healthy"
            else "degraded"
        )

        # If both are unhealthy, mark as unhealthy
        if (
            l1_health.get("status") != "healthy"
            and l2_health.get("status") != "healthy"
        ):
            overall_status = "unhealthy"

        return {
            "status": overall_status,
            "l1_cache": l1_health,
            "l2_cache": l2_health,
            "promotion_stats": {
                "tracked_keys": len(self._promotion_counts),
                "promotion_threshold": self._promote_threshold,
            },
        }

    # Private helper methods

    async def _consider_promotion(self, key: str, value: Any) -> None:
        """Consider promoting a key from L2 to L1 based on access patterns.

        Args:
            key: Cache key
            value: Cache value
        """
        # Increment access count for this key
        self._promotion_counts[key] = (
            self._promotion_counts.get(key, 0) + 1
        )

        # Promote if threshold reached
        if self._promotion_counts[key] >= self._promote_threshold:
            # Calculate L1 TTL (shorter than L2)
            l2_ttl = await self.l2_cache.ttl(key)
            l1_ttl = min(300, l2_ttl if l2_ttl and l2_ttl > 0 else 300)

            # Promote to L1
            success = await self.l1_cache.set(key, value, l1_ttl)

            if success:
                logger.debug(
                    "Promoted key to L1 cache",
                    key=key,
                    access_count=self._promotion_counts[key],
                    l1_ttl=l1_ttl,
                )

                # Reset promotion counter
                self._promotion_counts[key] = 0

    async def invalidate_l1(self, key: str) -> bool:
        """Invalidate key from L1 cache only.

        Useful when L2 is updated externally and L1 needs to be invalidated.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        return await self.l1_cache.delete(key)
