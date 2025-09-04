"""Core validation engine that orchestrates all validation operations."""

import asyncio
from typing import Any, Dict, List, Optional, Union, Type
from abc import ABC, abstractmethod

from .context import ValidationContext, DEFAULT_CONTEXT
from .exceptions import ValidationError, ValidationErrors, SecurityValidationError
from .validators import BaseValidator


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(
        self, 
        is_valid: bool = True, 
        value: Any = None,
        errors: Optional[List[ValidationError]] = None,
        warnings: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.is_valid = is_valid
        self.value = value
        self.errors = errors or []
        self.warnings = warnings or []
        self.metadata = metadata or {}
        
    def add_error(self, error: ValidationError):
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False
        
    def add_warning(self, warning: str):
        """Add a validation warning."""
        self.warnings.append(warning)
        
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result into this one."""
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.metadata.update(other.metadata)


class ValidationEngine:
    """Core validation engine that orchestrates all validation operations."""
    
    def __init__(self):
        self._validators: Dict[str, BaseValidator] = {}
        self._rules: Dict[str, Dict[str, Any]] = {}
        self._initialize_default_validators()
        
    def _initialize_default_validators(self):
        """Initialize default validators."""
        # Import here to avoid circular imports
        from .validators import (
            InputValidator, SecurityValidator, BusinessValidator,
            ConfigValidator, WorkflowValidator, AgentValidator
        )
        
        # Register default validators
        self.register_validator("input", InputValidator())
        self.register_validator("security", SecurityValidator())
        self.register_validator("business", BusinessValidator())
        self.register_validator("config", ConfigValidator())
        self.register_validator("workflow", WorkflowValidator())
        self.register_validator("agent", AgentValidator())
        
    def register_validator(self, name: str, validator: BaseValidator):
        """Register a validator with the engine."""
        self._validators[name] = validator
        
    def unregister_validator(self, name: str):
        """Unregister a validator from the engine."""
        if name in self._validators:
            del self._validators[name]
            
    def get_validator(self, name: str) -> Optional[BaseValidator]:
        """Get a registered validator by name."""
        return self._validators.get(name)
        
    def validate_input(
        self, 
        value: Any, 
        rule_name: str, 
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """Validate user input using the input validator."""
        context = context or DEFAULT_CONTEXT
        
        if not context.is_validator_enabled("input"):
            return ValidationResult(is_valid=True, value=value)
            
        input_validator = self.get_validator("input")
        if not input_validator:
            raise ValidationError("Input validator not available")
            
        return input_validator.validate(value, rule_name, context)
        
    def validate_security(
        self, 
        value: str, 
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """Validate input for security threats."""
        context = context or DEFAULT_CONTEXT
        
        if not context.is_validator_enabled("security"):
            return ValidationResult(is_valid=True, value=value)
            
        security_validator = self.get_validator("security")
        if not security_validator:
            raise ValidationError("Security validator not available")
            
        return security_validator.validate(value, "security_check", context)
        
    def validate_business_logic(
        self, 
        data: Dict[str, Any], 
        rules: List[str], 
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """Validate business logic rules."""
        context = context or DEFAULT_CONTEXT
        
        if not context.is_validator_enabled("business"):
            return ValidationResult(is_valid=True, value=data)
            
        business_validator = self.get_validator("business")
        if not business_validator:
            raise ValidationError("Business validator not available")
            
        return business_validator.validate(data, rules, context)
        
    def validate_workflow(
        self, 
        workflow_config: Dict[str, Any], 
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """Validate workflow configuration."""
        context = context or DEFAULT_CONTEXT
        
        if not context.is_validator_enabled("workflow"):
            return ValidationResult(is_valid=True, value=workflow_config)
            
        workflow_validator = self.get_validator("workflow")
        if not workflow_validator:
            raise ValidationError("Workflow validator not available")
            
        return workflow_validator.validate(workflow_config, "workflow_config", context)
        
    def validate_agent_input(
        self, 
        agent_data: Dict[str, Any], 
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """Validate agent-specific input."""
        context = context or DEFAULT_CONTEXT
        
        if not context.is_validator_enabled("agent"):
            return ValidationResult(is_valid=True, value=agent_data)
            
        agent_validator = self.get_validator("agent")
        if not agent_validator:
            raise ValidationError("Agent validator not available")
            
        return agent_validator.validate(agent_data, "agent_input", context)
        
    def validate_configuration(
        self, 
        config: Dict[str, Any], 
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """Validate configuration settings."""
        context = context or DEFAULT_CONTEXT
        
        if not context.is_validator_enabled("config"):
            return ValidationResult(is_valid=True, value=config)
            
        config_validator = self.get_validator("config")
        if not config_validator:
            raise ValidationError("Config validator not available")
            
        return config_validator.validate(config, "config_check", context)
        
    def validate_multiple(
        self, 
        validations: List[Dict[str, Any]], 
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """Validate multiple items and collect all results."""
        context = context or DEFAULT_CONTEXT
        combined_result = ValidationResult()
        
        for validation in validations:
            validator_name = validation.get("validator")
            value = validation.get("value")
            rule = validation.get("rule", "default")
            
            if validator_name and validator_name in self._validators:
                validator = self._validators[validator_name]
                result = validator.validate(value, rule, context)
                combined_result.merge(result)
                
        return combined_result
        
    async def validate_async(
        self, 
        validator_name: str, 
        value: Any, 
        rule: str, 
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """Asynchronously validate using a specific validator."""
        context = context or DEFAULT_CONTEXT
        
        if validator_name not in self._validators:
            raise ValidationError(f"Validator '{validator_name}' not found")
            
        validator = self._validators[validator_name]
        
        # Check if validator supports async
        if hasattr(validator, 'validate_async'):
            return await validator.validate_async(value, rule, context)
        else:
            # Fall back to sync validation in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, validator.validate, value, rule, context
            )
            
    def validate_with_recovery(
        self, 
        validator_name: str, 
        value: Any, 
        rule: str, 
        context: Optional[ValidationContext] = None,
        recovery_rules: Optional[List[str]] = None
    ) -> ValidationResult:
        """Validate with fallback recovery rules if initial validation fails."""
        context = context or DEFAULT_CONTEXT
        
        if validator_name not in self._validators:
            raise ValidationError(f"Validator '{validator_name}' not found")
            
        validator = self._validators[validator_name]
        
        # Try primary validation
        result = validator.validate(value, rule, context)
        
        # If validation failed and recovery rules are provided, try them
        if not result.is_valid and recovery_rules:
            for recovery_rule in recovery_rules:
                try:
                    recovery_result = validator.validate(value, recovery_rule, context)
                    if recovery_result.is_valid:
                        # Add warning about using recovery rule
                        recovery_result.add_warning(
                            f"Validation passed using recovery rule '{recovery_rule}'"
                        )
                        return recovery_result
                except Exception:
                    continue
                    
        return result
        
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of registered validators and their capabilities."""
        summary = {
            "registered_validators": list(self._validators.keys()),
            "validator_details": {}
        }
        
        for name, validator in self._validators.items():
            summary["validator_details"][name] = {
                "class": validator.__class__.__name__,
                "supported_rules": getattr(validator, 'supported_rules', []),
                "description": getattr(validator, 'description', "No description available")
            }
            
        return summary