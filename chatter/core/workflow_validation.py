"""Workflow validation utilities.

This module provides comprehensive validation for workflow configurations
and parameters, addressing the input validation gap identified in the review.
"""

from enum import Enum
from typing import Any

from chatter.core.exceptions import (
    WorkflowConfigurationError,
    WorkflowValidationError,
)


class ValidationResult:
    """Result of validation operation."""

    def __init__(self, valid: bool = True, errors: list[str] | None = None):
        self.valid = valid
        self.errors = errors or []


class ValidationRule:
    """Base class for validation rules."""

    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

    def validate(self, value: Any) -> bool:
        """Validate a value. Override in subclasses."""
        return True


class InputSanitizer:
    """Sanitize and validate user inputs."""

    @staticmethod
    def sanitize_text(text: str, max_length: int = 10000) -> str:
        """Sanitize text input."""
        if not text:
            return ""

        # Remove null bytes and control characters
        sanitized = "".join(
            char for char in text
            if ord(char) >= 32 or char in "\t\n\r"
        )

        # Truncate to max length
        sanitized = sanitized[:max_length]

        # Strip whitespace
        return sanitized.strip()

    @staticmethod
    def sanitize_html(html: str) -> str:
        """Remove potentially dangerous HTML tags."""
        # Basic HTML sanitization - remove script tags and other dangerous elements
        import re

        # Remove script tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)

        # Remove other dangerous tags
        dangerous_tags = ['iframe', 'object', 'embed', 'link', 'meta', 'style']
        for tag in dangerous_tags:
            html = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', html, flags=re.IGNORECASE | re.DOTALL)
            html = re.sub(f'<{tag}[^>]*/?>', '', html, flags=re.IGNORECASE)

        return html

    @staticmethod
    def sanitize_query_parameters(params: dict[str, str]) -> dict[str, str]:
        """Sanitize query parameters."""
        sanitized = {}
        for key, value in params.items():
            if isinstance(value, str):
                # Remove potential SQL injection patterns
                sanitized_value = value
                
                # Remove SQL injection patterns
                import re
                sql_patterns = [
                    r';.*?(DROP|DELETE|UPDATE|INSERT)\s+',
                    r'--.*$',
                    r'/\*.*?\*/',
                ]
                
                for pattern in sql_patterns:
                    sanitized_value = re.sub(pattern, '', sanitized_value, flags=re.IGNORECASE)
                
                sanitized[key] = sanitized_value.strip()
            else:
                sanitized[key] = value
        return sanitized

    @staticmethod
    def validate_file_path(path: str) -> bool:
        """Validate file path for safety."""
        import os
        
        # Check for path traversal attempts
        if '..' in path or path.startswith('/') or '\\' in path:
            return False
            
        # Normalize path and check if it's safe
        normalized = os.path.normpath(path)
        
        # Should not go outside current directory
        if normalized.startswith('..') or normalized.startswith('/'):
            return False
            
        return True

    @staticmethod
    def sanitize_user_input(user_input: dict[str, any]) -> dict[str, any]:
        """Sanitize comprehensive user input."""
        sanitized = {}
        
        for key, value in user_input.items():
            if isinstance(value, str):
                # Sanitize HTML and remove control characters
                sanitized_value = InputSanitizer.sanitize_html(value)
                sanitized_value = InputSanitizer.sanitize_text(sanitized_value)
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = InputSanitizer.sanitize_user_input(value)
            else:
                sanitized[key] = value
                
        return sanitized

    @staticmethod
    def validate_input_length(text: str, max_length: int) -> ValidationResult:
        """Validate input length."""
        if len(text) > max_length:
            return ValidationResult(
                valid=False,
                errors=[f"Input too long (maximum {max_length} characters)"]
            )
        return ValidationResult()

    @staticmethod
    def validate_no_suspicious_patterns(text: str) -> ValidationResult:
        """Check for suspicious patterns in text."""
        import re

        # Check for potential SQL injection patterns
        sql_patterns = [
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b',
            r'[;\'"]\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b',
            r'--\s*',
            r'/\*.*?\*/',
        ]

        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    valid=False,
                    errors=["Text contains potentially malicious patterns"]
                )

        return ValidationResult()


class WorkflowType(str, Enum):
    """Supported workflow types."""
    PLAIN = "plain"
    RAG = "rag"
    TOOLS = "tools"
    FULL = "full"


class WorkflowValidator:
    """Validates workflow configurations and parameters."""

    # Required parameters for each workflow type
    REQUIRED_PARAMS = {
        WorkflowType.PLAIN: [],
        WorkflowType.RAG: ["retriever"],
        WorkflowType.TOOLS: ["tools"],
        WorkflowType.FULL: ["retriever", "tools"]
    }

    # Optional parameters for each workflow type
    OPTIONAL_PARAMS = {
        "all": ["system_message", "enable_memory", "memory_window"],
        WorkflowType.RAG: ["max_documents", "similarity_threshold"],
        WorkflowType.TOOLS: ["max_tool_calls", "tool_timeout"],
        WorkflowType.FULL: ["max_documents", "similarity_threshold", "max_tool_calls", "tool_timeout"]
    }

    # Parameter validation rules
    VALIDATION_RULES = {
        "max_documents": {"type": int, "min": 1, "max": 100},
        "similarity_threshold": {"type": float, "min": 0.0, "max": 1.0},
        "max_tool_calls": {"type": int, "min": 1, "max": 50},
        "tool_timeout": {"type": int, "min": 1, "max": 300},  # seconds
        "memory_window": {"type": int, "min": 1, "max": 100},
        "system_message": {"type": str, "max_length": 10000},
        "enable_memory": {"type": bool}
    }

    @classmethod
    def validate_workflow_request(
        cls,
        workflow_type: str,
        retriever: Any = None,
        tools: list[Any] | None = None,
        system_message: str | None = None,
        enable_memory: bool = False,
        **kwargs: Any
    ) -> None:
        """Validate a complete workflow request.

        Args:
            workflow_type: Type of workflow
            retriever: Retriever instance for RAG workflows
            tools: List of tools for tool workflows
            system_message: System message override
            enable_memory: Whether to enable conversation memory
            **kwargs: Additional workflow parameters

        Raises:
            WorkflowValidationError: If validation fails
        """
        issues = []

        # Validate workflow type
        try:
            wf_type = WorkflowType(workflow_type)
        except ValueError:
            raise WorkflowConfigurationError(
                f"Invalid workflow type '{workflow_type}'. "
                f"Must be one of: {', '.join([t.value for t in WorkflowType])}"
            )

        # Validate required parameters
        required_params = cls.REQUIRED_PARAMS[wf_type]
        for param in required_params:
            if param == "retriever" and retriever is None:
                issues.append(f"Retriever is required for {workflow_type} workflow")
            elif param == "tools" and (not tools or len(tools) == 0):
                issues.append(f"Tools are required for {workflow_type} workflow")

        # Validate parameter types and values
        all_params = {
            "system_message": system_message,
            "enable_memory": enable_memory,
            **kwargs
        }

        for param_name, param_value in all_params.items():
            if param_value is not None:
                cls._validate_parameter(param_name, param_value, issues)

        # Validate tools if provided
        if tools:
            cls._validate_tools(tools, issues)

        # Validate retriever if provided
        if retriever:
            cls._validate_retriever(retriever, issues)

        # Validate workflow-specific combinations
        cls._validate_workflow_combinations(wf_type, retriever, tools, kwargs, issues)

        if issues:
            raise WorkflowValidationError(
                f"Workflow validation failed for {workflow_type}",
                validation_issues=issues,
                workflow_type=workflow_type
            )

    @classmethod
    def _validate_parameter(cls, name: str, value: Any, issues: list[str]) -> None:
        """Validate a single parameter."""
        if name not in cls.VALIDATION_RULES:
            return  # Unknown parameters are allowed

        rules = cls.VALIDATION_RULES[name]

        # Type validation
        expected_type = rules.get("type")
        if expected_type and not isinstance(value, expected_type):
            issues.append(f"Parameter '{name}' must be of type {expected_type.__name__}")
            return

        # Value range validation
        if isinstance(value, int | float):
            min_val = rules.get("min")
            max_val = rules.get("max")
            if min_val is not None and value < min_val:
                issues.append(f"Parameter '{name}' must be >= {min_val}")
            if max_val is not None and value > max_val:
                issues.append(f"Parameter '{name}' must be <= {max_val}")

        # String length validation
        if isinstance(value, str):
            max_length = rules.get("max_length")
            if max_length and len(value) > max_length:
                issues.append(f"Parameter '{name}' must be <= {max_length} characters")

    @classmethod
    def _validate_tools(cls, tools: list[Any], issues: list[str]) -> None:
        """Validate tools list."""
        if not isinstance(tools, list):
            issues.append("Tools must be provided as a list")
            return

        if len(tools) == 0:
            issues.append("At least one tool must be provided")
            return

        if len(tools) > 20:  # Reasonable limit
            issues.append("Too many tools (maximum 20 allowed)")

        # Validate individual tools
        for i, tool in enumerate(tools):
            if not hasattr(tool, 'name'):
                issues.append(f"Tool {i} missing 'name' attribute")
            if not hasattr(tool, 'description'):
                issues.append(f"Tool {i} missing 'description' attribute")
            # Add more tool-specific validations as needed

    @classmethod
    def _validate_retriever(cls, retriever: Any, issues: list[str]) -> None:
        """Validate retriever instance."""
        # Check if retriever has required methods
        required_methods = ['get_relevant_documents', 'aget_relevant_documents']
        for method in required_methods:
            if not hasattr(retriever, method):
                issues.append(f"Retriever missing required method '{method}'")
                break  # One method check is enough

    @classmethod
    def _validate_workflow_combinations(
        cls,
        workflow_type: WorkflowType,
        retriever: Any,
        tools: list[Any] | None,
        params: dict[str, Any],
        issues: list[str]
    ) -> None:
        """Validate workflow-specific parameter combinations."""

        # RAG-specific validations
        if workflow_type in [WorkflowType.RAG, WorkflowType.FULL] and retriever:
            max_docs = params.get("max_documents", 5)
            if max_docs > 20:
                issues.append("max_documents should not exceed 20 for performance reasons")

        # Tools-specific validations
        if workflow_type in [WorkflowType.TOOLS, WorkflowType.FULL] and tools:
            max_calls = params.get("max_tool_calls", 10)
            if len(tools) > 10 and max_calls > 5:
                issues.append("When using many tools, consider reducing max_tool_calls")

        # Memory-specific validations
        if params.get("enable_memory", False):
            memory_window = params.get("memory_window", 10)
            if memory_window > 50:
                issues.append("Large memory windows may impact performance")

    @classmethod
    def validate_workflow_parameters(
        cls,
        workflow_type: str,
        **params: Any
    ) -> dict[str, Any]:
        """Validate and normalize workflow parameters.

        Args:
            workflow_type: Type of workflow
            **params: Workflow parameters

        Returns:
            Validated and normalized parameters

        Raises:
            WorkflowValidationError: If validation fails
        """
        try:
            wf_type = WorkflowType(workflow_type)
        except ValueError:
            raise WorkflowConfigurationError(
                f"Invalid workflow type '{workflow_type}'"
            )

        validated_params = {}
        issues = []

        # Validate each parameter
        for name, value in params.items():
            if value is not None:
                cls._validate_parameter(name, value, issues)
                validated_params[name] = value

        # Set defaults for missing optional parameters
        optional_params = cls.OPTIONAL_PARAMS.get("all", [])
        if wf_type in cls.OPTIONAL_PARAMS:
            optional_params.extend(cls.OPTIONAL_PARAMS[wf_type])

        # Set sensible defaults
        defaults = {
            "max_documents": 5,
            "similarity_threshold": 0.7,
            "max_tool_calls": 10,
            "tool_timeout": 30,
            "memory_window": 10,
            "enable_memory": False
        }

        for param in optional_params:
            if param not in validated_params and param in defaults:
                validated_params[param] = defaults[param]

        if issues:
            raise WorkflowValidationError(
                f"Parameter validation failed for {workflow_type}",
                validation_issues=issues,
                workflow_type=workflow_type
            )

        return validated_params

    @classmethod
    def validate_workflow_config(cls, config: dict) -> ValidationResult:
        """Validate basic workflow configuration."""
        errors = []
        
        # Check required fields
        required_fields = ['id', 'name', 'steps']
        for field in required_fields:
            if field not in config:
                errors.append(f"Workflow config missing required field: {field}")
        
        # Validate workflow ID
        if 'id' in config:
            if not isinstance(config['id'], str) or not config['id'].strip():
                errors.append("Workflow ID must be a non-empty string")
        
        # Validate workflow name
        if 'name' in config:
            if not isinstance(config['name'], str) or not config['name'].strip():
                errors.append("Workflow name must be a non-empty string")
        
        # Validate steps
        if 'steps' in config:
            if not isinstance(config['steps'], list):
                errors.append("Workflow steps must be a list")
            elif len(config['steps']) == 0:
                errors.append("Workflow must have at least one step")
            else:
                # Validate each step
                step_validator = StepValidator()
                for i, step in enumerate(config['steps']):
                    step_result = step_validator.validate_step(step)
                    if not step_result.valid:
                        for error in step_result.errors:
                            errors.append(f"Step {i}: {error}")
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        return ValidationResult()

    @classmethod
    def validate_workflow_permissions(cls, workflow_config: dict, user_permissions: dict) -> ValidationResult:
        """Validate workflow permissions against user permissions."""
        errors = []
        
        workflow_perms = workflow_config.get('permissions', {})
        
        # Check required role
        required_role = workflow_perms.get('required_role')
        if required_role:
            user_role = user_permissions.get('role')
            if user_role != required_role:
                errors.append(f"User role '{user_role}' does not match required role '{required_role}'")
        
        # Check allowed tools
        allowed_tools = workflow_perms.get('allowed_tools', [])
        user_tools = user_permissions.get('tools', [])
        for tool in allowed_tools:
            if tool not in user_tools:
                errors.append(f"User does not have access to required tool: {tool}")
        
        # Check restricted actions
        restricted_actions = workflow_perms.get('restricted_actions', [])
        user_actions = user_permissions.get('actions', [])
        for action in restricted_actions:
            if action in user_actions:
                errors.append(f"User has restricted action: {action}")
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        return ValidationResult()

    @classmethod
    def validate_workflow_dependencies(cls, workflow_config: dict, available_services: list[str]) -> ValidationResult:
        """Validate workflow dependencies are available."""
        errors = []
        
        dependencies = workflow_config.get('dependencies', {})
        
        # Check required services
        required_services = dependencies.get('required_services', [])
        for service in required_services:
            if service not in available_services:
                errors.append(f"Required service not available: {service}")
        
        # Check optional services (warnings, not errors)
        optional_services = dependencies.get('optional_services', [])
        missing_optional = [s for s in optional_services if s not in available_services]
        if missing_optional:
            # For optional services, we could add warnings but keep validation passing
            pass
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        return ValidationResult()

    @classmethod
    def get_supported_workflow_types(cls) -> list[str]:
        """Get list of supported workflow types."""
        return [t.value for t in WorkflowType]

    @classmethod
    def get_required_parameters(cls, workflow_type: str) -> list[str]:
        """Get required parameters for a workflow type."""
        try:
            wf_type = WorkflowType(workflow_type)
            return cls.REQUIRED_PARAMS[wf_type]
        except ValueError:
            raise WorkflowConfigurationError(f"Invalid workflow type '{workflow_type}'")

    @classmethod
    def get_optional_parameters(cls, workflow_type: str) -> list[str]:
        """Get optional parameters for a workflow type."""
        try:
            wf_type = WorkflowType(workflow_type)
            params = cls.OPTIONAL_PARAMS.get("all", []).copy()
            if wf_type in cls.OPTIONAL_PARAMS:
                params.extend(cls.OPTIONAL_PARAMS[wf_type])
            return params
        except ValueError:
            raise WorkflowConfigurationError(f"Invalid workflow type '{workflow_type}'")


# Convenience functions for common validations
def validate_chat_request(
    message: str,
    workflow_type: str = "plain",
    max_message_length: int = 10000
) -> None:
    """Validate a chat request.

    Args:
        message: User message
        workflow_type: Type of workflow
        max_message_length: Maximum message length

    Raises:
        WorkflowValidationError: If validation fails
    """
    issues = []

    if not message or not message.strip():
        issues.append("Message cannot be empty")

    if len(message) > max_message_length:
        issues.append(f"Message too long (maximum {max_message_length} characters)")

    # Validate workflow type
    if workflow_type not in WorkflowValidator.get_supported_workflow_types():
        issues.append(f"Invalid workflow type '{workflow_type}'")

    if issues:
        raise WorkflowValidationError(
            "Chat request validation failed",
            validation_issues=issues
        )


def validate_conversation_id(conversation_id: str | None) -> None:
    """Validate conversation ID format.

    Args:
        conversation_id: Conversation ID to validate

    Raises:
        WorkflowValidationError: If validation fails
    """
    if conversation_id is not None:
        if not isinstance(conversation_id, str):
            raise WorkflowValidationError(
                "Conversation ID must be a string",
                validation_issues=["conversation_id must be string type"]
            )

        if len(conversation_id.strip()) == 0:
            raise WorkflowValidationError(
                "Conversation ID cannot be empty",
                validation_issues=["conversation_id cannot be empty"]
            )

        # Add format validation if needed (UUID, etc.)
        # For now, just check it's a non-empty string


class ParameterValidator:
    """Validates workflow parameters."""

    def __init__(self):
        pass

    def validate_temperature(self, temperature: float) -> ValidationResult:
        """Validate temperature parameter."""
        if not isinstance(temperature, (int, float)):
            return ValidationResult(
                valid=False,
                errors=["Temperature must be a number"]
            )
        
        if temperature < 0.0 or temperature > 1.0:
            return ValidationResult(
                valid=False,
                errors=["Temperature must be between 0.0 and 1.0"]
            )
        
        return ValidationResult()

    def validate_max_tokens(self, max_tokens: int) -> ValidationResult:
        """Validate max_tokens parameter."""
        if not isinstance(max_tokens, int):
            return ValidationResult(
                valid=False,
                errors=["max_tokens must be an integer"]
            )
        
        if max_tokens < 1:
            return ValidationResult(
                valid=False,
                errors=["max_tokens must be greater than 0"]
            )
        
        if max_tokens > 32000:  # Reasonable upper limit
            return ValidationResult(
                valid=False,
                errors=["max_tokens should not exceed 32000"]
            )
        
        return ValidationResult()

    def validate_model_name(self, model_name: str) -> ValidationResult:
        """Validate model name parameter."""
        if not isinstance(model_name, str):
            return ValidationResult(
                valid=False,
                errors=["Model name must be a string"]
            )
        
        if not model_name.strip():
            return ValidationResult(
                valid=False,
                errors=["Model name cannot be empty"]
            )
        
        # List of known valid model patterns
        valid_patterns = [
            'gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'gpt-4o',
            'claude-3-haiku', 'claude-3-sonnet', 'claude-3-opus',
            'claude-3-5-sonnet',
            'gemini-pro', 'gemini-1.5-pro',
            'command-r', 'command-r-plus'
        ]
        
        # Check if model matches any known pattern
        model_lower = model_name.lower().strip()
        if not any(pattern in model_lower for pattern in valid_patterns):
            return ValidationResult(
                valid=False,
                errors=[f"Unknown model name: {model_name}"]
            )
        
        return ValidationResult()


class SchemaValidator:
    """Validates data against JSON schemas."""

    def __init__(self):
        pass

    def validate_json_schema(self, data: dict, schema: dict) -> ValidationResult:
        """Validate data against JSON schema."""
        try:
            import jsonschema
            jsonschema.validate(data, schema)
            return ValidationResult()
        except ImportError:
            # Fallback basic validation if jsonschema not available
            return self._basic_schema_validation(data, schema)
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Schema validation failed: {str(e)}"]
            )

    def _basic_schema_validation(self, data: dict, schema: dict) -> ValidationResult:
        """Basic schema validation fallback."""
        errors = []
        
        # Check required fields
        required = schema.get('required', [])
        for field in required:
            if field not in data:
                errors.append(f"Required field '{field}' is missing")
        
        # Check property types
        properties = schema.get('properties', {})
        for field, value in data.items():
            if field in properties:
                expected_type = properties[field].get('type')
                if expected_type == 'string' and not isinstance(value, str):
                    errors.append(f"Field '{field}' must be a string")
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"Field '{field}' must be a number")
                elif expected_type == 'object' and not isinstance(value, dict):
                    errors.append(f"Field '{field}' must be an object")
                elif expected_type == 'array' and not isinstance(value, list):
                    errors.append(f"Field '{field}' must be an array")
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        return ValidationResult()

    def validate_workflow_output_schema(self, output: dict) -> ValidationResult:
        """Validate workflow output against expected schema."""
        # Define expected workflow output schema
        schema = {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
                "status": {"type": "string"},
                "metadata": {"type": "object"},
                "execution_time": {"type": "number"},
                "step_results": {"type": "array"}
            },
            "required": ["result", "status"]
        }
        
        return self.validate_json_schema(output, schema)


class StepValidator:
    """Validates workflow steps."""

    def __init__(self):
        self.param_validator = ParameterValidator()

    def validate_step(self, step: dict) -> ValidationResult:
        """Validate a workflow step."""
        errors = []
        
        # Check required fields
        required_fields = ['id', 'name', 'type']
        for field in required_fields:
            if field not in step:
                errors.append(f"Step missing required field: {field}")
        
        # Validate step ID
        if 'id' in step:
            if not isinstance(step['id'], str) or not step['id'].strip():
                errors.append("Step ID must be a non-empty string")
        
        # Validate step name
        if 'name' in step:
            if not isinstance(step['name'], str) or not step['name'].strip():
                errors.append("Step name must be a non-empty string")
        
        # Validate step type
        if 'type' in step:
            valid_types = ['input', 'llm_call', 'condition', 'aggregator', 'tool_call', 'output']
            if step['type'] not in valid_types:
                errors.append(f"Invalid step type: {step['type']}")
        
        # Validate type-specific requirements
        if 'type' in step and 'config' in step:
            if step['type'] == 'llm_call':
                llm_result = self.validate_llm_call_step(step)
                if not llm_result.valid:
                    errors.extend(llm_result.errors)
            elif step['type'] == 'condition':
                condition_result = self.validate_condition_step(step)
                if not condition_result.valid:
                    errors.extend(condition_result.errors)
            elif step['type'] == 'tool_call':
                tool_result = self.validate_tool_call_step(step)
                if not tool_result.valid:
                    errors.extend(tool_result.errors)
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        return ValidationResult()

    def validate_llm_call_step(self, step: dict) -> ValidationResult:
        """Validate LLM call step specific requirements."""
        errors = []
        config = step.get('config', {})
        
        # Validate required LLM config
        if 'model' not in config:
            errors.append("LLM step requires 'model' in config")
        else:
            model_result = self.param_validator.validate_model_name(config['model'])
            if not model_result.valid:
                errors.extend(model_result.errors)
        
        # Validate optional parameters
        if 'temperature' in config:
            temp_result = self.param_validator.validate_temperature(config['temperature'])
            if not temp_result.valid:
                errors.extend(temp_result.errors)
        
        if 'max_tokens' in config:
            tokens_result = self.param_validator.validate_max_tokens(config['max_tokens'])
            if not tokens_result.valid:
                errors.extend(tokens_result.errors)
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        return ValidationResult()

    def validate_condition_step(self, step: dict) -> ValidationResult:
        """Validate condition step specific requirements."""
        errors = []
        config = step.get('config', {})
        
        # Condition step should have condition logic
        if 'condition' not in config:
            errors.append("Condition step requires 'condition' in config")
        
        if 'true_path' not in config and 'false_path' not in config:
            errors.append("Condition step requires at least one of 'true_path' or 'false_path'")
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        return ValidationResult()

    def validate_tool_call_step(self, step: dict) -> ValidationResult:
        """Validate tool call step specific requirements."""
        errors = []
        config = step.get('config', {})
        
        # Tool call step should specify tool
        if 'tool_name' not in config:
            errors.append("Tool call step requires 'tool_name' in config")
        
        if 'parameters' in config and not isinstance(config['parameters'], dict):
            errors.append("Tool parameters must be a dictionary")
        
        if errors:
            return ValidationResult(valid=False, errors=errors)
        return ValidationResult()
