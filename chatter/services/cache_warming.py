"""Cache warming service for preloading frequently accessed analytics data."""

import asyncio
from datetime import datetime, timedelta, UTC
from typing import Any, List, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.analytics import AnalyticsService
from chatter.core.cache_factory import get_general_cache
from chatter.models.user import User
from chatter.models.conversation import Conversation
from chatter.schemas.analytics import AnalyticsTimeRange
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class CacheWarmingService:
    """Service for intelligent cache warming and optimization."""

    def __init__(self, session: AsyncSession):
        """Initialize cache warming service."""
        self.session = session
        self.cache = get_general_cache()
        self.analytics_service = AnalyticsService(session)
        
        # Warming configuration
        self.warming_config = {
            "active_user_threshold_days": 7,    # Users active in last 7 days
            "popular_time_ranges": ["24h", "7d", "30d"],
            "max_concurrent_warmings": 5,       # Prevent overwhelming the system
            "warming_batch_size": 10,           # Users per warming batch
            "warming_interval_minutes": 60,     # How often to run warming
        }

    async def warm_analytics_cache(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Warm cache for analytics data intelligently."""
        warming_start = datetime.now(UTC)
        results = {
            "started_at": warming_start.isoformat(),
            "users_processed": 0,
            "queries_warmed": 0,
            "errors": 0,
            "duration_seconds": 0,
            "cache_hit_improvement": 0.0
        }
        
        try:
            # Get list of active users to warm cache for
            active_users = await self._get_active_users()
            logger.info(f"Starting cache warming for {len(active_users)} active users")
            
            # Process users in batches to prevent overwhelming
            user_batches = [
                active_users[i:i + self.warming_config["warming_batch_size"]]
                for i in range(0, len(active_users), self.warming_config["warming_batch_size"])
            ]
            
            total_queries_warmed = 0
            total_errors = 0
            
            for batch in user_batches:
                batch_results = await self._warm_user_batch(batch, force_refresh)
                total_queries_warmed += batch_results["queries_warmed"]
                total_errors += batch_results["errors"]
                
                # Small delay between batches to prevent overwhelming the system
                await asyncio.sleep(1)
            
            # Warm global/system-wide caches
            system_results = await self._warm_system_caches(force_refresh)
            total_queries_warmed += system_results["queries_warmed"]
            total_errors += system_results["errors"]
            
            warming_end = datetime.now(UTC)
            duration = (warming_end - warming_start).total_seconds()
            
            results.update({
                "users_processed": len(active_users),
                "queries_warmed": total_queries_warmed,
                "errors": total_errors,
                "duration_seconds": duration,
                "completed_at": warming_end.isoformat(),
                "status": "completed" if total_errors == 0 else "completed_with_errors"
            })
            
            logger.info(f"Cache warming completed: {total_queries_warmed} queries warmed in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            results.update({
                "status": "failed",
                "error": str(e),
                "duration_seconds": (datetime.now(UTC) - warming_start).total_seconds()
            })
        
        return results

    async def _get_active_users(self) -> List[str]:
        """Get list of users who have been active recently."""
        try:
            # Get users who have created conversations in the last week
            cutoff_date = datetime.now(UTC) - timedelta(
                days=self.warming_config["active_user_threshold_days"]
            )
            
            query = select(Conversation.user_id).distinct().where(
                Conversation.created_at >= cutoff_date
            ).limit(100)  # Limit to prevent excessive warming
            
            result = await self.session.execute(query)
            user_ids = [row[0] for row in result.all()]
            
            logger.debug(f"Found {len(user_ids)} active users for cache warming")
            return user_ids
            
        except Exception as e:
            logger.error(f"Failed to get active users: {e}")
            return []

    async def _warm_user_batch(self, user_ids: List[str], force_refresh: bool) -> Dict[str, int]:
        """Warm cache for a batch of users."""
        batch_results = {"queries_warmed": 0, "errors": 0}
        
        # Create warming tasks for all users in batch
        warming_tasks = []
        
        for user_id in user_ids:
            for time_period in self.warming_config["popular_time_ranges"]:
                warming_tasks.append(
                    self._warm_user_analytics(user_id, time_period, force_refresh)
                )
        
        # Execute warming tasks with concurrency control
        semaphore = asyncio.Semaphore(self.warming_config["max_concurrent_warmings"])
        
        async def limited_warming_task(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(
            *[limited_warming_task(task) for task in warming_tasks],
            return_exceptions=True
        )
        
        # Count successes and errors
        for result in results:
            if isinstance(result, Exception):
                batch_results["errors"] += 1
            else:
                batch_results["queries_warmed"] += result
        
        return batch_results

    async def _warm_user_analytics(self, user_id: str, time_period: str, force_refresh: bool) -> int:
        """Warm analytics cache for a specific user and time period."""
        try:
            time_range = AnalyticsTimeRange(period=time_period)
            queries_warmed = 0
            
            # Warm the most commonly accessed analytics
            analytics_methods = [
                ("conversation_stats", self.analytics_service.get_conversation_stats),
                ("chart_data", self.analytics_service.get_chart_ready_data),
                ("integrated_stats", lambda uid, tr: self.analytics_service.get_integrated_dashboard_stats(uid))
            ]
            
            for method_name, method in analytics_methods:
                try:
                    if method_name == "integrated_stats" and time_period != "24h":
                        continue  # Only warm integrated stats for daily view
                    
                    if method_name == "integrated_stats":
                        await method(user_id)
                    else:
                        await method(user_id, time_range)
                    
                    queries_warmed += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to warm {method_name} for user {user_id}: {e}")
            
            return queries_warmed
            
        except Exception as e:
            logger.warning(f"Failed to warm analytics for user {user_id}, period {time_period}: {e}")
            return 0

    async def _warm_system_caches(self, force_refresh: bool) -> Dict[str, int]:
        """Warm system-wide caches that don't depend on specific users."""
        results = {"queries_warmed": 0, "errors": 0}
        
        try:
            # Warm system health data
            await self.analytics_service._get_system_health_stats()
            results["queries_warmed"] += 1
            
            # Warm cache performance stats
            await self.analytics_service._get_cache_health_stats()
            results["queries_warmed"] += 1
            
            # Warm database performance metrics
            await self.analytics_service._get_database_response_time()
            results["queries_warmed"] += 1
            
            logger.debug(f"Warmed {results['queries_warmed']} system-wide caches")
            
        except Exception as e:
            logger.error(f"Failed to warm system caches: {e}")
            results["errors"] += 1
        
        return results

    async def get_cache_warming_status(self) -> Dict[str, Any]:
        """Get current cache warming status and statistics."""
        try:
            # Get cache statistics
            cache_stats = await self.analytics_service.get_analytics_performance_metrics()
            
            # Get warming configuration
            status = {
                "warming_config": self.warming_config,
                "cache_performance": {
                    "hit_rate": cache_stats.get("cache_hit_rate", 0),
                    "total_instances": cache_stats.get("cache_instances", 0),
                },
                "system_health": cache_stats.get("system_health", {}),
                "last_warming": await self._get_last_warming_info(),
                "next_warming_due": self._calculate_next_warming_time(),
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get cache warming status: {e}")
            return {"error": str(e)}

    async def _get_last_warming_info(self) -> Dict[str, Any]:
        """Get information about the last cache warming run."""
        try:
            # Try to get last warming info from cache
            last_warming = await self.cache.get("cache_warming:last_run")
            if last_warming:
                return last_warming
            
            return {
                "status": "never_run",
                "message": "Cache warming has not been run yet"
            }
            
        except Exception as e:
            logger.debug(f"Could not get last warming info: {e}")
            return {"status": "unknown"}

    def _calculate_next_warming_time(self) -> str:
        """Calculate when the next cache warming should occur."""
        try:
            next_warming = datetime.now(UTC) + timedelta(
                minutes=self.warming_config["warming_interval_minutes"]
            )
            return next_warming.isoformat()
        except Exception:
            return "unknown"

    async def invalidate_stale_cache_entries(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Invalidate cache entries older than specified age."""
        try:
            invalidated_count = 0
            
            # This would require cache implementations to support TTL inspection
            # For now, we'll focus on invalidating user-specific entries based on activity
            
            # Get users who haven't been active recently
            cutoff_date = datetime.now(UTC) - timedelta(hours=max_age_hours)
            
            inactive_query = select(Conversation.user_id).distinct().where(
                Conversation.created_at < cutoff_date
            )
            
            result = await self.session.execute(inactive_query)
            inactive_users = [row[0] for row in result.all()]
            
            # Invalidate cache for inactive users
            for user_id in inactive_users:
                success = await self.analytics_service.invalidate_user_cache(user_id)
                if success:
                    invalidated_count += 1
            
            logger.info(f"Invalidated cache for {invalidated_count} inactive users")
            
            return {
                "invalidated_users": invalidated_count,
                "cutoff_date": cutoff_date.isoformat(),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Failed to invalidate stale cache entries: {e}")
            return {"status": "failed", "error": str(e)}

    async def optimize_cache_performance(self) -> Dict[str, Any]:
        """Analyze and optimize cache performance."""
        try:
            # Get current cache performance metrics
            performance_metrics = await self.analytics_service.get_analytics_performance_metrics()
            
            optimization_results = {
                "current_hit_rate": performance_metrics.get("cache_hit_rate", 0),
                "actions_taken": [],
                "recommendations": []
            }
            
            current_hit_rate = performance_metrics.get("cache_hit_rate", 0)
            
            # If hit rate is low, suggest cache warming
            if current_hit_rate < 60:
                optimization_results["recommendations"].append({
                    "action": "increase_cache_warming_frequency",
                    "reason": f"Cache hit rate is low ({current_hit_rate:.1f}%)",
                    "suggested_interval": 30  # minutes
                })
            
            # If cache instances are high, suggest consolidation
            cache_instances = performance_metrics.get("cache_instances", 0)
            if cache_instances > 10:
                optimization_results["recommendations"].append({
                    "action": "consolidate_cache_instances",
                    "reason": f"High number of cache instances ({cache_instances})",
                    "suggested_action": "Review cache instance usage patterns"
                })
            
            # Check system health and suggest optimizations
            system_health = performance_metrics.get("system_health", {})
            health_score = system_health.get("health_score", 100)
            
            if health_score < 80:
                optimization_results["recommendations"].append({
                    "action": "system_optimization",
                    "reason": f"System health score is low ({health_score})",
                    "suggested_actions": [
                        "Monitor CPU and memory usage",
                        "Consider increasing cache TTL for stable data",
                        "Review database query performance"
                    ]
                })
            
            # Automatically implement safe optimizations
            if current_hit_rate < 40:
                # Trigger cache warming for active users
                warming_result = await self._warm_user_batch(
                    await self._get_active_users()[:5],  # Warm top 5 active users
                    force_refresh=False
                )
                optimization_results["actions_taken"].append({
                    "action": "emergency_cache_warming",
                    "result": warming_result
                })
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to optimize cache performance: {e}")
            return {"status": "failed", "error": str(e)}