"""Error handling tests."""

import pytest
from unittest.mock import patch, MagicMock
from chatter.core.exceptions import (
    ChatterBaseException,
    ChatServiceError,
    LLMServiceError,
    DatabaseError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ConfigurationError,
    WorkflowError
)
from chatter.utils.problem import create_problem_detail, ProblemDetailResponse


@pytest.mark.unit
class TestExceptionHierarchy:
    """Test exception class hierarchy and structure."""

    def test_base_exception_properties(self):
        """Test base exception properties."""
        error = ChatterBaseException(
            message="Test error",
            error_code="TEST_ERROR",
            status_code=500
        )
        
        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.status_code == 500
        assert error.details is None

    def test_base_exception_with_details(self):
        """Test base exception with additional details."""
        details = {"field": "username", "validation": "required"}
        error = ChatterBaseException(
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            details=details
        )
        
        assert error.details == details
        assert error.details["field"] == "username"

    def test_chat_service_error(self):
        """Test ChatServiceError specialization."""
        error = ChatServiceError(
            message="Failed to process chat",
            conversation_id="conv-123"
        )
        
        assert isinstance(error, ChatterBaseException)
        assert error.error_code == "CHAT_SERVICE_ERROR"
        assert error.status_code == 500
        assert error.conversation_id == "conv-123"

    def test_llm_service_error(self):
        """Test LLMServiceError specialization."""
        error = LLMServiceError(
            message="LLM API failed",
            provider="openai",
            model="gpt-4"
        )
        
        assert isinstance(error, ChatterBaseException)
        assert error.error_code == "LLM_SERVICE_ERROR"
        assert error.provider == "openai"
        assert error.model == "gpt-4"

    def test_database_error(self):
        """Test DatabaseError specialization."""
        error = DatabaseError(
            message="Connection failed",
            operation="select",
            table="users"
        )
        
        assert isinstance(error, ChatterBaseException)
        assert error.error_code == "DATABASE_ERROR"
        assert error.operation == "select"
        assert error.table == "users"

    def test_validation_error(self):
        """Test ValidationError specialization."""
        errors = {
            "email": ["Invalid email format"],
            "password": ["Password too weak"]
        }
        error = ValidationError(
            message="Validation failed",
            field_errors=errors
        )
        
        assert isinstance(error, ChatterBaseException)
        assert error.error_code == "VALIDATION_ERROR"
        assert error.status_code == 400
        assert error.field_errors == errors

    def test_authentication_error(self):
        """Test AuthenticationError specialization."""
        error = AuthenticationError(
            message="Invalid credentials",
            auth_method="password"
        )
        
        assert isinstance(error, ChatterBaseException)
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert error.status_code == 401
        assert error.auth_method == "password"

    def test_authorization_error(self):
        """Test AuthorizationError specialization."""
        error = AuthorizationError(
            message="Access denied",
            resource="conversation",
            action="delete"
        )
        
        assert isinstance(error, ChatterBaseException)
        assert error.error_code == "AUTHORIZATION_ERROR"
        assert error.status_code == 403
        assert error.resource == "conversation"
        assert error.action == "delete"

    def test_rate_limit_error(self):
        """Test RateLimitError specialization."""
        error = RateLimitError(
            message="Rate limit exceeded",
            limit=100,
            window="60s",
            retry_after=30
        )
        
        assert isinstance(error, ChatterBaseException)
        assert error.error_code == "RATE_LIMIT_ERROR"
        assert error.status_code == 429
        assert error.limit == 100
        assert error.window == "60s"
        assert error.retry_after == 30

    def test_configuration_error(self):
        """Test ConfigurationError specialization."""
        error = ConfigurationError(
            message="Invalid configuration",
            config_key="OPENAI_API_KEY",
            config_value="sk-test"
        )
        
        assert isinstance(error, ChatterBaseException)
        assert error.error_code == "CONFIGURATION_ERROR"
        assert error.status_code == 500
        assert error.config_key == "OPENAI_API_KEY"

    def test_workflow_error(self):
        """Test WorkflowError specialization."""
        error = WorkflowError(
            message="Workflow execution failed",
            workflow_id="wf-123",
            step="llm_generation",
            step_details={"provider": "openai", "model": "gpt-4"}
        )
        
        assert isinstance(error, ChatterBaseException)
        assert error.error_code == "WORKFLOW_ERROR"
        assert error.workflow_id == "wf-123"
        assert error.step == "llm_generation"
        assert error.step_details["provider"] == "openai"


@pytest.mark.unit
class TestProblemDetailGeneration:
    """Test RFC 9457 Problem Detail generation."""

    def test_basic_problem_detail(self):
        """Test basic problem detail creation."""
        problem = create_problem_detail(
            status=400,
            title="Bad Request",
            detail="The request was invalid"
        )
        
        assert problem["status"] == 400
        assert problem["title"] == "Bad Request"
        assert problem["detail"] == "The request was invalid"
        assert problem["type"] == "about:blank"

    def test_problem_detail_with_type(self):
        """Test problem detail with custom type."""
        problem = create_problem_detail(
            status=404,
            title="Not Found",
            detail="Resource not found",
            type_="https://example.com/problems/not-found"
        )
        
        assert problem["type"] == "https://example.com/problems/not-found"

    def test_problem_detail_with_instance(self):
        """Test problem detail with instance."""
        problem = create_problem_detail(
            status=409,
            title="Conflict",
            detail="Resource already exists",
            instance="/api/v1/users/123"
        )
        
        assert problem["instance"] == "/api/v1/users/123"

    def test_problem_detail_with_extensions(self):
        """Test problem detail with extensions."""
        extensions = {
            "field_errors": {
                "email": ["Invalid format"],
                "password": ["Too weak"]
            },
            "error_code": "VALIDATION_ERROR",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        problem = create_problem_detail(
            status=400,
            title="Validation Error",
            detail="Request validation failed",
            **extensions
        )
        
        assert problem["field_errors"] == extensions["field_errors"]
        assert problem["error_code"] == "VALIDATION_ERROR"
        assert problem["timestamp"] == "2024-01-01T00:00:00Z"

    def test_exception_to_problem_detail(self):
        """Test converting exceptions to problem details."""
        # Test validation error
        validation_error = ValidationError(
            message="Validation failed",
            field_errors={"email": ["Required field"]}
        )
        
        problem = validation_error.to_problem_detail()
        assert problem["status"] == 400
        assert problem["title"] == "Validation Error"
        assert problem["detail"] == "Validation failed"
        assert problem["field_errors"] == {"email": ["Required field"]}

        # Test authentication error
        auth_error = AuthenticationError(
            message="Invalid token",
            auth_method="jwt"
        )
        
        problem = auth_error.to_problem_detail()
        assert problem["status"] == 401
        assert problem["title"] == "Authentication Error"
        assert problem["auth_method"] == "jwt"

    def test_problem_detail_response(self):
        """Test ProblemDetailResponse creation."""
        response = ProblemDetailResponse(
            status=400,
            title="Bad Request",
            detail="Invalid input data",
            field_errors={"name": ["Required"]}
        )
        
        assert response.status_code == 400
        assert response.media_type == "application/problem+json"
        
        content = response.body.decode()
        import json
        data = json.loads(content)
        
        assert data["status"] == 400
        assert data["title"] == "Bad Request"
        assert data["field_errors"]["name"] == ["Required"]


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling utilities and patterns."""

    def test_error_context_capture(self):
        """Test error context capturing."""
        try:
            # Simulate an error with context
            user_id = "user-123"
            operation = "create_conversation"
            raise ChatServiceError(
                message="Failed to create conversation",
                user_id=user_id,
                operation=operation
            )
        except ChatterBaseException as e:
            assert e.user_id == "user-123"
            assert e.operation == "create_conversation"

    def test_error_chaining(self):
        """Test error chaining and cause tracking."""
        try:
            # Simulate nested error
            try:
                raise DatabaseError("Connection lost")
            except DatabaseError as db_error:
                raise ChatServiceError(
                    message="Chat service unavailable",
                    cause=db_error
                )
        except ChatterBaseException as e:
            assert e.cause is not None
            assert isinstance(e.cause, DatabaseError)
            assert str(e.cause) == "Connection lost"

    def test_error_logging_context(self):
        """Test error logging context."""
        with patch('chatter.utils.logging.logger') as mock_logger:
            error = LLMServiceError(
                message="API rate limited",
                provider="openai",
                model="gpt-4",
                request_id="req-123"
            )
            
            # Simulate logging the error
            error.log_error()
            
            # Verify logging was called with proper context
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert "API rate limited" in str(call_args)
            assert "openai" in str(call_args) or "req-123" in str(call_args)

    def test_sensitive_data_filtering(self):
        """Test filtering of sensitive data from errors."""
        # Create error with potentially sensitive data
        error = ConfigurationError(
            message="Database connection failed: password=secret123",
            config_key="DATABASE_URL",
            config_value="postgresql://user:secret123@host/db"
        )
        
        # Get sanitized error message
        sanitized = error.get_safe_message()
        
        # Sensitive data should be removed
        assert "secret123" not in sanitized
        assert "password=" not in sanitized
        assert "Database connection failed" in sanitized

    def test_error_aggregation(self):
        """Test error aggregation for batch operations."""
        errors = [
            ValidationError("Invalid email", field_errors={"email": ["Invalid"]}),
            ValidationError("Invalid name", field_errors={"name": ["Required"]}),
            ValidationError("Invalid age", field_errors={"age": ["Must be positive"]})
        ]
        
        # Aggregate errors
        aggregated = ValidationError.aggregate(errors)
        
        assert isinstance(aggregated, ValidationError)
        assert len(aggregated.field_errors) == 3
        assert "email" in aggregated.field_errors
        assert "name" in aggregated.field_errors
        assert "age" in aggregated.field_errors


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Integration tests for error handling."""

    async def test_api_error_responses(self, test_client):
        """Test API error response formatting."""
        # Test validation error response
        invalid_data = {"email": "invalid-email"}
        response = await test_client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 400
        assert response.headers["content-type"] == "application/problem+json"
        
        data = response.json()
        assert data["status"] == 400
        assert data["title"] == "Validation Error"
        assert "field_errors" in data

    async def test_authentication_error_response(self, test_client):
        """Test authentication error response."""
        # Test with invalid credentials
        invalid_creds = {"email": "test@example.com", "password": "wrong"}
        response = await test_client.post("/api/v1/auth/login", json=invalid_creds)
        
        assert response.status_code == 401
        assert response.headers["content-type"] == "application/problem+json"
        
        data = response.json()
        assert data["status"] == 401
        assert data["title"] == "Authentication Error"

    async def test_authorization_error_response(self, test_client):
        """Test authorization error response."""
        # Test accessing protected resource without token
        response = await test_client.get("/api/v1/conversations")
        
        assert response.status_code in [401, 403]
        assert response.headers["content-type"] == "application/problem+json"

    async def test_rate_limit_error_response(self, test_client):
        """Test rate limit error response."""
        # Simulate rate limiting (would need actual rate limiter)
        # For now, test the error structure
        error = RateLimitError(
            message="Too many requests",
            limit=10,
            window="60s",
            retry_after=30
        )
        
        problem = error.to_problem_detail()
        assert problem["status"] == 429
        assert problem["limit"] == 10
        assert problem["retry_after"] == 30

    async def test_internal_error_handling(self, test_client):
        """Test internal error handling and sanitization."""
        # This would test how internal errors are sanitized
        # and not leak sensitive information to clients
        
        # Simulate internal error
        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.side_effect = Exception("Database password=secret123 failed")
            
            # Make request that would trigger the error
            response = await test_client.post("/api/v1/chat", json={
                "message": "Hello",
                "conversation_id": "test-conv"
            })
            
            # Should return generic error without sensitive data
            assert response.status_code == 500
            data = response.json()
            assert "password=" not in str(data)
            assert "secret123" not in str(data)

    async def test_error_correlation_ids(self, test_client):
        """Test error correlation ID generation."""
        # Test that errors include correlation IDs for tracing
        response = await test_client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        
        # Should include correlation ID for tracking
        assert "correlation_id" in data or "instance" in data