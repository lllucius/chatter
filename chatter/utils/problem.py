"""RFC 9457 Problem Details for HTTP APIs implementation.

This module provides utilities for creating RFC 9457 compliant error responses
for the Chatter API.
"""

from typing import Any, Dict, Optional
from urllib.parse import urljoin

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from chatter.config import settings


class ProblemDetail(BaseModel):
    """RFC 9457 Problem Detail model."""
    
    type: str = Field(
        default="about:blank",
        description="A URI reference that identifies the problem type"
    )
    title: str = Field(
        description="A short, human-readable summary of the problem type"
    )
    status: int = Field(
        description="The HTTP status code"
    )
    detail: Optional[str] = Field(
        default=None,
        description="A human-readable explanation specific to this occurrence"
    )
    instance: Optional[str] = Field(
        default=None,
        description="A URI reference that identifies the specific occurrence"
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
        detail: Optional[str] = None,
        type_suffix: Optional[str] = None,
        instance: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
        **extra_fields: Any
    ):
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
            self.type_uri = f"{settings.api_base_url}/problems/{type_suffix}"
        else:
            self.type_uri = "about:blank"
        
        super().__init__(status_code=status_code, detail=detail, headers=headers)
    
    def to_problem_detail(self, request: Optional[Request] = None) -> ProblemDetail:
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
            **self.extra_fields
        }
        
        # Remove None values
        problem_data = {k: v for k, v in problem_data.items() if v is not None}
        
        return ProblemDetail(**problem_data)
    
    def to_response(self, request: Optional[Request] = None) -> JSONResponse:
        """Convert to JSONResponse with RFC 9457 format."""
        problem = self.to_problem_detail(request)
        return JSONResponse(
            status_code=self.status_code,
            content=problem.model_dump(exclude_none=True),
            headers={
                "Content-Type": "application/problem+json",
                **(self.headers or {})
            }
        )


# Common problem types
class ValidationProblem(ProblemException):
    """Validation error problem."""
    
    def __init__(
        self,
        detail: str = "The request contains invalid data",
        validation_errors: Optional[list] = None,
        **kwargs
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Validation Failed",
            detail=detail,
            type_suffix="validation-failed",
            errors=validation_errors or [],
            **kwargs
        )


class AuthenticationProblem(ProblemException):
    """Authentication error problem."""
    
    def __init__(
        self,
        detail: str = "Authentication failed",
        **kwargs
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Authentication Required",
            detail=detail,
            type_suffix="authentication-required",
            headers={"WWW-Authenticate": "Bearer"},
            **kwargs
        )


class AuthorizationProblem(ProblemException):
    """Authorization error problem."""
    
    def __init__(
        self,
        detail: str = "Access denied",
        required_permissions: Optional[list] = None,
        **kwargs
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Access Forbidden",
            detail=detail,
            type_suffix="access-forbidden",
            required_permissions=required_permissions or [],
            **kwargs
        )


class NotFoundProblem(ProblemException):
    """Resource not found problem."""
    
    def __init__(
        self,
        detail: str = "The requested resource was not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        extra_fields = {}
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
            **kwargs
        )


class ConflictProblem(ProblemException):
    """Resource conflict problem."""
    
    def __init__(
        self,
        detail: str = "The request could not be completed due to a conflict",
        conflicting_resource: Optional[str] = None,
        **kwargs
    ):
        extra_fields = {}
        if conflicting_resource:
            extra_fields["conflictingResource"] = conflicting_resource
        
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Resource Conflict",
            detail=detail,
            type_suffix="resource-conflict",
            **extra_fields,
            **kwargs
        )


class RateLimitProblem(ProblemException):
    """Rate limit exceeded problem."""
    
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
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
            **kwargs
        )


class InternalServerProblem(ProblemException):
    """Internal server error problem."""
    
    def __init__(
        self,
        detail: str = "An internal server error occurred",
        error_id: Optional[str] = None,
        **kwargs
    ):
        extra_fields = {}
        if error_id:
            extra_fields["errorId"] = error_id
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            detail=detail,
            type_suffix="internal-server-error",
            **extra_fields,
            **kwargs
        )


def create_problem_response(
    status_code: int,
    title: str,
    detail: Optional[str] = None,
    type_suffix: Optional[str] = None,
    request: Optional[Request] = None,
    **extra_fields: Any
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
        **extra_fields
    )
    return problem.to_response(request)


def convert_http_exception(exc: HTTPException, request: Optional[Request] = None) -> JSONResponse:
    """Convert a standard HTTPException to RFC 9457 format.
    
    Args:
        exc: HTTPException to convert
        request: FastAPI request object for instance URI
    
    Returns:
        JSONResponse with RFC 9457 format
    """
    # Map common status codes to appropriate titles
    title_mapping = {
        400: "Bad Request",
        401: "Authentication Required",
        403: "Access Forbidden",
        404: "Resource Not Found",
        405: "Method Not Allowed",
        409: "Resource Conflict",
        422: "Validation Failed",
        429: "Rate Limit Exceeded",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
    }
    
    title = title_mapping.get(exc.status_code, "HTTP Error")
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    
    # Determine type suffix based on status code
    type_suffix_mapping = {
        400: "bad-request",
        401: "authentication-required",
        403: "access-forbidden", 
        404: "resource-not-found",
        405: "method-not-allowed",
        409: "resource-conflict",
        422: "validation-failed",
        429: "rate-limit-exceeded",
        500: "internal-server-error",
    }
    
    type_suffix = type_suffix_mapping.get(exc.status_code)
    
    problem = ProblemException(
        status_code=exc.status_code,
        title=title,
        detail=detail,
        type_suffix=type_suffix,
        headers=exc.headers
    )
    
    return problem.to_response(request)