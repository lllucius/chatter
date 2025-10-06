"""Retry middleware for workflow pipeline.

This middleware provides automatic retry logic for transient failures.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from chatter.core.pipeline.base import ExecutionContext, ExecutionResult, Middleware
from chatter.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from chatter.core.workflow_node_factory import Workflow

logger = get_logger(__name__)


class RetryMiddleware(Middleware):
    """Middleware for automatic retry logic.
    
    This middleware:
    - Retries failed executions automatically
    - Supports configurable retry count and backoff
    - Only retries transient errors (configurable)
    - Logs retry attempts
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff_seconds: float = 1.0,
        backoff_multiplier: float = 2.0,
        retryable_exceptions: tuple[type[Exception], ...] | None = None,
    ):
        """Initialize retry middleware.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_backoff_seconds: Initial backoff time in seconds
            backoff_multiplier: Multiplier for exponential backoff
            retryable_exceptions: Tuple of exception types to retry
                                 (None = retry all exceptions)
        """
        self.max_retries = max_retries
        self.initial_backoff_seconds = initial_backoff_seconds
        self.backoff_multiplier = backoff_multiplier
        self.retryable_exceptions = retryable_exceptions

    async def __call__(
        self,
        workflow: Workflow,
        context: ExecutionContext,
        next: Callable,
    ) -> ExecutionResult:
        """Execute with retry logic.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            next: Next middleware in chain
            
        Returns:
            Execution result
            
        Raises:
            Exception: If all retries are exhausted
        """
        execution_id = context.metadata.get("execution_id", "unknown")
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(
                        f"Retry attempt {attempt}/{self.max_retries} for execution {execution_id}"
                    )
                
                # Execute workflow
                return await next(workflow, context)
                
            except Exception as e:
                last_exception = e
                
                # Check if this exception is retryable
                if not self._is_retryable(e):
                    logger.warning(
                        f"Non-retryable exception in execution {execution_id}: {e}",
                        exc_info=True,
                    )
                    raise
                
                # Check if we have retries left
                if attempt >= self.max_retries:
                    logger.error(
                        f"Exhausted all {self.max_retries} retries for execution {execution_id}",
                        exc_info=True,
                    )
                    raise
                
                # Calculate backoff time
                backoff = self._calculate_backoff(attempt)
                
                logger.warning(
                    f"Execution {execution_id} failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                    f"retrying in {backoff:.2f}s: {e}"
                )
                
                # Wait before retry
                await asyncio.sleep(backoff)
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected retry loop exit")
    
    def _is_retryable(self, exception: Exception) -> bool:
        """Check if exception is retryable.
        
        Args:
            exception: Exception to check
            
        Returns:
            True if retryable
        """
        if self.retryable_exceptions is None:
            # Retry all exceptions by default
            return True
        
        return isinstance(exception, self.retryable_exceptions)
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff time for attempt.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            Backoff time in seconds
        """
        return self.initial_backoff_seconds * (self.backoff_multiplier ** attempt)


# Common retryable exceptions
class RetryableError(Exception):
    """Base class for retryable errors."""
    pass


class TemporaryServiceError(RetryableError):
    """Temporary service error (e.g., API rate limit, timeout)."""
    pass


class NetworkError(RetryableError):
    """Network connectivity error."""
    pass


class ResourceUnavailableError(RetryableError):
    """Resource temporarily unavailable."""
    pass
