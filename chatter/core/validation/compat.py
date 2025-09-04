"""Compatibility layer for existing validation usage.

This module provides backwards compatibility for existing code that uses
the old validation modules. It maps old validation functions and classes
to the new unified validation system.
"""

from typing import Any, Dict, List, Optional, Union
import warnings

# Import the new unified validation system
from chatter.core.validation import (
    validation_engine,
    ValidationError as NewValidationError,
    SecurityValidationError,
    ValidationContext,
)
from chatter.core.validation.context import DEFAULT_CONTEXT

# Legacy ValidationError for backwards compatibility
class ValidationError(Exception):
    """Legacy ValidationError class for backwards compatibility."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _convert_validation_result(result, return_value=False):
    """Convert new ValidationResult to legacy format."""
    if not result.is_valid:
        # Raise the first error in legacy format
        error_message = result.errors[0].message if result.errors else "Validation failed"
        raise ValidationError(error_message)
    
    if return_value:
        return result.value
    return True


# Legacy InputValidator for backwards compatibility
class InputValidator:
    """Legacy InputValidator for backwards compatibility."""
    
    def __init__(self):
        warnings.warn(
            "Using legacy InputValidator. Consider migrating to the unified validation system.",
            DeprecationWarning,
            stacklevel=2
        )
        
    def validate_and_sanitize(self, value: Any, rule_name: str) -> str:
        """Legacy validate_and_sanitize method."""
        result = validation_engine.validate_input(value, rule_name, DEFAULT_CONTEXT)
        return _convert_validation_result(result, return_value=True)
        
    def validate_input(self, rule_name: str, value: Any) -> bool:
        """Legacy validate_input method."""
        try:
            result = validation_engine.validate_input(value, rule_name, DEFAULT_CONTEXT)
            return result.is_valid
        except Exception as e:
            # Convert to ValueError for critical errors as per original behavior
            if any(critical in str(e) for critical in [
                "forbidden pattern", "exceeds maximum length", "below minimum length"
            ]):
                raise ValueError(str(e))
            return False
            
    def sanitize_input(self, rule_name: str, value: Any) -> str:
        """Legacy sanitize_input method."""
        try:
            result = validation_engine.validate_input(value, rule_name, DEFAULT_CONTEXT)
            return result.value if result.value is not None else str(value)
        except:
            # If validation fails, still return sanitized value as per original
            return str(value) if value is not None else ""


# Legacy SecurityValidator for backwards compatibility  
class SecurityValidator:
    """Legacy SecurityValidator for backwards compatibility."""
    
    def __init__(self):
        warnings.warn(
            "Using legacy SecurityValidator. Consider migrating to the unified validation system.",
            DeprecationWarning,
            stacklevel=2
        )
        
    def detect_sql_injection(self, value: str) -> bool:
        """Legacy detect_sql_injection method."""
        result = validation_engine.validate_security(value, DEFAULT_CONTEXT)
        return not result.is_valid and any(
            error.threat_type == "sql_injection" for error in result.errors
            if hasattr(error, 'threat_type')
        )
        
    def detect_xss(self, value: str) -> bool:
        """Legacy detect_xss method."""
        result = validation_engine.validate_security(value, DEFAULT_CONTEXT)
        return not result.is_valid and any(
            error.threat_type == "xss" for error in result.errors
            if hasattr(error, 'threat_type')
        )
        
    def detect_path_traversal(self, value: str) -> bool:
        """Legacy detect_path_traversal method."""
        result = validation_engine.validate_security(value, DEFAULT_CONTEXT)
        return not result.is_valid and any(
            error.threat_type == "path_traversal" for error in result.errors
            if hasattr(error, 'threat_type')
        )
        
    def validate_security(self, value: str) -> None:
        """Legacy validate_security method."""
        result = validation_engine.validate_security(value, DEFAULT_CONTEXT)
        if not result.is_valid:
            # Raise first security error
            error = result.errors[0] if result.errors else NewValidationError("Security validation failed")
            raise ValidationError(error.message)


# Legacy standalone functions for backwards compatibility
def validate_chat_message(message: str) -> str:
    """Legacy validate_chat_message function."""
    result = validation_engine.validate_input(message, "message", DEFAULT_CONTEXT)
    return _convert_validation_result(result, return_value=True)


def validate_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy validate_user_input function.""" 
    validated_data = {}
    
    # Define field validation rules based on common fields (from original)
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
        
    for field_name, rule_name in field_rules.items():
        value = data.get(field_name)
        result = validation_engine.validate_input(value, rule_name, DEFAULT_CONTEXT)
        if not result.is_valid:
            raise ValidationError(f"Field '{field_name}': {result.errors[0].message}")
        validated_data[field_name] = result.value
        
    return validated_data


def sanitize_input(text: str) -> str:
    """Legacy sanitize_input function."""
    try:
        result = validation_engine.validate_input(text, "text", DEFAULT_CONTEXT)
        return result.value if result.value is not None else text
    except:
        return text


def validate_email(email: str) -> bool:
    """Legacy validate_email function."""
    try:
        result = validation_engine.validate_input(email, "email", DEFAULT_CONTEXT)
        return result.is_valid
    except:
        return False


def validate_password(password: str) -> bool:
    """Legacy validate_password function."""
    try:
        result = validation_engine.validate_input(password, "password", DEFAULT_CONTEXT)
        if not result.is_valid:
            return False
            
        # Additional password strength check as per original
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    except:
        return False


def validate_url(url: str) -> bool:
    """Legacy validate_url function."""
    try:
        result = validation_engine.validate_input(url, "url", DEFAULT_CONTEXT)
        return result.is_valid
    except:
        return False


def validate_uuid(uuid_str: str) -> bool:
    """Legacy validate_uuid function."""
    import re
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_str.lower()))


def validate_phone_number(phone: str) -> bool:
    """Legacy validate_phone_number function."""
    import re
    pattern = r'^\+?[\d\s\-\(\)]{7,15}$'
    return bool(re.match(pattern, phone))


def validate_file_size(size: int, max_size_mb: int = 10) -> bool:
    """Legacy validate_file_size function."""
    max_size_bytes = max_size_mb * 1024 * 1024
    return 0 <= size <= max_size_bytes


def validate_file_type(filename: str, allowed_types: List[str] = None) -> bool:
    """Legacy validate_file_type function."""
    if allowed_types is None:
        allowed_types = ['.txt', '.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg']
    
    import os
    _, ext = os.path.splitext(filename.lower())
    return ext in allowed_types


def validate_json_schema(data: dict, schema: dict) -> bool:
    """Legacy validate_json_schema function."""
    try:
        # Basic validation as per original
        for field, field_type in schema.get('properties', {}).items():
            if field in data:
                expected_type = field_type.get('type')
                if expected_type == 'string' and not isinstance(data[field], str):
                    return False
                elif expected_type == 'integer' and not isinstance(data[field], int):
                    return False
                elif expected_type == 'number' and not isinstance(data[field], (int, float)):
                    return False
                elif expected_type == 'boolean' and not isinstance(data[field], bool):
                    return False
        return True
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """Legacy sanitize_filename function."""
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
    """Legacy sanitize_html function."""
    import re
    
    # Remove script tags and their content
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


# Global instances for backwards compatibility
input_validator = InputValidator()
security_validator = SecurityValidator()


# Legacy middleware function
async def validate_request_middleware(request, call_next):
    """Legacy validate_request_middleware function."""
    warnings.warn(
        "Using legacy validate_request_middleware. Consider using the unified validation middleware.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # For now, just pass through to maintain compatibility
    return await call_next(request)


# Enhanced validation compatibility
def validate_name_field(value: str, field_name: str = "name") -> str:
    """Legacy validate_name_field function."""
    # Map to appropriate rule
    rule = "username" if field_name in ["name", "username"] else "text"
    result = validation_engine.validate_input(value, rule, DEFAULT_CONTEXT)
    return _convert_validation_result(result, return_value=True)


def validate_display_name(value: str, field_name: str = "display_name") -> str:
    """Legacy validate_display_name function."""
    result = validation_engine.validate_input(value, "text", DEFAULT_CONTEXT)
    return _convert_validation_result(result, return_value=True)


def validate_description(value: str, field_name: str = "description") -> Optional[str]:
    """Legacy validate_description function."""
    if value is None:
        return None
    result = validation_engine.validate_input(value, "text", DEFAULT_CONTEXT)
    return result.value if result.is_valid else None


def validate_positive_integer(value: int, field_name: str, max_value: int = None, min_value: int = 1) -> Optional[int]:
    """Legacy validate_positive_integer function.""" 
    if value is None:
        return None
        
    if not isinstance(value, int):
        raise ValidationError(f"{field_name} must be an integer")
        
    if value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}")
        
    if max_value is not None and value > max_value:
        raise ValidationError(f"{field_name} must be at most {max_value}")
        
    return value


def validate_model_consistency(model_type: str, dimensions: int = None, max_tokens: int = None, 
                             max_batch_size: int = None, supports_batch: bool = None) -> None:
    """Legacy validate_model_consistency function."""
    data = {
        "model_type": model_type,
        "dimensions": dimensions,
        "max_tokens": max_tokens,
        "max_batch_size": max_batch_size,
        "supports_batch": supports_batch
    }
    result = validation_engine.validate_business_logic(data, ["model_consistency"], DEFAULT_CONTEXT)
    _convert_validation_result(result)


def validate_embedding_space_consistency(model_dimensions: int, base_dimensions: int, effective_dimensions: int) -> None:
    """Legacy validate_embedding_space_consistency function."""
    data = {
        "model_dimensions": model_dimensions,
        "base_dimensions": base_dimensions,
        "effective_dimensions": effective_dimensions
    }
    result = validation_engine.validate_business_logic(data, ["embedding_space"], DEFAULT_CONTEXT)
    _convert_validation_result(result)