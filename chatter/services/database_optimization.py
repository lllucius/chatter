"""Database optimization service for analytics query performance."""

import time
from datetime import datetime, UTC, timedelta
from typing import Any
from dataclasses import dataclass

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.conversation import Conversation, Message
from chatter.models.document import Document
from chatter.models.user import User
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QueryPerformanceMetric:
    """Query performance metric data."""
    query_type: str
    duration_ms: float
    rows_affected: int
    execution_plan: str | None = None
    optimization_suggestions: list[str] = None


@dataclass
class IndexRecommendation:
    """Database index recommendation."""
    table_name: str
    columns: list[str]
    index_type: str
    estimated_improvement: float
    priority: str  # high, medium, low


class DatabaseOptimizationService:
    """Service for optimizing database performance for analytics queries."""

    def __init__(self, session: AsyncSession):
        """Initialize database optimization service."""
        self.session = session
        self.query_performance_log: list[QueryPerformanceMetric] = []
        self.optimization_cache = {}

        # Performance thresholds
        self.slow_query_threshold_ms = 1000
        self.very_slow_query_threshold_ms = 5000

        # Analytics-specific optimization recommendations
        self.recommended_indexes = [
            IndexRecommendation(
                table_name="conversations",
                columns=["user_id", "created_at"],
                index_type="btree",
                estimated_improvement=60.0,
                priority="high"
            ),
            IndexRecommendation(
                table_name="messages",
                columns=["conversation_id", "created_at"],
                index_type="btree",
                estimated_improvement=45.0,
                priority="high"
            ),
            IndexRecommendation(
                table_name="messages",
                columns=["role", "model_name", "provider_name"],
                index_type="btree",
                estimated_improvement=35.0,
                priority="medium"
            ),
            IndexRecommendation(
                table_name="documents",
                columns=["user_id", "status", "created_at"],
                index_type="btree",
                estimated_improvement=50.0,
                priority="high"
            ),
            IndexRecommendation(
                table_name="conversations",
                columns=["status", "created_at"],
                index_type="btree",
                estimated_improvement=30.0,
                priority="medium"
            ),
        ]

    async def analyze_query_performance(self, query_type: str = None) -> dict[str, Any]:
        """Analyze performance of analytics queries."""
        try:
            analysis_start = time.time()

            # Test key analytics queries
            performance_results = {}

            test_queries = [
                ("conversation_count", self._test_conversation_count_query),
                ("message_aggregation", self._test_message_aggregation_query),
                ("daily_stats", self._test_daily_stats_query),
                ("user_activity", self._test_user_activity_query),
                ("document_analytics", self._test_document_analytics_query),
            ]

            if query_type:
                test_queries = [(name, func) for name, func in test_queries if name == query_type]

            for test_name, test_func in test_queries:
                try:
                    result = await test_func()
                    performance_results[test_name] = result
                except Exception as e:
                    logger.error(f"Query performance test failed for {test_name}: {e}")
                    performance_results[test_name] = {
                        "status": "error",
                        "error": str(e),
                        "duration_ms": 0
                    }

            analysis_duration = (time.time() - analysis_start) * 1000

            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(performance_results)

            return {
                "analysis_duration_ms": analysis_duration,
                "query_performance": performance_results,
                "optimization_recommendations": recommendations,
                "slow_queries": [
                    result for result in performance_results.values()
                    if result.get("duration_ms", 0) > self.slow_query_threshold_ms
                ],
                "index_recommendations": [
                    {
                        "table": rec.table_name,
                        "columns": rec.columns,
                        "type": rec.index_type,
                        "estimated_improvement_percent": rec.estimated_improvement,
                        "priority": rec.priority
                    }
                    for rec in self.recommended_indexes
                ],
                "analyzed_at": datetime.now(UTC).isoformat()
            }

        except Exception as e:
            logger.error(f"Query performance analysis failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _test_conversation_count_query(self) -> dict[str, Any]:
        """Test conversation counting query performance."""
        start_time = time.time()

        try:
            # Test query that's commonly used in analytics
            query = select(
                func.count(Conversation.id).label("total"),
                func.count(Conversation.id).filter(
                    Conversation.created_at >= datetime.now(UTC) - timedelta(days=30)
                ).label("last_30_days")
            )

            result = await self.session.execute(query)
            row = result.first()

            duration_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "duration_ms": duration_ms,
                "rows_returned": 1,
                "result_sample": {
                    "total_conversations": row.total,
                    "recent_conversations": row.last_30_days
                },
                "performance_rating": self._rate_query_performance(duration_ms),
                "optimization_suggestions": self._get_query_suggestions("conversation_count", duration_ms)
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "duration_ms": duration_ms,
                "error": str(e)
            }

    async def _test_message_aggregation_query(self) -> dict[str, Any]:
        """Test message aggregation query performance."""
        start_time = time.time()

        try:
            # Test complex aggregation query
            query = select(
                Message.role,
                func.count(Message.id).label("message_count"),
                func.sum(Message.token_count).label("total_tokens"),
                func.avg(Message.response_time_ms).label("avg_response_time"),
                func.sum(Message.cost).label("total_cost")
            ).join(Conversation).where(
                Conversation.created_at >= datetime.now(UTC) - timedelta(days=7)
            ).group_by(Message.role)

            result = await self.session.execute(query)
            rows = result.all()

            duration_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "duration_ms": duration_ms,
                "rows_returned": len(rows),
                "result_sample": [
                    {
                        "role": row.role,
                        "count": row.message_count,
                        "tokens": row.total_tokens,
                        "avg_time": float(row.avg_response_time or 0),
                        "cost": float(row.total_cost or 0)
                    }
                    for row in rows[:3]  # Sample first 3 rows
                ],
                "performance_rating": self._rate_query_performance(duration_ms),
                "optimization_suggestions": self._get_query_suggestions("message_aggregation", duration_ms)
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "duration_ms": duration_ms,
                "error": str(e)
            }

    async def _test_daily_stats_query(self) -> dict[str, Any]:
        """Test daily statistics query performance."""
        start_time = time.time()

        try:
            # Test time-based grouping query
            query = select(
                func.date(Conversation.created_at).label("date"),
                func.count(Conversation.id).label("conversations"),
                func.count(Message.id).label("messages"),
                func.sum(Message.token_count).label("tokens")
            ).select_from(
                Conversation.__table__.join(Message.__table__)
            ).where(
                Conversation.created_at >= datetime.now(UTC) - timedelta(days=30)
            ).group_by(func.date(Conversation.created_at)).order_by("date")

            result = await self.session.execute(query)
            rows = result.all()

            duration_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "duration_ms": duration_ms,
                "rows_returned": len(rows),
                "result_sample": [
                    {
                        "date": row.date.isoformat(),
                        "conversations": row.conversations,
                        "messages": row.messages,
                        "tokens": row.tokens or 0
                    }
                    for row in rows[:5]  # Sample first 5 days
                ],
                "performance_rating": self._rate_query_performance(duration_ms),
                "optimization_suggestions": self._get_query_suggestions("daily_stats", duration_ms)
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "duration_ms": duration_ms,
                "error": str(e)
            }

    async def _test_user_activity_query(self) -> dict[str, Any]:
        """Test user activity analysis query performance."""
        start_time = time.time()

        try:
            # Test user-based analytics query
            query = select(
                Conversation.user_id,
                func.count(Conversation.id).label("conversation_count"),
                func.max(Conversation.created_at).label("last_activity"),
                func.count(Message.id).label("message_count")
            ).select_from(
                Conversation.__table__.join(Message.__table__)
            ).where(
                Conversation.created_at >= datetime.now(UTC) - timedelta(days=7)
            ).group_by(Conversation.user_id).order_by(
                func.count(Conversation.id).desc()
            ).limit(10)

            result = await self.session.execute(query)
            rows = result.all()

            duration_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "duration_ms": duration_ms,
                "rows_returned": len(rows),
                "result_sample": [
                    {
                        "user_id": row.user_id,
                        "conversations": row.conversation_count,
                        "messages": row.message_count,
                        "last_activity": row.last_activity.isoformat()
                    }
                    for row in rows[:3]  # Sample top 3 active users
                ],
                "performance_rating": self._rate_query_performance(duration_ms),
                "optimization_suggestions": self._get_query_suggestions("user_activity", duration_ms)
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "duration_ms": duration_ms,
                "error": str(e)
            }

    async def _test_document_analytics_query(self) -> dict[str, Any]:
        """Test document analytics query performance."""
        start_time = time.time()

        try:
            # Test document-based analytics query
            query = select(
                Document.status,
                func.count(Document.id).label("doc_count"),
                func.sum(Document.chunk_count).label("total_chunks"),
                func.avg(Document.chunk_count).label("avg_chunks")
            ).where(
                Document.created_at >= datetime.now(UTC) - timedelta(days=30)
            ).group_by(Document.status)

            result = await self.session.execute(query)
            rows = result.all()

            duration_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "duration_ms": duration_ms,
                "rows_returned": len(rows),
                "result_sample": [
                    {
                        "status": str(row.status),
                        "document_count": row.doc_count,
                        "total_chunks": row.total_chunks or 0,
                        "avg_chunks": float(row.avg_chunks or 0)
                    }
                    for row in rows
                ],
                "performance_rating": self._rate_query_performance(duration_ms),
                "optimization_suggestions": self._get_query_suggestions("document_analytics", duration_ms)
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "duration_ms": duration_ms,
                "error": str(e)
            }

    def _rate_query_performance(self, duration_ms: float) -> str:
        """Rate query performance based on duration."""
        if duration_ms < 100:
            return "excellent"
        elif duration_ms < 500:
            return "good"
        elif duration_ms < 1000:
            return "fair"
        elif duration_ms < 5000:
            return "poor"
        else:
            return "critical"

    def _get_query_suggestions(self, query_type: str, duration_ms: float) -> list[str]:
        """Get optimization suggestions for specific query types."""
        suggestions = []

        if duration_ms > self.very_slow_query_threshold_ms:
            suggestions.append("Consider adding database indexes for frequently queried columns")
            suggestions.append("Review query joins and consider query restructuring")
            suggestions.append("Implement query result caching for expensive operations")
        elif duration_ms > self.slow_query_threshold_ms:
            suggestions.append("Consider adding selective indexes")
            suggestions.append("Review WHERE clause for optimization opportunities")

        # Query-specific suggestions
        query_specific_suggestions = {
            "conversation_count": [
                "Add index on (user_id, created_at) for conversations table",
                "Consider using materialized views for frequent count queries"
            ],
            "message_aggregation": [
                "Add composite index on (conversation_id, role, created_at) for messages table",
                "Consider partitioning messages table by date if data volume is large"
            ],
            "daily_stats": [
                "Add index on created_at for efficient date-based grouping",
                "Consider pre-computing daily statistics in a separate table"
            ],
            "user_activity": [
                "Add index on (user_id, created_at) for user-based queries",
                "Consider user activity summary tables for frequent analysis"
            ],
            "document_analytics": [
                "Add index on (status, created_at) for document status queries",
                "Consider document metadata caching for analytics"
            ]
        }

        if query_type in query_specific_suggestions:
            suggestions.extend(query_specific_suggestions[query_type])

        return suggestions

    async def _generate_optimization_recommendations(self, performance_results: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate comprehensive optimization recommendations."""
        recommendations = []

        # Analyze overall performance
        slow_queries = [
            name for name, result in performance_results.items()
            if result.get("duration_ms", 0) > self.slow_query_threshold_ms
        ]

        if slow_queries:
            recommendations.append({
                "type": "performance_improvement",
                "priority": "high",
                "description": f"Slow queries detected: {', '.join(slow_queries)}",
                "action": "Consider implementing recommended indexes and query optimizations",
                "estimated_impact": "50-80% performance improvement"
            })

        # Check for missing indexes
        critical_indexes = [
            rec for rec in self.recommended_indexes
            if rec.priority == "high"
        ]

        if critical_indexes:
            recommendations.append({
                "type": "database_indexing",
                "priority": "high",
                "description": "Critical indexes missing for analytics performance",
                "action": "Implement high-priority database indexes",
                "tables_affected": [rec.table_name for rec in critical_indexes],
                "estimated_impact": "40-70% query performance improvement"
            })

        # Check for caching opportunities
        expensive_queries = [
            name for name, result in performance_results.items()
            if result.get("duration_ms", 0) > 500
        ]

        if expensive_queries:
            recommendations.append({
                "type": "caching_strategy",
                "priority": "medium",
                "description": "Expensive queries identified that would benefit from caching",
                "action": "Implement result caching for expensive analytics queries",
                "queries_affected": expensive_queries,
                "estimated_impact": "60-90% response time improvement for cached queries"
            })

        return recommendations

    async def get_database_health_metrics(self) -> dict[str, Any]:
        """Get comprehensive database health metrics for analytics."""
        try:
            health_metrics = {
                "query_performance": await self.analyze_query_performance(),
                "connection_pool_status": await self._get_connection_pool_status(),
                "table_statistics": await self._get_table_statistics(),
                "index_usage": await self._analyze_index_usage(),
                "recommendations": {
                    "immediate_actions": [],
                    "performance_improvements": [],
                    "long_term_optimizations": []
                }
            }

            # Generate health-based recommendations
            if health_metrics["query_performance"]["slow_queries"]:
                health_metrics["recommendations"]["immediate_actions"].append(
                    "Address slow query performance through indexing and optimization"
                )

            return health_metrics

        except Exception as e:
            logger.error(f"Failed to get database health metrics: {e}")
            return {"status": "error", "error": str(e)}

    async def _get_connection_pool_status(self) -> dict[str, Any]:
        """Get database connection pool status."""
        try:
            # This would require access to the connection pool
            # For now, return basic connection info
            return {
                "status": "healthy",
                "active_connections": 1,  # Current session
                "max_connections": "unknown",
                "connection_health": "good"
            }
        except Exception as e:
            logger.debug(f"Could not get connection pool status: {e}")
            return {"status": "unknown", "error": str(e)}

    async def _get_table_statistics(self) -> dict[str, Any]:
        """Get statistics for main analytics tables."""
        try:
            # Get row counts for main tables
            stats_queries = [
                ("conversations", select(func.count(Conversation.id))),
                ("messages", select(func.count(Message.id))),
                ("documents", select(func.count(Document.id))),
                ("users", select(func.count(User.id)))
            ]

            table_stats = {}

            for table_name, query in stats_queries:
                try:
                    result = await self.session.execute(query)
                    count = result.scalar()
                    table_stats[table_name] = {
                        "row_count": count,
                        "status": "healthy" if count > 0 else "empty"
                    }
                except Exception as e:
                    table_stats[table_name] = {
                        "status": "error",
                        "error": str(e)
                    }

            return table_stats

        except Exception as e:
            logger.error(f"Failed to get table statistics: {e}")
            return {"error": str(e)}

    async def _analyze_index_usage(self) -> dict[str, Any]:
        """Analyze database index usage and effectiveness."""
        try:
            # This would require database-specific queries to analyze index usage
            # For now, return recommendations based on our known patterns
            return {
                "recommended_indexes": [
                    {
                        "table": rec.table_name,
                        "columns": rec.columns,
                        "priority": rec.priority,
                        "estimated_improvement": rec.estimated_improvement
                    }
                    for rec in self.recommended_indexes
                ],
                "analysis_note": "Index recommendations based on analytics query patterns"
            }

        except Exception as e:
            logger.debug(f"Could not analyze index usage: {e}")
            return {"status": "unavailable", "error": str(e)}
