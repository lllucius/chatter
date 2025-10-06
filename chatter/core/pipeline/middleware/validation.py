"""Validation middleware for workflow pipeline.

This middleware validates workflow inputs and outputs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from chatter.core.pipeline.base import ExecutionContext, ExecutionResult, Middleware
from chatter.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from chatter.core.workflow_node_factory import Workflow

logger = get_logger(__name__)


class ValidationMiddleware(Middleware):
    """Middleware for input/output validation.
    
    This middleware:
    - Validates execution context before execution
    - Validates execution result after execution
    - Provides extensible validation rules
    - Raises ValidationError on failures
    """

    def __init__(
        self,
        validate_input: bool = True,
        validate_output: bool = True,
        strict_mode: bool = False,
    ):
        """Initialize validation middleware.
        
        Args:
            validate_input: Whether to validate input
            validate_output: Whether to validate output
            strict_mode: If True, raise on validation warnings
        """
        self.validate_input = validate_input
        self.validate_output = validate_output
        self.strict_mode = strict_mode

    async def __call__(
        self,
        workflow: Workflow,
        context: ExecutionContext,
        next: Callable,
    ) -> ExecutionResult:
        """Execute with validation.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            next: Next middleware in chain
            
        Returns:
            Execution result
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate input
        if self.validate_input:
            self._validate_context(context)
        
        # Execute workflow
        result = await next(workflow, context)
        
        # Validate output
        if self.validate_output:
            self._validate_result(result, context)
        
        return result
    
    def _validate_context(self, context: ExecutionContext):
        """Validate execution context.
        
        Args:
            context: Context to validate
            
        Raises:
            ValidationError: If validation fails
        """
        errors = []
        warnings = []
        
        # Required fields
        if not context.user_id:
            errors.append("user_id is required")
        
        if not context.initial_state:
            errors.append("initial_state is required")
        
        # State validation
        if context.initial_state:
            if "messages" not in context.initial_state:
                warnings.append("initial_state missing 'messages' field")
            
            messages = context.initial_state.get("messages", [])
            if not isinstance(messages, list):
                errors.append("initial_state.messages must be a list")
        
        # Metadata validation
        if context.metadata:
            # Warn if missing common metadata
            if not context.metadata.get("provider"):
                warnings.append("metadata missing 'provider' field")
            
            if not context.metadata.get("model"):
                warnings.append("metadata missing 'model' field")
        
        # Log warnings
        if warnings:
            logger.warning(
                f"Validation warnings: {', '.join(warnings)}",
                execution_id=context.metadata.get("execution_id"),
            )
            
            if self.strict_mode:
                errors.extend(warnings)
        
        # Raise on errors
        if errors:
            raise ValidationError(
                f"Context validation failed: {', '.join(errors)}"
            )
    
    def _validate_result(self, result: ExecutionResult, context: ExecutionContext):
        """Validate execution result.
        
        Args:
            result: Result to validate
            context: Execution context (for reference)
            
        Raises:
            ValidationError: If validation fails
        """
        errors = []
        warnings = []
        
        # Check if result has required attributes
        if not hasattr(result, "output"):
            errors.append("result missing 'output' attribute")
        
        if not hasattr(result, "status"):
            errors.append("result missing 'status' attribute")
        
        # Validate output structure
        if hasattr(result, "output") and result.output:
            if not isinstance(result.output, dict):
                errors.append("result.output must be a dict")
            
            # Check for messages in output
            if isinstance(result.output, dict):
                if "messages" not in result.output:
                    warnings.append("result.output missing 'messages' field")
        
        # Validate status
        if hasattr(result, "status"):
            valid_statuses = {"completed", "failed", "cancelled"}
            if result.status not in valid_statuses:
                warnings.append(
                    f"result.status '{result.status}' not in {valid_statuses}"
                )
        
        # Log warnings
        if warnings:
            logger.warning(
                f"Validation warnings: {', '.join(warnings)}",
                execution_id=context.metadata.get("execution_id"),
            )
            
            if self.strict_mode:
                errors.extend(warnings)
        
        # Raise on errors
        if errors:
            raise ValidationError(
                f"Result validation failed: {', '.join(errors)}"
            )


class ValidationError(Exception):
    """Validation error."""
    
    pass
