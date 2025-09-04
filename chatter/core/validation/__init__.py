"""Unified validation architecture for Chatter.

This module provides a centralized validation system that consolidates all validation
logic scattered across the codebase into a unified, extensible architecture.

Key components:
- ValidationEngine: Core validation orchestrator
- BaseValidator: Base class for all validators
- ValidationContext: Contextual validation information
- Validation exceptions with consistent error handling
"""

from .engine import ValidationEngine
from .exceptions import (
    ValidationError,
    SecurityValidationError,
    BusinessValidationError,
    ConfigurationValidationError,
)
from .context import ValidationContext, DEFAULT_CONTEXT
from .validators import (
    InputValidator,
    SecurityValidator,
    BusinessValidator,
    ConfigValidator,
    WorkflowValidator,
    AgentValidator,
)

# Global validation engine instance
validation_engine = ValidationEngine()

# Convenience functions for common validations
def validate_input(value, rule_name: str, context: ValidationContext = None):
    """Validate user input using the unified validation engine."""
    return validation_engine.validate_input(value, rule_name, context or DEFAULT_CONTEXT)

def validate_security(value: str, context: ValidationContext = None):
    """Validate input for security threats."""
    return validation_engine.validate_security(value, context or DEFAULT_CONTEXT)

def validate_business_logic(data: dict, rules: list, context: ValidationContext = None):
    """Validate business logic rules."""
    return validation_engine.validate_business_logic(data, rules, context or DEFAULT_CONTEXT)

__all__ = [
    'ValidationEngine',
    'ValidationError',
    'SecurityValidationError', 
    'BusinessValidationError',
    'ConfigurationValidationError',
    'ValidationContext',
    'InputValidator',
    'SecurityValidator',
    'BusinessValidator',
    'ConfigValidator',
    'WorkflowValidator',
    'AgentValidator',
    'validation_engine',
    'validate_input',
    'validate_security',
    'validate_business_logic',
    'DEFAULT_CONTEXT',
]