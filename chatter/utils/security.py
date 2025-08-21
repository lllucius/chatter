"""Security utilities for authentication and password handling."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password, rounds=settings.bcrypt_rounds)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.debug("Token verification failed", error=str(e))
        return None


def extract_user_id_from_token(token: str) -> Optional[str]:
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
    
    return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)


class TokenValidator:
    """JWT token validator with type checking."""
    
    def __init__(self, token_type: str = "access"):
        """Initialize validator for specific token type.
        
        Args:
            token_type: Type of token to validate ('access' or 'refresh')
        """
        self.token_type = token_type
    
    def validate(self, token: str) -> Optional[Dict[str, Any]]:
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
                logger.debug("Invalid token type", expected="refresh", actual=payload.get("type"))
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
    return ''.join(secrets.choice(alphabet) for _ in range(length))


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
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
    
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
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": [],
        "score": 0,
    }
    
    if len(password) < 8:
        result["valid"] = False
        result["errors"].append("Password must be at least 8 characters long")
    else:
        result["score"] += 1
    
    if not any(c.isupper() for c in password):
        result["valid"] = False
        result["errors"].append("Password must contain at least one uppercase letter")
    else:
        result["score"] += 1
    
    if not any(c.islower() for c in password):
        result["valid"] = False
        result["errors"].append("Password must contain at least one lowercase letter")
    else:
        result["score"] += 1
    
    if not any(c.isdigit() for c in password):
        result["valid"] = False
        result["errors"].append("Password must contain at least one digit")
    else:
        result["score"] += 1
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        result["valid"] = False
        result["errors"].append("Password must contain at least one special character")
    else:
        result["score"] += 1
    
    return result