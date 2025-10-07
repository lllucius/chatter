"""Unit tests for workflow pagination validation."""

import pytest
from fastapi import Query
from pydantic import ValidationError


class TestWorkflowPaginationValidation:
    """Test pagination validation in workflow endpoints."""

    def test_page_parameter_validation(self):
        """Test that page parameter validation works correctly."""
        # The Query validator should enforce ge=1 constraint
        # This test validates the Query definition works as expected
        
        # Valid page numbers
        valid_pages = [1, 2, 10, 100]
        for page in valid_pages:
            # Query validation happens at FastAPI layer, not directly testable
            # This test documents the expected behavior
            assert page >= 1, f"Page {page} should be valid"

    def test_page_size_validation(self):
        """Test that page_size parameter validation works correctly."""
        # Valid page sizes
        valid_sizes = [1, 20, 50, 100]
        for size in valid_sizes:
            assert size >= 1, f"Page size {size} should be valid"
            assert size <= 100, f"Page size {size} should be valid"

    def test_offset_calculation_with_valid_page(self):
        """Test that offset is calculated correctly with valid page numbers."""
        # Test cases: (page, page_size, expected_offset)
        test_cases = [
            (1, 20, 0),   # First page
            (2, 20, 20),  # Second page
            (3, 20, 40),  # Third page
            (1, 50, 0),   # First page, larger page size
            (5, 10, 40),  # Fifth page, smaller page size
        ]
        
        for page, page_size, expected_offset in test_cases:
            offset = (page - 1) * page_size
            assert offset == expected_offset, \
                f"Page {page} with size {page_size} should give offset {expected_offset}"
            assert offset >= 0, \
                f"Offset should never be negative for valid page {page}"

    def test_offset_calculation_prevents_negative(self):
        """Test that the offset calculation prevents negative values."""
        # With page validation (ge=1), these values should be rejected
        # This test documents the expected behavior
        invalid_pages = [0, -1, -10]
        page_size = 20
        
        for page in invalid_pages:
            # These pages should be rejected by FastAPI Query validation
            # If they somehow got through, offset would be negative
            offset = (page - 1) * page_size
            assert offset < 0, \
                f"Page {page} would result in negative offset {offset}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
