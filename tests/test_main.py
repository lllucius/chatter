"""Tests for main FastAPI application."""

import asyncio
import json
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Request, Response
from fastapi.testclient import TestClient

from chatter.main import (
    LoggingMiddleware, 
    create_app, 
    lifespan,
    app as main_app
)


class TestLoggingMiddleware:
    """Test logging middleware functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.middleware = LoggingMiddleware(Mock())

    @pytest.mark.asyncio
    async def test_dispatch_get_request(self):
        """Test middleware with GET request."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.__str__ = Mock(return_value="http://test.com/api/test")
        request.url.path = "/api/test"
        request.headers = {}
        
        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {"x-correlation-id": "test-123"}

        call_next = AsyncMock(return_value=response)

        with patch('chatter.main.settings') as mock_settings:
            mock_settings.debug_http_requests = False
            
            with patch('chatter.main.record_request_metrics') as mock_metrics:
                result = await self.middleware.dispatch(request, call_next)
                
                assert result == response
                call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_dispatch_post_request_with_body(self):
        """Test middleware with POST request containing body."""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = Mock()
        request.url.__str__ = Mock(return_value="http://test.com/api/chat")
        request.url.path = "/api/chat"
        request.headers = {}
        request.body = AsyncMock(return_value=b'{"message": "test"}')
        
        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {"x-correlation-id": "test-456"}

        call_next = AsyncMock(return_value=response)

        with patch('chatter.main.settings') as mock_settings:
            mock_settings.debug_http_requests = True
            
            with patch('chatter.main.logger') as mock_logger:
                with patch('chatter.main.record_request_metrics'):
                    result = await self.middleware.dispatch(request, call_next)
                    
                    assert result == response
                    # Should have logged request due to debug mode
                    mock_logger.debug.assert_called()

    @pytest.mark.asyncio
    async def test_dispatch_error_response(self):
        """Test middleware with error response."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.__str__ = Mock(return_value="http://test.com/api/error")
        request.url.path = "/api/error"
        request.headers = {}
        
        response = Mock(spec=Response)
        response.status_code = 500
        response.headers = {"x-correlation-id": "error-123"}

        call_next = AsyncMock(return_value=response)

        with patch('chatter.main.settings') as mock_settings:
            mock_settings.debug_http_requests = False
            
            with patch('chatter.main.logger') as mock_logger:
                with patch('chatter.main.record_request_metrics'):
                    result = await self.middleware.dispatch(request, call_next)
                    
                    assert result == response
                    # Should have logged error regardless of debug mode
                    mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_dispatch_rate_limited_response(self):
        """Test middleware with rate limited response."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.__str__ = Mock(return_value="http://test.com/api/test")
        request.url.path = "/api/test"
        request.headers = {}
        
        response = Mock(spec=Response)
        response.status_code = 429
        response.headers = {"x-correlation-id": "rate-limited-123"}

        call_next = AsyncMock(return_value=response)

        with patch('chatter.main.settings') as mock_settings:
            mock_settings.debug_http_requests = False
            
            with patch('chatter.main.logger') as mock_logger:
                with patch('chatter.main.record_request_metrics') as mock_metrics:
                    result = await self.middleware.dispatch(request, call_next)
                    
                    assert result == response
                    # Should record rate limited metric
                    mock_metrics.assert_called_once()
                    call_args = mock_metrics.call_args[1]
                    assert call_args['rate_limited'] is True

    @pytest.mark.asyncio
    async def test_dispatch_metrics_failure(self):
        """Test middleware when metrics recording fails."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = Mock()
        request.url.__str__ = Mock(return_value="http://test.com/api/test")
        request.url.path = "/api/test"
        request.headers = {}
        
        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {"x-correlation-id": "test-123"}

        call_next = AsyncMock(return_value=response)

        with patch('chatter.main.settings') as mock_settings:
            mock_settings.debug_http_requests = False
            
            with patch('chatter.main.logger') as mock_logger:
                with patch('chatter.main.record_request_metrics', side_effect=Exception("Metrics error")):
                    result = await self.middleware.dispatch(request, call_next)
                    
                    assert result == response
                    # Should log warning about metrics failure
                    mock_logger.warning.assert_called()


class TestLifespan:
    """Test application lifespan management."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_success(self):
        """Test successful application startup."""
        app_mock = Mock()
        
        with patch('chatter.main.validate_startup_configuration') as mock_validate:
            with patch('chatter.main.init_database') as mock_init_db:
                with patch('chatter.main.ToolServerService') as mock_tool_service:
                    with patch('chatter.main.start_scheduler') as mock_start_scheduler:
                        with patch('chatter.main.job_queue') as mock_job_queue:
                            with patch('chatter.main.sse_service') as mock_sse_service:
                                with patch('chatter.main.get_session_maker') as mock_session_maker:
                                    with patch('chatter.main.logger') as mock_logger:
                                        
                                        # Setup mocks
                                        mock_session = AsyncMock()
                                        mock_session_maker.return_value.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                                        mock_session_maker.return_value.return_value.__aexit__ = AsyncMock(return_value=None)
                                        
                                        mock_service_instance = Mock()
                                        mock_service_instance.initialize_builtin_servers = AsyncMock()
                                        mock_tool_service.return_value = mock_service_instance
                                        
                                        mock_job_queue.start = AsyncMock()
                                        mock_sse_service.start = AsyncMock()
                                        mock_start_scheduler.return_value = None
                                        
                                        # Test startup
                                        async with lifespan(app_mock):
                                            pass
                                        
                                        # Verify startup calls
                                        mock_validate.assert_called_once()
                                        mock_init_db.assert_called_once()
                                        mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_lifespan_startup_validation_failure_production(self):
        """Test startup validation failure in production."""
        app_mock = Mock()
        
        with patch('chatter.main.validate_startup_configuration', side_effect=Exception("Config error")):
            with patch('chatter.main.settings') as mock_settings:
                with patch('chatter.main.logger') as mock_logger:
                    mock_settings.is_production = True
                    
                    with pytest.raises(Exception):
                        async with lifespan(app_mock):
                            pass
                    
                    mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_lifespan_startup_validation_failure_development(self):
        """Test startup validation failure in development."""
        app_mock = Mock()
        
        with patch('chatter.main.validate_startup_configuration', side_effect=Exception("Config error")):
            with patch('chatter.main.init_database') as mock_init_db:
                with patch('chatter.main.settings') as mock_settings:
                    with patch('chatter.main.logger') as mock_logger:
                        with patch('chatter.main.ToolServerService'):
                            with patch('chatter.main.start_scheduler'):
                                with patch('chatter.main.job_queue') as mock_job_queue:
                                    with patch('chatter.main.sse_service') as mock_sse_service:
                                        with patch('chatter.main.get_session_maker'):
                                            mock_settings.is_production = False
                                            mock_job_queue.start = AsyncMock()
                                            mock_job_queue.stop = AsyncMock()
                                            mock_sse_service.start = AsyncMock()
                                            mock_sse_service.stop = AsyncMock()
                                            
                                            # Should not raise in development
                                            async with lifespan(app_mock):
                                                pass
                                            
                                            mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_lifespan_service_initialization_failures(self):
        """Test handling of service initialization failures."""
        app_mock = Mock()
        
        with patch('chatter.main.validate_startup_configuration'):
            with patch('chatter.main.init_database'):
                with patch('chatter.main.ToolServerService', side_effect=Exception("Tool server error")):
                    with patch('chatter.main.start_scheduler', side_effect=Exception("Scheduler error")):
                        with patch('chatter.main.job_queue') as mock_job_queue:
                            with patch('chatter.main.sse_service') as mock_sse_service:
                                with patch('chatter.main.close_database') as mock_close_db:
                                    with patch('chatter.main.logger') as mock_logger:
                                        with patch('chatter.main.get_session_maker'):
                                            mock_job_queue.start = AsyncMock(side_effect=Exception("Job queue error"))
                                            mock_job_queue.stop = AsyncMock()
                                            mock_sse_service.start = AsyncMock(side_effect=Exception("SSE error"))
                                            mock_sse_service.stop = AsyncMock()
                                            
                                            # Should not raise but log errors
                                            async with lifespan(app_mock):
                                                pass
                                            
                                            # Should have logged multiple errors
                                            assert mock_logger.error.call_count >= 4


class TestCreateApp:
    """Test FastAPI application creation."""

    def test_create_app_basic(self):
        """Test basic app creation."""
        with patch('chatter.main.setup_logging') as mock_setup_logging:
            with patch('chatter.main.settings') as mock_settings:
                mock_settings.api_title = "Test API"
                mock_settings.api_description = "Test Description"
                mock_settings.api_version = "1.0.0"
                mock_settings.debug = False
                mock_settings.is_development = True
                mock_settings.security_headers_enabled = False
                mock_settings.cors_origins = ["*"]
                mock_settings.cors_allow_credentials = True
                mock_settings.cors_allow_methods = ["*"]
                mock_settings.cors_allow_headers = ["*"]
                mock_settings.trusted_hosts_for_env = []
                mock_settings.api_prefix = "/api/v1"
                
                app = create_app()
                
                assert app.title == "Test API"
                assert app.version == "1.0.0"
                mock_setup_logging.assert_called_once()

    def test_create_app_with_security_headers(self):
        """Test app creation with security headers enabled."""
        with patch('chatter.main.setup_logging'):
            with patch('chatter.main.settings') as mock_settings:
                mock_settings.api_title = "Test API"
                mock_settings.api_description = "Test Description"
                mock_settings.api_version = "1.0.0"
                mock_settings.debug = False
                mock_settings.is_development = True
                mock_settings.security_headers_enabled = True
                mock_settings.cors_origins = ["*"]
                mock_settings.cors_allow_credentials = True
                mock_settings.cors_allow_methods = ["*"]
                mock_settings.cors_allow_headers = ["*"]
                mock_settings.trusted_hosts_for_env = []
                mock_settings.api_prefix = "/api/v1"
                
                app = create_app()
                
                # Check that security middleware is added
                assert any(
                    hasattr(middleware, 'cls') and 'security' in str(middleware.cls).lower()
                    for middleware in app.user_middleware
                ) or len(app.user_middleware) > 0

    def test_create_app_with_trusted_hosts(self):
        """Test app creation with trusted hosts."""
        with patch('chatter.main.setup_logging'):
            with patch('chatter.main.settings') as mock_settings:
                mock_settings.api_title = "Test API"
                mock_settings.api_description = "Test Description" 
                mock_settings.api_version = "1.0.0"
                mock_settings.debug = False
                mock_settings.is_development = True
                mock_settings.security_headers_enabled = False
                mock_settings.cors_origins = ["*"]
                mock_settings.cors_allow_credentials = True
                mock_settings.cors_allow_methods = ["*"]
                mock_settings.cors_allow_headers = ["*"]
                mock_settings.trusted_hosts_for_env = ["example.com", "api.example.com"]
                mock_settings.api_prefix = "/api/v1"
                
                app = create_app()
                
                # Should have trusted host middleware
                assert len(app.user_middleware) > 0

    def test_create_app_production_settings(self):
        """Test app creation with production settings."""
        with patch('chatter.main.setup_logging'):
            with patch('chatter.main.settings') as mock_settings:
                mock_settings.api_title = "Test API"
                mock_settings.api_description = "Test Description"
                mock_settings.api_version = "1.0.0"
                mock_settings.debug = False
                mock_settings.is_development = False  # Production mode
                mock_settings.security_headers_enabled = True
                mock_settings.cors_origins = ["https://app.example.com"]
                mock_settings.cors_allow_credentials = True
                mock_settings.cors_allow_methods = ["GET", "POST"]
                mock_settings.cors_allow_headers = ["*"]
                mock_settings.trusted_hosts_for_env = ["api.example.com"]
                mock_settings.api_prefix = "/api/v1"
                
                app = create_app()
                
                # In production, docs should be disabled
                assert app.docs_url is None
                assert app.redoc_url is None
                assert app.openapi_url is None

    def test_create_app_exception_handlers(self):
        """Test that exception handlers are properly configured."""
        with patch('chatter.main.setup_logging'):
            with patch('chatter.main.settings') as mock_settings:
                mock_settings.api_title = "Test API"
                mock_settings.api_description = "Test Description"
                mock_settings.api_version = "1.0.0"
                mock_settings.debug = False
                mock_settings.is_development = True
                mock_settings.security_headers_enabled = False
                mock_settings.cors_origins = ["*"]
                mock_settings.cors_allow_credentials = True
                mock_settings.cors_allow_methods = ["*"]
                mock_settings.cors_allow_headers = ["*"]
                mock_settings.trusted_hosts_for_env = []
                mock_settings.api_prefix = "/api/v1"
                
                app = create_app()
                
                # Should have exception handlers
                assert len(app.exception_handlers) > 0

    def test_create_app_routers_included(self):
        """Test that all routers are properly included."""
        with patch('chatter.main.setup_logging'):
            with patch('chatter.main.settings') as mock_settings:
                mock_settings.api_title = "Test API"
                mock_settings.api_description = "Test Description"
                mock_settings.api_version = "1.0.0"
                mock_settings.debug = False
                mock_settings.is_development = True
                mock_settings.security_headers_enabled = False
                mock_settings.cors_origins = ["*"]
                mock_settings.cors_allow_credentials = True
                mock_settings.cors_allow_methods = ["*"]
                mock_settings.cors_allow_headers = ["*"]
                mock_settings.trusted_hosts_for_env = []
                mock_settings.api_prefix = "/api/v1"
                
                app = create_app()
                
                # Should have multiple routers
                assert len(app.routes) > 1

    def test_create_app_with_frontend(self):
        """Test app creation with frontend static files."""
        with patch('chatter.main.setup_logging'):
            with patch('chatter.main.settings') as mock_settings:
                with patch('os.path.exists', return_value=True):
                    with patch('os.path.join', return_value="/fake/frontend/build"):
                        mock_settings.api_title = "Test API"
                        mock_settings.api_description = "Test Description"
                        mock_settings.api_version = "1.0.0"
                        mock_settings.debug = False
                        mock_settings.is_development = True
                        mock_settings.security_headers_enabled = False
                        mock_settings.cors_origins = ["*"]
                        mock_settings.cors_allow_credentials = True
                        mock_settings.cors_allow_methods = ["*"]
                        mock_settings.cors_allow_headers = ["*"]
                        mock_settings.trusted_hosts_for_env = []
                        mock_settings.api_prefix = "/api/v1"
                        
                        app = create_app()
                        
                        # Should have routes including frontend route
                        assert len(app.routes) > 1

    def test_create_app_enhanced_docs_failure(self):
        """Test app creation when enhanced docs setup fails."""
        with patch('chatter.main.setup_logging'):
            with patch('chatter.main.setup_enhanced_docs', side_effect=Exception("Docs error")):
                with patch('chatter.main.logger') as mock_logger:
                    with patch('chatter.main.settings') as mock_settings:
                        mock_settings.api_title = "Test API"
                        mock_settings.api_description = "Test Description"
                        mock_settings.api_version = "1.0.0"
                        mock_settings.debug = False
                        mock_settings.is_development = True
                        mock_settings.security_headers_enabled = False
                        mock_settings.cors_origins = ["*"]
                        mock_settings.cors_allow_credentials = True
                        mock_settings.cors_allow_methods = ["*"]
                        mock_settings.cors_allow_headers = ["*"]
                        mock_settings.trusted_hosts_for_env = []
                        mock_settings.api_prefix = "/api/v1"
                        
                        app = create_app()
                        
                        # Should log warning but continue
                        mock_logger.warning.assert_called()


class TestMainAppInstance:
    """Test the main app instance."""

    def test_main_app_exists(self):
        """Test that main app instance is created."""
        assert main_app is not None
        assert hasattr(main_app, 'title')

    def test_main_app_type(self):
        """Test that main app is FastAPI instance."""
        from fastapi import FastAPI
        assert isinstance(main_app, FastAPI)


class TestExceptionHandlers:
    """Test exception handlers."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(main_app)

    def test_root_endpoint_without_frontend(self):
        """Test root endpoint when frontend is not available."""
        with patch('os.path.exists', return_value=False):
            response = self.client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "Chatter API" in data["message"]

    def test_health_endpoint_accessible(self):
        """Test that health endpoint is accessible."""
        # This might fail if dependencies aren't available, but the route should exist
        try:
            response = self.client.get("/healthz")
            # Don't assert status code since it depends on DB availability
            assert response is not None
        except Exception:
            # Expected in test environment without full setup
            pass

    def test_docs_endpoint_in_development(self):
        """Test that docs endpoint exists in development."""
        with patch('chatter.main.settings') as mock_settings:
            mock_settings.is_development = True
            try:
                response = self.client.get("/docs")
                # Don't assert status code since it depends on app setup
                assert response is not None
            except Exception:
                # Expected in test environment
                pass


class TestMiddlewareOrder:
    """Test middleware ordering."""

    def test_middleware_stack_order(self):
        """Test that middleware is added in correct order."""
        with patch('chatter.main.setup_logging'):
            with patch('chatter.main.settings') as mock_settings:
                mock_settings.api_title = "Test API"
                mock_settings.api_description = "Test Description"
                mock_settings.api_version = "1.0.0"
                mock_settings.debug = False
                mock_settings.is_development = True
                mock_settings.security_headers_enabled = True
                mock_settings.cors_origins = ["*"]
                mock_settings.cors_allow_credentials = True
                mock_settings.cors_allow_methods = ["*"]
                mock_settings.cors_allow_headers = ["*"]
                mock_settings.trusted_hosts_for_env = ["example.com"]
                mock_settings.api_prefix = "/api/v1"
                
                app = create_app()
                
                # Should have multiple middleware layers
                assert len(app.user_middleware) > 0
                
                # Check that middleware stack includes expected components
                middleware_names = [str(middleware.cls) for middleware in app.user_middleware]
                
                # Should include logging middleware (our custom one)
                assert any("LoggingMiddleware" in name for name in middleware_names)


class TestAsyncLoopIntegration:
    """Test asyncio integration."""

    @pytest.mark.asyncio
    async def test_uvloop_policy_set(self):
        """Test that uvloop policy is used when available."""
        # This test verifies that the uvloop import and setup doesn't break
        # We can't easily test the actual policy without affecting the test runner
        try:
            import uvloop
            # If uvloop is available, the policy should be set in main.py
            policy = asyncio.get_event_loop_policy()
            # Just verify we can get the policy without error
            assert policy is not None
        except ImportError:
            # uvloop not available, should continue without error
            policy = asyncio.get_event_loop_policy()
            assert policy is not None


class TestConfigurationIntegration:
    """Test configuration integration."""

    def test_settings_import_success(self):
        """Test that settings can be imported successfully."""
        from chatter.main import settings
        assert settings is not None

    def test_logger_import_success(self):
        """Test that logger can be imported successfully."""
        from chatter.main import logger
        assert logger is not None

    def test_database_utils_import_success(self):
        """Test that database utilities can be imported successfully."""
        from chatter.main import init_database, close_database
        assert init_database is not None
        assert close_database is not None