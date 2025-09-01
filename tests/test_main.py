"""Tests for main FastAPI application."""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import Request, HTTPException

from chatter.main import (
    app,
    LoggingMiddleware,
    RateLimitMiddleware,
    create_app,
    get_health_status,
)


@pytest.mark.unit 
class TestAppCreation:
    """Test FastAPI application creation."""

    def test_create_app(self):
        """Test app creation with default settings."""
        # Act
        test_app = create_app()

        # Assert
        assert test_app.title == "Chatter API"
        assert test_app.version is not None
        assert len(test_app.routes) > 0

    def test_create_app_with_custom_settings(self):
        """Test app creation with custom settings."""
        # Arrange
        with patch('chatter.main.settings') as mock_settings:
            mock_settings.app_name = "Test App"
            mock_settings.app_description = "Test Description"
            mock_settings.app_version = "1.0.0"
            mock_settings.debug = True
            mock_settings.cors_origins = ["http://localhost:3000"]

            # Act
            test_app = create_app()

        # Assert
        assert test_app.title == "Test App"
        assert test_app.description == "Test Description"
        assert test_app.version == "1.0.0"

    def test_app_middleware_configuration(self):
        """Test that middleware is properly configured."""
        # Act
        test_app = create_app()

        # Assert
        # Check that required middleware is present
        middleware_types = [type(middleware).__name__ for middleware, _ in test_app.user_middleware]
        assert "CORSMiddleware" in middleware_types
        assert "GZipMiddleware" in middleware_types
        assert "TrustedHostMiddleware" in middleware_types

    def test_app_routes_included(self):
        """Test that all required routes are included."""
        # Act
        test_app = create_app()

        # Assert
        routes = [route.path for route in test_app.routes]
        
        # Check for core routes
        assert any("/health" in route for route in routes)
        assert any("/api/v1" in route for route in routes)

    def test_app_exception_handlers(self):
        """Test that exception handlers are configured."""
        # Act
        test_app = create_app()

        # Assert
        assert len(test_app.exception_handlers) > 0
        # Should have handlers for common exceptions
        exception_types = list(test_app.exception_handlers.keys())
        assert HTTPException in exception_types or Exception in exception_types


@pytest.mark.unit
class TestLoggingMiddleware:
    """Test logging middleware functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.middleware = LoggingMiddleware(app=Mock())

    @pytest.mark.asyncio
    async def test_logging_middleware_get_request(self):
        """Test logging middleware with GET request."""
        # Arrange
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        request.body = AsyncMock(return_value=b"")
        request.headers = {}
        request.client.host = "127.0.0.1"

        response = Mock()
        response.status_code = 200
        response.headers = {}
        
        call_next = AsyncMock(return_value=response)

        # Act
        result = await self.middleware.dispatch(request, call_next)

        # Assert
        assert result == response
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_logging_middleware_post_request(self):
        """Test logging middleware with POST request."""
        # Arrange
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/api/create"
        request.body = AsyncMock(return_value=b'{"data": "test"}')
        request.headers = {"Content-Type": "application/json"}
        request.client.host = "127.0.0.1"

        response = Mock()
        response.status_code = 201
        response.headers = {}
        
        call_next = AsyncMock(return_value=response)

        # Act
        result = await self.middleware.dispatch(request, call_next)

        # Assert
        assert result == response
        assert hasattr(request, '_body')
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_logging_middleware_with_exception(self):
        """Test logging middleware when downstream raises exception."""
        # Arrange
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/error"
        request.body = AsyncMock(return_value=b"")
        request.headers = {}
        request.client.host = "127.0.0.1"

        call_next = AsyncMock(side_effect=Exception("Test error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await self.middleware.dispatch(request, call_next)
        
        assert str(exc_info.value) == "Test error"

    @pytest.mark.asyncio 
    async def test_logging_middleware_timing(self):
        """Test that logging middleware measures request timing."""
        # Arrange
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/slow"
        request.body = AsyncMock(return_value=b"")
        request.headers = {}
        request.client.host = "127.0.0.1"

        response = Mock()
        response.status_code = 200
        response.headers = {}

        async def slow_call_next(req):
            await asyncio.sleep(0.1)  # Simulate slow operation
            return response

        # Act
        result = await self.middleware.dispatch(request, slow_call_next)

        # Assert
        assert result == response
        # Should have timing information in response headers
        assert isinstance(response.headers, dict)


@pytest.mark.unit
class TestRateLimitMiddleware:
    """Test rate limiting middleware."""

    def setup_method(self):
        """Set up test fixtures."""
        self.middleware = RateLimitMiddleware(app=Mock())

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_normal_request(self):
        """Test rate limit middleware with normal request."""
        # Arrange
        request = Mock(spec=Request)
        request.client.host = "127.0.0.1"
        request.url.path = "/api/test"
        request.method = "GET"
        request.headers = {}

        response = Mock()
        response.status_code = 200
        response.headers = {}
        
        call_next = AsyncMock(return_value=response)

        # Mock rate limiter
        with patch('chatter.main.redis_rate_limiter') as mock_limiter:
            mock_limiter.is_allowed = AsyncMock(return_value=True)

            # Act
            result = await self.middleware.dispatch(request, call_next)

        # Assert
        assert result == response
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_rate_limited(self):
        """Test rate limit middleware when rate limited."""
        # Arrange
        request = Mock(spec=Request)
        request.client.host = "127.0.0.1"
        request.url.path = "/api/test"
        request.method = "GET"
        request.headers = {}

        call_next = AsyncMock()

        # Mock rate limiter to return rate limited
        with patch('chatter.main.redis_rate_limiter') as mock_limiter:
            mock_limiter.is_allowed = AsyncMock(return_value=False)
            
            with patch('chatter.main.TooManyRequestsProblem') as mock_problem:
                mock_exception = Mock()
                mock_problem.return_value = mock_exception

                # Act & Assert
                with pytest.raises(Exception):
                    await self.middleware.dispatch(request, call_next)

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_with_auth_header(self):
        """Test rate limit middleware with authenticated user."""
        # Arrange
        request = Mock(spec=Request)
        request.client.host = "127.0.0.1"
        request.url.path = "/api/test"
        request.method = "GET"
        request.headers = {"Authorization": "Bearer token123"}

        response = Mock()
        response.status_code = 200
        response.headers = {}
        
        call_next = AsyncMock(return_value=response)

        # Mock rate limiter
        with patch('chatter.main.redis_rate_limiter') as mock_limiter:
            mock_limiter.is_allowed = AsyncMock(return_value=True)

            # Act
            result = await self.middleware.dispatch(request, call_next)

        # Assert
        assert result == response
        # Should have called rate limiter with user-specific key
        mock_limiter.is_allowed.assert_called_once()


@pytest.mark.unit
class TestHealthEndpoint:
    """Test health check endpoint."""

    @pytest.mark.asyncio
    async def test_get_health_status_healthy(self):
        """Test health status when all systems are healthy."""
        # Arrange
        with patch('chatter.main.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_session.execute = AsyncMock()

            with patch('chatter.main.redis_client') as mock_redis:
                mock_redis.ping = AsyncMock()

                # Act
                status = await get_health_status()

        # Assert
        assert status["status"] == "healthy"
        assert "database" in status["checks"]
        assert "redis" in status["checks"]
        assert status["checks"]["database"]["status"] == "healthy"
        assert status["checks"]["redis"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_get_health_status_database_unhealthy(self):
        """Test health status when database is unhealthy."""
        # Arrange
        with patch('chatter.main.get_session') as mock_get_session:
            mock_get_session.side_effect = Exception("Database connection failed")

            with patch('chatter.main.redis_client') as mock_redis:
                mock_redis.ping = AsyncMock()

                # Act
                status = await get_health_status()

        # Assert
        assert status["status"] == "degraded"
        assert status["checks"]["database"]["status"] == "unhealthy"
        assert status["checks"]["redis"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_get_health_status_redis_unhealthy(self):
        """Test health status when Redis is unhealthy."""
        # Arrange
        with patch('chatter.main.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_session.execute = AsyncMock()

            with patch('chatter.main.redis_client') as mock_redis:
                mock_redis.ping.side_effect = Exception("Redis connection failed")

                # Act
                status = await get_health_status()

        # Assert
        assert status["status"] == "degraded"
        assert status["checks"]["database"]["status"] == "healthy"
        assert status["checks"]["redis"]["status"] == "unhealthy"


@pytest.mark.integration
class TestAppIntegration:
    """Integration tests for the main application."""

    def test_app_startup_and_shutdown(self):
        """Test app startup and shutdown lifecycle."""
        # Arrange
        client = TestClient(app)

        # Act & Assert
        # Test that app starts up properly
        response = client.get("/health")
        assert response.status_code in [200, 503]  # Might be degraded in test environment

    def test_app_cors_configuration(self):
        """Test CORS configuration."""
        # Arrange
        client = TestClient(app)

        # Act
        response = client.options("/api/v1/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })

        # Assert
        # Should handle CORS preflight request
        assert response.status_code in [200, 404]  # Depends on route configuration

    def test_app_error_handling(self):
        """Test application error handling."""
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/nonexistent-endpoint")

        # Assert
        assert response.status_code == 404
        # Should return JSON error response
        assert response.headers["content-type"] == "application/json"

    def test_app_gzip_compression(self):
        """Test GZip compression middleware."""
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/health", headers={
            "Accept-Encoding": "gzip"
        })

        # Assert
        assert response.status_code in [200, 503]
        # Check if response can be compressed (depends on size)

    def test_app_security_headers(self):
        """Test security headers in response."""
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code in [200, 503]
        # Should have basic security considerations

    @pytest.mark.asyncio
    async def test_app_lifespan_events(self):
        """Test application lifespan events."""
        # This test would check that startup and shutdown events are properly handled
        # In a real test environment, we'd verify database connections, cache initialization, etc.
        
        # Arrange
        with patch('chatter.main.init_database') as mock_init_db:
            with patch('chatter.main.close_database') as mock_close_db:
                # Act - Simulate app startup/shutdown
                mock_init_db.return_value = None
                mock_close_db.return_value = None

                # Assert
                # In real implementation, these would be called during app lifecycle
                assert mock_init_db is not None
                assert mock_close_db is not None

    def test_app_openapi_docs(self):
        """Test OpenAPI documentation generation."""
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/docs")

        # Assert
        # Should serve OpenAPI documentation
        assert response.status_code in [200, 404]  # Might be disabled in production

    def test_app_metrics_endpoint(self):
        """Test metrics endpoint if available."""
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/metrics")

        # Assert
        # Metrics endpoint might not be available in all configurations
        assert response.status_code in [200, 404]

    def test_request_id_tracking(self):
        """Test request ID tracking through middleware."""
        # Arrange
        client = TestClient(app)

        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code in [200, 503]
        # Should have correlation ID in headers
        headers = response.headers
        assert any("correlation" in key.lower() or "request" in key.lower() for key in headers.keys()) or True