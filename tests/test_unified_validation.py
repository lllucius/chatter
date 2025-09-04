"""Tests for the unified validation system."""

import pytest
from unittest.mock import Mock, patch

from chatter.core.validation import (
    validation_engine,
    ValidationError,
    SecurityValidationError,
    ValidationContext,
    DEFAULT_CONTEXT,
    LENIENT_CONTEXT,
)
from chatter.core.validation.validators import InputValidator, SecurityValidator, BusinessValidator
from chatter.core.validation.engine import ValidationResult


class TestValidationEngine:
    """Test the core validation engine."""
    
    def test_validate_input_success(self):
        """Test successful input validation."""
        result = validation_engine.validate_input("test@example.com", "email", DEFAULT_CONTEXT)
        assert result.is_valid
        assert result.value == "test@example.com"
        
    def test_validate_input_failure(self):
        """Test failed input validation."""
        result = validation_engine.validate_input("invalid-email", "email", DEFAULT_CONTEXT)
        assert not result.is_valid
        assert len(result.errors) > 0
        
    def test_validate_security_success(self):
        """Test successful security validation."""
        result = validation_engine.validate_security("normal text", DEFAULT_CONTEXT)
        assert result.is_valid
        
    def test_validate_security_failure(self):
        """Test failed security validation."""
        result = validation_engine.validate_security("<script>alert('xss')</script>", DEFAULT_CONTEXT)
        assert not result.is_valid
        assert any(isinstance(error, SecurityValidationError) for error in result.errors)


class TestInputValidator:
    """Test the input validator."""
    
    def test_email_validation(self):
        """Test email validation."""
        validator = InputValidator()
        context = ValidationContext()
        
        # Valid email
        result = validator.validate("test@example.com", "email", context)
        assert result.is_valid
        
        # Invalid email
        result = validator.validate("invalid-email", "email", context)
        assert not result.is_valid
        
    def test_username_validation(self):
        """Test username validation."""
        validator = InputValidator()
        context = ValidationContext()
        
        # Valid username
        result = validator.validate("test_user", "username", context)
        assert result.is_valid
        
        # Invalid username (too short)
        result = validator.validate("ab", "username", context)
        assert not result.is_valid
        
        # Invalid username (special chars)
        result = validator.validate("test@user", "username", context)
        assert not result.is_valid
        
    def test_sanitization(self):
        """Test input sanitization."""
        validator = InputValidator()
        context = ValidationContext(sanitize_input=True)
        
        # HTML should be sanitized
        result = validator.validate("<b>test</b>", "text", context)
        assert result.is_valid
        assert "<b>" not in result.value
        assert "test" in result.value


class TestSecurityValidator:
    """Test the security validator."""
    
    def test_xss_detection(self):
        """Test XSS detection."""
        validator = SecurityValidator()
        context = ValidationContext()
        
        # Should detect XSS
        result = validator.validate("<script>alert('xss')</script>", "xss_check", context)
        assert not result.is_valid
        
        # Normal text should pass
        result = validator.validate("normal text", "xss_check", context)
        assert result.is_valid
        
    def test_sql_injection_detection(self):
        """Test SQL injection detection."""
        validator = SecurityValidator()
        context = ValidationContext()
        
        # Should detect SQL injection
        result = validator.validate("'; DROP TABLE users; --", "sql_injection_check", context)
        assert not result.is_valid
        
        # Normal text should pass
        result = validator.validate("normal query text", "sql_injection_check", context)
        assert result.is_valid
        
    def test_path_traversal_detection(self):
        """Test path traversal detection."""
        validator = SecurityValidator()
        context = ValidationContext()
        
        # Should detect path traversal
        result = validator.validate("../../../etc/passwd", "path_traversal_check", context)
        assert not result.is_valid
        
        # Normal path should pass
        result = validator.validate("normal/path/file.txt", "path_traversal_check", context)
        assert result.is_valid


class TestBusinessValidator:
    """Test the business validator."""
    
    def test_model_consistency(self):
        """Test model consistency validation."""
        validator = BusinessValidator()
        context = ValidationContext()
        
        # Valid embedding model
        data = {
            "model_type": "EMBEDDING",
            "dimensions": 1536,
            "supports_batch": True,
            "max_batch_size": 100
        }
        result = validator.validate(data, "model_consistency", context)
        assert result.is_valid
        
        # Invalid embedding model (no dimensions)
        data = {
            "model_type": "EMBEDDING",
            "dimensions": None
        }
        result = validator.validate(data, "model_consistency", context)
        assert not result.is_valid
        
    def test_embedding_space_validation(self):
        """Test embedding space validation."""
        validator = BusinessValidator()
        context = ValidationContext()
        
        # Valid embedding space
        data = {
            "model_dimensions": 1536,
            "base_dimensions": 1536,
            "effective_dimensions": 1536
        }
        result = validator.validate(data, "embedding_space", context)
        assert result.is_valid
        
        # Invalid embedding space (dimension mismatch)
        data = {
            "model_dimensions": 1536,
            "base_dimensions": 512,
            "effective_dimensions": 512
        }
        result = validator.validate(data, "embedding_space", context)
        assert not result.is_valid


class TestValidationContext:
    """Test validation context functionality."""
    
    def test_context_overrides(self):
        """Test context overrides."""
        context = ValidationContext(
            max_length_overrides={"email": 100}
        )
        
        # Check override is applied
        assert context.get_max_length("email", 254) == 100
        assert context.get_max_length("username", 50) == 50
        
    def test_context_modes(self):
        """Test different validation modes."""
        from chatter.core.validation.context import ValidationMode
        
        strict_context = ValidationContext(mode=ValidationMode.STRICT)
        lenient_context = ValidationContext(mode=ValidationMode.LENIENT)
        
        assert strict_context.mode.value == "strict"
        assert lenient_context.mode.value == "lenient"
        
    def test_validator_enablement(self):
        """Test validator enablement control."""
        context = ValidationContext(
            enabled_validators={"input", "security"}
        )
        
        assert context.is_validator_enabled("input")
        assert context.is_validator_enabled("security")
        assert not context.is_validator_enabled("business")


class TestBackwardsCompatibility:
    """Test backwards compatibility layer."""
    
    def test_legacy_imports(self):
        """Test that legacy imports still work."""
        # Skip this test as compat module doesn't exist in current implementation
        # This functionality was removed during refactoring
        pytest.skip("Backwards compatibility module not implemented in current version")
        
    def test_legacy_validator_classes(self):
        """Test legacy validator class compatibility."""
        # Skip this test as compat module doesn't exist in current implementation
        # This functionality was removed during refactoring
        pytest.skip("Backwards compatibility module not implemented in current version")


class TestValidationResult:
    """Test validation result functionality."""
    
    def test_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult()
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        
    def test_result_with_errors(self):
        """Test ValidationResult with errors."""
        error = ValidationError("Test error")
        result = ValidationResult(is_valid=False, errors=[error])
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].message == "Test error"
        
    def test_result_merging(self):
        """Test merging validation results."""
        result1 = ValidationResult(is_valid=True)
        result2 = ValidationResult(is_valid=False, errors=[ValidationError("Error")])
        
        result1.merge(result2)
        
        assert not result1.is_valid
        assert len(result1.errors) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])