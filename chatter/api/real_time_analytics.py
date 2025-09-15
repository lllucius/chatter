"""Enhanced real-time analytics API endpoints for Phase 4 features."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_admin_user, get_current_user
from chatter.utils.database import get_session_generator
from chatter.models.user import User
from chatter.schemas.analytics import SystemAnalyticsResponse
from chatter.services.intelligent_search import (
    get_intelligent_search_service,
)
from chatter.services.real_time_analytics import (
    get_real_time_analytics_service,
)
from chatter.utils.logging import get_logger
from chatter.utils.unified_rate_limiter import (
    RateLimitExceeded,
    get_unified_rate_limiter,
)

logger = get_logger(__name__)
router = APIRouter()


@router.post("/real-time/dashboard/start")
async def start_real_time_dashboard(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict:
    """Start real-time dashboard updates for the current user.

    This endpoint initiates a background task that streams analytics data
    to the user via Server-Sent Events (SSE).
    """
    # Rate limit real-time dashboard requests
    rate_limiter = get_unified_rate_limiter()
    try:
        await rate_limiter.check_rate_limit(
            user_id=current_user.id,
            category="real_time_dashboard",
            action="start",
        )
    except RateLimitExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))

    real_time_service = get_real_time_analytics_service(session)

    # Start real-time updates in background
    background_tasks.add_task(
        real_time_service.start_real_time_dashboard, current_user.id
    )

    logger.info(
        f"Started real-time dashboard for user {current_user.id}"
    )
    return {
        "status": "started",
        "user_id": current_user.id,
        "message": "Real-time dashboard updates have been initiated. Connect to /events/stream to receive updates.",
    }


@router.post("/real-time/dashboard/stop")
async def stop_real_time_dashboard(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict:
    """Stop real-time dashboard updates for the current user."""
    real_time_service = get_real_time_analytics_service(session)

    await real_time_service.stop_real_time_dashboard(current_user.id)

    logger.info(
        f"Stopped real-time dashboard for user {current_user.id}"
    )
    return {
        "status": "stopped",
        "user_id": current_user.id,
        "message": "Real-time dashboard updates have been stopped.",
    }


@router.get("/user-behavior/{user_id}")
async def get_user_behavior_analytics(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict:
    """Get personalized behavior analytics for a user.

    Users can only access their own analytics unless they are admin.
    """
    # Check authorization
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Users can only access their own behavior analytics",
        )

    # Rate limit user behavior requests
    rate_limiter = get_unified_rate_limiter()
    try:
        await rate_limiter.check_rate_limit(
            user_id=current_user.id,
            category="user_behavior",
            action="get_analytics",
            max_requests=20,  # 20 requests per hour
            window_seconds=3600,
        )
    except RateLimitExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))

    real_time_service = get_real_time_analytics_service(session)
    analytics = await real_time_service.get_user_behavior_analytics(
        user_id
    )

    return analytics


@router.get("/search/intelligent")
async def intelligent_search(
    query: str,
    search_type: str = "documents",
    limit: int = 10,
    include_recommendations: bool = True,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict:
    """Perform intelligent semantic search with personalized results.

    Args:
        query: Search query string
        search_type: Type of content to search ("documents", "conversations", "prompts")
        limit: Maximum number of results to return
        include_recommendations: Whether to include search recommendations
    """
    # Validate search parameters
    if not query.strip():
        raise HTTPException(
            status_code=400, detail="Query cannot be empty"
        )

    if search_type not in ["documents", "conversations", "prompts"]:
        raise HTTPException(
            status_code=400,
            detail="search_type must be one of: documents, conversations, prompts",
        )

    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=400, detail="limit must be between 1 and 50"
        )

    # Rate limit search requests
    rate_limiter = get_unified_rate_limiter()
    try:
        await rate_limiter.check_rate_limit(
            user_id=current_user.id,
            category="intelligent_search",
            action="search",
            max_requests=100,  # 100 searches per hour
            window_seconds=3600,
        )
    except RateLimitExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))

    search_service = get_intelligent_search_service(session)

    try:
        results = await search_service.semantic_search(
            query=query,
            user_id=current_user.id,
            search_type=search_type,
            limit=limit,
            include_recommendations=include_recommendations,
        )

        logger.info(
            f"Intelligent search completed for user {current_user.id}: '{query}'"
        )
        return results

    except Exception as e:
        logger.error(f"Error in intelligent search: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during search. Please try again.",
        )


@router.get("/search/trending")
async def get_trending_content(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict:
    """Get trending content personalized for the current user."""
    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=400, detail="limit must be between 1 and 20"
        )

    # Rate limit trending content requests
    rate_limiter = get_unified_rate_limiter()
    try:
        await rate_limiter.check_rate_limit(
            user_id=current_user.id,
            category="trending_content",
            action="get",
            max_requests=30,  # 30 requests per hour
            window_seconds=3600,
        )
    except RateLimitExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))

    search_service = get_intelligent_search_service(session)
    trending = await search_service.get_trending_content(
        current_user.id, limit
    )

    return {
        "trending_content": trending,
        "user_id": current_user.id,
        "generated_at": SystemAnalyticsResponse.model_fields[
            "generated_at"
        ]
        .default_factory()
        .isoformat(),
    }


@router.post("/real-time/workflow/{workflow_id}/update")
async def send_workflow_update(
    workflow_id: str,
    update_type: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict:
    """Send a real-time workflow update to the user."""
    # Validate update type
    valid_update_types = [
        "status_change",
        "progress_update",
        "completion",
        "error",
    ]
    if update_type not in valid_update_types:
        raise HTTPException(
            status_code=400,
            detail=f"update_type must be one of: {', '.join(valid_update_types)}",
        )

    # Rate limit workflow updates
    rate_limiter = get_unified_rate_limiter()
    try:
        await rate_limiter.check_rate_limit(
            user_id=current_user.id,
            category="workflow_updates",
            action="send",
            max_requests=50,  # 50 updates per hour
            window_seconds=3600,
        )
    except RateLimitExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))

    real_time_service = get_real_time_analytics_service(session)

    await real_time_service.send_workflow_update(
        workflow_id=workflow_id,
        user_id=current_user.id,
        update_type=update_type,
        data=data,
    )

    return {
        "status": "sent",
        "workflow_id": workflow_id,
        "update_type": update_type,
        "user_id": current_user.id,
    }


@router.post("/real-time/system-health")
async def send_system_health_update(
    health_data: dict,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict:
    """Send system health update to all admin users.

    This endpoint is admin-only and broadcasts health information
    to all connected administrators.
    """
    # Rate limit system health updates
    rate_limiter = get_unified_rate_limiter()
    try:
        await rate_limiter.check_rate_limit(
            user_id=current_user.id,
            category="system_health",
            action="broadcast",
            max_requests=20,  # 20 broadcasts per hour
            window_seconds=3600,
        )
    except RateLimitExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))

    real_time_service = get_real_time_analytics_service(session)

    await real_time_service.send_system_health_update(health_data)

    logger.info(
        f"System health update broadcasted by admin {current_user.id}"
    )
    return {
        "status": "broadcasted",
        "admin_id": current_user.id,
        "health_severity": real_time_service._determine_health_severity(
            health_data
        ),
    }


@router.post("/real-time/cleanup")
async def cleanup_inactive_tasks(
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session_generator),
) -> dict:
    """Clean up inactive real-time tasks.

    This endpoint is admin-only and performs maintenance on the
    real-time analytics service.
    """
    real_time_service = get_real_time_analytics_service(session)

    await real_time_service.cleanup_inactive_tasks()

    logger.info(
        f"Real-time task cleanup performed by admin {current_user.id}"
    )
    return {
        "status": "completed",
        "admin_id": current_user.id,
        "message": "Inactive real-time tasks have been cleaned up",
    }
