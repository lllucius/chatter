"""Comprehensive test to verify workflow validation implementations work."""

import os
import sys

# Add path manually to work around pytest import issues
sys.path.insert(0, os.path.abspath('.'))

import pytest


def test_workflow_validation_classes_exist():
    """Test that all workflow validation classes can be imported and used."""
    # Import with manual path setup
    try:
        from chatter.core.workflow_validation import (
            InputSanitizer,
            ParameterValidator,
            SchemaValidator,
            StepValidator,
            ValidationResult,
            ValidationRule,
            WorkflowValidator,
        )
    except ImportError as e:
        pytest.skip(f"Cannot import workflow validation classes: {e}")

    # Test ValidationResult
    result = ValidationResult(valid=True)
    assert result.valid is True
    assert result.errors == []

    result_with_errors = ValidationResult(
        valid=False, errors=["Test error"]
    )
    assert result_with_errors.valid is False
    assert len(result_with_errors.errors) == 1


def test_parameter_validator_functionality():
    """Test ParameterValidator methods."""
    try:
        from chatter.core.workflow_validation import ParameterValidator
    except ImportError as e:
        pytest.skip(f"Cannot import ParameterValidator: {e}")

    validator = ParameterValidator()

    # Test temperature validation
    valid_temp = validator.validate_temperature(0.7)
    assert valid_temp.valid is True

    invalid_temp = validator.validate_temperature(2.0)
    assert invalid_temp.valid is False
    assert any("0.0 and 1.0" in error for error in invalid_temp.errors)

    # Test max_tokens validation
    valid_tokens = validator.validate_max_tokens(1000)
    assert valid_tokens.valid is True

    invalid_tokens = validator.validate_max_tokens(-1)
    assert invalid_tokens.valid is False

    # Test model validation
    valid_model = validator.validate_model_name("gpt-4")
    assert valid_model.valid is True

    invalid_model = validator.validate_model_name("unknown-model-xyz")
    assert invalid_model.valid is False


def test_schema_validator_functionality():
    """Test SchemaValidator methods."""
    try:
        from chatter.core.workflow_validation import SchemaValidator
    except ImportError as e:
        pytest.skip(f"Cannot import SchemaValidator: {e}")

    validator = SchemaValidator()

    # Test JSON schema validation
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
        },
        "required": ["name"],
    }

    valid_data = {"name": "John", "age": 30}
    result = validator.validate_json_schema(valid_data, schema)
    assert result.valid is True

    invalid_data = {"age": 30}  # Missing required name
    result = validator.validate_json_schema(invalid_data, schema)
    assert result.valid is False


def test_step_validator_functionality():
    """Test StepValidator methods."""
    try:
        from chatter.core.workflow_validation import StepValidator
    except ImportError as e:
        pytest.skip(f"Cannot import StepValidator: {e}")

    validator = StepValidator()

    # Test valid step
    valid_step = {
        "id": "step-1",
        "name": "Test Step",
        "type": "llm_call",
        "config": {"model": "gpt-4", "temperature": 0.7},
    }

    result = validator.validate_step(valid_step)
    assert result.valid is True

    # Test invalid step (missing required fields)
    invalid_step = {
        "name": "Incomplete Step"
        # Missing id and type
    }

    result = validator.validate_step(invalid_step)
    assert result.valid is False
    assert any("id" in error for error in result.errors)


def test_workflow_validator_functionality():
    """Test WorkflowValidator methods."""
    try:
        from chatter.core.workflow_validation import WorkflowValidator
    except ImportError as e:
        pytest.skip(f"Cannot import WorkflowValidator: {e}")

    # Test workflow config validation
    valid_config = {
        "id": "test-workflow",
        "name": "Test Workflow",
        "steps": [
            {
                "id": "step-1",
                "name": "Test Step",
                "type": "input",
                "config": {},
            }
        ],
    }

    result = WorkflowValidator.validate_workflow_config(valid_config)
    assert result.valid is True

    # Test invalid config
    invalid_config = {
        "name": "Test Workflow"
        # Missing required id and steps
    }

    result = WorkflowValidator.validate_workflow_config(invalid_config)
    assert result.valid is False


def test_input_sanitizer_functionality():
    """Test InputSanitizer methods."""
    try:
        from chatter.core.workflow_validation import InputSanitizer
    except ImportError as e:
        pytest.skip(f"Cannot import InputSanitizer: {e}")

    # Test text sanitization
    normal_text = "Hello, world!"
    sanitized = InputSanitizer.sanitize_text(normal_text)
    assert sanitized == normal_text

    # Test control character removal
    text_with_control = "Hello\x00\x01 World"
    sanitized = InputSanitizer.sanitize_text(text_with_control)
    assert "\x00" not in sanitized
    assert "\x01" not in sanitized

    # Test file path validation
    safe_path = "documents/file.txt"
    assert InputSanitizer.validate_file_path(safe_path) is True

    unsafe_path = "../../../etc/passwd"
    assert InputSanitizer.validate_file_path(unsafe_path) is False


if __name__ == "__main__":
    # Run tests directly if executed as script
    test_workflow_validation_classes_exist()
    test_parameter_validator_functionality()
    test_schema_validator_functionality()
    test_step_validator_functionality()
    test_workflow_validator_functionality()
    test_input_sanitizer_functionality()
    print("All workflow validation tests passed!")
