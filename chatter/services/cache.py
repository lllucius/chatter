"""Redis caching service for performance optimization with optional graceful fallback."""

import json
from datetime import timedelta
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Redis-based caching service with optional graceful fallback."""

    def __init__(self):
        """Initialize cache service."""
        self.redis: Redis | None = None
        self._connected = False
        self._enabled = settings.cache_enabled
        self._connection_attempts = 0
        
        if not self._enabled:
            logger.info("Cache service disabled by configuration")

    async def connect(self) -> None:
        """Connect to Redis server if caching is enabled."""
        if not self._enabled:
            logger.debug("Skipping Redis connection - caching disabled")
            return
            
        if self._connection_attempts >= settings.redis_connect_retries:
            logger.warning(f"Max Redis connection attempts ({settings.redis_connect_retries}) reached, disabling cache")
            self._enabled = False
            return
            
        try:
            self.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=settings.redis_connect_timeout,
                socket_timeout=settings.redis_connect_timeout,
                retry_on_timeout=True
            )
            # Test connection
            await self.redis.ping()
            self._connected = True
            self._connection_attempts = 0  # Reset on successful connection
            logger.info("Connected to Redis cache")
        except Exception as e:
            self._connection_attempts += 1
            logger.warning(
                f"Failed to connect to Redis (attempt {self._connection_attempts}/{settings.redis_connect_retries}): {e}"
            )
            self._connected = False
            
            # If max retries reached, disable caching
            if self._connection_attempts >= settings.redis_connect_retries:
                self._enabled = False
                logger.warning("Redis connection failed permanently, caching disabled")

    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self.redis:
            try:
                await self.redis.close()
                self._connected = False
                logger.info("Disconnected from Redis cache")
            except Exception as e:
                logger.warning(f"Error disconnecting from Redis: {e}")

    async def get(self, key: str) -> Any:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/cache unavailable
        """
        if not self._enabled or not self._connected or not self.redis:
            return None

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            # Try to reconnect on next operation
            if "Connection" in str(e) or "timeout" in str(e).lower():
                self._connected = False
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: timedelta | None = None
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled or not self._connected or not self.redis:
            return False

        try:
            serialized = json.dumps(value, default=str)
            if expire:
                await self.redis.setex(key, expire, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            # Try to reconnect on next operation
            if "Connection" in str(e) or "timeout" in str(e).lower():
                self._connected = False
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled or not self._connected or not self.redis:
            return False

        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            # Try to reconnect on next operation  
            if "Connection" in str(e) or "timeout" in str(e).lower():
                self._connected = False
            return False

    async def clear(self) -> bool:
        """Clear all cached values.

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled or not self._connected or not self.redis:
            return False

        try:
            await self.redis.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            # Try to reconnect on next operation
            if "Connection" in str(e) or "timeout" in str(e).lower():
                self._connected = False
            return False

    def is_connected(self) -> bool:
        """Check if cache is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._enabled and self._connected
        
    def is_enabled(self) -> bool:
        """Check if cache is enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        return self._enabled
        
    async def health_check(self) -> dict[str, Any]:
        """Perform health check on cache service.
        
        Returns:
            Health status information
        """
        status = {
            "enabled": self._enabled,
            "connected": self._connected,
            "connection_attempts": self._connection_attempts,
            "status": "healthy" if self.is_connected() else "unhealthy"
        }
        
        if self._enabled and self.redis:
            try:
                # Test with a simple ping
                await self.redis.ping()
                status["ping_success"] = True
                status["status"] = "healthy"
            except Exception as e:
                status["ping_success"] = False
                status["error"] = str(e)
                status["status"] = "unhealthy"
        else:
            status["ping_success"] = False
            
        return status
        
    async def ensure_connection(self) -> bool:
        """Ensure Redis connection is established if enabled.
        
        Returns:
            True if connected or caching disabled, False otherwise
        """
        if not self._enabled:
            return True
            
        if not self._connected:
            await self.connect()
            
        return self.is_connected()


# Global cache service instance
cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """Get cache service instance (dependency injection).

    Returns:
        Cache service instance
    """
    return cache_service
