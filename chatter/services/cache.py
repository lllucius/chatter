"""Redis caching service for performance optimization."""

import json
from typing import Any, Optional
from datetime import timedelta

import redis.asyncio as redis
from redis.asyncio import Redis

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Redis-based caching service."""
    
    def __init__(self):
        """Initialize cache service."""
        self.redis: Optional[Redis] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to Redis server."""
        try:
            self.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            self._connected = True
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self._connected = False
    
    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self.redis:
            await self.redis.close()
            self._connected = False
            logger.info("Disconnected from Redis cache")
    
    async def get(self, key: str) -> Any:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/cache unavailable
        """
        if not self._connected or not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[timedelta] = None
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected or not self.redis:
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
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected or not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cached values.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._connected or not self.redis:
            return False
        
        try:
            await self.redis.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if cache is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected


# Global cache service instance
cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """Get cache service instance (dependency injection).
    
    Returns:
        Cache service instance
    """
    return cache_service