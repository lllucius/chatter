"""Tests for cache disable functionality."""

import pytest

from chatter.core.cache_interface import CacheConfig, CacheStats
from chatter.core.enhanced_memory_cache import EnhancedInMemoryCache
from chatter.core.enhanced_redis_cache import EnhancedRedisCache
from chatter.core.multi_tier_cache import MultiTierCache


class TestCacheDisableFunctionality:
    """Test cases for cache disable functionality."""

    @pytest.mark.asyncio
    async def test_memory_cache_disabled_operations(self):
        """Test that memory cache operations return expected values when disabled."""
        config = CacheConfig(max_size=10, disabled=True)
        cache = EnhancedInMemoryCache(config)

        # Verify cache is marked as disabled
        assert cache.is_disabled

        # Test get returns None
        result = await cache.get("test_key")
        assert result is None

        # Test set returns False
        result = await cache.set("test_key", "test_value")
        assert result is False

        # Test delete returns False
        result = await cache.delete("test_key")
        assert result is False

        # Test clear returns True (considered successful when disabled)
        result = await cache.clear()
        assert result is True

        # Test exists returns False
        result = await cache.exists("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_memory_cache_enabled_operations(self):
        """Test that memory cache operations work normally when not disabled."""
        config = CacheConfig(max_size=10, disabled=False)
        cache = EnhancedInMemoryCache(config)

        # Verify cache is not disabled
        assert not cache.is_disabled

        # Test set returns True
        result = await cache.set("test_key", "test_value")
        assert result is True

        # Test get returns the value
        result = await cache.get("test_key")
        assert result == "test_value"

        # Test exists returns True
        result = await cache.exists("test_key")
        assert result is True

        # Test delete returns True
        result = await cache.delete("test_key")
        assert result is True

        # Test clear returns True
        result = await cache.clear()
        assert result is True

    @pytest.mark.asyncio
    async def test_redis_cache_disabled_operations(self):
        """Test that Redis cache operations return expected values when disabled."""
        config = CacheConfig(disabled=True)
        cache = EnhancedRedisCache(config)

        # Verify cache is marked as disabled
        assert cache.is_disabled

        # Test get returns None (no connection attempt)
        result = await cache.get("test_key")
        assert result is None

        # Test set returns False (no connection attempt)
        result = await cache.set("test_key", "test_value")
        assert result is False

        # Test delete returns False (no connection attempt)
        result = await cache.delete("test_key")
        assert result is False

        # Test clear returns True (considered successful when disabled)
        result = await cache.clear()
        assert result is True

    @pytest.mark.asyncio
    async def test_multi_tier_cache_disabled_operations(self):
        """Test that multi-tier cache operations return expected values when disabled."""
        config = CacheConfig(max_size=100, disabled=True)
        cache = MultiTierCache(config)

        # Verify cache is marked as disabled
        assert cache.is_disabled

        # Test get returns None
        result = await cache.get("test_key")
        assert result is None

        # Test set returns False
        result = await cache.set("test_key", "test_value")
        assert result is False

        # Test delete returns False
        result = await cache.delete("test_key")
        assert result is False

        # Test clear returns True (considered successful when disabled)
        result = await cache.clear()
        assert result is True

    @pytest.mark.asyncio
    async def test_cache_config_disabled_default(self):
        """Test that CacheConfig disabled defaults to False."""
        config = CacheConfig()
        assert config.disabled is False

        # Test explicit False
        config = CacheConfig(disabled=False)
        assert config.disabled is False

        # Test explicit True
        config = CacheConfig(disabled=True)
        assert config.disabled is True

    def test_cache_interface_is_disabled_property(self):
        """Test the is_disabled property on cache interface."""
        config_enabled = CacheConfig(disabled=False)
        config_disabled = CacheConfig(disabled=True)

        cache_enabled = EnhancedInMemoryCache(config_enabled)
        cache_disabled = EnhancedInMemoryCache(config_disabled)

        assert not cache_enabled.is_disabled
        assert cache_disabled.is_disabled

    @pytest.mark.asyncio
    async def test_disabled_cache_still_provides_stats(self):
        """Test that disabled cache can still provide statistics."""
        config = CacheConfig(disabled=True, enable_stats=True)
        cache = EnhancedInMemoryCache(config)

        # Even when disabled, stats should be accessible
        stats = await cache.get_stats()
        assert isinstance(stats, CacheStats)
        assert stats.cache_hits == 0
        assert stats.cache_misses == 0


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_cache_disable.py -v
    pytest.main([__file__, "-v"])
