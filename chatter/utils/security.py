"""Security utilities for authentication, password handling, and data sanitization."""

import hashlib
import re
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

# Patterns for sensitive data detection
SENSITIVE_PATTERNS = {
    'api_key': re.compile(r'(?i)(api[_-]?key|apikey|access[_-]?token|secret[_-]?key|bearer[_-]?token)["\s]*[:=]["\s]*([a-zA-Z0-9_\-\.]{8,})', re.IGNORECASE),
    'password': re.compile(r'(?i)(password|passwd|pwd)["\s]*[:=]["\s]*([^\s"]{6,})', re.IGNORECASE),
    'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
    'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    'jwt_token': re.compile(r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'),
    'bearer_token': re.compile(r'Bearer\s+([A-Za-z0-9_\-\.]{20,})', re.IGNORECASE),
    'authorization': re.compile(r'Authorization:\s*([^\r\n]*)', re.IGNORECASE),
}

# Common secret key names
SECRET_KEYS = {
    'api_key', 'apikey', 'access_token', 'secret_key', 'bearer_token',
    'password', 'passwd', 'pwd', 'client_secret', 'private_key',
    'authorization', 'auth_token', 'refresh_token', 'session_token',
    'database_url', 'redis_url', 'jwt_secret', 'encryption_key'
}


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=settings.bcrypt_rounds)).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except Exception as e:
        logger.warning(f"Password verification failed: {e}")
        return False


def hash_api_key(api_key: str, salt: str | None = None) -> str:
    """Hash an API key for secure storage.

    Args:
        api_key: The API key to hash
        salt: Optional salt (uses default if not provided)

    Returns:
        Hashed API key
    """
    if salt is None:
        salt = settings.secret_key[:16]  # Use first 16 chars of secret key as salt

    # Use SHA-256 with salt for API key hashing
    combined = f"{salt}{api_key}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str, salt: str | None = None) -> bool:
    """Verify an API key against its hash.

    Args:
        plain_key: Plain text API key
        hashed_key: Hashed API key to verify against
        salt: Optional salt (uses default if not provided)

    Returns:
        True if API key matches, False otherwise
    """
    try:
        computed_hash = hash_api_key(plain_key, salt)
        return computed_hash == hashed_key
    except Exception as e:
        logger.warning(f"API key verification failed: {e}")
        return False


def generate_api_key_hash(length: int = 32) -> tuple[str, str]:
    """Generate a new API key and its hash.

    Args:
        length: Length of the API key to generate

    Returns:
        Tuple of (plain_api_key, hashed_api_key)
    """
    import secrets
    import string

    # Generate secure random API key
    alphabet = string.ascii_letters + string.digits + "-_"
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))

    # Hash it for storage
    hashed_key = hash_api_key(api_key)

    return api_key, hashed_key


def sanitize_log_data(data: Any, max_depth: int = 5) -> Any:
    """Sanitize sensitive data from logs.

    Args:
        data: Data to sanitize (dict, list, string, etc.)
        max_depth: Maximum recursion depth to prevent infinite loops

    Returns:
        Sanitized data with sensitive information masked
    """
    if max_depth <= 0:
        return "[MAX_DEPTH_REACHED]"

    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Check if key indicates sensitive data
            if isinstance(key, str) and key.lower() in SECRET_KEYS:
                sanitized[key] = mask_sensitive_value(str(value))
            else:
                sanitized[key] = sanitize_log_data(value, max_depth - 1)
        return sanitized

    elif isinstance(data, list):
        return [sanitize_log_data(item, max_depth - 1) for item in data]

    elif isinstance(data, str):
        return sanitize_string(data)

    elif hasattr(data, '__dict__'):
        # Handle objects with attributes
        try:
            return sanitize_log_data(data.__dict__, max_depth - 1)
        except Exception:
            return str(type(data).__name__)

    else:
        return data


def sanitize_string(text: str) -> str:
    """Sanitize sensitive data from a string.

    Args:
        text: String to sanitize

    Returns:
        String with sensitive data masked
    """
    if not isinstance(text, str):
        return text

    sanitized = text

    # Apply all sensitive patterns
    for pattern_name, pattern in SENSITIVE_PATTERNS.items():
        def replace_match(match):
            if pattern_name == 'email':
                # For emails, just mask the domain part
                email = match.group(0)
                if '@' in email:
                    local, domain = email.split('@', 1)
                    return f"{local}@[MASKED]"
                return "[MASKED_EMAIL]"
            else:
                # For other patterns, mask the entire sensitive part
                if len(match.groups()) >= 2:
                    return f"{match.group(1)}=[MASKED]"
                else:
                    return "[MASKED]"

        sanitized = pattern.sub(replace_match, sanitized)

    return sanitized


def mask_sensitive_value(value: str, show_chars: int = 4) -> str:
    """Mask a sensitive value showing only first/last characters.

    Args:
        value: Value to mask
        show_chars: Number of characters to show at start/end

    Returns:
        Masked value
    """
    if not value or len(value) <= show_chars * 2:
        return "[MASKED]"

    return f"{value[:show_chars]}{'*' * (len(value) - show_chars * 2)}{value[-show_chars:]}"


def sanitize_url(url: str) -> str:
    """Sanitize sensitive information from URLs.

    Args:
        url: URL to sanitize

    Returns:
        URL with sensitive information masked
    """
    if not url:
        return url

    # Remove credentials from URLs
    # postgres://user:password@host:port/db -> postgres://[MASKED]@host:port/db
    url_pattern = re.compile(r'([\w+]+://)([^:]+):([^@]+)@(.+)')
    match = url_pattern.match(url)

    if match:
        protocol, user, password, rest = match.groups()
        return f"{protocol}[MASKED]@{rest}"

    return url


def is_sensitive_key(key: str) -> bool:
    """Check if a key name indicates sensitive data.

    Args:
        key: Key name to check

    Returns:
        True if key appears to contain sensitive data
    """
    return isinstance(key, str) and key.lower() in SECRET_KEYS


def create_secure_log_context(**kwargs) -> dict[str, Any]:
    """Create a sanitized context for logging.

    Args:
        **kwargs: Key-value pairs to include in log context

    Returns:
        Sanitized context dictionary
    """
    return sanitize_log_data(kwargs)


class SecureLogger:
    """Logger wrapper that automatically sanitizes sensitive data."""

    def __init__(self, logger_instance):
        """Initialize with a logger instance."""
        self.logger = logger_instance

    def _sanitize_message(self, message: str, *args, **kwargs) -> tuple[str, tuple, dict]:
        """Sanitize log message and arguments."""
        # Sanitize the message
        sanitized_message = sanitize_string(str(message))

        # Sanitize positional arguments
        sanitized_args = tuple(sanitize_log_data(arg) for arg in args)

        # Sanitize keyword arguments
        sanitized_kwargs = sanitize_log_data(kwargs)

        return sanitized_message, sanitized_args, sanitized_kwargs

    def debug(self, message: str, *args, **kwargs):
        """Log debug message with sanitization."""
        msg, args, kwargs = self._sanitize_message(message, *args, **kwargs)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message with sanitization."""
        msg, args, kwargs = self._sanitize_message(message, *args, **kwargs)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message with sanitization."""
        msg, args, kwargs = self._sanitize_message(message, *args, **kwargs)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message with sanitization."""
        msg, args, kwargs = self._sanitize_message(message, *args, **kwargs)
        self.logger.error(msg, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message with sanitization."""
        msg, args, kwargs = self._sanitize_message(message, *args, **kwargs)
        self.logger.critical(msg, *args, **kwargs)


def get_secure_logger(name: str):
    """Get a secure logger that sanitizes sensitive data.

    Args:
        name: Logger name

    Returns:
        SecureLogger instance
    """
    regular_logger = get_logger(name)
    return SecureLogger(regular_logger)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT refresh token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            days=settings.refresh_token_expire_days
        )

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def verify_token(token: str) -> dict[str, Any] | None:
    """Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.debug("Token verification failed", error=str(e))
        return None


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT refresh token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            days=settings.refresh_token_expire_days
        )

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def verify_token(token: str) -> dict[str, Any] | None:
    """Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.debug("Token verification failed", error=str(e))
        return None


def extract_user_id_from_token(token: str) -> str | None:
    """Extract user ID from JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID if token is valid, None otherwise
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


def is_token_expired(token: str) -> bool:
    """Check if a JWT token is expired.

    Args:
        token: JWT token string

    Returns:
        True if token is expired, False otherwise
    """
    payload = verify_token(token)
    if not payload:
        return True

    exp = payload.get("exp")
    if not exp:
        return True

    return datetime.fromtimestamp(exp, tz=UTC) < datetime.now(UTC)


class TokenValidator:
    """JWT token validator with type checking."""

    def __init__(self, token_type: str = "access"):
        """Initialize validator for specific token type.

        Args:
            token_type: Type of token to validate ('access' or 'refresh')
        """
        self.token_type = token_type

    def validate(self, token: str) -> dict[str, Any] | None:
        """Validate token and check type.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload if valid and correct type, None otherwise
        """
        payload = verify_token(token)
        if not payload:
            return None

        # Check token type for refresh tokens
        if self.token_type == "refresh":
            if payload.get("type") != "refresh":
                logger.debug(
                    "Invalid token type",
                    expected="refresh",
                    actual=payload.get("type"),
                )
                return None

        return payload


def generate_api_key(length: int = 32) -> str:
    """Generate a random API key.

    Args:
        length: Length of the API key

    Returns:
        Random API key string
    """
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def hash_api_key(api_key: str) -> str:
    """Hash an API key using bcrypt.

    Args:
        api_key: Plain text API key

    Returns:
        Hashed API key string
    """
    return bcrypt.hashpw(api_key.encode(), bcrypt.gensalt()).decode()


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Verify an API key against its hash.

    Args:
        plain_api_key: Plain text API key to verify
        hashed_api_key: Hashed API key to verify against

    Returns:
        True if API key matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_api_key.encode(), hashed_api_key.encode()
    )


def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """Sanitize user input by removing potentially dangerous characters.

    Args:
        input_string: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not input_string:
        return ""

    # Truncate to max length
    sanitized = input_string[:max_length]

    # Remove null bytes and other control characters
    sanitized = "".join(
        char
        for char in sanitized
        if ord(char) >= 32 or char in "\t\n\r"
    )

    # Strip whitespace
    sanitized = sanitized.strip()

    return sanitized


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> dict[str, Any]:
    """Validate password strength.

    Args:
        password: Password to validate

    Returns:
        Dictionary with validation results
    """
    result: dict[str, Any] = {
        "valid": True,
        "errors": [],
        "score": 0,
    }

    if len(password) < 8:
        result["valid"] = False
        result["errors"].append(
            "Password must be at least 8 characters long"
        )
    else:
        result["score"] += 1

    if not any(c.isupper() for c in password):
        result["valid"] = False
        result["errors"].append(
            "Password must contain at least one uppercase letter"
        )
    else:
        result["score"] += 1

    if not any(c.islower() for c in password):
        result["valid"] = False
        result["errors"].append(
            "Password must contain at least one lowercase letter"
        )
    else:
        result["score"] += 1

    if not any(c.isdigit() for c in password):
        result["valid"] = False
        result["errors"].append(
            "Password must contain at least one digit"
        )
    else:
        result["score"] += 1

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        result["valid"] = False
        result["errors"].append(
            "Password must contain at least one special character"
        )
    else:
        result["score"] += 1

    return result


def generate_secure_secret(length: int = 32) -> str:
    """Generate a cryptographically secure secret.

    Args:
        length: Length of the secret to generate

    Returns:
        Secure random string
    """
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))
