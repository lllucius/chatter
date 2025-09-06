"""Core validation engine that orchestrates all validation operations."""

import asyncio
from typing import Any

from .context import DEFAULT_CONTEXT, ValidationContext
from .exceptions import (
    ValidationError,
)
from .results import ValidationResult
from .validators import BaseValidator


class ValidationEngine:
    """Core validation engine that orchestrates all validation operations."""

    def __init__(self):
        self._validators: dict[str, BaseValidator] = {}
        self._rules: dict[str, dict[str, Any]] = {}
        self._initialize_default_validators()

    def _initialize_default_validators(self):
        """Initialize default validators."""
        # Import here to avoid circular imports
        from .validators import (
            AgentValidator,
            BusinessValidator,
            ConfigValidator,
            InputValidator,
            SecurityValidator,
            WorkflowValidator,
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

    def get_validator(self, name: str) -> BaseValidator | None:
        """Get a registered validator by name."""
        return self._validators.get(name)

    def validate_input(
        self,
        value: Any,
        rule_name: str,
        context: ValidationContext | None = None,
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
        self, value: str, context: ValidationContext | None = None
    ) -> ValidationResult:
        """Validate input for security threats."""
        context = context or DEFAULT_CONTEXT

        if not context.is_validator_enabled("security"):
            return ValidationResult(is_valid=True, value=value)

        security_validator = self.get_validator("security")
        if not security_validator:
            raise ValidationError("Security validator not available")

        return security_validator.validate(
            value, "security_check", context
        )

    def validate_business_logic(
        self,
        data: dict[str, Any],
        rules: list[str],
        context: ValidationContext | None = None,
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
        workflow_config: dict[str, Any],
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate workflow configuration."""
        context = context or DEFAULT_CONTEXT

        if not context.is_validator_enabled("workflow"):
            return ValidationResult(
                is_valid=True, value=workflow_config
            )

        workflow_validator = self.get_validator("workflow")
        if not workflow_validator:
            raise ValidationError("Workflow validator not available")

        return workflow_validator.validate(
            workflow_config, "workflow_config", context
        )

    def validate_agent_input(
        self,
        agent_data: dict[str, Any],
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate agent-specific input."""
        context = context or DEFAULT_CONTEXT

        if not context.is_validator_enabled("agent"):
            return ValidationResult(is_valid=True, value=agent_data)

        agent_validator = self.get_validator("agent")
        if not agent_validator:
            raise ValidationError("Agent validator not available")

        return agent_validator.validate(
            agent_data, "agent_input", context
        )

    def validate_configuration(
        self,
        config: dict[str, Any],
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Validate configuration settings."""
        context = context or DEFAULT_CONTEXT

        if not context.is_validator_enabled("config"):
            return ValidationResult(is_valid=True, value=config)

        config_validator = self.get_validator("config")
        if not config_validator:
            raise ValidationError("Config validator not available")

        return config_validator.validate(
            config, "config_check", context
        )

    def validate_multiple(
        self,
        validations: list[dict[str, Any]],
        context: ValidationContext | None = None,
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
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Asynchronously validate using a specific validator."""
        context = context or DEFAULT_CONTEXT

        if validator_name not in self._validators:
            raise ValidationError(
                f"Validator '{validator_name}' not found"
            )

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
        context: ValidationContext | None = None,
        recovery_rules: list[str] | None = None,
    ) -> ValidationResult:
        """Validate with fallback recovery rules if initial validation fails."""
        context = context or DEFAULT_CONTEXT

        if validator_name not in self._validators:
            raise ValidationError(
                f"Validator '{validator_name}' not found"
            )

        validator = self._validators[validator_name]

        # Try primary validation
        result = validator.validate(value, rule, context)

        # If validation failed and recovery rules are provided, try them
        if not result.is_valid and recovery_rules:
            for recovery_rule in recovery_rules:
                try:
                    recovery_result = validator.validate(
                        value, recovery_rule, context
                    )
                    if recovery_result.is_valid:
                        # Add warning about using recovery rule
                        recovery_result.add_warning(
                            f"Validation passed using recovery rule '{recovery_rule}'"
                        )
                        return recovery_result
                except Exception:
                    continue

        return result

    def get_validation_summary(self) -> dict[str, Any]:
        """Get summary of registered validators and their capabilities."""
        summary = {
            "registered_validators": list(self._validators.keys()),
            "validator_details": {},
        }

        for name, validator in self._validators.items():
            summary["validator_details"][name] = {
                "class": validator.__class__.__name__,
                "supported_rules": getattr(
                    validator, 'supported_rules', []
                ),
                "description": getattr(
                    validator, 'description', "No description available"
                ),
            }

        return summary
