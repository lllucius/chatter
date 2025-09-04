"""Rate limiter compatibility module.

This module provides backward compatibility for imports from chatter.utils.rate_limiter.
The actual implementation is now in chatter.utils.unified_rate_limiter, but this module
re-exports the necessary classes and functions for backward compatibility.

This module is deprecated. New code should use chatter.utils.unified_rate_limiter directly.
"""

import warnings
from typing import Dict, Any

# Import the actual implementations from unified_rate_limiter
from chatter.utils.unified_rate_limiter import (
    RateLimitExceeded,
    UnifiedRateLimiter,
    get_unified_rate_limiter,
)

# Re-export for backward compatibility
__all__ = [
    'RateLimitExceeded',
    'get_rate_limiter',
]

def get_rate_limiter():
    """Get a rate limiter instance with tool-compatible interface.
    
    This is a compatibility wrapper around the unified rate limiter.
    
    Returns:
        ToolRateLimiter: A rate limiter with tool-compatible interface
    """
    warnings.warn(
        "chatter.utils.rate_limiter is deprecated. "
        "Use chatter.utils.unified_rate_limiter instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Return a wrapper that provides the expected tool rate limiting interface
    return ToolRateLimiter()


class ToolRateLimiter:
    """Tool rate limiter compatibility wrapper."""
    
    def __init__(self):
        self._limiter = get_unified_rate_limiter()
    
    async def check_rate_limit(
        self, 
        key: str, 
        limit_per_hour: int = 100,
        limit_per_day: int = 1000
    ) -> Dict[str, Any]:
        """Check rate limit with tool-compatible interface.
        
        Args:
            key: Rate limiting key
            limit_per_hour: Hourly limit
            limit_per_day: Daily limit
            
        Returns:
            Dict with hour_remaining and day_remaining
            
        Raises:
            RateLimitExceeded: If either limit is exceeded
        """
        # Check hourly limit
        try:
            hour_status = await self._limiter.check_rate_limit(
                key=f"{key}:hour",
                limit=limit_per_hour,
                window=3600,
                identifier="hourly_limit"
            )
        except RateLimitExceeded:
            # Re-raise with tool-compatible message
            raise RateLimitExceeded(f"Hourly rate limit of {limit_per_hour} exceeded for {key}")
        
        # Check daily limit
        try:
            day_status = await self._limiter.check_rate_limit(
                key=f"{key}:day",
                limit=limit_per_day,
                window=86400,
                identifier="daily_limit"
            )
        except RateLimitExceeded:
            # Re-raise with tool-compatible message
            raise RateLimitExceeded(f"Daily rate limit of {limit_per_day} exceeded for {key}")
        
        return {
            "hour_remaining": hour_status["remaining"],
            "day_remaining": day_status["remaining"]
        }