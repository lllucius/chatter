"""Workflow validation utilities.

DEPRECATED: This module has been replaced by the unified validation system.
Import from chatter.core.validation for new functionality.
"""

import warnings
from typing import Any, Dict, List, Optional

# Import from the unified validation system
from chatter.core.validation import validation_engine, ValidationContext, DEFAULT_CONTEXT
from chatter.core.validation.exceptions import ValidationError as NewValidationError
from chatter.core.validation.validators import WorkflowValidator as NewWorkflowValidator

# Backwards compatibility classes
class ValidationResult:
    """Legacy ValidationResult for backwards compatibility."""
    
    def __init__(self, valid: bool = True, errors: List[str] = None):
        self.valid = valid
        self.errors = errors or []


class WorkflowValidator:
    """Legacy WorkflowValidator for backwards compatibility."""
    
    def __init__(self):
        warnings.warn(
            "chatter.core.workflow_validation.WorkflowValidator is deprecated. "
            "Use chatter.core.validation.validators.WorkflowValidator instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self._new_validator = NewWorkflowValidator()
    
    def validate_workflow_request(self, request_data: Dict[str, Any]) -> None:
        """Legacy validate_workflow_request method."""
        result = validation_engine.validate_workflow(request_data, DEFAULT_CONTEXT)
        if not result.is_valid:
            # Raise first error in legacy format
            error_message = result.errors[0].message if result.errors else "Workflow validation failed"
            raise ValidationError(error_message)
    
    def validate_workflow_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Legacy validate_workflow_config method."""
        result = self._new_validator.validate(config, "workflow_config", DEFAULT_CONTEXT)
        return ValidationResult(
            valid=result.is_valid,
            errors=[error.message for error in result.errors]
        )


class ParameterValidator:
    """Legacy ParameterValidator for backwards compatibility."""
    
    def __init__(self):
        warnings.warn(
            "chatter.core.workflow_validation.ParameterValidator is deprecated. "
            "Use chatter.core.validation instead.",
            DeprecationWarning,
            stacklevel=2
        )
    
    def validate_temperature(self, temperature: float) -> ValidationResult:
        """Legacy validate_temperature method."""
        try:
            result = validation_engine.validate_workflow(
                {"temperature": temperature}, DEFAULT_CONTEXT
            )
            return ValidationResult(
                valid=result.is_valid,
                errors=[error.message for error in result.errors]
            )
        except Exception as e:
            return ValidationResult(valid=False, errors=[str(e)])
    
    def validate_max_tokens(self, max_tokens: int) -> ValidationResult:
        """Legacy validate_max_tokens method."""
        try:
            result = validation_engine.validate_workflow(
                {"max_tokens": max_tokens}, DEFAULT_CONTEXT
            )
            return ValidationResult(
                valid=result.is_valid,
                errors=[error.message for error in result.errors]
            )
        except Exception as e:
            return ValidationResult(valid=False, errors=[str(e)])
    
    def validate_model_name(self, model_name: str) -> ValidationResult:
        """Legacy validate_model_name method."""
        try:
            result = validation_engine.validate_input(model_name, "text", DEFAULT_CONTEXT)
            return ValidationResult(
                valid=result.is_valid,
                errors=[error.message for error in result.errors]
            )
        except Exception as e:
            return ValidationResult(valid=False, errors=[str(e)])


class SchemaValidator:
    """Legacy SchemaValidator for backwards compatibility."""
    
    def __init__(self):
        warnings.warn(
            "chatter.core.workflow_validation.SchemaValidator is deprecated. "
            "Use chatter.core.validation instead.",
            DeprecationWarning,
            stacklevel=2
        )
    
    def validate_json_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """Legacy validate_json_schema method."""
        # Basic validation fallback
        errors = []
        required = schema.get('required', [])
        for field in required:
            if field not in data:
                errors.append(f"Required field '{field}' is missing")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)


class StepValidator:
    """Legacy StepValidator for backwards compatibility."""
    
    def __init__(self):
        warnings.warn(
            "chatter.core.workflow_validation.StepValidator is deprecated. "
            "Use chatter.core.validation instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.param_validator = ParameterValidator()
    
    def validate_step(self, step: Dict[str, Any]) -> ValidationResult:
        """Legacy validate_step method."""
        errors = []
        required_fields = ['id', 'name', 'type']
        for field in required_fields:
            if field not in step:
                errors.append(f"Step missing required field: {field}")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def validate_llm_call_step(self, step: Dict[str, Any]) -> ValidationResult:
        """Legacy validate_llm_call_step method.""" 
        errors = []
        config = step.get('config', {})
        
        if 'model' not in config:
            errors.append("LLM step requires 'model' in config")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def validate_condition_step(self, step: Dict[str, Any]) -> ValidationResult:
        """Legacy validate_condition_step method."""
        errors = []
        config = step.get('config', {})
        
        if 'condition' not in config:
            errors.append("Condition step requires 'condition' in config")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def validate_tool_call_step(self, step: Dict[str, Any]) -> ValidationResult:
        """Legacy validate_tool_call_step method."""
        errors = []
        config = step.get('config', {})
        
        if 'tool_name' not in config:
            errors.append("Tool call step requires 'tool_name' in config")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)


# Legacy ValidationError for backwards compatibility  
class ValidationError(Exception):
    """Legacy ValidationError for backwards compatibility."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# Legacy functions
def validate_chat_request(message: str, workflow_type: str = "plain", max_message_length: int = 10000) -> None:
    """Legacy validate_chat_request function."""
    result = validation_engine.validate_workflow({
        "message": message,
        "workflow_type": workflow_type
    }, DEFAULT_CONTEXT)
    
    if not result.is_valid:
        error_message = result.errors[0].message if result.errors else "Chat request validation failed"
        raise ValidationError(error_message)


def validate_conversation_id(conversation_id: Optional[str]) -> None:
    """Legacy validate_conversation_id function."""
    if conversation_id is not None:
        result = validation_engine.validate_agent_input({
            "conversation_id": conversation_id
        }, DEFAULT_CONTEXT)
        
        if not result.is_valid:
            error_message = result.errors[0].message if result.errors else "Conversation ID validation failed"
            raise ValidationError(error_message)


# Issue deprecation warning when this module is imported
warnings.warn(
    "chatter.core.workflow_validation is deprecated. Use chatter.core.validation instead.",
    DeprecationWarning,
    stacklevel=2
)
