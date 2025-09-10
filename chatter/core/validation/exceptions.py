"""Unified validation exceptions hierarchy."""

from typing import Any


class ValidationError(Exception):
    """Base validation error."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
        code: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value
        self.code = code
        self.context = context or {}

    def __str__(self) -> str:
        if self.field:
            return f"Validation error for field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class SecurityValidationError(ValidationError):
    """Security-related validation error."""

    def __init__(
        self, message: str, threat_type: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.threat_type = threat_type
        self.code = self.code or "SECURITY_VIOLATION"


class BusinessValidationError(ValidationError):
    """Business logic validation error."""

    def __init__(
        self, message: str, rule_name: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.rule_name = rule_name
        self.code = self.code or "BUSINESS_RULE_VIOLATION"


class ConfigurationValidationError(ValidationError):
    """Configuration validation error."""

    def __init__(
        self, message: str, config_key: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.code = self.code or "CONFIGURATION_ERROR"


class ValidationErrors(Exception):
    """Container for multiple validation errors."""

    def __init__(self, errors: list[ValidationError]):
        self.errors = errors
        message = f"Multiple validation errors ({len(errors)})"
        super().__init__(message)

    def __str__(self) -> str:
        error_messages = [str(error) for error in self.errors]
        return "\n".join(error_messages)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format for API responses."""
        return {
            "type": "validation_errors",
            "message": f"Validation failed with {len(self.errors)} error(s)",
            "errors": [
                {
                    "field": error.field,
                    "message": error.message,
                    "code": error.code,
                    "value": error.value,
                    "context": error.context,
                }
                for error in self.errors
            ],
        }
