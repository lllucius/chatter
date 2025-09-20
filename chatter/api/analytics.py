"""Analytics and statistics endpoints."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.api.real_time_analytics import router as real_time_router
from chatter.core.analytics import AnalyticsService
from chatter.models.user import User
from chatter.schemas.analytics import (
    AnalyticsExportResponse,
    AnalyticsHealthResponse,
    CacheStatusResponse,
    ChartReadyAnalytics,
    ConversationStatsResponse,
    DashboardResponse,
    DatabaseHealthResponse,
    DocumentAnalyticsResponse,
    IntegratedDashboardStats,
    MetricsSummaryResponse,
    PerformanceMetricsResponse,
    QueryAnalysisResponse,
    SystemAnalyticsResponse,
    ToolServerAnalyticsResponse,
    UsageMetricsResponse,
)
from chatter.schemas.common import SuccessResponse
from chatter.services.cache_warming import CacheWarmingService
from chatter.services.database_optimization import (
    DatabaseOptimizationService,
)
from chatter.utils.database import get_session_generator
from chatter.utils.logging import get_logger
from chatter.utils.problem import InternalServerProblem
from chatter.utils.unified_rate_limiter import rate_limit

logger = get_logger(__name__)
router = APIRouter()

# Include real-time analytics routes
router.include_router(
    real_time_router, prefix="/real-time", tags=["real-time-analytics"]
)


async def get_database_optimization_service(
    session: AsyncSession = Depends(get_session_generator),
) -> DatabaseOptimizationService:
    """Get database optimization service instance."""
    return DatabaseOptimizationService(session)


async def get_cache_warming_service(
    session: AsyncSession = Depends(get_session_generator),
) -> CacheWarmingService:
    """Get cache warming service instance."""
    return CacheWarmingService(session)


async def get_analytics_service(
    session: AsyncSession = Depends(get_session_generator),
) -> AnalyticsService:
    """Get analytics service instance."""
    return AnalyticsService(session)


@router.get("/conversations", response_model=ConversationStatsResponse)
@rate_limit(
    max_requests=20, window_seconds=60
)  # 20 requests per minute
async def get_conversation_stats(
    start_date: datetime | None = Query(
        None, description="Start date for analytics"
    ),
    end_date: datetime | None = Query(
        None, description="End date for analytics"
    ),
    period: str = Query(
        "7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"
    ),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> ConversationStatsResponse:
    """Get conversation statistics.

    Args:
        start_date: Start date for analytics
        end_date: End date for analytics
        period: Predefined period
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Conversation statistics
    """
    try:
        # Create time range object
        from pydantic import ValidationError

        from chatter.schemas.analytics import AnalyticsTimeRange

        try:
            time_range = AnalyticsTimeRange(
                start_date=start_date,
                end_date=end_date,
                period=period,
            )
        except ValidationError as ve:
            from chatter.utils.problem import BadRequestProblem

            raise BadRequestProblem(
                detail=f"Invalid time range parameters: {ve}"
            ) from ve

        stats = await analytics_service.get_conversation_stats(
            current_user.id, time_range
        )

        return ConversationStatsResponse(
            total_conversations=stats.get("total_conversations", 0),
            conversations_by_status=stats.get(
                "conversations_by_status", {}
            ),
            total_messages=stats.get("total_messages", 0),
            messages_by_role=stats.get("messages_by_role", {}),
            avg_messages_per_conversation=stats.get(
                "avg_messages_per_conversation", 0.0
            ),
            total_tokens_used=stats.get("total_tokens_used", 0),
            total_cost=stats.get("total_cost", 0.0),
            avg_response_time_ms=stats.get("avg_response_time_ms", 0.0),
            conversations_by_date=stats.get(
                "conversations_by_date", {}
            ),
            most_active_hours=stats.get("most_active_hours", {}),
            popular_models=stats.get("popular_models", {}),
            popular_providers=stats.get("popular_providers", {}),
            # Rating metrics
            total_ratings=stats.get("total_ratings", 0),
            avg_message_rating=stats.get("avg_message_rating", 0.0),
            messages_with_ratings=stats.get("messages_with_ratings", 0),
            rating_distribution=stats.get("rating_distribution", {}),
        )

    except Exception as e:
        logger.error("Failed to get conversation stats", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get conversation statistics"
        ) from e


@router.get("/usage", response_model=UsageMetricsResponse)
async def get_usage_metrics(
    start_date: datetime | None = Query(
        None, description="Start date for analytics"
    ),
    end_date: datetime | None = Query(
        None, description="End date for analytics"
    ),
    period: str = Query(
        "7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"
    ),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> UsageMetricsResponse:
    """Get usage metrics.

    Args:
        start_date: Start date for analytics
        end_date: End date for analytics
        period: Predefined period
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Usage metrics
    """
    try:
        # Create time range object
        from chatter.schemas.analytics import AnalyticsTimeRange

        time_range = AnalyticsTimeRange(
            start_date=start_date,
            end_date=end_date,
            period=period,
        )

        metrics = await analytics_service.get_usage_metrics(
            current_user.id, time_range
        )

        return UsageMetricsResponse(
            total_prompt_tokens=metrics.get("total_prompt_tokens", 0),
            total_completion_tokens=metrics.get(
                "total_completion_tokens", 0
            ),
            total_tokens=metrics.get("total_tokens", 0),
            tokens_by_model=metrics.get("tokens_by_model", {}),
            tokens_by_provider=metrics.get("tokens_by_provider", {}),
            total_cost=metrics.get("total_cost", 0.0),
            cost_by_model=metrics.get("cost_by_model", {}),
            cost_by_provider=metrics.get("cost_by_provider", {}),
            daily_usage=metrics.get("daily_usage", {}),
            daily_cost=metrics.get("daily_cost", {}),
            avg_response_time=metrics.get("avg_response_time", 0.0),
            response_times_by_model=metrics.get(
                "response_times_by_model", {}
            ),
            active_days=metrics.get("active_days", 0),
            peak_usage_hour=metrics.get("peak_usage_hour", 0),
            conversations_per_day=metrics.get(
                "conversations_per_day", 0.0
            ),
        )

    except Exception as e:
        logger.error("Failed to get usage metrics", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get usage metrics"
        ) from e


@router.get("/performance", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    start_date: datetime | None = Query(
        None, description="Start date for analytics"
    ),
    end_date: datetime | None = Query(
        None, description="End date for analytics"
    ),
    period: str = Query(
        "7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"
    ),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> PerformanceMetricsResponse:
    """Get performance metrics.

    Args:
        request: Performance metrics request parameters
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Performance metrics
    """
    try:
        # Create time range object
        from chatter.schemas.analytics import AnalyticsTimeRange

        time_range = AnalyticsTimeRange(
            start_date=start_date,
            end_date=end_date,
            period=period,
        )

        metrics = await analytics_service.get_performance_metrics(
            current_user.id, time_range
        )

        return PerformanceMetricsResponse(
            avg_response_time_ms=metrics.get(
                "avg_response_time_ms", 0.0
            ),
            median_response_time_ms=metrics.get(
                "median_response_time_ms", 0.0
            ),
            p95_response_time_ms=metrics.get(
                "p95_response_time_ms", 0.0
            ),
            p99_response_time_ms=metrics.get(
                "p99_response_time_ms", 0.0
            ),
            requests_per_minute=metrics.get("requests_per_minute", 0.0),
            tokens_per_minute=metrics.get("tokens_per_minute", 0.0),
            total_errors=metrics.get("total_errors", 0),
            error_rate=metrics.get("error_rate", 0.0),
            errors_by_type=metrics.get("errors_by_type", {}),
            performance_by_model=metrics.get(
                "performance_by_model", {}
            ),
            performance_by_provider=metrics.get(
                "performance_by_provider", {}
            ),
            database_response_time_ms=metrics.get(
                "database_response_time_ms", 0.0
            ),
            vector_search_time_ms=metrics.get(
                "vector_search_time_ms", 0.0
            ),
            embedding_generation_time_ms=metrics.get(
                "embedding_generation_time_ms", 0.0
            ),
        )

    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get performance metrics"
        ) from e


@router.get("/documents", response_model=DocumentAnalyticsResponse)
async def get_document_analytics(
    start_date: datetime | None = Query(
        None, description="Start date for analytics"
    ),
    end_date: datetime | None = Query(
        None, description="End date for analytics"
    ),
    period: str = Query(
        "7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"
    ),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> DocumentAnalyticsResponse:
    """Get document analytics.

    Args:
        request: Document analytics request parameters
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Document analytics
    """
    try:
        # Create time range object
        from chatter.schemas.analytics import AnalyticsTimeRange

        time_range = AnalyticsTimeRange(
            start_date=start_date,
            end_date=end_date,
            period=period,
        )

        analytics = await analytics_service.get_document_analytics(
            current_user.id, time_range
        )

        return DocumentAnalyticsResponse(
            total_documents=analytics.get("total_documents", 0),
            documents_by_status=analytics.get(
                "documents_by_status", {}
            ),
            documents_by_type=analytics.get("documents_by_type", {}),
            avg_processing_time_seconds=analytics.get(
                "avg_processing_time_seconds", 0.0
            ),
            processing_success_rate=analytics.get(
                "processing_success_rate", 0.0
            ),
            total_chunks=analytics.get("total_chunks", 0),
            avg_chunks_per_document=analytics.get(
                "avg_chunks_per_document", 0.0
            ),
            total_storage_bytes=analytics.get("total_storage_bytes", 0),
            avg_document_size_bytes=analytics.get(
                "avg_document_size_bytes", 0.0
            ),
            storage_by_type=analytics.get("storage_by_type", {}),
            total_searches=analytics.get("total_searches", 0),
            avg_search_results=analytics.get("avg_search_results", 0.0),
            popular_search_terms=analytics.get(
                "popular_search_terms", {}
            ),
            total_views=analytics.get("total_views", 0),
            most_viewed_documents=analytics.get(
                "most_viewed_documents", []
            ),
            documents_by_access_level=analytics.get(
                "documents_by_access_level", {}
            ),
        )

    except Exception as e:
        logger.error("Failed to get document analytics", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get document analytics"
        ) from e


@router.get("/system", response_model=SystemAnalyticsResponse)
async def get_system_analytics(
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> SystemAnalyticsResponse:
    """Get system analytics.

    Args:
        request: System analytics request parameters
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        System analytics
    """
    try:
        analytics = await analytics_service.get_system_analytics()

        return SystemAnalyticsResponse(
            total_users=analytics.get("total_users", 0),
            active_users_today=analytics.get("active_users_today", 0),
            active_users_week=analytics.get("active_users_week", 0),
            active_users_month=analytics.get("active_users_month", 0),
            system_uptime_seconds=analytics.get(
                "system_uptime_seconds", 0.0
            ),
            avg_cpu_usage=analytics.get("avg_cpu_usage", 0.0),
            avg_memory_usage=analytics.get("avg_memory_usage", 0.0),
            database_connections=analytics.get(
                "database_connections", 0
            ),
            total_api_requests=analytics.get("total_api_requests", 0),
            requests_per_endpoint=analytics.get(
                "requests_per_endpoint", {}
            ),
            avg_api_response_time=analytics.get(
                "avg_api_response_time", 0.0
            ),
            api_error_rate=analytics.get("api_error_rate", 0.0),
            storage_usage_bytes=analytics.get("storage_usage_bytes", 0),
            vector_database_size_bytes=analytics.get(
                "vector_database_size_bytes", 0
            ),
            cache_hit_rate=analytics.get("cache_hit_rate", 0.0),
        )

    except Exception as e:
        logger.error("Failed to get system analytics", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get system analytics"
        ) from e


@router.get("/dashboard/chart-data", response_model=ChartReadyAnalytics)
@rate_limit(
    max_requests=20, window_seconds=60
)  # 20 requests per minute
async def get_dashboard_chart_data(
    start_date: datetime | None = Query(
        None, description="Start date for analytics"
    ),
    end_date: datetime | None = Query(
        None, description="End date for analytics"
    ),
    period: str = Query(
        "7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"
    ),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> ChartReadyAnalytics:
    """Get chart-ready analytics data for dashboard visualization.

    Args:
        start_date: Start date for analytics
        end_date: End date for analytics
        period: Predefined period
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Chart-ready analytics data
    """
    try:
        # Create time range object
        from pydantic import ValidationError

        from chatter.schemas.analytics import AnalyticsTimeRange

        try:
            time_range = AnalyticsTimeRange(
                start_date=start_date,
                end_date=end_date,
                period=period,
            )
        except ValidationError as ve:
            from chatter.utils.problem import BadRequestProblem

            raise BadRequestProblem(
                detail=f"Invalid time range parameters: {ve}"
            ) from ve

        chart_data = await analytics_service.get_chart_ready_data(
            current_user.id, time_range
        )

        # Convert the dictionary to ChartReadyAnalytics object
        return ChartReadyAnalytics(**chart_data)

    except Exception as e:
        logger.error(f"Error getting chart data: {e}")
        from chatter.utils.problem import InternalServerProblem

        raise InternalServerProblem(
            detail="Failed to retrieve chart data"
        ) from e


@router.get(
    "/dashboard/integrated", response_model=IntegratedDashboardStats
)
@rate_limit(
    max_requests=20, window_seconds=60
)  # 20 requests per minute
async def get_integrated_dashboard_stats(
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> IntegratedDashboardStats:
    """Get integrated dashboard statistics.

    Args:
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Integrated dashboard statistics
    """
    try:
        stats = await analytics_service.get_integrated_dashboard_stats(
            current_user.id
        )
        return stats

    except Exception as e:
        logger.error(f"Error getting integrated dashboard stats: {e}")
        from chatter.utils.problem import InternalServerProblem

        raise InternalServerProblem(
            detail="Failed to retrieve integrated dashboard stats"
        ) from e


@router.get("/dashboard", response_model=DashboardResponse)
@rate_limit(
    max_requests=10, window_seconds=60
)  # 10 dashboard requests per minute
async def get_dashboard(
    start_date: datetime | None = Query(
        None, description="Start date for analytics"
    ),
    end_date: datetime | None = Query(
        None, description="End date for analytics"
    ),
    period: str = Query(
        "7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"
    ),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> DashboardResponse:
    """Get comprehensive dashboard data.

    Args:
        request: Dashboard request parameters
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Complete dashboard data
    """
    try:
        # Create time range object
        from chatter.schemas.analytics import AnalyticsTimeRange

        time_range = AnalyticsTimeRange(
            start_date=start_date,
            end_date=end_date,
            period=period,
        )

        dashboard_data = await analytics_service.get_dashboard_data(
            current_user.id, time_range
        )

        # Get chart-ready data as well
        chart_data = await analytics_service.get_chart_ready_data(
            current_user.id, time_range
        )

        return DashboardResponse(
            conversation_stats=ConversationStatsResponse(
                **dashboard_data.get("conversation_stats", {})
            ),
            usage_metrics=UsageMetricsResponse(
                **dashboard_data.get("usage_metrics", {})
            ),
            performance_metrics=PerformanceMetricsResponse(
                **dashboard_data.get("performance_metrics", {})
            ),
            document_analytics=DocumentAnalyticsResponse(
                **dashboard_data.get("document_analytics", {})
            ),
            system_health=SystemAnalyticsResponse(
                **dashboard_data.get("system_health", {})
            ),
            custom_metrics=dashboard_data.get("custom_metrics", []),
            chart_data=ChartReadyAnalytics(**chart_data),
            generated_at=dashboard_data.get(
                "generated_at", datetime.now(UTC)
            ),
        )

    except Exception as e:
        logger.error("Failed to get dashboard data", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get dashboard data"
        ) from e


@router.get("/toolservers", response_model=ToolServerAnalyticsResponse)
async def get_tool_server_analytics(
    start_date: datetime | None = Query(
        None, description="Start date for analytics"
    ),
    end_date: datetime | None = Query(
        None, description="End date for analytics"
    ),
    period: str = Query(
        "7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"
    ),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> dict[str, Any]:
    """Get tool server analytics.

    Args:
        request: Tool server analytics request parameters
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Tool server analytics data
    """
    try:
        # Create time range object
        from chatter.schemas.analytics import AnalyticsTimeRange

        time_range = AnalyticsTimeRange(
            start_date=start_date,
            end_date=end_date,
            period=period,
        )

        return await analytics_service.get_tool_server_analytics(
            current_user.id, time_range
        )

    except Exception as e:
        logger.error(
            "Failed to get tool server analytics", error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to get tool server analytics"
        ) from e


@router.get("/users/{user_id}", response_model=dict)
async def get_user_analytics(
    user_id: str,
    start_date: datetime | None = Query(
        None, description="Start date for analytics"
    ),
    end_date: datetime | None = Query(
        None, description="End date for analytics"
    ),
    period: str = Query(
        "7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"
    ),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> dict[str, Any]:
    """Get per-user analytics.

    Args:
        user_id: User ID
        start_date: Start date for analytics
        end_date: End date for analytics
        period: Predefined period
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        User-specific analytics
    """
    try:
        # Authorization check: users can only access their own analytics
        # unless they are admin (assuming is_admin field exists)
        if current_user.id != user_id and not getattr(
            current_user, "is_admin", False
        ):
            from chatter.utils.problem import ForbiddenProblem

            raise ForbiddenProblem(
                detail="Access denied: You can only view your own analytics"
            )

        # Validate user_id format (assuming it follows ULID format)
        if not user_id or len(user_id) != 26:
            from chatter.utils.problem import BadRequestProblem

            raise BadRequestProblem(detail="Invalid user ID format")

        # Create time range object
        from chatter.schemas.analytics import AnalyticsTimeRange

        time_range = AnalyticsTimeRange(
            start_date=start_date,
            end_date=end_date,
            period=period,
        )

        return await analytics_service.get_user_analytics(
            user_id, time_range.start_date, time_range.end_date
        )

    except Exception as e:
        logger.error("Failed to get user analytics", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get user analytics"
        ) from e


@router.post("/export", response_model=AnalyticsExportResponse)
@rate_limit(
    max_requests=5, window_seconds=300
)  # 5 exports per 5 minutes
async def export_analytics(
    format: str = Query(
        "json", description="Export format (json, csv, xlsx)"
    ),
    metrics: list[str] = Query(
        ..., description="List of metrics to export"
    ),
    start_date: datetime | None = Query(
        None, description="Start date for analytics"
    ),
    end_date: datetime | None = Query(
        None, description="End date for analytics"
    ),
    period: str = Query(
        "7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"
    ),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
):
    """Export analytics reports.

    Args:
        format: Export format
        metrics: List of metrics to export
        start_date: Start date for analytics
        end_date: End date for analytics
        period: Predefined period
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Exported analytics report
    """
    try:
        from fastapi.responses import StreamingResponse
        from pydantic import ValidationError

        # Validate export parameters first
        try:
            # Create time range object
            from chatter.schemas.analytics import AnalyticsTimeRange

            time_range = AnalyticsTimeRange(
                start_date=start_date,
                end_date=end_date,
                period=period,
            )

            # Validate the export request
            from chatter.schemas.analytics import AnalyticsExportRequest

            AnalyticsExportRequest(
                metrics=metrics,
                time_range=time_range,
                format=format,
                include_raw_data=False,
            )

        except ValidationError as ve:
            from chatter.utils.problem import BadRequestProblem

            raise BadRequestProblem(
                detail=f"Invalid export parameters: {ve}"
            ) from ve

        # Convert time range to tuple, handling None values
        date_range = None
        if time_range.start_date and time_range.end_date:
            date_range = (time_range.start_date, time_range.end_date)

        export_data = await analytics_service.export_analytics(
            format,
            date_range,
            {"user_id": current_user.id, "metrics": metrics},
        )

        if format == "json":
            return export_data
        elif format == "csv":
            return StreamingResponse(
                export_data,
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=analytics.csv"
                },
            )
        else:
            return StreamingResponse(
                export_data,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": "attachment; filename=analytics.xlsx"
                },
            )

    except Exception as e:
        logger.error("Failed to export analytics", error=str(e))
        raise InternalServerProblem(
            detail="Failed to export analytics"
        ) from e


@router.get("/health", response_model=AnalyticsHealthResponse)
async def get_analytics_health(
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> dict[str, Any]:
    """Get analytics system health status.

    Returns:
        Health check results for analytics system
    """
    try:
        return await analytics_service.get_analytics_health_check()
    except Exception as e:
        logger.error("Failed to get analytics health", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@router.get("/metrics/summary", response_model=MetricsSummaryResponse)
@rate_limit(
    max_requests=30, window_seconds=60
)  # 30 requests per minute
async def get_analytics_metrics_summary(
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> dict[str, Any]:
    """Get summary of key analytics metrics for monitoring.

    Returns:
        Summary of analytics metrics
    """
    try:
        return await analytics_service.get_analytics_metrics_summary()
    except Exception as e:
        logger.error(
            "Failed to get analytics metrics summary", error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to get analytics metrics summary"
        ) from e


@router.post("/cache/warm", response_model=SuccessResponse)
@rate_limit(
    max_requests=2, window_seconds=300
)  # 2 warming requests per 5 minutes
async def warm_analytics_cache(
    force_refresh: bool = False,
    current_user: User = Depends(get_current_user),
    cache_warming_service: CacheWarmingService = Depends(
        get_cache_warming_service
    ),
) -> dict[str, Any]:
    """Warm analytics cache to improve performance.

    Args:
        force_refresh: Force refresh of existing cache entries
        current_user: Current authenticated user
        cache_warming_service: Cache warming service

    Returns:
        Cache warming results
    """
    try:
        # Check if user has admin permissions (you may want to implement proper admin check)
        if not getattr(current_user, "is_admin", False):
            from chatter.utils.problem import ForbiddenProblem

            raise ForbiddenProblem(
                detail="Admin access required for cache warming"
            )

        logger.info(
            f"Starting cache warming initiated by user {current_user.id}"
        )

        warming_results = (
            await cache_warming_service.warm_analytics_cache(
                force_refresh
            )
        )

        return {
            "message": "Cache warming completed",
            "results": warming_results,
            "initiated_by": current_user.id,
        }

    except Exception as e:
        logger.error(f"Cache warming failed: {e}")
        raise InternalServerProblem(
            detail="Failed to warm cache"
        ) from e


@router.get("/cache/status", response_model=CacheStatusResponse)
@rate_limit(
    max_requests=10, window_seconds=60
)  # 10 requests per minute
async def get_cache_warming_status(
    current_user: User = Depends(get_current_user),
    cache_warming_service: CacheWarmingService = Depends(
        get_cache_warming_service
    ),
) -> dict[str, Any]:
    """Get cache warming status and performance metrics.

    Args:
        current_user: Current authenticated user
        cache_warming_service: Cache warming service

    Returns:
        Cache warming status and metrics
    """
    try:
        status = await cache_warming_service.get_cache_warming_status()
        return status

    except Exception as e:
        logger.error(f"Failed to get cache warming status: {e}")
        raise InternalServerProblem(
            detail="Failed to get cache status"
        ) from e


@router.post("/cache/optimize", response_model=SuccessResponse)
@rate_limit(
    max_requests=3, window_seconds=600
)  # 3 optimization requests per 10 minutes
async def optimize_cache_performance(
    current_user: User = Depends(get_current_user),
    cache_warming_service: CacheWarmingService = Depends(
        get_cache_warming_service
    ),
) -> dict[str, Any]:
    """Analyze and optimize cache performance automatically.

    Args:
        current_user: Current authenticated user
        cache_warming_service: Cache warming service

    Returns:
        Optimization results and recommendations
    """
    try:
        # Check if user has admin permissions
        if not getattr(current_user, "is_admin", False):
            from chatter.utils.problem import ForbiddenProblem

            raise ForbiddenProblem(
                detail="Admin access required for cache optimization"
            )

        logger.info(
            f"Cache optimization initiated by user {current_user.id}"
        )

        optimization_results = (
            await cache_warming_service.optimize_cache_performance()
        )

        return {
            "message": "Cache optimization completed",
            "results": optimization_results,
            "initiated_by": current_user.id,
        }

    except Exception as e:
        logger.error(f"Cache optimization failed: {e}")
        raise InternalServerProblem(
            detail="Failed to optimize cache"
        ) from e


@router.post("/cache/invalidate", response_model=SuccessResponse)
@rate_limit(
    max_requests=5, window_seconds=300
)  # 5 invalidation requests per 5 minutes
async def invalidate_stale_cache(
    max_age_hours: int = 24,
    current_user: User = Depends(get_current_user),
    cache_warming_service: CacheWarmingService = Depends(
        get_cache_warming_service
    ),
) -> dict[str, Any]:
    """Invalidate stale cache entries to free up memory.

    Args:
        max_age_hours: Maximum age in hours for cache entries to keep
        current_user: Current authenticated user
        cache_warming_service: Cache warming service

    Returns:
        Cache invalidation results
    """
    try:
        # Check if user has admin permissions
        if not getattr(current_user, "is_admin", False):
            from chatter.utils.problem import ForbiddenProblem

            raise ForbiddenProblem(
                detail="Admin access required for cache invalidation"
            )

        # Validate max_age_hours
        if max_age_hours < 1 or max_age_hours > 168:  # 1 hour to 1 week
            from chatter.utils.problem import BadRequestProblem

            raise BadRequestProblem(
                detail="max_age_hours must be between 1 and 168"
            )

        logger.info(
            f"Cache invalidation initiated by user {current_user.id}, max_age={max_age_hours}h"
        )

        invalidation_results = (
            await cache_warming_service.invalidate_stale_cache_entries(
                max_age_hours
            )
        )

        return {
            "message": "Cache invalidation completed",
            "results": invalidation_results,
            "max_age_hours": max_age_hours,
            "initiated_by": current_user.id,
        }

    except Exception as e:
        logger.error(f"Cache invalidation failed: {e}")
        raise InternalServerProblem(
            detail="Failed to invalidate cache"
        ) from e


@router.get("/performance/detailed", response_model=PerformanceMetricsResponse)
@rate_limit(
    max_requests=20, window_seconds=60
)  # 20 requests per minute
async def get_detailed_performance_metrics(
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> dict[str, Any]:
    """Get detailed performance metrics for analytics service.

    Args:
        current_user: Current authenticated user
        analytics_service: Analytics service

    Returns:
        Detailed performance metrics
    """
    try:
        performance_metrics = (
            await analytics_service.get_analytics_performance_metrics()
        )

        return {
            "message": "Performance metrics retrieved successfully",
            "metrics": performance_metrics,
            "retrieved_by": current_user.id,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get detailed performance metrics: {e}")
        raise InternalServerProblem(
            detail="Failed to retrieve performance metrics"
        ) from e


@router.get("/database/health", response_model=DatabaseHealthResponse)
@rate_limit(
    max_requests=10, window_seconds=60
)  # 10 requests per minute
async def get_database_health_metrics(
    current_user: User = Depends(get_current_user),
    db_optimization_service: DatabaseOptimizationService = Depends(
        get_database_optimization_service
    ),
) -> dict[str, Any]:
    """Get comprehensive database health metrics for analytics.

    Args:
        current_user: Current authenticated user
        db_optimization_service: Database optimization service

    Returns:
        Database health metrics and recommendations
    """
    try:
        health_metrics = (
            await db_optimization_service.get_database_health_metrics()
        )

        return {
            "message": "Database health metrics retrieved successfully",
            "health_metrics": health_metrics,
            "retrieved_by": current_user.id,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get database health metrics: {e}")
        raise InternalServerProblem(
            detail="Failed to retrieve database health metrics"
        ) from e


@router.post("/database/analyze-queries", response_model=QueryAnalysisResponse)
@rate_limit(
    max_requests=5, window_seconds=300
)  # 5 analysis requests per 5 minutes
async def analyze_query_performance(
    query_type: str = None,
    current_user: User = Depends(get_current_user),
    db_optimization_service: DatabaseOptimizationService = Depends(
        get_database_optimization_service
    ),
) -> dict[str, Any]:
    """Analyze performance of analytics database queries.

    Args:
        query_type: Specific query type to analyze (optional)
        current_user: Current authenticated user
        db_optimization_service: Database optimization service

    Returns:
        Query performance analysis and optimization recommendations
    """
    try:
        # Check if user has admin permissions for detailed analysis
        if not getattr(current_user, "is_admin", False):
            from chatter.utils.problem import ForbiddenProblem

            raise ForbiddenProblem(
                detail="Admin access required for query analysis"
            )

        logger.info(
            f"Query performance analysis initiated by user {current_user.id}"
        )

        analysis_results = (
            await db_optimization_service.analyze_query_performance(
                query_type
            )
        )

        return {
            "message": "Query performance analysis completed",
            "analysis": analysis_results,
            "query_type_filter": query_type,
            "initiated_by": current_user.id,
        }

    except Exception as e:
        logger.error(f"Query performance analysis failed: {e}")
        raise InternalServerProblem(
            detail="Failed to analyze query performance"
        ) from e
