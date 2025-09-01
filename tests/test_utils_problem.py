"""Tests for problem utility functions."""

import json
from unittest.mock import Mock

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse

from chatter.utils.problem import (
    ProblemException,
    BadRequestProblem,
    UnauthorizedProblem,
    ForbiddenProblem,
    NotFoundProblem,
    ConflictProblem,
    ValidationProblem,
    InternalServerProblem,
    ServiceUnavailableProblem,
    RateLimitProblem,
)


class TestProblemException:
    """Test base ProblemException class."""

    def test_problem_exception_init_minimal(self):
        """Test ProblemException with minimal parameters."""
        exc = ProblemException(
            status_code=400,
            title="Bad Request",
            detail="Invalid input"
        )
        
        assert exc.status_code == 400
        assert exc.title == "Bad Request"
        assert exc.detail == "Invalid input"
        assert exc.type == "about:blank"
        assert exc.instance is None
        assert exc.extra == {}

    def test_problem_exception_init_full(self):
        """Test ProblemException with all parameters."""
        extra_data = {"error_code": "INVALID_FORMAT", "field": "email"}
        
        exc = ProblemException(
            status_code=422,
            title="Validation Error",
            detail="Email format is invalid",
            type="https://api.example.com/problems/validation",
            instance="/users/123",
            extra=extra_data
        )
        
        assert exc.status_code == 422
        assert exc.title == "Validation Error"
        assert exc.detail == "Email format is invalid"
        assert exc.type == "https://api.example.com/problems/validation"
        assert exc.instance == "/users/123"
        assert exc.extra == extra_data

    def test_problem_exception_str(self):
        """Test string representation of ProblemException."""
        exc = ProblemException(
            status_code=404,
            title="Not Found",
            detail="Resource not found"
        )
        
        str_repr = str(exc)
        assert "404" in str_repr
        assert "Not Found" in str_repr

    def test_problem_exception_to_response(self):
        """Test converting ProblemException to HTTP response."""
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/test"
        
        exc = ProblemException(
            status_code=400,
            title="Bad Request",
            detail="Invalid parameter",
            extra={"parameter": "user_id"}
        )
        
        response = exc.to_response(request)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        
        # Check response body
        content = json.loads(response.body.decode())
        assert content["type"] == "about:blank"
        assert content["title"] == "Bad Request"
        assert content["detail"] == "Invalid parameter"
        assert content["status"] == 400
        assert content["instance"] == "/api/test"
        assert content["parameter"] == "user_id"

    def test_problem_exception_to_response_with_custom_type(self):
        """Test response generation with custom problem type."""
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/users"
        
        exc = ProblemException(
            status_code=409,
            title="Conflict",
            detail="User already exists",
            type="https://api.example.com/problems/user-exists"
        )
        
        response = exc.to_response(request)
        content = json.loads(response.body.decode())
        
        assert content["type"] == "https://api.example.com/problems/user-exists"

    def test_problem_exception_headers(self):
        """Test that response has correct headers."""
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/test"
        
        exc = ProblemException(
            status_code=400,
            title="Bad Request",
            detail="Test error"
        )
        
        response = exc.to_response(request)
        
        assert response.headers["content-type"] == "application/problem+json"


class TestBadRequestProblem:
    """Test BadRequestProblem class."""

    def test_bad_request_problem_defaults(self):
        """Test BadRequestProblem with default values."""
        problem = BadRequestProblem()
        
        assert problem.status_code == 400
        assert problem.title == "Bad Request"
        assert "request is malformed" in problem.detail

    def test_bad_request_problem_custom_detail(self):
        """Test BadRequestProblem with custom detail."""
        custom_detail = "Missing required parameter"
        problem = BadRequestProblem(detail=custom_detail)
        
        assert problem.detail == custom_detail
        assert problem.status_code == 400

    def test_bad_request_problem_with_extra(self):
        """Test BadRequestProblem with extra data."""
        extra = {"missing_fields": ["name", "email"]}
        problem = BadRequestProblem(
            detail="Required fields missing",
            extra=extra
        )
        
        assert problem.extra == extra


class TestUnauthorizedProblem:
    """Test UnauthorizedProblem class."""

    def test_unauthorized_problem_defaults(self):
        """Test UnauthorizedProblem with default values."""
        problem = UnauthorizedProblem()
        
        assert problem.status_code == 401
        assert problem.title == "Unauthorized"
        assert "authentication" in problem.detail.lower()

    def test_unauthorized_problem_custom_detail(self):
        """Test UnauthorizedProblem with custom detail."""
        custom_detail = "Invalid API key"
        problem = UnauthorizedProblem(detail=custom_detail)
        
        assert problem.detail == custom_detail


class TestForbiddenProblem:
    """Test ForbiddenProblem class."""

    def test_forbidden_problem_defaults(self):
        """Test ForbiddenProblem with default values."""
        problem = ForbiddenProblem()
        
        assert problem.status_code == 403
        assert problem.title == "Forbidden"
        assert "access" in problem.detail.lower()

    def test_forbidden_problem_with_resource(self):
        """Test ForbiddenProblem with specific resource."""
        problem = ForbiddenProblem(
            detail="Access denied to user management",
            extra={"resource": "users", "action": "delete"}
        )
        
        assert problem.extra["resource"] == "users"
        assert problem.extra["action"] == "delete"


class TestNotFoundProblem:
    """Test NotFoundProblem class."""

    def test_not_found_problem_defaults(self):
        """Test NotFoundProblem with default values."""
        problem = NotFoundProblem()
        
        assert problem.status_code == 404
        assert problem.title == "Not Found"
        assert "not found" in problem.detail.lower()

    def test_not_found_problem_with_resource(self):
        """Test NotFoundProblem with specific resource."""
        problem = NotFoundProblem(
            detail="User with ID 123 not found",
            extra={"resource_type": "user", "resource_id": "123"}
        )
        
        assert problem.extra["resource_type"] == "user"
        assert problem.extra["resource_id"] == "123"


class TestConflictProblem:
    """Test ConflictProblem class."""

    def test_conflict_problem_defaults(self):
        """Test ConflictProblem with default values."""
        problem = ConflictProblem()
        
        assert problem.status_code == 409
        assert problem.title == "Conflict"
        assert "conflict" in problem.detail.lower()

    def test_conflict_problem_with_conflicting_resource(self):
        """Test ConflictProblem with conflicting resource info."""
        problem = ConflictProblem(
            detail="Email address already in use",
            extra={"conflicting_field": "email", "value": "user@example.com"}
        )
        
        assert problem.extra["conflicting_field"] == "email"


class TestValidationProblem:
    """Test ValidationProblem class."""

    def test_validation_problem_defaults(self):
        """Test ValidationProblem with default values."""
        problem = ValidationProblem()
        
        assert problem.status_code == 422
        assert problem.title == "Validation Error"
        assert "validation" in problem.detail.lower()

    def test_validation_problem_with_errors(self):
        """Test ValidationProblem with validation errors."""
        validation_errors = [
            {
                "loc": ["body", "email"],
                "msg": "field required",
                "type": "value_error.missing"
            },
            {
                "loc": ["body", "age"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt"
            }
        ]
        
        problem = ValidationProblem(
            detail="Request validation failed",
            validation_errors=validation_errors
        )
        
        assert problem.extra["validation_errors"] == validation_errors

    def test_validation_problem_response_format(self):
        """Test ValidationProblem response includes validation errors."""
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/users"
        
        validation_errors = [
            {
                "loc": ["body", "name"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
        
        problem = ValidationProblem(validation_errors=validation_errors)
        response = problem.to_response(request)
        content = json.loads(response.body.decode())
        
        assert "validation_errors" in content
        assert content["validation_errors"] == validation_errors


class TestInternalServerProblem:
    """Test InternalServerProblem class."""

    def test_internal_server_problem_defaults(self):
        """Test InternalServerProblem with default values."""
        problem = InternalServerProblem()
        
        assert problem.status_code == 500
        assert problem.title == "Internal Server Error"
        assert "server error" in problem.detail.lower()

    def test_internal_server_problem_with_error_details(self):
        """Test InternalServerProblem with error details."""
        problem = InternalServerProblem(
            detail="Database connection failed",
            error_type="DatabaseError",
            error_traceback="Traceback: ..."
        )
        
        assert problem.extra["error_type"] == "DatabaseError"
        assert problem.extra["error_traceback"] == "Traceback: ..."

    def test_internal_server_problem_production_mode(self):
        """Test InternalServerProblem in production (no traceback)."""
        problem = InternalServerProblem(
            detail="An error occurred",
            error_type="ValueError"
            # No traceback in production
        )
        
        assert problem.extra["error_type"] == "ValueError"
        assert "error_traceback" not in problem.extra


class TestServiceUnavailableProblem:
    """Test ServiceUnavailableProblem class."""

    def test_service_unavailable_problem_defaults(self):
        """Test ServiceUnavailableProblem with default values."""
        problem = ServiceUnavailableProblem()
        
        assert problem.status_code == 503
        assert problem.title == "Service Unavailable"
        assert "temporarily unavailable" in problem.detail.lower()

    def test_service_unavailable_problem_with_retry_after(self):
        """Test ServiceUnavailableProblem with retry information."""
        problem = ServiceUnavailableProblem(
            detail="System maintenance in progress",
            extra={"retry_after": 300, "maintenance_window": "2024-01-01 02:00-04:00"}
        )
        
        assert problem.extra["retry_after"] == 300
        assert "maintenance_window" in problem.extra


class TestRateLimitProblem:
    """Test RateLimitProblem class."""

    def test_rate_limit_problem_defaults(self):
        """Test RateLimitProblem with default values."""
        problem = RateLimitProblem()
        
        assert problem.status_code == 429
        assert problem.title == "Too Many Requests"
        assert "rate limit" in problem.detail.lower()

    def test_rate_limit_problem_with_limit_info(self):
        """Test RateLimitProblem with rate limit details."""
        problem = RateLimitProblem(
            detail="API rate limit exceeded",
            extra={
                "limit": 100,
                "window": 3600,
                "retry_after": 60,
                "requests_made": 101
            }
        )
        
        assert problem.extra["limit"] == 100
        assert problem.extra["window"] == 3600
        assert problem.extra["retry_after"] == 60
        assert problem.extra["requests_made"] == 101

    def test_rate_limit_problem_response_headers(self):
        """Test that rate limit problem can include special headers."""
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/chat"
        
        problem = RateLimitProblem(
            extra={"retry_after": 120}
        )
        
        response = problem.to_response(request)
        content = json.loads(response.body.decode())
        
        assert content["retry_after"] == 120


class TestProblemResponseFormat:
    """Test RFC 9457 Problem Details compliance."""

    def test_response_content_type(self):
        """Test that all problems use correct content type."""
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/test"
        
        problems = [
            BadRequestProblem(),
            UnauthorizedProblem(),
            ForbiddenProblem(),
            NotFoundProblem(),
            ConflictProblem(),
            ValidationProblem(),
            InternalServerProblem(),
            ServiceUnavailableProblem(),
            RateLimitProblem()
        ]
        
        for problem in problems:
            response = problem.to_response(request)
            assert response.headers["content-type"] == "application/problem+json"

    def test_required_fields_present(self):
        """Test that all required RFC 9457 fields are present."""
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/test"
        
        problem = BadRequestProblem(detail="Test error")
        response = problem.to_response(request)
        content = json.loads(response.body.decode())
        
        # Required fields per RFC 9457
        assert "type" in content
        assert "title" in content
        assert "status" in content
        assert "detail" in content
        assert "instance" in content

    def test_optional_fields_when_provided(self):
        """Test that optional fields are included when provided."""
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/test"
        
        extra_data = {"correlation_id": "test-123", "timestamp": "2024-01-01T12:00:00Z"}
        
        problem = BadRequestProblem(
            detail="Test error",
            extra=extra_data
        )
        
        response = problem.to_response(request)
        content = json.loads(response.body.decode())
        
        # Extra fields should be included at top level
        assert content["correlation_id"] == "test-123"
        assert content["timestamp"] == "2024-01-01T12:00:00Z"

    def test_instance_field_from_request_path(self):
        """Test that instance field is set from request path."""
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/users/123"
        
        problem = NotFoundProblem()
        response = problem.to_response(request)
        content = json.loads(response.body.decode())
        
        assert content["instance"] == "/api/users/123"

    def test_status_field_matches_http_status(self):
        """Test that status field matches HTTP status code."""
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/test"
        
        test_cases = [
            (BadRequestProblem(), 400),
            (UnauthorizedProblem(), 401),
            (ForbiddenProblem(), 403),
            (NotFoundProblem(), 404),
            (ConflictProblem(), 409),
            (ValidationProblem(), 422),
            (InternalServerProblem(), 500),
            (ServiceUnavailableProblem(), 503),
            (RateLimitProblem(), 429)
        ]
        
        for problem, expected_status in test_cases:
            response = problem.to_response(request)
            content = json.loads(response.body.decode())
            
            assert response.status_code == expected_status
            assert content["status"] == expected_status