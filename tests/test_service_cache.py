"""Tests for cache service functionality."""

import json
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chatter.services.cache import CacheService


@pytest.mark.unit
class TestCacheService:
    """Test cache service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache_service = CacheService(
            fallback_to_memory=True,
            key_prefix="test:"
        )

    @pytest.mark.asyncio
    async def test_cache_service_initialization(self):
        """Test cache service initialization."""
        # Act
        cache = CacheService(
            key_prefix="app:",
            fallback_to_memory=True
        )

        # Assert
        assert cache.key_prefix == "app:"
        assert cache._fallback_to_memory is True
        assert cache._memory_cache == {}

    @pytest.mark.asyncio
    async def test_set_and_get_cache_success(self):
        """Test successful cache set and get operations."""
        # Arrange
        key = "test_key"
        value = {"data": "test_value", "number": 42}

        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.set = AsyncMock(return_value=True)
            mock_redis.get = AsyncMock(return_value=json.dumps(value))
            self.cache_service._connected = True

            # Act - Set
            result_set = await self.cache_service.set(key, value)

            # Assert - Set
            assert result_set is True
            mock_redis.set.assert_called_once()

            # Act - Get
            result_get = await self.cache_service.get(key)

            # Assert - Get
            assert result_get == value
            mock_redis.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_cache_with_expiration(self):
        """Test cache set with expiration time."""
        # Arrange
        key = "expiring_key"
        value = "expiring_value"
        ttl = timedelta(hours=1)

        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.set = AsyncMock(return_value=True)
            self.cache_service._connected = True

            # Act
            await self.cache_service.set(key, value, ttl=ttl)

            # Assert
            mock_redis.set.assert_called_once_with(
                f"test:{key}",
                json.dumps(value),
                ex=int(ttl.total_seconds())
            )

    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """Test cache miss scenario."""
        # Arrange
        key = "nonexistent_key"

        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.get = AsyncMock(return_value=None)
            self.cache_service._connected = True

            # Act
            result = await self.cache_service.get(key)

            # Assert
            assert result is None

    @pytest.mark.asyncio
    async def test_delete_cache_success(self):
        """Test successful cache deletion."""
        # Arrange
        key = "key_to_delete"

        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.delete = AsyncMock(return_value=1)
            self.cache_service._connected = True

            # Act
            result = await self.cache_service.delete(key)

            # Assert
            assert result is True
            mock_redis.delete.assert_called_once_with(f"test:{key}")

    @pytest.mark.asyncio
    async def test_cache_exists_check(self):
        """Test cache key existence check."""
        # Arrange
        existing_key = "existing_key"
        nonexistent_key = "nonexistent_key"

        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.exists = AsyncMock(side_effect=[1, 0])  # First exists, second doesn't
            self.cache_service._connected = True

            # Act
            exists_result = await self.cache_service.exists(existing_key)
            not_exists_result = await self.cache_service.exists(nonexistent_key)

            # Assert
            assert exists_result is True
            assert not_exists_result is False

    @pytest.mark.asyncio
    async def test_cache_clear_all(self):
        """Test clearing all cache entries."""
        # Arrange
        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.flushdb = AsyncMock(return_value=True)
            self.cache_service._connected = True

            # Act
            result = await self.cache_service.clear()

            # Assert
            assert result is True
            mock_redis.flushdb.assert_called_once()

    @pytest.mark.asyncio
    async def test_memory_fallback_when_redis_unavailable(self):
        """Test fallback to memory cache when Redis is unavailable."""
        # Arrange
        cache = CacheService(fallback_to_memory=True)
        cache._connected = False
        key = "fallback_key"
        value = "fallback_value"

        # Act - Set in memory fallback
        result_set = await cache.set(key, value)

        # Assert - Set
        assert result_set is True
        assert cache._memory_cache[key] == {"value": value, "expires_at": None}

        # Act - Get from memory fallback
        result_get = await cache.get(key)

        # Assert - Get
        assert result_get == value

    @pytest.mark.asyncio
    async def test_memory_fallback_with_expiration(self):
        """Test memory fallback with expiration."""
        # Arrange
        cache = CacheService(fallback_to_memory=True)
        cache._connected = False
        key = "expiring_key"
        value = "expiring_value"
        ttl = timedelta(seconds=1)

        with patch('chatter.services.cache.datetime') as mock_datetime:
            # Mock current time
            mock_now = MagicMock()
            mock_datetime.now.return_value = mock_now
            mock_datetime.utcnow.return_value = mock_now

            # Act - Set with expiration
            await cache.set(key, value, ttl=ttl)

            # Assert expiration was set
            assert key in cache._memory_cache
            assert cache._memory_cache[key]["expires_at"] is not None

    @pytest.mark.asyncio
    async def test_connection_retry_mechanism(self):
        """Test Redis connection retry mechanism."""
        # Arrange
        cache = CacheService()

        with patch.object(cache, '_connect_redis') as mock_connect:
            mock_connect.side_effect = [Exception("Connection failed"), True]

            # Act
            await cache._ensure_connected()

            # Assert
            assert mock_connect.call_count == 2

    @pytest.mark.asyncio
    async def test_custom_serializer_deserializer(self):
        """Test custom serialization and deserialization."""
        # Arrange
        def custom_serializer(obj):
            return f"CUSTOM:{json.dumps(obj)}"

        def custom_deserializer(data):
            if data.startswith("CUSTOM:"):
                return json.loads(data[7:])
            return data

        cache = CacheService(
            serializer=custom_serializer,
            deserializer=custom_deserializer,
            fallback_to_memory=True
        )
        cache._connected = False

        key = "custom_key"
        value = {"custom": "data"}

        # Act
        await cache.set(key, value)
        result = await cache.get(key)

        # Assert
        assert result == value

    @pytest.mark.asyncio
    async def test_batch_operations(self):
        """Test batch set and get operations."""
        # Arrange
        items = {
            "key1": "value1",
            "key2": {"nested": "value2"},
            "key3": [1, 2, 3]
        }

        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.mset = AsyncMock(return_value=True)
            mock_redis.mget = AsyncMock(return_value=[
                json.dumps("value1"),
                json.dumps({"nested": "value2"}),
                json.dumps([1, 2, 3])
            ])
            self.cache_service._connected = True

            # Act - Batch set
            result_set = await self.cache_service.set_many(items)

            # Assert - Set
            assert result_set is True

            # Act - Batch get
            result_get = await self.cache_service.get_many(list(items.keys()))

            # Assert - Get
            assert len(result_get) == 3
            assert result_get[0] == "value1"
            assert result_get[1] == {"nested": "value2"}

    @pytest.mark.asyncio
    async def test_cache_stats_collection(self):
        """Test cache statistics collection."""
        # Arrange
        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.info = AsyncMock(return_value={
                "used_memory": 1024000,
                "keyspace_hits": 1500,
                "keyspace_misses": 500,
                "connected_clients": 10
            })
            self.cache_service._connected = True

            # Act
            stats = await self.cache_service.get_stats()

            # Assert
            assert stats["hit_ratio"] == 0.75  # 1500 / (1500 + 500)
            assert stats["memory_usage_mb"] == 1.0  # 1024000 / (1024*1024)
            assert stats["connected_clients"] == 10

    @pytest.mark.asyncio
    async def test_cache_key_pattern_operations(self):
        """Test cache operations with key patterns."""
        # Arrange
        pattern = "user:*"
        matching_keys = ["test:user:123", "test:user:456"]

        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.keys = AsyncMock(return_value=matching_keys)
            mock_redis.delete = AsyncMock(return_value=2)
            self.cache_service._connected = True

            # Act - Get keys by pattern
            keys = await self.cache_service.get_keys(pattern)

            # Assert - Keys
            assert keys == matching_keys

            # Act - Delete by pattern
            deleted_count = await self.cache_service.delete_pattern(pattern)

            # Assert - Delete
            assert deleted_count == 2

    @pytest.mark.asyncio
    async def test_cache_health_check(self):
        """Test cache service health check."""
        # Arrange
        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.ping = AsyncMock(return_value=True)
            self.cache_service._connected = True

            # Act
            health = await self.cache_service.health_check()

            # Assert
            assert health["status"] == "healthy"
            assert health["connected"] is True
            assert "response_time" in health

    @pytest.mark.asyncio
    async def test_cache_health_check_failure(self):
        """Test cache service health check when Redis is down."""
        # Arrange
        cache = CacheService(fallback_to_memory=True)
        cache._connected = False

        # Act
        health = await cache.health_check()

        # Assert
        assert health["status"] == "degraded"
        assert health["connected"] is False
        assert health["fallback_active"] is True


@pytest.mark.integration
class TestCacheServiceIntegration:
    """Integration tests for cache service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache_service = CacheService(
            key_prefix="integration_test:",
            fallback_to_memory=True
        )

    @pytest.mark.asyncio
    async def test_cache_integration_workflow(self):
        """Test complete cache workflow integration."""
        # Arrange
        test_data = {
            "session:user123": {"user_id": 123, "preferences": {"theme": "dark"}},
            "config:app": {"feature_flags": {"new_ui": True}},
            "temp:calculation": {"result": 42, "timestamp": "2024-01-01T00:00:00Z"}
        }

        with patch.object(self.cache_service, 'redis') as mock_redis:
            mock_redis.set = AsyncMock(return_value=True)
            mock_redis.get = AsyncMock(side_effect=lambda key: json.dumps(
                test_data.get(key.replace("integration_test:", ""))
            ))
            mock_redis.exists = AsyncMock(return_value=1)
            mock_redis.delete = AsyncMock(return_value=1)
            self.cache_service._connected = True

            # Test full workflow
            for key, value in test_data.items():
                # Set cache
                set_result = await self.cache_service.set(key, value)
                assert set_result is True

                # Verify exists
                exists_result = await self.cache_service.exists(key)
                assert exists_result is True

                # Get cache
                get_result = await self.cache_service.get(key)
                assert get_result == value

                # Delete cache
                delete_result = await self.cache_service.delete(key)
                assert delete_result is True

    @pytest.mark.asyncio
    async def test_cache_resilience_with_fallback(self):
        """Test cache resilience with memory fallback."""
        cache = CacheService(fallback_to_memory=True)

        # Test without Redis connection
        cache._connected = False

        # Should work with memory fallback
        await cache.set("resilience_key", "resilience_value")
        result = await cache.get("resilience_key")
        assert result == "resilience_value"

        # Test health check shows fallback is active
        health = await cache.health_check()
        assert health["fallback_active"] is True
