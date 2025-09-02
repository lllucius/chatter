"""Tests for rate limiting middleware and utilities."""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import Response

from chatter.utils.rate_limit import (
    MemoryRateLimiter,
    RateLimiter,
    RateLimitExceeded,
    RateLimitMiddleware,
    RedisRateLimiter,
    create_rate_limit_key,
    get_client_ip,
)


@pytest.mark.unit
class TestRateLimitMiddleware:
    """Test RateLimitMiddleware functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = MagicMock()
        self.middleware = RateLimitMiddleware(
            self.app, requests_per_minute=2, requests_per_hour=10
        )

    @pytest.mark.asyncio
    async def test_middleware_initialization(self):
        """Test middleware initialization."""
        # Assert
        assert self.middleware.requests_per_minute == 2
        assert self.middleware.requests_per_hour == 10
        assert self.middleware.request_history == {}

    @pytest.mark.asyncio
    async def test_skip_health_check_endpoints(self):
        """Test that health check endpoints are skipped."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/healthz"

        mock_response = MagicMock(spec=Response)

        async def mock_call_next(request):
            return mock_response

        # Act
        response = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert response is mock_response
        assert self.middleware.request_history == {}

    @pytest.mark.asyncio
    async def test_rate_limit_within_limits(self):
        """Test request within rate limits."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        # Act
        response = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert response is mock_response
        assert "X-RateLimit-Limit-Minute" in response.headers
        assert response.headers["X-RateLimit-Limit-Minute"] == "2"
        assert "X-RateLimit-Remaining-Minute" in response.headers

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Test request exceeding rate limits."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}

        # Pre-populate request history to exceed limit
        client_id = "127.0.0.1"
        current_time = time.time()
        self.middleware.request_history[client_id] = [
            current_time - 10,  # Within minute window
            current_time - 5,  # Within minute window
        ]

        async def mock_call_next(request):
            return MagicMock(spec=Response)

        # Act
        response = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 429
        assert "Retry-After" in response.headers

    @pytest.mark.asyncio
    async def test_client_identification_with_auth_header(self):
        """Test client identification using authorization header."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"authorization": "Bearer test-token"}

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        # Act
        response = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert - Should use hashed auth token as client ID
        assert response is mock_response
        # Verify a client ID was created (can't predict exact hash)
        assert len(self.middleware.request_history) == 1

    @pytest.mark.asyncio
    async def test_client_identification_with_forwarded_for(self):
        """Test client identification using X-Forwarded-For header."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {
            "x-forwarded-for": "192.168.1.1, 10.0.0.1"
        }

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        # Act
        response = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert response is mock_response
        # Should use first IP from X-Forwarded-For
        assert "192.168.1.1" in self.middleware.request_history

    @pytest.mark.asyncio
    async def test_client_identification_no_client(self):
        """Test client identification when no client info available."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        mock_request.client = None
        mock_request.headers = {}

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        # Act
        response = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert response is mock_response
        assert "unknown" in self.middleware.request_history


@pytest.mark.unit
class TestRateLimitFunctions:
    """Test rate limiting utility functions."""

    def test_get_client_ip_basic(self):
        """Test basic client IP extraction."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}

        # Act
        client_ip = get_client_ip(mock_request)

        # Assert
        assert client_ip == "127.0.0.1"

    def test_get_client_ip_no_client(self):
        """Test client IP extraction when no client."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.client = None
        mock_request.headers = {}

        # Act
        client_ip = get_client_ip(mock_request)

        # Assert
        assert client_ip == "unknown"

    def test_get_client_ip_forwarded_for(self):
        """Test client IP extraction with X-Forwarded-For header."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.items.return_value = [
            ("x-forwarded-for", "192.168.1.1, 10.0.0.1")
        ]

        # Act
        client_ip = get_client_ip(mock_request)

        # Assert
        assert client_ip == "192.168.1.1"

    def test_get_client_ip_real_ip(self):
        """Test client IP extraction with X-Real-IP header."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.items.return_value = [
            ("x-real-ip", "192.168.1.2")
        ]

        # Act
        client_ip = get_client_ip(mock_request)

        # Assert
        assert client_ip == "192.168.1.2"

    def test_get_client_ip_forwarded_header(self):
        """Test client IP extraction with Forwarded header."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.items.return_value = [
            ("forwarded", 'for="192.168.1.3";proto=https')
        ]

        # Act
        client_ip = get_client_ip(mock_request)

        # Assert
        assert client_ip == "192.168.1.3"

    def test_get_client_ip_header_priority(self):
        """Test that X-Forwarded-For takes priority over other headers."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.items.return_value = [
            ("x-forwarded-for", "192.168.1.1"),
            ("x-real-ip", "192.168.1.2"),
            ("forwarded", 'for="192.168.1.3"'),
        ]

        # Act
        client_ip = get_client_ip(mock_request)

        # Assert
        assert client_ip == "192.168.1.1"

    def test_create_rate_limit_key_basic(self):
        """Test basic rate limit key creation."""
        # Act
        key = create_rate_limit_key("127.0.0.1", "/api/test")

        # Assert
        assert key == "rate_limit:ip:127.0.0.1:/api/test"

    def test_create_rate_limit_key_with_user(self):
        """Test rate limit key creation with user ID."""
        # Act
        key = create_rate_limit_key(
            "127.0.0.1", "/api/test", user_id="user123"
        )

        # Assert
        assert key == "rate_limit:user:user123:ip:127.0.0.1:/api/test"

    def test_create_rate_limit_key_custom_prefix(self):
        """Test rate limit key creation with custom prefix."""
        # Act
        key = create_rate_limit_key(
            "127.0.0.1", "/api/test", prefix="custom"
        )

        # Assert
        assert key == "custom:ip:127.0.0.1:/api/test"

    def test_create_rate_limit_key_path_normalization(self):
        """Test that paths are normalized in keys."""
        # Act
        key1 = create_rate_limit_key("127.0.0.1", "/API/Test/")
        key2 = create_rate_limit_key("127.0.0.1", "/api/test")

        # Assert
        assert key1 == key2 == "rate_limit:ip:127.0.0.1:/api/test"


@pytest.mark.unit
class TestMemoryRateLimiter:
    """Test MemoryRateLimiter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.limiter = MemoryRateLimiter()

    @pytest.mark.asyncio
    async def test_first_request_allowed(self):
        """Test that first request is always allowed."""
        # Act
        allowed = await self.limiter.is_allowed("test_key", 5, 60)

        # Assert
        assert allowed is True

    @pytest.mark.asyncio
    async def test_within_limit_allowed(self):
        """Test requests within limit are allowed."""
        # Act
        allowed1 = await self.limiter.is_allowed("test_key", 3, 60)
        allowed2 = await self.limiter.is_allowed("test_key", 3, 60)
        allowed3 = await self.limiter.is_allowed("test_key", 3, 60)

        # Assert
        assert allowed1 is True
        assert allowed2 is True
        assert allowed3 is True

    @pytest.mark.asyncio
    async def test_exceeding_limit_denied(self):
        """Test that requests exceeding limit are denied."""
        # Arrange - exhaust the limit
        for _ in range(3):
            await self.limiter.is_allowed("test_key", 3, 60)

        # Act
        allowed = await self.limiter.is_allowed("test_key", 3, 60)

        # Assert
        assert allowed is False

    @pytest.mark.asyncio
    async def test_get_remaining_new_key(self):
        """Test getting remaining count for new key."""
        # Act
        remaining = await self.limiter.get_remaining("new_key", 5, 60)

        # Assert
        assert remaining == 5

    @pytest.mark.asyncio
    async def test_get_remaining_after_requests(self):
        """Test getting remaining count after some requests."""
        # Arrange
        await self.limiter.is_allowed("test_key", 5, 60)
        await self.limiter.is_allowed("test_key", 5, 60)

        # Act
        remaining = await self.limiter.get_remaining("test_key", 5, 60)

        # Assert
        assert remaining == 3

    @pytest.mark.asyncio
    async def test_window_expiry(self):
        """Test that old requests expire outside the window."""
        # Arrange - simulate old request
        old_time = time.time() - 120  # 2 minutes ago
        self.limiter.requests["test_key"] = [old_time]

        # Act
        allowed = await self.limiter.is_allowed(
            "test_key", 1, 60
        )  # 1 minute window

        # Assert
        assert allowed is True  # Old request should be expired


@pytest.mark.unit
class TestRedisRateLimiter:
    """Test RedisRateLimiter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_redis = AsyncMock()
        self.limiter = RedisRateLimiter(self.mock_redis)

    @pytest.mark.asyncio
    async def test_is_allowed_under_limit(self):
        """Test allowing request under limit."""
        # Arrange
        mock_pipeline = AsyncMock()
        self.mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [
            None,
            2,
            None,
            None,
        ]  # Current count is 2

        # Act
        allowed = await self.limiter.is_allowed("test_key", 5, 60)

        # Assert
        assert allowed is True
        mock_pipeline.zremrangebyscore.assert_called_once()
        mock_pipeline.zcard.assert_called_once()
        mock_pipeline.zadd.assert_called_once()
        mock_pipeline.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_allowed_at_limit(self):
        """Test denying request at limit."""
        # Arrange
        mock_pipeline = AsyncMock()
        self.mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [
            None,
            5,
            None,
            None,
        ]  # Current count is 5

        # Act
        allowed = await self.limiter.is_allowed("test_key", 5, 60)

        # Assert
        assert allowed is False

    @pytest.mark.asyncio
    async def test_get_remaining_count(self):
        """Test getting remaining request count."""
        # Arrange
        self.mock_redis.zcard.return_value = 3

        # Act
        remaining = await self.limiter.get_remaining("test_key", 5, 60)

        # Assert
        assert remaining == 2
        self.mock_redis.zremrangebyscore.assert_called_once()
        self.mock_redis.zcard.assert_called_once()


@pytest.mark.unit
class TestRateLimitExceptions:
    """Test rate limit exception classes."""

    def test_rate_limit_exceeded_basic(self):
        """Test basic RateLimitExceeded exception."""
        # Act
        exception = RateLimitExceeded()

        # Assert
        assert str(exception) == "Rate limit exceeded"
        assert exception.limit is None
        assert exception.window is None
        assert exception.retry_after is None

    def test_rate_limit_exceeded_with_details(self):
        """Test RateLimitExceeded exception with details."""
        # Act
        exception = RateLimitExceeded(
            message="Custom message",
            limit=100,
            window=60,
            retry_after=30,
        )

        # Assert
        assert str(exception) == "Custom message"
        assert exception.limit == 100
        assert exception.window == 60
        assert exception.retry_after == 30

    @pytest.mark.asyncio
    async def test_rate_limiter_abstract_methods(self):
        """Test that abstract RateLimiter methods raise NotImplementedError."""
        # Arrange
        limiter = RateLimiter()

        # Act & Assert
        with pytest.raises(NotImplementedError):
            await limiter.is_allowed("key", 10, 60)

        with pytest.raises(NotImplementedError):
            await limiter.get_remaining("key", 10, 60)


@pytest.mark.integration
class TestRateLimitIntegration:
    """Integration tests for rate limiting system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = MagicMock()
        self.middleware = RateLimitMiddleware(
            self.app, requests_per_minute=3, requests_per_hour=10
        )

    @pytest.mark.asyncio
    async def test_rate_limit_headers_progression(self):
        """Test that rate limit headers correctly track progression."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        # Act - Make multiple requests
        response1 = await self.middleware.dispatch(
            mock_request, mock_call_next
        )
        response2 = await self.middleware.dispatch(
            mock_request, mock_call_next
        )
        response3 = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert response1.headers["X-RateLimit-Remaining-Minute"] == "2"
        assert response2.headers["X-RateLimit-Remaining-Minute"] == "1"
        assert response3.headers["X-RateLimit-Remaining-Minute"] == "0"

    @pytest.mark.asyncio
    async def test_rate_limit_reset_headers(self):
        """Test that reset headers are correctly calculated."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        # Act
        response = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert "X-RateLimit-Reset-Minute" in response.headers
        assert "X-RateLimit-Reset-Hour" in response.headers
        # Reset times should be integers
        minute_reset = int(response.headers["X-RateLimit-Reset-Minute"])
        hour_reset = int(response.headers["X-RateLimit-Reset-Hour"])
        current_time = int(time.time())
        assert minute_reset > current_time
        assert hour_reset > current_time
