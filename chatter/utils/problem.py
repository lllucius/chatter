"""RFC 9457 Problem Details for HTTP APIs implementation.

This module provides utilities for creating RFC 9457 compliant error responses
for the Chatter API.
"""

from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from chatter.config import settings


class ProblemDetail(BaseModel):
    """RFC 9457 Problem Detail model."""

    type: str = Field(
        default="about:blank",
        description="A URI reference that identifies the problem type",
    )
    title: str = Field(
        description="A short, human-readable summary of the problem type"
    )
    status: int = Field(description="The HTTP status code")
    detail: str | None = Field(
        default=None,
        description="A human-readable explanation specific to this occurrence",
    )
    instance: str | None = Field(
        default=None,
        description="A URI reference that identifies the specific occurrence",
    )

    # Additional fields can be included for context
    class Config:
        extra = "allow"


class ProblemException(HTTPException):
    """Base exception class for RFC 9457 compliant problems."""

    def __init__(
        self,
        status_code: int,
        title: str,
        detail: str | None = None,
        type_suffix: str | None = None,
        instance: str | None = None,
        headers: dict[str, Any] | None = None,
        **extra_fields: Any,
    ) -> None:
        """Initialize a problem exception.

        Args:
            status_code: HTTP status code
            title: Human-readable summary of the problem type
            detail: Human-readable explanation specific to this occurrence
            type_suffix: Suffix to append to the base problem type URI
            instance: URI reference identifying the specific occurrence
            headers: Additional HTTP headers
            **extra_fields: Additional problem details
        """
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.type_suffix = type_suffix
        self.instance = instance
        self.extra_fields = extra_fields

        # Generate problem type URI
        if type_suffix:
            self.type_uri = (
                f"{settings.api_base_url}/problems/{type_suffix}"
            )
        else:
            self.type_uri = "about:blank"

        super().__init__(
            status_code=status_code, detail=detail, headers=headers
        )

    def to_problem_detail(
        self, request: Request | None = None
    ) -> ProblemDetail:
        """Convert to ProblemDetail model."""
        instance = self.instance
        if not instance and request:
            instance = str(request.url)

        problem_data = {
            "type": self.type_uri,
            "title": self.title,
            "status": self.status_code,
            "detail": self.detail,
            "instance": instance,
            **self.extra_fields,
        }

        # Remove None values
        problem_data = {
            k: v for k, v in problem_data.items() if v is not None
        }

        return ProblemDetail(**problem_data)

    def to_response(
        self, request: Request | None = None
    ) -> JSONResponse:
        """Convert to JSONResponse with RFC 9457 format."""
        problem = self.to_problem_detail(request)
        return JSONResponse(
            status_code=self.status_code,
            content=problem.model_dump(exclude_none=True),
            headers={
                "Content-Type": "application/problem+json",
                **dict(self.headers or {}),
            },
        )


# Common problem types
class BadRequestProblem(ProblemException):
    """Bad request problem."""

    def __init__(
        self,
        detail: str = "The request contains invalid data or parameters",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Bad Request",
            detail=detail,
            type_suffix="bad-request",
            **kwargs,
        )


class ValidationProblem(ProblemException):
    """Validation error problem."""

    def __init__(
        self,
        detail: str = "The request contains invalid data",
        validation_errors: list[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Validation Failed",
            detail=detail,
            type_suffix="validation-failed",
            errors=validation_errors or [],
            **kwargs,
        )


class AuthenticationProblem(ProblemException):
    """Authentication error problem."""

    def __init__(
        self, detail: str = "Authentication failed", **kwargs: Any
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Authentication Required",
            detail=detail,
            type_suffix="authentication-required",
            headers={"WWW-Authenticate": "Bearer"},
            **kwargs,
        )


class AuthorizationProblem(ProblemException):
    """Authorization error problem."""

    def __init__(
        self,
        detail: str = "Access denied",
        required_permissions: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Access Forbidden",
            detail=detail,
            type_suffix="access-forbidden",
            required_permissions=required_permissions or [],
            **kwargs,
        )


class NotFoundProblem(ProblemException):
    """Resource not found problem."""

    def __init__(
        self,
        detail: str = "The requested resource was not found",
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        extra_fields: dict[str, Any] = {}
        if resource_type:
            extra_fields["resourceType"] = resource_type
        if resource_id:
            extra_fields["resourceId"] = resource_id

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Resource Not Found",
            detail=detail,
            type_suffix="resource-not-found",
            **extra_fields,
            **kwargs,
        )


class ConflictProblem(ProblemException):
    """Resource conflict problem."""

    def __init__(
        self,
        detail: str = "The request could not be completed due to a conflict",
        conflicting_resource: str | None = None,
        **kwargs: Any,
    ) -> None:
        extra_fields: dict[str, Any] = {}
        if conflicting_resource:
            extra_fields["conflictingResource"] = conflicting_resource

        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Resource Conflict",
            detail=detail,
            type_suffix="resource-conflict",
            **extra_fields,
            **kwargs,
        )


class RateLimitProblem(ProblemException):
    """Rate limit exceeded problem."""

    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)

        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            title="Rate Limit Exceeded",
            detail=detail,
            type_suffix="rate-limit-exceeded",
            headers=headers,
            retryAfter=retry_after,
            **kwargs,
        )


class InternalServerProblem(ProblemException):
    """Internal server error problem."""

    def __init__(
        self,
        detail: str = "An internal server error occurred",
        error_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        extra_fields: dict[str, Any] = {}
        if error_id:
            extra_fields["errorId"] = error_id

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            detail=detail,
            type_suffix="internal-server-error",
            **extra_fields,
            **kwargs,
        )


def create_problem_response(
    status_code: int,
    title: str,
    detail: str | None = None,
    type_suffix: str | None = None,
    request: Request | None = None,
    **extra_fields: Any,
) -> JSONResponse:
    """Create a RFC 9457 compliant problem response.

    Args:
        status_code: HTTP status code
        title: Human-readable summary of the problem type
        detail: Human-readable explanation specific to this occurrence
        type_suffix: Suffix to append to the base problem type URI
        request: FastAPI request object for instance URI
        **extra_fields: Additional problem details

    Returns:
        JSONResponse with RFC 9457 format
    """
    problem = ProblemException(
        status_code=status_code,
        title=title,
        detail=detail,
        type_suffix=type_suffix,
        **extra_fields,
    )
    return problem.to_response(request)
