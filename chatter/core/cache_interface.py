"""Unified cache interface for consistent caching across the application."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheStats:
    """Cache statistics data class."""

    total_entries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    hit_rate: float = 0.0
    memory_usage: int = 0
    evictions: int = 0
    errors: int = 0

    @property
    def total_requests(self) -> int:
        """Total cache requests."""
        return self.cache_hits + self.cache_misses


@dataclass
class CacheConfig:
    """Cache configuration data class."""

    default_ttl: int = 3600  # 1 hour
    max_size: int | None = None
    eviction_policy: str = "lru"  # lru, ttl, random
    key_prefix: str = ""
    enable_stats: bool = True
    enable_compression: bool = False
    disabled: bool = False  # Completely disable cache operations


class CacheInterface(ABC):
    """Abstract base class for all cache implementations."""

    def __init__(self, config: CacheConfig | None = None):
        """Initialize cache with configuration.

        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()
        self._stats = CacheStats()

    @property
    def is_disabled(self) -> bool:
        """Check if cache is completely disabled.
        
        Returns:
            True if cache operations should be skipped
        """
        return self.config.disabled

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        pass

    @abstractmethod
    async def set(
        self, key: str, value: Any, ttl: int | None = None
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cached values.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        pass

    @abstractmethod
    async def keys(self, pattern: str | None = None) -> list[str]:
        """Get list of cache keys.

        Args:
            pattern: Key pattern to match

        Returns:
            List of matching keys
        """
        pass

    @abstractmethod
    async def mget(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key-value pairs for found keys
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def increment(self, key: str, delta: int = 1) -> int:
        """Increment a numeric value in cache.

        Args:
            key: Cache key
            delta: Increment amount

        Returns:
            New value after increment
        """
        pass

    @abstractmethod
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key.

        Args:
            key: Cache key
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def ttl(self, key: str) -> int | None:
        """Get time-to-live for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds or None if key doesn't exist
        """
        pass

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            Cache statistics object
        """
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Perform health check.

        Returns:
            Health status information
        """
        pass

    # Helper methods that can be overridden

    def make_key(self, *parts: str, **kwargs: Any) -> str:
        """Create a consistent cache key.

        Args:
            *parts: Key parts to join
            **kwargs: Additional key parts as keyword arguments

        Returns:
            Formatted cache key
        """
        # Combine parts and kwargs into a consistent key
        key_parts = list(parts)

        # Add kwargs in sorted order for consistency
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")

        # Join with colon separator
        key = ":".join(str(part) for part in key_parts if part)

        # Add prefix if configured
        if self.config.key_prefix:
            key = f"{self.config.key_prefix}:{key}"

        return key

    def is_valid_key(self, key: str) -> bool:
        """Validate cache key format.

        Args:
            key: Cache key to validate

        Returns:
            True if key is valid
        """
        if not key or not isinstance(key, str):
            return False

        # Basic validation - no whitespace, reasonable length
        if len(key) > 250 or " " in key or "\n" in key or "\t" in key:
            return False

        return True

    async def get_or_set(
        self, key: str, callable_func: Callable[[], Any], ttl: int | None = None
    ) -> Any:
        """Get value from cache or set it using the callable.

        Args:
            key: Cache key
            callable_func: Function to call if key not in cache
            ttl: Time-to-live in seconds

        Returns:
            Cached or computed value
        """
        # Try to get from cache first
        value = await self.get(key)
        if value is not None:
            return value

        # Compute value and cache it
        if callable(callable_func):
            value = (
                await callable_func()
                if callable(callable_func)
                else callable_func
            )
        else:
            value = callable_func

        if value is not None:
            await self.set(key, value, ttl)

        return value

    async def warm_cache(
        self, data: dict[str, Any], ttl: int | None = None
    ) -> bool:
        """Warm cache with provided data.

        Args:
            data: Dictionary of key-value pairs to cache
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        return await self.mset(data, ttl)

    def _update_stats(
        self, hit: bool = False, miss: bool = False, error: bool = False
    ) -> None:
        """Update cache statistics.

        Args:
            hit: Whether this was a cache hit
            miss: Whether this was a cache miss
            error: Whether this was an error
        """
        if not self.config.enable_stats:
            return

        if hit:
            self._stats.cache_hits += 1
        elif miss:
            self._stats.cache_misses += 1
        elif error:
            self._stats.errors += 1

        # Update hit rate
        total = self._stats.total_requests
        if total > 0:
            self._stats.hit_rate = self._stats.cache_hits / total
