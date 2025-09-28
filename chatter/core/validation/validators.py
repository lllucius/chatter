"""Base validator classes and concrete validator implementations."""

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

from ulid import ULID

from chatter.config import settings
from chatter.core.exceptions import (
    BusinessValidationError,
    SecurityValidationError,
    ValidationError,
)
from chatter.utils.logging import get_logger

from .context import ValidationContext
from .results import ValidationResult

logger = get_logger(__name__)


class BaseValidator(ABC):
    """Base class for all validators."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.supported_rules: list[str] = []

    @abstractmethod
    def validate(
        self,
        value: Any,
        rule: str | list[str],
        context: ValidationContext,
    ) -> ValidationResult:
        """Validate a value according to the specified rule(s)."""
        pass

    def sanitize(self, value: Any, context: ValidationContext) -> Any:
        """Sanitize a value. Override in subclasses if needed."""
        return value


class ValidationRule:
    """Represents a validation rule configuration."""

    def __init__(
        self,
        name: str,
        pattern: str | None = None,
        max_length: int | None = None,
        min_length: int | None = None,
        required: bool = False,
        allowed_chars: str | None = None,
        forbidden_patterns: list[str] | None = None,
        sanitize: bool = False,
        custom_validator: Callable[[Any], bool] | None = None,
    ):
        self.name = name
        self.pattern = pattern
        self.max_length = max_length
        self.min_length = min_length
        self.required = required
        self.allowed_chars = allowed_chars
        self.forbidden_patterns = forbidden_patterns or []
        self.sanitize = sanitize
        self.custom_validator = custom_validator


class InputValidator(BaseValidator):
    """Validates and sanitizes user input."""

    def __init__(self) -> None:
        super().__init__(
            "input",
            "Validates user input according to predefined rules",
        )
        self.rules: dict[str, ValidationRule] = {}
        self._setup_default_rules()
        self.supported_rules = list(self.rules.keys())

    def _setup_default_rules(self) -> None:
        """Setup default validation rules."""
        self.rules.update(
            {
                "text": ValidationRule(
                    name="text",
                    max_length=10000,
                    forbidden_patterns=[
                        r"<script.*?>.*?</script>",
                        r"javascript:",
                        r"on\w+\s*=",
                    ],
                    sanitize=True,
                ),
                "message": ValidationRule(
                    name="message",
                    max_length=5000,
                    min_length=1,
                    required=True,
                    forbidden_patterns=[
                        r"<script.*?>.*?</script>",
                        r"javascript:",
                        r"on\w+\s*=",
                    ],
                    sanitize=True,
                ),
                "username": ValidationRule(
                    name="username",
                    pattern=r"^[a-zA-Z0-9_-]{3,50}$",
                    max_length=settings.max_name_length,
                    min_length=3,
                    required=True,
                    allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
                ),
                "email": ValidationRule(
                    name="email",
                    pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    max_length=254,
                    required=True,
                ),
                "password": ValidationRule(
                    name="password",
                    min_length=8,
                    max_length=128,
                    required=True,
                ),
                "url": ValidationRule(
                    name="url",
                    pattern=r"^https?://[^\s/$.?#].[^\s]*$",
                    max_length=2048,
                    sanitize=True,
                ),
                "filename": ValidationRule(
                    name="filename",
                    pattern=r"^[a-zA-Z0-9._-]+\.[a-zA-Z0-9]+$",
                    max_length=255,
                    forbidden_patterns=[r"\.\./", r"\\", r"/"],
                    sanitize=True,
                ),
                "api_key": ValidationRule(
                    name="api_key",
                    pattern=r"^[a-zA-Z0-9_-]{16,128}$",
                    min_length=16,
                    max_length=128,
                    required=True,
                ),
                "agent_name": ValidationRule(
                    name="agent_name",
                    max_length=settings.max_description_length,
                    min_length=1,
                    required=True,
                    forbidden_patterns=[
                        r"<script.*?>.*?</script>",
                        r"javascript:",
                        r"on\w+\s*=",
                    ],
                    sanitize=True,
                ),
                "agent_id": ValidationRule(
                    name="agent_id",
                    pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
                    max_length=36,
                    min_length=36,
                    required=True,
                ),
                "conversation_id": ValidationRule(
                    name="conversation_id",
                    pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
                    max_length=36,
                    min_length=36,
                    required=True,
                ),
            }
        )

    def validate(
        self,
        value: Any,
        rule: str | list[str],
        context: ValidationContext,
    ) -> ValidationResult:
        """Validate input according to the specified rule(s)."""
        # Handle multiple rules
        if isinstance(rule, list):
            errors = []
            for single_rule in rule:
                result = self.validate(value, single_rule, context)
                if not result.is_valid:
                    errors.extend(result.errors)
            return ValidationResult(
                is_valid=len(errors) == 0, value=value, errors=errors
            )

        # Handle single rule
        if rule not in self.rules:
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(f"Unknown validation rule: {rule}")
                ],
            )

        validation_rule = self.rules[rule]

        # Convert to string
        if value is None:
            if validation_rule.required:
                return ValidationResult(
                    is_valid=False,
                    errors=[ValidationError(f"{rule} is required")],
                )
            return ValidationResult(is_valid=True, value="")

        str_value = str(value)

        # Check required and length
        if validation_rule.required and not str_value.strip():
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(f"{rule} is required")],
            )

        # Apply context overrides for max length
        max_length = None
        if validation_rule.max_length is not None:
            max_length = context.get_max_length(
                rule, validation_rule.max_length
            )
        if max_length and len(str_value) > max_length:
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        f"{rule} exceeds maximum length of {max_length}"
                    )
                ],
            )

        if (
            validation_rule.min_length
            and len(str_value) < validation_rule.min_length
        ):
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        f"{rule} is below minimum length of {validation_rule.min_length}"
                    )
                ],
            )

        # Check pattern
        pattern = (
            context.get_custom_pattern(rule) or validation_rule.pattern
        )
        if pattern and not re.match(pattern, str_value):
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        f"{rule} does not match required pattern"
                    )
                ],
            )

        # Check allowed characters
        if validation_rule.allowed_chars:
            for char in str_value:
                if char not in validation_rule.allowed_chars:
                    return ValidationResult(
                        is_valid=False,
                        errors=[
                            ValidationError(
                                f"{rule} contains invalid character: {char}"
                            )
                        ],
                    )

        # Check forbidden patterns
        for pattern in validation_rule.forbidden_patterns:
            if re.search(pattern, str_value, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    errors=[
                        SecurityValidationError(
                            f"{rule} contains forbidden pattern"
                        )
                    ],
                )

        # Sanitize if needed and enabled
        if validation_rule.sanitize and context.sanitize_input:
            str_value = self._sanitize_value(str_value)

        return ValidationResult(is_valid=True, value=str_value)

    def _sanitize_value(self, value: str) -> str:
        """Sanitize input value."""
        # Remove HTML tags
        value = re.sub(r"<[^>]+>", "", value)
        # Remove null bytes
        value = value.replace("\x00", "")
        # Remove control characters except newlines and tabs
        value = re.sub(r"[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]", "", value)
        # Normalize whitespace
        value = re.sub(r"\s+", " ", value).strip()
        return value


class SecurityValidator(BaseValidator):
    """Validates input for security threats."""

    def __init__(self) -> None:
        super().__init__(
            "security", "Validates input for security threats"
        )
        self.supported_rules = [
            "security_check",
            "xss_check",
            "sql_injection_check",
            "path_traversal_check",
        ]

        self.sql_injection_patterns = [
            r"(\%27)|(\')\s*;\s*",  # Quote followed by semicolon (more specific)
            r"((\\%3D)|(=))[^\n]*((\\%27)|(\')|(\-\-)|(%23)|(#))",
            r"/\*(.|\n)*?\*/\s*;\s*",  # SQL comments followed by semicolon
            r"union\s+select",  # UNION SELECT attacks
            r"drop\s+table",  # DROP TABLE attacks
            r"insert\s+into",  # INSERT INTO attacks (when not legitimate)
        ]

        self.xss_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"on\w+\s*=",
            r"<iframe.*?>",
            r"<object.*?>",
            r"<embed.*?>",
        ]

        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e\\",
        ]

    def validate(
        self,
        value: Any,
        rule: str | list[str],
        context: ValidationContext,
    ) -> ValidationResult:
        """Validate input for security threats."""
        # Handle multiple rules
        if isinstance(rule, list):
            errors = []
            for single_rule in rule:
                result = self.validate(value, single_rule, context)
                if not result.is_valid:
                    errors.extend(result.errors)
            return ValidationResult(
                is_valid=len(errors) == 0, value=value, errors=errors
            )

        # Handle single rule
        if not isinstance(value, str):
            return ValidationResult(is_valid=True, value=value)

        errors = []

        if rule in ["security_check", "sql_injection_check"]:
            if self._detect_sql_injection(value):
                errors.append(
                    SecurityValidationError(
                        "Potential SQL injection detected",
                        threat_type="sql_injection",
                    )
                )

        if rule in ["security_check", "xss_check"]:
            if self._detect_xss(value):
                errors.append(
                    SecurityValidationError(
                        "Potential XSS attempt detected",
                        threat_type="xss",
                    )
                )

        if rule in ["security_check", "path_traversal_check"]:
            if self._detect_path_traversal(value):
                errors.append(
                    SecurityValidationError(
                        "Potential path traversal detected",
                        threat_type="path_traversal",
                    )
                )

        if errors:
            # Cast to base ValidationError list type
            return ValidationResult(is_valid=False, errors=list(errors))

        # Sanitize if enabled
        sanitized_value = value
        if context.sanitize_input:
            sanitized_value = self._sanitize_security_threats(value)

        return ValidationResult(is_valid=True, value=sanitized_value)

    def _detect_sql_injection(self, value: str) -> bool:
        """Detect potential SQL injection attempts."""
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def _detect_xss(self, value: str) -> bool:
        """Detect potential XSS attempts."""
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def _detect_path_traversal(self, value: str) -> bool:
        """Detect potential path traversal attempts."""
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def _sanitize_security_threats(self, value: str) -> str:
        """Remove security threats from input."""
        # Remove script tags
        value = re.sub(
            r"<script[^>]*>.*?</script>",
            "",
            value,
            flags=re.IGNORECASE | re.DOTALL,
        )
        # Remove javascript: URLs
        value = re.sub(
            r"javascript\s*:", "", value, flags=re.IGNORECASE
        )
        # Remove event handlers
        value = re.sub(
            r'on\w+\s*=\s*["\'][^"\']*["\']',
            "",
            value,
            flags=re.IGNORECASE,
        )
        # Remove path traversal
        value = re.sub(r"\.\./", "", value)
        return value


class BusinessValidator(BaseValidator):
    """Validates business logic rules."""

    def __init__(self) -> None:
        super().__init__("business", "Validates business logic rules")
        self.supported_rules = [
            "model_consistency",
            "embedding_space",
            "provider_rules",
        ]

    def validate(
        self,
        value: Any,
        rule: str | list[str],
        context: ValidationContext,
    ) -> ValidationResult:
        """Validate business logic rules."""

        # Handle multiple rules
        if isinstance(rule, list):
            errors = []
            for single_rule in rule:
                result = self._validate_single_rule(
                    value, single_rule, context
                )
                if not result.is_valid:
                    errors.extend(result.errors)
            return ValidationResult(
                is_valid=len(errors) == 0, value=value, errors=errors
            )
        else:
            return self._validate_single_rule(value, rule, context)

    def _validate_single_rule(
        self, value: Any, rule: str, context: ValidationContext
    ) -> ValidationResult:
        """Validate a single business rule."""

        if rule == "model_consistency":
            return self._validate_model_consistency(value, context)
        elif rule == "embedding_space":
            return self._validate_embedding_space(value, context)
        elif rule == "provider_rules":
            return self._validate_provider_rules(value, context)
        else:
            return ValidationResult(
                is_valid=False,
                errors=[
                    BusinessValidationError(
                        f"Unknown business rule: {rule}"
                    )
                ],
            )

    def _validate_model_consistency(
        self, data: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate model configuration consistency."""

        errors = []
        model_type = data.get("model_type")
        dimensions = data.get("dimensions")
        data.get("max_tokens")
        supports_batch = data.get("supports_batch")
        max_batch_size = data.get("max_batch_size")

        # Embedding models must have dimensions
        if model_type == "EMBEDDING" and not dimensions:
            errors.append(
                BusinessValidationError(
                    "Embedding models must specify dimensions > 0",
                    rule_name="model_consistency",
                )
            )

        # LLM models should not have dimensions
        if model_type == "LLM" and dimensions:
            errors.append(
                BusinessValidationError(
                    "LLM models should not specify dimensions",
                    rule_name="model_consistency",
                )
            )

        # Validate batch configuration
        if max_batch_size and not supports_batch:
            errors.append(
                BusinessValidationError(
                    "max_batch_size specified but supports_batch is False",
                    rule_name="model_consistency",
                )
            )

        return ValidationResult(
            is_valid=len(errors) == 0, value=data, errors=errors
        )

    def _validate_embedding_space(
        self, data: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate embedding space consistency."""

        errors = []
        model_dimensions = data.get("model_dimensions")
        base_dimensions = data.get("base_dimensions")
        effective_dimensions = data.get("effective_dimensions")

        if base_dimensions != model_dimensions:
            errors.append(
                BusinessValidationError(
                    f"Base dimensions ({base_dimensions}) must match model dimensions ({model_dimensions})",
                    rule_name="embedding_space",
                )
            )

        if (
            effective_dimensions
            and effective_dimensions > base_dimensions
        ):
            errors.append(
                BusinessValidationError(
                    "Effective dimensions cannot be greater than base dimensions",
                    rule_name="embedding_space",
                )
            )

        return ValidationResult(
            is_valid=len(errors) == 0, value=data, errors=errors
        )

    def _validate_provider_rules(
        self, data: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate provider-specific rules."""

        errors = []
        provider_name = data.get("name", "").lower()
        api_key = data.get("api_key", "")

        # Provider-specific validation rules
        if provider_name == "openai":
            if api_key and not api_key.startswith("sk-"):
                errors.append(
                    BusinessValidationError(
                        "OpenAI API keys must start with 'sk-'",
                        rule_name="provider_rules",
                    )
                )
        elif provider_name == "anthropic":
            if api_key and not api_key.startswith("sk-ant-"):
                errors.append(
                    BusinessValidationError(
                        "Anthropic API keys must start with 'sk-ant-'",
                        rule_name="provider_rules",
                    )
                )
        elif provider_name in ["cohere", "cohereai"]:
            if api_key and len(api_key) < 32:
                errors.append(
                    BusinessValidationError(
                        "Cohere API keys must be at least 32 characters",
                        rule_name="provider_rules",
                    )
                )

        # General validations for all providers
        if "api_key" in data and not api_key:
            errors.append(
                BusinessValidationError(
                    "API key cannot be empty",
                    rule_name="provider_rules",
                )
            )

        # Check required fields based on provider
        required_fields = data.get("required_fields", [])
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(
                    BusinessValidationError(
                        f"Required field '{field}' is missing or empty",
                        rule_name="provider_rules",
                    )
                )

        return ValidationResult(
            is_valid=len(errors) == 0, value=data, errors=errors
        )


class ConfigValidator(BaseValidator):
    """Validates configuration settings."""

    def __init__(self) -> None:
        super().__init__("config", "Validates configuration settings")
        self.supported_rules = [
            "database_config",
            "api_keys",
            "security_config",
        ]

    def validate(
        self,
        value: Any,
        rule: str | list[str],
        context: ValidationContext,
    ) -> ValidationResult:
        """Validate configuration settings."""
        # Handle multiple rules
        if isinstance(rule, list):
            errors = []
            for single_rule in rule:
                result = self.validate(value, single_rule, context)
                if not result.is_valid:
                    errors.extend(result.errors)
            return ValidationResult(
                is_valid=len(errors) == 0, value=value, errors=errors
            )

        # Handle single rule
        if rule == "database_config":
            return self._validate_database_config(value, context)
        elif rule == "api_keys":
            return self._validate_api_keys(value, context)
        elif rule == "security_config":
            return self._validate_security_config(value, context)
        else:
            return ValidationResult(is_valid=True, value=value)

    def _validate_database_config(
        self, config: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate database configuration."""

        errors = []
        database_url = config.get("DATABASE_URL", "")

        if not database_url:
            errors.append(ValidationError("DATABASE_URL is required"))
        else:
            try:
                parsed = urlparse(database_url)
                if not parsed.scheme or not parsed.hostname:
                    errors.append(
                        ValidationError(
                            "DATABASE_URL format is invalid"
                        )
                    )
            except Exception as e:
                errors.append(
                    ValidationError(
                        f"DATABASE_URL parsing failed: {str(e)}"
                    )
                )

        return ValidationResult(
            is_valid=len(errors) == 0, value=config, errors=errors
        )

    def _validate_api_keys(
        self, config: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate API keys."""

        errors = []

        for key_name in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
            if key_name in config:
                api_key = config[key_name]
                if not api_key or len(api_key) < 10:
                    errors.append(
                        ValidationError(f"{key_name} appears too short")
                    )
                elif api_key in ["your-api-key", "sk-test", "test-key"]:
                    errors.append(
                        ValidationError(
                            f"{key_name} appears to be a placeholder"
                        )
                    )

        return ValidationResult(
            is_valid=len(errors) == 0, value=config, errors=errors
        )

    def _validate_security_config(
        self, config: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate security configuration."""

        errors = []
        secret_key = config.get("SECRET_KEY", "")

        if len(secret_key) < 32:
            errors.append(
                ValidationError(
                    "SECRET_KEY too short (minimum 32 characters)"
                )
            )

        return ValidationResult(
            is_valid=len(errors) == 0, value=config, errors=errors
        )


class WorkflowValidator(BaseValidator):
    """Validates workflow configurations and definitions."""

    def __init__(self) -> None:
        super().__init__(
            "workflow", "Validates workflow configurations and definitions"
        )
        self.supported_rules = [
            "workflow_config",
            "workflow_request",
            "workflow_parameters",
            "workflow_definition",
        ]

    def validate(
        self,
        value: Any,
        rule: str | list[str],
        context: ValidationContext,
    ) -> ValidationResult:
        """Validate workflow configurations."""
        # Handle multiple rules
        if isinstance(rule, list):
            errors = []
            for single_rule in rule:
                result = self.validate(value, single_rule, context)
                if not result.is_valid:
                    errors.extend(result.errors)
            return ValidationResult(
                is_valid=len(errors) == 0, value=value, errors=errors
            )

        # Handle single rule
        if rule == "workflow_config":
            return self._validate_workflow_config(value, context)
        elif rule == "workflow_request":
            return self._validate_workflow_request(value, context)
        elif rule == "workflow_parameters":
            return self._validate_workflow_parameters(value, context)
        elif rule == "workflow_definition":
            return self._validate_workflow_definition(value, context)
        else:
            return ValidationResult(is_valid=True, value=value)

    def _validate_workflow_config(
        self, config: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate workflow configuration."""

        errors = []

        # Validate capability flags
        if any(
            key in config
            for key in [
                "enable_retrieval",
                "enable_tools",
                "enable_memory",
            ]
        ):
            # Validate capability flags
            if "enable_retrieval" in config and not isinstance(
                config["enable_retrieval"], bool
            ):
                errors.append(
                    ValidationError(
                        "enable_retrieval must be a boolean"
                    )
                )
            if "enable_tools" in config and not isinstance(
                config["enable_tools"], bool
            ):
                errors.append(
                    ValidationError("enable_tools must be a boolean")
                )
            if "enable_memory" in config and not isinstance(
                config["enable_memory"], bool
            ):
                errors.append(
                    ValidationError("enable_memory must be a boolean")
                )
        else:
            # Handle full workflow configuration validation
            required_fields = ["id", "name", "steps"]

            for field in required_fields:
                if field not in config:
                    errors.append(
                        ValidationError(
                            f"Workflow config missing required field: {field}"
                        )
                    )

        return ValidationResult(
            is_valid=len(errors) == 0, value=config, errors=errors
        )

    def _validate_workflow_request(
        self, request: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate workflow request."""

        errors = []
        message = request.get("message", "")

        if not message or not message.strip():
            errors.append(ValidationError("Message cannot be empty"))

        if len(message) > 10000:
            errors.append(
                ValidationError(
                    "Message too long (maximum 10000 characters)"
                )
            )

        return ValidationResult(
            is_valid=len(errors) == 0, value=request, errors=errors
        )

    def _validate_workflow_parameters(
        self, params: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate workflow parameters."""

        errors = []

        # Validate temperature
        if "temperature" in params:
            temp = params["temperature"]
            if (
                not isinstance(temp, int | float)
                or temp < 0.0
                or temp > 1.0
            ):
                errors.append(
                    ValidationError(
                        "Temperature must be between 0.0 and 1.0"
                    )
                )

        # Validate max_tokens
        if "max_tokens" in params:
            tokens = params["max_tokens"]
            if not isinstance(tokens, int) or tokens < 1:
                errors.append(
                    ValidationError(
                        "max_tokens must be a positive integer"
                    )
                )

        return ValidationResult(
            is_valid=len(errors) == 0, value=params, errors=errors
        )

    def _validate_workflow_definition(
        self, definition: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate a workflow definition structure."""
        errors = []
        warnings = []

        # Basic structure validation
        required_fields = ["name", "nodes", "edges"]
        for field in required_fields:
            if field not in definition:
                errors.append(
                    ValidationError(f"Missing required field: {field}")
                )
            elif field in ["nodes", "edges"] and not isinstance(definition[field], list):
                errors.append(
                    ValidationError(f"Field '{field}' must be a list")
                )
            elif field == "name" and not definition[field]:
                errors.append(
                    ValidationError(f"Missing required field: {field}")
                )

        # Validate name
        if "name" in definition:
            name = definition["name"]
            if not isinstance(name, str) or len(name.strip()) == 0:
                errors.append(
                    ValidationError(
                        "Workflow name must be a non-empty string"
                    )
                )
            elif len(name) > 255:
                errors.append(
                    ValidationError(
                        "Workflow name must be 255 characters or less"
                    )
                )

        # Validate nodes
        if "nodes" in definition and isinstance(definition["nodes"], list):
            if len(definition["nodes"]) == 0:
                warnings.append("Workflow has no nodes")
            else:
                node_errors, node_warnings = self._validate_nodes(
                    definition["nodes"]
                )
                errors.extend(node_errors)
                warnings.extend(node_warnings)

        # Validate edges
        if "edges" in definition and isinstance(definition["edges"], list):
            edge_errors, edge_warnings = self._validate_edges(
                definition["edges"], definition.get("nodes", [])
            )
            errors.extend(edge_errors)
            warnings.extend(edge_warnings)

        return ValidationResult(
            is_valid=len(errors) == 0,
            value=definition,
            errors=errors,
            warnings=warnings,
        )

    def _validate_nodes(self, nodes: list[dict]) -> tuple[list, list]:
        """Validate workflow nodes."""
        errors = []
        warnings = []
        node_ids = set()

        for i, node in enumerate(nodes):
            # Validate node structure
            if not isinstance(node, dict):
                errors.append(
                    ValidationError(f"Node {i} must be a dictionary")
                )
                continue

            # Check required fields
            required_node_fields = ["id", "type"]
            for field in required_node_fields:
                if field not in node:
                    errors.append(
                        ValidationError(
                            f"Node {i} missing required field: {field}"
                        )
                    )

            # Check for duplicate node IDs
            if "id" in node:
                node_id = node["id"]
                if node_id in node_ids:
                    errors.append(
                        ValidationError(f"Duplicate node ID: {node_id}")
                    )
                node_ids.add(node_id)

            # Validate node type
            if "type" in node:
                node_type = node["type"]
                valid_types = [
                    "start",
                    "end",
                    "llm",
                    "tool",
                    "conditional",
                    "passthrough",
                    "memory",
                    "retrieval", 
                    "model",
                ]
                if node_type not in valid_types:
                    warnings.append(
                        f"Node {i} has unknown type: {node_type}"
                    )

        return errors, warnings

    def _validate_edges(
        self, edges: list[dict], nodes: list[dict]
    ) -> tuple[list, list]:
        """Validate workflow edges."""
        errors = []
        warnings = []
        
        # Get valid node IDs
        node_ids = {node.get("id") for node in nodes if "id" in node}

        for i, edge in enumerate(edges):
            # Validate edge structure
            if not isinstance(edge, dict):
                errors.append(
                    ValidationError(f"Edge {i} must be a dictionary")
                )
                continue

            # Check required fields
            required_edge_fields = ["source", "target"]
            for field in required_edge_fields:
                if field not in edge:
                    errors.append(
                        ValidationError(
                            f"Edge {i} missing required field: {field}"
                        )
                    )

            # Validate source and target exist in nodes
            if "source" in edge and edge["source"] not in node_ids:
                errors.append(
                    ValidationError(
                        f"Edge {i} source '{edge['source']}' not found in nodes"
                    )
                )

            if "target" in edge and edge["target"] not in node_ids:
                errors.append(
                    ValidationError(
                        f"Edge {i} target '{edge['target']}' not found in nodes"
                    )
                )

        return errors, warnings


class AgentValidator(BaseValidator):
    """Validates agent-specific input."""

    def __init__(self) -> None:
        super().__init__("agent", "Validates agent-specific input")
        self.supported_rules = [
            "agent_input",
            "agent_id",
            "conversation_id",
            "agent_name",
        ]

    def validate(
        self,
        value: Any,
        rule: str | list[str],
        context: ValidationContext,
    ) -> ValidationResult:
        """Validate agent-specific input."""
        # Handle multiple rules
        if isinstance(rule, list):
            errors = []
            for single_rule in rule:
                result = self.validate(value, single_rule, context)
                if not result.is_valid:
                    errors.extend(result.errors)
            return ValidationResult(
                is_valid=len(errors) == 0, value=value, errors=errors
            )

        # Handle single rule
        if rule == "agent_id":
            return self._validate_agent_id(value, context)
        elif rule == "conversation_id":
            return self._validate_conversation_id(value, context)
        elif rule == "agent_name":
            return self._validate_agent_name(value, context)
        elif rule == "agent_input":
            return self._validate_agent_input(value, context)
        else:
            return ValidationResult(is_valid=True, value=value)

    def _validate_agent_id(
        self, agent_id: str, context: ValidationContext
    ) -> ValidationResult:
        """Validate agent ID."""

        if not agent_id or not isinstance(agent_id, str):
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Agent ID is required")],
            )

        try:
            ULID.from_str(agent_id.strip())
            return ValidationResult(
                is_valid=True, value=agent_id.strip()
            )
        except ValueError:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Invalid agent ID format")],
            )

    def _validate_conversation_id(
        self, conversation_id: str, context: ValidationContext
    ) -> ValidationResult:
        """Validate conversation ID."""

        if not conversation_id or not isinstance(conversation_id, str):
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Conversation ID is required")],
            )

        try:
            ULID.from_str(conversation_id.strip())
            return ValidationResult(
                is_valid=True, value=conversation_id.strip()
            )
        except ValueError:
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError("Invalid conversation ID format")
                ],
            )

    def _validate_agent_name(
        self, name: str, context: ValidationContext
    ) -> ValidationResult:
        """Validate agent name."""

        if not name or not isinstance(name, str):
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Agent name is required")],
            )

        name = name.strip()

        if len(name) < 1:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Agent name cannot be empty")],
            )

        if len(name) > settings.max_agent_name_length:
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        f"Agent name too long (max {settings.max_agent_name_length} characters)"
                    )
                ],
            )

        return ValidationResult(is_valid=True, value=name)

    def _validate_agent_input(
        self, data: dict[str, Any], context: ValidationContext
    ) -> ValidationResult:
        """Validate agent input data."""

        errors = []

        if "agent_id" in data:
            result = self._validate_agent_id(data["agent_id"], context)
            if not result.is_valid:
                errors.extend(result.errors)

        if "name" in data:
            result = self._validate_agent_name(data["name"], context)
            if not result.is_valid:
                errors.extend(result.errors)

        return ValidationResult(
            is_valid=len(errors) == 0, value=data, errors=errors
        )
