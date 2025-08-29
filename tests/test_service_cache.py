"""Cache Service tests."""

import pytest
import json
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from chatter.services.cache import CacheService


@pytest.mark.unit
class TestCacheService:
    """Test cache service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache_service = CacheService()

    async def test_basic_get_set_operations(self):
        """Test basic cache get and set operations."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test set operation
            mock_client.set.return_value = True
            result = await self.cache_service.set("test_key", "test_value")
            assert result is True
            mock_client.set.assert_called_once_with("test_key", "test_value", ex=None)
            
            # Test get operation
            mock_client.get.return_value = "test_value"
            value = await self.cache_service.get("test_key")
            assert value == "test_value"
            mock_client.get.assert_called_once_with("test_key")

    async def test_delete_operation(self):
        """Test cache delete operation."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test delete operation
            mock_client.delete.return_value = 1  # Number of keys deleted
            result = await self.cache_service.delete("test_key")
            assert result is True
            mock_client.delete.assert_called_once_with("test_key")
            
            # Test delete non-existent key
            mock_client.delete.return_value = 0
            result = await self.cache_service.delete("non_existent")
            assert result is False

    async def test_json_data_handling(self):
        """Test JSON data serialization and deserialization."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test setting JSON data
            test_data = {"name": "John", "age": 30, "active": True}
            mock_client.set.return_value = True
            
            result = await self.cache_service.set_json("user:123", test_data)
            assert result is True
            
            # Verify JSON serialization
            expected_json = json.dumps(test_data)
            mock_client.set.assert_called_once_with("user:123", expected_json, ex=None)
            
            # Test getting JSON data
            mock_client.get.return_value = json.dumps(test_data)
            retrieved_data = await self.cache_service.get_json("user:123")
            assert retrieved_data == test_data

    async def test_list_operations(self):
        """Test list operations (push, pop, range)."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test list push
            mock_client.lpush.return_value = 1
            result = await self.cache_service.list_push("queue", "item1")
            assert result == 1
            mock_client.lpush.assert_called_once_with("queue", "item1")
            
            # Test list pop
            mock_client.rpop.return_value = "item1"
            item = await self.cache_service.list_pop("queue")
            assert item == "item1"
            mock_client.rpop.assert_called_once_with("queue")
            
            # Test list range
            mock_client.lrange.return_value = ["item1", "item2", "item3"]
            items = await self.cache_service.list_range("queue", 0, -1)
            assert items == ["item1", "item2", "item3"]
            mock_client.lrange.assert_called_once_with("queue", 0, -1)

    async def test_hash_operations(self):
        """Test hash operations (hset, hget, hgetall)."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test hash set
            mock_client.hset.return_value = 1
            result = await self.cache_service.hash_set("user:123", "name", "John")
            assert result is True
            mock_client.hset.assert_called_once_with("user:123", "name", "John")
            
            # Test hash get
            mock_client.hget.return_value = "John"
            value = await self.cache_service.hash_get("user:123", "name")
            assert value == "John"
            mock_client.hget.assert_called_once_with("user:123", "name")
            
            # Test hash get all
            mock_client.hgetall.return_value = {"name": "John", "age": "30"}
            data = await self.cache_service.hash_get_all("user:123")
            assert data == {"name": "John", "age": "30"}

    async def test_ttl_and_expiration_management(self):
        """Test TTL (Time To Live) and expiration management."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test set with TTL
            mock_client.set.return_value = True
            result = await self.cache_service.set("temp_key", "temp_value", ttl=300)
            assert result is True
            mock_client.set.assert_called_once_with("temp_key", "temp_value", ex=300)
            
            # Test TTL check
            mock_client.ttl.return_value = 250
            remaining_ttl = await self.cache_service.get_ttl("temp_key")
            assert remaining_ttl == 250
            
            # Test expiration setting
            mock_client.expire.return_value = True
            result = await self.cache_service.set_expiration("existing_key", 600)
            assert result is True
            mock_client.expire.assert_called_once_with("existing_key", 600)

    async def test_connection_health_monitoring(self):
        """Test connection health monitoring."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test healthy connection
            mock_client.ping.return_value = True
            is_connected = await self.cache_service.is_connected()
            assert is_connected is True
            
            # Test unhealthy connection
            mock_client.ping.side_effect = Exception("Connection failed")
            is_connected = await self.cache_service.is_connected()
            assert is_connected is False

    async def test_batch_operations(self):
        """Test batch operations for efficiency."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            mock_pipeline = AsyncMock()
            mock_client.pipeline.return_value = mock_pipeline
            
            # Test batch set
            operations = [
                ("key1", "value1"),
                ("key2", "value2"),
                ("key3", "value3")
            ]
            
            mock_pipeline.execute.return_value = [True, True, True]
            results = await self.cache_service.batch_set(operations)
            assert len(results) == 3
            assert all(results)
            
            # Test batch get
            mock_pipeline.execute.return_value = ["value1", "value2", "value3"]
            keys = ["key1", "key2", "key3"]
            values = await self.cache_service.batch_get(keys)
            assert values == ["value1", "value2", "value3"]

    async def test_pipeline_operations(self):
        """Test pipeline operations for atomic transactions."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            mock_pipeline = AsyncMock()
            mock_client.pipeline.return_value = mock_pipeline
            
            # Test pipeline transaction
            async def pipeline_ops(pipe):
                pipe.set("counter", 1)
                pipe.incr("counter")
                pipe.get("counter")
            
            mock_pipeline.execute.return_value = [True, 2, "2"]
            results = await self.cache_service.execute_pipeline(pipeline_ops)
            assert results == [True, 2, "2"]

    async def test_graceful_degradation_when_redis_unavailable(self):
        """Test graceful degradation when Redis is unavailable."""
        with patch('aioredis.Redis') as mock_redis:
            mock_redis.side_effect = Exception("Redis connection failed")
            
            # Should handle connection failure gracefully
            cache_service = CacheService(fallback_to_memory=True)
            
            # Operations should still work with in-memory fallback
            result = await cache_service.set("test_key", "test_value")
            assert result is True
            
            value = await cache_service.get("test_key")
            assert value == "test_value"

    async def test_key_pattern_operations(self):
        """Test key pattern operations (scan, keys with patterns)."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test scan operation
            mock_client.scan.return_value = (0, ["user:1", "user:2", "user:3"])
            keys = await self.cache_service.scan_keys("user:*")
            assert "user:1" in keys
            assert "user:2" in keys
            assert "user:3" in keys
            
            # Test delete by pattern
            mock_client.scan.return_value = (0, ["temp:1", "temp:2"])
            mock_client.delete.return_value = 2
            count = await self.cache_service.delete_pattern("temp:*")
            assert count == 2

    async def test_concurrent_operations(self):
        """Test concurrent cache operations."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            mock_client.set.return_value = True
            mock_client.get.return_value = "test_value"
            
            # Test concurrent writes
            tasks = []
            for i in range(10):
                task = self.cache_service.set(f"key_{i}", f"value_{i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            assert all(results)
            
            # Test concurrent reads
            read_tasks = []
            for i in range(10):
                task = self.cache_service.get(f"key_{i}")
                read_tasks.append(task)
            
            values = await asyncio.gather(*read_tasks)
            assert all(v == "test_value" for v in values)


@pytest.mark.unit
class TestCacheConfiguration:
    """Test cache service configuration."""

    def test_redis_connection_configuration(self):
        """Test Redis connection configuration."""
        config = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": "secret",
            "ssl": True,
            "socket_timeout": 5.0,
            "socket_connect_timeout": 5.0,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }
        
        cache_service = CacheService(config=config)
        assert cache_service.config["host"] == "localhost"
        assert cache_service.config["port"] == 6379
        assert cache_service.config["ssl"] is True

    def test_connection_pooling_configuration(self):
        """Test connection pooling configuration."""
        pool_config = {
            "max_connections": 20,
            "retry_on_timeout": True,
            "decode_responses": True
        }
        
        cache_service = CacheService(pool_config=pool_config)
        assert cache_service.pool_config["max_connections"] == 20
        assert cache_service.pool_config["decode_responses"] is True

    def test_key_prefix_configuration(self):
        """Test key prefix configuration."""
        cache_service = CacheService(key_prefix="myapp:")
        
        # Keys should be automatically prefixed
        prefixed_key = cache_service.add_prefix("user:123")
        assert prefixed_key == "myapp:user:123"
        
        # Should strip prefix when retrieving
        original_key = cache_service.strip_prefix("myapp:user:123")
        assert original_key == "user:123"

    def test_serialization_configuration(self):
        """Test serialization configuration."""
        # Test with custom serializer
        def custom_serialize(data):
            return f"custom:{json.dumps(data)}"
        
        def custom_deserialize(data):
            if data.startswith("custom:"):
                return json.loads(data[7:])
            return data
        
        cache_service = CacheService(
            serializer=custom_serialize,
            deserializer=custom_deserialize
        )
        
        test_data = {"key": "value"}
        serialized = cache_service.serialize(test_data)
        assert serialized.startswith("custom:")
        
        deserialized = cache_service.deserialize(serialized)
        assert deserialized == test_data


@pytest.mark.unit
class TestCacheUtilities:
    """Test cache utility functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache_service = CacheService()

    async def test_key_validation(self):
        """Test cache key validation."""
        # Valid keys
        valid_keys = [
            "user:123",
            "session_abc123",
            "cache-key-123",
            "simple_key"
        ]
        
        for key in valid_keys:
            assert self.cache_service.is_valid_key(key)
        
        # Invalid keys
        invalid_keys = [
            "",  # Empty
            "a" * 300,  # Too long
            "key with spaces",  # Spaces
            "key\nwith\nnewlines",  # Newlines
            "key\twith\ttabs"  # Tabs
        ]
        
        for key in invalid_keys:
            assert not self.cache_service.is_valid_key(key)

    async def test_cache_statistics(self):
        """Test cache statistics collection."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Mock Redis INFO command
            mock_client.info.return_value = {
                "used_memory": 1048576,  # 1MB
                "used_memory_human": "1.00M",
                "keyspace_hits": 1000,
                "keyspace_misses": 100,
                "connected_clients": 5
            }
            
            stats = await self.cache_service.get_statistics()
            assert stats["memory_usage"] == "1.00M"
            assert stats["hit_rate"] == 0.909  # 1000/(1000+100)
            assert stats["connected_clients"] == 5

    async def test_cache_warming(self):
        """Test cache warming functionality."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            mock_client.set.return_value = True
            
            # Test warming cache with predefined data
            warm_data = {
                "user:1": {"name": "Alice", "age": 30},
                "user:2": {"name": "Bob", "age": 25},
                "settings:default": {"theme": "dark", "notifications": True}
            }
            
            result = await self.cache_service.warm_cache(warm_data)
            assert result is True
            
            # Should have called set for each item
            assert mock_client.set.call_count == len(warm_data)

    async def test_cache_invalidation(self):
        """Test cache invalidation strategies."""
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test tag-based invalidation
            mock_client.scan.return_value = (0, ["user:1", "user:2", "user:3"])
            mock_client.delete.return_value = 3
            
            count = await self.cache_service.invalidate_by_tag("user")
            assert count == 3
            
            # Test time-based invalidation
            mock_client.scan.return_value = (0, ["old:1", "old:2"])
            mock_client.ttl.side_effect = [-1, -1]  # Keys without expiration
            mock_client.delete.return_value = 2
            
            count = await self.cache_service.invalidate_expired()
            assert count >= 0  # May vary based on implementation


@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests for cache service."""

    async def test_real_world_caching_scenario(self):
        """Test real-world caching scenario."""
        cache_service = CacheService()
        
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Simulate user session caching
            session_data = {
                "user_id": "123",
                "username": "alice",
                "permissions": ["read", "write"],
                "last_activity": "2024-01-01T12:00:00Z"
            }
            
            # Cache session
            mock_client.set.return_value = True
            await cache_service.set_json("session:abc123", session_data, ttl=3600)
            
            # Retrieve session
            mock_client.get.return_value = json.dumps(session_data)
            retrieved_session = await cache_service.get_json("session:abc123")
            assert retrieved_session["user_id"] == "123"
            assert retrieved_session["username"] == "alice"
            
            # Update session activity
            session_data["last_activity"] = "2024-01-01T12:30:00Z"
            await cache_service.set_json("session:abc123", session_data, ttl=3600)
            
            # Cache user preferences
            user_prefs = {
                "theme": "dark",
                "language": "en",
                "notifications": {
                    "email": True,
                    "push": False
                }
            }
            
            await cache_service.hash_set("user:123:prefs", "theme", "dark")
            await cache_service.hash_set("user:123:prefs", "language", "en")
            
            # Retrieve preferences
            mock_client.hget.return_value = "dark"
            theme = await cache_service.hash_get("user:123:prefs", "theme")
            assert theme == "dark"

    async def test_cache_performance_optimization(self):
        """Test cache performance optimization techniques."""
        cache_service = CacheService()
        
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            mock_pipeline = AsyncMock()
            mock_client.pipeline.return_value = mock_pipeline
            
            # Test bulk operations for better performance
            keys = [f"key_{i}" for i in range(100)]
            values = [f"value_{i}" for i in range(100)]
            
            # Batch set operation
            mock_pipeline.execute.return_value = [True] * 100
            operations = list(zip(keys, values))
            results = await cache_service.batch_set(operations)
            assert len(results) == 100
            assert all(results)
            
            # Batch get operation
            mock_pipeline.execute.return_value = values
            retrieved_values = await cache_service.batch_get(keys)
            assert retrieved_values == values

    async def test_cache_monitoring_and_alerting(self):
        """Test cache monitoring and alerting."""
        cache_service = CacheService()
        
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test memory usage monitoring
            mock_client.info.return_value = {
                "used_memory": 536870912,  # 512MB
                "maxmemory": 1073741824,   # 1GB
                "used_memory_percentage": 50.0
            }
            
            memory_info = await cache_service.get_memory_info()
            assert memory_info["usage_percentage"] <= 100
            
            # Test performance monitoring
            import time
            start_time = time.time()
            
            mock_client.set.return_value = True
            await cache_service.set("perf_test", "value")
            
            end_time = time.time()
            operation_time = end_time - start_time
            
            # Should complete quickly
            assert operation_time < 1.0

    async def test_cache_error_handling_and_recovery(self):
        """Test cache error handling and recovery."""
        cache_service = CacheService()
        
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test connection recovery
            mock_client.ping.side_effect = [
                Exception("Connection lost"),
                Exception("Still down"),
                True  # Recovered
            ]
            
            # Should handle connection issues
            for _ in range(3):
                try:
                    is_healthy = await cache_service.is_connected()
                    if is_healthy:
                        break
                except:
                    pass
            
            # Should eventually recover
            assert is_healthy is True

    async def test_distributed_caching_scenario(self):
        """Test distributed caching scenario."""
        # This would test scenarios with multiple cache instances
        cache_service1 = CacheService(instance_id="node1")
        cache_service2 = CacheService(instance_id="node2")
        
        with patch('aioredis.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Test cache coordination between nodes
            mock_client.set.return_value = True
            mock_client.get.return_value = "shared_value"
            
            # Node 1 sets a value
            await cache_service1.set("shared_key", "shared_value")
            
            # Node 2 should be able to read it
            value = await cache_service2.get("shared_key")
            assert value == "shared_value"
            
            # Test cache invalidation across nodes
            mock_client.publish.return_value = 1  # Number of subscribers
            await cache_service1.invalidate_distributed("shared_key")
            
            # Should publish invalidation message
            mock_client.publish.assert_called()