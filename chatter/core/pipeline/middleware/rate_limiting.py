"""Rate limiting middleware for workflow pipeline.

This middleware provides request rate limiting to prevent abuse.
"""

from __future__ import annotations

import time
from collections import deque
from typing import TYPE_CHECKING

from chatter.core.pipeline.base import ExecutionContext, ExecutionResult, Middleware
from chatter.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from chatter.core.workflow_node_factory import Workflow

logger = get_logger(__name__)


class RateLimitingMiddleware(Middleware):
    """Middleware for rate limiting workflow executions.
    
    This middleware:
    - Limits executions per user/global
    - Supports sliding window rate limiting
    - Raises RateLimitExceeded on violations
    - Integrates with unified rate limiter
    """

    def __init__(
        self,
        max_requests: int = 60,
        window_seconds: int = 60,
        per_user: bool = True,
    ):
        """Initialize rate limiting middleware.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
            per_user: If True, rate limit per user; if False, global
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.per_user = per_user
        
        # Request tracking
        self._requests: dict[str, deque[float]] = {}
        self._global_requests: deque[float] = deque()

    async def __call__(
        self,
        workflow: Workflow,
        context: ExecutionContext,
        next: Callable,
    ) -> ExecutionResult:
        """Execute with rate limiting.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            next: Next middleware in chain
            
        Returns:
            Execution result
            
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        # Determine rate limit key
        if self.per_user:
            rate_limit_key = context.user_id
        else:
            rate_limit_key = "global"
        
        # Check rate limit
        if not self._check_rate_limit(rate_limit_key):
            execution_id = context.metadata.get("execution_id", "unknown")
            logger.warning(
                f"Rate limit exceeded for {rate_limit_key} "
                f"(execution {execution_id})"
            )
            raise RateLimitExceeded(
                f"Rate limit exceeded: {self.max_requests} requests "
                f"per {self.window_seconds} seconds"
            )
        
        # Record request
        self._record_request(rate_limit_key)
        
        # Execute workflow
        return await next(workflow, context)
    
    def _check_rate_limit(self, key: str) -> bool:
        """Check if rate limit allows request.
        
        Args:
            key: Rate limit key (user_id or "global")
            
        Returns:
            True if request is allowed
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Get or create request queue for this key
        if key not in self._requests:
            self._requests[key] = deque()
        
        requests = self._requests[key]
        
        # Remove expired requests
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # Check if under limit
        return len(requests) < self.max_requests
    
    def _record_request(self, key: str):
        """Record a request.
        
        Args:
            key: Rate limit key (user_id or "global")
        """
        current_time = time.time()
        
        if key not in self._requests:
            self._requests[key] = deque()
        
        self._requests[key].append(current_time)
    
    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests for key.
        
        Args:
            key: Rate limit key
            
        Returns:
            Number of remaining requests
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        if key not in self._requests:
            return self.max_requests
        
        requests = self._requests[key]
        
        # Remove expired requests
        while requests and requests[0] < window_start:
            requests.popleft()
        
        return max(0, self.max_requests - len(requests))
    
    def reset_user(self, user_id: str):
        """Reset rate limit for user.
        
        Args:
            user_id: User ID to reset
        """
        if user_id in self._requests:
            del self._requests[user_id]
    
    def reset_all(self):
        """Reset all rate limits."""
        self._requests.clear()
        self._global_requests.clear()


class RateLimitExceeded(Exception):
    """Rate limit exceeded error."""
    
    pass
