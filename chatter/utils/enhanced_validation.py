"""Enhanced input validation and sanitization utilities."""

import re
from typing import Any

from pydantic import BaseModel, validator

from chatter.core.exceptions import ValidationError
from chatter.utils.security import sanitize_input


class ValidationConfig:
    """Configuration for validation rules."""

    # Maximum lengths for different field types
    MAX_NAME_LENGTH = 100
    MAX_DISPLAY_NAME_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_URL_LENGTH = 500
    MAX_PATH_LENGTH = 500
    MAX_VERSION_LENGTH = 100
    MAX_INDEX_TYPE_LENGTH = 50

    # Patterns for field validation
    NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
    TABLE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")
    URL_PATTERN = re.compile(
        r"^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*)?(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?$"
    )

    # Numeric limits
    MAX_TOKENS = 1000000
    MAX_CONTEXT_LENGTH = 10000000
    MAX_DIMENSIONS = 10000
    MAX_CHUNK_SIZE = 100000
    MAX_BATCH_SIZE = 1000


def validate_name_field(value: str, field_name: str = "name") -> str:
    """Validate a name field.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        Validated and sanitized value

    Raises:
        ValidationError: If validation fails
    """
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")

    # Sanitize input
    sanitized = sanitize_input(value, ValidationConfig.MAX_NAME_LENGTH)

    if len(sanitized) < 1:
        raise ValidationError(f"{field_name} must be at least 1 character long")

    if len(sanitized) > ValidationConfig.MAX_NAME_LENGTH:
        raise ValidationError(
            f"{field_name} must be at most {ValidationConfig.MAX_NAME_LENGTH} characters long"
        )

    if not ValidationConfig.NAME_PATTERN.match(sanitized):
        raise ValidationError(
            f"{field_name} must contain only letters, numbers, hyphens, and underscores"
        )

    return sanitized


def validate_display_name(value: str, field_name: str = "display_name") -> str:
    """Validate a display name field.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        Validated and sanitized value

    Raises:
        ValidationError: If validation fails
    """
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")

    # Sanitize input
    sanitized = sanitize_input(value, ValidationConfig.MAX_DISPLAY_NAME_LENGTH)

    if len(sanitized) < 1:
        raise ValidationError(f"{field_name} must be at least 1 character long")

    if len(sanitized) > ValidationConfig.MAX_DISPLAY_NAME_LENGTH:
        raise ValidationError(
            f"{field_name} must be at most {ValidationConfig.MAX_DISPLAY_NAME_LENGTH} characters long"
        )

    return sanitized


def validate_description(value: str | None, field_name: str = "description") -> str | None:
    """Validate a description field.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        Validated and sanitized value

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        return None

    # Sanitize input
    sanitized = sanitize_input(value, ValidationConfig.MAX_DESCRIPTION_LENGTH)

    if len(sanitized) > ValidationConfig.MAX_DESCRIPTION_LENGTH:
        raise ValidationError(
            f"{field_name} must be at most {ValidationConfig.MAX_DESCRIPTION_LENGTH} characters long"
        )

    return sanitized if sanitized else None


def validate_url(value: str | None, field_name: str = "url") -> str | None:
    """Validate a URL field.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        Validated value

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        return None

    if not value.strip():
        return None

    # Basic length check
    if len(value) > ValidationConfig.MAX_URL_LENGTH:
        raise ValidationError(
            f"{field_name} must be at most {ValidationConfig.MAX_URL_LENGTH} characters long"
        )

    # Validate URL format
    if not ValidationConfig.URL_PATTERN.match(value):
        raise ValidationError(f"{field_name} must be a valid HTTP/HTTPS URL")

    return value


def validate_positive_integer(
    value: int | None,
    field_name: str,
    max_value: int | None = None,
    min_value: int = 1,
) -> int | None:
    """Validate a positive integer field.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        max_value: Maximum allowed value
        min_value: Minimum allowed value

    Returns:
        Validated value

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        return None

    if not isinstance(value, int):
        raise ValidationError(f"{field_name} must be an integer")

    if value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}")

    if max_value is not None and value > max_value:
        raise ValidationError(f"{field_name} must be at most {max_value}")

    return value


def validate_table_name(value: str, field_name: str = "table_name") -> str:
    """Validate a database table name.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        Validated value

    Raises:
        ValidationError: If validation fails
    """
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")

    # Sanitize input
    sanitized = sanitize_input(value, ValidationConfig.MAX_NAME_LENGTH)

    if len(sanitized) < 1:
        raise ValidationError(f"{field_name} must be at least 1 character long")

    if len(sanitized) > ValidationConfig.MAX_NAME_LENGTH:
        raise ValidationError(
            f"{field_name} must be at most {ValidationConfig.MAX_NAME_LENGTH} characters long"
        )

    if not ValidationConfig.TABLE_NAME_PATTERN.match(sanitized):
        raise ValidationError(
            f"{field_name} must contain only letters, numbers, and underscores"
        )

    # Additional database safety checks
    if sanitized.lower() in {
        "user", "users", "admin", "root", "system", "database", "schema",
        "table", "index", "view", "procedure", "function", "trigger",
        "select", "insert", "update", "delete", "drop", "create", "alter",
    }:
        raise ValidationError(f"{field_name} cannot be a reserved word")

    return sanitized


def validate_config_dict(value: dict[str, Any] | None) -> dict[str, Any] | None:
    """Validate a configuration dictionary.

    Args:
        value: Configuration dictionary to validate

    Returns:
        Validated configuration

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        return {}

    if not isinstance(value, dict):
        raise ValidationError("Configuration must be a dictionary")

    # Check for deeply nested structures that could cause issues
    def check_depth(obj: Any, depth: int = 0, max_depth: int = 10) -> None:
        if depth > max_depth:
            raise ValidationError("Configuration structure is too deeply nested")

        if isinstance(obj, dict):
            for v in obj.values():
                check_depth(v, depth + 1, max_depth)
        elif isinstance(obj, list):
            for item in obj:
                check_depth(item, depth + 1, max_depth)

    try:
        check_depth(value)
    except RecursionError:
        raise ValidationError("Configuration structure contains circular references") from None

    # Basic size check (serialized JSON size)
    import json
    try:
        serialized = json.dumps(value)
        if len(serialized) > 10000:  # 10KB limit
            raise ValidationError("Configuration data is too large")
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Configuration contains invalid data: {e}") from e

    return value


class SecureBaseModel(BaseModel):
    """Base model with enhanced security validation."""

    class Config:
        """Pydantic configuration."""
        # Validate all fields by default
        validate_all = True
        # Don't allow extra fields
        extra = "forbid"
        # Use enum values
        use_enum_values = True
        # Validate assignment
        validate_assignment = True

    @validator("*", pre=True)
    def sanitize_strings(cls, v):
        """Sanitize string inputs."""
        if isinstance(v, str):
            return sanitize_input(v)
        return v


class RequestSizeValidator:
    """Validator for request size limits."""

    def __init__(self, max_size_bytes: int = 1024 * 1024):  # 1MB default
        """Initialize validator.

        Args:
            max_size_bytes: Maximum request size in bytes
        """
        self.max_size_bytes = max_size_bytes

    def validate_request_size(self, content_length: int | None) -> None:
        """Validate request size.

        Args:
            content_length: Content length header value

        Raises:
            ValidationError: If request is too large
        """
        if content_length is None:
            return

        if content_length > self.max_size_bytes:
            raise ValidationError(
                f"Request size ({content_length} bytes) exceeds maximum "
                f"allowed size ({self.max_size_bytes} bytes)"
            )


def validate_model_consistency(
    model_type: str,
    dimensions: int | None,
    max_tokens: int | None,
    max_batch_size: int | None,
    supports_batch: bool | None,
) -> None:
    """Validate model configuration consistency.

    Args:
        model_type: Type of model
        dimensions: Model dimensions
        max_tokens: Maximum tokens
        max_batch_size: Maximum batch size
        supports_batch: Whether model supports batching

    Raises:
        ValidationError: If configuration is inconsistent
    """
    # Import here to avoid circular dependency
    from chatter.models.registry import ModelType

    if model_type == ModelType.EMBEDDING.value:
        if not dimensions or dimensions <= 0:
            raise ValidationError("Embedding models must specify dimensions > 0")
    elif model_type == ModelType.LLM.value:
        if dimensions is not None:
            raise ValidationError("LLM models should not specify dimensions")

    # Validate token limits
    if max_tokens is not None:
        validate_positive_integer(
            max_tokens, "max_tokens", ValidationConfig.MAX_TOKENS
        )

    # Validate batch configuration
    if max_batch_size is not None:
        validate_positive_integer(
            max_batch_size, "max_batch_size", ValidationConfig.MAX_BATCH_SIZE
        )

        if not supports_batch:
            raise ValidationError(
                "max_batch_size specified but supports_batch is False"
            )


def validate_embedding_space_consistency(
    model_dimensions: int,
    base_dimensions: int,
    effective_dimensions: int,
) -> None:
    """Validate embedding space dimensional consistency.

    Args:
        model_dimensions: Model's dimension count
        base_dimensions: Base dimensions
        effective_dimensions: Effective dimensions after reduction

    Raises:
        ValidationError: If dimensions are inconsistent
    """
    if base_dimensions != model_dimensions:
        raise ValidationError(
            f"Base dimensions ({base_dimensions}) must match "
            f"model dimensions ({model_dimensions})"
        )

    if effective_dimensions > base_dimensions:
        raise ValidationError(
            "Effective dimensions cannot be greater than base dimensions"
        )

    if effective_dimensions <= 0:
        raise ValidationError("Effective dimensions must be positive")
