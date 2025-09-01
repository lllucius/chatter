"""Tests for correlation utility functions."""

import uuid
from unittest.mock import Mock, patch

import pytest
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from chatter.utils.correlation import (
    CorrelationIdMiddleware,
    get_correlation_id,
    set_correlation_id,
)


class TestCorrelationId:
    """Test correlation ID functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear any existing correlation ID
        import contextvars
        try:
            correlation_id_var = contextvars.ContextVar('correlation_id')
            correlation_id_var.delete()
        except LookupError:
            pass

    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        test_id = "test-correlation-123"
        
        set_correlation_id(test_id)
        retrieved_id = get_correlation_id()
        
        assert retrieved_id == test_id

    def test_get_correlation_id_when_not_set(self):
        """Test getting correlation ID when not set."""
        # Should return None when not set
        correlation_id = get_correlation_id()
        assert correlation_id is None

    def test_set_correlation_id_overwrites_existing(self):
        """Test that setting correlation ID overwrites existing value."""
        first_id = "first-id"
        second_id = "second-id"
        
        set_correlation_id(first_id)
        assert get_correlation_id() == first_id
        
        set_correlation_id(second_id)
        assert get_correlation_id() == second_id

    def test_correlation_id_context_isolation(self):
        """Test that correlation IDs are isolated between contexts."""
        import asyncio
        import contextvars
        
        async def task_with_id(task_id: str, results: list):
            """Task that sets its own correlation ID."""
            set_correlation_id(f"task-{task_id}")
            await asyncio.sleep(0.01)  # Allow context switching
            results.append(get_correlation_id())
        
        async def test_isolation():
            results = []
            
            # Run multiple tasks concurrently
            await asyncio.gather(
                task_with_id("1", results),
                task_with_id("2", results),
                task_with_id("3", results)
            )
            
            # Each task should have its own correlation ID
            assert len(results) == 3
            assert "task-1" in results
            assert "task-2" in results
            assert "task-3" in results
        
        asyncio.run(test_isolation())


class TestCorrelationIdMiddleware:
    """Test correlation ID middleware."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = Mock()
        self.middleware = CorrelationIdMiddleware(self.app)

    @pytest.mark.asyncio
    async def test_middleware_with_existing_correlation_id(self):
        """Test middleware when request already has correlation ID."""
        # Mock request with existing correlation ID header
        request = Mock(spec=Request)
        request.headers = {"X-Correlation-ID": "existing-id-123"}
        
        # Mock response
        response = Mock(spec=Response)
        response.headers = {}
        
        # Mock call_next
        async def mock_call_next(req):
            # Simulate handler that might use correlation ID
            correlation_id = get_correlation_id()
            assert correlation_id == "existing-id-123"
            return response
        
        result = await self.middleware.dispatch(request, mock_call_next)
        
        # Should return response with correlation ID header
        assert result == response
        assert response.headers["X-Correlation-ID"] == "existing-id-123"

    @pytest.mark.asyncio
    async def test_middleware_without_correlation_id(self):
        """Test middleware when request doesn't have correlation ID."""
        # Mock request without correlation ID header
        request = Mock(spec=Request)
        request.headers = {}
        
        # Mock response
        response = Mock(spec=Response)
        response.headers = {}
        
        # Mock call_next
        async def mock_call_next(req):
            # Correlation ID should be generated
            correlation_id = get_correlation_id()
            assert correlation_id is not None
            assert len(correlation_id) > 0
            return response
        
        result = await self.middleware.dispatch(request, mock_call_next)
        
        # Should return response with generated correlation ID header
        assert result == response
        assert "X-Correlation-ID" in response.headers
        correlation_id = response.headers["X-Correlation-ID"]
        assert len(correlation_id) > 0

    @pytest.mark.asyncio
    async def test_middleware_generates_valid_uuid(self):
        """Test that middleware generates valid UUID format."""
        request = Mock(spec=Request)
        request.headers = {}
        
        response = Mock(spec=Response)
        response.headers = {}
        
        async def mock_call_next(req):
            correlation_id = get_correlation_id()
            # Should be a valid UUID format
            try:
                uuid.UUID(correlation_id)
            except ValueError:
                pytest.fail(f"Generated correlation ID is not valid UUID: {correlation_id}")
            return response
        
        await self.middleware.dispatch(request, mock_call_next)

    @pytest.mark.asyncio
    async def test_middleware_case_insensitive_header(self):
        """Test middleware handles case-insensitive header names."""
        # Test different case variations
        test_cases = [
            "x-correlation-id",
            "X-CORRELATION-ID", 
            "X-Correlation-Id",
            "x-Correlation-ID"
        ]
        
        for header_name in test_cases:
            request = Mock(spec=Request)
            request.headers = {header_name: "test-id-case"}
            
            response = Mock(spec=Response)
            response.headers = {}
            
            async def mock_call_next(req):
                correlation_id = get_correlation_id()
                assert correlation_id == "test-id-case"
                return response
            
            result = await self.middleware.dispatch(request, mock_call_next)
            assert response.headers["X-Correlation-ID"] == "test-id-case"

    @pytest.mark.asyncio
    async def test_middleware_preserves_existing_response_headers(self):
        """Test that middleware preserves existing response headers."""
        request = Mock(spec=Request)
        request.headers = {"X-Correlation-ID": "preserve-test"}
        
        response = Mock(spec=Response)
        response.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        
        async def mock_call_next(req):
            return response
        
        result = await self.middleware.dispatch(request, mock_call_next)
        
        # Should preserve existing headers and add correlation ID
        assert response.headers["Content-Type"] == "application/json"
        assert response.headers["Cache-Control"] == "no-cache"
        assert response.headers["X-Correlation-ID"] == "preserve-test"

    @pytest.mark.asyncio
    async def test_middleware_handles_call_next_exception(self):
        """Test middleware behavior when call_next raises exception."""
        request = Mock(spec=Request)
        request.headers = {}
        
        async def mock_call_next_with_exception(req):
            # Set correlation ID then raise exception
            correlation_id = get_correlation_id()
            assert correlation_id is not None
            raise Exception("Handler failed")
        
        with pytest.raises(Exception, match="Handler failed"):
            await self.middleware.dispatch(request, mock_call_next_with_exception)

    @pytest.mark.asyncio
    async def test_middleware_inheritance(self):
        """Test that middleware properly inherits from BaseHTTPMiddleware."""
        assert isinstance(self.middleware, BaseHTTPMiddleware)

    @pytest.mark.asyncio
    async def test_middleware_multiple_requests_different_ids(self):
        """Test that multiple requests get different correlation IDs."""
        correlation_ids = []
        
        async def process_request():
            request = Mock(spec=Request)
            request.headers = {}
            
            response = Mock(spec=Response)
            response.headers = {}
            
            async def mock_call_next(req):
                correlation_id = get_correlation_id()
                correlation_ids.append(correlation_id)
                return response
            
            await self.middleware.dispatch(request, mock_call_next)
        
        # Process multiple requests
        import asyncio
        await asyncio.gather(
            process_request(),
            process_request(),
            process_request()
        )
        
        # All correlation IDs should be different
        assert len(correlation_ids) == 3
        assert len(set(correlation_ids)) == 3  # All unique

    @pytest.mark.asyncio
    async def test_middleware_empty_correlation_id_header(self):
        """Test middleware when correlation ID header is empty."""
        request = Mock(spec=Request)
        request.headers = {"X-Correlation-ID": ""}
        
        response = Mock(spec=Response)
        response.headers = {}
        
        async def mock_call_next(req):
            # Should generate new ID when header is empty
            correlation_id = get_correlation_id()
            assert correlation_id is not None
            assert len(correlation_id) > 0
            return response
        
        result = await self.middleware.dispatch(request, mock_call_next)
        
        # Should have generated new correlation ID
        assert "X-Correlation-ID" in response.headers
        assert len(response.headers["X-Correlation-ID"]) > 0

    @pytest.mark.asyncio
    async def test_middleware_whitespace_correlation_id_header(self):
        """Test middleware when correlation ID header contains only whitespace."""
        request = Mock(spec=Request)
        request.headers = {"X-Correlation-ID": "   "}
        
        response = Mock(spec=Response)
        response.headers = {}
        
        async def mock_call_next(req):
            # Should generate new ID when header is whitespace
            correlation_id = get_correlation_id()
            assert correlation_id is not None
            assert correlation_id.strip() != ""
            return response
        
        result = await self.middleware.dispatch(request, mock_call_next)
        
        # Should have generated new correlation ID (not whitespace)
        assert "X-Correlation-ID" in response.headers
        correlation_id = response.headers["X-Correlation-ID"]
        assert correlation_id.strip() != ""
        assert len(correlation_id) > 0