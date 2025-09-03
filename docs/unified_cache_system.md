# Unified Cache System

This document describes the new unified cache system that consolidates all caching throughout the Chatter application.

## Overview

The unified cache system replaces multiple disparate caching implementations with a single, consistent interface that supports multiple backends and provides advanced features like multi-tier caching and intelligent eviction.

### Key Benefits

- **Consistent Interface**: All caches use the same get/set/delete/clear API
- **Multiple Backends**: Memory, Redis, and multi-tier (L1 + L2) caching
- **Type-Specific Configs**: Different cache types have optimized configurations
- **Performance Monitoring**: Unified statistics and health checking
- **Graceful Fallback**: Automatic fallback when Redis is unavailable
- **Easy Migration**: Drop-in replacements for existing cache usage

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cache Factory                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   Memory    │ │    Redis    │ │      Multi-Tier        │ │
│  │   Cache     │ │    Cache    │ │   (Memory + Redis)     │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                    CacheInterface
                            │
┌─────────────────────────────────────────────────────────────┐
│                 Specialized Caches                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │    Model    │ │  Workflow   │ │    Tool     │ │ Session │ │
│  │  Registry   │ │   Cache     │ │   Cache     │ │  Cache  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CacheInterface

Abstract base class that defines the standard interface for all cache implementations:

```python
from chatter.core.cache_interface import CacheInterface

# Standard methods available on all caches
async def get(key: str) -> Any
async def set(key: str, value: Any, ttl: Optional[int] = None) -> bool
async def delete(key: str) -> bool
async def clear() -> bool
async def exists(key: str) -> bool
async def keys(pattern: Optional[str] = None) -> List[str]
async def mget(keys: List[str]) -> Dict[str, Any]
async def mset(items: Dict[str, Any], ttl: Optional[int] = None) -> bool
async def increment(key: str, delta: int = 1) -> int
async def expire(key: str, ttl: int) -> bool
async def ttl(key: str) -> Optional[int]
async def get_stats() -> CacheStats
async def health_check() -> Dict[str, Any]
```

### 2. Cache Backends

#### EnhancedInMemoryCache
- LRU eviction with configurable policies (LRU, TTL, Random)
- TTL support with automatic expiration
- Thread-safe with async locks
- Memory usage tracking

#### EnhancedRedisCache  
- Production-ready Redis implementation
- Connection pooling and retry logic
- Graceful error handling with circuit breaker pattern
- Batch operations support

#### MultiTierCache
- Combines in-memory (L1) and Redis (L2) caching
- Intelligent promotion from L2 to L1 based on access patterns
- Configurable L1/L2 size ratios
- Automatic invalidation and synchronization

### 3. Cache Factory

Creates appropriate cache instances based on configuration:

```python
from chatter.core.cache_factory import CacheFactory, CacheType, CacheBackend

factory = CacheFactory()

# Create different cache types
model_cache = factory.create_cache(CacheType.MODEL_REGISTRY)
workflow_cache = factory.create_cache(CacheType.WORKFLOW)
tool_cache = factory.create_cache(CacheType.TOOL)

# Or use convenience methods
model_cache = factory.create_model_registry_cache()
workflow_cache = factory.create_workflow_cache()
```

## Configuration

Add these settings to your environment or configuration:

```python
# Cache backend selection
CACHE_BACKEND="auto"  # auto, memory, redis, multi_tier

# Type-specific TTL settings (seconds)
CACHE_MODEL_REGISTRY_TTL=1800  # 30 minutes
CACHE_WORKFLOW_TTL=3600        # 1 hour  
CACHE_TOOL_TTL=3600           # 1 hour
CACHE_SESSION_TTL=300         # 5 minutes

# Cache size and behavior
CACHE_MAX_MEMORY_SIZE=1000
CACHE_L1_SIZE_RATIO=0.1       # For multi-tier caching
CACHE_EVICTION_POLICY="lru"   # lru, ttl, random

# Redis settings (existing)
CACHE_ENABLED=true
REDIS_URL="redis://localhost:6379/0"
```

## Migration Guide

### Automatic Migration

Use the provided migration script to automatically update your code:

```bash
python scripts/migrate_cache.py /path/to/chatter
```

This will:
1. Update imports to use unified cache system
2. Convert synchronous cache calls to async
3. Create a backup (optional)
4. Report all changes made

### Manual Migration

#### Model Registry Cache

**Before:**
```python
from chatter.utils.caching import get_registry_cache

cache = get_registry_cache()
provider_id = cache.get_default_provider(model_type)
cache.set_default_provider(model_type, provider_id)
```

**After:**
```python
from chatter.core.unified_model_registry_cache import get_registry_cache

cache = get_registry_cache()
provider_id = await cache.get_default_provider(model_type)
await cache.set_default_provider(model_type, provider_id)
```

#### Workflow Cache

**Before:**
```python
from chatter.core.workflow_performance import workflow_cache

cached_workflow = workflow_cache.get(provider, type, config)
workflow_cache.put(provider, type, config, workflow)
```

**After:**
```python
from chatter.core.unified_workflow_cache import get_unified_workflow_cache

workflow_cache = get_unified_workflow_cache()
cached_workflow = await workflow_cache.get(provider, type, config)
await workflow_cache.put(provider, type, config, workflow)
```

#### Redis Cache Service

**Before:**
```python
from chatter.services.cache import get_cache_service

cache = await get_cache_service()
await cache.set("key", "value")
```

**After:**
```python
from chatter.core.cache_factory import get_general_cache

cache = get_general_cache()
await cache.set("key", "value")
```

## Usage Examples

### Basic Usage

```python
from chatter.core.cache_factory import get_model_registry_cache

# Get cache instance
cache = get_model_registry_cache()

# Basic operations
await cache.set("user:123", {"name": "John", "role": "admin"})
user = await cache.get("user:123")
await cache.delete("user:123")

# Batch operations
users = {"user:1": {"name": "Alice"}, "user:2": {"name": "Bob"}}
await cache.mset(users, ttl=3600)
batch_users = await cache.mget(["user:1", "user:2"])

# Advanced operations
await cache.increment("page_views", 1)
ttl = await cache.ttl("user:123")
exists = await cache.exists("user:123")
```

### Specialized Cache Types

```python
from chatter.core.unified_model_registry_cache import UnifiedModelRegistryCache
from chatter.core.unified_workflow_cache import UnifiedWorkflowCache

# Model registry cache
registry_cache = UnifiedModelRegistryCache()
await registry_cache.set_default_provider(ModelType.CHAT, "openai")
provider_id = await registry_cache.get_default_provider(ModelType.CHAT)

# Workflow cache
workflow_cache = UnifiedWorkflowCache()
config = {"temperature": 0.7, "max_tokens": 100}
await workflow_cache.put("openai", "chat", config, compiled_workflow)
cached_workflow = await workflow_cache.get("openai", "chat", config)
```

### Cache Monitoring

```python
from chatter.core.cache_factory import cache_factory

# Health check for all caches
health = await cache_factory.health_check_all()
print(f"Overall status: {health['overall_status']}")

# Statistics for all caches  
stats = await cache_factory.get_stats_all()
print(f"Total entries: {stats['aggregate']['total_entries']}")
print(f"Hit rate: {stats['aggregate']['overall_hit_rate']:.2%}")

# Individual cache stats
cache = get_model_registry_cache()
cache_stats = await cache.get_stats()
print(f"Cache hits: {cache_stats.cache_hits}")
print(f"Cache misses: {cache_stats.cache_misses}")
print(f"Hit rate: {cache_stats.hit_rate:.2%}")
```

## Performance Considerations

### Cache Backend Selection

- **Memory**: Fastest, but limited by single instance memory
- **Redis**: Shared across instances, persistent, but network latency
- **Multi-Tier**: Best of both worlds, automatic optimization

### TTL Recommendations

- **Model Registry**: 30 minutes (data changes infrequently)
- **Workflows**: 1 hour (compilation is expensive)
- **Tools**: 1 hour (tool definitions are stable)
- **Sessions**: 5 minutes (user-specific, security sensitive)

### Memory Management

- Use appropriate `max_size` based on available memory
- Monitor eviction rates and adjust if too high
- Consider LRU eviction for general data, TTL for time-sensitive data

## Monitoring and Debugging

### Cache Statistics

All caches provide comprehensive statistics:

```python
stats = await cache.get_stats()
print(f"""
Cache Statistics:
- Total entries: {stats.total_entries}
- Cache hits: {stats.cache_hits}
- Cache misses: {stats.cache_misses}
- Hit rate: {stats.hit_rate:.2%}
- Memory usage: {stats.memory_usage} bytes
- Evictions: {stats.evictions}
- Errors: {stats.errors}
""")
```

### Health Checks

Monitor cache health in your application:

```python
health = await cache.health_check()
if health["status"] != "healthy":
    logger.warning(f"Cache unhealthy: {health}")
```

### Logging

Enable debug logging to monitor cache operations:

```python
import logging
logging.getLogger("chatter.core.cache").setLevel(logging.DEBUG)
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failures**
   - Check `REDIS_URL` configuration
   - Verify Redis server is running
   - Check network connectivity
   - The system gracefully falls back to memory cache

2. **High Memory Usage**
   - Reduce `CACHE_MAX_MEMORY_SIZE`
   - Adjust TTL values to expire data sooner
   - Monitor eviction rates

3. **Low Hit Rates**
   - Check if TTL values are too short
   - Verify cache keys are consistent
   - Monitor access patterns

4. **Performance Issues**
   - Use multi-tier caching for optimal performance
   - Consider reducing cache size for better locality
   - Monitor network latency to Redis

### Migration Issues

1. **Import Errors**
   - Run the migration script to update imports
   - Check for circular import dependencies
   - Verify all cache method calls use `await`

2. **Async/Await Errors**
   - All cache methods are now async and require `await`
   - Update calling code to be async functions
   - Use `asyncio.run()` for top-level calls

## Best Practices

1. **Use Type-Specific Caches**: Use the appropriate cache type for your data
2. **Set Appropriate TTLs**: Balance between performance and data freshness
3. **Monitor Cache Performance**: Regular check cache hit rates and adjust
4. **Handle Cache Failures**: Always handle cache misses gracefully
5. **Use Batch Operations**: Use `mget`/`mset` for multiple items
6. **Consider Data Serialization**: Ensure cached data can be serialized to JSON
7. **Implement Cache Warming**: Pre-populate caches with frequently accessed data

## Future Enhancements

- **Distributed Caching**: Support for Redis Cluster
- **Cache Compression**: Automatic compression for large values  
- **Cache Encryption**: Encryption for sensitive cached data
- **Advanced Eviction**: Custom eviction policies based on usage patterns
- **Cache Mirroring**: Mirror writes across multiple cache instances
- **GraphQL Integration**: Cache GraphQL query results automatically