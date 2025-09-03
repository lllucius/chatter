"""Rate limiting utilities for API and tool access control.

This module provides a compatibility layer for the existing rate limiter
interface while using the new unified rate limiting system underneath.
"""

import asyncio
import time
from typing import Any

from chatter.config import settings
from chatter.utils.logging import get_logger
from chatter.utils.unified_rate_limiter import (
    RateLimitExceeded as UnifiedRateLimitExceeded,
    get_unified_rate_limiter,
)

logger = get_logger(__name__)


class RateLimitExceeded(Exception):
    """Rate limit exceeded error (compatibility layer)."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class RateLimiter:
    """Token bucket rate limiter with per-key limits (compatibility layer).
    
    This class maintains the same API as the original but uses the unified
    rate limiting system underneath for consistency.
    """

    def __init__(self):
        """Initialize rate limiter."""
        self._unified_limiter = get_unified_rate_limiter()

    async def check_rate_limit(
        self,
        key: str,
        limit_per_hour: int | None = None,
        limit_per_day: int | None = None,
    ) -> dict[str, Any]:
        """Check if request is within rate limits.
        
        Args:
            key: Unique identifier for rate limiting (e.g., user_id:tool_name)
            limit_per_hour: Maximum requests per hour
            limit_per_day: Maximum requests per day
            
        Returns:
            Rate limit info including remaining counts
            
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        try:
            # Check hourly limit if specified
            if limit_per_hour is not None:
                status_hour = await self._unified_limiter.check_rate_limit(
                    key=key,
                    limit=limit_per_hour,
                    window=3600,  # 1 hour in seconds
                    identifier="tool_hourly",
                )
                hour_remaining = status_hour["remaining"]
            else:
                hour_remaining = None

            # Check daily limit if specified
            if limit_per_day is not None:
                status_day = await self._unified_limiter.check_rate_limit(
                    key=key,
                    limit=limit_per_day,
                    window=86400,  # 1 day in seconds
                    identifier="tool_daily",
                )
                day_remaining = status_day["remaining"]
            else:
                day_remaining = None

            return {
                "allowed": True,
                "hour_remaining": hour_remaining,
                "day_remaining": day_remaining,
                "hour_limit": limit_per_hour,
                "day_limit": limit_per_day,
            }

        except UnifiedRateLimitExceeded as e:
            # Convert to the expected exception type
            if "tool_hourly" in str(e.message):
                raise RateLimitExceeded(
                    f"Hourly rate limit exceeded. Limit: {limit_per_hour}/hour"
                )
            elif "tool_daily" in str(e.message):
                raise RateLimitExceeded(
                    f"Daily rate limit exceeded. Limit: {limit_per_day}/day"
                )
            else:
                raise RateLimitExceeded(e.message)

    async def get_remaining_quota(
        self,
        key: str,
        limit_per_hour: int | None = None,
        limit_per_day: int | None = None,
    ) -> dict[str, Any]:
        """Get remaining quota without consuming tokens.
        
        Args:
            key: Unique identifier for rate limiting
            limit_per_hour: Maximum requests per hour
            limit_per_day: Maximum requests per day
            
        Returns:
            Remaining quota information
        """
        hour_remaining = limit_per_hour
        day_remaining = limit_per_day

        try:
            if limit_per_hour is not None:
                status_hour = await self._unified_limiter.get_status(
                    key=key,
                    limit=limit_per_hour,
                    window=3600,
                    identifier="tool_hourly",
                )
                hour_remaining = status_hour["remaining"]
        except Exception as e:
            logger.warning(f"Failed to get hourly quota for {key}: {e}")

        try:
            if limit_per_day is not None:
                status_day = await self._unified_limiter.get_status(
                    key=key,
                    limit=limit_per_day,
                    window=86400,
                    identifier="tool_daily",
                )
                day_remaining = status_day["remaining"]
        except Exception as e:
            logger.warning(f"Failed to get daily quota for {key}: {e}")

        return {
            "hour_remaining": hour_remaining,
            "day_remaining": day_remaining,
            "hour_limit": limit_per_hour,
            "day_limit": limit_per_day,
        }

    async def reset_limits(self, key: str) -> None:
        """Reset rate limits for a key.
        
        Args:
            key: Unique identifier to reset
        """
        try:
            await self._unified_limiter.reset(key, identifier="tool_hourly")
            await self._unified_limiter.reset(key, identifier="tool_daily")
        except Exception as e:
            logger.warning(f"Failed to reset limits for {key}: {e}")

    async def cleanup_old_buckets(self, max_age: int = 86400) -> None:
        """Clean up old unused buckets.
        
        Args:
            max_age: Maximum age in seconds before cleanup (default 1 day)
        """
        # The unified rate limiter handles cleanup automatically
        # through cache TTL and periodic cleanup
        await self._unified_limiter.cleanup_old_limiters(max_age)


# Global rate limiter instance (compatibility)
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter