"""Unit tests for API validation functions that don't require database."""

from uuid import uuid4

import pytest

from chatter.api.chat import _map_workflow_type, _validate_uuid
from chatter.utils.problem import BadRequestProblem


class TestWorkflowMapping:
    """Test workflow type mapping functionality."""

    def test_valid_workflow_types(self):
        """Test mapping of valid workflow types."""
        assert _map_workflow_type("plain") == "basic"
        assert _map_workflow_type("rag") == "rag"
        assert _map_workflow_type("tools") == "tools"
        assert _map_workflow_type("full") == "full"

    def test_case_insensitive_workflow_types(self):
        """Test case-insensitive workflow mapping."""
        assert _map_workflow_type("PLAIN") == "basic"
        assert _map_workflow_type("Plain") == "basic"
        assert _map_workflow_type("RAG") == "rag"
        assert _map_workflow_type("Tools") == "tools"

    def test_none_workflow_type(self):
        """Test None workflow type defaults to basic."""
        assert _map_workflow_type(None) == "basic"

    def test_empty_workflow_type(self):
        """Test empty workflow type defaults to basic."""
        assert _map_workflow_type("") == "basic"
        assert _map_workflow_type("   ") == "basic"

    def test_invalid_workflow_type(self):
        """Test invalid workflow type defaults to basic."""
        assert _map_workflow_type("invalid") == "basic"
        assert _map_workflow_type("unknown") == "basic"


class TestUUIDValidation:
    """Test UUID validation functionality."""

    def test_valid_uuid(self):
        """Test validation of valid UUIDs."""
        valid_uuid = str(uuid4())
        result = _validate_uuid(valid_uuid, "test_field")
        assert result == valid_uuid

    def test_invalid_uuid_format(self):
        """Test validation fails for invalid UUID format."""
        with pytest.raises(BadRequestProblem) as exc_info:
            _validate_uuid("not-a-uuid", "test_field")

        assert "Invalid test_field format" in str(exc_info.value.detail)
        assert "must be a valid UUID" in str(exc_info.value.detail)

    def test_empty_uuid(self):
        """Test validation fails for empty UUID."""
        with pytest.raises(BadRequestProblem):
            _validate_uuid("", "test_field")

    def test_none_uuid(self):
        """Test validation fails for None UUID."""
        with pytest.raises((BadRequestProblem, TypeError)):
            _validate_uuid(None, "test_field")

    def test_malformed_uuid(self):
        """Test validation fails for malformed UUIDs."""
        malformed_uuids = [
            "123e4567-e89b-12d3-a456-42661417400",  # Missing character
            "123e4567-e89b-12d3-a456-42661417400g",  # Invalid character
            "not-a-uuid-at-all",  # Completely invalid
            "123-456-789",  # Wrong format
        ]

        for malformed_uuid in malformed_uuids:
            with pytest.raises(BadRequestProblem):
                _validate_uuid(malformed_uuid, "test_field")


if __name__ == "__main__":
    pytest.main([__file__])
