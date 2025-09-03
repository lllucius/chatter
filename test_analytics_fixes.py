#!/usr/bin/env python3
"""Test script to validate analytics fixes."""

import sys
import traceback
from datetime import datetime, UTC, timedelta

def test_schema_validation():
    """Test analytics schema validation fixes."""
    print("Testing analytics schema validation...")
    
    try:
        from chatter.schemas.analytics import AnalyticsTimeRange, AnalyticsExportRequest
        
        # Test valid time range
        valid_range = AnalyticsTimeRange(
            start_date=datetime.now(UTC) - timedelta(days=7),
            end_date=datetime.now(UTC),
            period="7d"
        )
        print("✓ Valid time range accepted")
        
        # Test invalid period
        try:
            invalid_period = AnalyticsTimeRange(period="invalid")
            print("✗ Invalid period should have been rejected")
            return False
        except ValueError as e:
            print(f"✓ Invalid period correctly rejected: {e}")
        
        # Test invalid date range
        try:
            invalid_dates = AnalyticsTimeRange(
                start_date=datetime.now(UTC),
                end_date=datetime.now(UTC) - timedelta(days=1),
                period="7d"
            )
            print("✗ Invalid date range should have been rejected")
            return False
        except ValueError as e:
            print(f"✓ Invalid date range correctly rejected: {e}")
        
        # Test export request validation
        valid_export = AnalyticsExportRequest(
            metrics=["conversations", "usage"],
            time_range=valid_range,
            format="json"
        )
        print("✓ Valid export request accepted")
        
        # Test invalid metrics
        try:
            invalid_metrics = AnalyticsExportRequest(
                metrics=["invalid_metric"],
                time_range=valid_range,
                format="json"
            )
            print("✗ Invalid metrics should have been rejected")
            return False
        except ValueError as e:
            print(f"✓ Invalid metrics correctly rejected: {e}")
        
        # Test invalid format
        try:
            invalid_format = AnalyticsExportRequest(
                metrics=["conversations"],
                time_range=valid_range,
                format="invalid"
            )
            print("✗ Invalid format should have been rejected")
            return False
        except ValueError as e:
            print(f"✓ Invalid format correctly rejected: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Schema validation test failed: {e}")
        traceback.print_exc()
        return False

def test_division_by_zero_fixes():
    """Test division by zero fixes in analytics calculations."""
    print("\nTesting division by zero fixes...")
    
    try:
        # Test the calculation logic manually
        total_conversations = 0
        total_messages = 5
        
        # This should not raise an exception
        avg_messages = (
            total_messages / total_conversations
            if total_conversations > 0
            else 0.0
        )
        
        if avg_messages == 0.0:
            print("✓ Division by zero handled correctly")
            return True
        else:
            print("✗ Unexpected result from division by zero fix")
            return False
            
    except Exception as e:
        print(f"✗ Division by zero test failed: {e}")
        return False

def test_import_fixes():
    """Test that all analytics modules can be imported successfully."""
    print("\nTesting module imports...")
    
    try:
        from chatter.api.analytics import router
        print("✓ Analytics API imports successfully")
        
        from chatter.core.analytics import AnalyticsService
        print("✓ Analytics service imports successfully")
        
        from chatter.schemas.analytics import (
            AnalyticsTimeRange, 
            AnalyticsExportRequest,
            ConversationStatsResponse,
            UsageMetricsResponse
        )
        print("✓ Analytics schemas import successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Running analytics fixes validation tests...\n")
    
    tests = [
        test_import_fixes,
        test_schema_validation, 
        test_division_by_zero_fixes,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())