"""Comprehensive tests for A/B testing improvements."""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime, UTC

# Mock the dependencies to avoid config issues
import sys
from unittest.mock import MagicMock

# Mock chatter modules
sys.modules['chatter.utils.logging'] = MagicMock()
sys.modules['chatter.utils.logging'].get_logger = lambda x: Mock()

# Now we can import the actual classes
from chatter.services.ab_testing import (
    ABTestManager, TestStatus, TestType, VariantAllocation, MetricType
)


class TestABTestManagerFixes:
    """Test the core A/B testing manager fixes."""

    @pytest.fixture
    def manager(self):
        """Create a fresh ABTestManager instance."""
        return ABTestManager()

    @pytest.mark.asyncio
    async def test_metric_calculation_with_empty_events(self, manager):
        """Test that metric calculation handles empty events correctly."""
        # Create a test
        test_id = await manager.create_test(
            name="Empty Events Test",
            description="Test metric calculation with no events",
            test_type=TestType.PROMPT,
            variants=[
                {
                    "name": "Control",
                    "description": "Control variant",
                    "weight": 1.0,
                    "configuration": {},
                },
                {
                    "name": "Variant",
                    "description": "Test variant",
                    "weight": 1.0,
                    "configuration": {},
                }
            ],
            primary_metric={
                "name": "user_satisfaction",
                "metric_type": MetricType.USER_SATISFACTION,
                "direction": "increase",
                "improvement_threshold": 0.1,
            },
            created_by="test_user",
        )

        # Start the test
        await manager.start_test(test_id)

        # Analyze without any events (should not crash)
        results = await manager.analyze_test(test_id)
        
        assert results is not None
        assert results.test_id == test_id
        assert len(results.variant_results) == 2  # Should have entries for both variants
        
        # Each variant should have zero events but still have structure
        for variant_data in results.variant_results.values():
            assert variant_data["total_events"] == 0
            assert variant_data["unique_users"] == 0
            assert variant_data["metrics"] == {}

    @pytest.mark.asyncio
    async def test_traffic_percentage_precision(self, manager):
        """Test that traffic percentage allocation is precise."""
        test_id = await manager.create_test(
            name="Traffic Test",
            description="Test traffic percentage precision",
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
            traffic_percentage=0.25,  # 25% traffic
        )

        await manager.start_test(test_id)

        assigned_count = 0
        for i in range(1000):
            variant_id = await manager.assign_variant(test_id, f"user_{i}")
            if variant_id:
                assigned_count += 1

        # Should be approximately 250 users (25% of 1000), allow some variance
        assert 200 <= assigned_count <= 300, f"Expected ~250 users, got {assigned_count}"

    @pytest.mark.asyncio
    async def test_weighted_allocation_edge_cases(self, manager):
        """Test weighted allocation handles edge cases correctly."""
        # Test with zero weights
        test_id = await manager.create_test(
            name="Zero Weights Test",
            description="Test weighted allocation with zero weights",
            test_type=TestType.MODEL,
            variants=[
                {"name": "V1", "description": "Zero weight 1", "weight": 0.0, "configuration": {}},
                {"name": "V2", "description": "Zero weight 2", "weight": 0.0, "configuration": {}},
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

        # Should still assign users (fallback to equal distribution)
        variant_id = await manager.assign_variant(test_id, "test_user")
        assert variant_id is not None

    @pytest.mark.asyncio
    async def test_assignment_lookup_optimization(self, manager):
        """Test that assignment lookup is optimized."""
        test_id = await manager.create_test(
            name="Lookup Test",
            description="Test assignment lookup optimization",
            test_type=TestType.PROMPT,
            variants=[
                {"name": "Control", "description": "Control", "weight": 1.0, "configuration": {}},
                {"name": "Test", "description": "Test", "weight": 1.0, "configuration": {}},
            ],
            primary_metric={
                "name": "satisfaction",
                "metric_type": MetricType.USER_SATISFACTION,
                "direction": "increase",
                "improvement_threshold": 0.05,
            },
            created_by="test_user",
        )

        await manager.start_test(test_id)

        # Assign a user
        user_id = "test_user"
        variant_id1 = await manager.assign_variant(test_id, user_id)
        assert variant_id1 is not None

        # Check that user_assignments index is populated
        assert user_id in manager.user_assignments
        assert test_id in manager.user_assignments[user_id]

        # Second assignment should return same variant (lookup should be fast)
        variant_id2 = await manager.assign_variant(test_id, user_id)
        assert variant_id1 == variant_id2

    @pytest.mark.asyncio
    async def test_statistical_significance_calculation(self, manager):
        """Test that statistical significance is calculated properly."""
        test_id = await manager.create_test(
            name="Stats Test",
            description="Test statistical significance calculation",
            test_type=TestType.PROMPT,
            variants=[
                {"name": "Control", "description": "Control", "weight": 1.0, "configuration": {}, "is_control": True},
                {"name": "Test", "description": "Test", "weight": 1.0, "configuration": {}},
            ],
            primary_metric={
                "name": "user_satisfaction",
                "metric_type": MetricType.USER_SATISFACTION,
                "direction": "increase",
                "improvement_threshold": 0.1,
            },
            created_by="test_user",
            minimum_sample_size=10,
        )

        await manager.start_test(test_id)

        # Assign users and record events with different satisfaction levels
        control_variant = None
        test_variant = None
        
        for i in range(20):
            user_id = f"user_{i}"
            variant_id = await manager.assign_variant(test_id, user_id)
            
            if variant_id:
                # Determine variant type
                test_obj = await manager.get_test(test_id)
                for variant in test_obj.variants:
                    if variant.id == variant_id:
                        if variant.is_control:
                            control_variant = variant_id
                            satisfaction = 3.0  # Lower satisfaction for control
                        else:
                            test_variant = variant_id
                            satisfaction = 4.5  # Higher satisfaction for test
                        break
                
                # Record event
                await manager.record_event(
                    test_id=test_id,
                    user_id=user_id,
                    event_type="satisfaction_rating",
                    metrics={"user_satisfaction": satisfaction}
                )

        # Analyze results
        results = await manager.analyze_test(test_id)
        assert results is not None

        # Should have statistical significance data
        assert len(results.statistical_significance) > 0
        assert len(results.confidence_intervals) > 0

        # Both variants should have confidence intervals
        for variant_id in [control_variant, test_variant]:
            if variant_id and variant_id in results.confidence_intervals:
                ci = results.confidence_intervals[variant_id]
                assert "user_satisfaction" in ci
                assert "lower" in ci["user_satisfaction"]
                assert "upper" in ci["user_satisfaction"]

    @pytest.mark.asyncio
    async def test_test_validation(self, manager):
        """Test that test validation catches configuration errors."""
        
        # Test with no variants
        with pytest.raises(ValueError, match="at least one variant"):
            await manager.create_test(
                name="Invalid Test",
                description="No variants",
                test_type=TestType.PROMPT,
                variants=[],
                primary_metric={
                    "name": "test",
                    "metric_type": MetricType.CUSTOM,
                    "direction": "increase",
                    "improvement_threshold": 0.05,
                },
                created_by="test_user",
            )

        # Test with invalid traffic percentage
        with pytest.raises(ValueError, match="Traffic percentage"):
            await manager.create_test(
                name="Invalid Traffic",
                description="Invalid traffic percentage",
                test_type=TestType.PROMPT,
                variants=[
                    {"name": "V1", "description": "V1", "weight": 1.0, "configuration": {}},
                    {"name": "V2", "description": "V2", "weight": 1.0, "configuration": {}},
                ],
                primary_metric={
                    "name": "test",
                    "metric_type": MetricType.CUSTOM,
                    "direction": "increase",
                    "improvement_threshold": 0.05,
                },
                created_by="test_user",
                traffic_percentage=1.5,  # Invalid
            )

        # Test with insufficient sample size
        with pytest.raises(ValueError, match="Minimum sample size"):
            await manager.create_test(
                name="Invalid Sample Size",
                description="Invalid sample size",
                test_type=TestType.PROMPT,
                variants=[
                    {"name": "V1", "description": "V1", "weight": 1.0, "configuration": {}},
                    {"name": "V2", "description": "V2", "weight": 1.0, "configuration": {}},
                ],
                primary_metric={
                    "name": "test",
                    "metric_type": MetricType.CUSTOM,
                    "direction": "increase",
                    "improvement_threshold": 0.05,
                },
                created_by="test_user",
                minimum_sample_size=5,  # Too small
            )

    @pytest.mark.asyncio
    async def test_cleanup_on_delete(self, manager):
        """Test that delete properly cleans up all related data."""
        test_id = await manager.create_test(
            name="Cleanup Test",
            description="Test cleanup on delete",
            test_type=TestType.PROMPT,
            variants=[
                {"name": "Control", "description": "Control", "weight": 1.0, "configuration": {}},
                {"name": "Test", "description": "Test", "weight": 1.0, "configuration": {}},
            ],
            primary_metric={
                "name": "satisfaction",
                "metric_type": MetricType.USER_SATISFACTION,
                "direction": "increase",
                "improvement_threshold": 0.05,
            },
            created_by="test_user",
        )

        await manager.start_test(test_id)

        # Create some assignments and events
        user_ids = []
        for i in range(5):
            user_id = f"cleanup_user_{i}"
            user_ids.append(user_id)
            variant_id = await manager.assign_variant(test_id, user_id)
            if variant_id:
                await manager.record_event(
                    test_id=test_id,
                    user_id=user_id,
                    event_type="test_event",
                    metrics={"satisfaction": 4.0}
                )

        # Verify data exists before deletion
        assert test_id in manager.tests
        assignment_count_before = len([a for a in manager.assignments.values() if a.test_id == test_id])
        event_count_before = len([e for e in manager.events if e.test_id == test_id])
        user_assignment_entries_before = sum(
            1 for user_tests in manager.user_assignments.values() 
            if test_id in user_tests
        )

        assert assignment_count_before > 0
        assert event_count_before > 0
        assert user_assignment_entries_before > 0

        # Delete the test
        success = await manager.delete_test(test_id)
        assert success

        # Verify all data is cleaned up
        assert test_id not in manager.tests
        assert test_id not in manager.results

        assignment_count_after = len([a for a in manager.assignments.values() if a.test_id == test_id])
        event_count_after = len([e for e in manager.events if e.test_id == test_id])
        user_assignment_entries_after = sum(
            1 for user_tests in manager.user_assignments.values() 
            if test_id in user_tests
        )

        assert assignment_count_after == 0
        assert event_count_after == 0
        assert user_assignment_entries_after == 0

    @pytest.mark.asyncio
    async def test_secondary_metrics_calculation(self, manager):
        """Test that secondary metrics are calculated correctly."""
        test_id = await manager.create_test(
            name="Secondary Metrics Test",
            description="Test secondary metrics calculation",
            test_type=TestType.PROMPT,
            variants=[
                {"name": "Control", "description": "Control", "weight": 1.0, "configuration": {}},
                {"name": "Test", "description": "Test", "weight": 1.0, "configuration": {}},
            ],
            primary_metric={
                "name": "user_satisfaction",
                "metric_type": MetricType.USER_SATISFACTION,
                "direction": "increase",
                "improvement_threshold": 0.1,
            },
            secondary_metrics=[
                {
                    "name": "response_time",
                    "metric_type": MetricType.RESPONSE_TIME,
                    "direction": "decrease",
                    "improvement_threshold": 0.05,
                },
                {
                    "name": "token_usage",
                    "metric_type": MetricType.TOKEN_USAGE,
                    "direction": "decrease",
                    "improvement_threshold": 0.1,
                }
            ],
            created_by="test_user",
        )

        await manager.start_test(test_id)

        # Record events with multiple metrics
        for i in range(10):
            user_id = f"multi_metric_user_{i}"
            variant_id = await manager.assign_variant(test_id, user_id)
            if variant_id:
                await manager.record_event(
                    test_id=test_id,
                    user_id=user_id,
                    event_type="multi_metric_event",
                    metrics={
                        "user_satisfaction": 4.0 + (i % 3) * 0.5,
                        "response_time": 1.0 + (i % 2) * 0.3,
                        "token_usage": 100 + (i % 4) * 10,
                    }
                )

        # Analyze results
        results = await manager.analyze_test(test_id)
        assert results is not None

        # Check that all metrics are calculated for variants with data
        for variant_data in results.variant_results.values():
            metrics = variant_data["metrics"]
            if variant_data["total_events"] > 0:
                # Should have all three metrics
                assert "user_satisfaction" in metrics
                assert "response_time" in metrics
                assert "token_usage" in metrics
                
                # Each metric should have mean, count, sum, std
                for metric_name in ["user_satisfaction", "response_time", "token_usage"]:
                    metric_data = metrics[metric_name]
                    assert "mean" in metric_data
                    assert "count" in metric_data
                    assert "sum" in metric_data
                    assert "std" in metric_data
                    assert metric_data["count"] > 0