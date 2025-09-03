#!/usr/bin/env python3
"""Simple test for unified rate limiting system (no dependencies)."""

import asyncio
import time
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the settings and logger to avoid dependencies
class MockSettings:
    rate_limit_requests = 100
    rate_limit_window = 60

class MockLogger:
    def warning(self, msg, **kwargs):
        print(f"WARN: {msg}")
    
    def info(self, msg, **kwargs):
        print(f"INFO: {msg}")

# Patch the imports to avoid dependency issues
import sys
sys.modules['chatter.config'] = type(sys)('mock_config')
sys.modules['chatter.config'].settings = MockSettings()
sys.modules['chatter.utils.logging'] = type(sys)('mock_logging')
sys.modules['chatter.utils.logging'].get_logger = lambda x: MockLogger()


async def test_sliding_window():
    """Test the sliding window rate limiter directly."""
    print("Testing SlidingWindowRateLimiter...")
    
    # Import after mocking
    from chatter.utils.unified_rate_limiter import SlidingWindowRateLimiter
    
    limiter = SlidingWindowRateLimiter(limit=3, window_seconds=5, use_cache=False)
    
    key = "test_key"
    
    # Test successful requests
    for i in range(3):
        allowed, metadata = await limiter.is_allowed(key)
        if not allowed:
            print(f"✗ Request {i+1} should have been allowed")
            return False
        print(f"✓ Request {i+1}: remaining={metadata['remaining']}")
    
    # Test rate limit exceeded
    allowed, metadata = await limiter.is_allowed(key)
    if allowed:
        print("✗ Request 4 should have been blocked")
        return False
    print(f"✓ Request 4 correctly blocked: remaining={metadata['remaining']}")
    
    # Test status check
    status = await limiter.get_status(key)
    print(f"✓ Status: {status}")
    
    # Test reset
    await limiter.reset(key)
    allowed, metadata = await limiter.is_allowed(key)
    if not allowed:
        print("✗ Request after reset should have been allowed")
        return False
    print("✓ Reset successful")
    
    return True


async def test_unified_limiter():
    """Test the unified rate limiter."""
    print("\nTesting UnifiedRateLimiter...")
    
    from chatter.utils.unified_rate_limiter import (
        UnifiedRateLimiter,
        RateLimitExceeded
    )
    
    limiter = UnifiedRateLimiter(cache_service=None)
    
    key = "user123"
    limit = 2
    window = 10
    
    # Test successful requests
    for i in range(limit):
        try:
            result = await limiter.check_rate_limit(
                key=key, limit=limit, window=window
            )
            print(f"✓ Request {i+1}: {result}")
        except RateLimitExceeded:
            print(f"✗ Request {i+1} should have been allowed")
            return False
    
    # Test rate limit exceeded
    try:
        await limiter.check_rate_limit(key=key, limit=limit, window=window)
        print("✗ Request 3 should have been blocked")
        return False
    except RateLimitExceeded as e:
        print(f"✓ Request 3 correctly blocked: {e.message}")
    
    # Test different identifier
    try:
        result = await limiter.check_rate_limit(
            key=key, limit=limit, window=window, identifier="different"
        )
        print(f"✓ Different identifier allowed: {result}")
    except RateLimitExceeded:
        print("✗ Different identifier should have been allowed")
        return False
    
    return True


async def main():
    """Run tests."""
    print("Testing unified rate limiting system (simplified)...\n")
    
    tests = [
        test_sliding_window,
        test_unified_limiter,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print(f"\n{'='*50}")
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("✓ All tests passed!")
        return True
    else:
        print("✗ Some tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)