"""Standardized API response utilities."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from chatter.config import settings
from chatter.utils.correlation import get_correlation_id


class ResponseMetadata(BaseModel):
    """Standard metadata for API responses."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str | None = Field(default=None)
    version: str = Field(default=settings.api_version)
    request_id: str | None = Field(default=None)


class StandardResponse(BaseModel):
    """Standard API response envelope."""

    success: bool = Field(description="Whether the request was successful")
    data: Any | None = Field(default=None, description="Response data")
    message: str | None = Field(default=None, description="Human-readable message")
    errors: list[str] | None = Field(default=None, description="List of error messages")
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)

    def model_post_init(self, __context: Any) -> None:
        """Set correlation ID from context after initialization."""
        if self.metadata.correlation_id is None:
            self.metadata.correlation_id = get_correlation_id()


class PaginatedResponse(StandardResponse):
    """Standard paginated response envelope."""

    pagination: dict[str, Any] | None = Field(
        default=None,
        description="Pagination metadata"
    )


def create_success_response(
    data: Any = None,
    message: str | None = None,
    pagination: dict[str, Any] | None = None
) -> StandardResponse | PaginatedResponse:
    """Create a standardized success response.
    
    Args:
        data: The response data
        message: Optional success message
        pagination: Optional pagination metadata
        
    Returns:
        Standardized success response
    """
    if pagination:
        return PaginatedResponse(
            success=True,
            data=data,
            message=message,
            pagination=pagination
        )

    return StandardResponse(
        success=True,
        data=data,
        message=message
    )


def create_error_response(
    message: str,
    errors: list[str] | None = None,
    data: Any = None
) -> StandardResponse:
    """Create a standardized error response.
    
    Args:
        message: Primary error message
        errors: List of detailed error messages
        data: Optional error data
        
    Returns:
        Standardized error response
    """
    return StandardResponse(
        success=False,
        data=data,
        message=message,
        errors=errors or []
    )


def wrap_response(response_data: Any, message: str | None = None) -> StandardResponse:
    """Wrap existing response data in standard envelope.
    
    Args:
        response_data: Existing response data to wrap
        message: Optional message
        
    Returns:
        Wrapped response in standard format
    """
    return StandardResponse(
        success=True,
        data=response_data,
        message=message
    )
