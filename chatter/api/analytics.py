"""Analytics and statistics endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.core.analytics import AnalyticsService
from chatter.models.user import User
from chatter.schemas.analytics import (
    ConversationStatsRequest,
    ConversationStatsResponse,
    DashboardRequest,
    DashboardResponse,
    DocumentAnalyticsRequest,
    DocumentAnalyticsResponse,
    PerformanceMetricsRequest,
    PerformanceMetricsResponse,
    SystemAnalyticsRequest,
    SystemAnalyticsResponse,
    ToolServerAnalyticsRequest,
    UsageMetricsRequest,
    UsageMetricsResponse,
)
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger
from chatter.utils.problem import InternalServerProblem

logger = get_logger(__name__)
router = APIRouter()


async def get_analytics_service(
    session: AsyncSession = Depends(get_session)
) -> AnalyticsService:
    """Get analytics service instance."""
    return AnalyticsService(session)


@router.get("/conversations", response_model=ConversationStatsResponse)
async def get_conversation_stats(
    start_date: datetime | None = Query(None, description="Start date for analytics"),
    end_date: datetime | None = Query(None, description="End date for analytics"),
    period: str = Query("7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"),
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
        from chatter.schemas.analytics import AnalyticsTimeRange
        time_range = AnalyticsTimeRange(
            start_date=start_date,
            end_date=end_date,
            period=period,
        )
        
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
        )

    except Exception as e:
        logger.error("Failed to get conversation stats", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get conversation statistics"
        ) from e


@router.get("/usage", response_model=UsageMetricsResponse)
async def get_usage_metrics(
    start_date: datetime | None = Query(None, description="Start date for analytics"),
    end_date: datetime | None = Query(None, description="End date for analytics"),
    period: str = Query("7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"),
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
    start_date: datetime | None = Query(None, description="Start date for analytics"),
    end_date: datetime | None = Query(None, description="End date for analytics"),
    period: str = Query("7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"),
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
    start_date: datetime | None = Query(None, description="Start date for analytics"),
    end_date: datetime | None = Query(None, description="End date for analytics"),
    period: str = Query("7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"),
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


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    start_date: datetime | None = Query(None, description="Start date for analytics"),
    end_date: datetime | None = Query(None, description="End date for analytics"),
    period: str = Query("7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"),
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
            generated_at=dashboard_data.get(
                "generated_at", datetime.now(UTC)
            ),
        )

    except Exception as e:
        logger.error("Failed to get dashboard data", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get dashboard data"
        ) from e


@router.get("/toolservers")
async def get_tool_server_analytics(
    start_date: datetime | None = Query(None, description="Start date for analytics"),
    end_date: datetime | None = Query(None, description="End date for analytics"),
    period: str = Query("7d", description="Predefined period (1h, 24h, 7d, 30d, 90d)"),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> dict:
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
