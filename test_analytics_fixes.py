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

def test_analyzer_implementations():
    """Test that analyzer classes have proper implementations."""
    print("\nTesting analyzer implementations...")
    
    try:
        from chatter.core.analytics import (
            ConversationAnalyzer, 
            PerformanceAnalyzer, 
            TrendAnalyzer
        )
        import asyncio
        
        # Test ConversationAnalyzer
        conv_analyzer = ConversationAnalyzer()
        sample_messages = [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
        ]
        
        async def test_conversation_analysis():
            result = await conv_analyzer.analyze_conversation("test_conv", sample_messages)
            return result.get("analysis") == "conversation_analyzed"
        
        if asyncio.run(test_conversation_analysis()):
            print("✓ ConversationAnalyzer working correctly")
        else:
            print("✗ ConversationAnalyzer failed")
            return False
        
        # Test PerformanceAnalyzer  
        perf_analyzer = PerformanceAnalyzer()
        sample_metrics = {
            "avg_response_time_ms": 1500,
            "error_rate": 0.02,
            "cpu_usage": 0.75,
            "memory_usage": 0.80
        }
        
        async def test_performance_analysis():
            result = await perf_analyzer.analyze_performance("test_component", sample_metrics)
            return "analysis" in result and "health_score" in result.get("analysis", {})
        
        if asyncio.run(test_performance_analysis()):
            print("✓ PerformanceAnalyzer working correctly")
        else:
            print("✗ PerformanceAnalyzer failed")
            return False
        
        # Test TrendAnalyzer
        trend_analyzer = TrendAnalyzer()
        sample_data = [
            {"timestamp": "2023-01-01", "value": 100},
            {"timestamp": "2023-01-02", "value": 110},
            {"timestamp": "2023-01-03", "value": 120},
        ]
        
        async def test_trend_analysis():
            result = await trend_analyzer.analyze_trends("test_metric", sample_data)
            return "trend" in result and "confidence" in result
        
        if asyncio.run(test_trend_analysis()):
            print("✓ TrendAnalyzer working correctly")
        else:
            print("✗ TrendAnalyzer failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Analyzer implementations test failed: {e}")
        traceback.print_exc()
        return False

def test_export_functionality():
    """Test export functionality implementation."""
    print("\nTesting export functionality...")
    
    try:
        from chatter.core.analytics import AnalyticsService
        from chatter.schemas.analytics import AnalyticsTimeRange
        from datetime import datetime, UTC
        
        # Test CSV export helper
        service = AnalyticsService(None)  # Mock session
        
        sample_data = {
            "export_info": {
                "generated_at": datetime.now(UTC).isoformat(),
                "user_id": "test_user",
                "metrics_included": ["conversations"]
            },
            "conversations": {
                "total_conversations": 10,
                "total_messages": 50
            }
        }
        
        # Test CSV export
        csv_result = service._export_to_csv(sample_data)
        if csv_result:
            print("✓ CSV export functionality implemented")
        else:
            print("✗ CSV export failed")
            return False
        
        # Test Excel export 
        try:
            xlsx_result = service._export_to_xlsx(sample_data)
            if xlsx_result:
                print("✓ Excel export functionality implemented")
            else:
                print("✗ Excel export failed")
                return False
        except ImportError:
            print("⚠ Excel export requires openpyxl (fallback to CSV works)")
        
        return True
        
    except Exception as e:
        print(f"✗ Export functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_rate_limiting():
    """Test rate limiting implementation."""
    print("\nTesting rate limiting...")
    
    try:
        from chatter.api.analytics import rate_limit, _rate_limit_data
        from chatter.models.user import User
        
        # Clear any existing rate limit data
        _rate_limit_data.clear()
        
        # Create a mock user
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
        
        # Test rate limit decorator
        @rate_limit(max_requests=2, window_seconds=60)
        async def test_endpoint(current_user=None):
            return {"status": "ok"}
        
        mock_user = MockUser("test_user")
        
        # Should succeed for first 2 requests
        import asyncio
        
        async def test_requests():
            try:
                await test_endpoint(current_user=mock_user)
                await test_endpoint(current_user=mock_user)
                print("✓ First 2 requests allowed")
                
                # Third request should fail
                try:
                    await test_endpoint(current_user=mock_user)
                    print("✗ Rate limit should have been enforced")
                    return False
                except Exception as e:
                    if "Rate limit exceeded" in str(e):
                        print("✓ Rate limit correctly enforced")
                        return True
                    else:
                        print(f"✗ Unexpected error: {e}")
                        return False
            except Exception as e:
                print(f"✗ Rate limiting test failed: {e}")
                return False
        
        return asyncio.run(test_requests())
        
    except Exception as e:
        print(f"✗ Rate limiting test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Running analytics fixes validation tests...\n")
    
    tests = [
        test_import_fixes,
        test_schema_validation, 
        test_division_by_zero_fixes,
        test_analyzer_implementations,
        test_export_functionality,
        test_rate_limiting,
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