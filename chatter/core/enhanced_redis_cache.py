"""Enhanced Redis cache implementation with unified interface."""

import asyncio
import json
from datetime import timedelta
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from chatter.config import settings
from chatter.core.cache_interface import (
    CacheConfig,
    CacheInterface,
    CacheStats,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class EnhancedRedisCache(CacheInterface):
    """Enhanced Redis cache with unified interface and robust error handling."""

    def __init__(
        self,
        config: CacheConfig | None = None,
        redis_url: str | None = None,
        pool_config: dict | None = None,
    ):
        """Initialize enhanced Redis cache.

        Args:
            config: Cache configuration
            redis_url: Redis connection URL
            pool_config: Redis connection pool configuration
        """
        super().__init__(config)

        self.redis_url = redis_url or settings.redis_url
        self.pool_config = pool_config or {}
        self.redis: Redis | None = None
        self._connected = False
        self._connection_attempts = 0
        self._enabled = settings.cache_enabled

        # Connection configuration
        self._connect_timeout = settings.redis_connect_timeout
        self._max_retries = settings.redis_connect_retries

        logger.debug(
            "Enhanced Redis cache initialized",
            redis_url=self.redis_url[:20]
            + "...",  # Don't log full URL for security
            enabled=self._enabled,
            default_ttl=self.config.default_ttl,
        )

    async def connect(self) -> bool:
        """Connect to Redis server.

        Returns:
            True if connected successfully, False otherwise
        """
        if not self._enabled:
            logger.debug("Redis cache disabled by configuration")
            return False

        if self._connection_attempts >= self._max_retries:
            logger.warning(
                f"Max Redis connection attempts ({self._max_retries}) reached"
            )
            self._enabled = False
            return False

        try:
            self.redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=self._connect_timeout,
                socket_timeout=self._connect_timeout,
                retry_on_timeout=True,
                **self.pool_config,
            )

            # Test connection
            await self.redis.ping()
            self._connected = True
            self._connection_attempts = 0

            logger.info("Connected to Redis cache")
            return True

        except Exception as e:
            self._connection_attempts += 1
            logger.warning(
                f"Failed to connect to Redis (attempt {self._connection_attempts}/{self._max_retries}): {e}"
            )
            self._connected = False

            if self._connection_attempts >= self._max_retries:
                self._enabled = False
                logger.warning(
                    "Redis connection failed permanently, caching disabled"
                )

            return False

    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self.redis:
            try:
                await self.redis.close()
                self._connected = False
                logger.info("Disconnected from Redis cache")
            except Exception as e:
                logger.warning(f"Error disconnecting from Redis: {e}")

    async def _ensure_connection(self) -> bool:
        """Ensure Redis connection is established.

        Returns:
            True if connected, False otherwise
        """
        if not self._enabled:
            return False

        if not self._connected:
            return await self.connect()

        return True

    async def get(self, key: str) -> Any:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if self.is_disabled:
            return None

        if (
            not self.is_valid_key(key)
            or not await self._ensure_connection()
        ):
            self._update_stats(error=True)
            return None

        try:
            prefixed_key = self._add_prefix(key)
            value = await self.redis.get(prefixed_key)

            if value is None:
                self._update_stats(miss=True)
                return None

            # Deserialize JSON
            deserialized_value = json.loads(value)
            self._update_stats(hit=True)

            logger.debug("Redis cache hit", key=key)
            return deserialized_value

        except Exception as e:
            logger.warning(f"Redis get error for key {key}: {e}")
            self._handle_connection_error(e)
            self._update_stats(error=True)
            return None

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

        if (
            not self.is_valid_key(key)
            or not await self._ensure_connection()
        ):
            self._update_stats(error=True)
            return False

        try:
            prefixed_key = self._add_prefix(key)
            serialized_value = json.dumps(value, default=str)

            # Use default TTL if not specified
            ttl = ttl or self.config.default_ttl

            # Convert timedelta to seconds if needed
            if isinstance(ttl, timedelta):
                ttl_seconds = int(ttl.total_seconds())
            else:
                ttl_seconds = ttl

            if ttl_seconds > 0:
                await self.redis.setex(
                    prefixed_key, ttl_seconds, serialized_value
                )
            else:
                await self.redis.set(prefixed_key, serialized_value)

            logger.debug("Redis cache set", key=key, ttl=ttl_seconds)
            return True

        except Exception as e:
            logger.warning(f"Redis set error for key {key}: {e}")
            self._handle_connection_error(e)
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

        if (
            not self.is_valid_key(key)
            or not await self._ensure_connection()
        ):
            return False

        try:
            prefixed_key = self._add_prefix(key)
            result = await self.redis.delete(prefixed_key)

            success = result > 0
            if success:
                logger.debug("Redis cache delete", key=key)

            return success

        except Exception as e:
            logger.warning(f"Redis delete error for key {key}: {e}")
            self._handle_connection_error(e)
            self._update_stats(error=True)
            return False

    async def clear(self) -> bool:
        """Clear all cached values.

        Returns:
            True if successful, False otherwise
        """
        if self.is_disabled:
            return True  # Consider successful if cache is disabled

        if not await self._ensure_connection():
            return False

        try:
            if self.config.key_prefix:
                # Only clear keys with our prefix
                pattern = f"{self.config.key_prefix}:*"
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
                    logger.info(
                        f"Redis cache cleared {len(keys)} keys with prefix"
                    )
            else:
                # Clear entire database (use with caution)
                await self.redis.flushdb()
                logger.info("Redis cache cleared (entire database)")

            return True

        except Exception as e:
            logger.warning(f"Redis clear error: {e}")
            self._handle_connection_error(e)
            self._update_stats(error=True)
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if (
            not self.is_valid_key(key)
            or not await self._ensure_connection()
        ):
            return False

        try:
            prefixed_key = self._add_prefix(key)
            result = await self.redis.exists(prefixed_key)
            return result > 0

        except Exception as e:
            logger.warning(f"Redis exists error for key {key}: {e}")
            self._handle_connection_error(e)
            return False

    async def keys(self, pattern: str | None = None) -> list[str]:
        """Get list of cache keys.

        Args:
            pattern: Key pattern to match (Redis pattern syntax)

        Returns:
            List of matching keys
        """
        if not await self._ensure_connection():
            return []

        try:
            # Build search pattern
            if pattern:
                search_pattern = (
                    f"{self.config.key_prefix}:*{pattern}*"
                    if self.config.key_prefix
                    else f"*{pattern}*"
                )
            else:
                search_pattern = (
                    f"{self.config.key_prefix}:*"
                    if self.config.key_prefix
                    else "*"
                )

            keys = await self.redis.keys(search_pattern)

            # Remove prefix from returned keys
            if self.config.key_prefix:
                prefix_len = (
                    len(self.config.key_prefix) + 1
                )  # +1 for colon
                keys = [
                    key[prefix_len:]
                    for key in keys
                    if key.startswith(f"{self.config.key_prefix}:")
                ]

            return keys

        except Exception as e:
            logger.warning(f"Redis keys error: {e}")
            self._handle_connection_error(e)
            return []

    async def mget(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key-value pairs for found keys
        """
        if not keys or not await self._ensure_connection():
            return {}

        try:
            # Add prefixes to keys
            prefixed_keys = [
                self._add_prefix(key)
                for key in keys
                if self.is_valid_key(key)
            ]

            if not prefixed_keys:
                return {}

            # Get values
            values = await self.redis.mget(prefixed_keys)

            # Build result dict
            result = {}
            for i, value in enumerate(values):
                if value is not None:
                    original_key = keys[i]
                    try:
                        result[original_key] = json.loads(value)
                        self._update_stats(hit=True)
                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"JSON decode error for key {original_key}: {e}"
                        )
                        self._update_stats(error=True)
                else:
                    self._update_stats(miss=True)

            return result

        except Exception as e:
            logger.warning(f"Redis mget error: {e}")
            self._handle_connection_error(e)
            self._update_stats(error=True)
            return {}

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
        if not items or not await self._ensure_connection():
            return False

        try:
            # Use pipeline for efficiency
            async with self.redis.pipeline() as pipe:
                for key, value in items.items():
                    if self.is_valid_key(key):
                        prefixed_key = self._add_prefix(key)
                        serialized_value = json.dumps(
                            value, default=str
                        )

                        if ttl and ttl > 0:
                            pipe.setex(
                                prefixed_key, ttl, serialized_value
                            )
                        else:
                            pipe.set(prefixed_key, serialized_value)

                await pipe.execute()

            logger.debug(f"Redis mset completed for {len(items)} items")
            return True

        except Exception as e:
            logger.warning(f"Redis mset error: {e}")
            self._handle_connection_error(e)
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
        if (
            not self.is_valid_key(key)
            or not await self._ensure_connection()
        ):
            raise ValueError("Invalid key or connection failed")

        try:
            prefixed_key = self._add_prefix(key)
            result = await self.redis.incrby(prefixed_key, delta)

            logger.debug(
                "Redis increment",
                key=key,
                delta=delta,
                new_value=result,
            )
            return result

        except Exception as e:
            logger.warning(f"Redis increment error for key {key}: {e}")
            self._handle_connection_error(e)
            self._update_stats(error=True)
            raise

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key.

        Args:
            key: Cache key
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        if (
            not self.is_valid_key(key)
            or not await self._ensure_connection()
        ):
            return False

        try:
            prefixed_key = self._add_prefix(key)
            result = await self.redis.expire(prefixed_key, ttl)
            return result > 0

        except Exception as e:
            logger.warning(f"Redis expire error for key {key}: {e}")
            self._handle_connection_error(e)
            return False

    async def ttl(self, key: str) -> int | None:
        """Get time-to-live for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds or None if key doesn't exist
        """
        if (
            not self.is_valid_key(key)
            or not await self._ensure_connection()
        ):
            return None

        try:
            prefixed_key = self._add_prefix(key)
            result = await self.redis.ttl(prefixed_key)

            # Redis returns -1 if key exists but has no expiry, -2 if key doesn't exist
            if result == -2:
                return None
            elif result == -1:
                return -1  # No expiry set
            else:
                return result

        except Exception as e:
            logger.warning(f"Redis ttl error for key {key}: {e}")
            self._handle_connection_error(e)
            return None

    async def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            Cache statistics object
        """
        if not await self._ensure_connection():
            return CacheStats(
                errors=self._stats.errors,
                cache_hits=self._stats.cache_hits,
                cache_misses=self._stats.cache_misses,
                hit_rate=self._stats.hit_rate,
            )

        try:
            info = await self.redis.info()
            dbsize = await self.redis.dbsize()

            # Get Redis-specific stats
            memory_usage = info.get("used_memory", 0)
            keyspace_hits = info.get("keyspace_hits", 0)
            keyspace_misses = info.get("keyspace_misses", 0)

            # Calculate hit rate from Redis stats if available
            total_requests = keyspace_hits + keyspace_misses
            redis_hit_rate = (
                keyspace_hits / total_requests
                if total_requests > 0
                else 0
            )

            return CacheStats(
                total_entries=dbsize,
                cache_hits=self._stats.cache_hits + keyspace_hits,
                cache_misses=self._stats.cache_misses + keyspace_misses,
                hit_rate=redis_hit_rate,
                memory_usage=memory_usage,
                errors=self._stats.errors,
            )

        except Exception as e:
            logger.warning(f"Redis stats error: {e}")
            return CacheStats(
                errors=self._stats.errors + 1,
                cache_hits=self._stats.cache_hits,
                cache_misses=self._stats.cache_misses,
                hit_rate=self._stats.hit_rate,
            )

    async def health_check(self) -> dict[str, Any]:
        """Perform health check.

        Returns:
            Health status information
        """
        try:
            if not await self._ensure_connection():
                return {
                    "status": "unhealthy",
                    "connected": False,
                    "enabled": self._enabled,
                    "error": "Connection failed",
                }

            # Test ping
            ping_result = await self.redis.ping()

            # Test basic operations
            test_key = (
                f"__health_check_{int(asyncio.get_event_loop().time())}"
            )
            test_value = "test"

            set_success = await self.set(test_key, test_value, 1)
            get_value = await self.get(test_key)
            get_success = get_value == test_value
            delete_success = await self.delete(test_key)

            stats = await self.get_stats()

            return {
                "status": (
                    "healthy"
                    if all(
                        [
                            ping_result,
                            set_success,
                            get_success,
                            delete_success,
                        ]
                    )
                    else "unhealthy"
                ),
                "connected": self._connected,
                "enabled": self._enabled,
                "ping": ping_result,
                "operations": {
                    "set": set_success,
                    "get": get_success,
                    "delete": delete_success,
                },
                "total_entries": stats.total_entries,
                "memory_usage": stats.memory_usage,
                "hit_rate": stats.hit_rate,
                "connection_attempts": self._connection_attempts,
            }

        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "connected": self._connected,
                "enabled": self._enabled,
                "error": str(e),
            }

    # Private helper methods

    def _add_prefix(self, key: str) -> str:
        """Add prefix to cache key.

        Args:
            key: Original key

        Returns:
            Prefixed key
        """
        if self.config.key_prefix:
            return f"{self.config.key_prefix}:{key}"
        return key

    def _handle_connection_error(self, error: Exception) -> None:
        """Handle connection errors by marking connection as failed.

        Args:
            error: Exception that occurred
        """
        error_str = str(error).lower()
        if any(
            keyword in error_str
            for keyword in ["connection", "timeout", "redis"]
        ):
            self._connected = False
            logger.debug(
                "Redis connection marked as failed due to error"
            )
