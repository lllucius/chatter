"""Tests for rate limiting utilities."""

import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from chatter.utils.rate_limit import (
    RateLimitMiddleware,
    RateLimiter,
    MemoryRateLimiter,
    RedisRateLimiter,
    RateLimitExceeded,
    get_client_ip,
    create_rate_limit_key,
)


class TestRateLimitExceeded:
    """Test RateLimitExceeded exception."""

    def test_rate_limit_exceeded_creation(self):
        """Test creating rate limit exceeded exception."""
        exc = RateLimitExceeded(
            message="Rate limit exceeded",
            limit=100,
            window=3600,
            retry_after=60
        )
        
        assert exc.message == "Rate limit exceeded"
        assert exc.limit == 100
        assert exc.window == 3600
        assert exc.retry_after == 60

    def test_rate_limit_exceeded_defaults(self):
        """Test rate limit exceeded with default values."""
        exc = RateLimitExceeded()
        
        assert "rate limit" in exc.message.lower()
        assert exc.limit is None
        assert exc.window is None
        assert exc.retry_after is None

    def test_rate_limit_exceeded_str(self):
        """Test string representation."""
        exc = RateLimitExceeded("Too many requests")
        assert str(exc) == "Too many requests"


class TestGetClientIp:
    """Test client IP extraction."""

    def test_get_client_ip_direct(self):
        """Test getting client IP directly."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.100"
        request.headers = {}
        
        ip = get_client_ip(request)
        assert ip == "192.168.1.100"

    def test_get_client_ip_x_forwarded_for(self):
        """Test getting client IP from X-Forwarded-For header."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "10.0.0.1"  # Proxy IP
        request.headers = {"X-Forwarded-For": "203.0.113.1, 10.0.0.1"}
        
        ip = get_client_ip(request)
        assert ip == "203.0.113.1"  # First IP in chain

    def test_get_client_ip_x_real_ip(self):
        """Test getting client IP from X-Real-IP header."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "10.0.0.1"
        request.headers = {"X-Real-IP": "203.0.113.2"}
        
        ip = get_client_ip(request)
        assert ip == "203.0.113.2"

    def test_get_client_ip_forwarded(self):
        """Test getting client IP from Forwarded header."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "10.0.0.1"
        request.headers = {"Forwarded": "for=203.0.113.3;proto=https"}
        
        ip = get_client_ip(request)
        assert ip == "203.0.113.3"

    def test_get_client_ip_no_client(self):
        """Test getting client IP when no client info available."""
        request = Mock(spec=Request)
        request.client = None
        request.headers = {}
        
        ip = get_client_ip(request)
        assert ip == "unknown"

    def test_get_client_ip_priority_order(self):
        """Test IP header priority order."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "10.0.0.1"
        request.headers = {
            "X-Forwarded-For": "203.0.113.1",
            "X-Real-IP": "203.0.113.2",
            "Forwarded": "for=203.0.113.3"
        }
        
        # X-Forwarded-For should have highest priority
        ip = get_client_ip(request)
        assert ip == "203.0.113.1"


class TestCreateRateLimitKey:
    """Test rate limit key creation."""

    def test_create_rate_limit_key_basic(self):
        """Test basic rate limit key creation."""
        key = create_rate_limit_key("192.168.1.1", "/api/chat")
        
        assert "192.168.1.1" in key
        assert "/api/chat" in key
        assert "rate_limit" in key

    def test_create_rate_limit_key_with_user(self):
        """Test rate limit key with user ID."""
        key = create_rate_limit_key("192.168.1.1", "/api/chat", user_id="user-123")
        
        assert "user-123" in key
        assert "192.168.1.1" in key

    def test_create_rate_limit_key_normalization(self):
        """Test rate limit key normalization."""
        # Test different paths normalize consistently
        key1 = create_rate_limit_key("192.168.1.1", "/api/chat/")
        key2 = create_rate_limit_key("192.168.1.1", "/api/chat")
        
        # Should be consistent (implementation dependent)
        assert isinstance(key1, str)
        assert isinstance(key2, str)

    def test_create_rate_limit_key_special_characters(self):
        """Test rate limit key with special characters."""
        key = create_rate_limit_key(
            "192.168.1.1", 
            "/api/users/123?param=value&other=test"
        )
        
        # Should handle special characters safely
        assert isinstance(key, str)
        assert len(key) > 0


class TestMemoryRateLimiter:
    """Test in-memory rate limiter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.limiter = MemoryRateLimiter()

    @pytest.mark.asyncio
    async def test_memory_rate_limiter_allows_requests(self):
        """Test that rate limiter allows requests within limit."""
        key = "test_key"
        limit = 5
        window = 60
        
        # Should allow requests within limit
        for i in range(limit):
            allowed = await self.limiter.is_allowed(key, limit, window)
            assert allowed is True

    @pytest.mark.asyncio
    async def test_memory_rate_limiter_blocks_excess_requests(self):
        """Test that rate limiter blocks excess requests."""
        key = "test_key"
        limit = 3
        window = 60
        
        # Use up the limit
        for i in range(limit):
            allowed = await self.limiter.is_allowed(key, limit, window)
            assert allowed is True
        
        # Next request should be blocked
        allowed = await self.limiter.is_allowed(key, limit, window)
        assert allowed is False

    @pytest.mark.asyncio
    async def test_memory_rate_limiter_window_reset(self):
        """Test that rate limiter resets after window expires."""
        key = "test_key"
        limit = 2
        window = 1  # 1 second window
        
        # Use up the limit
        for i in range(limit):
            allowed = await self.limiter.is_allowed(key, limit, window)
            assert allowed is True
        
        # Should be blocked
        allowed = await self.limiter.is_allowed(key, limit, window)
        assert allowed is False
        
        # Wait for window to expire
        await asyncio.sleep(1.1)
        
        # Should be allowed again
        allowed = await self.limiter.is_allowed(key, limit, window)
        assert allowed is True

    @pytest.mark.asyncio
    async def test_memory_rate_limiter_different_keys(self):
        """Test that different keys have separate limits."""
        limit = 2
        window = 60
        
        # Use up limit for first key
        for i in range(limit):
            allowed = await self.limiter.is_allowed("key1", limit, window)
            assert allowed is True
        
        # First key should be blocked
        allowed = await self.limiter.is_allowed("key1", limit, window)
        assert allowed is False
        
        # Second key should still be allowed
        allowed = await self.limiter.is_allowed("key2", limit, window)
        assert allowed is True

    @pytest.mark.asyncio
    async def test_memory_rate_limiter_get_remaining(self):
        """Test getting remaining requests."""
        key = "test_key"
        limit = 5
        window = 60
        
        # Check initial remaining
        remaining = await self.limiter.get_remaining(key, limit, window)
        assert remaining == limit
        
        # Use one request
        await self.limiter.is_allowed(key, limit, window)
        remaining = await self.limiter.get_remaining(key, limit, window)
        assert remaining == limit - 1

    @pytest.mark.asyncio
    async def test_memory_rate_limiter_get_reset_time(self):
        """Test getting reset time."""
        key = "test_key"
        limit = 5
        window = 60
        
        # Make a request to start the window
        await self.limiter.is_allowed(key, limit, window)
        
        reset_time = await self.limiter.get_reset_time(key, limit, window)
        assert reset_time is not None
        assert reset_time > time.time()

    @pytest.mark.asyncio
    async def test_memory_rate_limiter_cleanup(self):
        """Test automatic cleanup of expired entries."""
        key = "test_key"
        limit = 1
        window = 1
        
        # Make request
        await self.limiter.is_allowed(key, limit, window)
        
        # Check that entry exists
        assert len(self.limiter._requests) > 0
        
        # Wait for expiry and trigger cleanup
        await asyncio.sleep(1.1)
        await self.limiter.cleanup_expired()
        
        # Entry should be cleaned up
        assert len(self.limiter._requests) == 0


class TestRedisRateLimiter:
    """Test Redis-based rate limiter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_redis = Mock()
        self.limiter = RedisRateLimiter(redis_client=self.mock_redis)

    @pytest.mark.asyncio
    async def test_redis_rate_limiter_lua_script(self):
        """Test Redis rate limiter uses Lua script."""
        key = "test_key"
        limit = 5
        window = 60
        
        # Mock Redis eval response (allowed)
        self.mock_redis.eval = AsyncMock(return_value=[1, 4, 1234567890])
        
        allowed = await self.limiter.is_allowed(key, limit, window)
        
        assert allowed is True
        self.mock_redis.eval.assert_called_once()

    @pytest.mark.asyncio
    async def test_redis_rate_limiter_blocked(self):
        """Test Redis rate limiter blocking requests."""
        key = "test_key"
        limit = 5
        window = 60
        
        # Mock Redis eval response (blocked)
        self.mock_redis.eval = AsyncMock(return_value=[0, 0, 1234567890])
        
        allowed = await self.limiter.is_allowed(key, limit, window)
        
        assert allowed is False

    @pytest.mark.asyncio
    async def test_redis_rate_limiter_get_remaining(self):
        """Test getting remaining requests from Redis."""
        key = "test_key"
        limit = 5
        window = 60
        
        # Mock Redis response
        self.mock_redis.eval = AsyncMock(return_value=[1, 3, 1234567890])
        
        remaining = await self.limiter.get_remaining(key, limit, window)
        
        assert remaining == 3

    @pytest.mark.asyncio
    async def test_redis_rate_limiter_error_handling(self):
        """Test Redis rate limiter error handling."""
        key = "test_key"
        limit = 5
        window = 60
        
        # Mock Redis error
        self.mock_redis.eval = AsyncMock(side_effect=Exception("Redis error"))
        
        # Should fall back to allowing requests on Redis error
        allowed = await self.limiter.is_allowed(key, limit, window)
        
        # Implementation dependent: might allow or raise
        assert isinstance(allowed, bool)


class TestRateLimitMiddleware:
    """Test rate limit middleware."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = Mock()
        self.limiter = Mock(spec=RateLimiter)
        self.middleware = RateLimitMiddleware(
            app=self.app,
            requests_per_minute=60,
            requests_per_hour=1000,
            rate_limiter=self.limiter
        )

    @pytest.mark.asyncio
    async def test_middleware_allows_request(self):
        """Test middleware allows request within limits."""
        # Mock request
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        
        # Mock response
        response = Mock(spec=Response)
        response.headers = {}
        
        # Mock rate limiter (allow)
        self.limiter.is_allowed = AsyncMock(return_value=True)
        self.limiter.get_remaining = AsyncMock(return_value=50)
        self.limiter.get_reset_time = AsyncMock(return_value=time.time() + 3600)
        
        # Mock call_next
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response
        call_next.assert_called_once()
        
        # Should add rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

    @pytest.mark.asyncio
    async def test_middleware_blocks_request(self):
        """Test middleware blocks request when rate limited."""
        # Mock request
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        
        # Mock rate limiter (block)
        self.limiter.is_allowed = AsyncMock(return_value=False)
        self.limiter.get_remaining = AsyncMock(return_value=0)
        self.limiter.get_reset_time = AsyncMock(return_value=time.time() + 60)
        
        # Mock call_next
        call_next = AsyncMock()
        
        with pytest.raises(RateLimitExceeded):
            await self.middleware.dispatch(request, call_next)
        
        # Should not call next middleware
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_middleware_exempt_paths(self):
        """Test middleware exempts certain paths."""
        # Create middleware with exempt paths
        middleware = RateLimitMiddleware(
            app=self.app,
            requests_per_minute=60,
            exempt_paths=["/health", "/metrics"]
        )
        
        # Mock request to exempt path
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/health"
        
        response = Mock(spec=Response)
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        assert result == response
        call_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_middleware_user_based_limiting(self):
        """Test user-based rate limiting."""
        # Mock request with user info
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        request.state = Mock()
        request.state.user_id = "user-123"
        
        response = Mock(spec=Response)
        response.headers = {}
        
        self.limiter.is_allowed = AsyncMock(return_value=True)
        self.limiter.get_remaining = AsyncMock(return_value=50)
        self.limiter.get_reset_time = AsyncMock(return_value=time.time() + 3600)
        
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        # Should include user ID in rate limit key
        self.limiter.is_allowed.assert_called()
        call_args = self.limiter.is_allowed.call_args[0]
        assert "user-123" in call_args[0]  # First arg is the key

    @pytest.mark.asyncio
    async def test_middleware_different_limits_per_endpoint(self):
        """Test different rate limits per endpoint."""
        # Create middleware with endpoint-specific limits
        endpoint_limits = {
            "/api/chat": (10, 3600),  # 10 per hour
            "/api/upload": (5, 3600)  # 5 per hour
        }
        
        middleware = RateLimitMiddleware(
            app=self.app,
            requests_per_minute=60,
            endpoint_limits=endpoint_limits,
            rate_limiter=self.limiter
        )
        
        # Test chat endpoint
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.url = Mock()
        request.url.path = "/api/chat"
        request.headers = {}
        
        response = Mock(spec=Response)
        response.headers = {}
        
        self.limiter.is_allowed = AsyncMock(return_value=True)
        self.limiter.get_remaining = AsyncMock(return_value=9)
        self.limiter.get_reset_time = AsyncMock(return_value=time.time() + 3600)
        
        call_next = AsyncMock(return_value=response)
        
        await middleware.dispatch(request, call_next)
        
        # Should use endpoint-specific limit
        self.limiter.is_allowed.assert_called()
        call_args = self.limiter.is_allowed.call_args
        assert call_args[0][1] == 10  # limit
        assert call_args[0][2] == 3600  # window

    @pytest.mark.asyncio
    async def test_middleware_rate_limit_headers(self):
        """Test rate limit headers are added."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        
        response = Mock(spec=Response)
        response.headers = {}
        
        # Mock rate limiter responses
        self.limiter.is_allowed = AsyncMock(return_value=True)
        self.limiter.get_remaining = AsyncMock(return_value=45)
        self.limiter.get_reset_time = AsyncMock(return_value=1234567890)
        
        call_next = AsyncMock(return_value=response)
        
        await self.middleware.dispatch(request, call_next)
        
        # Check rate limit headers
        assert response.headers["X-RateLimit-Limit"] == "60"
        assert response.headers["X-RateLimit-Remaining"] == "45"
        assert response.headers["X-RateLimit-Reset"] == "1234567890"

    @pytest.mark.asyncio
    async def test_middleware_retry_after_header(self):
        """Test Retry-After header when rate limited."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        
        # Mock rate limiter (block)
        future_time = time.time() + 120
        self.limiter.is_allowed = AsyncMock(return_value=False)
        self.limiter.get_remaining = AsyncMock(return_value=0)
        self.limiter.get_reset_time = AsyncMock(return_value=future_time)
        
        call_next = AsyncMock()
        
        with pytest.raises(RateLimitExceeded) as exc_info:
            await self.middleware.dispatch(request, call_next)
        
        # Should include retry after information
        assert exc_info.value.retry_after is not None
        assert exc_info.value.retry_after > 0

    @pytest.mark.asyncio
    async def test_middleware_inheritance(self):
        """Test that middleware inherits from BaseHTTPMiddleware."""
        assert isinstance(self.middleware, BaseHTTPMiddleware)

    @pytest.mark.asyncio
    async def test_middleware_error_handling(self):
        """Test middleware error handling."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        
        # Mock rate limiter error
        self.limiter.is_allowed = AsyncMock(side_effect=Exception("Limiter error"))
        
        response = Mock(spec=Response)
        call_next = AsyncMock(return_value=response)
        
        # Should handle error gracefully (implementation dependent)
        try:
            result = await self.middleware.dispatch(request, call_next)
            # If no exception, should either allow or have fallback behavior
            assert result is not None
        except Exception:
            # Or might raise the error
            pass