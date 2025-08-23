"""Common schemas used across the API."""

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
        default_factory=PaginationRequest,
        description="Pagination parameters",
    )
    sorting: SortingRequest = Field(
        default_factory=SortingRequest, description="Sorting parameters"
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
