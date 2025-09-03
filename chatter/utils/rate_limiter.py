"""Rate limiting utilities for API and tool access control."""

import asyncio
import time
from collections import defaultdict
from typing import Any

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class RateLimitExceeded(Exception):
    """Rate limit exceeded error."""
    pass


class RateLimiter:
    """Token bucket rate limiter with per-key limits."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self._buckets: dict[str, dict[str, Any]] = defaultdict(dict)
        self._lock = asyncio.Lock()
    
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
        async with self._lock:
            now = time.time()
            bucket = self._buckets[key]
            
            # Initialize bucket if needed
            if 'hour_tokens' not in bucket:
                bucket.update({
                    'hour_tokens': limit_per_hour or float('inf'),
                    'hour_last_refill': now,
                    'day_tokens': limit_per_day or float('inf'),
                    'day_last_refill': now,
                })
            
            # Refill hourly tokens
            if limit_per_hour is not None:
                hour_elapsed = now - bucket['hour_last_refill']
                if hour_elapsed >= 3600:  # 1 hour
                    # Full refill after an hour
                    bucket['hour_tokens'] = limit_per_hour
                    bucket['hour_last_refill'] = now
                else:
                    # Partial refill based on time elapsed
                    refill_rate = limit_per_hour / 3600  # tokens per second
                    tokens_to_add = hour_elapsed * refill_rate
                    bucket['hour_tokens'] = min(
                        limit_per_hour,
                        bucket['hour_tokens'] + tokens_to_add
                    )
                    bucket['hour_last_refill'] = now
            
            # Refill daily tokens
            if limit_per_day is not None:
                day_elapsed = now - bucket['day_last_refill']
                if day_elapsed >= 86400:  # 1 day
                    # Full refill after a day
                    bucket['day_tokens'] = limit_per_day
                    bucket['day_last_refill'] = now
                else:
                    # Partial refill based on time elapsed
                    refill_rate = limit_per_day / 86400  # tokens per second
                    tokens_to_add = day_elapsed * refill_rate
                    bucket['day_tokens'] = min(
                        limit_per_day,
                        bucket['day_tokens'] + tokens_to_add
                    )
                    bucket['day_last_refill'] = now
            
            # Check limits
            hour_remaining = int(bucket.get('hour_tokens', float('inf')))
            day_remaining = int(bucket.get('day_tokens', float('inf')))
            
            if limit_per_hour is not None and bucket['hour_tokens'] < 1:
                raise RateLimitExceeded(
                    f"Hourly rate limit exceeded. Limit: {limit_per_hour}/hour"
                )
            
            if limit_per_day is not None and bucket['day_tokens'] < 1:
                raise RateLimitExceeded(
                    f"Daily rate limit exceeded. Limit: {limit_per_day}/day"
                )
            
            # Consume tokens
            if limit_per_hour is not None:
                bucket['hour_tokens'] -= 1
                hour_remaining -= 1
            
            if limit_per_day is not None:
                bucket['day_tokens'] -= 1
                day_remaining -= 1
            
            return {
                'allowed': True,
                'hour_remaining': hour_remaining if limit_per_hour else None,
                'day_remaining': day_remaining if limit_per_day else None,
                'hour_limit': limit_per_hour,
                'day_limit': limit_per_day,
            }
    
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
        async with self._lock:
            bucket = self._buckets.get(key, {})
            
            if not bucket:
                return {
                    'hour_remaining': limit_per_hour,
                    'day_remaining': limit_per_day,
                    'hour_limit': limit_per_hour,
                    'day_limit': limit_per_day,
                }
            
            # Calculate current tokens (similar to check_rate_limit but without consuming)
            now = time.time()
            
            hour_remaining = limit_per_hour
            if limit_per_hour is not None and 'hour_tokens' in bucket:
                hour_elapsed = now - bucket['hour_last_refill']
                if hour_elapsed >= 3600:
                    hour_remaining = limit_per_hour
                else:
                    refill_rate = limit_per_hour / 3600
                    tokens_to_add = hour_elapsed * refill_rate
                    current_tokens = min(
                        limit_per_hour,
                        bucket['hour_tokens'] + tokens_to_add
                    )
                    hour_remaining = int(current_tokens)
            
            day_remaining = limit_per_day
            if limit_per_day is not None and 'day_tokens' in bucket:
                day_elapsed = now - bucket['day_last_refill']
                if day_elapsed >= 86400:
                    day_remaining = limit_per_day
                else:
                    refill_rate = limit_per_day / 86400
                    tokens_to_add = day_elapsed * refill_rate
                    current_tokens = min(
                        limit_per_day,
                        bucket['day_tokens'] + tokens_to_add
                    )
                    day_remaining = int(current_tokens)
            
            return {
                'hour_remaining': hour_remaining,
                'day_remaining': day_remaining,
                'hour_limit': limit_per_hour,
                'day_limit': limit_per_day,
            }
    
    async def reset_limits(self, key: str) -> None:
        """Reset rate limits for a key.
        
        Args:
            key: Unique identifier to reset
        """
        async with self._lock:
            if key in self._buckets:
                del self._buckets[key]
    
    async def cleanup_old_buckets(self, max_age: int = 86400) -> None:
        """Clean up old unused buckets.
        
        Args:
            max_age: Maximum age in seconds before cleanup (default 1 day)
        """
        async with self._lock:
            now = time.time()
            keys_to_remove = []
            
            for key, bucket in self._buckets.items():
                # Remove buckets that haven't been accessed recently
                last_access = max(
                    bucket.get('hour_last_refill', 0),
                    bucket.get('day_last_refill', 0)
                )
                if now - last_access > max_age:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._buckets[key]
            
            if keys_to_remove:
                logger.info(f"Cleaned up {len(keys_to_remove)} old rate limit buckets")


# Global rate limiter instance
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter