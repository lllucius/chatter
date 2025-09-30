"""Unit tests for API validation functions that don't require database."""

import pytest
from ulid import ULID

from chatter.utils.problem import BadRequestProblem


class TestULIDValidation:
    """Test ULID validation functionality."""

    def test_valid_ulid(self):
        """Test validation of valid ULIDs."""
        from chatter.api.dependencies import ValidatedULID

        valid_ulid = str(ULID())
        result = ValidatedULID.validate(valid_ulid)
        assert result == valid_ulid

    def test_error_case_ulid(self):
        """Test validation of the specific ULID from the error case."""
        from chatter.api.dependencies import ValidatedULID

        error_ulid = "01K4NFEZK5027EEC011J336R5Z"
        result = ValidatedULID.validate(error_ulid)
        assert result == error_ulid

    def test_invalid_ulid_format(self):
        """Test validation fails for invalid ULID format."""
        from chatter.api.dependencies import ValidatedULID

        with pytest.raises(BadRequestProblem) as exc_info:
            ValidatedULID.validate("not-a-ulid")

        assert "Invalid ULID format" in str(exc_info.value.detail)
        # Updated to match new detailed error messages
        assert "must be exactly 26 characters" in str(
            exc_info.value.detail
        )

    def test_empty_ulid(self):
        """Test validation fails for empty ULID."""
        from chatter.api.dependencies import ValidatedULID

        with pytest.raises(BadRequestProblem):
            ValidatedULID.validate("")

    def test_none_ulid(self):
        """Test validation fails for None ULID."""
        from chatter.api.dependencies import ValidatedULID

        with pytest.raises((BadRequestProblem, TypeError)):
            ValidatedULID.validate(None)

    def test_malformed_ulid(self):
        """Test validation fails for malformed ULIDs."""
        from chatter.api.dependencies import ValidatedULID

        malformed_ulids = [
            "123e4567-e89b-12d3-a456-426614174000",  # UUID format
            "01K4NFEZK5027EEC011J336R5",  # Missing character
            "01K4NFEZK5027EEC011J336R5!!",  # Invalid characters
            "not-a-ulid-at-all",  # Completely invalid
            "123-456-789",  # Wrong format
        ]

        for malformed_ulid in malformed_ulids:
            with pytest.raises(BadRequestProblem):
                ValidatedULID.validate(malformed_ulid)

    def test_improved_error_messages(self):
        """Test that ULID validation provides detailed error messages."""
        from chatter.api.dependencies import ValidatedULID

        # Test workflow name gives name-specific error (spaces detected)
        with pytest.raises(BadRequestProblem) as exc_info:
            ValidatedULID.validate("Untitled Workflow")

        assert "appears to be a name or title, not a ULID" in str(
            exc_info.value.detail
        )
        assert "must be exactly 26 characters without spaces" in str(
            exc_info.value.detail
        )
        assert "Untitled Workflow" in str(exc_info.value.detail)
        assert (
            "there may be a bug where a workflow/resource name is being used as an ID"
            in str(exc_info.value.detail)
        )

        # Test empty string gives length-specific error
        with pytest.raises(BadRequestProblem) as exc_info:
            ValidatedULID.validate("")

        assert "must be exactly 26 characters" in str(
            exc_info.value.detail
        )
        assert "got 0 characters" in str(exc_info.value.detail)

        # Test descriptive names get appropriate error (this may be generic if it's short)
        with pytest.raises(BadRequestProblem) as exc_info:
            ValidatedULID.validate("untitled")

        # Accept either detailed message or generic message for short strings
        assert (
            "appears to be a descriptive name rather than a ULID"
            in str(exc_info.value.detail)
            or "must be exactly 26 characters, got 8 characters"
            in str(exc_info.value.detail)
        )


if __name__ == "__main__":
    pytest.main([__file__])
