"""Cache factory for creating and managing cache instances."""

from enum import Enum
from typing import Dict, Optional, Any

from chatter.core.cache_interface import CacheInterface, CacheConfig
from chatter.core.enhanced_memory_cache import EnhancedInMemoryCache
from chatter.core.enhanced_redis_cache import EnhancedRedisCache
from chatter.core.multi_tier_cache import MultiTierCache
from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class CacheBackend(Enum):
    """Available cache backend types."""
    MEMORY = "memory"
    REDIS = "redis"
    MULTI_TIER = "multi_tier"


class CacheType(Enum):
    """Cache types for different use cases."""
    MODEL_REGISTRY = "model_registry"
    WORKFLOW = "workflow"
    TOOL = "tool"
    GENERAL = "general"
    SESSION = "session"


class CacheFactory:
    """Factory for creating and managing cache instances."""
    
    def __init__(self):
        """Initialize cache factory."""
        self._cache_instances: Dict[str, CacheInterface] = {}
        self._default_configs = self._create_default_configs()
        
        logger.debug("Cache factory initialized")
    
    def _create_default_configs(self) -> Dict[CacheType, CacheConfig]:
        """Create default configurations for different cache types.
        
        Returns:
            Dictionary of cache type to default configuration
        """
        return {
            CacheType.MODEL_REGISTRY: CacheConfig(
                default_ttl=settings.cache_ttl_medium,  # 30 minutes
                max_size=500,
                eviction_policy="lru",
                key_prefix="model_registry",
                enable_stats=True
            ),
            CacheType.WORKFLOW: CacheConfig(
                default_ttl=settings.cache_ttl_long,  # 1 hour
                max_size=100,
                eviction_policy="lru",
                key_prefix="workflow",
                enable_stats=True
            ),
            CacheType.TOOL: CacheConfig(
                default_ttl=settings.cache_ttl_long,  # 1 hour
                max_size=200,
                eviction_policy="lru",
                key_prefix="tool",
                enable_stats=True
            ),
            CacheType.GENERAL: CacheConfig(
                default_ttl=settings.cache_ttl,  # Default TTL
                max_size=1000,
                eviction_policy="lru",
                key_prefix="general",
                enable_stats=True
            ),
            CacheType.SESSION: CacheConfig(
                default_ttl=settings.cache_ttl_short,  # 5 minutes
                max_size=1000,
                eviction_policy="ttl",  # Sessions expire by time
                key_prefix="session",
                enable_stats=True
            )
        }
    
    def create_cache(
        self,
        cache_type: CacheType,
        backend: Optional[CacheBackend] = None,
        config: Optional[CacheConfig] = None,
        **kwargs
    ) -> CacheInterface:
        """Create a cache instance.
        
        Args:
            cache_type: Type of cache to create
            backend: Cache backend to use (auto-detected if None)
            config: Custom cache configuration (uses default if None)
            **kwargs: Additional arguments for cache initialization
            
        Returns:
            Cache instance
        """
        # Use provided config or default for cache type
        if config is None:
            config = self._default_configs.get(cache_type, self._default_configs[CacheType.GENERAL])
        
        # Auto-detect backend if not specified
        if backend is None:
            backend = self._detect_optimal_backend()
        
        # Create instance key for potential reuse
        instance_key = f"{cache_type.value}_{backend.value}_{id(config)}"
        
        # Return existing instance if available (for singleton-like behavior)
        if instance_key in self._cache_instances:
            logger.debug(f"Reusing existing cache instance", cache_type=cache_type.value, backend=backend.value)
            return self._cache_instances[instance_key]
        
        # Create new cache instance
        cache_instance = self._create_cache_instance(backend, config, **kwargs)
        
        # Store instance for potential reuse
        self._cache_instances[instance_key] = cache_instance
        
        logger.info(
            "Created cache instance",
            cache_type=cache_type.value,
            backend=backend.value,
            max_size=config.max_size,
            default_ttl=config.default_ttl,
            key_prefix=config.key_prefix
        )
        
        return cache_instance
    
    def _detect_optimal_backend(self) -> CacheBackend:
        """Detect the optimal cache backend based on configuration and availability.
        
        Returns:
            Optimal cache backend
        """
        # If Redis is explicitly disabled, use memory
        if not settings.cache_enabled:
            logger.debug("Redis disabled, using memory cache")
            return CacheBackend.MEMORY
        
        # If we're in development mode, prefer multi-tier for best performance
        if settings.environment == "development":
            logger.debug("Development environment, using multi-tier cache")
            return CacheBackend.MULTI_TIER
        
        # For production, also prefer multi-tier if Redis is available
        try:
            # Quick Redis availability check could be added here
            return CacheBackend.MULTI_TIER
        except Exception:
            logger.warning("Redis not available, falling back to memory cache")
            return CacheBackend.MEMORY
    
    def _create_cache_instance(
        self,
        backend: CacheBackend,
        config: CacheConfig,
        **kwargs
    ) -> CacheInterface:
        """Create cache instance based on backend type.
        
        Args:
            backend: Cache backend type
            config: Cache configuration
            **kwargs: Additional arguments
            
        Returns:
            Cache instance
        """
        if backend == CacheBackend.MEMORY:
            return EnhancedInMemoryCache(config)
        
        elif backend == CacheBackend.REDIS:
            redis_url = kwargs.get('redis_url')
            pool_config = kwargs.get('pool_config')
            return EnhancedRedisCache(config, redis_url, pool_config)
        
        elif backend == CacheBackend.MULTI_TIER:
            redis_url = kwargs.get('redis_url')
            l1_config = kwargs.get('l1_config')
            l1_size_ratio = kwargs.get('l1_size_ratio', 0.1)
            return MultiTierCache(config, l1_config, redis_url, l1_size_ratio)
        
        else:
            raise ValueError(f"Unsupported cache backend: {backend}")
    
    def get_cache(self, cache_type: CacheType) -> Optional[CacheInterface]:
        """Get existing cache instance if available.
        
        Args:
            cache_type: Type of cache to get
            
        Returns:
            Cache instance or None if not found
        """
        # Look for any instance of this cache type
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
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all cache instances.
        
        Returns:
            Health status for all cache instances
        """
        health_results = {}
        
        for instance_key, cache_instance in self._cache_instances.items():
            try:
                health_result = await cache_instance.health_check()
                health_results[instance_key] = health_result
            except Exception as e:
                health_results[instance_key] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Overall health summary
        all_healthy = all(
            result.get("status") == "healthy"
            for result in health_results.values()
        )
        
        overall_status = "healthy" if all_healthy else "degraded"
        if not health_results:
            overall_status = "no_caches"
        elif all(result.get("status") == "unhealthy" for result in health_results.values()):
            overall_status = "unhealthy"
        
        return {
            "overall_status": overall_status,
            "cache_instances": health_results,
            "total_instances": len(self._cache_instances)
        }
    
    async def get_stats_all(self) -> Dict[str, Any]:
        """Get statistics for all cache instances.
        
        Returns:
            Statistics for all cache instances
        """
        stats_results = {}
        
        for instance_key, cache_instance in self._cache_instances.items():
            try:
                stats = await cache_instance.get_stats()
                stats_results[instance_key] = {
                    "total_entries": stats.total_entries,
                    "cache_hits": stats.cache_hits,
                    "cache_misses": stats.cache_misses,
                    "hit_rate": stats.hit_rate,
                    "memory_usage": stats.memory_usage,
                    "evictions": stats.evictions,
                    "errors": stats.errors
                }
            except Exception as e:
                stats_results[instance_key] = {
                    "error": str(e)
                }
        
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
        overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0
        
        return {
            "aggregate": {
                "total_entries": total_entries,
                "total_hits": total_hits,
                "total_misses": total_misses,
                "overall_hit_rate": overall_hit_rate,
                "total_instances": len(self._cache_instances)
            },
            "instances": stats_results
        }
    
    async def clear_all(self) -> Dict[str, bool]:
        """Clear all cache instances.
        
        Returns:
            Dictionary of instance key to clear success status
        """
        clear_results = {}
        
        for instance_key, cache_instance in self._cache_instances.items():
            try:
                success = await cache_instance.clear()
                clear_results[instance_key] = success
            except Exception as e:
                logger.error(f"Failed to clear cache {instance_key}", error=str(e))
                clear_results[instance_key] = False
        
        successful_clears = sum(1 for success in clear_results.values() if success)
        logger.info(f"Cleared {successful_clears}/{len(clear_results)} cache instances")
        
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