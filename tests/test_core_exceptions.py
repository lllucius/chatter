"""Tests for exception handling core functionality."""

from unittest.mock import patch

import pytest

from chatter.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ChatServiceError,
    ChatterException,
    ConflictError,
    EmbeddingError,
    ExternalServiceError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    WorkflowExecutionError,
)


@pytest.mark.unit
class TestBaseException:
    """Test base exception functionality."""

    def test_chatter_exception_creation(self):
        """Test basic ChatterException creation."""
        # Arrange
        message = "Test exception message"
        code = "TEST_ERROR"

        # Act
        exception = ChatterException(message, error_code=code)

        # Assert
        assert str(exception) == message
        assert exception.error_code == code
        assert exception.details is None

    def test_chatter_exception_with_details(self):
        """Test ChatterException with additional details."""
        # Arrange
        message = "Error with details"
        details = {"field": "username", "value": "invalid"}

        # Act
        exception = ChatterException(message, details=details)

        # Assert
        assert exception.details == details
        assert exception.error_code is None

    def test_chatter_exception_with_cause(self):
        """Test ChatterException with underlying cause."""
        # Arrange
        original_error = ValueError("Original error")

        # Act
        exception = ChatterException(
            "Wrapped error", cause=original_error
        )

        # Assert
        assert exception.cause == original_error
        assert exception.__cause__ == original_error

    def test_exception_serialization(self):
        """Test exception serialization to dict."""
        # Arrange
        exception = ChatterException(
            "Serialization test",
            error_code="SERIALIZE_ERROR",
            details={"key": "value"},
        )

        # Act
        serialized = exception.to_dict()

        # Assert
        assert serialized["message"] == "Serialization test"
        assert serialized["error_code"] == "SERIALIZE_ERROR"
        assert serialized["details"] == {"key": "value"}
        assert "timestamp" in serialized


@pytest.mark.unit
class TestAuthenticationErrors:
    """Test authentication-related exceptions."""

    def test_authentication_error_basic(self):
        """Test basic AuthenticationError."""
        # Act
        error = AuthenticationError("Invalid credentials")

        # Assert
        assert isinstance(error, ChatterException)
        assert str(error) == "Invalid credentials"
        assert error.error_code == "AUTHENTICATION_ERROR"

    def test_authentication_error_with_user_id(self):
        """Test AuthenticationError with user ID."""
        # Act
        error = AuthenticationError(
            "Token expired",
            details={"user_id": "user-123", "token_type": "access"},
        )

        # Assert
        assert error.details["user_id"] == "user-123"
        assert error.details["token_type"] == "access"

    def test_authorization_error_basic(self):
        """Test basic AuthorizationError."""
        # Act
        error = AuthorizationError("Insufficient permissions")

        # Assert
        assert isinstance(error, ChatterException)
        assert str(error) == "Insufficient permissions"
        assert error.error_code == "AUTHORIZATION_ERROR"

    def test_authorization_error_with_permissions(self):
        """Test AuthorizationError with permission details."""
        # Act
        error = AuthorizationError(
            "Missing permission",
            details={
                "required_permission": "documents:write",
                "user_permissions": ["documents:read", "chats:write"],
            },
        )

        # Assert
        assert error.details["required_permission"] == "documents:write"
        assert "documents:read" in error.details["user_permissions"]


@pytest.mark.unit
class TestResourceErrors:
    """Test resource-related exceptions."""

    def test_not_found_error_basic(self):
        """Test basic NotFoundError."""
        # Act
        error = NotFoundError("Document not found")

        # Assert
        assert isinstance(error, ChatterException)
        assert str(error) == "Document not found"
        assert error.error_code == "NOT_FOUND"

    def test_not_found_error_with_resource_id(self):
        """Test NotFoundError with resource details."""
        # Act
        error = NotFoundError(
            "User not found",
            details={
                "resource_type": "user",
                "resource_id": "user-123",
                "operation": "get_profile",
            },
        )

        # Assert
        assert error.details["resource_type"] == "user"
        assert error.details["resource_id"] == "user-123"

    def test_conflict_error_basic(self):
        """Test basic ConflictError."""
        # Act
        error = ConflictError("Email already exists")

        # Assert
        assert isinstance(error, ChatterException)
        assert str(error) == "Email already exists"
        assert error.error_code == "CONFLICT"

    def test_conflict_error_with_existing_resource(self):
        """Test ConflictError with existing resource details."""
        # Act
        error = ConflictError(
            "Username taken",
            details={
                "field": "username",
                "value": "testuser",
                "existing_id": "user-456",
            },
        )

        # Assert
        assert error.details["field"] == "username"
        assert error.details["existing_id"] == "user-456"


@pytest.mark.unit
class TestValidationErrors:
    """Test validation-related exceptions."""

    def test_validation_error_basic(self):
        """Test basic ValidationError."""
        # Act
        error = ValidationError("Invalid input format")

        # Assert
        assert isinstance(error, ChatterException)
        assert str(error) == "Invalid input format"
        assert error.error_code == "VALIDATION_ERROR"

    def test_validation_error_with_field_errors(self):
        """Test ValidationError with field-specific errors."""
        # Act
        error = ValidationError(
            "Validation failed",
            details={
                "field_errors": {
                    "email": ["Invalid email format"],
                    "password": [
                        "Password too short",
                        "Must contain numbers",
                    ],
                }
            },
        )

        # Assert
        assert "email" in error.details["field_errors"]
        assert len(error.details["field_errors"]["password"]) == 2

    def test_validation_error_from_pydantic(self):
        """Test ValidationError created from Pydantic validation."""
        # Arrange
        pydantic_errors = [
            {
                "loc": ("email",),
                "msg": "field required",
                "type": "value_error.missing",
            },
            {
                "loc": ("age",),
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
            },
        ]

        # Act
        error = ValidationError.from_pydantic_errors(pydantic_errors)

        # Assert
        assert "email" in str(error)
        assert "field required" in str(error)


@pytest.mark.unit
class TestServiceErrors:
    """Test service-related exceptions."""

    def test_rate_limit_error_basic(self):
        """Test basic RateLimitError."""
        # Act
        error = RateLimitError("Rate limit exceeded")

        # Assert
        assert isinstance(error, ChatterException)
        assert str(error) == "Rate limit exceeded"
        assert error.error_code == "RATE_LIMIT_EXCEEDED"

    def test_rate_limit_error_with_retry_info(self):
        """Test RateLimitError with retry information."""
        # Act
        error = RateLimitError(
            "Too many requests",
            details={
                "retry_after": 60,
                "limit": 100,
                "remaining": 0,
                "reset_time": "2024-01-01T12:00:00Z",
            },
        )

        # Assert
        assert error.details["retry_after"] == 60
        assert error.details["limit"] == 100

    def test_external_service_error_basic(self):
        """Test basic ExternalServiceError."""
        # Act
        error = ExternalServiceError("OpenAI API unavailable")

        # Assert
        assert isinstance(error, ChatterException)
        assert str(error) == "OpenAI API unavailable"
        assert error.error_code == "EXTERNAL_SERVICE_ERROR"

    def test_external_service_error_with_service_details(self):
        """Test ExternalServiceError with service details."""
        # Act
        error = ExternalServiceError(
            "Service timeout",
            details={
                "service": "openai",
                "endpoint": "/v1/chat/completions",
                "status_code": 504,
                "response_time": 30.5,
            },
        )

        # Assert
        assert error.details["service"] == "openai"
        assert error.details["status_code"] == 504

    def test_workflow_execution_error_basic(self):
        """Test basic WorkflowExecutionError."""
        # Act
        error = WorkflowExecutionError("Workflow step failed")

        # Assert
        assert isinstance(error, ChatterException)
        assert str(error) == "Workflow step failed"
        assert error.error_code == "WORKFLOW_EXECUTION_ERROR"

    def test_workflow_execution_error_with_step_details(self):
        """Test WorkflowExecutionError with step details."""
        # Act
        error = WorkflowExecutionError(
            "Step execution failed",
            details={
                "workflow_id": "workflow-123",
                "step_id": "step-2",
                "step_name": "LLM Processing",
                "execution_time": 15.2,
            },
        )

        # Assert
        assert error.details["workflow_id"] == "workflow-123"
        assert error.details["step_name"] == "LLM Processing"


@pytest.mark.unit
class TestSpecializedErrors:
    """Test specialized domain-specific exceptions."""

    def test_embedding_error_basic(self):
        """Test basic EmbeddingError."""
        # Act
        error = EmbeddingError("Embedding generation failed")

        # Assert
        assert isinstance(error, ChatterException)
        assert str(error) == "Embedding generation failed"
        assert error.error_code == "EMBEDDING_ERROR"

    def test_embedding_error_with_model_details(self):
        """Test EmbeddingError with model details."""
        # Act
        error = EmbeddingError(
            "Model not available",
            details={
                "model": "text-embedding-ada-002",
                "provider": "openai",
                "text_length": 5000,
                "max_tokens": 8191,
            },
        )

        # Assert
        assert error.details["model"] == "text-embedding-ada-002"
        assert error.details["text_length"] == 5000

    def test_chat_service_error_basic(self):
        """Test basic ChatServiceError."""
        # Act
        error = ChatServiceError("Chat processing failed")

        # Assert
        assert isinstance(error, ChatterException)
        assert str(error) == "Chat processing failed"
        assert error.error_code == "CHAT_SERVICE_ERROR"

    def test_chat_service_error_with_conversation_details(self):
        """Test ChatServiceError with conversation details."""
        # Act
        error = ChatServiceError(
            "Message processing failed",
            details={
                "conversation_id": "conv-123",
                "message_id": "msg-456",
                "user_id": "user-789",
                "agent_id": "agent-abc",
            },
        )

        # Assert
        assert error.details["conversation_id"] == "conv-123"
        assert error.details["agent_id"] == "agent-abc"


@pytest.mark.unit
class TestExceptionHandling:
    """Test exception handling utilities."""

    def test_exception_logging(self):
        """Test exception logging functionality."""
        # Arrange
        error = ChatterException("Test error for logging")

        with patch('chatter.core.exceptions.logger') as mock_logger:
            # Act
            error.log_error()

            # Assert
            mock_logger.error.assert_called_once()

    def test_exception_with_traceback(self):
        """Test exception with traceback capture."""
        # Arrange
        try:
            raise ValueError("Original error")
        except ValueError as e:
            # Act
            wrapped_error = ChatterException("Wrapped error", cause=e)

            # Assert
            assert wrapped_error.cause is not None
            assert isinstance(wrapped_error.cause, ValueError)

    def test_exception_chain_handling(self):
        """Test exception chaining."""
        # Arrange
        original = ValueError("Original")
        try:
            raise RuntimeError("Middle") from original
        except RuntimeError:
            pass

        # Act
        final = ChatterException("Final", cause=middle)

        # Assert
        assert final.cause == middle
        assert final.cause.__cause__ == original

    def test_exception_context_manager(self):
        """Test exception context manager usage."""
        # Act & Assert
        with pytest.raises(ChatterException) as exc_info:
            with ChatterException.context("Test operation"):
                raise ValueError("Internal error")

        # The context manager should wrap the error
        assert "Test operation" in str(exc_info.value)

    def test_exception_error_codes(self):
        """Test that all exception types have correct error codes."""
        # Act & Assert
        assert (
            AuthenticationError("test").error_code
            == "AUTHENTICATION_ERROR"
        )
        assert (
            AuthorizationError("test").error_code
            == "AUTHORIZATION_ERROR"
        )
        assert NotFoundError("test").error_code == "NOT_FOUND"
        assert ConflictError("test").error_code == "CONFLICT"
        assert ValidationError("test").error_code == "VALIDATION_ERROR"
        assert (
            RateLimitError("test").error_code == "RATE_LIMIT_EXCEEDED"
        )
        assert (
            ExternalServiceError("test").error_code
            == "EXTERNAL_SERVICE_ERROR"
        )
        assert (
            WorkflowExecutionError("test").error_code
            == "WORKFLOW_EXECUTION_ERROR"
        )
        assert EmbeddingError("test").error_code == "EMBEDDING_ERROR"
        assert (
            ChatServiceError("test").error_code == "CHAT_SERVICE_ERROR"
        )


@pytest.mark.integration
class TestExceptionIntegration:
    """Integration tests for exception handling."""

    def test_exception_in_request_context(self):
        """Test exception handling in request context."""
        # This would test how exceptions are handled in the FastAPI context
        # For now, we'll test the basic exception handling flow

        # Arrange
        error = ValidationError(
            "Request validation failed",
            details={"field": "email", "value": "invalid"},
        )

        # Act
        error_dict = error.to_dict()

        # Assert
        assert error_dict["error_code"] == "VALIDATION_ERROR"
        assert error_dict["details"]["field"] == "email"

    def test_exception_error_response_format(self):
        """Test exception formatting for API responses."""
        # Arrange
        error = NotFoundError(
            "Resource not found",
            details={"resource_id": "123", "resource_type": "document"},
        )

        # Act
        response_data = error.to_response_dict()

        # Assert
        assert "error" in response_data
        assert response_data["error"]["code"] == "NOT_FOUND"
        assert response_data["error"]["message"] == "Resource not found"

    def test_exception_monitoring_integration(self):
        """Test exception integration with monitoring systems."""
        # Arrange
        error = ExternalServiceError(
            "Service unavailable",
            details={"service": "openai", "status_code": 503},
        )

        with patch(
            'chatter.core.exceptions.monitoring'
        ) as mock_monitoring:
            # Act
            error.report_to_monitoring()

            # Assert
            mock_monitoring.report_error.assert_called_once_with(
                error_type="EXTERNAL_SERVICE_ERROR",
                message="Service unavailable",
                details={"service": "openai", "status_code": 503},
            )
