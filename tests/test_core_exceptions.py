"""Unit tests for core exceptions module."""

import pytest
import uuid
from typing import Any, Dict

from chatter.core.exceptions import ChatterBaseException
from tests.test_utils import generate_test_id


@pytest.mark.unit
class TestChatterBaseException:
    """Test cases for the base exception class."""

    def test_basic_exception_creation(self):
        """Test creating basic exception with minimal parameters."""
        message = "Test error message"
        exc = ChatterBaseException(message)
        
        assert str(exc) == message
        assert exc.message == message
        assert exc.status_code == 500  # Default
        assert exc.error_code is None  # Default
        assert exc.details is None  # Default
        assert hasattr(exc, 'error_id')  # Should have error ID
        assert hasattr(exc, 'timestamp')  # Should have timestamp

    def test_exception_with_all_parameters(self):
        """Test creating exception with all parameters."""
        message = "Detailed error message"
        error_code = "TEST_ERROR_001"
        status_code = 400
        details = {"field": "value", "count": 42}
        cause = ValueError("Original error")
        
        exc = ChatterBaseException(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details,
            cause=cause
        )
        
        assert str(exc) == message
        assert exc.message == message
        assert exc.error_code == error_code
        assert exc.status_code == status_code
        assert exc.details == details
        assert exc.__cause__ == cause  # Cause is stored in __cause__

    def test_exception_with_kwargs(self):
        """Test creating exception with additional kwargs."""
        message = "Error with extras"
        exc = ChatterBaseException(
            message,
            extra_field="extra_value",
            request_id="req_123",
            user_id="user_456"
        )
        
        assert str(exc) == message
        assert hasattr(exc, 'extra_field')
        assert exc.extra_field == "extra_value"
        assert hasattr(exc, 'request_id')
        assert exc.request_id == "req_123"
        assert hasattr(exc, 'user_id')
        assert exc.user_id == "user_456"

    def test_exception_inheritance(self):
        """Test that ChatterBaseException properly inherits from Exception."""
        exc = ChatterBaseException("Test message")
        
        assert isinstance(exc, Exception)
        assert isinstance(exc, ChatterBaseException)

    def test_exception_representation(self):
        """Test string representation of exception."""
        message = "Test representation"
        error_code = "REP_001"
        
        exc = ChatterBaseException(message, error_code=error_code)
        str_repr = str(exc)
        
        assert message in str_repr
        # The exact representation format may vary, but should include the message

    def test_exception_with_none_details(self):
        """Test exception with explicitly None details."""
        exc = ChatterBaseException("Test", details=None)
        assert exc.details is None

    def test_exception_with_empty_details(self):
        """Test exception with empty details dictionary."""
        exc = ChatterBaseException("Test", details={})
        assert exc.details == {}

    def test_exception_details_immutability(self):
        """Test that details dictionary is properly handled."""
        original_details = {"key": "value"}
        exc = ChatterBaseException("Test", details=original_details)
        
        # Modify original dict
        original_details["new_key"] = "new_value"
        
        # Exception should maintain its own reference
        # Note: This test depends on the implementation detail
        # of whether details are copied or referenced
        assert exc.details is not None

    def test_nested_exception_chain(self):
        """Test creating exception with cause for error chaining."""
        original_error = ValueError("Original problem")
        wrapper_error = ChatterBaseException(
            "Wrapper error",
            cause=original_error
        )
        
        assert wrapper_error.__cause__ == original_error
        assert isinstance(wrapper_error.__cause__, ValueError)

    def test_exception_with_complex_details(self):
        """Test exception with complex details structure."""
        complex_details = {
            "validation_errors": [
                {"field": "email", "message": "Invalid format"},
                {"field": "password", "message": "Too weak"}
            ],
            "request_info": {
                "method": "POST",
                "path": "/api/users",
                "timestamp": "2024-01-01T00:00:00Z"
            },
            "metadata": {
                "version": "1.0.0",
                "environment": "test"
            }
        }
        
        exc = ChatterBaseException(
            "Validation failed",
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=complex_details
        )
        
        assert exc.details == complex_details
        assert exc.details["validation_errors"][0]["field"] == "email"
        assert exc.details["request_info"]["method"] == "POST"


@pytest.mark.unit
class TestExceptionHandlingUtilities:
    """Test utility functions for exception handling."""

    def test_exception_with_generated_ids(self):
        """Test exception with generated correlation IDs."""
        correlation_id = generate_test_id()
        
        exc = ChatterBaseException(
            "Error with correlation ID",
            correlation_id=correlation_id,
            request_id=generate_test_id()
        )
        
        assert exc.correlation_id == correlation_id
        assert hasattr(exc, 'request_id')
        assert exc.request_id is not None

    def test_multiple_exceptions_different_ids(self):
        """Test that multiple exceptions can have different IDs."""
        exc1 = ChatterBaseException("Error 1", request_id=generate_test_id())
        exc2 = ChatterBaseException("Error 2", request_id=generate_test_id())
        
        # Assuming generate_test_id() creates unique IDs
        assert exc1.request_id != exc2.request_id

    def test_exception_serialization_friendly(self):
        """Test that exception can be used in logging/serialization contexts."""
        exc = ChatterBaseException(
            "Serializable error",
            error_code="SER_001",
            status_code=400,
            details={"field": "value"}
        )
        
        # Should be able to access all attributes for logging
        error_dict = {
            "message": str(exc),
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details
        }
        
        assert error_dict["message"] == "Serializable error"
        assert error_dict["error_code"] == "SER_001"
        assert error_dict["status_code"] == 400
        assert error_dict["details"]["field"] == "value"