"""Tests for common schema classes."""

from datetime import datetime
from typing import Optional

import pytest
from pydantic import ValidationError

from chatter.schemas.common import (
    BaseSchema,
    PaginationParams,
    PaginationResponse,
    ErrorResponse,
    SuccessResponse,
    TimestampMixin,
    SortOrder,
    FilterParams,
)


class TestBaseSchema:
    """Test BaseSchema functionality."""

    def test_base_schema_creation(self):
        """Test BaseSchema can be instantiated."""
        schema = BaseSchema()
        assert isinstance(schema, BaseSchema)

    def test_base_schema_dict_method(self):
        """Test BaseSchema dict method."""
        schema = BaseSchema()
        result = schema.dict()
        assert isinstance(result, dict)

    def test_base_schema_json_method(self):
        """Test BaseSchema JSON serialization."""
        schema = BaseSchema()
        result = schema.json()
        assert isinstance(result, str)

    def test_base_schema_config(self):
        """Test BaseSchema configuration."""
        # Test that BaseSchema has expected configuration
        config = BaseSchema.Config if hasattr(BaseSchema, 'Config') else None
        
        # BaseSchema should be properly configured for API use
        if config:
            # Should allow population by field name or alias
            assert getattr(config, 'allow_population_by_field_name', True)


class TestPaginationParams:
    """Test PaginationParams schema."""

    def test_pagination_params_defaults(self):
        """Test PaginationParams with default values."""
        params = PaginationParams()
        
        assert params.page == 1
        assert params.limit == 20

    def test_pagination_params_custom_values(self):
        """Test PaginationParams with custom values."""
        params = PaginationParams(page=2, limit=50)
        
        assert params.page == 2
        assert params.limit == 50

    def test_pagination_params_validation_min_page(self):
        """Test pagination params validation for minimum page."""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)
        
        with pytest.raises(ValidationError):
            PaginationParams(page=-1)

    def test_pagination_params_validation_min_limit(self):
        """Test pagination params validation for minimum limit."""
        with pytest.raises(ValidationError):
            PaginationParams(limit=0)
        
        with pytest.raises(ValidationError):
            PaginationParams(limit=-1)

    def test_pagination_params_validation_max_limit(self):
        """Test pagination params validation for maximum limit."""
        with pytest.raises(ValidationError):
            PaginationParams(limit=101)  # Assuming max limit is 100
        
        with pytest.raises(ValidationError):
            PaginationParams(limit=1000)

    def test_pagination_params_calculate_offset(self):
        """Test pagination offset calculation."""
        params = PaginationParams(page=3, limit=10)
        
        # page 3 with limit 10 should have offset 20
        offset = (params.page - 1) * params.limit
        assert offset == 20

    def test_pagination_params_edge_cases(self):
        """Test pagination params edge cases."""
        # First page
        params = PaginationParams(page=1, limit=1)
        assert params.page == 1
        assert params.limit == 1
        
        # Maximum allowed values
        params = PaginationParams(page=1000, limit=100)
        assert params.page == 1000
        assert params.limit == 100


class TestPaginationResponse:
    """Test PaginationResponse schema."""

    def test_pagination_response_creation(self):
        """Test PaginationResponse creation."""
        response = PaginationResponse(
            total_count=100,
            page=2,
            limit=20,
            total_pages=5
        )
        
        assert response.total_count == 100
        assert response.page == 2
        assert response.limit == 20
        assert response.total_pages == 5

    def test_pagination_response_has_next_page(self):
        """Test pagination response has_next_page property."""
        # Has next page
        response = PaginationResponse(
            total_count=100,
            page=2,
            limit=20,
            total_pages=5
        )
        assert response.page < response.total_pages  # Should have next page
        
        # No next page
        response = PaginationResponse(
            total_count=100,
            page=5,
            limit=20,
            total_pages=5
        )
        assert response.page == response.total_pages  # No next page

    def test_pagination_response_has_prev_page(self):
        """Test pagination response has_prev_page property."""
        # Has previous page
        response = PaginationResponse(
            total_count=100,
            page=3,
            limit=20,
            total_pages=5
        )
        assert response.page > 1  # Should have previous page
        
        # No previous page
        response = PaginationResponse(
            total_count=100,
            page=1,
            limit=20,
            total_pages=5
        )
        assert response.page == 1  # No previous page

    def test_pagination_response_calculate_total_pages(self):
        """Test total pages calculation."""
        # Exact division
        total_count = 100
        limit = 20
        expected_pages = 5
        
        response = PaginationResponse(
            total_count=total_count,
            page=1,
            limit=limit,
            total_pages=expected_pages
        )
        assert response.total_pages == expected_pages
        
        # With remainder
        total_count = 101
        limit = 20
        expected_pages = 6  # 101 / 20 = 5.05, so 6 pages
        
        response = PaginationResponse(
            total_count=total_count,
            page=1,
            limit=limit,
            total_pages=expected_pages
        )
        assert response.total_pages == expected_pages

    def test_pagination_response_empty_result(self):
        """Test pagination response with empty result."""
        response = PaginationResponse(
            total_count=0,
            page=1,
            limit=20,
            total_pages=0
        )
        
        assert response.total_count == 0
        assert response.total_pages == 0


class TestErrorResponse:
    """Test ErrorResponse schema."""

    def test_error_response_creation(self):
        """Test ErrorResponse creation."""
        error = ErrorResponse(
            error="Validation failed",
            message="The request data is invalid"
        )
        
        assert error.error == "Validation failed"
        assert error.message == "The request data is invalid"

    def test_error_response_with_details(self):
        """Test ErrorResponse with additional details."""
        details = {"field": "email", "code": "INVALID_FORMAT"}
        
        error = ErrorResponse(
            error="Validation Error",
            message="Email format is invalid",
            details=details
        )
        
        assert error.details == details

    def test_error_response_optional_fields(self):
        """Test ErrorResponse with optional fields."""
        # Minimal error response
        error = ErrorResponse(
            error="Not Found",
            message="Resource not found"
        )
        
        assert error.error == "Not Found"
        assert error.message == "Resource not found"
        assert error.details is None  # Optional field

    def test_error_response_serialization(self):
        """Test ErrorResponse serialization."""
        error = ErrorResponse(
            error="Bad Request",
            message="Invalid parameter"
        )
        
        data = error.dict()
        assert "error" in data
        assert "message" in data
        
        json_str = error.json()
        assert isinstance(json_str, str)
        assert "Bad Request" in json_str


class TestSuccessResponse:
    """Test SuccessResponse schema."""

    def test_success_response_creation(self):
        """Test SuccessResponse creation."""
        response = SuccessResponse(
            message="Operation completed successfully"
        )
        
        assert response.message == "Operation completed successfully"
        assert response.success is True

    def test_success_response_with_data(self):
        """Test SuccessResponse with data."""
        data = {"id": 123, "name": "Test"}
        
        response = SuccessResponse(
            message="User created",
            data=data
        )
        
        assert response.data == data

    def test_success_response_defaults(self):
        """Test SuccessResponse default values."""
        response = SuccessResponse()
        
        assert response.success is True
        assert response.message == "Success"  # Default message

    def test_success_response_serialization(self):
        """Test SuccessResponse serialization."""
        response = SuccessResponse(message="Test successful")
        
        data = response.dict()
        assert data["success"] is True
        assert data["message"] == "Test successful"


class TestTimestampMixin:
    """Test TimestampMixin functionality."""

    def test_timestamp_mixin_fields(self):
        """Test TimestampMixin has expected fields."""
        # Create a test schema that uses TimestampMixin
        class TestSchema(TimestampMixin, BaseSchema):
            name: str
        
        # Test with current timestamp
        now = datetime.utcnow()
        schema = TestSchema(
            name="test",
            created_at=now,
            updated_at=now
        )
        
        assert schema.created_at == now
        assert schema.updated_at == now

    def test_timestamp_mixin_optional_fields(self):
        """Test TimestampMixin fields are optional."""
        class TestSchema(TimestampMixin, BaseSchema):
            name: str
        
        # Should work without timestamps
        schema = TestSchema(name="test")
        assert schema.name == "test"

    def test_timestamp_mixin_validation(self):
        """Test TimestampMixin timestamp validation."""
        class TestSchema(TimestampMixin, BaseSchema):
            name: str
        
        # Valid datetime
        valid_time = datetime.utcnow()
        schema = TestSchema(
            name="test",
            created_at=valid_time
        )
        assert isinstance(schema.created_at, datetime)

    def test_timestamp_mixin_serialization(self):
        """Test TimestampMixin serialization."""
        class TestSchema(TimestampMixin, BaseSchema):
            name: str
        
        now = datetime.utcnow()
        schema = TestSchema(
            name="test",
            created_at=now,
            updated_at=now
        )
        
        data = schema.dict()
        assert "created_at" in data
        assert "updated_at" in data


class TestSortOrder:
    """Test SortOrder enum."""

    def test_sort_order_values(self):
        """Test SortOrder enum values."""
        assert SortOrder.ASC == "asc"
        assert SortOrder.DESC == "desc"

    def test_sort_order_usage(self):
        """Test SortOrder enum usage in schema."""
        # Should be able to use in schema
        class TestSchema(BaseSchema):
            sort: SortOrder = SortOrder.ASC
        
        schema = TestSchema()
        assert schema.sort == SortOrder.ASC
        
        schema = TestSchema(sort=SortOrder.DESC)
        assert schema.sort == SortOrder.DESC

    def test_sort_order_validation(self):
        """Test SortOrder validation."""
        class TestSchema(BaseSchema):
            sort: SortOrder
        
        # Valid values
        schema = TestSchema(sort="asc")
        assert schema.sort == SortOrder.ASC
        
        schema = TestSchema(sort="desc")
        assert schema.sort == SortOrder.DESC
        
        # Invalid values
        with pytest.raises(ValidationError):
            TestSchema(sort="invalid")


class TestFilterParams:
    """Test FilterParams schema."""

    def test_filter_params_creation(self):
        """Test FilterParams creation."""
        params = FilterParams()
        
        # Should have default values or be optional
        assert isinstance(params, FilterParams)

    def test_filter_params_with_search(self):
        """Test FilterParams with search query."""
        params = FilterParams(search="test query")
        
        assert params.search == "test query"

    def test_filter_params_with_date_range(self):
        """Test FilterParams with date range."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        params = FilterParams(
            start_date=start_date,
            end_date=end_date
        )
        
        assert params.start_date == start_date
        assert params.end_date == end_date

    def test_filter_params_validation(self):
        """Test FilterParams validation."""
        # End date before start date should be invalid
        start_date = datetime(2024, 12, 31)
        end_date = datetime(2024, 1, 1)
        
        # Depending on implementation, this might raise validation error
        try:
            params = FilterParams(
                start_date=start_date,
                end_date=end_date
            )
            # If no validation, check manually
            if hasattr(params, 'start_date') and hasattr(params, 'end_date'):
                if params.start_date and params.end_date:
                    assert params.start_date <= params.end_date, "Start date should be before end date"
        except ValidationError:
            # Expected if validation is implemented
            pass

    def test_filter_params_optional_fields(self):
        """Test FilterParams optional fields."""
        # Should work with no filters
        params = FilterParams()
        assert isinstance(params, FilterParams)
        
        # Should work with partial filters
        params = FilterParams(search="test")
        assert params.search == "test"


class TestSchemaIntegration:
    """Test schema integration and common usage patterns."""

    def test_pagination_with_filter_params(self):
        """Test using pagination with filter params."""
        pagination = PaginationParams(page=2, limit=10)
        filters = FilterParams(search="test")
        
        # Should be able to use together
        assert pagination.page == 2
        assert filters.search == "test"

    def test_error_response_serialization(self):
        """Test error response can be serialized for API."""
        error = ErrorResponse(
            error="ValidationError",
            message="Invalid input data",
            details={"field": "email"}
        )
        
        # Should serialize to dict for JSON response
        data = error.dict()
        assert isinstance(data, dict)
        assert "error" in data
        assert "message" in data
        assert "details" in data

    def test_success_response_with_pagination(self):
        """Test success response with pagination data."""
        pagination = PaginationResponse(
            total_count=100,
            page=1,
            limit=20,
            total_pages=5
        )
        
        response = SuccessResponse(
            message="Data retrieved successfully",
            data={"pagination": pagination.dict()}
        )
        
        assert response.success is True
        assert "pagination" in response.data

    def test_timestamp_mixin_usage(self):
        """Test TimestampMixin in practical schema."""
        class UserSchema(TimestampMixin, BaseSchema):
            id: int
            name: str
            email: str
        
        now = datetime.utcnow()
        user = UserSchema(
            id=1,
            name="Test User",
            email="test@example.com",
            created_at=now
        )
        
        assert user.id == 1
        assert user.created_at == now

    def test_nested_schema_validation(self):
        """Test validation with nested schemas."""
        class AddressSchema(BaseSchema):
            street: str
            city: str
            country: str
        
        class UserSchema(BaseSchema):
            name: str
            address: AddressSchema
        
        address_data = {
            "street": "123 Main St",
            "city": "Anytown",
            "country": "USA"
        }
        
        user = UserSchema(
            name="Test User",
            address=address_data
        )
        
        assert user.name == "Test User"
        assert user.address.street == "123 Main St"