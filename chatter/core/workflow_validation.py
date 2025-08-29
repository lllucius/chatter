"""Workflow validation utilities.

This module provides comprehensive validation for workflow configurations
and parameters, addressing the input validation gap identified in the review.
"""

from typing import Any, Dict, List, Optional, Union
from enum import Enum

from chatter.core.exceptions import WorkflowValidationError, WorkflowConfigurationError, WorkflowExecutionError


class ValidationResult:
    """Result of validation operation."""
    
    def __init__(self, valid: bool = True, errors: Optional[List[str]] = None):
        self.valid = valid
        self.errors = errors or []


class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message
    
    def validate(self, value: Any) -> bool:
        """Validate a value. Override in subclasses."""
        return True


class InputSanitizer:
    """Sanitize and validate user inputs."""
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 10000) -> str:
        """Sanitize text input."""
        if not text:
            return ""
        
        # Remove null bytes and control characters
        sanitized = "".join(
            char for char in text
            if ord(char) >= 32 or char in "\t\n\r"
        )
        
        # Truncate to max length
        sanitized = sanitized[:max_length]
        
        # Strip whitespace
        return sanitized.strip()
    
    @staticmethod
    def sanitize_html(html: str) -> str:
        """Remove potentially dangerous HTML tags."""
        # Basic HTML sanitization - remove script tags and other dangerous elements
        import re
        
        # Remove script tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove other dangerous tags
        dangerous_tags = ['iframe', 'object', 'embed', 'link', 'meta', 'style']
        for tag in dangerous_tags:
            html = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', html, flags=re.IGNORECASE | re.DOTALL)
            html = re.sub(f'<{tag}[^>]*/?>', '', html, flags=re.IGNORECASE)
        
        return html
    
    @staticmethod
    def validate_input_length(text: str, max_length: int) -> ValidationResult:
        """Validate input length."""
        if len(text) > max_length:
            return ValidationResult(
                valid=False,
                errors=[f"Input too long (maximum {max_length} characters)"]
            )
        return ValidationResult()
    
    @staticmethod  
    def validate_no_suspicious_patterns(text: str) -> ValidationResult:
        """Check for suspicious patterns in text."""
        import re
        
        # Check for potential SQL injection patterns
        sql_patterns = [
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b',
            r'[;\'"]\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b',
            r'--\s*',
            r'/\*.*?\*/',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    valid=False,
                    errors=["Text contains potentially malicious patterns"]
                )
        
        return ValidationResult()


class WorkflowType(str, Enum):
    """Supported workflow types."""
    PLAIN = "plain"
    RAG = "rag"
    TOOLS = "tools"
    FULL = "full"


class WorkflowValidator:
    """Validates workflow configurations and parameters."""
    
    # Required parameters for each workflow type
    REQUIRED_PARAMS = {
        WorkflowType.PLAIN: [],
        WorkflowType.RAG: ["retriever"],
        WorkflowType.TOOLS: ["tools"],
        WorkflowType.FULL: ["retriever", "tools"]
    }
    
    # Optional parameters for each workflow type
    OPTIONAL_PARAMS = {
        "all": ["system_message", "enable_memory", "memory_window"],
        WorkflowType.RAG: ["max_documents", "similarity_threshold"],
        WorkflowType.TOOLS: ["max_tool_calls", "tool_timeout"],
        WorkflowType.FULL: ["max_documents", "similarity_threshold", "max_tool_calls", "tool_timeout"]
    }
    
    # Parameter validation rules
    VALIDATION_RULES = {
        "max_documents": {"type": int, "min": 1, "max": 100},
        "similarity_threshold": {"type": float, "min": 0.0, "max": 1.0},
        "max_tool_calls": {"type": int, "min": 1, "max": 50},
        "tool_timeout": {"type": int, "min": 1, "max": 300},  # seconds
        "memory_window": {"type": int, "min": 1, "max": 100},
        "system_message": {"type": str, "max_length": 10000},
        "enable_memory": {"type": bool}
    }
    
    @classmethod
    def validate_workflow_request(
        cls,
        workflow_type: str,
        retriever: Any = None,
        tools: Optional[List[Any]] = None,
        system_message: Optional[str] = None,
        enable_memory: bool = False,
        **kwargs: Any
    ) -> None:
        """Validate a complete workflow request.
        
        Args:
            workflow_type: Type of workflow
            retriever: Retriever instance for RAG workflows
            tools: List of tools for tool workflows
            system_message: System message override
            enable_memory: Whether to enable conversation memory
            **kwargs: Additional workflow parameters
            
        Raises:
            WorkflowValidationError: If validation fails
        """
        issues = []
        
        # Validate workflow type
        try:
            wf_type = WorkflowType(workflow_type)
        except ValueError:
            raise WorkflowConfigurationError(
                f"Invalid workflow type '{workflow_type}'. "
                f"Must be one of: {', '.join([t.value for t in WorkflowType])}"
            )
        
        # Validate required parameters
        required_params = cls.REQUIRED_PARAMS[wf_type]
        for param in required_params:
            if param == "retriever" and retriever is None:
                issues.append(f"Retriever is required for {workflow_type} workflow")
            elif param == "tools" and (not tools or len(tools) == 0):
                issues.append(f"Tools are required for {workflow_type} workflow")
        
        # Validate parameter types and values
        all_params = {
            "system_message": system_message,
            "enable_memory": enable_memory,
            **kwargs
        }
        
        for param_name, param_value in all_params.items():
            if param_value is not None:
                cls._validate_parameter(param_name, param_value, issues)
        
        # Validate tools if provided
        if tools:
            cls._validate_tools(tools, issues)
        
        # Validate retriever if provided
        if retriever:
            cls._validate_retriever(retriever, issues)
        
        # Validate workflow-specific combinations
        cls._validate_workflow_combinations(wf_type, retriever, tools, kwargs, issues)
        
        if issues:
            raise WorkflowValidationError(
                f"Workflow validation failed for {workflow_type}",
                validation_issues=issues,
                workflow_type=workflow_type
            )
    
    @classmethod
    def _validate_parameter(cls, name: str, value: Any, issues: List[str]) -> None:
        """Validate a single parameter."""
        if name not in cls.VALIDATION_RULES:
            return  # Unknown parameters are allowed
        
        rules = cls.VALIDATION_RULES[name]
        
        # Type validation
        expected_type = rules.get("type")
        if expected_type and not isinstance(value, expected_type):
            issues.append(f"Parameter '{name}' must be of type {expected_type.__name__}")
            return
        
        # Value range validation
        if isinstance(value, (int, float)):
            min_val = rules.get("min")
            max_val = rules.get("max")
            if min_val is not None and value < min_val:
                issues.append(f"Parameter '{name}' must be >= {min_val}")
            if max_val is not None and value > max_val:
                issues.append(f"Parameter '{name}' must be <= {max_val}")
        
        # String length validation
        if isinstance(value, str):
            max_length = rules.get("max_length")
            if max_length and len(value) > max_length:
                issues.append(f"Parameter '{name}' must be <= {max_length} characters")
    
    @classmethod
    def _validate_tools(cls, tools: List[Any], issues: List[str]) -> None:
        """Validate tools list."""
        if not isinstance(tools, list):
            issues.append("Tools must be provided as a list")
            return
        
        if len(tools) == 0:
            issues.append("At least one tool must be provided")
            return
        
        if len(tools) > 20:  # Reasonable limit
            issues.append("Too many tools (maximum 20 allowed)")
        
        # Validate individual tools
        for i, tool in enumerate(tools):
            if not hasattr(tool, 'name'):
                issues.append(f"Tool {i} missing 'name' attribute")
            if not hasattr(tool, 'description'):
                issues.append(f"Tool {i} missing 'description' attribute")
            # Add more tool-specific validations as needed
    
    @classmethod
    def _validate_retriever(cls, retriever: Any, issues: List[str]) -> None:
        """Validate retriever instance."""
        # Check if retriever has required methods
        required_methods = ['get_relevant_documents', 'aget_relevant_documents']
        for method in required_methods:
            if not hasattr(retriever, method):
                issues.append(f"Retriever missing required method '{method}'")
                break  # One method check is enough
    
    @classmethod
    def _validate_workflow_combinations(
        cls,
        workflow_type: WorkflowType,
        retriever: Any,
        tools: Optional[List[Any]],
        params: Dict[str, Any],
        issues: List[str]
    ) -> None:
        """Validate workflow-specific parameter combinations."""
        
        # RAG-specific validations
        if workflow_type in [WorkflowType.RAG, WorkflowType.FULL] and retriever:
            max_docs = params.get("max_documents", 5)
            if max_docs > 20:
                issues.append("max_documents should not exceed 20 for performance reasons")
        
        # Tools-specific validations
        if workflow_type in [WorkflowType.TOOLS, WorkflowType.FULL] and tools:
            max_calls = params.get("max_tool_calls", 10)
            if len(tools) > 10 and max_calls > 5:
                issues.append("When using many tools, consider reducing max_tool_calls")
        
        # Memory-specific validations
        if params.get("enable_memory", False):
            memory_window = params.get("memory_window", 10)
            if memory_window > 50:
                issues.append("Large memory windows may impact performance")
    
    @classmethod
    def validate_workflow_parameters(
        cls,
        workflow_type: str,
        **params: Any
    ) -> Dict[str, Any]:
        """Validate and normalize workflow parameters.
        
        Args:
            workflow_type: Type of workflow
            **params: Workflow parameters
            
        Returns:
            Validated and normalized parameters
            
        Raises:
            WorkflowValidationError: If validation fails
        """
        try:
            wf_type = WorkflowType(workflow_type)
        except ValueError:
            raise WorkflowConfigurationError(
                f"Invalid workflow type '{workflow_type}'"
            )
        
        validated_params = {}
        issues = []
        
        # Validate each parameter
        for name, value in params.items():
            if value is not None:
                cls._validate_parameter(name, value, issues)
                validated_params[name] = value
        
        # Set defaults for missing optional parameters
        optional_params = cls.OPTIONAL_PARAMS.get("all", [])
        if wf_type in cls.OPTIONAL_PARAMS:
            optional_params.extend(cls.OPTIONAL_PARAMS[wf_type])
        
        # Set sensible defaults
        defaults = {
            "max_documents": 5,
            "similarity_threshold": 0.7,
            "max_tool_calls": 10,
            "tool_timeout": 30,
            "memory_window": 10,
            "enable_memory": False
        }
        
        for param in optional_params:
            if param not in validated_params and param in defaults:
                validated_params[param] = defaults[param]
        
        if issues:
            raise WorkflowValidationError(
                f"Parameter validation failed for {workflow_type}",
                validation_issues=issues,
                workflow_type=workflow_type
            )
        
        return validated_params
    
    @classmethod
    def get_supported_workflow_types(cls) -> List[str]:
        """Get list of supported workflow types."""
        return [t.value for t in WorkflowType]
    
    @classmethod
    def get_required_parameters(cls, workflow_type: str) -> List[str]:
        """Get required parameters for a workflow type."""
        try:
            wf_type = WorkflowType(workflow_type)
            return cls.REQUIRED_PARAMS[wf_type]
        except ValueError:
            raise WorkflowConfigurationError(f"Invalid workflow type '{workflow_type}'")
    
    @classmethod
    def get_optional_parameters(cls, workflow_type: str) -> List[str]:
        """Get optional parameters for a workflow type."""
        try:
            wf_type = WorkflowType(workflow_type)
            params = cls.OPTIONAL_PARAMS.get("all", []).copy()
            if wf_type in cls.OPTIONAL_PARAMS:
                params.extend(cls.OPTIONAL_PARAMS[wf_type])
            return params
        except ValueError:
            raise WorkflowConfigurationError(f"Invalid workflow type '{workflow_type}'")


# Convenience functions for common validations
def validate_chat_request(
    message: str,
    workflow_type: str = "plain",
    max_message_length: int = 10000
) -> None:
    """Validate a chat request.
    
    Args:
        message: User message
        workflow_type: Type of workflow
        max_message_length: Maximum message length
        
    Raises:
        WorkflowValidationError: If validation fails
    """
    issues = []
    
    if not message or not message.strip():
        issues.append("Message cannot be empty")
    
    if len(message) > max_message_length:
        issues.append(f"Message too long (maximum {max_message_length} characters)")
    
    # Validate workflow type
    if workflow_type not in WorkflowValidator.get_supported_workflow_types():
        issues.append(f"Invalid workflow type '{workflow_type}'")
    
    if issues:
        raise WorkflowValidationError(
            "Chat request validation failed",
            validation_issues=issues
        )


def validate_conversation_id(conversation_id: Optional[str]) -> None:
    """Validate conversation ID format.
    
    Args:
        conversation_id: Conversation ID to validate
        
    Raises:
        WorkflowValidationError: If validation fails
    """
    if conversation_id is not None:
        if not isinstance(conversation_id, str):
            raise WorkflowValidationError(
                "Conversation ID must be a string",
                validation_issues=["conversation_id must be string type"]
            )
        
        if len(conversation_id.strip()) == 0:
            raise WorkflowValidationError(
                "Conversation ID cannot be empty",
                validation_issues=["conversation_id cannot be empty"]
            )
        
        # Add format validation if needed (UUID, etc.)
        # For now, just check it's a non-empty string