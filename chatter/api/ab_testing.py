"""A/B testing management endpoints."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.ab_testing import (
    ABTestActionResponse,
    ABTestAnalyticsResponse,
    ABTestCreateRequest,
    ABTestDeleteResponse,
    ABTestListRequest,
    ABTestListResponse,
    ABTestMetricsResponse,
    ABTestResponse,
    ABTestResultsResponse,
    ABTestUpdateRequest,
    TestStatus,
    TestType,
)
from chatter.services.ab_testing import (
    ABTestManager,
    MetricType,
    VariantAllocation,
)
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    ForbiddenProblem,
    InternalServerProblem,
    NotFoundProblem,
)

logger = get_logger(__name__)
router = APIRouter()


def _check_test_access(
    test: ABTestResponse | None, current_user: User
) -> None:
    """Check if user has access to the test.

    Args:
        test: Test to check access for
        current_user: Current user

    Raises:
        NotFoundProblem: If test doesn't exist
        ForbiddenProblem: If user doesn't have access
    """
    if not test:
        raise NotFoundProblem(detail="A/B test not found")

    # For now, users can only access their own tests
    # In a production system, you'd implement proper RBAC here
    if test.created_by != current_user.username:
        # Allow admins to access all tests (assuming admin role exists)
        user_roles = getattr(current_user, "roles", [])
        if (
            "admin" not in user_roles
            and "ab_testing_admin" not in user_roles
        ):
            raise ForbiddenProblem(
                detail="You don't have permission to access this A/B test"
            )


def _validate_test_operation(
    test: ABTestResponse, operation: str, current_user: User
) -> None:
    """Validate if user can perform operation on test.

    Args:
        test: Test to operate on
        operation: Operation to perform (start, stop, delete, etc.)
        current_user: Current user

    Raises:
        ForbiddenProblem: If operation is not allowed
        BadRequestProblem: If operation is invalid for current test state
    """
    _check_test_access(test, current_user)

    # Check operation validity based on test status
    if operation == "start" and test.status not in [
        TestStatus.DRAFT,
        TestStatus.PAUSED,
    ]:
        raise BadRequestProblem(
            detail=f"Cannot start test in {test.status} status"
        )

    if operation == "pause" and test.status != TestStatus.RUNNING:
        raise BadRequestProblem(
            detail=f"Cannot pause test in {test.status} status"
        )

    if operation in ["complete", "end"] and test.status not in [
        TestStatus.RUNNING,
        TestStatus.PAUSED,
    ]:
        raise BadRequestProblem(
            detail=f"Cannot complete test in {test.status} status"
        )

    if operation == "delete" and test.status == TestStatus.RUNNING:
        raise BadRequestProblem(
            detail="Cannot delete running test. Pause or complete it first."
        )


async def get_ab_test_manager() -> ABTestManager:
    """Get A/B test manager instance.

    Returns:
        ABTestManager instance
    """
    from chatter.services.ab_testing import ab_test_manager

    return ab_test_manager


@router.post(
    "/",
    response_model=ABTestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ab_test(
    test_data: ABTestCreateRequest,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestResponse:
    """Create a new A/B test.

    Args:
        test_data: A/B test creation data
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Created test data
    """
    try:
        # Validate and sanitize inputs
        if not test_data.name or len(test_data.name.strip()) == 0:
            raise BadRequestProblem(detail="Test name is required")

        if len(test_data.name) > 200:
            raise BadRequestProblem(
                detail="Test name too long (max 200 characters)"
            )

        if len(test_data.description) > 1000:
            raise BadRequestProblem(
                detail="Test description too long (max 1000 characters)"
            )

        # Validate variants
        if len(test_data.variants) < 2:
            raise BadRequestProblem(
                detail="Test must have at least 2 variants"
            )

        if len(test_data.variants) > 10:
            raise BadRequestProblem(
                detail="Test cannot have more than 10 variants"
            )

        # Create variants with validation
        variants = []
        total_weight = 0
        for i, variant_data in enumerate(test_data.variants):
            if (
                not variant_data.name
                or len(variant_data.name.strip()) == 0
            ):
                raise BadRequestProblem(
                    detail=f"Variant {i+1} name is required"
                )

            if len(variant_data.name) > 100:
                raise BadRequestProblem(
                    detail=f"Variant {i+1} name too long (max 100 characters)"
                )

            if variant_data.weight < 0:
                raise BadRequestProblem(
                    detail=f"Variant {i+1} weight cannot be negative"
                )

            total_weight += variant_data.weight

            variant_dict = {
                "name": variant_data.name.strip(),
                "description": variant_data.description[
                    :500
                ],  # Limit description length
                "weight": variant_data.weight,
                "configuration": variant_data.configuration,
                "is_control": (i == 0),  # First variant is control
            }
            variants.append(variant_dict)

        # Validate total weight for weighted allocation
        if (
            test_data.allocation_strategy == VariantAllocation.WEIGHTED
            and total_weight <= 0
        ):
            raise BadRequestProblem(
                detail="Weighted allocation requires at least one variant with positive weight"
            )

        # Validate metrics
        if not test_data.metrics:
            raise BadRequestProblem(
                detail="Test must have at least one metric"
            )

        # Create test
        test_id = await ab_test_manager.create_test(
            name=test_data.name,
            description=test_data.description,
            test_type=test_data.test_type,
            variants=variants,
            primary_metric={
                "name": test_data.metrics[0].value,
                "metric_type": test_data.metrics[0],
                "direction": "increase",  # Default direction
                "improvement_threshold": 0.05,  # Default 5% improvement
            },
            created_by=current_user.username,
            secondary_metrics=[
                {
                    "name": metric.value,
                    "metric_type": metric,
                    "direction": "increase",
                    "improvement_threshold": 0.05,
                }
                for metric in test_data.metrics[1:]
            ],
            allocation_strategy=test_data.allocation_strategy,
            traffic_percentage=test_data.traffic_percentage / 100.0,
            duration_days=test_data.duration_days,
            target_users=test_data.target_audience or {},
            confidence_level=test_data.confidence_level,
            minimum_sample_size=test_data.min_sample_size,
            tags=test_data.tags,
            metadata=test_data.metadata,
        )
        created_test = await ab_test_manager.get_test(test_id)

        if not created_test:
            raise InternalServerProblem(
                detail="Failed to retrieve created test"
            )

        # Convert to response format
        from chatter.schemas.ab_testing import (
            TestVariant as ResponseTestVariant,
        )

        response_variants = []
        for variant in created_test.variants:
            response_variants.append(
                ResponseTestVariant(
                    name=variant.name,
                    description=variant.description,
                    configuration=variant.configuration,
                    weight=variant.weight,
                )
            )

        return ABTestResponse(
            id=created_test.id,
            name=created_test.name,
            description=created_test.description,
            test_type=created_test.test_type,
            status=created_test.status,
            allocation_strategy=created_test.allocation_strategy,
            variants=response_variants,
            metrics=test_data.metrics,
            duration_days=created_test.duration_days
            or test_data.duration_days,
            min_sample_size=created_test.minimum_sample_size,
            confidence_level=created_test.confidence_level,
            target_audience=created_test.target_users,
            traffic_percentage=created_test.traffic_percentage * 100.0,
            start_date=created_test.start_date,
            end_date=created_test.end_date,
            participant_count=0,
            created_at=created_test.created_at,
            updated_at=created_test.updated_at,
            created_by=created_test.created_by,
            tags=created_test.tags,
            metadata=created_test.metadata,
        )

    except Exception as e:
        logger.error("Failed to create A/B test", error=str(e))
        raise InternalServerProblem(
            detail="Failed to create A/B test"
        ) from e


@router.get("/", response_model=ABTestListResponse)
async def list_ab_tests(
    status: TestStatus | None = Query(None, description="Filter by status"),
    test_type: TestType | None = Query(None, description="Filter by test type"),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestListResponse:
    """List A/B tests with optional filtering.

    Args:
        status: Filter by status
        test_type: Filter by test type
        tags: Filter by tags
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        List of A/B tests
    """
    try:
        tests = await ab_test_manager.list_tests(
            status=status,
            test_type=test_type,
        )

        # Filter by tags if specified
        if tags:
            filtered_tests = []
            for test in tests:
                if any(tag in test.tags for tag in tags):
                    filtered_tests.append(test)
            tests = filtered_tests

        # Convert to response format
        test_responses = []
        for test in tests:
            from chatter.schemas.ab_testing import (
                TestVariant as ResponseTestVariant,
            )

            response_variants = []
            for variant in test.variants:
                response_variants.append(
                    ResponseTestVariant(
                        name=variant.name,
                        description=variant.description,
                        configuration=variant.configuration,
                        weight=variant.weight,
                    )
                )

            # Get metrics from test configuration
            metrics = [test.primary_metric.metric_type]
            metrics.extend(
                [m.metric_type for m in test.secondary_metrics]
            )

            test_responses.append(
                ABTestResponse(
                    id=test.id,
                    name=test.name,
                    description=test.description,
                    test_type=test.test_type,
                    status=test.status,
                    allocation_strategy=test.allocation_strategy,
                    variants=response_variants,
                    metrics=metrics,
                    duration_days=test.duration_days or 7,
                    min_sample_size=test.minimum_sample_size,
                    confidence_level=test.confidence_level,
                    target_audience=test.target_users,
                    traffic_percentage=test.traffic_percentage * 100.0,
                    start_date=test.start_date,
                    end_date=test.end_date,
                    participant_count=0,  # Would need to be calculated
                    created_at=test.created_at,
                    updated_at=test.updated_at,
                    created_by=test.created_by,
                    tags=test.tags,
                    metadata=test.metadata,
                )
            )

        return ABTestListResponse(
            tests=test_responses, total=len(test_responses)
        )

    except Exception as e:
        logger.error("Failed to list A/B tests", error=str(e))
        raise InternalServerProblem(
            detail="Failed to list A/B tests"
        ) from e


@router.get("/{test_id}", response_model=ABTestResponse)
async def get_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestResponse:
    """Get A/B test by ID.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        A/B test data
    """
    try:
        test = await ab_test_manager.get_test(test_id)
        if not test:
            raise NotFoundProblem(
                detail=f"A/B test {test_id} not found"
            )

        # Convert to response format for access check
        from chatter.schemas.ab_testing import (
            TestVariant as ResponseTestVariant,
        )

        response_variants = []
        for variant in test.variants:
            response_variants.append(
                ResponseTestVariant(
                    name=variant.name,
                    description=variant.description,
                    configuration=variant.configuration,
                    weight=variant.weight,
                )
            )

        # Get metrics from test configuration
        metrics = [test.primary_metric.metric_type]
        metrics.extend([m.metric_type for m in test.secondary_metrics])

        test_response = ABTestResponse(
            id=test.id,
            name=test.name,
            description=test.description,
            test_type=test.test_type,
            status=test.status,
            allocation_strategy=test.allocation_strategy,
            variants=response_variants,
            metrics=metrics,
            duration_days=test.duration_days or 7,
            min_sample_size=test.minimum_sample_size,
            confidence_level=test.confidence_level,
            target_audience=test.target_users,
            traffic_percentage=test.traffic_percentage * 100.0,
            start_date=test.start_date,
            end_date=test.end_date,
            participant_count=0,  # Would need to be calculated
            created_at=test.created_at,
            updated_at=test.updated_at,
            created_by=test.created_by,
            tags=test.tags,
            metadata=test.metadata,
        )

        # Check access permissions
        _check_test_access(test_response, current_user)

        return test_response

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to get A/B test", test_id=test_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to get A/B test"
        ) from e


@router.put("/{test_id}", response_model=ABTestResponse)
async def update_ab_test(
    test_id: str,
    test_data: ABTestUpdateRequest,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestResponse:
    """Update an A/B test.

    Args:
        test_id: Test ID
        test_data: Test update data
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Updated test data
    """
    try:
        # Check if test exists
        test = await ab_test_manager.get_test(test_id)
        if not test:
            raise NotFoundProblem(
                detail=f"A/B test {test_id} not found"
            )

        # Update test data
        update_data = test_data.model_dump(exclude_unset=True)

        # Convert traffic percentage back to decimal
        if "traffic_percentage" in update_data:
            update_data["traffic_percentage"] = (
                update_data["traffic_percentage"] / 100.0
            )

        updated_test = await ab_test_manager.update_test(
            test_id, update_data
        )
        if not updated_test:
            raise InternalServerProblem(
                detail="Failed to update A/B test"
            )

        # Convert to response format (reuse logic from get_ab_test)
        from chatter.schemas.ab_testing import (
            TestVariant as ResponseTestVariant,
        )

        response_variants = []
        for variant in updated_test.variants:
            response_variants.append(
                ResponseTestVariant(
                    name=variant.name,
                    description=variant.description,
                    configuration=variant.configuration,
                    weight=variant.weight,
                )
            )

        metrics = [updated_test.primary_metric.metric_type]
        metrics.extend(
            [m.metric_type for m in updated_test.secondary_metrics]
        )

        return ABTestResponse(
            id=updated_test.id,
            name=updated_test.name,
            description=updated_test.description,
            test_type=updated_test.test_type,
            status=updated_test.status,
            allocation_strategy=updated_test.allocation_strategy,
            variants=response_variants,
            metrics=metrics,
            duration_days=updated_test.duration_days or 7,
            min_sample_size=updated_test.minimum_sample_size,
            confidence_level=updated_test.confidence_level,
            target_audience=updated_test.target_users,
            traffic_percentage=updated_test.traffic_percentage * 100.0,
            start_date=updated_test.start_date,
            end_date=updated_test.end_date,
            participant_count=0,
            created_at=updated_test.created_at,
            updated_at=updated_test.updated_at,
            created_by=updated_test.created_by,
            tags=updated_test.tags,
            metadata=updated_test.metadata,
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to update A/B test", test_id=test_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to update A/B test"
        ) from e


@router.delete("/{test_id}", response_model=ABTestDeleteResponse)
async def delete_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestDeleteResponse:
    """Delete an A/B test.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Deletion result
    """
    try:
        success = await ab_test_manager.delete_test(test_id)

        if not success:
            raise NotFoundProblem(
                detail=f"A/B test {test_id} not found"
            )

        return ABTestDeleteResponse(
            success=True,
            message=f"A/B test {test_id} deleted successfully",
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete A/B test", test_id=test_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to delete A/B test"
        ) from e


@router.post("/{test_id}/start", response_model=ABTestActionResponse)
async def start_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestActionResponse:
    """Start an A/B test.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Action result
    """
    try:
        success = await ab_test_manager.start_test(test_id)

        if not success:
            raise BadRequestProblem(
                detail="Failed to start test - check test status and configuration"
            )

        from chatter.services.ab_testing import TestStatus

        return ABTestActionResponse(
            success=True,
            message=f"A/B test {test_id} started successfully",
            test_id=test_id,
            new_status=TestStatus.RUNNING,
        )

    except BadRequestProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to start A/B test", test_id=test_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to start A/B test"
        ) from e


@router.post("/{test_id}/pause", response_model=ABTestActionResponse)
async def pause_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestActionResponse:
    """Pause an A/B test.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Action result
    """
    try:
        success = await ab_test_manager.pause_test(test_id)

        if not success:
            raise BadRequestProblem(
                detail="Failed to pause test - check test status"
            )

        from chatter.services.ab_testing import TestStatus

        return ABTestActionResponse(
            success=True,
            message=f"A/B test {test_id} paused successfully",
            test_id=test_id,
            new_status=TestStatus.PAUSED,
        )

    except BadRequestProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to pause A/B test", test_id=test_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to pause A/B test"
        ) from e


@router.post("/{test_id}/complete", response_model=ABTestActionResponse)
async def complete_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestActionResponse:
    """Complete an A/B test.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Action result
    """
    try:
        success = await ab_test_manager.complete_test(test_id)

        if not success:
            raise BadRequestProblem(
                detail="Failed to complete test - check test status"
            )

        from chatter.services.ab_testing import TestStatus

        return ABTestActionResponse(
            success=True,
            message=f"A/B test {test_id} completed successfully",
            test_id=test_id,
            new_status=TestStatus.COMPLETED,
        )

    except BadRequestProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to complete A/B test", test_id=test_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to complete A/B test"
        ) from e


@router.get("/{test_id}/results", response_model=ABTestResultsResponse)
async def get_ab_test_results(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestResultsResponse:
    """Get A/B test results and analysis.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Test results and analysis
    """
    try:
        results = await ab_test_manager.analyze_test(test_id)

        if not results:
            raise NotFoundProblem(
                detail=f"Results not available for test {test_id}"
            )

        # Convert results to response format
        from chatter.schemas.ab_testing import TestMetric

        metrics = []
        test = await ab_test_manager.get_test(test_id)
        test_name = test.name if test else "Unknown Test"
        test_status = test.status if test else TestStatus.COMPLETED

        # Convert variant results to metrics
        for variant_id, variant_data in results.variant_results.items():
            variant_name = variant_data.get("variant_name", variant_id)
            variant_metrics = variant_data.get("metrics", {})

            for metric_name, metric_data in variant_metrics.items():
                # Map string metric name to MetricType enum
                try:
                    metric_type = MetricType(metric_name)
                except ValueError:
                    metric_type = MetricType.CUSTOM

                # Extract confidence interval for this variant and metric
                confidence_interval = None
                if (
                    variant_id in results.confidence_intervals
                    and metric_name
                    in results.confidence_intervals[variant_id]
                ):
                    ci_data = results.confidence_intervals[variant_id][
                        metric_name
                    ]
                    if (
                        isinstance(ci_data, dict)
                        and "lower" in ci_data
                        and "upper" in ci_data
                    ):
                        confidence_interval = [
                            ci_data["lower"],
                            ci_data["upper"],
                        ]

                metrics.append(
                    TestMetric(
                        metric_type=metric_type,
                        variant_name=variant_name,
                        value=float(metric_data.get("mean", 0)),
                        sample_size=int(metric_data.get("count", 0)),
                        confidence_interval=confidence_interval,
                    )
                )

        # Format confidence intervals properly for response
        confidence_intervals_formatted = {}
        for (
            variant_id,
            intervals,
        ) in results.confidence_intervals.items():
            confidence_intervals_formatted[variant_id] = {}
            for metric, ci_data in intervals.items():
                if (
                    isinstance(ci_data, dict)
                    and "lower" in ci_data
                    and "upper" in ci_data
                ):
                    confidence_intervals_formatted[variant_id][
                        metric
                    ] = [
                        float(ci_data["lower"]),
                        float(ci_data["upper"]),
                    ]
                else:
                    # Fallback for malformed data
                    confidence_intervals_formatted[variant_id][
                        metric
                    ] = [0.0, 0.0]

        # Determine winning variant from statistical significance
        winning_variant = None
        for (
            variant_id,
            is_significant,
        ) in results.statistical_significance.items():
            if is_significant and variant_id in results.variant_results:
                # Check if this variant is better than others
                variant_data = results.variant_results[variant_id]
                variant_metrics = variant_data.get("metrics", {})
                primary_metric_name = (
                    test.primary_metric.name if test else None
                )
                if (
                    primary_metric_name
                    and primary_metric_name in variant_metrics
                ):
                    winning_variant = variant_data.get(
                        "variant_name", variant_id
                    )
                    break

        # Calculate total sample size and duration
        total_sample_size = sum(
            data.get("unique_users", 0)
            for data in results.variant_results.values()
        )

        duration_days = 7  # Default
        if test and test.start_date:
            from datetime import UTC, datetime

            end_date = test.end_date or datetime.now(UTC)
            duration_days = (end_date - test.start_date).days
            if duration_days <= 0:
                duration_days = 1

        return ABTestResultsResponse(
            test_id=test_id,
            test_name=test_name,
            status=test_status,
            metrics=metrics,
            statistical_significance=results.statistical_significance,
            confidence_intervals=confidence_intervals_formatted,
            winning_variant=winning_variant,
            recommendation=(
                results.recommendations[0]
                if results.recommendations
                else "Continue monitoring for more data"
            ),
            generated_at=results.analysis_date,
            sample_size=total_sample_size,
            duration_days=duration_days,
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to get A/B test results",
            test_id=test_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to get A/B test results"
        ) from e


@router.get("/{test_id}/metrics", response_model=ABTestMetricsResponse)
async def get_ab_test_metrics(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestMetricsResponse:
    """Get current A/B test metrics.

    Args:
        test_id: Test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Current test metrics
    """
    try:
        # Get test results from AB test manager
        test_result = await ab_test_manager.get_test_results(test_id)
        test_performance = await ab_test_manager.get_test_performance(
            test_id
        )

        if not test_result or not test_performance:
            # If no test results, return empty metrics
            return ABTestMetricsResponse(
                test_id=test_id,
                metrics=[],
                participant_count=0,
                last_updated=datetime.now(UTC),
            )

        from chatter.schemas.ab_testing import TestMetric

        # Build metrics from test results
        metrics = []
        for (
            variant_name,
            variant_data,
        ) in test_result.variant_results.items():
            for metric_name, metric_value in variant_data.items():
                # Convert metric name to MetricType enum
                try:
                    metric_type = MetricType(metric_name.lower())
                except ValueError:
                    # Skip unknown metric types
                    continue

                # Get sample size from variant data or use 0 as default
                sample_size = variant_data.get("sample_size", 0)

                # Get confidence interval if available
                confidence_interval = None
                if (
                    variant_name in test_result.confidence_intervals
                    and metric_name
                    in test_result.confidence_intervals[variant_name]
                ):
                    ci_data = test_result.confidence_intervals[
                        variant_name
                    ][metric_name]
                    if (
                        isinstance(ci_data, dict)
                        and "lower" in ci_data
                        and "upper" in ci_data
                    ):
                        confidence_interval = (
                            ci_data["lower"],
                            ci_data["upper"],
                        )

                metrics.append(
                    TestMetric(
                        metric_type=metric_type,
                        variant_name=variant_name,
                        value=(
                            float(metric_value)
                            if isinstance(metric_value, int | float)
                            else 0.0
                        ),
                        sample_size=(
                            int(sample_size)
                            if isinstance(sample_size, int | float)
                            else 0
                        ),
                        confidence_interval=(
                            list(confidence_interval)
                            if confidence_interval
                            else None
                        ),
                    )
                )

        return ABTestMetricsResponse(
            test_id=test_id,
            metrics=metrics,
            participant_count=test_performance.get(
                "total_participants", 0
            ),
            last_updated=test_result.analysis_date,
        )

    except Exception as e:
        logger.error(
            "Failed to get A/B test metrics",
            test_id=test_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to get A/B test metrics"
        ) from e


@router.post("/{test_id}/end", response_model=ABTestActionResponse)
async def end_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
    winner_variant: str | None = Query(
        None, description="Winning variant identifier"
    ),
) -> ABTestActionResponse:
    """End A/B test and declare winner.

    Args:
        test_id: A/B test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance
        winner_variant: Optional winning variant identifier

    Returns:
        Action response
    """
    try:
        # Check if test exists and get test details for validation
        test = await ab_test_manager.get_test(test_id)
        if not test:
            raise NotFoundProblem(
                detail=f"A/B test {test_id} not found"
            )

        # Create response for access check
        from chatter.schemas.ab_testing import (
            TestVariant as ResponseTestVariant,
        )

        response_variants = []
        for variant in test.variants:
            response_variants.append(
                ResponseTestVariant(
                    name=variant.name,
                    description=variant.description,
                    configuration=variant.configuration,
                    weight=variant.weight,
                )
            )

        # Get metrics from test configuration
        metrics = [test.primary_metric.metric_type]
        metrics.extend([m.metric_type for m in test.secondary_metrics])

        test_response = ABTestResponse(
            id=test.id,
            name=test.name,
            description=test.description,
            test_type=test.test_type,
            status=test.status,
            allocation_strategy=test.allocation_strategy,
            variants=response_variants,
            metrics=metrics,
            duration_days=test.duration_days or 7,
            min_sample_size=test.minimum_sample_size,
            confidence_level=test.confidence_level,
            target_audience=test.target_users,
            traffic_percentage=test.traffic_percentage * 100.0,
            start_date=test.start_date,
            end_date=test.end_date,
            participant_count=0,  # Would need to be calculated
            created_at=test.created_at,
            updated_at=test.updated_at,
            created_by=test.created_by,
            tags=test.tags,
            metadata=test.metadata,
        )

        # Validate test operation (access control and state validation)
        _validate_test_operation(test_response, "end", current_user)

        # Validate winner variant if provided
        if winner_variant:
            variant_exists = any(
                v.id == winner_variant for v in test.variants
            )
            if not variant_exists:
                # Also check by name for convenience
                variant_exists = any(
                    v.name == winner_variant for v in test.variants
                )
                if not variant_exists:
                    raise BadRequestProblem(
                        detail=f"Winner variant '{winner_variant}' not found in test variants"
                    )

        success = await ab_test_manager.end_test(
            test_id, winner_variant
        )

        if not success:
            raise InternalServerProblem(
                detail="Failed to end A/B test - internal error"
            )

        # Create appropriate message based on whether winner was specified
        if winner_variant:
            message = f"A/B test ended with winner: {winner_variant}"
        else:
            message = "A/B test ended successfully"

        return ABTestActionResponse(
            success=True,
            message=message,
            test_id=test_id,
            new_status=TestStatus.COMPLETED,
        )

    except (NotFoundProblem, BadRequestProblem, ForbiddenProblem):
        raise
    except Exception as e:
        logger.error(
            "Failed to end A/B test", test_id=test_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to end A/B test"
        ) from e


@router.get("/{test_id}/performance", response_model=dict[str, Any])
async def get_ab_test_performance(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> dict[str, Any]:
    """Get A/B test performance results by variant.

    Args:
        test_id: A/B test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Performance results per variant
    """
    try:
        performance = await ab_test_manager.get_test_performance(
            test_id
        )

        if not performance:
            raise NotFoundProblem(
                detail="A/B test not found or no performance data available",
                resource_type="ab_test",
                resource_id=test_id,
            ) from None

        return performance

    except Exception as e:
        logger.error(
            "Failed to get A/B test performance",
            test_id=test_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to get A/B test performance"
        ) from e


@router.get("/{test_id}/recommendations", response_model=dict[str, Any])
async def get_ab_test_recommendations(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> dict[str, Any]:
    """Get comprehensive recommendations for an A/B test.

    Args:
        test_id: A/B test ID
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Recommendations and insights for the test
    """
    try:
        # Check test exists and user has access
        test = await ab_test_manager.get_test(test_id)
        if not test:
            raise NotFoundProblem(
                detail="A/B test not found",
                resource_type="ab_test",
                resource_id=test_id,
            )

        # Create response for access check
        test_response = ABTestResponse(
            id=test.id,
            name=test.name,
            description=test.description,
            test_type=test.test_type,
            status=test.status,
            allocation_strategy=test.allocation_strategy,
            variants=[],  # Minimal for access check
            metrics=[test.primary_metric.metric_type],
            duration_days=test.duration_days or 7,
            min_sample_size=test.minimum_sample_size,
            confidence_level=test.confidence_level,
            target_audience=test.target_users,
            traffic_percentage=test.traffic_percentage * 100.0,
            start_date=test.start_date,
            end_date=test.end_date,
            participant_count=0,
            created_at=test.created_at,
            updated_at=test.updated_at,
            created_by=test.created_by,
            tags=test.tags,
            metadata=test.metadata,
        )

        _check_test_access(test_response, current_user)

        # Get recommendations
        recommendations = (
            await ab_test_manager.get_test_recommendations(test_id)
        )
        return recommendations

    except (NotFoundProblem, ForbiddenProblem):
        raise
    except Exception as e:
        logger.error(
            "Failed to get A/B test recommendations",
            test_id=test_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to get A/B test recommendations"
        ) from e


@router.get(
    "/{test_id}/analytics",
    response_model=ABTestAnalyticsResponse,
    responses={
        404: {"description": "A/B test not found"},
        403: {"description": "Access denied"},
    },
)
async def get_test_analytics(
    test_id: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestAnalyticsResponse:
    """Get comprehensive analytics for an A/B test."""
    try:
        test = await ab_test_manager.get_test(test_id)
        if not test:
            raise NotFoundProblem(
                detail="A/B test not found",
                resource_type="ab_test",
                resource_id=test_id,
            )

        # Create response for access check
        test_response = ABTestResponse(
            id=test.id,
            name=test.name,
            description=test.description,
            test_type=test.test_type,
            status=test.status,
            allocation_strategy=test.allocation_strategy,
            variants=[],  # Minimal for access check
            metrics=[test.primary_metric.metric_type],
            duration_days=test.duration_days or 7,
            min_sample_size=test.minimum_sample_size,
            confidence_level=test.confidence_level,
            target_audience=test.target_users,
            traffic_percentage=test.traffic_percentage * 100.0,
            start_date=test.start_date,
            end_date=test.end_date,
            participant_count=0,
            created_at=test.created_at,
            updated_at=test.updated_at,
            created_by=test.created_by,
            tags=test.tags,
            metadata=test.metadata,
        )

        _check_test_access(test_response, current_user)

        # Calculate analytics
        analytics_data = await ab_test_manager.calculate_test_analytics(
            test_id
        )
        if not analytics_data:
            raise InternalServerProblem(
                detail="Failed to calculate test analytics"
            )

        # Import schemas for response
        from chatter.schemas.ab_testing import (
            ABTestAnalyticsResponse,
            StatisticalAnalysis,
            VariantPerformance,
        )

        # Convert to response format
        variants = [
            VariantPerformance(**variant)
            for variant in analytics_data["variants"]
        ]

        statistical_analysis = StatisticalAnalysis(
            **analytics_data["statistical_analysis"]
        )

        return ABTestAnalyticsResponse(
            test_id=analytics_data["test_id"],
            test_name=analytics_data["test_name"],
            status=analytics_data["status"],
            total_participants=analytics_data["total_participants"],
            variants=variants,
            statistical_analysis=statistical_analysis,
            winner=analytics_data["winner"],
            improvement=analytics_data["improvement"],
            recommendation=analytics_data["recommendation"],
            duration_days=analytics_data["duration_days"],
            remaining_days=analytics_data["remaining_days"],
            progress_percentage=analytics_data["progress_percentage"],
            generated_at=analytics_data["generated_at"],
            last_updated=analytics_data["last_updated"],
        )

    except (NotFoundProblem, ForbiddenProblem):
        raise
    except Exception as e:
        logger.error(
            "Failed to get A/B test analytics",
            test_id=test_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to get A/B test analytics"
        ) from e
