"""Common schemas used across the API."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PaginationRequest(BaseModel):
    """Common pagination request schema."""

    limit: int = Field(
        50, ge=1, le=100, description="Maximum number of results"
    )
    offset: int = Field(
        0, ge=0, description="Number of results to skip"
    )


class SortingRequest(BaseModel):
    """Common sorting request schema."""

    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field(
        "desc", pattern="^(asc|desc)$", description="Sort order"
    )


class PaginatedRequest(BaseModel):
    """Base class for paginated requests."""

    pagination: PaginationRequest = Field(
        default=PaginationRequest(),
        description="Pagination parameters",
    )
    sorting: SortingRequest = Field(
        default=SortingRequest(), description="Sorting parameters"
    )


class ListRequestBase(BaseModel):
    """Base schema for list requests without pagination."""

    pass


class GetRequestBase(BaseModel):
    """Base schema for get requests."""

    pass


class DeleteRequestBase(BaseModel):
    """Base schema for delete requests."""

    pass


class BaseSchema(BaseModel):
    """Base schema with common fields and configuration."""

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        use_enum_values = True


class PaginationParams(BaseModel):
    """Pagination parameters for requests."""

    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Page size limit")


class PaginationResponse(BaseModel):
    """Pagination information for responses."""

    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Page size limit")
    total_count: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")

    @property
    def has_next_page(self) -> bool:
        """Check if there is a next page."""
        return self.page < self.total_pages

    @property
    def has_prev_page(self) -> bool:
        """Check if there is a previous page."""
        return self.page > 1


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: dict[str, Any] | None = Field(None, description="Error details")


class SuccessResponse(BaseModel):
    """Standard success response schema."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Success message")
    data: dict[str, Any] | None = Field(None, description="Response data")


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SortOrder(str, Enum):
    """Sort order enumeration."""

    ASC = "asc"
    DESC = "desc"


class FilterParams(BaseModel):
    """Base filter parameters."""

    search: str | None = Field(None, description="Search query")
    tags: list[str] | None = Field(None, description="Filter by tags")
    created_after: datetime | None = Field(None, description="Created after date")
    start_date: datetime | None = Field(None, description="Start date for filtering")
    end_date: datetime | None = Field(None, description="End date for filtering")
    created_before: datetime | None = Field(None, description="Created before date")
    """Base schema for delete requests."""

    pass
