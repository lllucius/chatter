"""Simple workflow validation test to verify pytest can run."""

import pytest


def test_basic_import():
    """Test that we can import workflow validation classes."""
    try:
        from chatter.core.workflow_validation import (
            ParameterValidator,
            SchemaValidator,
            StepValidator,
            ValidationResult,
        )

        # Basic functionality test
        result = ValidationResult(valid=True)
        assert result.valid is True

        param_validator = ParameterValidator()
        temp_result = param_validator.validate_temperature(0.7)
        assert temp_result.valid is True

        print(
            "✓ Basic workflow validation imports and functionality working"
        )

    except ImportError as e:
        pytest.fail(
            f"Could not import workflow validation classes: {e}"
        )


if __name__ == "__main__":
    test_basic_import()
    print("Direct execution successful!")
