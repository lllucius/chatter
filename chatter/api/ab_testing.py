"""A/B testing management endpoints."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, status

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.ab_testing import (
    ABTestActionResponse,
    ABTestCreateRequest,
    ABTestDeleteResponse,
    ABTestListRequest,
    ABTestListResponse,
    ABTestMetricsResponse,
    ABTestResponse,
    ABTestResultsResponse,
    ABTestUpdateRequest,
    TestStatus,
)
from chatter.services.ab_testing import MetricType
from chatter.services.ab_testing import ABTestManager
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    InternalServerProblem,
    NotFoundProblem,
)

logger = get_logger(__name__)
router = APIRouter()


async def get_ab_test_manager() -> ABTestManager:
    """Get A/B test manager instance.

    Returns:
        ABTestManager instance
    """
    from chatter.services.ab_testing import ab_test_manager
    return ab_test_manager


@router.post("/", response_model=ABTestResponse, status_code=status.HTTP_201_CREATED)
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
        # Convert request data to ABTest model format

        from chatter.services.ab_testing import ABTest, TestMetric
        from chatter.services.ab_testing import (
            TestVariant as ServiceTestVariant,
        )

        # Create variants
        variants = []
        for i, variant_data in enumerate(test_data.variants):
            variant = ServiceTestVariant(
                name=variant_data.name,
                description=variant_data.description,
                weight=variant_data.weight,
                configuration=variant_data.configuration,
                is_control=(i == 0),  # First variant is control
            )
            variants.append(variant)

        # Create primary metric from first metric in list
        primary_metric = TestMetric(
            name=test_data.metrics[0].value,
            metric_type=test_data.metrics[0],
        )

        # Create secondary metrics
        secondary_metrics = []
        for metric in test_data.metrics[1:]:
            secondary_metrics.append(TestMetric(
                name=metric.value,
                metric_type=metric,
            ))

        # Create test

        test_id = await ab_test_manager.create_test(
            name=test_data.name,
            description=test_data.description,
            test_type=test_data.test_type,
            variants=variants,
            primary_metric={
                "name": test_data.metrics[0].value,
                "metric_type": test_data.metrics[0].value,
            },
            created_by=current_user.username,
            secondary_metrics=[{
                "name": metric.value,
                "metric_type": metric.value,
            } for metric in test_data.metrics[1:]],
            allocation_strategy=test_data.allocation_strategy,
            traffic_percentage=test_data.traffic_percentage / 100.0,
            duration_days=test_data.duration_days,
            target_users=test_data.target_audience or {},
        )
        created_test = await ab_test_manager.get_test(test_id)

        if not created_test:
            raise InternalServerProblem(detail="Failed to retrieve created test")

        # Convert to response format
        from chatter.schemas.ab_testing import (
            TestVariant as ResponseTestVariant,
        )

        response_variants = []
        for variant in created_test.variants:
            response_variants.append(ResponseTestVariant(
                name=variant.name,
                description=variant.description,
                configuration=variant.configuration,
                weight=variant.weight,
            ))

        return ABTestResponse(
            id=created_test.id,
            name=created_test.name,
            description=created_test.description,
            test_type=created_test.test_type,
            status=created_test.status,
            allocation_strategy=created_test.allocation_strategy,
            variants=response_variants,
            metrics=test_data.metrics,
            duration_days=created_test.duration_days or test_data.duration_days,
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
        raise InternalServerProblem(detail="Failed to create A/B test") from e


@router.get("/", response_model=ABTestListResponse)
async def list_ab_tests(
    request: ABTestListRequest = Depends(),
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestListResponse:
    """List A/B tests with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        List of A/B tests
    """
    try:
        tests = await ab_test_manager.list_tests(
            status=request.status,
            test_type=request.test_type,
        )

        # Filter by tags if specified
        if request.tags:
            filtered_tests = []
            for test in tests:
                if any(tag in test.tags for tag in request.tags):
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
                response_variants.append(ResponseTestVariant(
                    name=variant.name,
                    description=variant.description,
                    configuration=variant.configuration,
                    weight=variant.weight,
                ))

            # Get metrics from test configuration
            metrics = [test.primary_metric.metric_type]
            metrics.extend([m.metric_type for m in test.secondary_metrics])

            test_responses.append(ABTestResponse(
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
            ))

        return ABTestListResponse(
            tests=test_responses,
            total=len(test_responses)
        )

    except Exception as e:
        logger.error("Failed to list A/B tests", error=str(e))
        raise InternalServerProblem(detail="Failed to list A/B tests") from e


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
            raise NotFoundProblem(detail=f"A/B test {test_id} not found")

        # Convert to response format
        from chatter.schemas.ab_testing import (
            TestVariant as ResponseTestVariant,
        )

        response_variants = []
        for variant in test.variants:
            response_variants.append(ResponseTestVariant(
                name=variant.name,
                description=variant.description,
                configuration=variant.configuration,
                weight=variant.weight,
            ))

        # Get metrics from test configuration
        metrics = [test.primary_metric.metric_type]
        metrics.extend([m.metric_type for m in test.secondary_metrics])

        return ABTestResponse(
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

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error("Failed to get A/B test", test_id=test_id, error=str(e))
        raise InternalServerProblem(detail="Failed to get A/B test") from e


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
            raise NotFoundProblem(detail=f"A/B test {test_id} not found")

        # Update test data
        update_data = test_data.model_dump(exclude_unset=True)

        # Convert traffic percentage back to decimal
        if "traffic_percentage" in update_data:
            update_data["traffic_percentage"] = update_data["traffic_percentage"] / 100.0

        updated_test = await ab_test_manager.update_test(test_id, update_data)
        if not updated_test:
            raise InternalServerProblem(detail="Failed to update A/B test")

        # Convert to response format (reuse logic from get_ab_test)
        from chatter.schemas.ab_testing import (
            TestVariant as ResponseTestVariant,
        )

        response_variants = []
        for variant in updated_test.variants:
            response_variants.append(ResponseTestVariant(
                name=variant.name,
                description=variant.description,
                configuration=variant.configuration,
                weight=variant.weight,
            ))

        metrics = [updated_test.primary_metric.metric_type]
        metrics.extend([m.metric_type for m in updated_test.secondary_metrics])

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
        logger.error("Failed to update A/B test", test_id=test_id, error=str(e))
        raise InternalServerProblem(detail="Failed to update A/B test") from e


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
            raise NotFoundProblem(detail=f"A/B test {test_id} not found")

        return ABTestDeleteResponse(
            success=True,
            message=f"A/B test {test_id} deleted successfully"
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error("Failed to delete A/B test", test_id=test_id, error=str(e))
        raise InternalServerProblem(detail="Failed to delete A/B test") from e


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
            raise BadRequestProblem(detail="Failed to start test - check test status and configuration")

        from chatter.services.ab_testing import TestStatus

        return ABTestActionResponse(
            success=True,
            message=f"A/B test {test_id} started successfully",
            test_id=test_id,
            new_status=TestStatus.RUNNING
        )

    except BadRequestProblem:
        raise
    except Exception as e:
        logger.error("Failed to start A/B test", test_id=test_id, error=str(e))
        raise InternalServerProblem(detail="Failed to start A/B test") from e


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
            raise BadRequestProblem(detail="Failed to pause test - check test status")

        from chatter.services.ab_testing import TestStatus

        return ABTestActionResponse(
            success=True,
            message=f"A/B test {test_id} paused successfully",
            test_id=test_id,
            new_status=TestStatus.PAUSED
        )

    except BadRequestProblem:
        raise
    except Exception as e:
        logger.error("Failed to pause A/B test", test_id=test_id, error=str(e))
        raise InternalServerProblem(detail="Failed to pause A/B test") from e


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
            raise BadRequestProblem(detail="Failed to complete test - check test status")

        from chatter.services.ab_testing import TestStatus

        return ABTestActionResponse(
            success=True,
            message=f"A/B test {test_id} completed successfully",
            test_id=test_id,
            new_status=TestStatus.COMPLETED
        )

    except BadRequestProblem:
        raise
    except Exception as e:
        logger.error("Failed to complete A/B test", test_id=test_id, error=str(e))
        raise InternalServerProblem(detail="Failed to complete A/B test") from e


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
            raise NotFoundProblem(detail=f"Results not available for test {test_id}")

        # Convert results to response format

        from chatter.schemas.ab_testing import TestMetric

        metrics = []
        for variant_name, variant_results in results.variant_results.items():
            for metric_name, metric_value in variant_results.items():
                # Map string metric name to MetricType enum
                try:
                    metric_type = MetricType(metric_name)
                except ValueError:
                    metric_type = MetricType.CUSTOM
                
                metrics.append(TestMetric(
                    metric_type=metric_type,
                    variant_name=variant_name,
                    value=float(metric_value),
                    sample_size=100,  # Placeholder
                    confidence_interval=None,
                ))

        # Convert confidence intervals to expected format
        confidence_intervals_formatted = {}
        for variant_id, intervals in results.confidence_intervals.items():
            confidence_intervals_formatted[variant_id] = {}
            for metric, value in intervals.items():
                # Convert single float to list of floats [lower, upper]
                if isinstance(value, (int, float)):
                    confidence_intervals_formatted[variant_id][metric] = [float(value), float(value)]
                else:
                    confidence_intervals_formatted[variant_id][metric] = [float(value), float(value)]

        return ABTestResultsResponse(
            test_id=test_id,
            test_name="Test Name",  # Would need to fetch from test
            status=TestStatus.COMPLETED,  # Would need to fetch from test
            metrics=metrics,
            statistical_significance=results.statistical_significance,
            confidence_intervals=confidence_intervals_formatted,
            winning_variant=None,  # Would be determined from analysis
            recommendation="Continue monitoring",  # Would be generated
            generated_at=results.analysis_date,
            sample_size=100,  # Would need to be calculated
            duration_days=7,  # Would need to be calculated
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error("Failed to get A/B test results", test_id=test_id, error=str(e))
        raise InternalServerProblem(detail="Failed to get A/B test results") from e


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
        # This would need to be implemented in the AB test manager
        # For now, return a placeholder response

        from chatter.schemas.ab_testing import TestMetric

        # Placeholder metrics
        metrics = [
            TestMetric(
                metric_type=MetricType.RESPONSE_TIME,
                variant_name="control",
                value=1.5,
                sample_size=50,
                confidence_interval=None,
            ),
            TestMetric(
                metric_type=MetricType.RESPONSE_TIME,
                variant_name="variant_a",
                value=1.2,
                sample_size=50,
                confidence_interval=None,
            ),
        ]

        return ABTestMetricsResponse(
            test_id=test_id,
            metrics=metrics,
            participant_count=100,
            last_updated=datetime.now(UTC),
        )

    except Exception as e:
        logger.error("Failed to get A/B test metrics", test_id=test_id, error=str(e))
        raise InternalServerProblem(detail="Failed to get A/B test metrics") from e


@router.post("/{test_id}/end", response_model=ABTestActionResponse)
async def end_ab_test(
    test_id: str,
    winner_variant: str,
    current_user: User = Depends(get_current_user),
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
) -> ABTestActionResponse:
    """End A/B test and declare winner.

    Args:
        test_id: A/B test ID
        winner_variant: Winning variant identifier
        current_user: Current authenticated user
        ab_test_manager: A/B test manager instance

    Returns:
        Action response
    """
    try:
        success = await ab_test_manager.end_test(test_id, winner_variant)

        if not success:
            raise NotFoundProblem(
                detail="A/B test not found or could not be ended",
                resource_type="ab_test",
                resource_id=test_id,
            ) from None

        return ABTestActionResponse(
            success=True,
            message=f"A/B test ended with winner: {winner_variant}",
            test_id=test_id,
            new_status=TestStatus.COMPLETED,
        )

    except Exception as e:
        logger.error("Failed to end A/B test", test_id=test_id, error=str(e))
        raise InternalServerProblem(detail="Failed to end A/B test") from e


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
        performance = await ab_test_manager.get_test_performance(test_id)

        if not performance:
            raise NotFoundProblem(
                detail="A/B test not found or no performance data available",
                resource_type="ab_test",
                resource_id=test_id,
            ) from None

        return performance

    except Exception as e:
        logger.error("Failed to get A/B test performance", test_id=test_id, error=str(e))
        raise InternalServerProblem(detail="Failed to get A/B test performance") from e
