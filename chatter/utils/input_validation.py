"""Enhanced input validation and sanitization for security."""

import re
import html
import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)


class InputSanitizer:
    """Enhanced input sanitization for security."""
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',               # JavaScript URLs
        r'vbscript:',                # VBScript URLs
        r'onload=',                  # Event handlers
        r'onerror=',
        r'onclick=',
        r'onmouseover=',
        r'<iframe[^>]*>.*?</iframe>',# iframes
        r'<object[^>]*>.*?</object>',# objects
        r'<embed[^>]*>.*?</embed>',  # embeds
        r'<form[^>]*>.*?</form>',    # forms
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b|\bDROP\b|\bCREATE\b|\bALTER\b)",
        r"(\bOR\s+\d+=\d+|\bAND\s+\d+=\d+)",
        r"('|\")(\s*)(;|\s*--|\s*/\*)",
        r"(\bEXEC\b|\bEXECUTE\b|\bsp_\w+)",
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"(;|\||&|`|\$\(.*\))",
        r"(\.\./){2,}",  # Directory traversal
        r"(\\|/)+(etc|proc|sys|dev)/",
        r"(nc|netcat|wget|curl|ping|telnet)\s+",
    ]
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Sanitize HTML content."""
        if not text:
            return ""
        
        # HTML escape
        sanitized = html.escape(text)
        
        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def sanitize_sql_input(cls, text: str) -> str:
        """Sanitize input to prevent SQL injection."""
        if not text:
            return ""
        
        sanitized = text
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.warning(
                    "Potential SQL injection attempt detected",
                    input_text=text[:100],  # Log first 100 chars
                    pattern=pattern
                )
                # Remove the dangerous content
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @classmethod
    def sanitize_command_input(cls, text: str) -> str:
        """Sanitize input to prevent command injection."""
        if not text:
            return ""
        
        sanitized = text
        
        # Check for command injection patterns
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, sanitized):
                logger.warning(
                    "Potential command injection attempt detected",
                    input_text=text[:100],
                    pattern=pattern
                )
                # Remove dangerous content
                sanitized = re.sub(pattern, '', sanitized)
        
        return sanitized.strip()
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for safe storage."""
        if not filename:
            return "untitled"
        
        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        sanitized = re.sub(r'\.{2,}', '.', sanitized)  # Multiple dots
        sanitized = sanitized.strip('. ')  # Leading/trailing dots and spaces
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = Path(sanitized).stem, Path(sanitized).suffix
            sanitized = name[:250-len(ext)] + ext
        
        return sanitized or "untitled"
    
    @classmethod
    def sanitize_json_input(cls, data: Union[str, Dict, List]) -> Optional[Union[Dict, List]]:
        """Sanitize JSON input data."""
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON input provided")
                return None
        
        if isinstance(data, dict):
            return cls._sanitize_dict(data)
        elif isinstance(data, list):
            return cls._sanitize_list(data)
        else:
            return None
    
    @classmethod
    def _sanitize_dict(cls, data: Dict) -> Dict:
        """Recursively sanitize dictionary."""
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            safe_key = cls.sanitize_html(str(key))
            if len(safe_key) > 100:  # Limit key length
                safe_key = safe_key[:100]
            
            # Sanitize value
            if isinstance(value, str):
                sanitized[safe_key] = cls.sanitize_html(value)
            elif isinstance(value, dict):
                sanitized[safe_key] = cls._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[safe_key] = cls._sanitize_list(value)
            else:
                sanitized[safe_key] = value
        
        return sanitized
    
    @classmethod
    def _sanitize_list(cls, data: List) -> List:
        """Recursively sanitize list."""
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(cls.sanitize_html(item))
            elif isinstance(item, dict):
                sanitized.append(cls._sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(cls._sanitize_list(item))
            else:
                sanitized.append(item)
        
        return sanitized


class InputValidator:
    """Enhanced input validation."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) if email else False
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        if not username or len(username) < 3 or len(username) > 50:
            return False
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, bool]:
        """Validate password strength."""
        if not password:
            return {"valid": False, "errors": ["Password is required"]}
        
        checks = {
            "length": len(password) >= 8,
            "uppercase": bool(re.search(r'[A-Z]', password)),
            "lowercase": bool(re.search(r'[a-z]', password)),
            "digit": bool(re.search(r'\d', password)),
            "special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
        }
        
        errors = []
        if not checks["length"]:
            errors.append("Password must be at least 8 characters long")
        if not checks["uppercase"]:
            errors.append("Password must contain at least one uppercase letter")
        if not checks["lowercase"]:
            errors.append("Password must contain at least one lowercase letter")
        if not checks["digit"]:
            errors.append("Password must contain at least one digit")
        if not checks["special"]:
            errors.append("Password must contain at least one special character")
        
        return {
            "valid": all(checks.values()),
            "checks": checks,
            "errors": errors
        }
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
        """Validate file type against allowed types."""
        if not filename:
            return False
        
        file_ext = Path(filename).suffix.lower().lstrip('.')
        return file_ext in [ext.lower().lstrip('.') for ext in allowed_types]
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
        """Validate file size."""
        max_size_bytes = max_size_mb * 1024 * 1024
        return 0 < file_size <= max_size_bytes
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        if not url:
            return False
        
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_json_schema(data: Any, required_fields: List[str]) -> Dict[str, bool]:
        """Validate JSON data against required schema."""
        if not isinstance(data, dict):
            return {"valid": False, "errors": ["Data must be a JSON object"]}
        
        errors = []
        for field in required_fields:
            if field not in data:
                errors.append(f"Required field '{field}' is missing")
            elif data[field] is None or data[field] == "":
                errors.append(f"Field '{field}' cannot be empty")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


def validate_and_sanitize_input(
    data: Any, 
    sanitize_html: bool = True,
    check_sql_injection: bool = True,
    check_command_injection: bool = True
) -> Any:
    """Comprehensive input validation and sanitization."""
    if isinstance(data, str):
        sanitized = data
        
        if check_sql_injection:
            sanitized = InputSanitizer.sanitize_sql_input(sanitized)
        
        if check_command_injection:
            sanitized = InputSanitizer.sanitize_command_input(sanitized)
            
        if sanitize_html:
            sanitized = InputSanitizer.sanitize_html(sanitized)
            
        return sanitized
    
    elif isinstance(data, dict):
        return InputSanitizer.sanitize_json_input(data)
    
    elif isinstance(data, list):
        return InputSanitizer.sanitize_json_input(data)
    
    else:
        return data