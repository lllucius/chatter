"""Input validation middleware for API security."""

import html
import re
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import HTTPException, Request
from starlette.responses import Response

from chatter.config import settings
from chatter.schemas.utilities import ValidationRule
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom validation error for input validation."""

    pass


class InputValidator:
    """Input validation and sanitization engine."""

    def __init__(self) -> None:
        """Initialize the input validator."""
        self.rules: dict[str, ValidationRule] = {}
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Setup default validation rules."""
        # Text input rules
        self.rules["text"] = ValidationRule(
            name="text",
            max_length=10000,
            forbidden_patterns=[
                r"<script.*?>.*?</script>",  # Script tags
                r"javascript:",  # JavaScript URLs
                r"on\w+\s*=",  # Event handlers
                r"<iframe.*?>.*?</iframe>",  # Iframe tags
                r"<object.*?>.*?</object>",  # Object tags
                r"<embed.*?>.*?</embed>",  # Embed tags
            ],
            sanitize=True,
        )

        # Chat message rules
        self.rules["message"] = ValidationRule(
            name="message",
            max_length=5000,
            min_length=1,
            forbidden_patterns=[
                r"<script.*?>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
            ],
            required=True,
            sanitize=True,
        )

        # Username rules
        self.rules["username"] = ValidationRule(
            name="username",
            pattern=r"^[a-zA-Z0-9_-]{3,50}$",
            max_length=50,
            min_length=3,
            allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
            required=True,
            sanitize=False,
        )

        # Email rules
        self.rules["email"] = ValidationRule(
            name="email",
            pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            max_length=254,
            required=True,
            sanitize=False,
        )

        # Password rules
        self.rules["password"] = ValidationRule(
            name="password",
            min_length=8,
            max_length=128,
            required=True,
            sanitize=False,
        )

        # URL rules
        self.rules["url"] = ValidationRule(
            name="url",
            pattern=r"^https?://[^\s/$.?#].[^\s]*$",
            max_length=2048,
            sanitize=True,
        )

        # File name rules
        self.rules["filename"] = ValidationRule(
            name="filename",
            pattern=r"^[a-zA-Z0-9._-]+\.[a-zA-Z0-9]+$",
            max_length=255,
            forbidden_patterns=[
                r"\.\./",  # Path traversal
                r"\\",  # Backslashes
                r"/",  # Forward slashes
            ],
            sanitize=True,
        )

        # API key rules
        self.rules["api_key"] = ValidationRule(
            name="api_key",
            pattern=r"^[a-zA-Z0-9_-]{16,128}$",
            min_length=16,
            max_length=128,
            required=True,
            sanitize=False,
        )

        # JSON field rules
        self.rules["json"] = ValidationRule(
            name="json",
            max_length=100000,
            forbidden_patterns=[
                r"<script.*?>.*?</script>",
                r"javascript:",
            ],
            sanitize=True,
        )

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a custom validation rule.

        Args:
            rule: Validation rule to add
        """
        self.rules[rule.name] = rule
        logger.info(f"Added validation rule: {rule.name}")

    def validate_and_sanitize(self, value: Any, rule_name: str) -> str:
        """Validate and sanitize input value.

        Args:
            value: Value to validate
            rule_name: Name of validation rule to apply

        Returns:
            Validated and sanitized value

        Raises:
            ValidationError: If validation fails
        """
        if rule_name not in self.rules:
            raise ValidationError(
                f"Unknown validation rule: {rule_name}"
            )

        rule = self.rules[rule_name]

        # Convert to string
        if value is None:
            if rule.required:
                raise ValidationError(f"{rule.name} is required")
            return ""

        str_value = str(value)

        # Check required
        if rule.required and not str_value.strip():
            raise ValidationError(f"{rule.name} is required")

        # Check length constraints
        if rule.max_length and len(str_value) > rule.max_length:
            raise ValidationError(
                f"{rule.name} exceeds maximum length of {rule.max_length}"
            )

        if rule.min_length and len(str_value) < rule.min_length:
            raise ValidationError(
                f"{rule.name} is below minimum length of {rule.min_length}"
            )

        # Check pattern
        if rule.pattern and not re.match(rule.pattern, str_value):
            raise ValidationError(
                f"{rule.name} does not match required pattern"
            )

        # Check allowed characters
        if rule.allowed_chars:
            for char in str_value:
                if char not in rule.allowed_chars:
                    raise ValidationError(
                        f"{rule.name} contains invalid character: {char}"
                    )

        # Check forbidden patterns
        for pattern in rule.forbidden_patterns:
            if re.search(pattern, str_value, re.IGNORECASE):
                raise ValidationError(
                    f"{rule.name} contains forbidden pattern"
                )

        # Sanitize if needed
        if rule.sanitize:
            str_value = self._sanitize_value(str_value)

        return str_value

    def _sanitize_value(self, value: str) -> str:
        """Sanitize input value.

        Args:
            value: Value to sanitize

        Returns:
            Sanitized value
        """
        # HTML escape
        value = html.escape(value)

        # Remove null bytes
        value = value.replace('\x00', '')

        # Remove control characters except newlines and tabs
        value = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)

        # Normalize whitespace
        value = re.sub(r'\s+', ' ', value).strip()

        return value

    def validate_dict(
        self, data: dict[str, Any], field_rules: dict[str, str]
    ) -> dict[str, Any]:
        """Validate a dictionary of values.

        Args:
            data: Dictionary to validate
            field_rules: Mapping of field names to rule names

        Returns:
            Validated and sanitized dictionary

        Raises:
            ValidationError: If validation fails
        """
        validated_data = {}

        for field_name, rule_name in field_rules.items():
            value = data.get(field_name)
            try:
                validated_data[field_name] = self.validate_and_sanitize(
                    value, rule_name
                )
            except ValidationError as e:
                raise ValidationError(f"Field '{field_name}': {str(e)}")

        return validated_data

    def validate_input(self, rule_name: str, value: Any) -> bool:
        """Validate input value and return boolean result.

        Args:
            rule_name: Name of validation rule to apply
            value: Value to validate

        Returns:
            True if valid, False otherwise
            
        Raises:
            ValueError: If validation fails with forbidden patterns or other critical errors
        """
        try:
            self.validate_and_sanitize(value, rule_name)
            return True
        except ValidationError as e:
            # Re-raise ValidationErrors that indicate security issues as ValueError
            error_msg = str(e)
            if "forbidden pattern" in error_msg or "exceeds maximum length" in error_msg or "below minimum length" in error_msg or "Unknown validation rule" in error_msg:
                raise ValueError(error_msg) from e
            return False

    def sanitize_input(self, rule_name: str, value: Any) -> str:
        """Sanitize input value using specified rule.

        Args:
            rule_name: Name of validation rule to apply
            value: Value to sanitize

        Returns:
            Sanitized value
        """
        try:
            return self.validate_and_sanitize(value, rule_name)
        except ValidationError:
            # If validation fails, still return sanitized value
            return self._sanitize_value(
                str(value) if value is not None else ""
            )


class RateLimitValidator:
    """Rate limiting validation."""

    def __init__(self) -> None:
        """Initialize rate limit validator."""
        self.request_counts: dict[str, list[float]] = {}

    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int | None = None,
        window_seconds: int | None = None,
    ) -> bool:
        """Check if request is within rate limits.

        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if within limits, False otherwise
        """
        max_requests = max_requests or settings.rate_limit_requests
        window_seconds = window_seconds or settings.rate_limit_window

        import time

        current_time = time.time()

        # Initialize if new identifier
        if identifier not in self.request_counts:
            self.request_counts[identifier] = []

        # Clean old requests outside window
        self.request_counts[identifier] = [
            req_time
            for req_time in self.request_counts[identifier]
            if current_time - req_time < window_seconds
        ]

        # Check if under limit
        if len(self.request_counts[identifier]) >= max_requests:
            return False

        # Add current request
        self.request_counts[identifier].append(current_time)
        return True


class SecurityValidator:
    """Security-focused validation for potential threats."""

    def __init__(self) -> None:
        """Initialize security validator."""
        self.sql_injection_patterns = [
            r"(\%27)|(\')|(\-\-)|(%23)|(#)",
            r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(%23)|(#))",
            r"/\*(.|\n)*?\*/",
            r"(\%27)|(\')\s*((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
            r"(\%27)|(\')\s*((\%55)|u|(\%75))((\%6E)|n|(\%4E))((\%69)|i|(\%49))((\%6F)|o|(\%4F))((\%6E)|n|(\%4E))",
        ]

        self.xss_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"on\w+\s*=",
            r"<iframe.*?>",
            r"<object.*?>",
            r"<embed.*?>",
            r"<form.*?>",
        ]

        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e\\",
        ]

    def detect_sql_injection(self, value: str) -> bool:
        """Detect potential SQL injection attempts.

        Args:
            value: Value to check

        Returns:
            True if potential SQL injection detected
        """
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def detect_xss(self, value: str) -> bool:
        """Detect potential XSS attempts.

        Args:
            value: Value to check

        Returns:
            True if potential XSS detected
        """
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def detect_path_traversal(self, value: str) -> bool:
        """Detect potential path traversal attempts.

        Args:
            value: Value to check

        Returns:
            True if potential path traversal detected
        """
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def validate_security(self, value: str) -> None:
        """Validate value for security threats.

        Args:
            value: Value to validate

        Raises:
            ValidationError: If security threat detected
        """
        if self.detect_sql_injection(value):
            raise ValidationError("Potential SQL injection detected")

        if self.detect_xss(value):
            raise ValidationError("Potential XSS attempt detected")

        if self.detect_path_traversal(value):
            raise ValidationError("Potential path traversal detected")


# Global validator instances
input_validator = InputValidator()
rate_limit_validator = RateLimitValidator()
security_validator = SecurityValidator()


async def validate_request_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Middleware to validate incoming requests.

    Args:
        request: FastAPI request object
        call_next: Next middleware in chain

    Returns:
        Response from next middleware

    Raises:
        HTTPException: If validation fails
    """
    # Get client identifier for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    client_id = client_ip

    # Check rate limits
    if not rate_limit_validator.check_rate_limit(client_id):
        logger.warning(f"Rate limit exceeded for client: {client_id}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )

    # Validate request body if present
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            # This is a simplified validation - in a real implementation,
            # you would validate based on the specific endpoint and request body structure
            body = await request.body()
            if body:
                body_str = body.decode('utf-8')

                # Basic security validation
                security_validator.validate_security(body_str)

                # Log the request for monitoring
                logger.debug(
                    "Validated request",
                    method=request.method,
                    url=str(request.url),
                    client_ip=client_ip,
                    body_length=len(body_str),
                )

        except ValidationError as e:
            logger.warning(
                "Request validation failed",
                client_ip=client_ip,
                error=str(e),
                url=str(request.url),
            )
            raise HTTPException(
                status_code=400,
                detail=f"Request validation failed: {str(e)}",
            )
        except Exception as e:
            logger.error(
                "Error during request validation",
                client_ip=client_ip,
                error=str(e),
                url=str(request.url),
            )
            # Don't block requests for unexpected validation errors
            pass

    # Continue to next middleware
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    return response


def validate_chat_message(message: str) -> str:
    """Validate and sanitize a chat message.

    Args:
        message: Chat message to validate

    Returns:
        Validated and sanitized message

    Raises:
        ValidationError: If validation fails
    """
    return input_validator.validate_and_sanitize(message, "message")


def validate_user_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate user input data.

    Args:
        data: User input data

    Returns:
        Validated data

    Raises:
        ValidationError: If validation fails
    """
    # Define field validation rules based on common fields
    field_rules = {}

    if "username" in data:
        field_rules["username"] = "username"
    if "email" in data:
        field_rules["email"] = "email"
    if "password" in data:
        field_rules["password"] = "password"
    if "message" in data:
        field_rules["message"] = "message"
    if "text" in data:
        field_rules["text"] = "text"
    if "url" in data:
        field_rules["url"] = "url"
    if "filename" in data:
        field_rules["filename"] = "filename"
    if "api_key" in data:
        field_rules["api_key"] = "api_key"

    return input_validator.validate_dict(data, field_rules)


def sanitize_input(text: str) -> str:
    """Backward compatibility function for sanitizing input.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    return input_validator._sanitize_value(text)


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> bool:
    """Validate password strength.

    Args:
        password: Password to validate

    Returns:
        True if password meets requirements
    """
    if len(password) < 8:
        return False

    # Check for uppercase, lowercase, digit, and special character
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(
        c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
    )

    return has_upper and has_lower and has_digit and has_special


def validate_url(url: str) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid URL format
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID format.

    Args:
        uuid_str: UUID string to validate

    Returns:
        True if valid UUID format
    """
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_str.lower()))


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid phone number format
    """
    # Simple international phone validation
    pattern = r'^\+?[\d\s\-\(\)]{7,15}$'
    return bool(re.match(pattern, phone))


def validate_file_size(size: int, max_size_mb: int = 10) -> bool:
    """Validate file size.

    Args:
        size: File size in bytes
        max_size_mb: Maximum allowed size in MB (default 10MB)

    Returns:
        True if file size is within limits
    """
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    return 0 <= size <= max_size_bytes


def validate_file_type(
    filename: str, allowed_types: list[str] | None = None
) -> bool:
    """Validate file type by extension.

    Args:
        filename: Name of file to validate
        allowed_types: List of allowed file extensions

    Returns:
        True if file type is allowed
    """
    if allowed_types is None:
        allowed_types = [
            '.txt',
            '.pdf',
            '.doc',
            '.docx',
            '.png',
            '.jpg',
            '.jpeg',
        ]

    import os

    _, ext = os.path.splitext(filename.lower())
    return ext in allowed_types


def validate_json_schema(data: dict, schema: dict) -> bool:
    """Validate data against JSON schema.

    Args:
        data: Data to validate
        schema: JSON schema to validate against

    Returns:
        True if data matches schema
    """
    try:
        # Basic validation - in practice you'd use jsonschema library
        for field, field_type in schema.get('properties', {}).items():
            if field in data:
                expected_type = field_type.get('type')
                if expected_type == 'string' and not isinstance(
                    data[field], str
                ):
                    return False
                elif expected_type == 'integer' and not isinstance(
                    data[field], int
                ):
                    return False
                elif expected_type == 'number' and not isinstance(
                    data[field], int | float
                ):
                    return False
                elif expected_type == 'boolean' and not isinstance(
                    data[field], bool
                ):
                    return False
        return True
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path components
    import os

    filename = os.path.basename(filename)

    # Replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Ensure not empty
    if not filename:
        filename = 'unnamed'

    return filename


def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content by removing tags and dangerous content.

    Args:
        html_content: HTML content to sanitize

    Returns:
        Sanitized HTML content with tags and dangerous content removed
    """
    import re

    # First remove script tags and their content
    clean_text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove other dangerous tags and content
    clean_text = re.sub(r'<(style|iframe|object|embed)[^>]*>.*?</\1>', '', clean_text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove HTML tags completely
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    
    # Remove javascript: URLs and other dangerous patterns
    clean_text = re.sub(r'javascript\s*:', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', clean_text, flags=re.IGNORECASE)
    
    # Clean up whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text


def validate_email_format(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    return validate_email(email)


def validate_username_format(username: str) -> bool:
    """Validate username format.

    Args:
        username: Username to validate

    Returns:
        True if valid username format
    """
    pattern = r'^[a-zA-Z0-9_-]{3,50}$'
    return bool(re.match(pattern, username))


def validate_url_format(url: str) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid URL format
    """
    return validate_url(url)


def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if valid API key format
    """
    # Allow common API key patterns with underscores, hyphens, and alphanumeric
    pattern = r'^[a-zA-Z0-9_-]{16,128}$'
    return bool(re.match(pattern, api_key))


def validate_json_structure(
    data: dict[str, Any],
    required_fields: list[str],
    allowed_fields: list[str],
) -> bool:
    """Validate JSON structure.

    Args:
        data: Data to validate
        required_fields: List of required field names
        allowed_fields: List of allowed field names

    Returns:
        True if structure is valid

    Raises:
        ValueError: If validation fails
    """
    # Check for missing required fields
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    # Check for unexpected fields
    for field in data:
        if field not in allowed_fields:
            raise ValueError(f"Unexpected field: {field}")

    return True


def validate_sql_identifier(identifier: str) -> bool:
    """Validate SQL identifier (table name, column name, etc.).

    Args:
        identifier: SQL identifier to validate

    Returns:
        True if valid SQL identifier
    """
    # SQL identifiers should only contain alphanumeric and underscore
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, identifier)) and len(identifier) <= 64


class ValidationMiddleware:
    """Middleware for request validation and sanitization."""

    def __init__(self) -> None:
        """Initialize the validation middleware."""
        self.validator = InputValidator()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Process request through validation middleware.

        Args:
            request: The incoming request
            call_next: The next handler in the chain

        Returns:
            Response from the handler or error response
        """
        # Skip validation for GET requests
        if request.method == "GET":
            return await call_next(request)

        # For POST/PUT/PATCH requests, validate JSON if present
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Check if request has JSON body
                if hasattr(request, 'json'):
                    # This would validate the JSON structure if needed
                    # For now, just pass through
                    pass
            except ValidationError:
                # Return validation error response
                return Response(
                    content='{"error": "Invalid request format"}',
                    status_code=422,
                    media_type="application/json",
                )

        # Call the next handler
        return await call_next(request)
