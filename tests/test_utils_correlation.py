"""Tests for correlation ID utilities."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import Response

from chatter.utils.correlation import (
    CorrelationIdMiddleware,
    correlation_id_var,
    generate_correlation_id,
    get_correlation_id,
    set_correlation_id,
)


@pytest.mark.unit
class TestCorrelationIdFunctions:
    """Test correlation ID utility functions."""

    def setup_method(self):
        """Reset correlation ID context before each test."""
        correlation_id_var.set(None)

    def test_generate_correlation_id(self):
        """Test correlation ID generation."""
        # Act
        correlation_id = generate_correlation_id()

        # Assert
        assert isinstance(correlation_id, str)
        assert len(correlation_id) == 36  # UUID4 string length
        # Verify it's a valid UUID
        parsed_uuid = uuid.UUID(correlation_id)
        assert str(parsed_uuid) == correlation_id

    def test_generate_correlation_id_unique(self):
        """Test that generated correlation IDs are unique."""
        # Act
        id1 = generate_correlation_id()
        id2 = generate_correlation_id()

        # Assert
        assert id1 != id2

    def test_get_correlation_id_default(self):
        """Test getting correlation ID when none is set."""
        # Act
        correlation_id = get_correlation_id()

        # Assert
        assert correlation_id is None

    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        # Arrange
        test_id = "test-correlation-id"

        # Act
        set_correlation_id(test_id)
        retrieved_id = get_correlation_id()

        # Assert
        assert retrieved_id == test_id

    def test_correlation_id_context_isolation(self):
        """Test that correlation IDs are isolated per context."""
        # This test verifies the ContextVar behavior
        # Arrange
        test_id = "test-id"

        # Act
        set_correlation_id(test_id)
        id_before = get_correlation_id()

        # Reset context
        correlation_id_var.set(None)
        id_after = get_correlation_id()

        # Assert
        assert id_before == test_id
        assert id_after is None


@pytest.mark.unit
class TestCorrelationIdMiddleware:
    """Test CorrelationIdMiddleware functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = MagicMock()
        self.middleware = CorrelationIdMiddleware(self.app)
        correlation_id_var.set(None)

    @pytest.mark.asyncio
    async def test_middleware_with_existing_correlation_id(self):
        """Test middleware when correlation ID is provided in request."""
        # Arrange
        test_correlation_id = "existing-correlation-id"
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"x-correlation-id": test_correlation_id}

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        # Act
        response = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert (
            response.headers['x-correlation-id'] == test_correlation_id
        )
        assert get_correlation_id() == test_correlation_id

    @pytest.mark.asyncio
    async def test_middleware_without_correlation_id(self):
        """Test middleware when no correlation ID is provided."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        with patch(
            'chatter.utils.correlation.generate_correlation_id'
        ) as mock_generate:
            mock_generate.return_value = "generated-id"

            # Act
            response = await self.middleware.dispatch(
                mock_request, mock_call_next
            )

            # Assert
            assert (
                response.headers['x-correlation-id'] == "generated-id"
            )
            assert get_correlation_id() == "generated-id"
            mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_middleware_with_empty_correlation_id(self):
        """Test middleware when empty correlation ID is provided."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {
            "x-correlation-id": "   "
        }  # Empty/whitespace

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        with patch(
            'chatter.utils.correlation.generate_correlation_id'
        ) as mock_generate:
            mock_generate.return_value = "generated-id"

            # Act
            response = await self.middleware.dispatch(
                mock_request, mock_call_next
            )

            # Assert
            assert (
                response.headers['x-correlation-id'] == "generated-id"
            )
            assert get_correlation_id() == "generated-id"
            mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_middleware_case_insensitive_header(self):
        """Test that middleware handles case-insensitive header lookup."""
        # Arrange
        test_correlation_id = "case-test-id"
        mock_request = MagicMock(spec=Request)
        # Simulate headers with different cases
        mock_request.headers = {"X-CORRELATION-ID": test_correlation_id}

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        # Act
        response = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert (
            response.headers['x-correlation-id'] == test_correlation_id
        )
        assert get_correlation_id() == test_correlation_id

    @pytest.mark.asyncio
    async def test_middleware_header_iteration(self):
        """Test that middleware correctly iterates through headers."""
        # Arrange
        test_correlation_id = "header-test-id"
        mock_request = MagicMock(spec=Request)
        # Mock headers.items() to return an iterable
        headers_items = [
            ("content-type", "application/json"),
            ("x-correlation-id", test_correlation_id),
            ("authorization", "Bearer token"),
        ]
        mock_request.headers.items.return_value = headers_items

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        # Act
        response = await self.middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert (
            response.headers['x-correlation-id'] == test_correlation_id
        )
        assert get_correlation_id() == test_correlation_id


@pytest.mark.integration
class TestCorrelationIdIntegration:
    """Integration tests for correlation ID functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        correlation_id_var.set(None)

    @pytest.mark.asyncio
    async def test_full_middleware_workflow(self):
        """Test complete middleware workflow with context."""
        # Arrange
        app = MagicMock()
        middleware = CorrelationIdMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        mock_response = MagicMock(spec=Response)
        mock_response.headers = {}

        # Track correlation ID during request processing
        captured_correlation_id = None

        async def mock_call_next(request):
            nonlocal captured_correlation_id
            captured_correlation_id = get_correlation_id()
            return mock_response

        # Act
        response = await middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert captured_correlation_id is not None
        assert (
            response.headers['x-correlation-id']
            == captured_correlation_id
        )
        # Correlation ID should still be accessible after middleware
        assert get_correlation_id() == captured_correlation_id

    def test_context_var_behavior(self):
        """Test context variable behavior across function calls."""
        # Arrange
        test_id = "context-test-id"

        def nested_function():
            return get_correlation_id()

        # Act
        set_correlation_id(test_id)
        nested_result = nested_function()

        # Assert
        assert nested_result == test_id
        assert get_correlation_id() == test_id


@pytest.mark.unit
class TestCorrelationIdEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        correlation_id_var.set(None)

    def test_set_correlation_id_with_none(self):
        """Test setting correlation ID to None."""
        # Arrange
        set_correlation_id("test")

        # Act
        set_correlation_id(None)

        # Assert
        assert get_correlation_id() is None

    def test_uuid_format_validation(self):
        """Test that generated UUIDs have correct format."""
        # Act
        correlation_id = generate_correlation_id()

        # Assert - Should be valid UUID4 format
        assert len(correlation_id) == 36
        assert correlation_id.count('-') == 4
        # Verify it's a valid UUID by parsing it
        parsed = uuid.UUID(correlation_id)
        assert parsed.version == 4

    @pytest.mark.asyncio
    async def test_middleware_preserves_original_response(self):
        """Test that middleware doesn't modify response content."""
        # Arrange
        app = MagicMock()
        middleware = CorrelationIdMiddleware(app)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"x-correlation-id": "test-id"}

        original_response = MagicMock(spec=Response)
        original_response.headers = {"content-type": "application/json"}
        original_response.body = b'{"test": "data"}'

        async def mock_call_next(request):
            return original_response

        # Act
        response = await middleware.dispatch(
            mock_request, mock_call_next
        )

        # Assert
        assert response is original_response
        assert response.headers['x-correlation-id'] == "test-id"
        assert response.headers['content-type'] == "application/json"
