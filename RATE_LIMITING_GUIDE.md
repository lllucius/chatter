# Unified Rate Limiting System

This document describes the new unified rate limiting system that consolidates all previous rate limiting implementations in the Chatter project.

## Overview

The unified rate limiting system replaces multiple disparate rate limiting implementations with a single, consistent system that supports:

- **Sliding window algorithm** for accurate rate limiting
- **Redis backend** with memory fallback for distributed rate limiting
- **Endpoint-specific limits** for fine-grained control
- **Multiple rate limits per key** (e.g., hourly + daily limits)
- **Backward compatibility** with existing APIs
- **Rich metadata** including remaining requests and reset times

## Architecture

### Core Components

1. **`SlidingWindowRateLimiter`**: Core rate limiting algorithm
2. **`UnifiedRateLimiter`**: Main interface supporting multiple identifiers
3. **`UnifiedRateLimitMiddleware`**: FastAPI middleware with endpoint-specific limits
4. **`rate_limit` decorator**: Drop-in replacement for existing decorators

### Integration Points

- **Cache Service**: Uses existing Redis cache with memory fallback
- **Problem Exceptions**: RFC 9457 compliant error responses
- **Configuration**: Centralized settings in `config.py`
- **Logging**: Structured logging for monitoring

## Usage

### Middleware (Global Rate Limiting)

The middleware is automatically configured in `main.py` with endpoint-specific limits:

```python
from chatter.utils.unified_rate_limiter import UnifiedRateLimitMiddleware

app.add_middleware(
    UnifiedRateLimitMiddleware,
    rate_limiter=rate_limiter,
    endpoint_limits={
        "/api/v1/auth/login": (10, 300),  # 10 requests per 5 minutes
        "/api/v1/models/": (200, 60),     # 200 requests per minute
    }
)
```

### Decorator (Endpoint-Specific Rate Limiting)

```python
from chatter.utils.unified_rate_limiter import rate_limit

@rate_limit(max_requests=20, window_seconds=60)
async def analytics_endpoint(current_user: User):
    # Endpoint implementation
    pass
```

### Direct Usage (Programmatic Rate Limiting)

```python
from chatter.utils.unified_rate_limiter import get_unified_rate_limiter

rate_limiter = get_unified_rate_limiter()

try:
    status = await rate_limiter.check_rate_limit(
        key="user:123",
        limit=100,
        window=3600,  # 1 hour
        identifier="api_calls"
    )
    print(f"Remaining: {status['remaining']}")
except RateLimitExceeded as e:
    print(f"Rate limited: {e.message}")
```

### Tool Rate Limiting (Compatibility Layer)

The existing tool rate limiting API is preserved through a compatibility layer:

```python
from chatter.utils.rate_limiter import get_rate_limiter

limiter = get_rate_limiter()

try:
    result = await limiter.check_rate_limit(
        key="tool:gpt4:user:123",
        limit_per_hour=10,
        limit_per_day=100
    )
    print(f"Hour remaining: {result['hour_remaining']}")
    print(f"Day remaining: {result['day_remaining']}")
except RateLimitExceeded as e:
    print(f"Rate limited: {e}")
```

## Configuration

All rate limiting settings are centralized in `config.py`:

```python
# Global defaults
rate_limit_requests: int = 100
rate_limit_window: int = 60

# Endpoint-specific settings
rate_limit_auth_requests: int = 10
rate_limit_auth_window: int = 300

rate_limit_analytics_requests: int = 20
rate_limit_analytics_window: int = 60

# Cache integration
rate_limit_use_cache: bool = True
```

## Rate Limiting Headers

The system adds standard rate limiting headers to all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
X-RateLimit-Window: 60
```

When rate limited, additional headers are included:

```
Retry-After: 60
```

## Error Responses

Rate limit errors use RFC 9457 Problem Details format:

```json
{
  "type": "https://api.example.com/problems/rate-limit-exceeded",
  "title": "Rate Limit Exceeded", 
  "status": 429,
  "detail": "Rate limit exceeded: 100 requests per 60 seconds",
  "instance": "/api/v1/analytics/dashboard",
  "limit": 100,
  "window": 60,
  "remaining": 0,
  "retryAfter": 60
}
```

## Migration Guide

### From Old Rate Limiting Middleware

**Before:**
```python
from chatter.utils.rate_limit import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100,
    requests_per_hour=2000,
)
```

**After:**
```python
from chatter.utils.unified_rate_limiter import UnifiedRateLimitMiddleware

# Middleware is pre-configured in main.py with endpoint-specific limits
# No changes needed for most applications
```

### From Old Analytics Decorator

**Before:**
```python
from chatter.api.analytics import rate_limit

@rate_limit(max_requests=20, window_seconds=60)
async def endpoint():
    pass
```

**After:**
```python
from chatter.utils.unified_rate_limiter import rate_limit

@rate_limit(max_requests=20, window_seconds=60)
async def endpoint():
    pass
```

### From Old Tool Rate Limiter

**Before and After:** No changes needed - compatibility layer preserves existing API.

## Deprecated Modules

The following modules are deprecated and will be removed in a future version:

- `chatter.utils.rate_limit` → Use `chatter.utils.unified_rate_limiter`
- `chatter.utils.rate_limiting` → Use `chatter.utils.unified_rate_limiter`
- Custom rate limiting in `chatter.api.analytics` → Use `chatter.utils.unified_rate_limiter.rate_limit`

## Performance Considerations

- **Redis Backend**: Provides distributed rate limiting across multiple instances
- **Memory Fallback**: Graceful degradation when Redis is unavailable
- **Sliding Window**: More accurate than fixed windows, minimal overhead
- **Cache TTL**: Automatic cleanup prevents memory leaks
- **Async/Await**: Non-blocking operations for high concurrency

## Monitoring

Rate limiting events are logged with structured data for monitoring:

```python
logger.warning(
    "Rate limit exceeded",
    key=key,
    path=path,
    limit=limit,
    window=window,
    remaining=remaining,
)
```

## Testing

Test the rate limiting system with the provided test scripts:

```bash
# Simple functionality test (no dependencies)
python test_simple_rate_limiting.py

# Full integration test (requires dependencies)
python test_unified_rate_limiting.py
```

## Future Enhancements

- **User Tiers**: Different limits based on user subscription level
- **Dynamic Limits**: Adjust limits based on system load
- **Metrics Dashboard**: Real-time rate limiting metrics
- **Geographic Limits**: Different limits by region
- **Time-based Limits**: Different limits by time of day