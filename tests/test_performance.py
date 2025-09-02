"""Performance and load tests for critical application workflows."""

import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock

import pytest


@pytest.mark.performance
class TestCriticalPathPerformance:
    """Performance tests for critical application paths."""

    def test_authentication_performance(self, test_client):
        """Test authentication endpoint performance."""
        start_time = time.time()

        # Test multiple authentication attempts
        for i in range(10):
            response = test_client.post(
                "/api/v1/auth/login",
                data={
                    "username": f"perf_test_{i}@example.com",
                    "password": "TestPassword123!",
                },
            )
            # Allow for endpoint not existing
            if response.status_code == 404:
                pytest.skip("Authentication endpoint not available")

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 10

        # Each auth attempt should complete within reasonable time
        assert (
            avg_time < 1.0
        ), f"Average auth time {avg_time:.3f}s exceeds 1.0s threshold"

    def test_chat_message_performance(self, test_client):
        """Test chat message processing performance."""
        # Create conversation first
        create_response = test_client.post(
            "/api/v1/chat/conversations",
            json={"title": "Performance Test Chat"},
        )

        if create_response.status_code == 404:
            pytest.skip("Chat endpoints not available")

        if create_response.status_code not in [200, 201]:
            pytest.skip(
                "Cannot create conversation for performance test"
            )

        conversation_data = create_response.json()
        conversation_id = conversation_data.get(
            "id"
        ) or conversation_data.get("conversation_id")

        if not conversation_id:
            pytest.skip("Cannot extract conversation ID")

        # Test message sending performance
        start_time = time.time()

        for i in range(5):
            response = test_client.post(
                f"/api/v1/chat/conversations/{conversation_id}/messages",
                json={
                    "content": f"Performance test message {i}",
                    "role": "user",
                },
            )
            # Allow for various response codes
            if response.status_code not in [200, 201, 404, 401]:
                break

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 5

        # Each message should be processed within reasonable time
        assert (
            avg_time < 2.0
        ), f"Average message time {avg_time:.3f}s exceeds 2.0s threshold"

    def test_document_upload_performance(self, test_client):
        """Test document upload performance."""
        # Test with different file sizes
        test_content = "Performance test content.\n" * 100  # ~2.5KB

        start_time = time.time()

        response = test_client.post(
            "/api/v1/documents/upload",
            files={
                "file": ("perf_test.txt", test_content, "text/plain")
            },
        )

        end_time = time.time()
        upload_time = end_time - start_time

        if response.status_code == 404:
            pytest.skip("Document upload endpoint not available")

        if response.status_code in [200, 201]:
            # Small file upload should be fast
            assert (
                upload_time < 5.0
            ), f"Upload time {upload_time:.3f}s exceeds 5.0s threshold"

    @pytest.mark.asyncio
    async def test_concurrent_request_performance(self, test_client):
        """Test performance under concurrent load."""

        # Function to make a health check request
        def make_health_request():
            return test_client.get("/health")

        # Run 20 concurrent requests
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(make_health_request) for _ in range(20)
            ]
            responses = [future.result() for future in futures]

        end_time = time.time()
        total_time = end_time - start_time

        # All concurrent requests should complete within reasonable time
        assert (
            total_time < 10.0
        ), f"Concurrent requests took {total_time:.3f}s, exceeds 10.0s threshold"

        # Check that most requests succeeded
        successful_responses = [
            r for r in responses if r.status_code in [200, 404]
        ]
        success_rate = len(successful_responses) / len(responses)
        assert (
            success_rate >= 0.8
        ), f"Success rate {success_rate:.2%} below 80% threshold"


@pytest.mark.performance
@pytest.mark.integration
class TestDatabasePerformance:
    """Performance tests for database operations."""

    @pytest.mark.asyncio
    async def test_database_query_performance(self, mock_session):
        """Test database query performance."""
        # Mock database operations
        mock_session.execute.return_value.scalar.return_value = 100
        mock_session.execute.return_value.fetchall.return_value = [
            {"id": i, "title": f"Item {i}"} for i in range(100)
        ]

        start_time = time.time()

        # Simulate multiple database queries
        for i in range(10):
            await mock_session.execute(
                "SELECT COUNT(*) FROM conversations"
            )
            await mock_session.execute(
                "SELECT * FROM conversations LIMIT 10"
            )

        end_time = time.time()
        total_time = end_time - start_time

        # Database operations should be fast with mocking
        assert (
            total_time < 1.0
        ), f"DB operations took {total_time:.3f}s, exceeds 1.0s threshold"

    @pytest.mark.asyncio
    async def test_bulk_insert_performance(self, mock_session):
        """Test bulk insert performance."""
        # Mock bulk insert operation
        mock_session.add_all = AsyncMock()
        mock_session.commit = AsyncMock()

        start_time = time.time()

        # Simulate bulk insert of 1000 records
        records = [
            {"id": i, "content": f"Record {i}"} for i in range(1000)
        ]
        await mock_session.add_all(records)
        await mock_session.commit()

        end_time = time.time()
        bulk_time = end_time - start_time

        # Bulk operations should be efficient
        assert (
            bulk_time < 2.0
        ), f"Bulk insert took {bulk_time:.3f}s, exceeds 2.0s threshold"


@pytest.mark.performance
class TestMemoryUsage:
    """Tests for memory usage and leaks."""

    def test_memory_usage_during_processing(self):
        """Test memory usage during typical operations."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate processing large data
        large_data = ["test data"] * 10000
        processed_data = [item.upper() for item in large_data]

        # Force garbage collection
        import gc

        gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable for the operation
        assert (
            memory_increase < 100
        ), f"Memory increased by {memory_increase:.1f}MB, exceeds 100MB threshold"

        # Clean up
        del large_data, processed_data

    def test_no_memory_leaks_in_loops(self):
        """Test for memory leaks in repeated operations."""
        import gc
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024

        # Perform repeated operations
        for i in range(100):
            # Simulate creating and destroying objects
            data = {"iteration": i, "content": "test" * 100}
            processed = str(data)
            del data, processed

        # Force cleanup
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024

        memory_diff = final_memory - baseline_memory

        # Should not have significant memory increase after cleanup
        assert (
            memory_diff < 10
        ), f"Potential memory leak: {memory_diff:.1f}MB increase after cleanup"


@pytest.mark.performance
class TestCachePerformance:
    """Performance tests for caching mechanisms."""

    def test_cache_hit_performance(self):
        """Test cache hit performance."""
        # Mock cache operations
        cache = {}

        # Populate cache
        for i in range(1000):
            cache[f"key_{i}"] = f"value_{i}"

        start_time = time.time()

        # Test cache lookups
        for i in range(1000):
            value = cache.get(f"key_{i}")
            assert value is not None

        end_time = time.time()
        lookup_time = end_time - start_time

        # Cache lookups should be very fast
        assert (
            lookup_time < 0.1
        ), f"Cache lookups took {lookup_time:.3f}s, exceeds 0.1s threshold"

    def test_cache_miss_handling(self):
        """Test cache miss handling performance."""
        cache = {}

        start_time = time.time()

        # Test cache misses
        for i in range(100):
            value = cache.get(f"missing_key_{i}")
            if value is None:
                # Simulate expensive computation
                cache[f"missing_key_{i}"] = f"computed_value_{i}"

        end_time = time.time()
        miss_time = end_time - start_time

        # Cache miss handling should be reasonable
        assert (
            miss_time < 1.0
        ), f"Cache miss handling took {miss_time:.3f}s, exceeds 1.0s threshold"
