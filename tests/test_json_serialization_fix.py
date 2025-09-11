"""Test for JSON serialization fix for bytes objects in validation errors."""

import json
from fastapi.exceptions import RequestValidationError
import pytest

from chatter.utils.problem import ValidationProblem, _sanitize_for_json


class TestJsonSerializationFix:
    """Test the fix for JSON serialization of bytes objects."""

    def test_sanitize_bytes(self):
        """Test that bytes objects are properly sanitized."""
        test_bytes = b"some binary data"
        result = _sanitize_for_json(test_bytes)

        assert isinstance(result, str)
        assert result == "<bytes: 16 bytes>"

        # Verify it's JSON serializable
        json.dumps(result)

    def test_sanitize_nested_structures(self):
        """Test that nested structures with bytes are properly sanitized."""
        test_data = {
            "simple": "text",
            "bytes_field": b"binary data",
            "nested": {
                "deep_bytes": b"deep binary",
                "list_with_bytes": [b"item1", "normal", b"item2"],
            },
        }

        result = _sanitize_for_json(test_data)

        # Verify structure is preserved
        assert result["simple"] == "text"
        assert result["bytes_field"] == "<bytes: 11 bytes>"
        assert result["nested"]["deep_bytes"] == "<bytes: 11 bytes>"
        assert result["nested"]["list_with_bytes"] == [
            "<bytes: 5 bytes>",
            "normal",
            "<bytes: 5 bytes>",
        ]

        # Verify it's JSON serializable
        json.dumps(result)

    def test_validation_problem_with_bytes(self):
        """Test that ValidationProblem handles bytes in validation errors."""
        # Create validation error with bytes
        validation_error = RequestValidationError(
            [
                {
                    "type": "value_error",
                    "loc": ["body", "file"],
                    "msg": "Invalid file",
                    "input": b"binary file data",
                    "ctx": {"metadata": b"binary metadata"},
                }
            ]
        )

        # Create ValidationProblem
        validation_problem = ValidationProblem(
            detail="The request contains invalid data",
            validation_errors=validation_error.errors(),
        )

        # This should not raise a JSON serialization error
        response = validation_problem.to_response(None)

        # Verify response is properly formed
        assert response.status_code == 422
        assert (
            response.headers["Content-Type"]
            == "application/problem+json"
        )

        # Verify content is valid JSON
        content = response.body.decode()
        parsed_content = json.loads(content)

        assert parsed_content["title"] == "Validation Failed"
        assert "errors" in parsed_content

        # Verify bytes were sanitized
        errors = parsed_content["errors"]
        assert len(errors) == 1
        error = errors[0]
        assert error["input"] == "<bytes: 16 bytes>"
        assert error["ctx"]["metadata"] == "<bytes: 15 bytes>"

    def test_various_non_serializable_types(self):
        """Test that various non-serializable types are handled."""

        class CustomObject:
            def __init__(self):
                self.data = b"some bytes"

        test_cases = [
            b"bytes",
            [b"bytes", "string"],
            {"key": b"value"},
            CustomObject(),
        ]

        for test_obj in test_cases:
            result = _sanitize_for_json(test_obj)
            # Should be JSON serializable
            json.dumps(result)

    def test_already_serializable_objects_unchanged(self):
        """Test that already JSON-serializable objects are not modified."""
        test_data = {
            "string": "text",
            "number": 42,
            "boolean": True,
            "null": None,
            "list": [1, 2, "three"],
            "nested": {"key": "value"},
        }

        result = _sanitize_for_json(test_data)
        assert result == test_data

        # Verify it's still JSON serializable
        json.dumps(result)
