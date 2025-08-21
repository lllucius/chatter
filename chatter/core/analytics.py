"""Analytics service for generating statistics and insights."""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, func, and_, or_, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import get_settings
from chatter.models.conversation import Conversation, Message, MessageRole
from chatter.models.document import Document, DocumentChunk, DocumentStatus
from chatter.models.profile import Profile
from chatter.models.user import User
from chatter.schemas.analytics import AnalyticsTimeRange
from chatter.utils.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class AnalyticsService:
    """Service for analytics and statistics generation."""
    
    def __init__(self, session: AsyncSession):
        """Initialize analytics service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def get_conversation_stats(
        self,
        user_id: str,
        time_range: Optional[AnalyticsTimeRange] = None
    ) -> Dict[str, Any]:
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
                    and_(
                        Conversation.user_id == user_id,
                        time_filter
                    )
                )
            )
            total_conversations = total_conversations_result.scalar()
            
            # Conversations by status
            status_result = await self.session.execute(
                select(
                    Conversation.status,
                    func.count(Conversation.id)
                ).where(
                    and_(
                        Conversation.user_id == user_id,
                        time_filter
                    )
                ).group_by(Conversation.status)
            )
            conversations_by_status = {status: count for status, count in status_result.all()}
            
            # Total messages
            total_messages_result = await self.session.execute(
                select(func.count(Message.id))
                .select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        time_filter
                    )
                )
            )
            total_messages = total_messages_result.scalar()
            
            # Messages by role
            role_result = await self.session.execute(
                select(
                    Message.role,
                    func.count(Message.id)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        time_filter
                    )
                ).group_by(Message.role)
            )
            messages_by_role = {role.value: count for role, count in role_result.all()}
            
            # Token usage
            token_stats_result = await self.session.execute(
                select(
                    func.sum(Message.prompt_tokens),
                    func.sum(Message.completion_tokens),
                    func.sum(Message.total_tokens),
                    func.sum(Message.cost),
                    func.avg(Message.response_time_ms)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        time_filter
                    )
                )
            )
            
            token_stats = token_stats_result.first()
            total_prompt_tokens = token_stats[0] or 0
            total_completion_tokens = token_stats[1] or 0
            total_tokens = token_stats[2] or 0
            total_cost = float(token_stats[3] or 0)
            avg_response_time = float(token_stats[4] or 0)
            
            # Conversations by date
            date_result = await self.session.execute(
                select(
                    func.date(Conversation.created_at),
                    func.count(Conversation.id)
                ).where(
                    and_(
                        Conversation.user_id == user_id,
                        time_filter
                    )
                ).group_by(func.date(Conversation.created_at))
                .order_by(func.date(Conversation.created_at))
            )
            conversations_by_date = {str(date): count for date, count in date_result.all()}
            
            # Most active hours
            hour_result = await self.session.execute(
                select(
                    func.extract('hour', Conversation.created_at),
                    func.count(Conversation.id)
                ).where(
                    and_(
                        Conversation.user_id == user_id,
                        time_filter
                    )
                ).group_by(func.extract('hour', Conversation.created_at))
            )
            most_active_hours = {str(int(hour)): count for hour, count in hour_result.all()}
            
            # Popular models and providers
            model_result = await self.session.execute(
                select(
                    Message.model_used,
                    func.count(Message.id)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.model_used.is_not(None),
                        time_filter
                    )
                ).group_by(Message.model_used)
            )
            popular_models = {model: count for model, count in model_result.all() if model}
            
            provider_result = await self.session.execute(
                select(
                    Message.provider_used,
                    func.count(Message.id)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.provider_used.is_not(None),
                        time_filter
                    )
                ).group_by(Message.provider_used)
            )
            popular_providers = {provider: count for provider, count in provider_result.all() if provider}
            
            return {
                "total_conversations": total_conversations,
                "conversations_by_status": conversations_by_status,
                "total_messages": total_messages,
                "messages_by_role": messages_by_role,
                "avg_messages_per_conversation": total_messages / total_conversations if total_conversations > 0 else 0,
                "total_tokens_used": total_tokens,
                "total_cost": total_cost,
                "avg_response_time_ms": avg_response_time,
                "conversations_by_date": conversations_by_date,
                "most_active_hours": most_active_hours,
                "popular_models": popular_models,
                "popular_providers": popular_providers,
            }
            
        except Exception as e:
            logger.error("Failed to get conversation stats", error=str(e))
            return {}
    
    async def get_usage_metrics(
        self,
        user_id: str,
        time_range: Optional[AnalyticsTimeRange] = None
    ) -> Dict[str, Any]:
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
                    func.sum(Message.cost)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        time_filter
                    )
                )
            )
            
            usage_totals = total_usage_result.first()
            total_prompt_tokens = usage_totals[0] or 0
            total_completion_tokens = usage_totals[1] or 0
            total_tokens = usage_totals[2] or 0
            total_cost = float(usage_totals[3] or 0)
            
            # Usage by model
            model_usage_result = await self.session.execute(
                select(
                    Message.model_used,
                    func.sum(Message.total_tokens),
                    func.sum(Message.cost)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.model_used.is_not(None),
                        time_filter
                    )
                ).group_by(Message.model_used)
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
                    func.sum(Message.cost)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.provider_used.is_not(None),
                        time_filter
                    )
                ).group_by(Message.provider_used)
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
                    func.sum(Message.cost)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        Message.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
                    )
                ).group_by(func.date(Message.created_at))
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
                select(
                    func.avg(Message.response_time_ms)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        Message.response_time_ms.is_not(None),
                        time_filter
                    )
                )
            )
            avg_response_time = float(response_time_result.scalar() or 0)
            
            # Response times by model
            model_response_result = await self.session.execute(
                select(
                    Message.model_used,
                    func.avg(Message.response_time_ms)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.model_used.is_not(None),
                        Message.response_time_ms.is_not(None),
                        time_filter
                    )
                ).group_by(Message.model_used)
            )
            response_times_by_model = {
                model: float(time) for model, time in model_response_result.all() if model
            }
            
            # Activity metrics
            activity_result = await self.session.execute(
                select(
                    func.count(func.distinct(func.date(Conversation.created_at))),
                    func.extract('hour', func.max(Conversation.created_at)),
                    func.count(Conversation.id) / func.count(func.distinct(func.date(Conversation.created_at)))
                ).where(
                    and_(
                        Conversation.user_id == user_id,
                        time_filter
                    )
                )
            )
            
            activity_stats = activity_result.first()
            active_days = activity_stats[0] or 0
            peak_usage_hour = int(activity_stats[1] or 0)
            conversations_per_day = float(activity_stats[2] or 0)
            
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
            return {}
    
    async def get_performance_metrics(
        self,
        user_id: str,
        time_range: Optional[AnalyticsTimeRange] = None
    ) -> Dict[str, Any]:
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
                    func.percentile_cont(0.5).within_group(Message.response_time_ms),
                    func.percentile_cont(0.95).within_group(Message.response_time_ms),
                    func.percentile_cont(0.99).within_group(Message.response_time_ms)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        Message.response_time_ms.is_not(None),
                        time_filter
                    )
                )
            )
            
            response_stats = response_stats_result.first()
            avg_response_time = float(response_stats[0] or 0)
            median_response_time = float(response_stats[1] or 0)
            p95_response_time = float(response_stats[2] or 0)
            p99_response_time = float(response_stats[3] or 0)
            
            # Throughput metrics
            throughput_result = await self.session.execute(
                select(
                    func.count(Message.id),
                    func.sum(Message.total_tokens)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.role == MessageRole.ASSISTANT,
                        time_filter
                    )
                )
            )
            
            throughput_stats = throughput_result.first()
            total_requests = throughput_stats[0] or 0
            total_tokens = throughput_stats[1] or 0
            
            # Calculate per-minute rates (assuming time range)
            time_range_minutes = self._get_time_range_minutes(time_range)
            requests_per_minute = total_requests / time_range_minutes if time_range_minutes > 0 else 0
            tokens_per_minute = total_tokens / time_range_minutes if time_range_minutes > 0 else 0
            
            # Error metrics (placeholder - would need error tracking)
            total_errors = 0
            error_rate = 0.0
            errors_by_type = {}
            
            # Performance by model
            model_performance_result = await self.session.execute(
                select(
                    Message.model_used,
                    func.avg(Message.response_time_ms),
                    func.count(Message.id),
                    func.sum(Message.total_tokens)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.model_used.is_not(None),
                        Message.response_time_ms.is_not(None),
                        time_filter
                    )
                ).group_by(Message.model_used)
            )
            
            performance_by_model = {}
            for model, avg_time, count, tokens in model_performance_result.all():
                if model:
                    performance_by_model[model] = {
                        "avg_response_time_ms": float(avg_time),
                        "total_requests": count,
                        "total_tokens": tokens or 0,
                        "tokens_per_request": (tokens or 0) / count if count > 0 else 0
                    }
            
            # Performance by provider
            provider_performance_result = await self.session.execute(
                select(
                    Message.provider_used,
                    func.avg(Message.response_time_ms),
                    func.count(Message.id),
                    func.sum(Message.total_tokens)
                ).select_from(Message)
                .join(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Message.provider_used.is_not(None),
                        Message.response_time_ms.is_not(None),
                        time_filter
                    )
                ).group_by(Message.provider_used)
            )
            
            performance_by_provider = {}
            for provider, avg_time, count, tokens in provider_performance_result.all():
                if provider:
                    performance_by_provider[provider] = {
                        "avg_response_time_ms": float(avg_time),
                        "total_requests": count,
                        "total_tokens": tokens or 0,
                        "tokens_per_request": (tokens or 0) / count if count > 0 else 0
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
                "database_response_time_ms": 0.0,  # Placeholder
                "vector_search_time_ms": 0.0,  # Placeholder
                "embedding_generation_time_ms": 0.0,  # Placeholder
            }
            
        except Exception as e:
            logger.error("Failed to get performance metrics", error=str(e))
            return {}
    
    async def get_document_analytics(
        self,
        user_id: str,
        time_range: Optional[AnalyticsTimeRange] = None
    ) -> Dict[str, Any]:
        """Get document analytics.
        
        Args:
            user_id: User ID
            time_range: Time range filter
            
        Returns:
            Dictionary with document analytics
        """
        try:
            time_filter = self._build_time_filter(time_range, "Document")
            
            # Document counts
            total_docs_result = await self.session.execute(
                select(func.count(Document.id)).where(
                    and_(
                        Document.owner_id == user_id,
                        time_filter
                    )
                )
            )
            total_documents = total_docs_result.scalar()
            
            # Documents by status
            status_result = await self.session.execute(
                select(
                    Document.status,
                    func.count(Document.id)
                ).where(
                    and_(
                        Document.owner_id == user_id,
                        time_filter
                    )
                ).group_by(Document.status)
            )
            documents_by_status = {status.value: count for status, count in status_result.all()}
            
            # Documents by type
            type_result = await self.session.execute(
                select(
                    Document.document_type,
                    func.count(Document.id)
                ).where(
                    and_(
                        Document.owner_id == user_id,
                        time_filter
                    )
                ).group_by(Document.document_type)
            )
            documents_by_type = {doc_type.value: count for doc_type, count in type_result.all()}
            
            # Processing metrics
            processing_result = await self.session.execute(
                select(
                    func.avg(
                        func.extract('epoch', Document.processing_completed_at) -
                        func.extract('epoch', Document.processing_started_at)
                    ),
                    func.count(Document.id).filter(Document.status == DocumentStatus.PROCESSED),
                    func.count(Document.id),
                    func.sum(Document.chunk_count),
                    func.avg(Document.chunk_count)
                ).where(
                    and_(
                        Document.owner_id == user_id,
                        Document.processing_started_at.is_not(None),
                        time_filter
                    )
                )
            )
            
            processing_stats = processing_result.first()
            avg_processing_time = float(processing_stats[0] or 0)
            processed_docs = processing_stats[1] or 0
            total_docs = processing_stats[2] or 0
            total_chunks = processing_stats[3] or 0
            avg_chunks = float(processing_stats[4] or 0)
            
            processing_success_rate = processed_docs / total_docs if total_docs > 0 else 0
            
            # Storage metrics
            storage_result = await self.session.execute(
                select(
                    func.sum(Document.file_size),
                    func.avg(Document.file_size)
                ).where(
                    and_(
                        Document.owner_id == user_id,
                        time_filter
                    )
                )
            )
            
            storage_stats = storage_result.first()
            total_storage = storage_stats[0] or 0
            avg_size = float(storage_stats[1] or 0)
            
            # Storage by type
            storage_by_type_result = await self.session.execute(
                select(
                    Document.document_type,
                    func.sum(Document.file_size)
                ).where(
                    and_(
                        Document.owner_id == user_id,
                        time_filter
                    )
                ).group_by(Document.document_type)
            )
            storage_by_type = {doc_type.value: size for doc_type, size in storage_by_type_result.all()}
            
            # Search and access metrics
            search_result = await self.session.execute(
                select(
                    func.sum(Document.search_count),
                    func.sum(Document.view_count)
                ).where(
                    and_(
                        Document.owner_id == user_id,
                        time_filter
                    )
                )
            )
            
            search_stats = search_result.first()
            total_searches = search_stats[0] or 0
            total_views = search_stats[1] or 0
            
            # Most viewed documents
            most_viewed_result = await self.session.execute(
                select(
                    Document.id,
                    Document.filename,
                    Document.view_count
                ).where(
                    and_(
                        Document.owner_id == user_id,
                        time_filter
                    )
                ).order_by(desc(Document.view_count))
                .limit(10)
            )
            
            most_viewed_documents = [
                {
                    "id": doc_id,
                    "filename": filename,
                    "view_count": view_count
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
                    "private": total_documents,  # Simplified
                    "public": 0,
                    "shared": 0
                }
            }
            
        except Exception as e:
            logger.error("Failed to get document analytics", error=str(e))
            return {}
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide analytics.
        
        Returns:
            Dictionary with system analytics
        """
        try:
            # User activity
            user_activity_result = await self.session.execute(
                select(
                    func.count(User.id),
                    func.count(User.id).filter(User.last_login_at >= datetime.now(timezone.utc) - timedelta(days=1)),
                    func.count(User.id).filter(User.last_login_at >= datetime.now(timezone.utc) - timedelta(days=7)),
                    func.count(User.id).filter(User.last_login_at >= datetime.now(timezone.utc) - timedelta(days=30))
                )
            )
            
            user_stats = user_activity_result.first()
            total_users = user_stats[0] or 0
            active_users_today = user_stats[1] or 0
            active_users_week = user_stats[2] or 0
            active_users_month = user_stats[3] or 0
            
            # System health (placeholder values)
            system_health = {
                "system_uptime_seconds": 0.0,
                "avg_cpu_usage": 0.0,
                "avg_memory_usage": 0.0,
                "database_connections": 0,
            }
            
            # API metrics (placeholder values)
            api_metrics = {
                "total_api_requests": 0,
                "requests_per_endpoint": {},
                "avg_api_response_time": 0.0,
                "api_error_rate": 0.0,
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
                "vector_database_size_bytes": 0,  # Placeholder
                "cache_hit_rate": 0.0,  # Placeholder
            }
            
        except Exception as e:
            logger.error("Failed to get system analytics", error=str(e))
            return {}
    
    async def get_dashboard_data(
        self,
        user_id: str,
        time_range: Optional[AnalyticsTimeRange] = None
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data.
        
        Args:
            user_id: User ID
            time_range: Time range filter
            
        Returns:
            Dictionary with all dashboard data
        """
        try:
            # Run all analytics in parallel
            conversation_task = self.get_conversation_stats(user_id, time_range)
            usage_task = self.get_usage_metrics(user_id, time_range)
            performance_task = self.get_performance_metrics(user_id, time_range)
            document_task = self.get_document_analytics(user_id, time_range)
            system_task = self.get_system_analytics()
            
            # Wait for all tasks to complete
            conversation_stats, usage_metrics, performance_metrics, document_analytics, system_health = await asyncio.gather(
                conversation_task, usage_task, performance_task, document_task, system_task
            )
            
            return {
                "conversation_stats": conversation_stats,
                "usage_metrics": usage_metrics,
                "performance_metrics": performance_metrics,
                "document_analytics": document_analytics,
                "system_health": system_health,
                "custom_metrics": [],  # Placeholder for custom metrics
                "generated_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error("Failed to get dashboard data", error=str(e))
            return {}
    
    def _build_time_filter(
        self,
        time_range: Optional[AnalyticsTimeRange],
        table_alias: str = "Conversation"
    ):
        """Build time filter for queries.
        
        Args:
            time_range: Time range filter
            table_alias: Table alias for time field
            
        Returns:
            SQLAlchemy filter condition
        """
        if not time_range:
            return True
        
        # Get the appropriate table
        if table_alias == "Document":
            time_field = Document.created_at
        else:
            time_field = Conversation.created_at
        
        if time_range.start_date and time_range.end_date:
            return and_(
                time_field >= time_range.start_date,
                time_field <= time_range.end_date
            )
        
        # Handle predefined periods
        now = datetime.now(timezone.utc)
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
    
    def _get_time_range_minutes(self, time_range: Optional[AnalyticsTimeRange]) -> float:
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


class AnalyticsError(Exception):
    """Analytics operation error."""
    pass