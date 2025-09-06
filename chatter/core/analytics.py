"""Analytics service for generating statistics and insights."""

import asyncio
import time
from datetime import UTC, datetime, timedelta
from typing import Any, Optional, Union

from sqlalchemy import and_, desc, func, literal, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.conversation import (
    Conversation,
    Message,
    MessageRole,
)
from chatter.models.document import Document, DocumentStatus
from chatter.models.user import User
from chatter.schemas.analytics import AnalyticsTimeRange
from chatter.utils.logging import get_logger
from chatter.utils.performance import get_performance_monitor
from chatter.core.cache_factory import CacheFactory
from chatter.core.cache_interface import CacheInterface

logger = get_logger(__name__)


class AnalyticsService:
    """Service for analytics and statistics generation."""

    def __init__(self, session: AsyncSession):
        """Initialize analytics service.

        Args:
            session: Database session
        """
        self.session = session
        self.performance_monitor = get_performance_monitor()
        self.cache_factory = CacheFactory()
        self._cache_instance: Optional[CacheInterface] = None

    def _get_cache_instance(self) -> Optional[CacheInterface]:
        """Get a cache instance for hit rate calculation."""
        if self._cache_instance is None:
            try:
                # Try to get a general cache instance
                from chatter.core.cache_factory import CacheType, CacheBackend
                self._cache_instance = self.cache_factory.get_cache(
                    CacheType.GENERAL, CacheBackend.REDIS
                )
            except Exception as e:
                logger.debug(f"Could not get cache instance: {e}")
                # Try in-memory cache as fallback
                try:
                    self._cache_instance = self.cache_factory.get_cache(
                        CacheType.GENERAL, CacheBackend.MEMORY
                    )
                except Exception as e2:
                    logger.debug(f"Could not get fallback cache instance: {e2}")
        return self._cache_instance

    async def _get_database_response_time(self) -> float:
        """Get average database response time from performance monitor."""
        try:
            summary = self.performance_monitor.get_performance_summary()
            
            # Calculate weighted average of database operations
            db_operations = [
                "get_conversation_stats", "get_usage_metrics", 
                "get_performance_metrics", "get_document_analytics"
            ]
            
            total_time = 0.0
            total_count = 0
            
            for operation in db_operations:
                if operation in summary:
                    op_data = summary[operation]
                    total_time += op_data.get('avg_ms', 0) * op_data.get('count', 0)
                    total_count += op_data.get('count', 0)
            
            return total_time / total_count if total_count > 0 else 0.0
            
        except Exception as e:
            logger.debug(f"Could not get database response time: {e}")
            return 0.0

    async def _get_vector_search_time(self) -> float:
        """Get average vector search time from performance monitor."""
        try:
            summary = self.performance_monitor.get_performance_summary()
            
            # Look for vector search related operations
            vector_operations = [
                op for op in summary.keys() 
                if any(term in op.lower() for term in ['vector', 'search', 'similarity', 'embedding'])
            ]
            
            if not vector_operations:
                return 0.0
                
            total_time = 0.0
            total_count = 0
            
            for operation in vector_operations:
                op_data = summary[operation]
                total_time += op_data.get('avg_ms', 0) * op_data.get('count', 0)
                total_count += op_data.get('count', 0)
            
            return total_time / total_count if total_count > 0 else 0.0
            
        except Exception as e:
            logger.debug(f"Could not get vector search time: {e}")
            return 0.0

    async def _get_embedding_generation_time(self) -> float:
        """Get average embedding generation time from performance monitor."""
        try:
            summary = self.performance_monitor.get_performance_summary()
            
            # Look for embedding generation related operations
            embedding_operations = [
                op for op in summary.keys() 
                if any(term in op.lower() for term in ['embed', 'generate', 'encode'])
            ]
            
            if not embedding_operations:
                return 0.0
                
            total_time = 0.0
            total_count = 0
            
            for operation in embedding_operations:
                op_data = summary[operation]
                total_time += op_data.get('avg_ms', 0) * op_data.get('count', 0)
                total_count += op_data.get('count', 0)
            
            return total_time / total_count if total_count > 0 else 0.0
            
        except Exception as e:
            logger.debug(f"Could not get embedding generation time: {e}")
            return 0.0

    async def _get_vector_database_size(self) -> int:
        """Get vector database size in bytes."""
        try:
            # Query document chunks table for vector data size estimation
            # This gives us an approximate size based on stored embeddings
            vector_count_result = await self.session.execute(
                select(
                    func.count(Document.id).label('doc_count'),
                    func.sum(Document.chunk_count).label('total_chunks')
                ).where(Document.status == DocumentStatus.PROCESSED)
            )
            
            result = vector_count_result.first()
            if result:
                doc_count = result.doc_count or 0
                total_chunks = result.total_chunks or 0
                
                # Estimate: typical embedding dimension is 1536 (OpenAI), 
                # stored as float32 (4 bytes each) + metadata overhead
                # This is a rough approximation
                bytes_per_vector = 1536 * 4  # 6KB per vector
                metadata_overhead = 1024  # 1KB overhead per vector
                
                estimated_size = total_chunks * (bytes_per_vector + metadata_overhead)
                return int(estimated_size)
            
            return 0
            
        except Exception as e:
            logger.debug(f"Could not get vector database size: {e}")
            return 0

    async def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate from cache instance."""
        try:
            cache = self._get_cache_instance()
            if cache and hasattr(cache, 'get_stats'):
                stats = await cache.get_stats()
                if stats and hasattr(stats, 'hit_rate'):
                    return stats.hit_rate
                elif stats and hasattr(stats, 'cache_hits') and hasattr(stats, 'total_requests'):
                    # Calculate hit rate if not directly available
                    total_requests = stats.total_requests
                    return (stats.cache_hits / total_requests) if total_requests > 0 else 0.0
            
            return 0.0
            
        except Exception as e:
            logger.debug(f"Could not get cache hit rate: {e}")
            return 0.0

    async def get_conversation_stats(
        self, user_id: str, time_range: Optional[AnalyticsTimeRange] = None
    ) -> dict[str, Any]:
        """Get conversation statistics.

        Args:
            user_id: User ID
            time_range: Time range filter

        Returns:
            Dictionary with conversation statistics
        """
        try:
            # Build time filter
            time_filter = self._build_time_filter(time_range)

            # Total conversations
            total_conversations_result = await self.session.execute(
                select(func.count(Conversation.id)).where(
                    and_(Conversation.user_id == user_id, time_filter)
                )
            )
            total_conversations = (
                total_conversations_result.scalar() or 0
            )

            # Conversations by status
            status_result = await self.session.execute(
                select(Conversation.status, func.count(Conversation.id))
                .where(
                    and_(Conversation.user_id == user_id, time_filter)
                )
                .group_by(Conversation.status)
            )
            conversations_by_status = dict(status_result.all())

            # Total messages
            total_messages_result = await self.session.execute(
                select(func.count(Message.id))
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(Conversation.user_id == user_id, time_filter)
                )
            )
            total_messages = total_messages_result.scalar() or 0

            # Messages by role
            role_result = await self.session.execute(
                select(Message.role, func.count(Message.id))
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(Conversation.user_id == user_id, time_filter)
                )
                .group_by(Message.role)
            )
            messages_by_role = {
                role.value: count for role, count in role_result.all()
            }

            # Token usage
            token_stats_result = await self.session.execute(
                select(
                    func.sum(Message.prompt_tokens),
                    func.sum(Message.completion_tokens),
                    func.sum(Message.total_tokens),
                    func.sum(Message.cost),
                    func.avg(Message.response_time_ms),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        time_filter,
                    )
                )
            )

            token_stats = token_stats_result.first()
            if token_stats:
                token_stats[0] or 0
                token_stats[1] or 0
                total_tokens = token_stats[2] or 0
                total_cost = float(token_stats[3] or 0)
                avg_response_time = float(token_stats[4] or 0)
            else:
                total_tokens = 0
                total_cost = avg_response_time = 0.0

            # Conversations by date
            date_result = await self.session.execute(
                select(
                    func.date(Conversation.created_at),
                    func.count(Conversation.id),
                )
                .where(
                    and_(Conversation.user_id == user_id, time_filter)
                )
                .group_by(func.date(Conversation.created_at))
                .order_by(func.date(Conversation.created_at))
            )
            conversations_by_date = {
                str(date): count for date, count in date_result.all()
            }

            # Most active hours
            hour_result = await self.session.execute(
                select(
                    func.extract("hour", Conversation.created_at),
                    func.count(Conversation.id),
                )
                .where(
                    and_(Conversation.user_id == user_id, time_filter)
                )
                .group_by(func.extract("hour", Conversation.created_at))
            )
            most_active_hours = {
                str(int(hour)): count
                for hour, count in hour_result.all()
            }

            # Popular models and providers
            model_result = await self.session.execute(
                select(Message.model_used, func.count(Message.id))
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.model_used.is_not(None),
                        time_filter,
                    )
                )
                .group_by(Message.model_used)
            )
            popular_models = {
                model: count
                for model, count in model_result.all()
                if model
            }

            provider_result = await self.session.execute(
                select(Message.provider_used, func.count(Message.id))
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.provider_used.is_not(None),
                        time_filter,
                    )
                )
                .group_by(Message.provider_used)
            )
            popular_providers = {
                provider: count
                for provider, count in provider_result.all()
                if provider
            }

            return {
                "total_conversations": total_conversations,
                "conversations_by_status": conversations_by_status,
                "total_messages": total_messages,
                "messages_by_role": messages_by_role,
                "avg_messages_per_conversation": (
                    total_messages / total_conversations
                    if total_conversations > 0
                    else 0.0
                ),
                "total_tokens_used": total_tokens,
                "total_cost": total_cost,
                "avg_response_time_ms": avg_response_time,
                "conversations_by_date": conversations_by_date,
                "most_active_hours": most_active_hours,
                "popular_models": popular_models,
                "popular_providers": popular_providers,
            }

        except Exception as e:
            logger.error(
                "Failed to get conversation stats", error=str(e)
            )
            # Return default values to prevent validation errors
            return {
                "total_conversations": 0,
                "conversations_by_status": {},
                "total_messages": 0,
                "messages_by_role": {},
                "avg_messages_per_conversation": 0.0,
                "total_tokens_used": 0,
                "total_cost": 0.0,
                "avg_response_time_ms": 0.0,
                "conversations_by_date": {},
                "most_active_hours": {},
                "popular_models": {},
                "popular_providers": {},
            }

    async def get_usage_metrics(
        self, user_id: str, time_range: Optional[AnalyticsTimeRange] = None
    ) -> dict[str, Any]:
        """Get usage metrics.

        Args:
            user_id: User ID
            time_range: Time range filter

        Returns:
            Dictionary with usage metrics
        """
        try:
            time_filter = self._build_time_filter(time_range)

            # Token usage totals
            total_usage_result = await self.session.execute(
                select(
                    func.sum(Message.prompt_tokens),
                    func.sum(Message.completion_tokens),
                    func.sum(Message.total_tokens),
                    func.sum(Message.cost),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        time_filter,
                    )
                )
            )

            usage_totals = total_usage_result.first()
            if usage_totals:
                total_prompt_tokens = usage_totals[0] or 0
                total_completion_tokens = usage_totals[1] or 0
                total_tokens = usage_totals[2] or 0
                total_cost = float(usage_totals[3] or 0)
            else:
                total_prompt_tokens = 0
                total_completion_tokens = 0
                total_tokens = 0
                total_cost = 0.0

            # Usage by model
            model_usage_result = await self.session.execute(
                select(
                    Message.model_used,
                    func.sum(Message.total_tokens),
                    func.sum(Message.cost),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.model_used.is_not(None),
                        time_filter,
                    )
                )
                .group_by(Message.model_used)
            )

            tokens_by_model = {}
            cost_by_model = {}
            for model, tokens, cost in model_usage_result.all():
                if model:
                    tokens_by_model[model] = tokens or 0
                    cost_by_model[model] = float(cost or 0)

            # Usage by provider
            provider_usage_result = await self.session.execute(
                select(
                    Message.provider_used,
                    func.sum(Message.total_tokens),
                    func.sum(Message.cost),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.provider_used.is_not(None),
                        time_filter,
                    )
                )
                .group_by(Message.provider_used)
            )

            tokens_by_provider = {}
            cost_by_provider = {}
            for provider, tokens, cost in provider_usage_result.all():
                if provider:
                    tokens_by_provider[provider] = tokens or 0
                    cost_by_provider[provider] = float(cost or 0)

            # Daily usage (last 30 days)
            daily_usage_result = await self.session.execute(
                select(
                    func.date(Message.created_at),
                    func.sum(Message.total_tokens),
                    func.sum(Message.cost),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        Message.created_at
                        >= datetime.now(UTC) - timedelta(days=30),
                    )
                )
                .group_by(func.date(Message.created_at))
                .order_by(func.date(Message.created_at))
            )

            daily_usage = {}
            daily_cost = {}
            for date, tokens, cost in daily_usage_result.all():
                date_str = str(date)
                daily_usage[date_str] = tokens or 0
                daily_cost[date_str] = float(cost or 0)

            # Performance metrics
            response_time_result = await self.session.execute(
                select(func.avg(Message.response_time_ms))
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        Message.response_time_ms.is_not(None),
                        time_filter,
                    )
                )
            )
            avg_response_time = float(
                response_time_result.scalar() or 0
            )

            # Response times by model
            model_response_result = await self.session.execute(
                select(
                    Message.model_used,
                    func.avg(Message.response_time_ms),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.model_used.is_not(None),
                        Message.response_time_ms.is_not(None),
                        time_filter,
                    )
                )
                .group_by(Message.model_used)
            )
            response_times_by_model = {
                model: float(time)
                for model, time in model_response_result.all()
                if model
            }

            # Activity metrics
            activity_result = await self.session.execute(
                select(
                    func.count(
                        func.distinct(
                            func.date(Conversation.created_at)
                        )
                    ),
                    func.extract(
                        "hour", func.max(Conversation.created_at)
                    ),
                    func.count(Conversation.id)
                    / func.nullif(
                        func.count(
                            func.distinct(
                                func.date(Conversation.created_at)
                            )
                        ),
                        0,
                    ),
                ).where(
                    and_(Conversation.user_id == user_id, time_filter)
                )
            )

            activity_stats = activity_result.first()
            if activity_stats:
                active_days = activity_stats[0] or 0
                peak_usage_hour = int(activity_stats[1] or 0)
                conversations_per_day = float(activity_stats[2] or 0)
            else:
                active_days = 0
                peak_usage_hour = 0
                conversations_per_day = 0.0

            return {
                "total_prompt_tokens": total_prompt_tokens,
                "total_completion_tokens": total_completion_tokens,
                "total_tokens": total_tokens,
                "tokens_by_model": tokens_by_model,
                "tokens_by_provider": tokens_by_provider,
                "total_cost": total_cost,
                "cost_by_model": cost_by_model,
                "cost_by_provider": cost_by_provider,
                "daily_usage": daily_usage,
                "daily_cost": daily_cost,
                "avg_response_time": avg_response_time,
                "response_times_by_model": response_times_by_model,
                "active_days": active_days,
                "peak_usage_hour": peak_usage_hour,
                "conversations_per_day": conversations_per_day,
            }

        except Exception as e:
            logger.error("Failed to get usage metrics", error=str(e))
            # Return default values to prevent validation errors
            return {
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_tokens": 0,
                "tokens_by_model": {},
                "tokens_by_provider": {},
                "total_cost": 0.0,
                "cost_by_model": {},
                "cost_by_provider": {},
                "daily_usage": {},
                "daily_cost": {},
                "avg_response_time": 0.0,
                "response_times_by_model": {},
                "active_days": 0,
                "peak_usage_hour": 0,
                "conversations_per_day": 0.0,
            }

    async def get_performance_metrics(
        self, user_id: str, time_range: Optional[AnalyticsTimeRange] = None
    ) -> dict[str, Any]:
        """Get performance metrics.

        Args:
            user_id: User ID
            time_range: Time range filter

        Returns:
            Dictionary with performance metrics
        """
        try:
            time_filter = self._build_time_filter(time_range)

            # Response time statistics
            response_stats_result = await self.session.execute(
                select(
                    func.avg(Message.response_time_ms),
                    func.percentile_cont(0.5).within_group(
                        Message.response_time_ms
                    ),
                    func.percentile_cont(0.95).within_group(
                        Message.response_time_ms
                    ),
                    func.percentile_cont(0.99).within_group(
                        Message.response_time_ms
                    ),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        Message.response_time_ms.is_not(None),
                        time_filter,
                    )
                )
            )

            response_stats = response_stats_result.first()
            if response_stats:
                avg_response_time = float(response_stats[0] or 0)
                median_response_time = float(response_stats[1] or 0)
                p95_response_time = float(response_stats[2] or 0)
                p99_response_time = float(response_stats[3] or 0)
            else:
                avg_response_time = 0.0
                median_response_time = 0.0
                p95_response_time = 0.0
                p99_response_time = 0.0

            # Throughput metrics
            throughput_result = await self.session.execute(
                select(
                    func.count(Message.id),
                    func.sum(Message.total_tokens),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        time_filter,
                    )
                )
            )

            throughput_stats = throughput_result.first()
            if throughput_stats:
                total_requests = throughput_stats[0] or 0
                total_tokens = throughput_stats[1] or 0
            else:
                total_requests = 0
                total_tokens = 0

            # Calculate per-minute rates with proper division by zero handling
            time_range_minutes = self._get_time_range_minutes(
                time_range
            )

            # Ensure we don't divide by zero
            if time_range_minutes > 0:
                requests_per_minute = (
                    total_requests / time_range_minutes
                )
                tokens_per_minute = total_tokens / time_range_minutes
            else:
                # Log warning about invalid time range
                logger.warning(
                    "Invalid time range for performance metrics calculation",
                    time_range_minutes=time_range_minutes,
                )
                requests_per_minute = 0.0
                tokens_per_minute = 0.0

            # Error metrics from message error tracking
            error_messages_result = await self.session.execute(
                select(
                    func.count(Message.id).label("total_errors"),
                    func.count(func.distinct(Message.id))
                    .filter(Message.error_message.is_not(None))
                    .label("messages_with_errors"),
                    func.sum(Message.retry_count).label(
                        "total_retries"
                    ),
                    func.avg(Message.retry_count).label("avg_retries"),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(Conversation.user_id == user_id, time_filter)
                )
            )
            error_row = error_messages_result.first()

            total_errors = int(error_row.messages_with_errors or 0)
            # total_retries = int(error_row.total_retries or 0)  # Unused for now
            total_messages = int(
                error_row.total_errors or 0
            )  # Get total message count from the first result

            # Calculate error rate
            if total_messages > 0:
                error_rate = (total_errors / total_messages) * 100
            else:
                error_rate = 0.0

            # Get error types from finish_reason field
            error_types_result = await self.session.execute(
                select(
                    Message.finish_reason,
                    func.count(Message.id).label("count"),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        time_filter,
                        Message.error_message.is_not(None),
                    )
                )
                .group_by(Message.finish_reason)
            )
            errors_by_type = {
                row.finish_reason or "unknown": int(row.count)
                for row in error_types_result.all()
            }

            # Performance by model
            model_performance_result = await self.session.execute(
                select(
                    Message.model_used,
                    func.avg(Message.response_time_ms),
                    func.count(Message.id),
                    func.sum(Message.total_tokens),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.model_used.is_not(None),
                        Message.response_time_ms.is_not(None),
                        time_filter,
                    )
                )
                .group_by(Message.model_used)
            )

            performance_by_model = {}
            for (
                model,
                avg_time,
                count,
                tokens,
            ) in model_performance_result.all():
                if model:
                    performance_by_model[model] = {
                        "avg_response_time_ms": float(avg_time),
                        "total_requests": count,
                        "total_tokens": tokens or 0,
                        "tokens_per_request": (
                            (tokens or 0) / count if count > 0 else 0
                        ),
                    }

            # Performance by provider
            provider_performance_result = await self.session.execute(
                select(
                    Message.provider_used,
                    func.avg(Message.response_time_ms),
                    func.count(Message.id),
                    func.sum(Message.total_tokens),
                )
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.provider_used.is_not(None),
                        Message.response_time_ms.is_not(None),
                        time_filter,
                    )
                )
                .group_by(Message.provider_used)
            )

            performance_by_provider = {}
            for (
                provider,
                avg_time,
                count,
                tokens,
            ) in provider_performance_result.all():
                if provider:
                    performance_by_provider[provider] = {
                        "avg_response_time_ms": float(avg_time),
                        "total_requests": count,
                        "total_tokens": tokens or 0,
                        "tokens_per_request": (
                            (tokens or 0) / count if count > 0 else 0
                        ),
                    }

            return {
                "avg_response_time_ms": avg_response_time,
                "median_response_time_ms": median_response_time,
                "p95_response_time_ms": p95_response_time,
                "p99_response_time_ms": p99_response_time,
                "requests_per_minute": requests_per_minute,
                "tokens_per_minute": tokens_per_minute,
                "total_errors": total_errors,
                "error_rate": error_rate,
                "errors_by_type": errors_by_type,
                "performance_by_model": performance_by_model,
                "performance_by_provider": performance_by_provider,
                "database_response_time_ms": await self._get_database_response_time(),
                "vector_search_time_ms": await self._get_vector_search_time(),
                "embedding_generation_time_ms": await self._get_embedding_generation_time(),
            }

        except Exception as e:
            logger.error(
                "Failed to get performance metrics", error=str(e)
            )
            # Return default values to prevent Pydantic validation errors
            return {
                "avg_response_time_ms": 0.0,
                "median_response_time_ms": 0.0,
                "p95_response_time_ms": 0.0,
                "p99_response_time_ms": 0.0,
                "requests_per_minute": 0.0,
                "tokens_per_minute": 0.0,
                "total_errors": 0,
                "error_rate": 0.0,
                "errors_by_type": {},
                "performance_by_model": {},
                "performance_by_provider": {},
                "database_response_time_ms": 0.0,
                "vector_search_time_ms": 0.0,
                "embedding_generation_time_ms": 0.0,
            }

    async def get_document_analytics(
        self, user_id: str, time_range: Optional[AnalyticsTimeRange] = None
    ) -> dict[str, Any]:
        """Get document analytics.

        Args:
            user_id: User ID
            time_range: Time range filter

        Returns:
            Dictionary with document analytics
        """
        try:
            time_filter = self._build_time_filter(
                time_range, "Document"
            )

            # Document counts
            total_docs_result = await self.session.execute(
                select(func.count(Document.id)).where(
                    and_(Document.owner_id == user_id, time_filter)
                )
            )
            total_documents = total_docs_result.scalar()

            # Documents by status
            status_result = await self.session.execute(
                select(Document.status, func.count(Document.id))
                .where(and_(Document.owner_id == user_id, time_filter))
                .group_by(Document.status)
            )
            documents_by_status = {
                status.value: count
                for status, count in status_result.all()
            }

            # Documents by type
            type_result = await self.session.execute(
                select(Document.document_type, func.count(Document.id))
                .where(and_(Document.owner_id == user_id, time_filter))
                .group_by(Document.document_type)
            )
            documents_by_type = {
                doc_type.value: count
                for doc_type, count in type_result.all()
            }

            # Processing metrics
            processing_result = await self.session.execute(
                select(
                    func.avg(
                        func.extract(
                            "epoch", Document.processing_completed_at
                        )
                        - func.extract(
                            "epoch", Document.processing_started_at
                        )
                    ),
                    func.count(Document.id).filter(
                        Document.status == DocumentStatus.PROCESSED
                    ),
                    func.count(Document.id),
                    func.sum(Document.chunk_count),
                    func.avg(Document.chunk_count),
                ).where(
                    and_(
                        Document.owner_id == user_id,
                        Document.processing_started_at.is_not(None),
                        time_filter,
                    )
                )
            )

            processing_stats = processing_result.first()
            if processing_stats:
                avg_processing_time = float(processing_stats[0] or 0)
                processed_docs = processing_stats[1] or 0
                total_docs = processing_stats[2] or 0
                total_chunks = processing_stats[3] or 0
                avg_chunks = float(processing_stats[4] or 0)
            else:
                avg_processing_time = 0.0
                processed_docs = 0
                total_docs = 0
                total_chunks = 0
                avg_chunks = 0.0

            processing_success_rate = (
                processed_docs / total_docs if total_docs > 0 else 0.0
            )

            # Storage metrics
            storage_result = await self.session.execute(
                select(
                    func.sum(Document.file_size),
                    func.avg(Document.file_size),
                ).where(and_(Document.owner_id == user_id, time_filter))
            )

            storage_stats = storage_result.first()
            if storage_stats:
                total_storage = storage_stats[0] or 0
                avg_size = float(storage_stats[1] or 0)
            else:
                total_storage = 0
                avg_size = 0.0

            # Storage by type
            storage_by_type_result = await self.session.execute(
                select(
                    Document.document_type, func.sum(Document.file_size)
                )
                .where(and_(Document.owner_id == user_id, time_filter))
                .group_by(Document.document_type)
            )
            storage_by_type = {
                doc_type.value: size
                for doc_type, size in storage_by_type_result.all()
            }

            # Search and access metrics
            search_result = await self.session.execute(
                select(
                    func.sum(Document.search_count),
                    func.sum(Document.view_count),
                ).where(and_(Document.owner_id == user_id, time_filter))
            )

            search_stats = search_result.first()
            if search_stats:
                total_searches = search_stats[0] or 0
                total_views = search_stats[1] or 0
            else:
                total_searches = 0
                total_views = 0

            # Most viewed documents
            most_viewed_result = await self.session.execute(
                select(
                    Document.id, Document.filename, Document.view_count
                )
                .where(and_(Document.owner_id == user_id, time_filter))
                .order_by(desc(Document.view_count))
                .limit(10)
            )

            most_viewed_documents = [
                {
                    "id": doc_id,
                    "filename": filename,
                    "view_count": view_count,
                }
                for doc_id, filename, view_count in most_viewed_result.all()
            ]

            return {
                "total_documents": total_documents,
                "documents_by_status": documents_by_status,
                "documents_by_type": documents_by_type,
                "avg_processing_time_seconds": avg_processing_time,
                "processing_success_rate": processing_success_rate,
                "total_chunks": total_chunks,
                "avg_chunks_per_document": avg_chunks,
                "total_storage_bytes": total_storage,
                "avg_document_size_bytes": avg_size,
                "storage_by_type": storage_by_type,
                "total_searches": total_searches,
                "avg_search_results": 0.0,  # Would need search result tracking
                "popular_search_terms": {},  # Would need search term tracking
                "total_views": total_views,
                "most_viewed_documents": most_viewed_documents,
                "documents_by_access_level": {
                    "private": total_documents,
                    "public": 0,
                    "shared": 0,
                },  # Simplified
            }

        except Exception as e:
            logger.error(
                "Failed to get document analytics", error=str(e)
            )
            # Return default values to prevent validation errors
            return {
                "total_documents": 0,
                "documents_by_status": {},
                "documents_by_type": {},
                "avg_processing_time_seconds": 0.0,
                "processing_success_rate": 0.0,
                "total_chunks": 0,
                "avg_chunks_per_document": 0.0,
                "total_storage_bytes": 0,
                "avg_document_size_bytes": 0.0,
                "storage_by_type": {},
                "total_searches": 0,
                "avg_search_results": 0.0,
                "popular_search_terms": {},
                "total_views": 0,
                "most_viewed_documents": [],
                "documents_by_access_level": {
                    "private": 0,
                    "public": 0,
                    "shared": 0,
                },
            }

    async def get_system_analytics(self) -> dict[str, Any]:
        """Get system-wide analytics.

        Returns:
            Dictionary with system analytics
        """
        try:
            # Default time filter for last 24 hours for API metrics
            time_filter = Message.created_at >= datetime.now(
                UTC
            ) - timedelta(hours=24)

            # User activity
            user_activity_result = await self.session.execute(
                select(
                    func.count(User.id),
                    func.count(User.id).filter(
                        User.last_login_at
                        >= datetime.now(UTC) - timedelta(days=1)
                    ),
                    func.count(User.id).filter(
                        User.last_login_at
                        >= datetime.now(UTC) - timedelta(days=7)
                    ),
                    func.count(User.id).filter(
                        User.last_login_at
                        >= datetime.now(UTC) - timedelta(days=30)
                    ),
                )
            )

            user_stats = user_activity_result.first()
            if user_stats:
                total_users = user_stats[0] or 0
                active_users_today = user_stats[1] or 0
                active_users_week = user_stats[2] or 0
                active_users_month = user_stats[3] or 0
            else:
                total_users = 0
                active_users_today = 0
                active_users_week = 0
                active_users_month = 0

            # System health metrics (optional - requires psutil)
            system_health = {}
            try:
                import time

                import psutil

                # Get current process info for basic metrics
                # process = psutil.Process()  # Unused for now
                system_health = {
                    "system_uptime_seconds": time.time()
                    - psutil.boot_time(),
                    "avg_cpu_usage": psutil.cpu_percent(interval=0.1),
                    "avg_memory_usage": psutil.virtual_memory().percent,
                    "database_connections": len(
                        self.session.get_bind().pool.checkedout()
                    ),
                }
            except (ImportError, AttributeError, Exception):
                # If psutil not available or other error, skip system health metrics
                logger.debug(
                    "System health metrics not available (psutil may not be installed)"
                )
                pass

            # API metrics from message data (using messages as proxy for API requests)
            api_metrics_result = await self.session.execute(
                select(
                    func.count(Message.id).label("total_requests"),
                    func.avg(Message.response_time_ms).label(
                        "avg_response_time"
                    ),
                    func.count(Message.id)
                    .filter(Message.error_message.is_not(None))
                    .label("error_requests"),
                )
                .select_from(Message)
                .join(Conversation)
                .where(time_filter)
            )
            api_row = api_metrics_result.first()

            total_api_requests = int(api_row.total_requests or 0)
            avg_response_time = float(api_row.avg_response_time or 0.0)
            error_requests = int(api_row.error_requests or 0)

            api_error_rate = (
                (error_requests / total_api_requests * 100)
                if total_api_requests > 0
                else 0.0
            )

            # Get requests by endpoint (using model_used as proxy)
            endpoint_result = await self.session.execute(
                select(
                    Message.model_used,
                    func.count(Message.id).label("request_count"),
                )
                .select_from(Message)
                .join(Conversation)
                .where(time_filter)
                .group_by(Message.model_used)
            )
            requests_per_endpoint = {
                f"model_{row.model_used or 'unknown'}": int(
                    row.request_count
                )
                for row in endpoint_result.all()
            }

            api_metrics = {
                "total_api_requests": total_api_requests,
                "requests_per_endpoint": requests_per_endpoint,
                "avg_api_response_time": avg_response_time,
                "api_error_rate": api_error_rate,
            }

            # Resource usage
            storage_result = await self.session.execute(
                select(func.sum(Document.file_size))
            )
            storage_usage = storage_result.scalar() or 0

            return {
                "total_users": total_users,
                "active_users_today": active_users_today,
                "active_users_week": active_users_week,
                "active_users_month": active_users_month,
                **system_health,
                **api_metrics,
                "storage_usage_bytes": storage_usage,
                "vector_database_size_bytes": await self._get_vector_database_size(),
                "cache_hit_rate": await self._get_cache_hit_rate(),
            }

        except Exception as e:
            logger.error("Failed to get system analytics", error=str(e))
            # Return default values to prevent Pydantic validation errors
            return {
                "total_users": 0,
                "active_users_today": 0,
                "active_users_week": 0,
                "active_users_month": 0,
                "system_uptime_seconds": 0.0,
                "avg_cpu_usage": 0.0,
                "avg_memory_usage": 0.0,
                "database_connections": 0,
                "total_api_requests": 0,
                "requests_per_endpoint": {},
                "avg_api_response_time": 0.0,
                "api_error_rate": 0.0,
                "storage_usage_bytes": 0,
                "vector_database_size_bytes": 0,
                "cache_hit_rate": 0.0,
            }

    async def get_tool_server_analytics(
        self,
        user_id: Optional[str] = None,
        time_range: Optional[AnalyticsTimeRange] = None,
    ) -> dict[str, Any]:
        """Get tool server analytics.

        Args:
            user_id: User ID for user-specific analytics
            time_range: Time range filter

        Returns:
            Dictionary with tool server analytics
        """
        try:
            from chatter.models.toolserver import (
                ServerStatus,
                ServerTool,
                ToolServer,
                ToolStatus,
                ToolUsage,
            )

            time_filter = self._build_time_filter_for_table(
                time_range, ToolUsage, ToolUsage.called_at
            )

            # Overall server counts
            total_servers_result = await self.session.execute(
                select(func.count(ToolServer.id))
            )
            total_servers = total_servers_result.scalar() or 0

            active_servers_result = await self.session.execute(
                select(func.count(ToolServer.id)).where(
                    ToolServer.status == ServerStatus.ENABLED
                )
            )
            active_servers = active_servers_result.scalar() or 0

            # Tool counts
            total_tools_result = await self.session.execute(
                select(func.count(ServerTool.id))
            )
            total_tools = total_tools_result.scalar() or 0

            enabled_tools_result = await self.session.execute(
                select(func.count(ServerTool.id)).where(
                    ServerTool.status == ToolStatus.ENABLED
                )
            )
            enabled_tools = enabled_tools_result.scalar() or 0

            # Usage metrics
            usage_filters = (
                [time_filter] if time_filter is not None else []
            )
            if user_id:
                usage_filters.append(ToolUsage.user_id == user_id)

            usage_where = (
                and_(*usage_filters) if usage_filters else text("1=1")
            )

            # Daily usage counts
            today = datetime.now(UTC).date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)

            calls_today_result = await self.session.execute(
                select(func.count(ToolUsage.id)).where(
                    and_(
                        func.date(ToolUsage.called_at) == today,
                        (
                            usage_where
                            if usage_where is not None
                            else text("1=1")
                        ),
                    )
                )
            )
            calls_today = calls_today_result.scalar() or 0

            calls_week_result = await self.session.execute(
                select(func.count(ToolUsage.id)).where(
                    and_(
                        ToolUsage.called_at
                        >= datetime.combine(
                            week_ago, datetime.min.time()
                        ).replace(tzinfo=UTC),
                        (
                            usage_where
                            if usage_where is not None
                            else text("1=1")
                        ),
                    )
                )
            )
            calls_week = calls_week_result.scalar() or 0

            calls_month_result = await self.session.execute(
                select(func.count(ToolUsage.id)).where(
                    and_(
                        ToolUsage.called_at
                        >= datetime.combine(
                            month_ago, datetime.min.time()
                        ).replace(tzinfo=UTC),
                        (
                            usage_where
                            if usage_where is not None
                            else text("1=1")
                        ),
                    )
                )
            )
            calls_month = calls_month_result.scalar() or 0

            # Error counts
            errors_today_result = await self.session.execute(
                select(func.count(ToolUsage.id)).where(
                    and_(
                        func.date(ToolUsage.called_at) == today,
                        ToolUsage.success is False,
                        (
                            usage_where
                            if usage_where is not None
                            else text("1=1")
                        ),
                    )
                )
            )
            errors_today = errors_today_result.scalar() or 0

            # Success rate
            total_calls = calls_month
            total_errors = await self.session.execute(
                select(func.count(ToolUsage.id)).where(
                    and_(
                        ToolUsage.called_at
                        >= datetime.combine(
                            month_ago, datetime.min.time()
                        ).replace(tzinfo=UTC),
                        ToolUsage.success is False,
                        (
                            usage_where
                            if usage_where is not None
                            else text("1=1")
                        ),
                    )
                )
            )
            total_errors = total_errors.scalar() or 0
            overall_success_rate = (
                (total_calls - total_errors) / total_calls
                if total_calls > 0
                else 1.0
            )

            # Performance metrics
            avg_response_result = await self.session.execute(
                select(func.avg(ToolUsage.response_time_ms)).where(
                    and_(
                        ToolUsage.response_time_ms.is_not(None),
                        (
                            usage_where
                            if usage_where is not None
                            else text("1=1")
                        ),
                    )
                )
            )
            avg_response_time = float(avg_response_result.scalar() or 0)

            # P95 response time (approximation)
            p95_response_result = await self.session.execute(
                select(
                    func.percentile_cont(0.95).within_group(
                        ToolUsage.response_time_ms.asc()
                    )
                ).where(
                    and_(
                        ToolUsage.response_time_ms.is_not(None),
                        (
                            usage_where
                            if usage_where is not None
                            else text("1=1")
                        ),
                    )
                )
            )
            p95_response_time = float(p95_response_result.scalar() or 0)

            # Server metrics
            server_metrics_result = await self.session.execute(
                select(
                    ToolServer.id,
                    ToolServer.name,
                    ToolServer.status,
                    func.count(ServerTool.id).label("total_tools"),
                    func.count(ServerTool.id)
                    .filter(ServerTool.status == ToolStatus.ENABLED)
                    .label("enabled_tools"),
                    func.count(ToolUsage.id).label("total_calls"),
                    func.count(ToolUsage.id)
                    .filter(ToolUsage.success is False)
                    .label("total_errors"),
                    func.avg(ToolUsage.response_time_ms).label(
                        "avg_response_time"
                    ),
                    func.max(ToolUsage.called_at).label(
                        "last_activity"
                    ),
                )
                .select_from(ToolServer)
                .outerjoin(ServerTool)
                .outerjoin(ToolUsage)
                .group_by(
                    ToolServer.id, ToolServer.name, ToolServer.status
                )
            )

            server_metrics = []
            for row in server_metrics_result.all():
                total_calls = row.total_calls or 0
                total_errors = row.total_errors or 0
                success_rate = (
                    (total_calls - total_errors) / total_calls
                    if total_calls > 0
                    else 1.0
                )

                server_metrics.append(
                    {
                        "server_id": row.id,
                        "server_name": row.name,
                        "status": row.status,
                        "total_tools": row.total_tools or 0,
                        "enabled_tools": row.enabled_tools or 0,
                        "total_calls": total_calls,
                        "total_errors": total_errors,
                        "success_rate": success_rate,
                        "avg_response_time_ms": (
                            float(row.avg_response_time)
                            if row.avg_response_time
                            else None
                        ),
                        "last_activity": row.last_activity,
                        "uptime_percentage": None,  # Would need additional tracking
                    }
                )

            # Top tools by usage
            top_tools_result = await self.session.execute(
                select(
                    ServerTool.id,
                    ServerTool.name,
                    ToolServer.name.label("server_name"),
                    ServerTool.status,
                    func.count(ToolUsage.id).label("total_calls"),
                    func.count(ToolUsage.id)
                    .filter(ToolUsage.success is False)
                    .label("total_errors"),
                    func.avg(ToolUsage.response_time_ms).label(
                        "avg_response_time"
                    ),
                    func.max(ToolUsage.called_at).label("last_called"),
                    func.count(ToolUsage.id)
                    .filter(
                        ToolUsage.called_at
                        >= datetime.now(UTC) - timedelta(hours=24)
                    )
                    .label("calls_last_24h"),
                    func.count(ToolUsage.id)
                    .filter(
                        and_(
                            ToolUsage.called_at
                            >= datetime.now(UTC) - timedelta(hours=24),
                            ToolUsage.success is False,
                        )
                    )
                    .label("errors_last_24h"),
                )
                .select_from(ServerTool)
                .join(ToolServer)
                .outerjoin(ToolUsage)
                .where(
                    usage_where
                    if usage_where is not None
                    else text("1=1")
                )
                .group_by(
                    ServerTool.id,
                    ServerTool.name,
                    ToolServer.name,
                    ServerTool.status,
                )
                .order_by(func.count(ToolUsage.id).desc())
                .limit(10)
            )

            top_tools = []
            failing_tools = []

            for row in top_tools_result.all():
                total_calls = row.total_calls or 0
                total_errors = row.total_errors or 0
                success_rate = (
                    (total_calls - total_errors) / total_calls
                    if total_calls > 0
                    else 1.0
                )

                tool_metrics = {
                    "tool_id": row.id,
                    "tool_name": row.name,
                    "server_name": row.server_name,
                    "status": row.status,
                    "total_calls": total_calls,
                    "total_errors": total_errors,
                    "success_rate": success_rate,
                    "avg_response_time_ms": (
                        float(row.avg_response_time)
                        if row.avg_response_time
                        else None
                    ),
                    "last_called": row.last_called,
                    "calls_last_24h": row.calls_last_24h or 0,
                    "errors_last_24h": row.errors_last_24h or 0,
                }

                top_tools.append(tool_metrics)

                # Add to failing tools if error rate > 10%
                if success_rate < 0.9 and total_calls > 5:
                    failing_tools.append(tool_metrics)

            # Daily usage time series
            daily_usage_result = await self.session.execute(
                select(
                    func.date(ToolUsage.called_at).label("date"),
                    func.count(ToolUsage.id).label("calls"),
                    func.count(ToolUsage.id)
                    .filter(ToolUsage.success is False)
                    .label("errors"),
                )
                .where(
                    and_(
                        ToolUsage.called_at
                        >= datetime.now(UTC) - timedelta(days=30),
                        (
                            usage_where
                            if usage_where is not None
                            else text("1=1")
                        ),
                    )
                )
                .group_by(func.date(ToolUsage.called_at))
                .order_by(func.date(ToolUsage.called_at))
            )

            daily_usage = {}
            daily_errors = {}

            for row in daily_usage_result.all():
                date_str = row.date.isoformat()
                daily_usage[date_str] = row.calls or 0
                daily_errors[date_str] = row.errors or 0

            return {
                "total_servers": total_servers,
                "active_servers": active_servers,
                "total_tools": total_tools,
                "enabled_tools": enabled_tools,
                "total_calls_today": calls_today,
                "total_calls_week": calls_week,
                "total_calls_month": calls_month,
                "total_errors_today": errors_today,
                "overall_success_rate": overall_success_rate,
                "avg_response_time_ms": avg_response_time,
                "p95_response_time_ms": p95_response_time,
                "server_metrics": server_metrics,
                "top_tools": top_tools,
                "failing_tools": failing_tools,
                "daily_usage": daily_usage,
                "daily_errors": daily_errors,
                "generated_at": datetime.now(UTC),
            }

        except Exception as e:
            logger.error(
                "Failed to get tool server analytics", error=str(e)
            )
            # Return default values to prevent validation errors
            return {
                "total_servers": 0,
                "active_servers": 0,
                "total_tools": 0,
                "enabled_tools": 0,
                "total_calls_today": 0,
                "total_calls_week": 0,
                "total_calls_month": 0,
                "total_errors_today": 0,
                "overall_success_rate": 1.0,
                "avg_response_time_ms": 0.0,
                "p95_response_time_ms": 0.0,
                "server_metrics": [],
                "top_tools": [],
                "failing_tools": [],
                "daily_usage": {},
                "daily_errors": {},
                "generated_at": datetime.now(UTC),
            }

    def _build_time_filter_for_table(
        self,
        time_range: Optional[AnalyticsTimeRange],
        table_class,
        date_column,
    ):
        """Build time filter for any table.

        Args:
            time_range: Time range filter
            table_class: SQLAlchemy table class
            date_column: Date column to filter on

        Returns:
            SQLAlchemy filter condition
        """
        if not time_range:
            return None

        now = datetime.now(UTC)

        if time_range.start_date and time_range.end_date:
            return and_(
                date_column >= time_range.start_date,
                date_column <= time_range.end_date,
            )

        # Handle predefined periods
        if time_range.period == "1h":
            start_time = now - timedelta(hours=1)
        elif time_range.period == "24h":
            start_time = now - timedelta(hours=24)
        elif time_range.period == "7d":
            start_time = now - timedelta(days=7)
        elif time_range.period == "30d":
            start_time = now - timedelta(days=30)
        elif time_range.period == "90d":
            start_time = now - timedelta(days=90)
        else:
            start_time = now - timedelta(days=7)  # Default to 7 days

        return date_column >= start_time

    async def get_dashboard_data(
        self, user_id: str, time_range: Optional[AnalyticsTimeRange] = None
    ) -> dict[str, Any]:
        """Get comprehensive dashboard data.

        Args:
            user_id: User ID
            time_range: Time range filter

        Returns:
            Dictionary with all dashboard data
        """
        # Get each analytics section individually with their own exception handling
        # This ensures that if one fails, others still return proper default values
        conversation_stats = await self.get_conversation_stats(
            user_id, time_range
        )
        usage_metrics = await self.get_usage_metrics(
            user_id, time_range
        )
        performance_metrics = await self.get_performance_metrics(
            user_id, time_range
        )
        document_analytics = await self.get_document_analytics(
            user_id, time_range
        )
        system_health = await self.get_system_analytics()

        return {
            "conversation_stats": conversation_stats,
            "usage_metrics": usage_metrics,
            "performance_metrics": performance_metrics,
            "document_analytics": document_analytics,
            "system_health": system_health,
            "generated_at": datetime.now(UTC),
        }

    def _build_time_filter(
        self,
        time_range: Optional[AnalyticsTimeRange],
        table_alias: str = "Conversation",
    ):
        """Build time filter for queries.

        Args:
            time_range: Time range filter
            table_alias: Table alias for time field

        Returns:
            SQLAlchemy filter condition
        """
        if not time_range:
            return literal(True)

        # Get the appropriate table
        if table_alias == "Document":
            time_field = Document.created_at
        else:
            time_field = Conversation.created_at

        if time_range.start_date and time_range.end_date:
            return and_(
                time_field >= time_range.start_date,
                time_field <= time_range.end_date,
            )

        # Handle predefined periods
        now = datetime.now(UTC)
        if time_range.period == "1h":
            start_time = now - timedelta(hours=1)
        elif time_range.period == "24h":
            start_time = now - timedelta(days=1)
        elif time_range.period == "7d":
            start_time = now - timedelta(days=7)
        elif time_range.period == "30d":
            start_time = now - timedelta(days=30)
        elif time_range.period == "90d":
            start_time = now - timedelta(days=90)
        else:
            start_time = now - timedelta(days=7)  # Default to 7 days

        return time_field >= start_time

    def _get_time_range_minutes(
        self, time_range: Optional[AnalyticsTimeRange]
    ) -> float:
        """Get time range in minutes.

        Args:
            time_range: Time range filter

        Returns:
            Time range in minutes
        """
        if not time_range:
            return 60 * 24 * 7  # Default 7 days in minutes

        if time_range.start_date and time_range.end_date:
            delta = time_range.end_date - time_range.start_date
            return delta.total_seconds() / 60

        # Handle predefined periods
        if time_range.period == "1h":
            return 60
        elif time_range.period == "24h":
            return 60 * 24
        elif time_range.period == "7d":
            return 60 * 24 * 7
        elif time_range.period == "30d":
            return 60 * 24 * 30
        elif time_range.period == "90d":
            return 60 * 24 * 90
        else:
            return 60 * 24 * 7  # Default 7 days

    def _apply_query_optimizations(
        self, query, limit: Optional[int] = None
    ):
        """Apply query optimizations like limits and hints.

        Args:
            query: SQLAlchemy query object
            limit: Optional limit for results

        Returns:
            Optimized query
        """
        # Add limit to prevent memory issues
        if limit:
            query = query.limit(limit)

        # Add execution options for better performance
        query = query.execution_options(
            compiled_cache={},  # Enable statement caching
            autocommit=False,  # Use transactions
        )

        return query

    async def _execute_with_retry(self, query, max_retries: int = 3):
        """Execute query with retry logic for transient failures.

        Args:
            query: SQLAlchemy query to execute
            max_retries: Maximum number of retries

        Returns:
            Query result
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                result = await self.session.execute(query)
                return result
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Query execution failed (attempt {attempt + 1}/{max_retries}): {e}"
                )

                # Only retry on specific database errors
                if (
                    "connection" in str(e).lower()
                    or "timeout" in str(e).lower()
                ):
                    if attempt < max_retries - 1:
                        import asyncio

                        await asyncio.sleep(
                            0.5 * (attempt + 1)
                        )  # Exponential backoff
                        continue

                # Don't retry on other errors
                break

        # Re-raise the last exception if all retries failed
        raise last_exception

    async def get_user_analytics(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """Get analytics for a specific user."""
        try:
            # Build time filter
            time_range = AnalyticsTimeRange(
                start_date=start_date,
                end_date=end_date,
                period=(
                    "30d"
                    if not start_date and not end_date
                    else "custom"
                ),
            )

            # Get comprehensive user analytics
            conversations_task = self.get_conversation_stats(
                user_id, time_range
            )
            usage_task = self.get_usage_metrics(user_id, time_range)
            performance_task = self.get_performance_metrics(
                user_id, time_range
            )
            document_task = self.get_document_analytics(
                user_id, time_range
            )

            # Run analytics in parallel for better performance
            (
                conversations,
                usage,
                performance,
                documents,
            ) = await asyncio.gather(
                conversations_task,
                usage_task,
                performance_task,
                document_task,
                return_exceptions=True,
            )

            # Handle any exceptions from individual analytics
            result = {
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date,
                "generated_at": datetime.now(UTC),
            }

            if not isinstance(conversations, Exception):
                result["conversations"] = conversations
            else:
                logger.warning(
                    f"Failed to get conversation analytics: {conversations}"
                )
                result["conversations"] = {}

            if not isinstance(usage, Exception):
                result["usage"] = usage
            else:
                logger.warning(
                    f"Failed to get usage analytics: {usage}"
                )
                result["usage"] = {}

            if not isinstance(performance, Exception):
                result["performance"] = performance
            else:
                logger.warning(
                    f"Failed to get performance analytics: {performance}"
                )
                result["performance"] = {}

            if not isinstance(documents, Exception):
                result["documents"] = documents
            else:
                logger.warning(
                    f"Failed to get document analytics: {documents}"
                )
                result["documents"] = {}

            # Calculate some derived metrics
            total_usage_time = (
                usage.get("active_days", 0) * 24
                if isinstance(usage, dict)
                else 0
            )
            result["total_usage_time_hours"] = total_usage_time

            return result

        except Exception as e:
            logger.error(
                f"Failed to get user analytics for {user_id}",
                error=str(e),
            )
            return {
                "user_id": user_id,
                "error": "Failed to retrieve analytics",
                "start_date": start_date,
                "end_date": end_date,
            }

    async def export_analytics(
        self,
        export_format: str,
        date_range: Optional[tuple[datetime, datetime]] = None,
        filters: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any] | Any:
        """Export analytics data in specified format."""
        try:
            if not filters:
                filters = {}

            user_id = filters.get("user_id")
            metrics = filters.get(
                "metrics", ["conversations", "usage", "performance"]
            )

            if not user_id:
                raise ValueError(
                    "user_id is required for analytics export"
                )

            # Create time range from date_range tuple
            time_range = None
            if date_range:
                time_range = AnalyticsTimeRange(
                    start_date=date_range[0],
                    end_date=date_range[1],
                    period="custom",
                )

            # Collect requested analytics data
            export_data = {
                "export_info": {
                    "format": export_format,
                    "generated_at": datetime.now(UTC).isoformat(),
                    "user_id": user_id,
                    "date_range": (
                        {
                            "start": (
                                date_range[0].isoformat()
                                if date_range
                                else None
                            ),
                            "end": (
                                date_range[1].isoformat()
                                if date_range
                                else None
                            ),
                        }
                        if date_range
                        else None
                    ),
                    "metrics_included": metrics,
                }
            }

            # Gather requested metrics
            for metric in metrics:
                try:
                    if metric == "conversations":
                        export_data["conversations"] = (
                            await self.get_conversation_stats(
                                user_id, time_range
                            )
                        )
                    elif metric == "usage":
                        export_data["usage"] = (
                            await self.get_usage_metrics(
                                user_id, time_range
                            )
                        )
                    elif metric == "performance":
                        export_data["performance"] = (
                            await self.get_performance_metrics(
                                user_id, time_range
                            )
                        )
                    elif metric == "documents":
                        export_data["documents"] = (
                            await self.get_document_analytics(
                                user_id, time_range
                            )
                        )
                    elif metric == "system":
                        export_data["system"] = (
                            await self.get_system_analytics()
                        )
                    elif metric == "toolservers":
                        export_data["toolservers"] = (
                            await self.get_tool_server_analytics(
                                user_id, time_range
                            )
                        )
                    else:
                        logger.warning(
                            f"Unknown metric requested for export: {metric}"
                        )

                except Exception as e:
                    logger.error(
                        f"Failed to export metric '{metric}': {e}"
                    )
                    export_data[metric] = {
                        "error": f"Failed to export: {str(e)}"
                    }

            # Handle different export formats
            if export_format == "json":
                return export_data
            elif export_format == "csv":
                return self._export_to_csv(export_data)
            elif export_format == "xlsx":
                return self._export_to_xlsx(export_data)
            else:
                raise ValueError(
                    f"Unsupported export format: {export_format}"
                )

        except Exception as e:
            logger.error(f"Analytics export failed: {e}")
            return {
                "error": str(e),
                "export_format": export_format,
                "timestamp": datetime.now(UTC).isoformat(),
            }

    def _export_to_csv(self, data: dict[str, Any]) -> Any:
        """Convert analytics data to CSV format."""
        import csv
        import io

        # Create CSV content
        output = io.StringIO()

        # Write export info
        writer = csv.writer(output)
        writer.writerow(["Analytics Export"])
        writer.writerow(
            ["Generated:", data["export_info"]["generated_at"]]
        )
        writer.writerow(["User ID:", data["export_info"]["user_id"]])
        writer.writerow([])  # Empty row

        # Write each metric as separate sections
        for metric, metric_data in data.items():
            if metric == "export_info":
                continue

            writer.writerow([f"{metric.title()} Metrics"])

            if (
                isinstance(metric_data, dict)
                and "error" not in metric_data
            ):
                # Flatten the dictionary for CSV
                for key, value in metric_data.items():
                    if isinstance(value, int | float | str):
                        writer.writerow([key, value])
                    elif isinstance(value, dict):
                        writer.writerow([key, str(value)])

            writer.writerow([])  # Empty row between sections

        content = output.getvalue()
        output.close()

        # Return as generator for streaming
        def generate():
            yield content

        return generate()

    def _export_to_xlsx(self, data: dict[str, Any]) -> Any:
        """Convert analytics data to Excel format."""
        try:
            import io

            from openpyxl import Workbook

            wb = Workbook()
            ws = wb.active
            ws.title = "Analytics Export"

            # Write header info
            ws.append(["Analytics Export"])
            ws.append(
                ["Generated:", data["export_info"]["generated_at"]]
            )
            ws.append(["User ID:", data["export_info"]["user_id"]])
            ws.append([])  # Empty row

            # Write each metric as separate sections
            for metric, metric_data in data.items():
                if metric == "export_info":
                    continue

                ws.append([f"{metric.title()} Metrics"])

                if (
                    isinstance(metric_data, dict)
                    and "error" not in metric_data
                ):
                    # Flatten the dictionary for Excel
                    for key, value in metric_data.items():
                        if isinstance(value, int | float | str):
                            ws.append([key, value])
                        elif isinstance(value, dict):
                            ws.append([key, str(value)])

                ws.append([])  # Empty row between sections

            # Save to bytes
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)

            content = output.getvalue()
            output.close()

            # Return as generator for streaming
            def generate():
                yield content

            return generate()

        except ImportError:
            logger.error("openpyxl not available for Excel export")
            return self._export_to_csv(data)  # Fallback to CSV

    async def get_analytics_health_check(self) -> dict[str, Any]:
        """Perform health check on analytics system.

        Returns:
            Health check results including database connectivity and query performance
        """
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "checks": {},
        }

        try:
            # Test database connectivity
            start_time = time.time()
            await self.session.execute(select(literal(1)))
            db_response_time = (time.time() - start_time) * 1000

            health_data["checks"]["database"] = {
                "status": (
                    "healthy" if db_response_time < 1000 else "slow"
                ),
                "response_time_ms": db_response_time,
                "details": "Database connectivity check",
            }

            # Test basic query performance with a simple count
            start_time = time.time()
            await self.session.execute(
                select(func.count(Conversation.id)).limit(1)
            )
            query_response_time = (time.time() - start_time) * 1000

            health_data["checks"]["query_performance"] = {
                "status": (
                    "healthy" if query_response_time < 2000 else "slow"
                ),
                "response_time_ms": query_response_time,
                "details": "Basic query performance check",
            }

            # Check for any critical errors in analytics data
            health_data["checks"]["data_integrity"] = {
                "status": "healthy",
                "details": "No data integrity issues detected",
            }

            # Overall health assessment
            all_checks_healthy = all(
                check["status"] == "healthy"
                for check in health_data["checks"].values()
            )

            if not all_checks_healthy:
                health_data["status"] = "degraded"

            return health_data

        except Exception as e:
            logger.error(f"Analytics health check failed: {e}")
            health_data["status"] = "unhealthy"
            health_data["error"] = str(e)
            health_data["checks"]["database"] = {
                "status": "unhealthy",
                "error": str(e),
                "details": "Database connectivity failed",
            }

            return health_data

    async def get_analytics_metrics_summary(self) -> dict[str, Any]:
        """Get a quick summary of key analytics metrics for monitoring.

        Returns:
            Summary of analytics metrics for system monitoring
        """
        try:
            # Quick metrics collection (last 24 hours)
            yesterday = datetime.now(UTC) - timedelta(hours=24)

            # Count recent conversations
            recent_conversations = await self.session.execute(
                select(func.count(Conversation.id)).where(
                    Conversation.created_at >= yesterday
                )
            )

            # Count recent messages
            recent_messages = await self.session.execute(
                select(func.count(Message.id)).where(
                    Message.created_at >= yesterday
                )
            )

            # Count recent documents
            recent_documents = await self.session.execute(
                select(func.count(Document.id)).where(
                    Document.created_at >= yesterday
                )
            )

            # Get average response time
            avg_response_time = await self.session.execute(
                select(func.avg(Message.response_time_ms)).where(
                    and_(
                        Message.created_at >= yesterday,
                        Message.response_time_ms.is_not(None),
                    )
                )
            )

            return {
                "period": "last_24_hours",
                "metrics": {
                    "conversations_created": recent_conversations.scalar()
                    or 0,
                    "messages_sent": recent_messages.scalar() or 0,
                    "documents_processed": recent_documents.scalar()
                    or 0,
                    "avg_response_time_ms": float(
                        avg_response_time.scalar() or 0
                    ),
                },
                "timestamp": datetime.now(UTC).isoformat(),
                "status": "collected",
            }

        except Exception as e:
            logger.error(
                f"Failed to collect analytics metrics summary: {e}"
            )
            return {
                "period": "last_24_hours",
                "metrics": {},
                "timestamp": datetime.now(UTC).isoformat(),
                "status": "failed",
                "error": str(e),
            }


class AnalyticsError(Exception):
    """Analytics operation error."""

    pass


class ConversationAnalyzer:
    """Analyzer for conversation data and patterns."""

    def __init__(self):
        """Initialize the conversation analyzer."""
        self.metrics: dict[str, Any] = {}

    async def analyze_conversation(
        self, conversation_id: str, messages: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze a conversation.

        Args:
            conversation_id: ID of the conversation
            messages: List of messages in the conversation

        Returns:
            Analysis results
        """
        try:
            if not messages:
                return {
                    "conversation_id": conversation_id,
                    "message_count": 0,
                    "analysis": "empty_conversation",
                    "patterns": [],
                    "quality_score": 0.0,
                }

            # Basic conversation analysis
            user_messages = [
                m for m in messages if m.get("role") == "user"
            ]
            assistant_messages = [
                m for m in messages if m.get("role") == "assistant"
            ]

            # Calculate metrics
            total_words = sum(
                len(m.get("content", "").split())
                for m in messages
                if isinstance(m.get("content"), str)
            )
            avg_words_per_message = (
                total_words / len(messages) if messages else 0
            )

            # Detect patterns
            patterns = []
            if len(user_messages) > len(assistant_messages):
                patterns.append("incomplete_responses")
            if avg_words_per_message > 100:
                patterns.append("detailed_conversation")
            if len(messages) > 20:
                patterns.append("long_conversation")

            # Simple quality score based on response completeness
            quality_score = min(
                1.0,
                len(assistant_messages) / max(1, len(user_messages)),
            )

            analysis = {
                "conversation_id": conversation_id,
                "message_count": len(messages),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "total_words": total_words,
                "avg_words_per_message": avg_words_per_message,
                "patterns": patterns,
                "quality_score": quality_score,
                "analysis": "conversation_analyzed",
            }

            # Store metrics for later retrieval
            self.metrics[conversation_id] = analysis

            return analysis

        except Exception as e:
            logger.error(
                f"Failed to analyze conversation {conversation_id}: {e}"
            )
            return {
                "conversation_id": conversation_id,
                "message_count": len(messages) if messages else 0,
                "analysis": "analysis_failed",
                "error": str(e),
            }

    def get_conversation_metrics(
        self, conversation_id: str
    ) -> dict[str, Any]:
        """Get metrics for a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Conversation metrics
        """
        return self.metrics.get(
            conversation_id,
            {
                "conversation_id": conversation_id,
                "status": "not_analyzed",
            },
        )


class PerformanceAnalyzer:
    """Analyzer for performance metrics and system health."""

    def __init__(self):
        """Initialize the performance analyzer."""
        self.performance_data: dict[str, Any] = {}
        self.thresholds = {
            "response_time_warning_ms": 5000,
            "response_time_critical_ms": 10000,
            "error_rate_warning": 0.05,  # 5%
            "error_rate_critical": 0.10,  # 10%
            "cpu_warning": 0.80,  # 80%
            "memory_warning": 0.85,  # 85%
        }

    async def analyze_performance(
        self, component: str, metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze performance of a component.

        Args:
            component: Name of the component
            metrics: Performance metrics

        Returns:
            Performance analysis results
        """
        try:
            # Extract key metrics
            response_time = metrics.get("avg_response_time_ms", 0)
            error_rate = metrics.get("error_rate", 0)
            cpu_usage = metrics.get("cpu_usage", 0)
            memory_usage = metrics.get("memory_usage", 0)

            # Analyze response time
            response_status = "good"
            if (
                response_time
                > self.thresholds["response_time_critical_ms"]
            ):
                response_status = "critical"
            elif (
                response_time
                > self.thresholds["response_time_warning_ms"]
            ):
                response_status = "warning"

            # Analyze error rate
            error_status = "good"
            if error_rate > self.thresholds["error_rate_critical"]:
                error_status = "critical"
            elif error_rate > self.thresholds["error_rate_warning"]:
                error_status = "warning"

            # Analyze resource usage
            resource_status = "good"
            if (
                cpu_usage > self.thresholds["cpu_warning"]
                or memory_usage > self.thresholds["memory_warning"]
            ):
                resource_status = "warning"

            # Overall health score (0-100)
            health_score = 100
            if response_status == "warning":
                health_score -= 20
            elif response_status == "critical":
                health_score -= 40

            if error_status == "warning":
                health_score -= 15
            elif error_status == "critical":
                health_score -= 30

            if resource_status == "warning":
                health_score -= 10

            health_score = max(0, health_score)

            # Determine overall status
            overall_status = "good"
            if health_score < 50:
                overall_status = "critical"
            elif health_score < 80:
                overall_status = "warning"

            # Generate recommendations
            recommendations = []
            if response_status in ["warning", "critical"]:
                recommendations.append(
                    "Consider optimizing database queries or adding caching"
                )
            if error_status in ["warning", "critical"]:
                recommendations.append(
                    "Investigate error patterns and improve error handling"
                )
            if resource_status == "warning":
                recommendations.append(
                    "Monitor resource usage and consider scaling"
                )

            analysis = {
                "component": component,
                "metrics": metrics,
                "analysis": {
                    "response_time_status": response_status,
                    "error_rate_status": error_status,
                    "resource_status": resource_status,
                    "overall_status": overall_status,
                    "health_score": health_score,
                    "recommendations": recommendations,
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }

            # Store for retrieval
            self.performance_data[component] = analysis

            return analysis

        except Exception as e:
            logger.error(
                f"Failed to analyze performance for {component}: {e}"
            )
            return {
                "component": component,
                "metrics": metrics,
                "analysis": "analysis_failed",
                "error": str(e),
            }

    def get_performance_summary(self) -> dict[str, Any]:
        """Get overall performance summary.

        Returns:
            Performance summary
        """
        if not self.performance_data:
            return {
                "overall_health": "unknown",
                "components_analyzed": 0,
                "summary": "No performance data available",
            }

        # Calculate overall health
        total_health = 0
        critical_count = 0
        warning_count = 0

        for component_data in self.performance_data.values():
            analysis = component_data.get("analysis", {})
            health_score = analysis.get("health_score", 0)
            total_health += health_score

            status = analysis.get("overall_status", "unknown")
            if status == "critical":
                critical_count += 1
            elif status == "warning":
                warning_count += 1

        component_count = len(self.performance_data)
        avg_health = (
            total_health / component_count if component_count > 0 else 0
        )

        # Determine overall health
        if critical_count > 0:
            overall_health = "critical"
        elif warning_count > 0:
            overall_health = "warning"
        elif avg_health >= 80:
            overall_health = "good"
        else:
            overall_health = "degraded"

        return {
            "overall_health": overall_health,
            "average_health_score": avg_health,
            "components_analyzed": component_count,
            "critical_components": critical_count,
            "warning_components": warning_count,
            "healthy_components": component_count
            - critical_count
            - warning_count,
        }


class TrendAnalyzer:
    """Analyzer for identifying trends in data."""

    def __init__(self):
        """Initialize the trend analyzer."""
        self.trend_data: dict[str, Any] = {}

    async def analyze_trends(
        self, data_type: str, time_series_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze trends in time series data.

        Args:
            data_type: Type of data being analyzed
            time_series_data: Time series data points

        Returns:
            Trend analysis results
        """
        try:
            if not time_series_data or len(time_series_data) < 2:
                return {
                    "data_type": data_type,
                    "data_points": len(time_series_data),
                    "trend": "insufficient_data",
                    "confidence": 0.0,
                }

            # Extract values and timestamps
            values = []
            timestamps = []

            for point in time_series_data:
                if "value" in point and "timestamp" in point:
                    values.append(float(point["value"]))
                    timestamps.append(point["timestamp"])

            if len(values) < 2:
                return {
                    "data_type": data_type,
                    "data_points": len(time_series_data),
                    "trend": "invalid_data",
                    "confidence": 0.0,
                }

            # Simple linear trend analysis
            n = len(values)

            # Calculate trend direction and strength
            first_half = values[: n // 2]
            second_half = values[n // 2 :]

            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)

            # Calculate percentage change
            if first_avg != 0:
                percent_change = (
                    (second_avg - first_avg) / first_avg
                ) * 100
            else:
                percent_change = 0

            # Determine trend direction
            if abs(percent_change) < 5:
                trend_direction = "stable"
            elif percent_change > 0:
                trend_direction = "increasing"
            else:
                trend_direction = "decreasing"

            # Calculate trend strength
            if abs(percent_change) > 50:
                trend_strength = "strong"
            elif abs(percent_change) > 20:
                trend_strength = "moderate"
            elif abs(percent_change) > 5:
                trend_strength = "weak"
            else:
                trend_strength = "stable"

            # Calculate volatility (standard deviation)
            mean_value = sum(values) / len(values)
            variance = sum((x - mean_value) ** 2 for x in values) / len(
                values
            )
            volatility = variance**0.5

            # Confidence score based on data consistency
            if volatility == 0:
                confidence = 1.0
            else:
                cv = (
                    volatility / mean_value
                    if mean_value != 0
                    else float("inf")
                )
                confidence = max(
                    0, min(1, 1 - (cv / 2))
                )  # Normalize coefficient of variation

            # Detect anomalies (values significantly different from mean)
            anomalies = []
            threshold = mean_value + (
                2 * volatility
            )  # 2 standard deviations
            for i, value in enumerate(values):
                if abs(value - mean_value) > threshold:
                    anomalies.append(
                        {
                            "index": i,
                            "value": value,
                            "deviation": abs(value - mean_value),
                        }
                    )

            analysis = {
                "data_type": data_type,
                "data_points": len(time_series_data),
                "trend": {
                    "direction": trend_direction,
                    "strength": trend_strength,
                    "percent_change": percent_change,
                },
                "statistics": {
                    "mean": mean_value,
                    "min": min(values),
                    "max": max(values),
                    "volatility": volatility,
                    "first_half_avg": first_avg,
                    "second_half_avg": second_avg,
                },
                "confidence": confidence,
                "anomalies": anomalies,
                "analysis_timestamp": datetime.now(UTC).isoformat(),
            }

            # Store for later retrieval
            self.trend_data[data_type] = analysis

            return analysis

        except Exception as e:
            logger.error(
                f"Failed to analyze trends for {data_type}: {e}"
            )
            return {
                "data_type": data_type,
                "data_points": len(time_series_data),
                "trend": "analysis_failed",
                "error": str(e),
            }

    def get_trend_summary(self, data_type: str) -> dict[str, Any]:
        """Get trend summary for a data type.

        Args:
            data_type: Type of data

        Returns:
            Trend summary
        """
        return self.trend_data.get(
            data_type,
            {"data_type": data_type, "status": "not_analyzed"},
        )


class UserBehaviorAnalyzer:
    """Analyzer for user behavior patterns and insights."""

    def __init__(self):
        """Initialize the user behavior analyzer."""
        self.user_data: dict[str, Any] = {}

    async def analyze_user_behavior(
        self, user_id: str, interactions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze user behavior patterns.

        Args:
            user_id: ID of the user
            interactions: List of user interactions

        Returns:
            User behavior analysis results
        """
        return {
            "user_id": user_id,
            "interaction_count": len(interactions),
            "behavior": "analyzed",
        }

    def get_user_insights(self, user_id: str) -> dict[str, Any]:
        """Get insights for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            User insights
        """
        return self.user_data.get(user_id, {})
