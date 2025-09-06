"""Tests for the unified cache system."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from chatter.core.cache_factory import (
    CacheBackend,
    CacheFactory,
    CacheType,
)
from chatter.core.cache_interface import (
    CacheConfig,
    CacheInterface,
    CacheStats,
)
from chatter.core.enhanced_memory_cache import EnhancedInMemoryCache
from chatter.core.unified_model_registry_cache import (
    UnifiedModelRegistryCache,
)
from chatter.core.unified_workflow_cache import UnifiedWorkflowCache
from chatter.models.registry import ModelType


class TestCacheInterface:
    """Test cases for the cache interface and implementations."""

    @pytest.fixture
    def cache_config(self):
        """Create test cache configuration."""
        return CacheConfig(
            default_ttl=300,
            max_size=100,
            eviction_policy="lru",
            key_prefix="test",
            enable_stats=True,
        )

    @pytest.fixture
    def memory_cache(self, cache_config):
        """Create memory cache for testing."""
        return EnhancedInMemoryCache(cache_config)

    @pytest.mark.asyncio
    async def test_memory_cache_basic_operations(self, memory_cache):
        """Test basic cache operations."""
        # Test set and get
        assert await memory_cache.set("key1", "value1", 60)
        value = await memory_cache.get("key1")
        assert value == "value1"

        # Test exists
        assert await memory_cache.exists("key1")
        assert not await memory_cache.exists("nonexistent")

        # Test delete
        assert await memory_cache.delete("key1")
        assert await memory_cache.get("key1") is None

        # Test clear
        await memory_cache.set("key2", "value2")
        await memory_cache.set("key3", "value3")
        assert await memory_cache.clear()
        assert await memory_cache.get("key2") is None
        assert await memory_cache.get("key3") is None

    @pytest.mark.asyncio
    async def test_memory_cache_batch_operations(self, memory_cache):
        """Test batch cache operations."""
        # Test mset
        items = {"key1": "value1", "key2": "value2", "key3": "value3"}
        assert await memory_cache.mset(items, 60)

        # Test mget
        result = await memory_cache.mget(
            ["key1", "key2", "key3", "nonexistent"]
        )
        assert result == {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }

    @pytest.mark.asyncio
    async def test_memory_cache_increment(self, memory_cache):
        """Test cache increment operations."""
        # Test increment on new key
        result = await memory_cache.increment("counter", 5)
        assert result == 5

        # Test increment on existing key
        result = await memory_cache.increment("counter", 3)
        assert result == 8

        # Test increment with default delta
        result = await memory_cache.increment("counter")
        assert result == 9

    @pytest.mark.asyncio
    async def test_memory_cache_ttl(self, memory_cache):
        """Test TTL functionality."""
        # Set with TTL
        await memory_cache.set("key1", "value1", 1)

        # Check TTL
        ttl = await memory_cache.ttl("key1")
        assert ttl is not None and ttl <= 1

        # Test expire
        await memory_cache.set("key2", "value2", 60)
        assert await memory_cache.expire("key2", 1)

        ttl = await memory_cache.ttl("key2")
        assert ttl is not None and ttl <= 1

    @pytest.mark.asyncio
    async def test_memory_cache_key_generation(self, memory_cache):
        """Test cache key generation."""
        # Test basic key generation
        key1 = memory_cache.make_key("prefix", "suffix")
        assert key1 == "test:prefix:suffix"

        # Test key generation with kwargs
        key2 = memory_cache.make_key(
            "type", param1="value1", param2="value2"
        )
        assert "param1=value1" in key2
        assert "param2=value2" in key2

        # Test key validation
        assert memory_cache.is_valid_key("valid_key")
        assert not memory_cache.is_valid_key("")
        assert not memory_cache.is_valid_key("key with spaces")
        assert not memory_cache.is_valid_key(
            "very_long_key" * 50
        )  # Too long

    @pytest.mark.asyncio
    async def test_memory_cache_eviction(self):
        """Test cache eviction policies."""
        # Create cache with small size for testing eviction
        config = CacheConfig(max_size=3, eviction_policy="lru")
        cache = EnhancedInMemoryCache(config)

        # Fill cache to capacity
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")

        # Access key1 to make it most recently used
        await cache.get("key1")

        # Add another key, should evict key2 (least recently used)
        await cache.set("key4", "value4")

        # key2 should be evicted
        assert await cache.get("key2") is None
        assert await cache.get("key1") == "value1"  # Should still exist
        assert await cache.get("key3") == "value3"  # Should still exist
        assert await cache.get("key4") == "value4"  # Should exist

    @pytest.mark.asyncio
    async def test_memory_cache_stats(self, memory_cache):
        """Test cache statistics."""
        # Perform some operations
        await memory_cache.set("key1", "value1")
        await memory_cache.get("key1")  # Hit
        await memory_cache.get("nonexistent")  # Miss

        stats = await memory_cache.get_stats()
        assert isinstance(stats, CacheStats)
        assert stats.total_entries >= 1
        assert stats.cache_hits >= 1
        assert stats.cache_misses >= 1
        assert 0 <= stats.hit_rate <= 1

    @pytest.mark.asyncio
    async def test_memory_cache_health_check(self, memory_cache):
        """Test cache health check."""
        health = await memory_cache.health_check()
        assert health["status"] == "healthy"
        assert health["operations"]["set"] is True
        assert health["operations"]["get"] is True
        assert health["operations"]["delete"] is True


class TestCacheFactory:
    """Test cases for the cache factory."""

    @pytest.fixture
    def factory(self):
        """Create cache factory for testing."""
        return CacheFactory()

    def test_create_different_cache_types(self, factory):
        """Test creating different cache types."""
        # Test model registry cache
        model_cache = factory.create_cache(
            CacheType.MODEL_REGISTRY, CacheBackend.MEMORY
        )
        assert isinstance(model_cache, CacheInterface)
        assert model_cache.config.key_prefix == "model_registry"

        # Test workflow cache
        workflow_cache = factory.create_cache(
            CacheType.WORKFLOW, CacheBackend.MEMORY
        )
        assert isinstance(workflow_cache, CacheInterface)
        assert workflow_cache.config.key_prefix == "workflow"

        # Test tool cache
        tool_cache = factory.create_cache(
            CacheType.TOOL, CacheBackend.MEMORY
        )
        assert isinstance(tool_cache, CacheInterface)
        assert tool_cache.config.key_prefix == "tool"

    def test_convenience_methods(self, factory):
        """Test convenience methods for cache creation."""
        model_cache = factory.create_model_registry_cache(
            backend=CacheBackend.MEMORY
        )
        assert isinstance(model_cache, CacheInterface)

        workflow_cache = factory.create_workflow_cache(
            backend=CacheBackend.MEMORY
        )
        assert isinstance(workflow_cache, CacheInterface)

        tool_cache = factory.create_tool_cache(
            backend=CacheBackend.MEMORY
        )
        assert isinstance(tool_cache, CacheInterface)

    @pytest.mark.asyncio
    async def test_health_check_all(self, factory):
        """Test health check for all cache instances."""
        # Create some caches
        factory.create_cache(
            CacheType.MODEL_REGISTRY, CacheBackend.MEMORY
        )
        factory.create_cache(CacheType.WORKFLOW, CacheBackend.MEMORY)

        health_results = await factory.health_check_all()
        assert health_results["overall_status"] in [
            "healthy",
            "degraded",
            "unhealthy",
        ]
        assert health_results["total_instances"] >= 2
        assert "cache_instances" in health_results

    @pytest.mark.asyncio
    async def test_get_stats_all(self, factory):
        """Test getting stats for all cache instances."""
        # Create and use some caches
        cache1 = factory.create_cache(
            CacheType.MODEL_REGISTRY, CacheBackend.MEMORY
        )
        cache2 = factory.create_cache(
            CacheType.WORKFLOW, CacheBackend.MEMORY
        )

        await cache1.set("test_key", "test_value")
        await cache2.set("test_key", "test_value")

        stats_results = await factory.get_stats_all()
        assert "aggregate" in stats_results
        assert "instances" in stats_results
        assert stats_results["aggregate"]["total_instances"] >= 2
        assert stats_results["aggregate"]["total_entries"] >= 2


class TestUnifiedModelRegistryCache:
    """Test cases for the unified model registry cache."""

    @pytest.fixture
    def mock_cache(self):
        """Create mock cache for testing."""
        cache = AsyncMock(spec=CacheInterface)
        cache.make_key = MagicMock(
            side_effect=lambda *args, **kwargs: ":".join(
                str(arg) for arg in args
            )
        )
        return cache

    @pytest.fixture
    def registry_cache(self, mock_cache):
        """Create unified model registry cache with mock."""
        return UnifiedModelRegistryCache(mock_cache)

    @pytest.mark.asyncio
    async def test_default_provider_operations(
        self, registry_cache, mock_cache
    ):
        """Test default provider cache operations."""
        # Test set default provider
        mock_cache.set.return_value = True
        result = await registry_cache.set_default_provider(
            ModelType.CHAT, "provider1"
        )
        assert result is True
        mock_cache.set.assert_called_once()

        # Test get default provider
        mock_cache.get.return_value = "provider1"
        result = await registry_cache.get_default_provider(
            ModelType.CHAT
        )
        assert result == "provider1"
        mock_cache.get.assert_called()

    @pytest.mark.asyncio
    async def test_provider_data_operations(
        self, registry_cache, mock_cache
    ):
        """Test provider data cache operations."""
        provider_data = {
            "id": "provider1",
            "name": "Test Provider",
            "active": True,
        }

        # Test set provider
        mock_cache.set.return_value = True
        result = await registry_cache.set_provider(
            "provider1", provider_data
        )
        assert result is True

        # Test get provider
        mock_cache.get.return_value = provider_data
        result = await registry_cache.get_provider("provider1")
        assert result == provider_data

        # Test invalidate provider
        mock_cache.delete.return_value = True
        result = await registry_cache.invalidate_provider("provider1")
        assert result is True

    @pytest.mark.asyncio
    async def test_list_operations(self, registry_cache, mock_cache):
        """Test list cache operations."""
        providers = [{"id": "provider1", "name": "Test Provider"}]

        # Test set provider list
        mock_cache.set.return_value = True
        result = await registry_cache.set_provider_list(
            provider_type="openai",
            active_only=True,
            page=1,
            per_page=20,
            providers=providers,
            total=1,
        )
        assert result is True

        # Test get provider list
        mock_cache.get.return_value = (providers, 1)
        result = await registry_cache.get_provider_list(
            provider_type="openai",
            active_only=True,
            page=1,
            per_page=20,
        )
        assert result == (providers, 1)


class TestUnifiedWorkflowCache:
    """Test cases for the unified workflow cache."""

    @pytest.fixture
    def mock_cache(self):
        """Create mock cache for testing."""
        cache = AsyncMock(spec=CacheInterface)
        cache.make_key = MagicMock(
            side_effect=lambda *args, **kwargs: f"unified:{':'.join(str(arg) for arg in args)}"
        )
        return cache

    @pytest.fixture
    def workflow_cache(self, mock_cache):
        """Create unified workflow cache with mock."""
        return UnifiedWorkflowCache(mock_cache)

    @pytest.mark.asyncio
    async def test_workflow_operations(
        self, workflow_cache, mock_cache
    ):
        """Test workflow cache operations."""
        config = {"param1": "value1", "param2": "value2"}
        workflow_obj = {"compiled": True, "data": "test_workflow"}

        # Test put workflow
        mock_cache.set.return_value = True
        result = await workflow_cache.put(
            "openai", "chat", config, workflow_obj
        )
        assert result is True
        mock_cache.set.assert_called_once()

        # Test get workflow
        mock_cache.get.return_value = workflow_obj
        result = await workflow_cache.get("openai", "chat", config)
        assert result == workflow_obj
        assert workflow_cache.cache_hits == 1

        # Test cache miss
        mock_cache.get.return_value = None
        result = await workflow_cache.get(
            "openai", "chat", {"different": "config"}
        )
        assert result is None
        assert workflow_cache.cache_misses == 1

    @pytest.mark.asyncio
    async def test_workflow_stats(self, workflow_cache, mock_cache):
        """Test workflow cache statistics."""
        mock_stats = CacheStats(
            total_entries=5,
            cache_hits=10,
            cache_misses=2,
            hit_rate=0.8,
            memory_usage=1024,
            evictions=1,
            errors=0,
        )
        mock_cache.get_stats.return_value = mock_stats

        # Set some local stats for testing
        workflow_cache.cache_hits = 15
        workflow_cache.cache_misses = 5

        stats = await workflow_cache.get_stats()
        assert stats["cache_size"] == 5
        assert stats["cache_hits"] == 15
        assert stats["cache_misses"] == 5
        assert stats["hit_rate"] == 0.75  # 15 / (15 + 5)
        assert stats["memory_usage"] == 1024
        assert stats["evictions"] == 1

    @pytest.mark.asyncio
    async def test_workflow_key_generation(self, workflow_cache):
        """Test workflow cache key generation."""
        config1 = {"param1": "value1", "param2": "value2"}
        config2 = {
            "param2": "value2",
            "param1": "value1",
        }  # Same but different order

        # Should generate the same key regardless of dict order
        key1 = workflow_cache._generate_cache_key(
            "openai", "chat", config1
        )
        key2 = workflow_cache._generate_cache_key(
            "openai", "chat", config2
        )
        assert key1 == key2

        # Different configs should generate different keys
        config3 = {"param1": "different_value", "param2": "value2"}
        key3 = workflow_cache._generate_cache_key(
            "openai", "chat", config3
        )
        assert key1 != key3


@pytest.mark.asyncio
async def test_cache_integration():
    """Integration test for the unified cache system."""
    # Create a real memory cache
    config = CacheConfig(
        default_ttl=300,
        max_size=100,
        eviction_policy="lru",
        key_prefix="integration_test",
    )
    cache = EnhancedInMemoryCache(config)

    # Test unified model registry cache
    registry_cache = UnifiedModelRegistryCache(cache)

    # Test setting and getting default provider
    await registry_cache.set_default_provider(ModelType.CHAT, "openai")
    result = await registry_cache.get_default_provider(ModelType.CHAT)
    assert result == "openai"

    # Test setting and getting provider data
    provider_data = {"id": "openai", "name": "OpenAI", "active": True}
    await registry_cache.set_provider("openai", provider_data)
    result = await registry_cache.get_provider("openai")
    assert result == provider_data

    # Test workflow cache
    workflow_cache = UnifiedWorkflowCache(cache)

    config_data = {"temperature": 0.7, "max_tokens": 100}
    workflow_obj = {"type": "chat", "compiled": True}

    # Test workflow caching
    await workflow_cache.put(
        "openai", "chat", config_data, workflow_obj
    )
    result = await workflow_cache.get("openai", "chat", config_data)
    assert result == workflow_obj

    # Test cache stats
    stats = await cache.get_stats()
    assert stats.total_entries > 0

    # Test health check
    health = await cache.health_check()
    assert health["status"] == "healthy"


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])
