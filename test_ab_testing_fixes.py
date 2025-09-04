#!/usr/bin/env python3
"""Test script to verify A/B testing fixes."""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from chatter.services.ab_testing import ABTestManager, MetricType, TestType, VariantAllocation


async def test_basic_functionality():
    """Test basic A/B testing functionality."""
    print("Testing basic A/B testing functionality...")
    
    manager = ABTestManager()
    
    # Test 1: Create a basic test
    try:
        test_id = await manager.create_test(
            name="Test Basic Functionality",
            description="A test to verify basic functionality",
            test_type=TestType.PROMPT,
            variants=[
                {
                    "name": "Control",
                    "description": "Control variant",
                    "weight": 1.0,
                    "configuration": {"prompt": "Hello"},
                    "is_control": True,
                },
                {
                    "name": "Variant A",
                    "description": "Test variant",
                    "weight": 1.0,
                    "configuration": {"prompt": "Hi there"},
                    "is_control": False,
                }
            ],
            primary_metric={
                "name": "user_satisfaction",
                "metric_type": MetricType.USER_SATISFACTION,
                "direction": "increase",
                "improvement_threshold": 0.1,
            },
            created_by="test_user",
            traffic_percentage=1.0,
        )
        print(f"✓ Created test: {test_id}")
    except Exception as e:
        print(f"✗ Failed to create test: {e}")
        return False
    
    # Test 2: Start the test
    try:
        success = await manager.start_test(test_id)
        if success:
            print("✓ Started test successfully")
        else:
            print("✗ Failed to start test")
            return False
    except Exception as e:
        print(f"✗ Error starting test: {e}")
        return False
    
    # Test 3: Assign users to variants
    try:
        for i in range(10):
            variant_id = await manager.assign_variant(test_id, f"user_{i}")
            if variant_id:
                print(f"✓ Assigned user_{i} to variant {variant_id}")
            else:
                print(f"✗ Failed to assign user_{i}")
    except Exception as e:
        print(f"✗ Error assigning users: {e}")
        return False
    
    # Test 4: Record events with metrics
    try:
        for i in range(10):
            event_id = await manager.record_event(
                test_id=test_id,
                user_id=f"user_{i}",
                event_type="satisfaction_rating",
                metrics={"user_satisfaction": 4.0 + (i % 3) * 0.5}  # Vary between 4.0-5.0
            )
            if event_id:
                print(f"✓ Recorded event for user_{i}")
            else:
                print(f"? No event recorded for user_{i} (may not be assigned)")
    except Exception as e:
        print(f"✗ Error recording events: {e}")
        return False
    
    # Test 5: Analyze results
    try:
        results = await manager.analyze_test(test_id)
        if results:
            print("✓ Generated test results")
            print(f"  Variants analyzed: {len(results.variant_results)}")
            print(f"  Statistical significance: {results.statistical_significance}")
            print(f"  Recommendations: {len(results.recommendations)}")
        else:
            print("✗ No results generated")
            return False
    except Exception as e:
        print(f"✗ Error analyzing results: {e}")
        return False
    
    # Test 6: Test traffic percentage functionality
    try:
        test_id_traffic = await manager.create_test(
            name="Test Traffic Percentage",
            description="Test with 50% traffic",
            test_type=TestType.PROMPT,
            variants=[
                {"name": "Control", "description": "Control", "weight": 1.0, "configuration": {}},
                {"name": "Test", "description": "Test", "weight": 1.0, "configuration": {}},
            ],
            primary_metric={
                "name": "conversion",
                "metric_type": MetricType.CONVERSION,
                "direction": "increase",
                "improvement_threshold": 0.05,
            },
            created_by="test_user",
            traffic_percentage=0.5,  # 50% traffic
        )
        
        await manager.start_test(test_id_traffic)
        
        assigned_count = 0
        for i in range(100):
            variant_id = await manager.assign_variant(test_id_traffic, f"traffic_user_{i}")
            if variant_id:
                assigned_count += 1
        
        # Should be approximately 50 users assigned (with some variance due to hashing)
        if 35 <= assigned_count <= 65:
            print(f"✓ Traffic percentage working correctly: {assigned_count}/100 users assigned")
        else:
            print(f"✗ Traffic percentage issue: {assigned_count}/100 users assigned (expected ~50)")
            
    except Exception as e:
        print(f"✗ Error testing traffic percentage: {e}")
        return False
    
    print("\n✓ All basic functionality tests passed!")
    return True


async def test_weighted_allocation():
    """Test weighted allocation strategy."""
    print("\nTesting weighted allocation...")
    
    manager = ABTestManager()
    
    try:
        test_id = await manager.create_test(
            name="Weighted Allocation Test",
            description="Test weighted allocation",
            test_type=TestType.MODEL,
            variants=[
                {"name": "Low Weight", "description": "Low weight variant", "weight": 0.2, "configuration": {}},
                {"name": "High Weight", "description": "High weight variant", "weight": 0.8, "configuration": {}},
            ],
            primary_metric={
                "name": "accuracy",
                "metric_type": MetricType.ACCURACY,
                "direction": "increase",
                "improvement_threshold": 0.05,
            },
            created_by="test_user",
            allocation_strategy=VariantAllocation.WEIGHTED,
        )
        
        await manager.start_test(test_id)
        
        variant_counts = {}
        for i in range(100):
            variant_id = await manager.assign_variant(test_id, f"weighted_user_{i}")
            if variant_id:
                # Get variant name for counting
                test = await manager.get_test(test_id)
                for variant in test.variants:
                    if variant.id == variant_id:
                        variant_name = variant.name
                        variant_counts[variant_name] = variant_counts.get(variant_name, 0) + 1
                        break
        
        print(f"  Allocation results: {variant_counts}")
        
        # High weight variant should have more assignments (approximately 80%)
        high_weight_count = variant_counts.get("High Weight", 0)
        if high_weight_count > 60:  # Allow some variance
            print("✓ Weighted allocation working correctly")
            return True
        else:
            print(f"✗ Weighted allocation issue: High weight variant got {high_weight_count}/100 (expected ~80)")
            return False
            
    except Exception as e:
        print(f"✗ Error testing weighted allocation: {e}")
        return False


async def test_validation():
    """Test validation functionality."""
    print("\nTesting validation...")
    
    manager = ABTestManager()
    
    # Test 1: Invalid configuration (no variants)
    try:
        await manager.create_test(
            name="Invalid Test",
            description="Should fail validation",
            test_type=TestType.PROMPT,
            variants=[],  # No variants
            primary_metric={
                "name": "test",
                "metric_type": MetricType.CUSTOM,
                "direction": "increase",
                "improvement_threshold": 0.05,
            },
            created_by="test_user",
        )
        print("✗ Validation failed - should have rejected empty variants")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected invalid config: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # Test 2: Invalid traffic percentage
    try:
        await manager.create_test(
            name="Invalid Traffic Test",
            description="Should fail validation",
            test_type=TestType.PROMPT,
            variants=[
                {"name": "V1", "description": "Variant 1", "weight": 1.0, "configuration": {}},
                {"name": "V2", "description": "Variant 2", "weight": 1.0, "configuration": {}},
            ],
            primary_metric={
                "name": "test",
                "metric_type": MetricType.CUSTOM,
                "direction": "increase",
                "improvement_threshold": 0.05,
            },
            created_by="test_user",
            traffic_percentage=1.5,  # Invalid > 1.0
        )
        print("✗ Validation failed - should have rejected traffic > 1.0")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected invalid traffic percentage: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    print("✓ Validation tests passed!")
    return True


async def main():
    """Run all tests."""
    print("Starting A/B Testing Fixes Verification\n")
    
    success = True
    
    # Run test suites
    success &= await test_basic_functionality()
    success &= await test_weighted_allocation()
    success &= await test_validation()
    
    if success:
        print("\n🎉 All tests passed! A/B testing fixes are working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)