"""A/B testing infrastructure for prompts and models."""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class TestStatus(str, Enum):
    """A/B test status."""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestType(str, Enum):
    """Types of A/B tests."""

    PROMPT = "prompt"
    MODEL = "model"
    PARAMETER = "parameter"
    WORKFLOW = "workflow"
    TEMPLATE = "template"


class VariantAllocation(str, Enum):
    """Variant allocation strategies."""

    EQUAL = "equal"
    WEIGHTED = "weighted"
    GRADUAL_ROLLOUT = "gradual_rollout"
    USER_ATTRIBUTE = "user_attribute"


class MetricType(str, Enum):
    """Types of metrics to track."""

    RESPONSE_TIME = "response_time"
    USER_SATISFACTION = "user_satisfaction"
    ACCURACY = "accuracy"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    ERROR_RATE = "error_rate"
    TOKEN_USAGE = "token_usage"
    CUSTOM = "custom"


class TestVariant(BaseModel):
    """A/B test variant configuration."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    weight: float = 1.0
    configuration: dict[str, Any] = Field(default_factory=dict)
    is_control: bool = False
    active: bool = True


class TestMetric(BaseModel):
    """Metric configuration for A/B tests."""

    name: str
    metric_type: MetricType
    target_value: float | None = None
    improvement_threshold: float = 0.05  # 5% improvement threshold
    direction: str = "increase"  # "increase" or "decrease"
    weight: float = 1.0


class ABTest(BaseModel):
    """A/B test configuration."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    test_type: TestType
    status: TestStatus = TestStatus.DRAFT

    # Test configuration
    variants: list[TestVariant] = Field(default_factory=list)
    allocation_strategy: VariantAllocation = VariantAllocation.EQUAL
    traffic_percentage: float = (
        1.0  # Percentage of traffic to include in test
    )

    # Metrics and goals
    primary_metric: TestMetric
    secondary_metrics: list[TestMetric] = Field(default_factory=list)

    # Timeline
    start_date: datetime | None = None
    end_date: datetime | None = None
    duration_days: int | None = None

    # Targeting
    target_users: dict[str, Any] = Field(default_factory=dict)
    exclude_users: dict[str, Any] = Field(default_factory=dict)

    # Statistical settings
    confidence_level: float = 0.95
    statistical_power: float = 0.8
    minimum_sample_size: int = 100

    # Metadata
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    created_by: str
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TestAssignment(BaseModel):
    """User assignment to test variant."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str
    user_id: str
    variant_id: str
    session_id: str | None = None
    assigned_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class TestEvent(BaseModel):
    """Event recorded during A/B test."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str
    variant_id: str
    user_id: str
    session_id: str | None = None
    event_type: str
    event_data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    metrics: dict[str, float] = Field(default_factory=dict)


class TestResult(BaseModel):
    """A/B test results and analysis."""

    test_id: str
    variant_results: dict[str, dict[str, Any]] = Field(
        default_factory=dict
    )
    statistical_significance: dict[str, bool] = Field(
        default_factory=dict
    )
    confidence_intervals: dict[str, dict[str, float]] = Field(
        default_factory=dict
    )
    recommendations: list[str] = Field(default_factory=list)
    analysis_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class ABTestManager:
    """Manages A/B tests for prompts, models, and configurations."""

    def __init__(self):
        """Initialize the A/B test manager."""
        self.tests: dict[str, ABTest] = {}
        self.assignments: dict[str, TestAssignment] = {}
        # Add index for faster user assignment lookups
        self.user_assignments: dict[str, dict[str, TestAssignment]] = {}  # user_id -> {test_id: assignment}
        self.events: list[TestEvent] = []
        self.results: dict[str, TestResult] = {}
        self.max_events = 100000  # Limit event storage

    def _validate_test_config(self, test: ABTest) -> list[str]:
        """Validate test configuration and return list of errors.

        Args:
            test: Test to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate variants
        if not test.variants:
            errors.append("Test must have at least one variant")
        elif len(test.variants) < 2:
            errors.append("Test must have at least two variants for comparison")

        # Check for control variant
        control_count = sum(1 for v in test.variants if v.is_control)
        if control_count == 0:
            errors.append("Test should have exactly one control variant")
        elif control_count > 1:
            errors.append("Test cannot have multiple control variants")

        # Validate variant weights for weighted allocation
        if test.allocation_strategy == VariantAllocation.WEIGHTED:
            total_weight = sum(v.weight for v in test.variants if v.active)
            if total_weight <= 0:
                errors.append("Weighted allocation requires at least one variant with positive weight")

        # Validate sample size requirements
        if test.minimum_sample_size < 10:
            errors.append("Minimum sample size should be at least 10")

        # Validate confidence level
        if not (0.5 <= test.confidence_level <= 0.99):
            errors.append("Confidence level must be between 0.5 and 0.99")

        # Validate traffic percentage
        if not (0.0 <= test.traffic_percentage <= 1.0):
            errors.append("Traffic percentage must be between 0.0 and 1.0")

        # Validate duration
        if test.duration_days and test.duration_days <= 0:
            errors.append("Duration must be positive")

        # Validate metric configuration
        if test.primary_metric.improvement_threshold < 0:
            errors.append("Improvement threshold must be non-negative")

        return errors

    async def create_test(
        self,
        name: str,
        description: str,
        test_type: TestType,
        variants: list[dict[str, Any]],
        primary_metric: dict[str, Any],
        created_by: str,
        secondary_metrics: list[dict[str, Any]] | None = None,
        allocation_strategy: VariantAllocation = VariantAllocation.EQUAL,
        traffic_percentage: float = 1.0,
        duration_days: int | None = None,
        target_users: dict[str, Any] | None = None,
        **kwargs,
    ) -> str:
        """Create a new A/B test.

        Args:
            name: Test name
            description: Test description
            test_type: Type of test
            variants: List of variant configurations
            primary_metric: Primary metric configuration
            created_by: User creating the test
            secondary_metrics: Secondary metrics
            allocation_strategy: Variant allocation strategy
            traffic_percentage: Percentage of traffic to include
            duration_days: Test duration in days
            target_users: User targeting configuration
            **kwargs: Additional test configuration

        Returns:
            Test ID
        """
        # Create variants
        test_variants = []
        for i, variant_config in enumerate(variants):
            variant = TestVariant(
                name=variant_config.get("name", f"Variant {i+1}"),
                description=variant_config.get("description", ""),
                weight=variant_config.get("weight", 1.0),
                configuration=variant_config.get("configuration", {}),
                is_control=variant_config.get("is_control", i == 0),
            )
            test_variants.append(variant)

        # Create metrics
        primary_test_metric = TestMetric(**primary_metric)
        secondary_test_metrics = [
            TestMetric(**metric) for metric in (secondary_metrics or [])
        ]

        # Create test
        test = ABTest(
            name=name,
            description=description,
            test_type=test_type,
            variants=test_variants,
            primary_metric=primary_test_metric,
            secondary_metrics=secondary_test_metrics,
            allocation_strategy=allocation_strategy,
            traffic_percentage=traffic_percentage,
            duration_days=duration_days,
            created_by=created_by,
            target_users=target_users or {},
            **kwargs,
        )

        # Validate test configuration
        validation_errors = self._validate_test_config(test)
        if validation_errors:
            error_msg = f"Test validation failed: {'; '.join(validation_errors)}"
            logger.error(error_msg, test_id=test.id)
            raise ValueError(error_msg)

        self.tests[test.id] = test

        logger.info(
            "Created A/B test",
            test_id=test.id,
            name=name,
            test_type=test_type.value,
            variants=len(test_variants),
        )

        return test.id

    async def start_test(self, test_id: str) -> bool:
        """Start an A/B test.

        Args:
            test_id: Test ID

        Returns:
            True if started successfully, False otherwise
        """
        test = self.tests.get(test_id)
        if not test:
            return False

        if test.status != TestStatus.DRAFT:
            logger.warning(
                f"Cannot start test {test_id} - status is {test.status}"
            )
            return False

        test.status = TestStatus.RUNNING
        test.start_date = datetime.now(UTC)

        if test.duration_days:
            test.end_date = test.start_date + timedelta(
                days=test.duration_days
            )

        test.updated_at = datetime.now(UTC)

        logger.info(f"Started A/B test {test_id}")
        return True

    async def pause_test(self, test_id: str) -> bool:
        """Pause an A/B test.

        Args:
            test_id: Test ID

        Returns:
            True if paused successfully, False otherwise
        """
        test = self.tests.get(test_id)
        if not test:
            return False

        if test.status != TestStatus.RUNNING:
            return False

        test.status = TestStatus.PAUSED
        test.updated_at = datetime.now(UTC)

        logger.info(f"Paused A/B test {test_id}")
        return True

    async def stop_test(self, test_id: str) -> bool:
        """Stop an A/B test.

        Args:
            test_id: Test ID

        Returns:
            True if stopped successfully, False otherwise
        """
        test = self.tests.get(test_id)
        if not test:
            return False

        if test.status not in [TestStatus.RUNNING, TestStatus.PAUSED]:
            return False

        test.status = TestStatus.COMPLETED
        test.end_date = datetime.now(UTC)
        test.updated_at = datetime.now(UTC)

        # Generate final results
        await self._analyze_test_results(test_id)

        logger.info(f"Stopped A/B test {test_id}")
        return True

    async def assign_variant(
        self,
        test_id: str,
        user_id: str,
        session_id: str | None = None,
        user_attributes: dict[str, Any] | None = None,
    ) -> str | None:
        """Assign a user to a test variant.

        Args:
            test_id: Test ID
            user_id: User ID
            session_id: Optional session ID
            user_attributes: User attributes for targeting

        Returns:
            Variant ID or None if not assigned
        """
        test = self.tests.get(test_id)
        if not test or test.status != TestStatus.RUNNING:
            return None

        # Check if user already assigned
        existing_assignment = await self._get_user_assignment(
            test_id, user_id
        )
        if existing_assignment:
            return existing_assignment.variant_id

        # Check traffic percentage
        if not self._should_include_user_in_test(test, user_id):
            return None

        # Check targeting criteria
        if not self._matches_targeting_criteria(
            test, user_attributes or {}
        ):
            return None

        # Assign variant based on strategy
        variant_id = await self._assign_variant_by_strategy(
            test, user_id, user_attributes
        )

        if variant_id:
            assignment = TestAssignment(
                test_id=test_id,
                user_id=user_id,
                variant_id=variant_id,
                session_id=session_id,
            )
            self.assignments[assignment.id] = assignment

            # Update user assignments index
            if user_id not in self.user_assignments:
                self.user_assignments[user_id] = {}
            self.user_assignments[user_id][test_id] = assignment

            logger.debug(
                "Assigned user to variant",
                test_id=test_id,
                user_id=user_id,
                variant_id=variant_id,
            )

        return variant_id

    async def record_event(
        self,
        test_id: str,
        user_id: str,
        event_type: str,
        event_data: dict[str, Any] | None = None,
        metrics: dict[str, float] | None = None,
        session_id: str | None = None,
    ) -> str:
        """Record an event for A/B test analysis.

        Args:
            test_id: Test ID
            user_id: User ID
            event_type: Type of event
            event_data: Event data
            metrics: Metrics to record
            session_id: Optional session ID

        Returns:
            Event ID
        """
        # Get user's variant assignment
        assignment = await self._get_user_assignment(test_id, user_id)
        if not assignment:
            # User not assigned to this test
            return ""

        event = TestEvent(
            test_id=test_id,
            variant_id=assignment.variant_id,
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            event_data=event_data or {},
            metrics=metrics or {},
        )

        self.events.append(event)

        # Limit event storage
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events :]

        logger.debug(
            "Recorded test event",
            test_id=test_id,
            user_id=user_id,
            event_type=event_type,
            variant_id=assignment.variant_id,
        )

        return event.id

    async def get_test_results(self, test_id: str) -> TestResult | None:
        """Get results for an A/B test.

        Args:
            test_id: Test ID

        Returns:
            Test results or None if not found
        """
        if test_id not in self.results:
            await self._analyze_test_results(test_id)

        return self.results.get(test_id)

    async def list_tests(
        self,
        status: TestStatus | None = None,
        test_type: TestType | None = None,
        created_by: str | None = None,
    ) -> list[ABTest]:
        """List A/B tests with optional filtering.

        Args:
            status: Filter by status
            test_type: Filter by test type
            created_by: Filter by creator

        Returns:
            List of tests
        """
        tests = list(self.tests.values())

        if status:
            tests = [t for t in tests if t.status == status]

        if test_type:
            tests = [t for t in tests if t.test_type == test_type]

        if created_by:
            tests = [t for t in tests if t.created_by == created_by]

        # Sort by creation date descending
        tests.sort(key=lambda x: x.created_at, reverse=True)

        return tests

    async def get_variant_configuration(
        self, test_id: str, variant_id: str
    ) -> dict[str, Any] | None:
        """Get configuration for a specific variant.

        Args:
            test_id: Test ID
            variant_id: Variant ID

        Returns:
            Variant configuration or None if not found
        """
        test = self.tests.get(test_id)
        if not test:
            return None

        for variant in test.variants:
            if variant.id == variant_id:
                return variant.configuration

        return None

    def _should_include_user_in_test(
        self, test: ABTest, user_id: str
    ) -> bool:
        """Check if user should be included in test based on traffic percentage.

        Args:
            test: A/B test
            user_id: User ID

        Returns:
            True if user should be included
        """
        if test.traffic_percentage >= 1.0:
            return True

        # Use deterministic hash-based assignment
        hash_input = f"{test.id}:{user_id}"
        hash_value = int(
            hashlib.md5(hash_input.encode()).hexdigest(), 16
        )
        return (hash_value % 10000) / 10000.0 < test.traffic_percentage

    def _matches_targeting_criteria(
        self, test: ABTest, user_attributes: dict[str, Any]
    ) -> bool:
        """Check if user matches targeting criteria.

        Args:
            test: A/B test
            user_attributes: User attributes

        Returns:
            True if user matches criteria
        """
        # Check inclusion criteria
        for key, value in test.target_users.items():
            if key not in user_attributes:
                return False
            if user_attributes[key] != value:
                return False

        # Check exclusion criteria
        for key, value in test.exclude_users.items():
            if key in user_attributes and user_attributes[key] == value:
                return False

        return True

    async def _assign_variant_by_strategy(
        self,
        test: ABTest,
        user_id: str,
        user_attributes: dict[str, Any] | None,
    ) -> str | None:
        """Assign variant based on allocation strategy.

        Args:
            test: A/B test
            user_id: User ID
            user_attributes: User attributes

        Returns:
            Variant ID or None
        """
        active_variants = [v for v in test.variants if v.active]
        if not active_variants:
            return None

        if test.allocation_strategy == VariantAllocation.EQUAL:
            # Equal distribution
            hash_input = f"{test.id}:{user_id}"
            hash_value = int(
                hashlib.md5(hash_input.encode()).hexdigest(), 16
            )
            variant_index = hash_value % len(active_variants)
            return active_variants[variant_index].id

        elif test.allocation_strategy == VariantAllocation.WEIGHTED:
            # Weighted distribution
            total_weight = sum(v.weight for v in active_variants)
            if total_weight <= 0:
                # If all weights are 0 or negative, fall back to equal distribution
                hash_input = f"{test.id}:{user_id}"
                hash_value = int(
                    hashlib.md5(hash_input.encode()).hexdigest(), 16
                )
                variant_index = hash_value % len(active_variants)
                return active_variants[variant_index].id

            hash_input = f"{test.id}:{user_id}"
            hash_value = int(
                hashlib.md5(hash_input.encode()).hexdigest(), 16
            )
            # Use higher precision for better distribution
            random_value = (
                (hash_value % 10000000) / 10000000.0 * total_weight
            )

            cumulative_weight = 0
            for variant in active_variants:
                cumulative_weight += variant.weight
                if random_value <= cumulative_weight:
                    return variant.id

        # Fallback to first variant
        return active_variants[0].id

    async def _get_user_assignment(
        self, test_id: str, user_id: str
    ) -> TestAssignment | None:
        """Get user's assignment for a test.

        Args:
            test_id: Test ID
            user_id: User ID

        Returns:
            Assignment or None if not found
        """
        # Use indexed lookup for O(1) performance
        user_tests = self.user_assignments.get(user_id, {})
        return user_tests.get(test_id)

    async def _analyze_test_results(self, test_id: str) -> None:
        """Analyze test results and generate statistics.

        Args:
            test_id: Test ID
        """
        test = self.tests.get(test_id)
        if not test:
            return

        # Get test events
        test_events = [e for e in self.events if e.test_id == test_id]

        # Group by variant
        variant_results = {}
        for variant in test.variants:
            variant_events = [
                e for e in test_events if e.variant_id == variant.id
            ]

            # Calculate basic metrics
            total_events = len(variant_events)
            unique_users = len({e.user_id for e in variant_events})

            # Calculate metric aggregations
            metrics = {}
            if variant_events:
                # Check if any events have the primary metric
                metric_values = [
                    e.metrics.get(test.primary_metric.name, 0)
                    for e in variant_events
                    if test.primary_metric.name in e.metrics
                ]
                if metric_values:
                    metrics[test.primary_metric.name] = {
                        "mean": sum(metric_values) / len(metric_values),
                        "count": len(metric_values),
                        "sum": sum(metric_values),
                        "std": (
                            (sum((x - sum(metric_values) / len(metric_values))**2 for x in metric_values) / len(metric_values))**0.5
                            if len(metric_values) > 1 else 0.0
                        )
                    }

                # Calculate secondary metrics as well
                for secondary_metric in test.secondary_metrics:
                    secondary_values = [
                        e.metrics.get(secondary_metric.name, 0)
                        for e in variant_events
                        if secondary_metric.name in e.metrics
                    ]
                    if secondary_values:
                        metrics[secondary_metric.name] = {
                            "mean": sum(secondary_values) / len(secondary_values),
                            "count": len(secondary_values),
                            "sum": sum(secondary_values),
                            "std": (
                                (sum((x - sum(secondary_values) / len(secondary_values))**2 for x in secondary_values) / len(secondary_values))**0.5
                                if len(secondary_values) > 1 else 0.0
                            )
                        }

            variant_results[variant.id] = {
                "variant_name": variant.name,
                "total_events": total_events,
                "unique_users": unique_users,
                "metrics": metrics,
            }

        # Statistical significance and confidence intervals
        statistical_significance = {}
        confidence_intervals = {}

        if len(variant_results) >= 2:
            # Implement proper statistical testing
            control_variant = None
            test_variants = []

            # Find control variant (first is_control=True variant)
            for variant in test.variants:
                if variant.is_control and variant.id in variant_results:
                    control_variant = variant.id
                    break

            # If no explicit control, use first variant
            if not control_variant and variant_results:
                control_variant = list(variant_results.keys())[0]

            # Collect test variants
            for variant_id in variant_results:
                if variant_id != control_variant:
                    test_variants.append(variant_id)

            # Perform statistical tests for each variant vs control
            if control_variant and test_variants:
                control_metrics = variant_results[control_variant].get("metrics", {})

                for variant_id in test_variants:
                    variant_metrics = variant_results[variant_id].get("metrics", {})

                    # Test primary metric
                    primary_metric_name = test.primary_metric.name
                    if (primary_metric_name in control_metrics and
                        primary_metric_name in variant_metrics):

                        control_data = control_metrics[primary_metric_name]
                        variant_data = variant_metrics[primary_metric_name]

                        # Simple two-sample test approximation
                        # In production, use scipy.stats.ttest_ind or similar
                        control_mean = control_data.get("mean", 0)
                        variant_mean = variant_data.get("mean", 0)
                        control_count = control_data.get("count", 0)
                        variant_count = variant_data.get("count", 0)
                        control_std = control_data.get("std", 0)
                        variant_std = variant_data.get("std", 0)

                        # Calculate confidence intervals (95% CI approximation)
                        if control_count > 1 and variant_count > 1:
                            # Simple t-test approximation
                            control_se = control_std / (control_count ** 0.5) if control_count > 0 else 0
                            variant_se = variant_std / (variant_count ** 0.5) if variant_count > 0 else 0

                            # 95% CI (using z-score approximation of 1.96)
                            z_score = 1.96
                            control_margin = z_score * control_se
                            variant_margin = z_score * variant_se

                            confidence_intervals[control_variant] = {
                                primary_metric_name: {
                                    "lower": control_mean - control_margin,
                                    "upper": control_mean + control_margin,
                                }
                            }

                            confidence_intervals[variant_id] = {
                                primary_metric_name: {
                                    "lower": variant_mean - variant_margin,
                                    "upper": variant_mean + variant_margin,
                                }
                            }

                            # Simple significance test: check if confidence intervals overlap
                            control_upper = control_mean + control_margin
                            control_lower = control_mean - control_margin
                            variant_upper = variant_mean + variant_margin
                            variant_lower = variant_mean - variant_margin

                            # Non-overlapping intervals suggest significance
                            intervals_overlap = not (control_upper < variant_lower or variant_upper < control_lower)

                            # Also check minimum sample size and effect size
                            min_sample_met = (control_count >= test.minimum_sample_size and
                                            variant_count >= test.minimum_sample_size)

                            # Check if difference meets improvement threshold
                            if test.primary_metric.direction == "increase":
                                meets_threshold = (variant_mean - control_mean) / control_mean >= test.primary_metric.improvement_threshold if control_mean > 0 else False
                            else:
                                meets_threshold = (control_mean - variant_mean) / control_mean >= test.primary_metric.improvement_threshold if control_mean > 0 else False

                            statistical_significance[variant_id] = (
                                not intervals_overlap and min_sample_met and meets_threshold
                            )
                        else:
                            # Insufficient data
                            statistical_significance[variant_id] = False
                            confidence_intervals[variant_id] = {
                                primary_metric_name: {
                                    "lower": variant_mean,
                                    "upper": variant_mean,
                                }
                            }
                    else:
                        statistical_significance[variant_id] = False

                # Also set significance for control
                if control_variant:
                    if control_variant not in statistical_significance:
                        statistical_significance[control_variant] = True  # Control is baseline

        # Generate recommendations
        recommendations = []
        if variant_results:
            best_variant = max(
                variant_results.items(),
                key=lambda x: x[1]
                .get("metrics", {})
                .get(test.primary_metric.name, {})
                .get("mean", 0),
            )
            recommendations.append(
                f"Variant '{best_variant[1]['variant_name']}' shows the highest {test.primary_metric.name}"
            )

        # Store results
        result = TestResult(
            test_id=test_id,
            variant_results=variant_results,
            statistical_significance=statistical_significance,
            confidence_intervals=confidence_intervals,
            recommendations=recommendations,
        )

        self.results[test_id] = result

        logger.info(f"Analyzed results for test {test_id}")

    async def get_test(self, test_id: str) -> ABTest | None:
        """Get a test by ID."""
        return self.tests.get(test_id)

    async def update_test(
        self, test_id: str, update_data: dict[str, Any]
    ) -> ABTest | None:
        """Update a test configuration."""
        test = self.tests.get(test_id)
        if not test:
            return None

        # Update allowed fields
        for field, value in update_data.items():
            if hasattr(test, field):
                setattr(test, field, value)

        self.tests[test_id] = test
        logger.info(f"Updated test {test_id}")
        return test

    async def delete_test(self, test_id: str) -> bool:
        """Delete a test and clean up all related data."""
        if test_id in self.tests:
            # Clean up test
            del self.tests[test_id]

            # Clean up results
            if test_id in self.results:
                del self.results[test_id]

            # Clean up assignments and user assignment index
            assignments_to_remove = []
            for assignment_id, assignment in self.assignments.items():
                if assignment.test_id == test_id:
                    assignments_to_remove.append(assignment_id)
                    # Remove from user assignments index
                    user_id = assignment.user_id
                    if user_id in self.user_assignments:
                        if test_id in self.user_assignments[user_id]:
                            del self.user_assignments[user_id][test_id]
                        # Clean up empty user entries
                        if not self.user_assignments[user_id]:
                            del self.user_assignments[user_id]

            # Remove assignments
            for assignment_id in assignments_to_remove:
                del self.assignments[assignment_id]

            # Clean up events
            self.events = [e for e in self.events if e.test_id != test_id]

            logger.info(f"Deleted test {test_id} and cleaned up {len(assignments_to_remove)} assignments")
            return True
        return False

    async def complete_test(self, test_id: str) -> bool:
        """Mark a test as completed."""
        test = self.tests.get(test_id)
        if test:
            test.status = TestStatus.COMPLETED
            test.end_date = datetime.now(UTC)
            logger.info(f"Completed test {test_id}")
            return True
        return False

    async def analyze_test(self, test_id: str) -> TestResult | None:
        """Analyze test results."""
        await self._analyze_test_results(test_id)
        return self.results.get(test_id)

    async def end_test(
        self, test_id: str, winner_variant: str | None = None
    ) -> bool:
        """End a test with optional winner selection."""
        test = self.tests.get(test_id)
        if test:
            test.status = TestStatus.COMPLETED
            test.end_date = datetime.now(UTC)
            if winner_variant:
                # Store winner information in metadata
                if not test.metadata:
                    test.metadata = {}
                test.metadata["winner_variant"] = winner_variant
            logger.info(f"Ended test {test_id}")
            return True
        return False

    async def get_test_performance(
        self, test_id: str
    ) -> dict[str, Any] | None:
        """Get test performance metrics."""
        test = self.tests.get(test_id)
        result = self.results.get(test_id)

        if not test:
            return None

        performance = {
            "test_id": test_id,
            "status": test.status.value,
            "total_participants": len(
                [
                    a
                    for a in self.assignments.values()
                    if a.test_id == test_id
                ]
            ),
            "events_count": len(
                [e for e in self.events if e.test_id == test_id]
            ),
            "start_date": test.start_date,
            "end_date": test.end_date,
        }

        if result:
            performance.update(
                {
                    "variant_results": result.variant_results,
                    "statistical_significance": result.statistical_significance,
                    "confidence_intervals": result.confidence_intervals,
                    "recommendations": result.recommendations,
                }
            )

        return performance


# Global A/B test manager
ab_test_manager = ABTestManager()


# Helper functions for common test scenarios
async def create_prompt_test(
    name: str,
    prompt_variants: list[dict[str, Any]],
    created_by: str,
    duration_days: int = 7,
) -> str:
    """Create an A/B test for prompt variations.

    Args:
        name: Test name
        prompt_variants: List of prompt configurations
        created_by: User creating the test
        duration_days: Test duration

    Returns:
        Test ID
    """
    return await ab_test_manager.create_test(
        name=name,
        description=f"A/B test for prompt variations: {name}",
        test_type=TestType.PROMPT,
        variants=prompt_variants,
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
            },
            {
                "name": "token_usage",
                "metric_type": MetricType.TOKEN_USAGE,
                "direction": "decrease",
            },
        ],
        created_by=created_by,
        duration_days=duration_days,
    )


async def create_model_test(
    name: str,
    model_variants: list[dict[str, Any]],
    created_by: str,
    duration_days: int = 14,
) -> str:
    """Create an A/B test for model variations.

    Args:
        name: Test name
        model_variants: List of model configurations
        created_by: User creating the test
        duration_days: Test duration

    Returns:
        Test ID
    """
    return await ab_test_manager.create_test(
        name=name,
        description=f"A/B test for model variations: {name}",
        test_type=TestType.MODEL,
        variants=model_variants,
        primary_metric={
            "name": "accuracy",
            "metric_type": MetricType.ACCURACY,
            "direction": "increase",
            "improvement_threshold": 0.05,
        },
        secondary_metrics=[
            {
                "name": "response_time",
                "metric_type": MetricType.RESPONSE_TIME,
                "direction": "decrease",
            },
            {
                "name": "error_rate",
                "metric_type": MetricType.ERROR_RATE,
                "direction": "decrease",
            },
        ],
        created_by=created_by,
        duration_days=duration_days,
    )
