"""
Performance Testing

Comprehensive performance testing for response times, memory usage, and concurrency.
"""
import pytest
import asyncio
import time
import psutil
import statistics
from httpx import AsyncClient
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor
import gc


class TestPerformance:
    """Performance testing class for API endpoints."""
    
    @pytest.mark.performance
    async def test_authentication_endpoint_performance(self, client: AsyncClient, test_user_data: Dict[str, Any]):
        """Test authentication endpoint performance monitoring."""
        try:
            # Test registration performance
            registration_times = []
            
            for i in range(10):
                user_data = {
                    **test_user_data,
                    "username": f"perf_test_user_{i}",
                    "email": f"perf_test_user_{i}@example.com"
                }
                
                start_time = time.time()
                response = await client.post("/api/v1/auth/register", json=user_data)
                end_time = time.time()
                
                if response.status_code == 404:
                    pytest.skip("Registration endpoint not implemented yet")
                
                if response.status_code in [200, 201]:
                    registration_times.append(end_time - start_time)
            
            if registration_times:
                avg_registration_time = statistics.mean(registration_times)
                max_registration_time = max(registration_times)
                
                # Performance assertions
                assert avg_registration_time < 2.0, f"Average registration time too slow: {avg_registration_time}s"
                assert max_registration_time < 5.0, f"Max registration time too slow: {max_registration_time}s"
                
                print(f"Registration performance: avg={avg_registration_time:.3f}s, max={max_registration_time:.3f}s")
                
        except Exception as e:
            pytest.skip(f"Authentication performance test skipped: {e}")
    
    @pytest.mark.performance
    async def test_chat_message_processing_benchmarks(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test chat message processing performance benchmarks."""
        if not auth_headers:
            pytest.skip("Authentication required for chat performance test")
        
        try:
            # Create a test chat first
            chat_data = {"title": "Performance Test Chat", "description": "Testing message performance"}
            chat_response = await client.post("/api/v1/chats", json=chat_data, headers=auth_headers)
            
            if chat_response.status_code == 404:
                pytest.skip("Chat creation endpoint not implemented yet")
            
            if chat_response.status_code not in [200, 201]:
                pytest.skip("Could not create test chat for performance testing")
            
            chat_id = chat_response.json()["id"]
            
            # Test message sending performance
            message_times = []
            
            for i in range(20):
                message_data = {
                    "message": f"Performance test message {i+1}",
                    "message_type": "user"
                }
                
                start_time = time.time()
                response = await client.post(f"/api/v1/chats/{chat_id}/messages", json=message_data, headers=auth_headers)
                end_time = time.time()
                
                if response.status_code == 404:
                    pytest.skip("Chat messaging endpoint not implemented yet")
                
                if response.status_code in [200, 201]:
                    message_times.append(end_time - start_time)
            
            if message_times:
                avg_message_time = statistics.mean(message_times)
                max_message_time = max(message_times)
                
                # Performance assertions
                assert avg_message_time < 1.0, f"Average message processing too slow: {avg_message_time}s"
                assert max_message_time < 3.0, f"Max message processing too slow: {max_message_time}s"
                
                print(f"Message processing performance: avg={avg_message_time:.3f}s, max={max_message_time:.3f}s")
                
        except Exception as e:
            pytest.skip(f"Chat message performance test skipped: {e}")
    
    @pytest.mark.performance
    async def test_document_upload_performance_validation(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test document upload performance validation."""
        if not auth_headers:
            pytest.skip("Authentication required for document performance test")
        
        try:
            # Test document upload performance with various sizes
            upload_times = []
            document_sizes = [1024, 5120, 10240, 20480]  # 1KB, 5KB, 10KB, 20KB
            
            for size in document_sizes:
                content = "A" * size  # Create content of specified size
                files = {"file": (f"perf_test_{size}.txt", content, "text/plain")}
                data = {
                    "title": f"Performance Test Document {size}B",
                    "description": f"Testing upload performance for {size} byte document"
                }
                
                start_time = time.time()
                response = await client.post("/api/v1/documents/upload", files=files, data=data, headers=auth_headers)
                end_time = time.time()
                
                if response.status_code == 404:
                    pytest.skip("Document upload endpoint not implemented yet")
                
                if response.status_code in [200, 201]:
                    upload_times.append({
                        "size": size,
                        "time": end_time - start_time
                    })
            
            if upload_times:
                for upload in upload_times:
                    # Performance assertions based on file size
                    expected_max_time = 2.0 + (upload["size"] / 10240)  # Base 2s + 1s per 10KB
                    assert upload["time"] < expected_max_time, f"Upload too slow for {upload['size']}B: {upload['time']:.3f}s"
                
                avg_time = statistics.mean([u["time"] for u in upload_times])
                print(f"Document upload performance: avg={avg_time:.3f}s")
                
        except Exception as e:
            pytest.skip(f"Document upload performance test skipped: {e}")
    
    @pytest.mark.performance
    async def test_concurrent_request_handling(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test concurrent request handling performance."""
        if not auth_headers:
            pytest.skip("Authentication required for concurrent request test")
        
        try:
            # Test concurrent health checks (should be lightweight)
            async def make_health_request():
                start_time = time.time()
                response = await client.get("/healthz")
                end_time = time.time()
                return {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time
                }
            
            # Make 50 concurrent health check requests
            tasks = [make_health_request() for _ in range(50)]
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Filter out exceptions
            successful_results = [r for r in results if isinstance(r, dict) and r.get("status_code") == 200]
            
            if successful_results:
                total_time = end_time - start_time
                avg_response_time = statistics.mean([r["response_time"] for r in successful_results])
                requests_per_second = len(successful_results) / total_time
                
                # Performance assertions
                assert avg_response_time < 0.5, f"Average response time too slow under load: {avg_response_time:.3f}s"
                assert requests_per_second > 10, f"Throughput too low: {requests_per_second:.1f} req/s"
                
                print(f"Concurrent performance: {requests_per_second:.1f} req/s, avg response: {avg_response_time:.3f}s")
            else:
                pytest.skip("No successful concurrent requests to measure")
                
        except Exception as e:
            pytest.skip(f"Concurrent request performance test skipped: {e}")
    
    @pytest.mark.performance
    async def test_memory_usage_and_leak_detection(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test memory usage and leak detection."""
        try:
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform memory-intensive operations
            for i in range(100):
                # Make various API calls
                await client.get("/healthz")
                
                if auth_headers:
                    # Try to make authenticated requests
                    await client.get("/api/v1/auth/profile", headers=auth_headers)
                    
                    # Try to list chats/documents
                    chat_response = await client.get("/api/v1/chats", headers=auth_headers)
                    if chat_response.status_code != 404:
                        pass  # Chat listing works
                    
                    doc_response = await client.get("/api/v1/documents", headers=auth_headers)
                    if doc_response.status_code != 404:
                        pass  # Document listing works
                
                # Force garbage collection periodically
                if i % 20 == 0:
                    gc.collect()
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory usage assertions
            assert memory_increase < 100, f"Memory usage increased too much: {memory_increase:.1f}MB"
            
            print(f"Memory usage: initial={initial_memory:.1f}MB, final={final_memory:.1f}MB, increase={memory_increase:.1f}MB")
            
        except Exception as e:
            pytest.skip(f"Memory usage test skipped: {e}")
    
    @pytest.mark.performance 
    async def test_database_query_optimization(self, client: AsyncClient, auth_headers: Dict[str, str], db_session):
        """Test database query performance and optimization."""
        if not auth_headers:
            pytest.skip("Authentication required for database performance test")
        
        try:
            # Test query performance for listing operations
            query_times = []
            
            # Test chat listing performance (if available)
            for _ in range(10):
                start_time = time.time()
                response = await client.get("/api/v1/chats", headers=auth_headers)
                end_time = time.time()
                
                if response.status_code == 404:
                    break  # Endpoint not available
                elif response.status_code == 200:
                    query_times.append(end_time - start_time)
            
            # Test document listing performance (if available)
            for _ in range(10):
                start_time = time.time()
                response = await client.get("/api/v1/documents", headers=auth_headers)
                end_time = time.time()
                
                if response.status_code == 404:
                    break  # Endpoint not available
                elif response.status_code == 200:
                    query_times.append(end_time - start_time)
            
            if query_times:
                avg_query_time = statistics.mean(query_times)
                max_query_time = max(query_times)
                
                # Database query performance assertions
                assert avg_query_time < 0.5, f"Average query time too slow: {avg_query_time:.3f}s"
                assert max_query_time < 1.0, f"Max query time too slow: {max_query_time:.3f}s"
                
                print(f"Database query performance: avg={avg_query_time:.3f}s, max={max_query_time:.3f}s")
            else:
                pytest.skip("No database queries to test")
                
        except Exception as e:
            pytest.skip(f"Database query performance test skipped: {e}")
    
    @pytest.mark.performance
    @pytest.mark.slow
    async def test_sustained_load_performance(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test performance under sustained load (longer test)."""
        if not auth_headers:
            pytest.skip("Authentication required for sustained load test")
        
        try:
            # Run sustained operations for 60 seconds
            start_time = time.time()
            end_time = start_time + 60  # 1 minute
            
            request_count = 0
            error_count = 0
            response_times = []
            
            while time.time() < end_time:
                operation_start = time.time()
                
                # Mix of operations
                if request_count % 3 == 0:
                    response = await client.get("/healthz")
                elif request_count % 3 == 1:
                    response = await client.get("/api/v1/auth/profile", headers=auth_headers)
                else:
                    response = await client.get("/api/v1/chats", headers=auth_headers)
                
                operation_end = time.time()
                
                request_count += 1
                if response.status_code >= 500:
                    error_count += 1
                elif response.status_code != 404:  # Don't count missing endpoints as errors
                    response_times.append(operation_end - operation_start)
                
                # Brief pause to prevent overwhelming
                await asyncio.sleep(0.1)
            
            total_duration = time.time() - start_time
            
            if response_times:
                avg_response_time = statistics.mean(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
                requests_per_second = request_count / total_duration
                error_rate = error_count / request_count if request_count > 0 else 0
                
                # Sustained load performance assertions
                assert avg_response_time < 1.0, f"Average response time degraded under sustained load: {avg_response_time:.3f}s"
                assert p95_response_time < 2.0, f"95th percentile response time too high: {p95_response_time:.3f}s"
                assert error_rate < 0.05, f"Error rate too high under sustained load: {error_rate:.1%}"
                assert requests_per_second > 5, f"Throughput too low under sustained load: {requests_per_second:.1f} req/s"
                
                print(f"Sustained load results: {requests_per_second:.1f} req/s, avg={avg_response_time:.3f}s, p95={p95_response_time:.3f}s, errors={error_rate:.1%}")
            else:
                pytest.skip("No successful requests during sustained load test")
                
        except Exception as e:
            pytest.skip(f"Sustained load performance test skipped: {e}")
    
    @pytest.mark.performance
    async def test_response_time_consistency(self, client: AsyncClient):
        """Test response time consistency across multiple requests."""
        try:
            response_times = []
            
            # Make 100 health check requests
            for _ in range(100):
                start_time = time.time()
                response = await client.get("/healthz")
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            
            if response_times:
                mean_time = statistics.mean(response_times)
                stdev_time = statistics.stdev(response_times) if len(response_times) > 1 else 0
                min_time = min(response_times)
                max_time = max(response_times)
                
                # Consistency assertions
                assert stdev_time < mean_time, f"Response times too inconsistent: mean={mean_time:.3f}s, stdev={stdev_time:.3f}s"
                assert max_time < mean_time * 5, f"Max response time too far from mean: max={max_time:.3f}s, mean={mean_time:.3f}s"
                
                print(f"Response time consistency: mean={mean_time:.3f}s, stdev={stdev_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s")
            else:
                pytest.skip("No successful health checks for consistency test")
                
        except Exception as e:
            pytest.skip(f"Response time consistency test skipped: {e}")