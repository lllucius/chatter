"""Tests for workflow validation utilities."""

import pytest

from chatter.core.workflow_validation import (
    InputSanitizer,
    ParameterValidator,
    SchemaValidator,
    StepValidator,
    ValidationResult,
    ValidationRule,
    WorkflowValidator,
)


@pytest.mark.unit
class TestValidationResult:
    """Test ValidationResult class."""

    def test_validation_result_success(self):
        """Test ValidationResult for successful validation."""
        # Act
        result = ValidationResult(valid=True)

        # Assert
        assert result.valid is True
        assert result.errors == []

    def test_validation_result_failure(self):
        """Test ValidationResult for failed validation."""
        # Arrange
        errors = ["Error 1", "Error 2"]

        # Act
        result = ValidationResult(valid=False, errors=errors)

        # Assert
        assert result.valid is False
        assert result.errors == errors

    def test_validation_result_default(self):
        """Test ValidationResult default initialization."""
        # Act
        result = ValidationResult()

        # Assert
        assert result.valid is True
        assert result.errors == []


@pytest.mark.unit
class TestValidationRule:
    """Test ValidationRule base class."""

    def test_validation_rule_initialization(self):
        """Test ValidationRule initialization."""
        # Arrange
        name = "test_rule"
        message = "Test validation message"

        # Act
        rule = ValidationRule(name, message)

        # Assert
        assert rule.name == name
        assert rule.message == message

    def test_validation_rule_default_validate(self):
        """Test ValidationRule default validate method."""
        # Arrange
        rule = ValidationRule("test", "message")

        # Act
        result = rule.validate("any_value")

        # Assert
        assert result is True


@pytest.mark.unit
class TestInputSanitizer:
    """Test InputSanitizer functionality."""

    def test_sanitize_text_normal_text(self):
        """Test sanitizing normal text."""
        # Arrange
        text = "Hello, world! This is a normal text."

        # Act
        sanitized = InputSanitizer.sanitize_text(text)

        # Assert
        assert sanitized == text

    def test_sanitize_text_empty_string(self):
        """Test sanitizing empty string."""
        # Act
        sanitized = InputSanitizer.sanitize_text("")

        # Assert
        assert sanitized == ""

    def test_sanitize_text_none_input(self):
        """Test sanitizing None input."""
        # Act
        sanitized = InputSanitizer.sanitize_text(None)

        # Assert
        assert sanitized == ""

    def test_sanitize_text_with_control_characters(self):
        """Test sanitizing text with control characters."""
        # Arrange
        text = "Hello\x00\x01\x02 World"

        # Act
        sanitized = InputSanitizer.sanitize_text(text)

        # Assert
        assert "\x00" not in sanitized
        assert "\x01" not in sanitized
        assert "\x02" not in sanitized
        assert "Hello World" in sanitized

    def test_sanitize_text_with_allowed_whitespace(self):
        """Test sanitizing text preserves allowed whitespace."""
        # Arrange
        text = "Hello\tWorld\nNew Line\rReturn"

        # Act
        sanitized = InputSanitizer.sanitize_text(text)

        # Assert
        assert "\t" in sanitized
        assert "\n" in sanitized
        assert "\r" in sanitized

    def test_sanitize_text_max_length(self):
        """Test sanitizing text respects max length."""
        # Arrange
        text = "A" * 15000
        max_length = 5000

        # Act
        sanitized = InputSanitizer.sanitize_text(
            text, max_length=max_length
        )

        # Assert
        assert len(sanitized) == max_length

    def test_sanitize_query_parameters(self):
        """Test sanitizing query parameters."""
        # Arrange
        params = {
            "q": "search term",
            "limit": "10",
            "offset": "0",
            "malicious": "'; DROP TABLE users; --",
        }

        # Act
        sanitized = InputSanitizer.sanitize_query_parameters(params)

        # Assert
        assert "search term" in sanitized["q"]
        assert sanitized["limit"] == "10"
        assert "DROP TABLE" not in sanitized["malicious"]

    def test_validate_file_path_safe_path(self):
        """Test validating safe file paths."""
        # Arrange
        safe_paths = [
            "documents/file.txt",
            "uploads/image.jpg",
            "data/config.json",
        ]

        # Act & Assert
        for path in safe_paths:
            assert InputSanitizer.validate_file_path(path) is True

    def test_validate_file_path_unsafe_path(self):
        """Test validating unsafe file paths."""
        # Arrange
        unsafe_paths = [
            "../../../etc/passwd",
            "/etc/shadow",
            "..\\..\\windows\\system32",
            "uploads/../config/secrets.env",
        ]

        # Act & Assert
        for path in unsafe_paths:
            assert InputSanitizer.validate_file_path(path) is False

    def test_sanitize_user_input_comprehensive(self):
        """Test comprehensive user input sanitization."""
        # Arrange
        user_input = {
            "message": "Hello <script>alert('xss')</script>world",
            "user_id": "user-123",
            "session_data": {"key": "value\x00\x01"},
        }

        # Act
        sanitized = InputSanitizer.sanitize_user_input(user_input)

        # Assert
        assert "<script>" not in sanitized["message"]
        assert "alert" not in sanitized["message"]
        assert sanitized["user_id"] == "user-123"
        assert "\x00" not in str(sanitized["session_data"])


@pytest.mark.unit
class TestWorkflowValidator:
    """Test WorkflowValidator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = WorkflowValidator()

    def test_validate_workflow_config_valid(self):
        """Test validating valid workflow configuration."""
        # Arrange
        valid_config = {
            "id": "test-workflow",
            "name": "Test Workflow",
            "description": "A test workflow",
            "steps": [
                {
                    "id": "step-1",
                    "name": "Input Step",
                    "type": "input",
                    "config": {"source": "user_input"},
                }
            ],
        }

        # Act
        result = self.validator.validate_workflow_config(valid_config)

        # Assert
        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_workflow_config_missing_required_field(self):
        """Test validating workflow config with missing required fields."""
        # Arrange
        invalid_config = {
            "name": "Test Workflow",
            # Missing 'id' and 'steps'
        }

        # Act
        result = self.validator.validate_workflow_config(invalid_config)

        # Assert
        assert result.valid is False
        assert len(result.errors) > 0
        assert any("id" in error.lower() for error in result.errors)

    def test_validate_workflow_config_invalid_step_type(self):
        """Test validating workflow config with invalid step type."""
        # Arrange
        invalid_config = {
            "id": "test-workflow",
            "name": "Test Workflow",
            "steps": [
                {
                    "id": "step-1",
                    "name": "Invalid Step",
                    "type": "unknown_type",  # Invalid type
                    "config": {},
                }
            ],
        }

        # Act
        result = self.validator.validate_workflow_config(invalid_config)

        # Assert
        assert result.valid is False
        assert any("type" in error.lower() for error in result.errors)

    def test_validate_workflow_permissions(self):
        """Test validating workflow permissions."""
        # Arrange
        workflow_config = {
            "id": "secure-workflow",
            "permissions": {
                "required_role": "admin",
                "allowed_tools": ["tool1", "tool2"],
                "restricted_actions": ["delete", "modify"],
            },
        }
        user_permissions = {
            "role": "admin",
            "tools": ["tool1", "tool2", "tool3"],
            "actions": ["read", "write", "execute"],
        }

        # Act
        result = self.validator.validate_workflow_permissions(
            workflow_config, user_permissions
        )

        # Assert
        assert result.valid is True

    def test_validate_workflow_permissions_insufficient(self):
        """Test validating insufficient workflow permissions."""
        # Arrange
        workflow_config = {
            "id": "secure-workflow",
            "permissions": {
                "required_role": "admin",
                "allowed_tools": ["tool1", "tool2"],
            },
        }
        user_permissions = {
            "role": "user",  # Insufficient role
            "tools": ["tool1"],  # Missing tool2
        }

        # Act
        result = self.validator.validate_workflow_permissions(
            workflow_config, user_permissions
        )

        # Assert
        assert result.valid is False
        assert len(result.errors) > 0

    def test_validate_workflow_dependencies(self):
        """Test validating workflow dependencies."""
        # Arrange
        workflow_config = {
            "id": "dependent-workflow",
            "dependencies": {
                "required_services": ["llm_service", "vector_store"],
                "optional_services": ["analytics_service"],
            },
        }
        available_services = [
            "llm_service",
            "vector_store",
            "analytics_service",
        ]

        # Act
        result = self.validator.validate_workflow_dependencies(
            workflow_config, available_services
        )

        # Assert
        assert result.valid is True

    def test_validate_workflow_dependencies_missing(self):
        """Test validating workflow with missing dependencies."""
        # Arrange
        workflow_config = {
            "id": "dependent-workflow",
            "dependencies": {
                "required_services": [
                    "llm_service",
                    "vector_store",
                    "missing_service",
                ]
            },
        }
        available_services = ["llm_service", "vector_store"]

        # Act
        result = self.validator.validate_workflow_dependencies(
            workflow_config, available_services
        )

        # Assert
        assert result.valid is False
        assert any(
            "missing_service" in error for error in result.errors
        )


@pytest.mark.unit
class TestStepValidator:
    """Test StepValidator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = StepValidator()

    def test_validate_step_config_valid(self):
        """Test validating valid step configuration."""
        # Arrange
        valid_step = {
            "id": "step-1",
            "name": "Valid Step",
            "type": "llm_call",
            "config": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000,
            },
        }

        # Act
        result = self.validator.validate_step(valid_step)

        # Assert
        assert result.valid is True

    def test_validate_step_config_missing_id(self):
        """Test validating step with missing ID."""
        # Arrange
        invalid_step = {
            "name": "Step without ID",
            "type": "llm_call",
            "config": {},
        }

        # Act
        result = self.validator.validate_step(invalid_step)

        # Assert
        assert result.valid is False
        assert any("id" in error.lower() for error in result.errors)

    def test_validate_llm_call_step(self):
        """Test validating LLM call step specific requirements."""
        # Arrange
        llm_step = {
            "id": "llm-step",
            "name": "LLM Step",
            "type": "llm_call",
            "config": {
                "model": "gpt-4",
                "prompt": "Test prompt",
                "temperature": 0.5,
            },
        }

        # Act
        result = self.validator.validate_llm_call_step(llm_step)

        # Assert
        assert result.valid is True

    def test_validate_llm_call_step_missing_model(self):
        """Test validating LLM call step without model."""
        # Arrange
        invalid_llm_step = {
            "id": "llm-step",
            "name": "LLM Step",
            "type": "llm_call",
            "config": {
                "prompt": "Test prompt"
                # Missing 'model'
            },
        }

        # Act
        result = self.validator.validate_llm_call_step(invalid_llm_step)

        # Assert
        assert result.valid is False
        assert any("model" in error.lower() for error in result.errors)

    def test_validate_condition_step(self):
        """Test validating condition step."""
        # Arrange
        condition_step = {
            "id": "condition-step",
            "name": "Condition Step",
            "type": "condition",
            "config": {
                "condition": "input.value > 10",
                "true_path": "step-2",
                "false_path": "step-3",
            },
        }

        # Act
        result = self.validator.validate_condition_step(condition_step)

        # Assert
        assert result.valid is True

    def test_validate_tool_call_step(self):
        """Test validating tool call step."""
        # Arrange
        tool_step = {
            "id": "tool-step",
            "name": "Tool Step",
            "type": "tool_call",
            "config": {
                "tool_name": "calculator",
                "parameters": {"operation": "add", "a": 5, "b": 3},
            },
        }

        # Act
        result = self.validator.validate_tool_call_step(tool_step)

        # Assert
        assert result.valid is True


@pytest.mark.unit
class TestParameterValidator:
    """Test ParameterValidator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ParameterValidator()

    def test_validate_temperature_valid_range(self):
        """Test validating temperature in valid range."""
        # Arrange
        valid_temperatures = [0.0, 0.5, 1.0, 0.7, 0.1]

        # Act & Assert
        for temp in valid_temperatures:
            result = self.validator.validate_temperature(temp)
            assert result.valid is True

    def test_validate_temperature_invalid_range(self):
        """Test validating temperature outside valid range."""
        # Arrange
        invalid_temperatures = [-0.1, 1.1, 2.0, -1.0]

        # Act & Assert
        for temp in invalid_temperatures:
            result = self.validator.validate_temperature(temp)
            assert result.valid is False

    def test_validate_max_tokens_valid(self):
        """Test validating valid max_tokens values."""
        # Arrange
        valid_tokens = [1, 100, 1000, 4096, 8192]

        # Act & Assert
        for tokens in valid_tokens:
            result = self.validator.validate_max_tokens(tokens)
            assert result.valid is True

    def test_validate_max_tokens_invalid(self):
        """Test validating invalid max_tokens values."""
        # Arrange
        invalid_tokens = [0, -1, 100000, "not_a_number"]

        # Act & Assert
        for tokens in invalid_tokens:
            result = self.validator.validate_max_tokens(tokens)
            assert result.valid is False

    def test_validate_model_name_supported(self):
        """Test validating supported model names."""
        # Arrange
        supported_models = [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3",
            "llama-2",
        ]

        # Act & Assert
        for model in supported_models:
            result = self.validator.validate_model_name(model)
            assert result.valid is True

    def test_validate_model_name_unsupported(self):
        """Test validating unsupported model names."""
        # Arrange
        unsupported_models = [
            "unknown-model",
            "",
            None,
            "deprecated-model",
        ]

        # Act & Assert
        for model in unsupported_models:
            result = self.validator.validate_model_name(model)
            assert result.valid is False


@pytest.mark.unit
class TestSchemaValidator:
    """Test SchemaValidator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator()

    def test_validate_json_schema_valid(self):
        """Test validating data against valid JSON schema."""
        # Arrange
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number", "minimum": 0},
            },
            "required": ["name"],
        }
        data = {"name": "John", "age": 30}

        # Act
        result = self.validator.validate_json_schema(data, schema)

        # Assert
        assert result.valid is True

    def test_validate_json_schema_invalid(self):
        """Test validating data against JSON schema with errors."""
        # Arrange
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number", "minimum": 0},
            },
            "required": ["name"],
        }
        data = {"age": -5}  # Missing required 'name', invalid age

        # Act
        result = self.validator.validate_json_schema(data, schema)

        # Assert
        assert result.valid is False
        assert len(result.errors) > 0

    def test_validate_workflow_output_schema(self):
        """Test validating workflow output against schema."""
        # Arrange
        output_schema = {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                },
                "metadata": {"type": "object"},
            },
            "required": ["result"],
        }

        valid_output = {
            "result": "Task completed successfully",
            "confidence": 0.95,
            "metadata": {"timestamp": "2024-01-01T00:00:00Z"},
        }

        # Act
        result = self.validator.validate_workflow_output_schema(
            valid_output, output_schema
        )

        # Assert
        assert result.valid is True


@pytest.mark.integration
class TestWorkflowValidationIntegration:
    """Integration tests for workflow validation system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.workflow_validator = WorkflowValidator()
        self.step_validator = StepValidator()
        self.param_validator = ParameterValidator()

    def test_complete_workflow_validation(self):
        """Test complete workflow validation process."""
        # Arrange
        complete_workflow = {
            "id": "complete-test-workflow",
            "name": "Complete Test Workflow",
            "description": "A comprehensive workflow for validation testing",
            "version": "1.0.0",
            "steps": [
                {
                    "id": "input-step",
                    "name": "Input Processing",
                    "type": "input",
                    "config": {
                        "source": "user_input",
                        "validation": True,
                    },
                },
                {
                    "id": "llm-step",
                    "name": "LLM Processing",
                    "type": "llm_call",
                    "config": {
                        "model": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 1000,
                        "prompt": "Process the user input",
                    },
                },
                {
                    "id": "condition-step",
                    "name": "Decision Point",
                    "type": "condition",
                    "config": {
                        "condition": "output.confidence > 0.8",
                        "true_path": "success-step",
                        "false_path": "retry-step",
                    },
                },
            ],
            "permissions": {
                "required_role": "user",
                "allowed_tools": ["calculator", "search"],
            },
            "dependencies": {
                "required_services": ["llm_service"],
                "optional_services": ["analytics_service"],
            },
        }

        # Mock available services and user permissions
        available_services = ["llm_service", "analytics_service"]
        user_permissions = {
            "role": "user",
            "tools": ["calculator", "search", "other_tool"],
            "actions": ["read", "write", "execute"],
        }

        # Act - Validate complete workflow
        config_result = (
            self.workflow_validator.validate_workflow_config(
                complete_workflow
            )
        )

        if config_result.valid:
            perm_result = (
                self.workflow_validator.validate_workflow_permissions(
                    complete_workflow, user_permissions
                )
            )
            dep_result = (
                self.workflow_validator.validate_workflow_dependencies(
                    complete_workflow, available_services
                )
            )

            # Validate individual steps
            step_results = []
            for step in complete_workflow["steps"]:
                step_result = self.step_validator.validate_step(step)
                step_results.append(step_result)

        # Assert - All validations pass
        assert config_result.valid is True
        assert perm_result.valid is True
        assert dep_result.valid is True
        assert all(result.valid for result in step_results)

    def test_workflow_validation_with_errors(self):
        """Test workflow validation that should fail."""
        # Arrange
        invalid_workflow = {
            "id": "invalid-workflow",
            # Missing 'name' - required field
            "steps": [
                {
                    "id": "invalid-step",
                    "name": "Invalid Step",
                    "type": "unknown_type",  # Invalid step type
                    "config": {
                        "model": "unsupported-model",  # Invalid model
                        "temperature": 2.0,  # Invalid temperature
                    },
                }
            ],
        }

        # Act
        config_result = (
            self.workflow_validator.validate_workflow_config(
                invalid_workflow
            )
        )

        # Validate the invalid step
        step_result = self.step_validator.validate_step(
            invalid_workflow["steps"][0]
        )

        # Validate parameters
        temp_result = self.param_validator.validate_temperature(2.0)
        model_result = self.param_validator.validate_model_name(
            "unsupported-model"
        )

        # Assert - All validations should fail
        assert config_result.valid is False
        assert step_result.valid is False
        assert temp_result.valid is False
        assert model_result.valid is False

        # Check that errors are descriptive
        assert len(config_result.errors) > 0
        assert len(step_result.errors) > 0
