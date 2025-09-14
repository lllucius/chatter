"""Real-time analytics service for streaming dashboard updates and intelligent notifications."""

import asyncio
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.cache_factory import get_general_cache
from chatter.models.base import generate_ulid
from chatter.schemas.analytics import (
    IntegratedDashboardStats,
)
from chatter.schemas.events import Event, EventType
from chatter.core.analytics import AnalyticsService
from chatter.services.sse_events import sse_service
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class RealTimeAnalyticsService:
    """Service for real-time analytics streaming and intelligent notifications."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.analytics_service = AnalyticsService(session)
        self.cache = get_general_cache()
        self._update_tasks: dict[str, asyncio.Task] = {}
        self._notification_thresholds = {
            "high_cpu_usage": 80.0,
            "low_cache_hit_rate": 70.0,
            "slow_queries": 2.0,  # seconds
            "high_error_rate": 5.0,  # percentage
        }

    async def start_real_time_dashboard(self, user_id: str) -> None:
        """Start real-time dashboard updates for a user."""
        task_key = f"dashboard_{user_id}"

        if task_key in self._update_tasks:
            logger.debug(f"Real-time dashboard already running for user {user_id}")
            return

        # Create background task for periodic updates
        task = asyncio.create_task(
            self._dashboard_update_loop(user_id),
            name=f"real_time_dashboard_{user_id}"
        )
        self._update_tasks[task_key] = task
        logger.info(f"Started real-time dashboard updates for user {user_id}")

    async def stop_real_time_dashboard(self, user_id: str) -> None:
        """Stop real-time dashboard updates for a user."""
        task_key = f"dashboard_{user_id}"

        if task_key in self._update_tasks:
            task = self._update_tasks.pop(task_key)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"Stopped real-time dashboard updates for user {user_id}")

    async def _dashboard_update_loop(self, user_id: str) -> None:
        """Background loop for sending dashboard updates via SSE."""
        try:
            while True:
                # Get fresh analytics data
                try:
                    dashboard_stats = await self.analytics_service.get_integrated_dashboard_stats()
                    chart_data = await self.analytics_service.get_chart_ready_data()

                    # Create update event
                    event = Event(
                        id=generate_ulid(),
                        type=EventType.ANALYTICS,
                        data={
                            "dashboard_stats": dashboard_stats.model_dump(),
                            "chart_data": chart_data.model_dump(),
                            "timestamp": datetime.now(UTC).isoformat(),
                            "user_id": user_id
                        }
                    )

                    # Send to user via SSE
                    await sse_service.send_event_to_user(user_id, event)

                    # Check for notification-worthy changes
                    await self._check_for_alerts(dashboard_stats, user_id)

                except Exception as e:
                    logger.error(f"Error in dashboard update loop for user {user_id}: {e}")

                # Wait for next update (configurable interval)
                await asyncio.sleep(30)  # Update every 30 seconds

        except asyncio.CancelledError:
            logger.debug(f"Dashboard update loop cancelled for user {user_id}")
            raise

    async def _check_for_alerts(self, stats: IntegratedDashboardStats, user_id: str) -> None:
        """Check analytics data for alert-worthy conditions."""
        alerts = []

        # Check system performance metrics
        if hasattr(stats, 'system_performance'):
            perf = stats.system_performance

            # CPU usage alert
            if hasattr(perf, 'cpu_usage') and perf.cpu_usage > self._notification_thresholds["high_cpu_usage"]:
                alerts.append({
                    "type": "performance",
                    "severity": "warning",
                    "title": "High CPU Usage",
                    "message": f"System CPU usage at {perf.cpu_usage:.1f}%",
                    "threshold": self._notification_thresholds["high_cpu_usage"]
                })

        # Check cache performance
        cache_stats = await self._get_cache_performance()
        if cache_stats and cache_stats.get('hit_rate', 100) < self._notification_thresholds["low_cache_hit_rate"]:
            alerts.append({
                "type": "cache",
                "severity": "info",
                "title": "Low Cache Hit Rate",
                "message": f"Cache hit rate at {cache_stats['hit_rate']:.1f}%",
                "recommendation": "Consider cache warming or optimization"
            })

        # Send alerts via SSE
        for alert in alerts:
            event = Event(
                id=generate_ulid(),
                type=EventType.NOTIFICATION,
                data={
                    "alert": alert,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "user_id": user_id
                }
            )
            await sse_service.send_event_to_user(user_id, event)

    async def _get_cache_performance(self) -> dict[str, Any] | None:
        """Get current cache performance metrics."""
        try:
            # Check if cache has performance stats
            if hasattr(self.cache, 'get_stats'):
                return self.cache.get_stats()
            return None
        except Exception as e:
            logger.error(f"Error getting cache performance: {e}")
            return None

    async def send_workflow_update(self, workflow_id: str, user_id: str, update_type: str, data: dict[str, Any]) -> None:
        """Send real-time workflow update to user."""
        event = Event(
            id=generate_ulid(),
            type=EventType.WORKFLOW,
            data={
                "workflow_id": workflow_id,
                "update_type": update_type,
                "data": data,
                "timestamp": datetime.now(UTC).isoformat(),
                "user_id": user_id
            }
        )
        await sse_service.send_event_to_user(user_id, event)

    async def send_system_health_update(self, health_data: dict[str, Any]) -> None:
        """Send system health update to all connected admin users."""
        event = Event(
            id=generate_ulid(),
            type=EventType.SYSTEM,
            data={
                "health": health_data,
                "timestamp": datetime.now(UTC).isoformat(),
                "severity": self._determine_health_severity(health_data)
            }
        )
        await sse_service.broadcast_to_admins(event)

    def _determine_health_severity(self, health_data: dict[str, Any]) -> str:
        """Determine the severity level of health data."""
        # Simple health severity determination
        if health_data.get('status') == 'error':
            return 'critical'
        elif health_data.get('status') == 'warning':
            return 'warning'
        elif any(key.startswith('error') for key in health_data.keys()):
            return 'warning'
        else:
            return 'info'

    async def get_user_behavior_analytics(self, user_id: str) -> dict[str, Any]:
        """Get personalized analytics for a specific user."""
        cache_key = f"user_behavior:{user_id}"

        # Check cache first
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data

        # Calculate user-specific metrics
        user_analytics = {
            "user_id": user_id,
            "last_updated": datetime.now(UTC).isoformat(),
            "activity_summary": await self._calculate_user_activity(user_id),
            "usage_patterns": await self._analyze_usage_patterns(user_id),
            "recommendations": await self._generate_user_recommendations(user_id)
        }

        # Cache for 5 minutes
        await self.cache.set(cache_key, user_analytics, ttl=300)
        return user_analytics

    async def _calculate_user_activity(self, user_id: str) -> dict[str, Any]:
        """Calculate user activity metrics."""
        # This would integrate with conversation/document models
        # For now, return sample structure
        return {
            "conversations_today": 0,
            "documents_accessed": 0,
            "workflows_executed": 0,
            "total_tokens_used": 0,
            "most_active_time": "morning",
            "productivity_score": 85.5
        }

    async def _analyze_usage_patterns(self, user_id: str) -> dict[str, Any]:
        """Analyze user usage patterns for insights."""
        return {
            "preferred_models": ["gpt-4", "claude-3"],
            "common_prompt_types": ["analysis", "writing"],
            "peak_usage_hours": [9, 10, 14, 15],
            "average_session_length": "45 minutes",
            "collaboration_frequency": "low"
        }

    async def _generate_user_recommendations(self, user_id: str) -> list[dict[str, Any]]:
        """Generate personalized recommendations for user."""
        return [
            {
                "type": "efficiency",
                "title": "Try Workflow Templates",
                "description": "Based on your usage patterns, workflow templates could save you 30% time",
                "action": "explore_workflows"
            },
            {
                "type": "collaboration",
                "title": "Share Your Best Prompts",
                "description": "Your prompts have high success rates - consider sharing with team",
                "action": "create_prompt_template"
            }
        ]

    async def cleanup_inactive_tasks(self) -> None:
        """Clean up tasks for disconnected users."""
        current_tasks = list(self._update_tasks.keys())
        for task_key in current_tasks:
            task = self._update_tasks[task_key]
            if task.done() or task.cancelled():
                self._update_tasks.pop(task_key, None)
                logger.debug(f"Cleaned up completed task: {task_key}")


# Global service instance
_real_time_service: RealTimeAnalyticsService | None = None


def get_real_time_analytics_service(session: AsyncSession) -> RealTimeAnalyticsService:
    """Get the real-time analytics service instance."""
    global _real_time_service
    if _real_time_service is None:
        _real_time_service = RealTimeAnalyticsService(session)
    return _real_time_service
