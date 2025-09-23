"""Unified cache implementation with memory, Redis, and multi-tier support."""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


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
        """Initialize cache with configuration."""
        self.config = config or CacheConfig()
        self._stats = CacheStats()

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(
        self, key: str, value: Any, ttl: int | None = None
    ) -> bool:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check cache health status."""
        pass

    def _build_key(self, key: str) -> str:
        """Build cache key with prefix."""
        if self.config.key_prefix:
            return f"{self.config.key_prefix}:{key}"
        return key

    def make_key(self, *args, **kwargs) -> str:
        """Build cache key from components.
        
        Args:
            *args: Key components to join with ':'
            **kwargs: Additional key-value pairs to include
            
        Returns:
            Formatted cache key with prefix
        """
        # Start with args joined by ':'
        parts = [str(arg) for arg in args]
        
        # Add kwargs as key=value pairs
        if kwargs:
            for key, value in sorted(kwargs.items()):
                parts.append(f"{key}={value}")
        
        # Join all parts and build with prefix
        key = ":".join(parts)
        return self._build_key(key)
    
    def is_valid_key(self, key: str) -> bool:
        """Validate cache key format.
        
        Args:
            key: Key to validate
            
        Returns:
            True if key is valid, False otherwise
        """
        if not key:
            return False
        if " " in key:
            return False
        if len(key) > 250:  # Redis key limit is 512MB, but let's be reasonable
            return False
        return True


class MemoryCache(CacheInterface):
    """In-memory cache implementation with LRU eviction."""

    def __init__(self, config: CacheConfig | None = None):
        """Initialize in-memory cache."""
        super().__init__(config)
        
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._expiry_times: dict[str, datetime] = {}
        self._evictions = 0
        self._lock = asyncio.Lock()
        
        if self.config.max_size is None:
            self.config.max_size = 1000

        logger.debug(
            "Memory cache initialized",
            max_size=self.config.max_size,
            default_ttl=self.config.default_ttl,
        )

    async def get(self, key: str) -> Any:
        """Get value from memory cache."""
        if self.config.disabled:
            return None

        async with self._lock:
            cache_key = self._build_key(key)
            
            # Check if key exists and not expired
            if cache_key not in self._cache:
                self._stats.cache_misses += 1
                return None

            # Check expiration
            if cache_key in self._expiry_times:
                if datetime.now() > self._expiry_times[cache_key]:
                    del self._cache[cache_key]
                    del self._expiry_times[cache_key]
                    self._stats.cache_misses += 1
                    return None

            # Move to end (LRU)
            value = self._cache.pop(cache_key)
            self._cache[cache_key] = value
            self._stats.cache_hits += 1
            
            return value

    async def set(
        self, key: str, value: Any, ttl: int | None = None
    ) -> bool:
        """Set value in memory cache."""
        if self.config.disabled:
            return False

        async with self._lock:
            cache_key = self._build_key(key)
            ttl = ttl or self.config.default_ttl
            
            # Set expiry if TTL specified
            if ttl > 0:
                self._expiry_times[cache_key] = datetime.now() + timedelta(seconds=ttl)
            
            # Remove oldest entries if at capacity
            while len(self._cache) >= self.config.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                if oldest_key in self._expiry_times:
                    del self._expiry_times[oldest_key]
                self._evictions += 1

            self._cache[cache_key] = value
            return True

    async def delete(self, key: str) -> bool:
        """Delete key from memory cache."""
        if self.config.disabled:
            return False

        async with self._lock:
            cache_key = self._build_key(key)
            if cache_key in self._cache:
                del self._cache[cache_key]
                if cache_key in self._expiry_times:
                    del self._expiry_times[cache_key]
                return True
            return False

    async def clear(self) -> bool:
        """Clear all memory cache entries."""
        if self.config.disabled:
            return False

        async with self._lock:
            self._cache.clear()
            self._expiry_times.clear()
            return True

    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        if self.config.disabled:
            return False

        cache_key = self._build_key(key)
        return cache_key in self._cache

    async def get_stats(self) -> dict[str, Any]:
        """Get memory cache statistics."""
        return {
            "total_entries": len(self._cache),
            "cache_hits": self._stats.cache_hits,
            "cache_misses": self._stats.cache_misses,
            "hit_rate": (
                self._stats.cache_hits / max(1, self._stats.total_requests)
            ),
            "memory_usage": len(self._cache),
            "evictions": self._evictions,
            "errors": self._stats.errors,
        }

    async def health_check(self) -> dict[str, Any]:
        """Check memory cache health status."""
        if self.config.disabled:
            return {"status": "disabled", "message": "Cache is disabled"}
        
        try:
            # Memory cache is healthy if we can access basic properties
            total_entries = len(self._cache)
            return {
                "status": "healthy",
                "backend": "memory",
                "total_entries": total_entries,
                "max_size": self.config.max_size,
                "evictions": self._evictions,
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "backend": "memory",
                "error": str(e)
            }


class RedisCache(CacheInterface):
    """Redis cache implementation with connection pooling."""

    def __init__(
        self,
        config: CacheConfig | None = None,
        redis_url: str | None = None,
    ):
        """Initialize Redis cache."""
        super().__init__(config)
        
        self.redis_url = redis_url or settings.redis_url
        self.redis: Redis | None = None
        self._connected = False
        self._connection_attempts = 0
        self._enabled = not settings.cache_disabled

        logger.debug(
            "Redis cache initialized",
            redis_url=self.redis_url,
            default_ttl=self.config.default_ttl,
        )

    async def _ensure_connection(self) -> bool:
        """Ensure Redis connection is established."""
        if not self._enabled or self.config.disabled:
            return False

        if self._connected and self.redis:
            return True

        try:
            self.redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            
            # Test connection
            await self.redis.ping()
            self._connected = True
            self._connection_attempts = 0
            
            logger.info("Redis cache connection established")
            return True
            
        except Exception as e:
            self._connection_attempts += 1
            logger.warning(
                "Redis connection failed",
                error=str(e),
                attempts=self._connection_attempts,
            )
            self._connected = False
            return False

    async def get(self, key: str) -> Any:
        """Get value from Redis cache."""
        if not await self._ensure_connection():
            self._stats.cache_misses += 1
            return None

        try:
            cache_key = self._build_key(key)
            value = await self.redis.get(cache_key)
            
            if value is None:
                self._stats.cache_misses += 1
                return None
                
            self._stats.cache_hits += 1
            return json.loads(value)
            
        except Exception as e:
            logger.warning("Redis get failed", key=key, error=str(e))
            self._stats.errors += 1
            self._stats.cache_misses += 1
            return None

    async def set(
        self, key: str, value: Any, ttl: int | None = None
    ) -> bool:
        """Set value in Redis cache."""
        if not await self._ensure_connection():
            return False

        try:
            cache_key = self._build_key(key)
            ttl = ttl or self.config.default_ttl
            serialized_value = json.dumps(value)
            
            if ttl > 0:
                await self.redis.setex(cache_key, ttl, serialized_value)
            else:
                await self.redis.set(cache_key, serialized_value)
                
            return True
            
        except Exception as e:
            logger.warning("Redis set failed", key=key, error=str(e))
            self._stats.errors += 1
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        if not await self._ensure_connection():
            return False

        try:
            cache_key = self._build_key(key)
            result = await self.redis.delete(cache_key)
            return result > 0
            
        except Exception as e:
            logger.warning("Redis delete failed", key=key, error=str(e))
            self._stats.errors += 1
            return False

    async def clear(self) -> bool:
        """Clear Redis cache entries with prefix."""
        if not await self._ensure_connection():
            return False

        try:
            if self.config.key_prefix:
                pattern = f"{self.config.key_prefix}:*"
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
            else:
                await self.redis.flushdb()
            return True
            
        except Exception as e:
            logger.warning("Redis clear failed", error=str(e))
            self._stats.errors += 1
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        if not await self._ensure_connection():
            return False

        try:
            cache_key = self._build_key(key)
            result = await self.redis.exists(cache_key)
            return result > 0
            
        except Exception as e:
            logger.warning("Redis exists failed", key=key, error=str(e))
            self._stats.errors += 1
            return False

    async def get_stats(self) -> dict[str, Any]:
        """Get Redis cache statistics."""
        stats = {
            "cache_hits": self._stats.cache_hits,
            "cache_misses": self._stats.cache_misses,
            "hit_rate": (
                self._stats.cache_hits / max(1, self._stats.total_requests)
            ),
            "errors": self._stats.errors,
            "connected": self._connected,
        }
        
        if await self._ensure_connection():
            try:
                info = await self.redis.info("memory")
                stats.update({
                    "memory_usage": info.get("used_memory", 0),
                    "total_entries": await self.redis.dbsize(),
                })
            except Exception as e:
                logger.warning("Failed to get Redis stats", error=str(e))
                
        return stats

    async def health_check(self) -> dict[str, Any]:
        """Check Redis cache health status."""
        if self.config.disabled:
            return {"status": "disabled", "message": "Cache is disabled"}
        
        if not self._enabled:
            return {"status": "disabled", "message": "Redis cache is disabled"}
        
        try:
            # Try to ensure connection and ping Redis
            if await self._ensure_connection():
                await self.redis.ping()
                return {
                    "status": "healthy",
                    "backend": "redis",
                    "connected": True,
                    "connection_attempts": self._connection_attempts,
                }
            else:
                return {
                    "status": "unhealthy",
                    "backend": "redis", 
                    "connected": False,
                    "connection_attempts": self._connection_attempts,
                    "message": "Unable to connect to Redis"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "backend": "redis",
                "connected": False,
                "error": str(e)
            }


class MultiTierCache(CacheInterface):
    """Multi-tier cache combining memory (L1) and Redis (L2)."""

    def __init__(
        self,
        config: CacheConfig | None = None,
        l1_config: CacheConfig | None = None,
        redis_url: str | None = None,
        l1_size_ratio: float = 0.1,
    ):
        """Initialize multi-tier cache."""
        super().__init__(config)
        
        # Create L1 (memory) cache with smaller size
        if l1_config is None:
            l1_config = CacheConfig(
                default_ttl=min(300, self.config.default_ttl),
                max_size=int((self.config.max_size or 1000) * l1_size_ratio),
                eviction_policy="lru",
                key_prefix=self.config.key_prefix,
                enable_stats=True,
                disabled=self.config.disabled,
            )
            
        self.l1_cache = MemoryCache(l1_config)
        self.l2_cache = RedisCache(self.config, redis_url)
        
        logger.info(
            "Multi-tier cache initialized",
            l1_max_size=l1_config.max_size,
            l2_enabled=not self.config.disabled,
        )

    async def get(self, key: str) -> Any:
        """Get value from multi-tier cache (L1 first, then L2)."""
        if self.config.disabled:
            return None

        # Try L1 cache first
        value = await self.l1_cache.get(key)
        if value is not None:
            self._stats.cache_hits += 1
            return value

        # Try L2 cache
        value = await self.l2_cache.get(key)
        if value is not None:
            # Promote to L1 cache
            await self.l1_cache.set(key, value)
            self._stats.cache_hits += 1
            return value

        self._stats.cache_misses += 1
        return None

    async def set(
        self, key: str, value: Any, ttl: int | None = None
    ) -> bool:
        """Set value in both cache tiers."""
        if self.config.disabled:
            return False

        # Set in both caches
        l1_success = await self.l1_cache.set(key, value, ttl)
        l2_success = await self.l2_cache.set(key, value, ttl)
        
        return l1_success or l2_success

    async def delete(self, key: str) -> bool:
        """Delete key from both cache tiers."""
        if self.config.disabled:
            return False

        l1_success = await self.l1_cache.delete(key)
        l2_success = await self.l2_cache.delete(key)
        
        return l1_success or l2_success

    async def clear(self) -> bool:
        """Clear both cache tiers."""
        if self.config.disabled:
            return False

        l1_success = await self.l1_cache.clear()
        l2_success = await self.l2_cache.clear()
        
        return l1_success and l2_success

    async def exists(self, key: str) -> bool:
        """Check if key exists in either cache tier."""
        if self.config.disabled:
            return False

        return (
            await self.l1_cache.exists(key) or 
            await self.l2_cache.exists(key)
        )

    async def get_stats(self) -> dict[str, Any]:
        """Get combined statistics from both cache tiers."""
        l1_stats = await self.l1_cache.get_stats()
        l2_stats = await self.l2_cache.get_stats()
        
        return {
            "multi_tier": {
                "cache_hits": self._stats.cache_hits,
                "cache_misses": self._stats.cache_misses,
                "hit_rate": (
                    self._stats.cache_hits / max(1, self._stats.total_requests)
                ),
            },
            "l1_cache": l1_stats,
            "l2_cache": l2_stats,
        }

    async def health_check(self) -> dict[str, Any]:
        """Check multi-tier cache health status."""
        if self.config.disabled:
            return {"status": "disabled", "message": "Cache is disabled"}
        
        try:
            # Check health of both cache tiers
            l1_health = await self.l1_cache.health_check()
            l2_health = await self.l2_cache.health_check()
            
            # Determine overall health
            l1_healthy = l1_health.get("status") == "healthy"
            l2_healthy = l2_health.get("status") == "healthy"
            
            if l1_healthy and l2_healthy:
                overall_status = "healthy"
            elif l1_healthy or l2_healthy:
                overall_status = "degraded"
            else:
                overall_status = "unhealthy"
            
            return {
                "status": overall_status,
                "backend": "multi_tier",
                "l1_cache": l1_health,
                "l2_cache": l2_health,
                "message": f"L1 cache: {l1_health.get('status', 'unknown')}, L2 cache: {l2_health.get('status', 'unknown')}"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "backend": "multi_tier",
                "error": str(e)
            }