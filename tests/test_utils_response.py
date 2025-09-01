"""Tests for standardized API response utilities."""

from datetime import datetime
from unittest.mock import patch

import pytest

from chatter.utils.response import (
    PaginatedResponse,
    ResponseMetadata,
    StandardResponse,
    create_error_response,
    create_success_response,
    wrap_response,
)


@pytest.mark.unit
class TestResponseMetadata:
    """Test ResponseMetadata functionality."""

    def test_response_metadata_defaults(self):
        """Test ResponseMetadata with default values."""
        # Act
        metadata = ResponseMetadata()
        
        # Assert
        assert isinstance(metadata.timestamp, datetime)
        assert metadata.correlation_id is None
        assert metadata.version is not None  # Should get from settings
        assert metadata.request_id is None

    def test_response_metadata_with_values(self):
        """Test ResponseMetadata with custom values."""
        # Arrange
        test_timestamp = datetime(2024, 1, 1, 12, 0, 0)
        test_correlation_id = "test-correlation-123"
        test_version = "v2.0"
        test_request_id = "req-456"
        
        # Act
        metadata = ResponseMetadata(
            timestamp=test_timestamp,
            correlation_id=test_correlation_id,
            version=test_version,
            request_id=test_request_id
        )
        
        # Assert
        assert metadata.timestamp == test_timestamp
        assert metadata.correlation_id == test_correlation_id
        assert metadata.version == test_version
        assert metadata.request_id == test_request_id

    def test_response_metadata_serialization(self):
        """Test that ResponseMetadata can be serialized."""
        # Arrange
        metadata = ResponseMetadata(correlation_id="test-123")
        
        # Act
        serialized = metadata.model_dump()
        
        # Assert
        assert isinstance(serialized, dict)
        assert "timestamp" in serialized
        assert "correlation_id" in serialized
        assert "version" in serialized
        assert "request_id" in serialized


@pytest.mark.unit
class TestStandardResponse:
    """Test StandardResponse functionality."""

    def test_standard_response_basic(self):
        """Test basic StandardResponse creation."""
        # Act
        response = StandardResponse(success=True)
        
        # Assert
        assert response.success is True
        assert response.data is None
        assert response.message is None
        assert response.errors is None
        assert isinstance(response.metadata, ResponseMetadata)

    def test_standard_response_with_data(self):
        """Test StandardResponse with data."""
        # Arrange
        test_data = {"key": "value", "number": 123}
        test_message = "Operation successful"
        test_errors = ["warning 1", "warning 2"]
        
        # Act
        response = StandardResponse(
            success=True,
            data=test_data,
            message=test_message,
            errors=test_errors
        )
        
        # Assert
        assert response.success is True
        assert response.data == test_data
        assert response.message == test_message
        assert response.errors == test_errors

    @patch('chatter.utils.response.get_correlation_id')
    def test_standard_response_correlation_id_injection(self, mock_get_correlation_id):
        """Test that correlation ID is automatically injected."""
        # Arrange
        mock_get_correlation_id.return_value = "auto-correlation-123"
        
        # Act
        response = StandardResponse(success=True)
        
        # Assert
        assert response.metadata.correlation_id == "auto-correlation-123"
        mock_get_correlation_id.assert_called_once()

    @patch('chatter.utils.response.get_correlation_id')
    def test_standard_response_existing_correlation_id_preserved(self, mock_get_correlation_id):
        """Test that existing correlation ID is not overwritten."""
        # Arrange
        mock_get_correlation_id.return_value = "auto-correlation-123"
        existing_correlation_id = "existing-correlation-456"
        metadata = ResponseMetadata(correlation_id=existing_correlation_id)
        
        # Act
        response = StandardResponse(success=True, metadata=metadata)
        
        # Assert
        assert response.metadata.correlation_id == existing_correlation_id
        # get_correlation_id should not be called since we have existing ID
        mock_get_correlation_id.assert_not_called()

    @patch('chatter.utils.response.get_correlation_id')
    def test_standard_response_no_correlation_id_from_context(self, mock_get_correlation_id):
        """Test behavior when no correlation ID is available from context."""
        # Arrange
        mock_get_correlation_id.return_value = None
        
        # Act
        response = StandardResponse(success=True)
        
        # Assert
        assert response.metadata.correlation_id is None
        mock_get_correlation_id.assert_called_once()

    def test_standard_response_serialization(self):
        """Test that StandardResponse can be serialized."""
        # Arrange
        response = StandardResponse(
            success=True,
            data={"test": "data"},
            message="Test message"
        )
        
        # Act
        serialized = response.model_dump()
        
        # Assert
        assert isinstance(serialized, dict)
        assert serialized["success"] is True
        assert serialized["data"] == {"test": "data"}
        assert serialized["message"] == "Test message"
        assert "metadata" in serialized


@pytest.mark.unit
class TestPaginatedResponse:
    """Test PaginatedResponse functionality."""

    def test_paginated_response_basic(self):
        """Test basic PaginatedResponse creation."""
        # Arrange
        pagination_data = {
            "page": 1,
            "per_page": 10,
            "total": 100,
            "pages": 10
        }
        
        # Act
        response = PaginatedResponse(
            success=True,
            pagination=pagination_data
        )
        
        # Assert
        assert response.success is True
        assert response.pagination == pagination_data
        assert isinstance(response.metadata, ResponseMetadata)

    def test_paginated_response_inheritance(self):
        """Test that PaginatedResponse inherits from StandardResponse."""
        # Act
        response = PaginatedResponse(success=True)
        
        # Assert
        assert isinstance(response, StandardResponse)
        assert hasattr(response, 'pagination')

    def test_paginated_response_serialization(self):
        """Test that PaginatedResponse can be serialized."""
        # Arrange
        response = PaginatedResponse(
            success=True,
            data=[1, 2, 3],
            pagination={"page": 1, "total": 3}
        )
        
        # Act
        serialized = response.model_dump()
        
        # Assert
        assert isinstance(serialized, dict)
        assert "pagination" in serialized
        assert serialized["pagination"] == {"page": 1, "total": 3}


@pytest.mark.unit
class TestResponseFunctions:
    """Test response utility functions."""

    def test_create_success_response_basic(self):
        """Test basic success response creation."""
        # Act
        response = create_success_response()
        
        # Assert
        assert isinstance(response, StandardResponse)
        assert response.success is True
        assert response.data is None
        assert response.message is None

    def test_create_success_response_with_data(self):
        """Test success response with data."""
        # Arrange
        test_data = {"result": "success", "count": 5}
        test_message = "Data retrieved successfully"
        
        # Act
        response = create_success_response(data=test_data, message=test_message)
        
        # Assert
        assert isinstance(response, StandardResponse)
        assert response.success is True
        assert response.data == test_data
        assert response.message == test_message

    def test_create_success_response_with_pagination(self):
        """Test success response with pagination returns PaginatedResponse."""
        # Arrange
        test_data = [1, 2, 3, 4, 5]
        test_message = "Page retrieved"
        pagination_data = {
            "page": 2,
            "per_page": 5,
            "total": 25,
            "pages": 5
        }
        
        # Act
        response = create_success_response(
            data=test_data,
            message=test_message,
            pagination=pagination_data
        )
        
        # Assert
        assert isinstance(response, PaginatedResponse)
        assert response.success is True
        assert response.data == test_data
        assert response.message == test_message
        assert response.pagination == pagination_data

    def test_create_error_response_basic(self):
        """Test basic error response creation."""
        # Arrange
        error_message = "Something went wrong"
        
        # Act
        response = create_error_response(message=error_message)
        
        # Assert
        assert isinstance(response, StandardResponse)
        assert response.success is False
        assert response.message == error_message
        assert response.errors == []
        assert response.data is None

    def test_create_error_response_with_details(self):
        """Test error response with detailed errors."""
        # Arrange
        error_message = "Validation failed"
        error_details = ["Field 'name' is required", "Field 'email' is invalid"]
        error_data = {"field_errors": {"name": "required", "email": "invalid"}}
        
        # Act
        response = create_error_response(
            message=error_message,
            errors=error_details,
            data=error_data
        )
        
        # Assert
        assert isinstance(response, StandardResponse)
        assert response.success is False
        assert response.message == error_message
        assert response.errors == error_details
        assert response.data == error_data

    def test_create_error_response_none_errors(self):
        """Test error response when errors list is None."""
        # Act
        response = create_error_response(message="Error occurred", errors=None)
        
        # Assert
        assert response.errors == []

    def test_wrap_response_basic(self):
        """Test basic response wrapping."""
        # Arrange
        existing_data = {"existing": "data", "values": [1, 2, 3]}
        
        # Act
        response = wrap_response(existing_data)
        
        # Assert
        assert isinstance(response, StandardResponse)
        assert response.success is True
        assert response.data == existing_data
        assert response.message is None

    def test_wrap_response_with_message(self):
        """Test response wrapping with message."""
        # Arrange
        existing_data = "simple string data"
        wrap_message = "Data successfully wrapped"
        
        # Act
        response = wrap_response(existing_data, message=wrap_message)
        
        # Assert
        assert isinstance(response, StandardResponse)
        assert response.success is True
        assert response.data == existing_data
        assert response.message == wrap_message

    def test_wrap_response_various_data_types(self):
        """Test wrapping various data types."""
        # Test cases with different data types
        test_cases = [
            "string data",
            123,
            [1, 2, 3],
            {"dict": "data"},
            None,
            True,
            ["mixed", 123, {"nested": "dict"}]
        ]
        
        for test_data in test_cases:
            # Act
            response = wrap_response(test_data)
            
            # Assert
            assert isinstance(response, StandardResponse)
            assert response.success is True
            assert response.data == test_data


@pytest.mark.integration
class TestResponseIntegration:
    """Integration tests for response utilities."""

    @patch('chatter.utils.response.get_correlation_id')
    def test_response_creation_workflow(self, mock_get_correlation_id):
        """Test complete response creation workflow."""
        # Arrange
        mock_get_correlation_id.return_value = "workflow-correlation-789"
        
        # Act - Create different types of responses
        success_response = create_success_response(
            data={"workflow": "test"},
            message="Workflow completed"
        )
        
        error_response = create_error_response(
            message="Workflow failed",
            errors=["Step 1 failed", "Step 2 failed"]
        )
        
        paginated_response = create_success_response(
            data=[1, 2, 3],
            pagination={"page": 1, "total": 3}
        )
        
        wrapped_response = wrap_response({"legacy": "data"})
        
        # Assert
        responses = [success_response, error_response, paginated_response, wrapped_response]
        
        for response in responses:
            assert hasattr(response, 'metadata')
            assert response.metadata.correlation_id == "workflow-correlation-789"
            # All responses should be serializable
            serialized = response.model_dump()
            assert isinstance(serialized, dict)

    def test_response_metadata_consistency(self):
        """Test that metadata is consistent across response types."""
        # Act
        responses = [
            StandardResponse(success=True),
            PaginatedResponse(success=True),
            create_success_response(),
            create_error_response("error"),
            wrap_response("data")
        ]
        
        # Assert
        for response in responses:
            assert hasattr(response, 'metadata')
            assert isinstance(response.metadata, ResponseMetadata)
            assert hasattr(response.metadata, 'timestamp')
            assert hasattr(response.metadata, 'correlation_id')
            assert hasattr(response.metadata, 'version')
            assert hasattr(response.metadata, 'request_id')

    def test_response_json_serialization(self):
        """Test that responses can be converted to JSON-compatible formats."""
        import json
        
        # Arrange
        response = create_success_response(
            data={"test": "json", "number": 42},
            message="JSON test"
        )
        
        # Act
        response_dict = response.model_dump()
        json_string = json.dumps(response_dict, default=str)
        
        # Assert
        assert isinstance(json_string, str)
        parsed = json.loads(json_string)
        assert parsed["success"] is True
        assert parsed["data"]["test"] == "json"
        assert parsed["message"] == "JSON test"


@pytest.mark.unit
class TestResponseEdgeCases:
    """Test edge cases and error scenarios."""

    def test_response_with_empty_strings(self):
        """Test response creation with empty strings."""
        # Act
        response = create_success_response(
            data="",
            message=""
        )
        
        # Assert
        assert response.success is True
        assert response.data == ""
        assert response.message == ""

    def test_response_with_large_data(self):
        """Test response with large data structures."""
        # Arrange
        large_data = {"items": list(range(1000)), "metadata": {"size": "large"}}
        
        # Act
        response = create_success_response(data=large_data)
        
        # Assert
        assert response.success is True
        assert len(response.data["items"]) == 1000
        assert response.data["metadata"]["size"] == "large"

    def test_error_response_with_empty_errors_list(self):
        """Test error response with explicitly empty errors list."""
        # Act
        response = create_error_response(message="Error", errors=[])
        
        # Assert
        assert response.success is False
        assert response.errors == []

    def test_pagination_response_with_none_pagination(self):
        """Test that None pagination returns StandardResponse."""
        # Act
        response = create_success_response(
            data={"test": "data"},
            pagination=None
        )
        
        # Assert
        assert isinstance(response, StandardResponse)
        assert not isinstance(response, PaginatedResponse)

    def test_pagination_response_with_empty_dict_pagination(self):
        """Test that empty dict pagination returns StandardResponse."""
        # Act
        response = create_success_response(
            data={"test": "data"},
            pagination={}
        )
        
        # Assert
        assert isinstance(response, StandardResponse)
        assert not isinstance(response, PaginatedResponse)

    @patch('chatter.utils.response.get_correlation_id')
    def test_correlation_id_exception_handling(self, mock_get_correlation_id):
        """Test behavior when get_correlation_id raises an exception."""
        # Arrange
        mock_get_correlation_id.side_effect = Exception("Correlation ID error")
        
        # Act & Assert - Exception should propagate since no error handling in current implementation
        with pytest.raises(Exception, match="Correlation ID error"):
            StandardResponse(success=True)