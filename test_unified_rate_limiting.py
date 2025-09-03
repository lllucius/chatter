#!/usr/bin/env python3
"""Test script for unified rate limiting system."""

import asyncio
import time
from typing import Any

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up environment for testing
os.environ.setdefault("CHATTER_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")


async def test_unified_rate_limiter():
    """Test the unified rate limiter functionality."""
    print("Testing unified rate limiter...")
    
    try:
        from chatter.utils.unified_rate_limiter import (
            UnifiedRateLimiter,
            RateLimitExceeded,
        )
        
        # Create rate limiter without cache for testing
        limiter = UnifiedRateLimiter(cache_service=None)
        
        # Test basic rate limiting
        key = "test_user_123"
        limit = 3
        window = 60
        
        print(f"Testing {limit} requests per {window} seconds...")
        
        # First 3 requests should succeed
        for i in range(limit):
            try:
                result = await limiter.check_rate_limit(
                    key=key, limit=limit, window=window
                )
                print(f"✓ Request {i+1}: {result['remaining']} remaining")
            except RateLimitExceeded as e:
                print(f"✗ Request {i+1} failed unexpectedly: {e}")
                return False
        
        # 4th request should fail
        try:
            await limiter.check_rate_limit(
                key=key, limit=limit, window=window
            )
            print("✗ Rate limit should have been enforced")
            return False
        except RateLimitExceeded as e:
            print(f"✓ Rate limit correctly enforced: {e.message}")
        
        # Test status checking without consuming
        status = await limiter.get_status(key=key, limit=limit, window=window)
        print(f"✓ Status check: {status}")
        
        # Test different identifier (should allow requests)
        try:
            result = await limiter.check_rate_limit(
                key=key, limit=limit, window=window, identifier="different"
            )
            print(f"✓ Different identifier allowed: {result['remaining']} remaining")
        except RateLimitExceeded as e:
            print(f"✗ Different identifier should be allowed: {e}")
            return False
        
        # Test reset
        await limiter.reset(key=key)
        try:
            result = await limiter.check_rate_limit(
                key=key, limit=limit, window=window
            )
            print(f"✓ Reset successful: {result['remaining']} remaining")
        except RateLimitExceeded as e:
            print(f"✗ Reset should have allowed request: {e}")
            return False
        
        print("✓ Unified rate limiter tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Unified rate limiter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_compatibility_layer():
    """Test compatibility with existing rate limiter interface."""
    print("\nTesting compatibility layer...")
    
    try:
        from chatter.utils.rate_limiter import get_rate_limiter, RateLimitExceeded
        
        limiter = get_rate_limiter()
        
        # Test hourly and daily limits
        key = "tool:test_tool:user:123"
        hourly_limit = 2
        daily_limit = 5
        
        print(f"Testing tool rate limits: {hourly_limit}/hour, {daily_limit}/day")
        
        # First 2 requests should succeed
        for i in range(hourly_limit):
            try:
                result = await limiter.check_rate_limit(
                    key=key, 
                    limit_per_hour=hourly_limit,
                    limit_per_day=daily_limit
                )
                print(f"✓ Request {i+1}: hour={result['hour_remaining']}, day={result['day_remaining']}")
            except RateLimitExceeded as e:
                print(f"✗ Request {i+1} failed unexpectedly: {e}")
                return False
        
        # 3rd request should fail due to hourly limit
        try:
            await limiter.check_rate_limit(
                key=key,
                limit_per_hour=hourly_limit,
                limit_per_day=daily_limit
            )
            print("✗ Hourly rate limit should have been enforced")
            return False
        except RateLimitExceeded as e:
            print(f"✓ Hourly rate limit correctly enforced: {e}")
        
        # Test quota checking
        quota = await limiter.get_remaining_quota(
            key=key,
            limit_per_hour=hourly_limit,
            limit_per_day=daily_limit
        )
        print(f"✓ Quota check: {quota}")
        
        print("✓ Compatibility layer tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Compatibility layer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_decorator():
    """Test the rate limiting decorator."""
    print("\nTesting rate limiting decorator...")
    
    try:
        from chatter.utils.unified_rate_limiter import rate_limit
        
        # Mock user class
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
        
        @rate_limit(max_requests=2, window_seconds=60)
        async def test_endpoint(current_user=None):
            return {"status": "ok", "user": getattr(current_user, 'id', 'unknown')}
        
        user = MockUser("test_user_456")
        
        # First 2 requests should succeed
        for i in range(2):
            try:
                result = await test_endpoint(current_user=user)
                print(f"✓ Decorated request {i+1}: {result}")
            except Exception as e:
                print(f"✗ Decorated request {i+1} failed: {e}")
                return False
        
        # 3rd request should fail
        try:
            await test_endpoint(current_user=user)
            print("✗ Decorator rate limit should have been enforced")
            return False
        except Exception as e:
            if "Rate limit exceeded" in str(e):
                print(f"✓ Decorator rate limit correctly enforced")
            else:
                print(f"✗ Unexpected error: {e}")
                return False
        
        print("✓ Decorator tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Decorator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("Running unified rate limiting validation tests...\n")
    
    tests = [
        test_unified_rate_limiter,
        test_compatibility_layer,
        test_decorator,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print(f"\n{'='*50}")
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("✓ All unified rate limiting tests passed!")
        return True
    else:
        print("✗ Some tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)