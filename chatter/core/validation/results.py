"""Validation result classes."""

from collections.abc import Sequence
from typing import Any

from chatter.core.exceptions import ValidationError


class ValidationResult:
    """Result of a validation operation."""

    def __init__(
        self,
        is_valid: bool = True,
        value: Any = None,
        errors: Sequence[ValidationError] | None = None,
        warnings: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.is_valid = is_valid
        self.value = value
        self.errors = list(errors) if errors else []
        self.warnings = warnings or []
        self.metadata = metadata or {}

    @property
    def valid(self) -> bool:
        """Alias for is_valid for backward compatibility."""
        return self.is_valid

    @property
    def requirements_met(self) -> bool:
        """Alias for is_valid for backward compatibility."""
        return self.is_valid

    def add_error(self, error: ValidationError) -> None:
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a validation warning."""
        self.warnings.append(warning)

    def merge(self, other: "ValidationResult") -> None:
        """Merge another validation result into this one."""
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.metadata.update(other.metadata)

    def has_errors(self) -> bool:
        """Check if result has any errors.
        
        Returns:
            True if errors exist
        """
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if result has any warnings.
        
        Returns:
            True if warnings exist
        """
        return len(self.warnings) > 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "is_valid": self.is_valid,
            "errors": [str(e) for e in self.errors],
            "warnings": self.warnings,
            "metadata": self.metadata,
        }

    def to_api_response(self) -> dict[str, Any]:
        """Convert to API response format.
        
        Returns:
            API-friendly dictionary
        """
        return {
            "valid": self.is_valid,
            "errors": [str(e) for e in self.errors],
            "warnings": self.warnings,
            "details": self.metadata,
        }
