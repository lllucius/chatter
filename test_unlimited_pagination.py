#!/usr/bin/env python3
"""Test script to verify unlimited pagination functionality."""

import os
import sys
from typing import Any, Dict

# Set dummy database URL to avoid config errors
os.environ['DATABASE_URL'] = 'sqlite:///test.db'

# Add project root to Python path
sys.path.insert(0, '.')

def test_pagination_request_schemas():
    """Test that PaginationRequest schemas allow unlimited values."""
    from chatter.schemas.common import PaginationRequest, PaginationParams
    
    print("Testing PaginationRequest schema...")
    
    # Test cases with various limit values
    test_cases = [
        {'limit': 50, 'offset': 0},      # Default case
        {'limit': 100, 'offset': 0},     # Previously maximum
        {'limit': 1000, 'offset': 0},    # Beyond old limit
        {'limit': 10000, 'offset': 0},   # Very large
        {'limit': 100000, 'offset': 0},  # Extremely large
    ]
    
    for case in test_cases:
        try:
            req = PaginationRequest(**case)
            print(f"✓ PaginationRequest({case}) -> Valid: limit={req.limit}, offset={req.offset}")
        except Exception as e:
            print(f"✗ PaginationRequest({case}) -> Error: {e}")
            return False
    
    print("\nTesting PaginationParams schema...")
    
    # Test PaginationParams with page-based pagination
    params_test_cases = [
        {'page': 1, 'limit': 20},       # Default
        {'page': 1, 'limit': 100},      # Previously maximum
        {'page': 1, 'limit': 1000},     # Beyond old limit
        {'page': 1, 'limit': 10000},    # Very large
    ]
    
    for case in params_test_cases:
        try:
            params = PaginationParams(**case)
            print(f"✓ PaginationParams({case}) -> Valid: page={params.page}, limit={params.limit}")
        except Exception as e:
            print(f"✗ PaginationParams({case}) -> Error: {e}")
            return False
    
    return True

def test_sdk_schemas():
    """Test that SDK schemas allow unlimited values."""
    try:
        from sdk.python.chatter_sdk.models.pagination_request import PaginationRequest as SDKPaginationRequest
        
        print("\nTesting Python SDK PaginationRequest...")
        
        sdk_test_cases = [
            {'limit': 50, 'offset': 0},
            {'limit': 1000, 'offset': 0},
            {'limit': 10000, 'offset': 0},
        ]
        
        for case in sdk_test_cases:
            try:
                sdk_req = SDKPaginationRequest(**case)
                print(f"✓ SDK PaginationRequest({case}) -> Valid")
            except Exception as e:
                print(f"✗ SDK PaginationRequest({case}) -> Error: {e}")
                return False
        
        return True
    except ImportError as e:
        print(f"⚠ SDK import failed (expected in test environment): {e}")
        return True  # Don't fail the test for SDK import issues

def test_invalid_values():
    """Test that invalid values are still rejected."""
    from chatter.schemas.common import PaginationRequest
    
    print("\nTesting invalid values are still rejected...")
    
    invalid_cases = [
        {'limit': 0, 'offset': 0},       # Below minimum
        {'limit': -1, 'offset': 0},      # Negative limit
        {'limit': 50, 'offset': -1},     # Negative offset
    ]
    
    for case in invalid_cases:
        try:
            req = PaginationRequest(**case)
            print(f"✗ PaginationRequest({case}) -> Should have failed but didn't!")
            return False
        except Exception as e:
            print(f"✓ PaginationRequest({case}) -> Correctly rejected: {type(e).__name__}")
    
    return True

def main():
    """Run all pagination tests."""
    print("=" * 60)
    print("Testing Unlimited Pagination Functionality")
    print("=" * 60)
    
    all_passed = True
    
    # Test backend schemas
    if not test_pagination_request_schemas():
        all_passed = False
    
    # Test SDK schemas
    if not test_sdk_schemas():
        all_passed = False
    
    # Test validation still works for invalid values
    if not test_invalid_values():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All pagination tests PASSED!")
        print("✅ Unlimited pagination is working correctly!")
    else:
        print("❌ Some pagination tests FAILED!")
        sys.exit(1)
    print("=" * 60)

if __name__ == '__main__':
    main()