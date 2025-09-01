"""Tests for RFC 9457 Problem Details utilities."""

import pytest
from unittest.mock import Mock, patch
from fastapi import Request, status
from fastapi.responses import JSONResponse

from chatter.utils.problem import (
    ProblemException,
    ValidationProblem,
    AuthenticationProblem,
    AuthorizationProblem,
    NotFoundProblem,
    ConflictProblem,
    InternalServerProblem,
    ServiceUnavailableProblem,
    RateLimitProblem,  # Changed from TooManyRequestsProblem
    BadRequestProblem,
    UnauthorizedProblem,
    ForbiddenProblem,
    ProblemDetailResponse,
    create_problem_response,
    create_problem_detail,
)
from chatter.schemas.utilities import ProblemDetail


@pytest.mark.unit
class TestProblemException:
    """Test ProblemException class."""

    def test_problem_exception_basic(self):
        """Test basic ProblemException creation."""
        # Arrange & Act
        exception = ProblemException(
            status_code=400,
            title="Bad Request",
            detail="The request was invalid"
        )

        # Assert
        assert exception.status_code == 400
        assert exception.title == "Bad Request"
        assert exception.detail == "The request was invalid"
        assert exception.type_suffix is None
        assert exception.instance is None
        assert exception.extra_fields == {}

    def test_problem_exception_with_type_suffix(self):
        """Test ProblemException with type suffix."""
        # Arrange & Act
        with patch('chatter.utils.problem.settings') as mock_settings:
            mock_settings.api_base_url = "https://api.example.com"
            
            exception = ProblemException(
                status_code=422,
                title="Validation Error",
                detail="Field validation failed",
                type_suffix="validation-error"
            )

        # Assert
        assert exception.status_code == 422
        assert exception.title == "Validation Error"
        assert exception.type_suffix == "validation-error"
        assert exception.type_uri == "https://api.example.com/problems/validation-error"

    def test_problem_exception_with_instance(self):
        """Test ProblemException with instance URI."""
        # Arrange & Act
        exception = ProblemException(
            status_code=404,
            title="Not Found",
            detail="User not found",
            instance="/users/123"
        )

        # Assert
        assert exception.status_code == 404
        assert exception.title == "Not Found"
        assert exception.instance == "/users/123"

    def test_problem_exception_with_extra_fields(self):
        """Test ProblemException with extra fields."""
        # Arrange & Act
        exception = ProblemException(
            status_code=422,
            title="Validation Error",
            detail="Field validation failed",
            errors=["field1 is required", "field2 is invalid"],
            code="VALIDATION_FAILED"
        )

        # Assert
        assert exception.status_code == 422
        assert exception.extra_fields["errors"] == ["field1 is required", "field2 is invalid"]
        assert exception.extra_fields["code"] == "VALIDATION_FAILED"

    def test_problem_exception_to_problem_detail(self):
        """Test converting ProblemException to ProblemDetail."""
        # Arrange
        with patch('chatter.utils.problem.settings') as mock_settings:
            mock_settings.api_base_url = "https://api.example.com"
            
            exception = ProblemException(
                status_code=400,
                title="Bad Request",
                detail="Invalid input",
                type_suffix="bad-request",
                instance="/api/test",
                custom_field="custom_value"
            )

        # Act
        problem_detail = exception.to_problem_detail()

        # Assert
        assert isinstance(problem_detail, ProblemDetail)
        assert problem_detail.status == 400
        assert problem_detail.title == "Bad Request"
        assert problem_detail.detail == "Invalid input"
        assert problem_detail.type == "https://api.example.com/problems/bad-request"
        assert problem_detail.instance == "/api/test"


@pytest.mark.unit
class TestSpecificProblemExceptions:
    """Test specific problem exception classes."""

    def test_validation_problem(self):
        """Test ValidationProblem."""
        # Arrange & Act
        exception = ValidationProblem(
            detail="Email is required",
            errors=["email field is missing"]
        )

        # Assert
        assert exception.status_code == 422
        assert exception.title == "Validation Error"
        assert exception.detail == "Email is required"
        assert exception.extra_fields["errors"] == ["email field is missing"]

    def test_authentication_problem(self):
        """Test AuthenticationProblem."""
        # Arrange & Act
        exception = AuthenticationProblem(
            detail="Invalid credentials"
        )

        # Assert
        assert exception.status_code == 401
        assert exception.title == "Authentication Required"
        assert exception.detail == "Invalid credentials"

    def test_authorization_problem(self):
        """Test AuthorizationProblem."""
        # Arrange & Act
        exception = AuthorizationProblem(
            detail="Insufficient permissions"
        )

        # Assert
        assert exception.status_code == 403
        assert exception.title == "Forbidden"
        assert exception.detail == "Insufficient permissions"

    def test_not_found_problem(self):
        """Test NotFoundProblem."""
        # Arrange & Act
        exception = NotFoundProblem(
            detail="User with ID 123 not found",
            resource="user",
            resource_id="123"
        )

        # Assert
        assert exception.status_code == 404
        assert exception.title == "Not Found"
        assert exception.detail == "User with ID 123 not found"
        assert exception.extra_fields["resource"] == "user"
        assert exception.extra_fields["resource_id"] == "123"

    def test_conflict_problem(self):
        """Test ConflictProblem."""
        # Arrange & Act
        exception = ConflictProblem(
            detail="Username already exists",
            conflicting_field="username"
        )

        # Assert
        assert exception.status_code == 409
        assert exception.title == "Conflict"
        assert exception.detail == "Username already exists"
        assert exception.extra_fields["conflicting_field"] == "username"

    def test_internal_server_problem(self):
        """Test InternalServerProblem."""
        # Arrange & Act
        exception = InternalServerProblem(
            detail="Database connection failed"
        )

        # Assert
        assert exception.status_code == 500
        assert exception.title == "Internal Server Error"
        assert exception.detail == "Database connection failed"

    def test_service_unavailable_problem(self):
        """Test ServiceUnavailableProblem."""
        # Arrange & Act
        exception = ServiceUnavailableProblem(
            detail="Service temporarily unavailable",
            retry_after=60
        )

        # Assert
        assert exception.status_code == 503
        assert exception.title == "Service Unavailable"
        assert exception.detail == "Service temporarily unavailable"
        assert exception.extra_fields["retry_after"] == 60

    def test_rate_limit_problem(self):
        """Test RateLimitProblem."""
        # Arrange & Act
        exception = RateLimitProblem(
            detail="Rate limit exceeded",
            retry_after=120,
            limit=100,
            window="hour"
        )

        # Assert
        assert exception.status_code == 429
        assert exception.title == "Rate Limited"
        assert exception.detail == "Rate limit exceeded"
        assert exception.extra_fields["retry_after"] == 120
        assert exception.extra_fields["limit"] == 100
        assert exception.extra_fields["window"] == "hour"


@pytest.mark.unit
class TestProblemUtilities:
    """Test problem utility functions."""

    def test_create_problem_response(self):
        """Test creating problem response."""
        # Arrange
        problem_detail = ProblemDetail(
            type="https://api.example.com/problems/bad-request",
            title="Bad Request",
            status=400,
            detail="Invalid input",
            instance="/api/test"
        )

        # Act
        response = create_problem_response(problem_detail)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert response.headers["content-type"] == "application/problem+json"

    def test_create_problem_response_with_extra_headers(self):
        """Test creating problem response with extra headers."""
        # Arrange
        problem_detail = ProblemDetail(
            type="https://api.example.com/problems/rate-limit",
            title="Too Many Requests",
            status=429,
            detail="Rate limit exceeded"
        )
        headers = {"Retry-After": "60"}

        # Act
        response = create_problem_response(problem_detail, headers=headers)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 429
        assert response.headers["content-type"] == "application/problem+json"
        assert response.headers["Retry-After"] == "60"

    def test_problem_exception_to_response(self):
        """Test ProblemException.to_response method."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        
        exception = ValidationProblem(
            detail="Validation failed",
            validation_errors=[{"field": "name", "message": "required"}]
        )

        # Act
        response = exception.to_response(request)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 422
        assert response.headers["content-type"] == "application/problem+json"


@pytest.mark.integration
class TestProblemIntegration:
    """Integration tests for problem details."""

    def test_problem_exception_inheritance(self):
        """Test that problem exceptions inherit correctly."""
        # Act
        validation_problem = ValidationProblem("Validation error")
        auth_problem = AuthenticationProblem("Auth error")

        # Assert
        assert isinstance(validation_problem, ProblemException)
        assert isinstance(auth_problem, ProblemException)
        assert validation_problem.status_code == 422
        assert auth_problem.status_code == 401

    def test_problem_detail_serialization(self):
        """Test problem detail serialization."""
        # Arrange
        exception = ValidationProblem(
            detail="Field validation failed",
            errors=["email is required", "password too short"]
        )

        # Act
        problem_detail = exception.to_problem_detail()
        data = problem_detail.model_dump()

        # Assert
        assert isinstance(data, dict)
        assert data["status"] == 422
        assert data["title"] == "Validation Error"
        assert data["detail"] == "Field validation failed"
        assert "type" in data
        assert "errors" in data

    def test_problem_response_headers(self):
        """Test problem response headers."""
        # Arrange
        exception = RateLimitProblem(
            detail="Rate limit exceeded",
            retry_after=60
        )
        problem_detail = exception.to_problem_detail()

        # Act
        response = create_problem_response(
            problem_detail,
            headers={"Retry-After": "60"}
        )

        # Assert
        assert response.headers["content-type"] == "application/problem+json"
        assert response.headers["Retry-After"] == "60"

    def test_problem_with_correlation_id(self):
        """Test problem with correlation ID."""
        # Arrange
        exception = InternalServerProblem(
            detail="Database error",
            correlation_id="abc-123-def"
        )

        # Act
        problem_detail = exception.to_problem_detail()

        # Assert
        assert problem_detail.status == 500
        assert "correlation_id" in problem_detail.model_dump()

    def test_complete_problem_workflow(self):
        """Test complete problem workflow from exception to response."""
        # Arrange
        try:
            # Simulate a validation error
            raise ValidationProblem(
                detail="User registration failed",
                errors=[
                    "Email is required",
                    "Password must be at least 8 characters"
                ],
                invalid_fields=["email", "password"]
            )
        except ProblemException as e:
            # Act
            problem_detail = e.to_problem_detail()
            response = create_problem_response(problem_detail)

        # Assert
        assert response.status_code == 422
        assert response.headers["content-type"] == "application/problem+json"
        
        # Verify response body structure
        response_body = response.body
        assert b"Validation Error" in response_body
        assert b"User registration failed" in response_body