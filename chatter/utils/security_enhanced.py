"""Enhanced security utilities for authentication and authorization."""

import base64
import os
import re
import secrets
import string
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from jose import JWTError, jwt

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

# Enhanced patterns for sensitive data detection
SENSITIVE_PATTERNS = {
    "api_key": re.compile(
        r'(?i)(api[_-]?key|apikey|access[_-]?token|secret[_-]?key|bearer[_-]?token)["\s]*[:=]["\s]*([a-zA-Z0-9_\-\.]{8,})',
        re.IGNORECASE,
    ),
    "password": re.compile(
        r'(?i)(password|passwd|pwd)["\s]*[:=]["\s]*([^\s"]{6,})',
        re.IGNORECASE,
    ),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "email": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    ),
    "jwt_token": re.compile(
        r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*"
    ),
    "bearer_token": re.compile(
        r"Bearer\s+([A-Za-z0-9_\-\.]{20,})", re.IGNORECASE
    ),
    "authorization": re.compile(
        r"Authorization:\s*([^\r\n]*)", re.IGNORECASE
    ),
}

# Expanded secret key names (consolidated from crypto.py)
SECRET_KEYS = {
    "api_key",
    "apikey",
    "access_token",
    "secret_key",
    "bearer_token",
    "password",
    "passwd",
    "pwd",
    "client_secret",
    "private_key",
    "authorization",
    "auth_token",
    "refresh_token",
    "session_token",
    "database_url",
    "redis_url",
    "jwt_secret",
    "encryption_key",
    "webhook_secret",
    "oauth_secret",
    "api_secret",
    # Additional fields from crypto.py
    "secret",
    "token",
    "key",
    "oauth_client_secret",
}

# Common weak passwords (subset for performance)
COMMON_PASSWORDS = {
    "password",
    "123456",
    "123456789",
    "qwerty",
    "abc123",
    "password123",
    "admin",
    "letmein",
    "welcome",
    "monkey",
    "1234567890",
    "password1",
    "qwerty123",
    "admin123",
    "root",
    "test",
    "guest",
    "user",
}

# Disposable email domains
DISPOSABLE_DOMAINS = {
    "10minutemail.com",
    "tempmail.org",
    "guerrillamail.com",
    "mailinator.com",
    "throwaway.email",
    "temp-mail.org",
    "emailondeck.com",
    "getairmail.com",
    "maildrop.cc",
}


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with enhanced security.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    # Use higher cost factor for better security
    cost_factor = max(12, settings.bcrypt_rounds)
    return bcrypt.hashpw(
        password.encode(), bcrypt.gensalt(rounds=cost_factor)
    ).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode(), hashed_password.encode()
        )
    except Exception as e:
        logger.warning("Password verification failed", error=str(e))
        return False


def generate_secure_api_key(length: int = 32) -> tuple[str, str]:
    """Generate cryptographically secure API key with proper hashing.

    Args:
        length: Length of the API key to generate

    Returns:
        Tuple of (plain_api_key, hashed_api_key)
    """
    # Generate secure random API key
    timestamp = int(datetime.now(UTC).timestamp())
    salt = secrets.token_hex(8)
    random_part = secrets.token_urlsafe(length)

    # Create unique key with timestamp and salt
    api_key = f"chatter_api_{timestamp}_{salt}_{random_part}"

    # Hash with bcrypt for secure storage (like passwords)
    hashed_key = bcrypt.hashpw(
        api_key.encode(), bcrypt.gensalt(rounds=12)
    )

    return api_key, hashed_key.decode()


def verify_api_key_secure(plain_key: str, hashed_key: str) -> bool:
    """Verify API key using bcrypt.

    Args:
        plain_key: Plain text API key
        hashed_key: Bcrypt hashed API key

    Returns:
        True if API key matches, False otherwise
    """
    try:
        return bcrypt.checkpw(plain_key.encode(), hashed_key.encode())
    except Exception as e:
        logger.warning("API key verification failed", error=str(e))
        return False


def validate_email_advanced(email: str) -> bool:
    """Advanced email validation with security checks.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid and secure, False otherwise
    """
    if not email or len(email) > 254:  # RFC 5321 limit
        return False

    # Basic format validation
    if not re.match(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email
    ):
        return False

    # Check for disposable email domains
    domain = email.split("@")[1].lower()
    if domain in DISPOSABLE_DOMAINS:
        logger.info("Blocked disposable email domain", domain=domain)
        return False

    # Check for suspicious patterns
    if ".." in email or email.startswith(".") or email.endswith("."):
        return False

    # Optional: DNS MX record validation (commented out for performance)
    # try:
    #     dns.resolver.resolve(domain, 'MX')
    # except:
    #     return False

    return True


def validate_username_secure(username: str) -> bool:
    """Secure username validation with security checks.

    Args:
        username: Username to validate

    Returns:
        True if username is valid and secure, False otherwise
    """
    if not username or len(username) < 3 or len(username) > 50:
        return False

    # Check basic format
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False

    # Prohibited usernames
    prohibited = {
        "admin",
        "root",
        "system",
        "api",
        "www",
        "mail",
        "ftp",
        "test",
        "guest",
        "user",
        "null",
        "undefined",
        "support",
        "security",
        "moderator",
        "operator",
        "service",
    }

    if username.lower() in prohibited:
        return False

    # Check for sequential patterns
    if re.search(r"(012|123|234|345|456|567|678|789|890)", username):
        return False

    # Check for repeated characters
    if re.search(r"(.)\1{3,}", username):  # 4+ repeated chars
        return False

    return True


def validate_password_advanced(password: str) -> dict[str, Any]:
    """Advanced password validation with entropy and security checks.

    Args:
        password: Password to validate

    Returns:
        Dictionary with validation results
    """
    result = {"valid": True, "errors": [], "score": 0, "entropy": 0}

    # Length check
    if len(password) < 8:
        result["valid"] = False
        result["errors"].append(
            "Password must be at least 8 characters long"
        )
    elif len(password) >= 12:
        result["score"] += 2
    else:
        result["score"] += 1

    # Character type checks
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    has_special = any(c in special_chars for c in password)

    if not has_upper:
        result["valid"] = False
        result["errors"].append(
            "Password must contain at least one uppercase letter"
        )
    else:
        result["score"] += 1

    if not has_lower:
        result["valid"] = False
        result["errors"].append(
            "Password must contain at least one lowercase letter"
        )
    else:
        result["score"] += 1

    if not has_digit:
        result["valid"] = False
        result["errors"].append(
            "Password must contain at least one digit"
        )
    else:
        result["score"] += 1

    if not has_special:
        result["valid"] = False
        result["errors"].append(
            "Password must contain at least one special character"
        )
    else:
        result["score"] += 1

    # Advanced checks
    if result["valid"]:
        # Entropy calculation
        entropy = calculate_password_entropy(password)
        result["entropy"] = entropy

        if entropy < 30:
            result["valid"] = False
            result["errors"].append("Password complexity is too low")
        elif entropy < 50:
            result["errors"].append(
                "Consider using a more complex password"
            )
        else:
            result["score"] += 1

        # Common password check
        if is_common_password(password):
            result["valid"] = False
            result["errors"].append("Password is too common")
        else:
            result["score"] += 1

        # Keyboard pattern check
        if has_keyboard_pattern(password):
            result["valid"] = False
            result["errors"].append(
                "Password contains keyboard patterns"
            )
        else:
            result["score"] += 1

        # Repetition check
        if has_excessive_repetition(password):
            result["valid"] = False
            result["errors"].append(
                "Password has too much character repetition"
            )
        else:
            result["score"] += 1

    return result


def calculate_password_entropy(password: str) -> float:
    """Calculate password entropy using Shannon entropy.

    Args:
        password: Password to analyze

    Returns:
        Password entropy value
    """
    import math
    from collections import Counter

    if not password:
        return 0

    # Count character space
    charset_size = 0
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        charset_size += 32

    # Calculate base entropy
    base_entropy = (
        len(password) * math.log2(charset_size)
        if charset_size > 0
        else 0
    )

    # Shannon entropy for character distribution
    char_counts = Counter(password)
    total_chars = len(password)
    shannon_entropy = 0

    for count in char_counts.values():
        probability = count / total_chars
        if probability > 0:
            shannon_entropy += -probability * math.log2(probability)

    # Combine entropies with weighting
    combined_entropy = (base_entropy * 0.7) + (
        shannon_entropy * total_chars * 0.3
    )

    # Penalty for patterns
    pattern_penalty = 0
    if has_keyboard_pattern(password):
        pattern_penalty += 10
    if has_excessive_repetition(password):
        pattern_penalty += 5

    return max(0, combined_entropy - pattern_penalty)


def is_common_password(password: str) -> bool:
    """Check if password is in common password list.

    Args:
        password: Password to check

    Returns:
        True if password is common, False otherwise
    """
    return password.lower() in COMMON_PASSWORDS


def has_keyboard_pattern(password: str) -> bool:
    """Check for keyboard patterns in password.

    Args:
        password: Password to check

    Returns:
        True if keyboard patterns found, False otherwise
    """
    # Common keyboard patterns
    patterns = [
        "qwerty",
        "asdf",
        "zxcv",
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm",
        "123456",
        "1234567890",
        "abcdef",
        "abcdefg",
    ]

    password_lower = password.lower()

    for pattern in patterns:
        if pattern in password_lower or pattern[::-1] in password_lower:
            return True

    # Check for sequential patterns
    if re.search(
        r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",
        password_lower,
    ):
        return True

    return False


def has_excessive_repetition(password: str) -> bool:
    """Check for excessive character repetition.

    Args:
        password: Password to check

    Returns:
        True if excessive repetition found, False otherwise
    """
    # Check for 3+ consecutive repeated characters
    if re.search(r"(.)\1{2,}", password):
        return True

    # Check for high repetition ratio
    from collections import Counter

    char_counts = Counter(password)

    # If any character appears more than 40% of the time
    max_count = max(char_counts.values())
    if max_count / len(password) > 0.4:
        return True

    return False


def contains_personal_info(password: str, user_data: dict) -> bool:
    """Check if password contains personal information.

    Args:
        password: Password to check
        user_data: User data dictionary

    Returns:
        True if personal info found, False otherwise
    """
    password_lower = password.lower()

    # Check against user data fields
    fields_to_check = [
        "username",
        "email",
        "full_name",
        "first_name",
        "last_name",
    ]

    for field in fields_to_check:
        value = user_data.get(field)
        if value and len(str(value)) >= 3:
            if str(value).lower() in password_lower:
                return True

            # Check email local part
            if field == "email" and "@" in str(value):
                local_part = str(value).split("@")[0].lower()
                if (
                    len(local_part) >= 3
                    and local_part in password_lower
                ):
                    return True

    return False


# Security utility functions
def sanitize_log_data(data: Any, max_depth: int = 5) -> Any:
    """Sanitize sensitive data from logs."""
    if max_depth <= 0:
        return "[MAX_DEPTH_REACHED]"

    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if isinstance(key, str) and key.lower() in SECRET_KEYS:
                sanitized[key] = mask_sensitive_value(str(value))
            else:
                sanitized[key] = sanitize_log_data(value, max_depth - 1)
        return sanitized

    elif isinstance(data, list):
        return [sanitize_log_data(item, max_depth - 1) for item in data]

    elif isinstance(data, str):
        return sanitize_string(data)

    elif hasattr(data, "__dict__"):
        try:
            return sanitize_log_data(data.__dict__, max_depth - 1)
        except Exception:
            return str(type(data).__name__)

    else:
        return data


def sanitize_string(text: str) -> str:
    """Sanitize sensitive data from a string."""
    if not isinstance(text, str):
        return text

    sanitized = text

    for pattern_name, pattern in SENSITIVE_PATTERNS.items():

        def replace_match(match, current_pattern_name=pattern_name):
            if current_pattern_name == "email":
                email = match.group(0)
                if "@" in email:
                    local, domain = email.split("@", 1)
                    return f"{local}@[MASKED]"
                return "[MASKED_EMAIL]"
            else:
                if len(match.groups()) >= 2:
                    return f"{match.group(1)}=[MASKED]"
                else:
                    return "[MASKED]"

        sanitized = pattern.sub(replace_match, sanitized)

    return sanitized


def mask_sensitive_value(value: str, show_chars: int = 4) -> str:
    """Mask a sensitive value showing only first/last characters."""
    if not value or len(value) <= show_chars * 2:
        return "[MASKED]"

    return f"{value[:show_chars]}{'*' * (len(value) - show_chars * 2)}{value[-show_chars:]}"


# JWT token functions
def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
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
    """Create a JWT refresh token."""
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
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.debug("Token verification failed", error=str(e))
        return None


def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """Sanitize user input by removing potentially dangerous characters."""
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


def generate_secure_secret(length: int = 32) -> str:
    """Generate a cryptographically secure secret."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_session_id(length: int = 32) -> str:
    """Generate a secure session ID."""
    return secrets.token_urlsafe(length)


class SecureLogger:
    """Logger wrapper that automatically sanitizes sensitive data."""

    def __init__(self, logger_instance):
        """Initialize with a logger instance."""
        self.logger = logger_instance

    def _sanitize_message(
        self, message: str, *args, **kwargs
    ) -> tuple[str, tuple, dict]:
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
        msg, args, kwargs = self._sanitize_message(
            message, *args, **kwargs
        )
        self.logger.debug(msg, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message with sanitization."""
        msg, args, kwargs = self._sanitize_message(
            message, *args, **kwargs
        )
        self.logger.info(msg, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message with sanitization."""
        msg, args, kwargs = self._sanitize_message(
            message, *args, **kwargs
        )
        self.logger.warning(msg, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message with sanitization."""
        msg, args, kwargs = self._sanitize_message(
            message, *args, **kwargs
        )
        self.logger.error(msg, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message with sanitization."""
        msg, args, kwargs = self._sanitize_message(
            message, *args, **kwargs
        )
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


# Cryptography utilities (consolidated from crypto.py)
class CryptoError(Exception):
    """Cryptography related error."""

    pass


class SecretManager:
    """Manager for encrypting and decrypting sensitive data."""

    def __init__(self, key: str | None = None):
        """Initialize with encryption key.

        Args:
            key: Base64 encoded encryption key. If None, generates from environment.
        """
        if key is None:
            key = self._get_or_generate_key()

        try:
            self._key = key.encode() if isinstance(key, str) else key
            self._fernet = Fernet(self._key)
        except Exception as e:
            raise CryptoError(
                f"Failed to initialize encryption: {e}"
            ) from e

    def _get_or_generate_key(self) -> str:
        """Get encryption key from environment or generate new one."""
        # Try to get from environment
        env_key = os.environ.get("CHATTER_ENCRYPTION_KEY")
        if env_key:
            return env_key

        # Generate from password + salt
        password = os.environ.get(
            "CHATTER_SECRET_PASSWORD", "default-dev-password"
        ).encode()
        salt = os.environ.get(
            "CHATTER_SECRET_SALT", "default-dev-salt"
        ).encode()

        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))

        logger.warning(
            "Using derived encryption key. Set CHATTER_ENCRYPTION_KEY in production."
        )
        return key.decode()

    def encrypt(self, data: str) -> str:
        """Encrypt string data.

        Args:
            data: String to encrypt

        Returns:
            Base64 encoded encrypted data
        """
        try:
            encrypted = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise CryptoError(f"Failed to encrypt data: {e}") from e

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data.

        Args:
            encrypted_data: Base64 encoded encrypted data

        Returns:
            Decrypted string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(
                encrypted_data.encode()
            )
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise CryptoError(f"Failed to decrypt data: {e}") from e

    def encrypt_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Encrypt sensitive fields in a dictionary.

        Args:
            data: Dictionary with potential sensitive fields

        Returns:
            Dictionary with sensitive fields encrypted
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and any(
                field in key.lower() for field in SECRET_KEYS
            ):
                result[key] = self.encrypt(value)
                result[f"{key}_encrypted"] = True
            else:
                result[key] = value

        return result

    def decrypt_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Decrypt sensitive fields in a dictionary.

        Args:
            data: Dictionary with encrypted sensitive fields

        Returns:
            Dictionary with sensitive fields decrypted
        """
        result = {}
        for key, value in data.items():
            if key.endswith("_encrypted"):
                continue  # Skip encryption markers

            encryption_marker = f"{key}_encrypted"
            if encryption_marker in data and data[encryption_marker]:
                if isinstance(value, str):
                    result[key] = self.decrypt(value)
                else:
                    result[key] = value
            else:
                result[key] = value

        return result


# Global instance
_secret_manager: SecretManager | None = None


def get_secret_manager() -> SecretManager:
    """Get global secret manager instance."""
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = SecretManager()
    return _secret_manager


def encrypt_secret(data: str) -> str:
    """Encrypt a secret string."""
    return get_secret_manager().encrypt(data)


def decrypt_secret(encrypted_data: str) -> str:
    """Decrypt a secret string."""
    return get_secret_manager().decrypt(encrypted_data)
