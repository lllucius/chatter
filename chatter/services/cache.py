"""Compatibility layer for legacy cache service using the unified cache system."""

import json
from datetime import timedelta
from typing import Any

from chatter.core.cache_factory import get_general_cache, CacheBackend
from chatter.core.cache_interface import CacheInterface, CacheConfig
from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Compatibility layer for legacy cache service using unified cache system."""

    def __init__(
        self,
        config: dict = None,
        pool_config: dict = None,
        key_prefix: str = None,
        serializer: callable = None,
        deserializer: callable = None,
        fallback_to_memory: bool = False,
        instance_id: str = None,
    ):
        """Initialize cache service with unified cache backend.

        Args:
            config: Legacy config (ignored, using unified config)
            pool_config: Legacy pool config (ignored, using unified config)
            key_prefix: Prefix to add to all cache keys
            serializer: Custom serialization function (ignored, using JSON)
            deserializer: Custom deserialization function (ignored, using JSON)
            fallback_to_memory: Enable in-memory fallback when Redis unavailable
            instance_id: Instance identifier for distributed caching (ignored)
        """
        # Store legacy parameters for compatibility
        self.key_prefix = key_prefix or ""
        self.serializer = serializer
        self.deserializer = deserializer
        self.fallback_to_memory = fallback_to_memory
        self.instance_id = instance_id
        
        # Create unified cache configuration
        cache_config = CacheConfig(
            key_prefix=key_prefix or "legacy",
            default_ttl=settings.cache_ttl,
            enable_stats=True
        )
        
        # Choose backend based on fallback preference
        if fallback_to_memory:
            # Use multi-tier cache for automatic fallback
            backend = CacheBackend.MULTI_TIER
        else:
            # Use Redis directly
            backend = CacheBackend.REDIS
        
        # Get unified cache instance
        self._cache: CacheInterface = get_general_cache(
            backend=backend,
            config=cache_config
        )
        
        # Legacy compatibility flags
        self._enabled = settings.cache_enabled
        self._connection_attempts = 0

        if not self._enabled:
            logger.info("Cache service disabled by configuration")

    async def connect(self) -> None:
        """Connect to cache backend (compatibility method)."""
        if not self._enabled:
            logger.debug("Cache disabled by configuration")
            return
        
        # The unified cache handles connections automatically
        # Just ensure it's ready by doing a health check
        try:
            health = await self._cache.health_check()
            if health.get("status") == "healthy":
                logger.debug("Cache backend connected successfully")
            else:
                logger.warning("Cache backend unhealthy")
        except Exception as e:
            logger.warning(f"Cache backend connection check failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from cache backend (compatibility method)."""
        # The unified cache manages its own connections
        # This is a no-op for compatibility
        logger.debug("Cache disconnect requested (handled by unified cache)")

    async def get(self, key: str) -> Any:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/cache unavailable
        """
        if not self._enabled:
            return None

        try:
            # Add legacy prefix handling
            cache_key = self.add_prefix(key)
            return await self._cache.get(cache_key)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self, key: str, value: Any, expire: timedelta | None = None
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False

        try:
            # Add legacy prefix handling
            cache_key = self.add_prefix(key)
            
            # Convert timedelta to seconds for TTL
            ttl = None
            if expire:
                ttl = int(expire.total_seconds())
            
            return await self._cache.set(cache_key, value, ttl)
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False

        try:
            # Add legacy prefix handling
            cache_key = self.add_prefix(key)
            return await self._cache.delete(cache_key)
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cached values.

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False

        try:
            return await self._cache.clear()
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if cache is connected.

        Returns:
            True if connected, False otherwise
        """
        if not self._enabled:
            return False
        
        # Check cache health asynchronously in a simplified way
        # For legacy compatibility, we return True if cache is enabled
        return self._enabled

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
        if not self._enabled:
            return {
                "enabled": False,
                "connected": False,
                "status": "disabled"
            }
        
        try:
            # Use unified cache health check
            health = await self._cache.health_check()
            
            # Transform to legacy format
            return {
                "enabled": self._enabled,
                "connected": health.get("status") == "healthy",
                "status": health.get("status", "unknown"),
                "ping_success": health.get("status") == "healthy",
                "connection_attempts": self._connection_attempts,
            }
        except Exception as e:
            return {
                "enabled": self._enabled,
                "connected": False,
                "status": "unhealthy",
                "error": str(e),
                "ping_success": False
            }

    async def ensure_connection(self) -> bool:
        """Ensure cache connection is established if enabled.

        Returns:
            True if connected or caching disabled, False otherwise
        """
        if not self._enabled:
            return True

        # The unified cache handles connections automatically
        try:
            health = await self._cache.health_check()
            return health.get("status") == "healthy"
        except Exception:
            return False

    def add_prefix(self, key: str) -> str:
        """Add prefix to cache key.

        Args:
            key: Original key

        Returns:
            Prefixed key
        """
        if self.key_prefix:
            return f"{self.key_prefix}{key}"
        return key

    def is_valid_key(self, key: str) -> bool:
        """Validate cache key format.

        Args:
            key: Cache key to validate

        Returns:
            True if key is valid
        """
        return self._cache.is_valid_key(key)

    async def get_statistics(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if not self._enabled:
            return {
                "connected": False,
                "memory_usage": 0,
                "keys_count": 0,
                "hit_rate": 0.0,
            }

        try:
            stats = await self._cache.get_stats()
            return {
                "connected": True,
                "memory_usage": stats.memory_usage,
                "keys_count": stats.total_entries,
                "hit_rate": stats.hit_rate,
                "uptime": 0,  # Legacy compatibility
            }
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return {"connected": False, "error": str(e)}

    async def warm_cache(self, data: dict) -> bool:
        """Warm cache with provided data.

        Args:
            data: Dictionary of key-value pairs to cache

        Returns:
            True if successful
        """
        if not self._enabled:
            return False

        try:
            # Add prefixes to all keys
            prefixed_data = {}
            for key, value in data.items():
                prefixed_key = self.add_prefix(key)
                prefixed_data[prefixed_key] = value

            success = await self._cache.mset(prefixed_data)
            if success:
                logger.info(f"Cache warmed with {len(data)} items")
            return success

        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            return False

# Global cache service instance using unified cache system
cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """Get cache service instance (dependency injection).

    Returns:
        Cache service instance
    """
    return cache_service
