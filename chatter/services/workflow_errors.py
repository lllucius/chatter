"""Unified workflow error handling.

This module provides centralized error handling for workflow execution,
replacing duplicate try/catch blocks across multiple methods.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from chatter.services.workflow_events import (
    WorkflowEvent,
    WorkflowEventType,
    get_event_bus,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowExecutionError(Exception):
    """Base exception for workflow execution errors."""

    def __init__(self, message: str, execution_id: str | None = None):
        """Initialize workflow execution error.
        
        Args:
            message: Error message
            execution_id: Optional execution ID
        """
        super().__init__(message)
        self.execution_id = execution_id


class WorkflowPreparationError(WorkflowExecutionError):
    """Error during workflow preparation.
    
    Raised when preparing LLM, tools, retriever, or workflow definition fails.
    """

    pass


class WorkflowRuntimeError(WorkflowExecutionError):
    """Error during workflow execution.
    
    Raised when the actual workflow execution fails.
    """

    pass


class WorkflowResultProcessingError(WorkflowExecutionError):
    """Error during result processing.
    
    Raised when processing workflow results or saving messages fails.
    """

    pass


def handle_workflow_errors(
    error_stage: str | None = None,
) -> Callable:
    """Decorator for unified workflow error handling.
    
    This decorator:
    - Catches all exceptions during workflow execution
    - Publishes error events to the unified event system
    - Updates execution records
    - Logs errors with proper context
    - Re-raises exceptions for upstream handling
    
    Args:
        error_stage: Optional stage identifier for error context
        
    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to extract context from arguments
            execution_id = None
            user_id = None
            conversation_id = None
            
            # Common patterns for extracting execution context
            if "execution_id" in kwargs:
                execution_id = kwargs["execution_id"]
            if "user_id" in kwargs:
                user_id = kwargs["user_id"]
            if "conversation_id" in kwargs:
                conversation_id = kwargs["conversation_id"]
            
            # Try to get from workflow_input if present
            workflow_input = kwargs.get("workflow_input")
            if workflow_input:
                if not user_id and hasattr(workflow_input, "user_id"):
                    user_id = workflow_input.user_id
                if not conversation_id and hasattr(workflow_input, "conversation_id"):
                    conversation_id = workflow_input.conversation_id

            try:
                return await func(*args, **kwargs)

            except WorkflowPreparationError as e:
                # Handle preparation errors
                logger.error(
                    f"Workflow preparation failed: {e}",
                    execution_id=execution_id or e.execution_id,
                    error_stage=error_stage or "preparation",
                    exc_info=True,
                )

                # Publish error event if we have execution context
                if execution_id or e.execution_id:
                    event_bus = get_event_bus()
                    await event_bus.publish(
                        WorkflowEvent.create(
                            event_type=WorkflowEventType.EXECUTION_FAILED,
                            execution_id=execution_id or e.execution_id,
                            user_id=user_id or "unknown",
                            conversation_id=conversation_id,
                            error=str(e),
                            error_type=type(e).__name__,
                            error_stage=error_stage or "preparation",
                        )
                    )

                # Re-raise
                raise

            except WorkflowRuntimeError as e:
                # Handle runtime errors
                logger.error(
                    f"Workflow execution failed: {e}",
                    execution_id=execution_id or e.execution_id,
                    error_stage=error_stage or "runtime",
                    exc_info=True,
                )

                # Publish error event
                if execution_id or e.execution_id:
                    event_bus = get_event_bus()
                    await event_bus.publish(
                        WorkflowEvent.create(
                            event_type=WorkflowEventType.EXECUTION_FAILED,
                            execution_id=execution_id or e.execution_id,
                            user_id=user_id or "unknown",
                            conversation_id=conversation_id,
                            error=str(e),
                            error_type=type(e).__name__,
                            error_stage=error_stage or "runtime",
                        )
                    )

                # Re-raise
                raise

            except WorkflowResultProcessingError as e:
                # Handle result processing errors
                logger.error(
                    f"Workflow result processing failed: {e}",
                    execution_id=execution_id or e.execution_id,
                    error_stage=error_stage or "result_processing",
                    exc_info=True,
                )

                # Publish error event
                if execution_id or e.execution_id:
                    event_bus = get_event_bus()
                    await event_bus.publish(
                        WorkflowEvent.create(
                            event_type=WorkflowEventType.EXECUTION_FAILED,
                            execution_id=execution_id or e.execution_id,
                            user_id=user_id or "unknown",
                            conversation_id=conversation_id,
                            error=str(e),
                            error_type=type(e).__name__,
                            error_stage=error_stage or "result_processing",
                        )
                    )

                # Re-raise
                raise

            except Exception as e:
                # Handle unexpected errors
                logger.error(
                    f"Unexpected workflow error: {e}",
                    execution_id=execution_id,
                    error_stage=error_stage or "unknown",
                    exc_info=True,
                )

                # Publish error event if we have execution context
                if execution_id:
                    event_bus = get_event_bus()
                    await event_bus.publish(
                        WorkflowEvent.create(
                            event_type=WorkflowEventType.EXECUTION_FAILED,
                            execution_id=execution_id,
                            user_id=user_id or "unknown",
                            conversation_id=conversation_id,
                            error=str(e),
                            error_type=type(e).__name__,
                            error_stage=error_stage or "unknown",
                        )
                    )

                # Re-raise
                raise

        return wrapper

    return decorator
