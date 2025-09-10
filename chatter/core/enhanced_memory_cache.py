"""Enhanced in-memory cache implementation with LRU eviction and unified interface."""

import asyncio
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any

from chatter.core.cache_interface import (
    CacheConfig,
    CacheInterface,
    CacheStats,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class EnhancedInMemoryCache(CacheInterface):
    """Enhanced in-memory cache with LRU eviction and unified interface."""

    def __init__(self, config: CacheConfig | None = None):
        """Initialize enhanced in-memory cache.

        Args:
            config: Cache configuration
        """
        super().__init__(config)

        # Main cache storage with LRU ordering
        self._cache: OrderedDict[str, Any] = OrderedDict()

        # TTL tracking
        self._expiry_times: dict[str, datetime] = {}

        # Statistics tracking
        self._evictions = 0
        self._lock = asyncio.Lock()

        # Default max size if not specified
        if self.config.max_size is None:
            self.config.max_size = 1000

        logger.debug(
            "Enhanced in-memory cache initialized",
            max_size=self.config.max_size,
            eviction_policy=self.config.eviction_policy,
            default_ttl=self.config.default_ttl,
        )

    async def get(self, key: str) -> Any:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if self.is_disabled:
            return None
            
        if not self.is_valid_key(key):
            self._update_stats(error=True)
            return None

        async with self._lock:
            # Check if key exists and is not expired
            if key not in self._cache:
                self._update_stats(miss=True)
                return None

            # Check expiration
            if self._is_expired(key):
                await self._remove_key(key)
                self._update_stats(miss=True)
                return None

            # Move to end for LRU (most recently used)
            value = self._cache[key]
            self._cache.move_to_end(key)

            self._update_stats(hit=True)

            logger.debug("Cache hit", key=key)
            return value

    async def set(
        self, key: str, value: Any, ttl: int | timedelta | None = None
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (int) or as timedelta object

        Returns:
            True if successful, False otherwise
        """
        if self.is_disabled:
            return False
            
        if not self.is_valid_key(key):
            self._update_stats(error=True)
            return False

        try:
            async with self._lock:
                # Use default TTL if not specified
                ttl = ttl or self.config.default_ttl

                # Convert timedelta to seconds if needed
                if isinstance(ttl, timedelta):
                    ttl_seconds = int(ttl.total_seconds())
                else:
                    ttl_seconds = ttl

                # Calculate expiry time
                expiry_time = datetime.now() + timedelta(
                    seconds=ttl_seconds
                )

                # Check if we need to evict items
                if (
                    key not in self._cache
                    and len(self._cache) >= self.config.max_size
                ):
                    await self._evict()

                # Store value and expiry
                self._cache[key] = value
                self._expiry_times[key] = expiry_time

                # Move to end for LRU
                self._cache.move_to_end(key)

                logger.debug(
                    "Cache set",
                    key=key,
                    ttl=ttl_seconds,
                    cache_size=len(self._cache),
                )

                return True

        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            self._update_stats(error=True)
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if self.is_disabled:
            return False
            
        if not self.is_valid_key(key):
            return False

        try:
            async with self._lock:
                success = await self._remove_key(key)
                if success:
                    logger.debug("Cache delete", key=key)
                return success
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            self._update_stats(error=True)
            return False

    async def clear(self) -> bool:
        """Clear all cached values.

        Returns:
            True if successful, False otherwise
        """
        if self.is_disabled:
            return True  # Consider successful if cache is disabled
            
        try:
            async with self._lock:
                cache_size = len(self._cache)
                self._cache.clear()
                self._expiry_times.clear()

                logger.info("Cache cleared", previous_size=cache_size)
                return True

        except Exception as e:
            logger.error("Cache clear error", error=str(e))
            self._update_stats(error=True)
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.is_valid_key(key):
            return False

        async with self._lock:
            if key not in self._cache:
                return False

            # Check if expired
            if self._is_expired(key):
                await self._remove_key(key)
                return False

            return True

    async def keys(self, pattern: str | None = None) -> list[str]:
        """Get list of cache keys.

        Args:
            pattern: Key pattern to match (simple string matching)

        Returns:
            List of matching keys
        """
        async with self._lock:
            # Clean up expired keys first
            await self._cleanup_expired()

            all_keys = list(self._cache.keys())

            if pattern is None:
                return all_keys

            # Simple pattern matching (contains)
            matching_keys = [key for key in all_keys if pattern in key]
            return matching_keys

    async def mget(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key-value pairs for found keys
        """
        result = {}

        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value

        return result

    async def mset(
        self, items: dict[str, Any], ttl: int | None = None
    ) -> bool:
        """Set multiple values in cache.

        Args:
            items: Dictionary of key-value pairs
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            success_count = 0

            for key, value in items.items():
                if await self.set(key, value, ttl):
                    success_count += 1

            # Consider successful if at least 50% of items were set
            return success_count >= len(items) * 0.5

        except Exception as e:
            logger.error("Cache mset error", error=str(e))
            self._update_stats(error=True)
            return False

    async def increment(self, key: str, delta: int = 1) -> int:
        """Increment a numeric value in cache.

        Args:
            key: Cache key
            delta: Increment amount

        Returns:
            New value after increment
        """
        if not self.is_valid_key(key):
            raise ValueError("Invalid cache key")

        async with self._lock:
            # Get current value without using the async get method to avoid deadlock
            current_value = None
            if key in self._cache and not self._is_expired(key):
                current_value = self._cache[key]
                # Move to end for LRU
                self._cache.move_to_end(key)

            if current_value is None:
                new_value = delta
            else:
                try:
                    new_value = int(current_value) + delta
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        f"Cannot increment non-numeric value: {current_value}"
                    ) from e

            # Set value directly without using async set method to avoid deadlock
            ttl = self.config.default_ttl
            expiry_time = datetime.now() + timedelta(seconds=ttl)

            # Check if we need to evict items
            if (
                key not in self._cache
                and len(self._cache) >= self.config.max_size
            ):
                await self._evict()

            # Store value and expiry
            self._cache[key] = new_value
            self._expiry_times[key] = expiry_time

            # Move to end for LRU
            self._cache.move_to_end(key)

            return new_value

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key.

        Args:
            key: Cache key
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.is_valid_key(key):
            return False

        async with self._lock:
            if key not in self._cache:
                return False

            # Update expiry time
            self._expiry_times[key] = datetime.now() + timedelta(
                seconds=ttl
            )
            return True

    async def ttl(self, key: str) -> int | None:
        """Get time-to-live for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds or None if key doesn't exist
        """
        if not self.is_valid_key(key):
            return None

        async with self._lock:
            if key not in self._cache or key not in self._expiry_times:
                return None

            expiry_time = self._expiry_times[key]
            now = datetime.now()

            if now >= expiry_time:
                await self._remove_key(key)
                return None

            return int((expiry_time - now).total_seconds())

    async def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            Cache statistics object
        """
        async with self._lock:
            # Update current state
            await self._cleanup_expired()

            # Calculate memory usage (rough estimate)
            memory_usage = sum(
                len(str(key)) + len(str(value))
                for key, value in self._cache.items()
            )

            stats = CacheStats(
                total_entries=len(self._cache),
                cache_hits=self._stats.cache_hits,
                cache_misses=self._stats.cache_misses,
                hit_rate=self._stats.hit_rate,
                memory_usage=memory_usage,
                evictions=self._evictions,
                errors=self._stats.errors,
            )

            return stats

    async def health_check(self) -> dict[str, Any]:
        """Perform health check.

        Returns:
            Health status information
        """
        try:
            # Test basic operations
            test_key = f"__health_check_{int(time.time())}"
            test_value = "test"

            # Test set
            set_success = await self.set(test_key, test_value, 1)

            # Test get
            get_value = await self.get(test_key)
            get_success = get_value == test_value

            # Test delete
            delete_success = await self.delete(test_key)

            stats = await self.get_stats()

            return {
                "status": (
                    "healthy"
                    if all([set_success, get_success, delete_success])
                    else "unhealthy"
                ),
                "operations": {
                    "set": set_success,
                    "get": get_success,
                    "delete": delete_success,
                },
                "cache_size": stats.total_entries,
                "memory_usage": stats.memory_usage,
                "hit_rate": stats.hit_rate,
                "max_size": self.config.max_size,
                "evictions": self._evictions,
            }

        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}

    # Private helper methods

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired.

        Args:
            key: Cache key

        Returns:
            True if expired, False otherwise
        """
        if key not in self._expiry_times:
            return True

        return datetime.now() > self._expiry_times[key]

    async def _remove_key(self, key: str) -> bool:
        """Remove key from cache and expiry tracking.

        Args:
            key: Cache key

        Returns:
            True if key was removed, False if not found
        """
        removed = False

        if key in self._cache:
            del self._cache[key]
            removed = True

        if key in self._expiry_times:
            del self._expiry_times[key]

        return removed

    async def _evict(self) -> None:
        """Evict items according to eviction policy."""
        if self.config.eviction_policy == "lru":
            await self._evict_lru()
        elif self.config.eviction_policy == "ttl":
            await self._evict_ttl()
        else:
            await self._evict_random()

    async def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if self._cache:
            # OrderedDict maintains insertion/access order
            # Oldest item is at the beginning
            key = next(iter(self._cache))
            await self._remove_key(key)
            self._evictions += 1

            logger.debug("LRU eviction", key=key)

    async def _evict_ttl(self) -> None:
        """Evict item with earliest expiry time."""
        if not self._expiry_times:
            await self._evict_lru()
            return

        # Find key with earliest expiry
        earliest_key = min(
            self._expiry_times.keys(),
            key=lambda k: self._expiry_times[k],
        )

        await self._remove_key(earliest_key)
        self._evictions += 1

        logger.debug("TTL eviction", key=earliest_key)

    async def _evict_random(self) -> None:
        """Evict a random item."""
        if self._cache:
            import random

            key = random.choice(list(self._cache.keys()))
            await self._remove_key(key)
            self._evictions += 1

            logger.debug("Random eviction", key=key)

    async def _cleanup_expired(self) -> int:
        """Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = [
            key
            for key, expiry in self._expiry_times.items()
            if now > expiry
        ]

        for key in expired_keys:
            await self._remove_key(key)

        if expired_keys:
            logger.debug(
                "Expired entries cleaned", count=len(expired_keys)
            )

        return len(expired_keys)
