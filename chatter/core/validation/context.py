"""Validation context for providing metadata and configuration."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from chatter.config import settings


class ValidationMode(Enum):
    """Validation modes."""

    STRICT = "strict"  # Fail on any validation error
    LENIENT = "lenient"  # Allow minor validation issues
    SANITIZE = "sanitize"  # Attempt to sanitize and fix issues


@dataclass
class ValidationContext:
    """Context information for validation operations."""

    # Core context
    user_id: str | None = None
    session_id: str | None = None
    request_id: str | None = None

    # Validation configuration
    mode: ValidationMode = ValidationMode.STRICT
    sanitize_input: bool = True
    check_security: bool = True

    # Feature flags
    enabled_validators: set[str] = field(
        default_factory=lambda: {
            "input",
            "security",
            "business",
            "config",
            "workflow",
            "agent",
        }
    )
    disabled_rules: set[str] = field(default_factory=set)

    # Custom configuration
    max_length_overrides: dict[str, int] = field(default_factory=dict)
    custom_patterns: dict[str, str] = field(default_factory=dict)
    extra_context: dict[str, Any] = field(default_factory=dict)

    # Performance settings
    timeout_seconds: int = field(
        default_factory=lambda: settings.validation_timeout
    )
    max_recursion_depth: int = 10

    def is_validator_enabled(self, validator_name: str) -> bool:
        """Check if a validator is enabled."""
        return validator_name in self.enabled_validators

    def is_rule_disabled(self, rule_name: str) -> bool:
        """Check if a rule is disabled."""
        return rule_name in self.disabled_rules

    def get_max_length(self, field_name: str, default: int) -> int:
        """Get max length for a field with override support."""
        return self.max_length_overrides.get(field_name, default)

    def get_custom_pattern(self, pattern_name: str) -> str | None:
        """Get custom pattern if defined."""
        return self.custom_patterns.get(pattern_name)

    def with_overrides(self, **kwargs: Any) -> "ValidationContext":
        """Create a new context with overrides."""
        # Create a copy of current context
        new_context = ValidationContext(
            user_id=self.user_id,
            session_id=self.session_id,
            request_id=self.request_id,
            mode=self.mode,
            sanitize_input=self.sanitize_input,
            check_security=self.check_security,
            enabled_validators=self.enabled_validators.copy(),
            disabled_rules=self.disabled_rules.copy(),
            max_length_overrides=self.max_length_overrides.copy(),
            custom_patterns=self.custom_patterns.copy(),
            extra_context=self.extra_context.copy(),
            timeout_seconds=self.timeout_seconds,
            max_recursion_depth=self.max_recursion_depth,
        )

        # Apply overrides
        for key, value in kwargs.items():
            if hasattr(new_context, key):
                setattr(new_context, key, value)

        return new_context


# Default contexts for common scenarios
DEFAULT_CONTEXT = ValidationContext()

LENIENT_CONTEXT = ValidationContext(
    mode=ValidationMode.LENIENT,
    sanitize_input=True,
    check_security=True,
)

STRICT_CONTEXT = ValidationContext(
    mode=ValidationMode.STRICT,
    sanitize_input=False,
    check_security=True,
)

SANITIZE_CONTEXT = ValidationContext(
    mode=ValidationMode.SANITIZE,
    sanitize_input=True,
    check_security=True,
)
