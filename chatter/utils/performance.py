"""Performance optimization utilities for model registry."""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chatter.models.registry import ModelDef, ModelType, Provider
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class QueryOptimizer:
    """Optimized database query implementations."""

    def __init__(self, session: AsyncSession):
        """Initialize query optimizer.

        Args:
            session: Database session
        """
        self.session = session

    async def list_models_optimized(
        self,
        provider_id: str | None = None,
        model_type: ModelType | None = None,
        active_only: bool = True,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[ModelDef], int]:
        """Optimized model listing with efficient counting.

        Args:
            provider_id: Filter by provider ID
            model_type: Filter by model type
            active_only: Filter by active status
            page: Page number
            per_page: Items per page

        Returns:
            Tuple of (models, total_count)
        """
        # Build filter conditions
        conditions = []
        if provider_id:
            conditions.append(ModelDef.provider_id == provider_id)
        if model_type:
            conditions.append(ModelDef.model_type == model_type)
        if active_only:
            conditions.append(ModelDef.is_active)

        where_clause = and_(*conditions) if conditions else None

        # Get count efficiently without subquery
        count_query = select(func.count(ModelDef.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total = await self.session.scalar(count_query) or 0

        # Get data with same conditions
        data_query = (
            select(ModelDef)
            .options(selectinload(ModelDef.provider))
            .order_by(ModelDef.is_default.desc(), ModelDef.display_name)
        )

        if where_clause is not None:
            data_query = data_query.where(where_clause)

        data_query = data_query.offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(data_query)
        models = result.scalars().all()

        return list(models), total

    async def list_providers_optimized(
        self,
        provider_type: str | None = None,
        active_only: bool = True,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Provider], int]:
        """Optimized provider listing with efficient counting.

        Args:
            provider_type: Filter by provider type
            active_only: Filter by active status
            page: Page number
            per_page: Items per page

        Returns:
            Tuple of (providers, total_count)
        """
        # Build filter conditions
        conditions = []
        if provider_type:
            conditions.append(Provider.provider_type == provider_type)
        if active_only:
            conditions.append(Provider.is_active)

        where_clause = and_(*conditions) if conditions else None

        # Get count efficiently
        count_query = select(func.count(Provider.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total = await self.session.scalar(count_query) or 0

        # Get data
        data_query = select(Provider).order_by(
            Provider.is_default.desc(), Provider.display_name
        )

        if where_clause is not None:
            data_query = data_query.where(where_clause)

        data_query = data_query.offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(data_query)
        providers = result.scalars().all()

        return list(providers), total

    async def get_default_provider_optimized(
        self, model_type: ModelType
    ) -> Provider | None:
        """Get default provider for model type with optimized query.

        Args:
            model_type: Model type to get default for

        Returns:
            Default provider or None
        """
        # Single optimized query using EXISTS subquery
        query = (
            select(Provider)
            .where(
                Provider.is_active,
                Provider.id.in_(
                    select(ModelDef.provider_id)
                    .where(
                        ModelDef.model_type == model_type,
                        ModelDef.is_active,
                        ModelDef.is_default,
                    )
                    .distinct()
                )
            )
            .order_by(Provider.is_default.desc())
            .limit(1)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_provider_model_counts(
        self, provider_ids: list[str]
    ) -> dict[str, dict[str, int]]:
        """Get model counts by type for multiple providers efficiently.

        Args:
            provider_ids: List of provider IDs

        Returns:
            Dict mapping provider_id -> {model_type: count}
        """
        if not provider_ids:
            return {}

        # Single query to get all counts
        query = (
            select(
                ModelDef.provider_id,
                ModelDef.model_type,
                func.count(ModelDef.id).label('count')
            )
            .where(
                ModelDef.provider_id.in_(provider_ids),
                ModelDef.is_active
            )
            .group_by(ModelDef.provider_id, ModelDef.model_type)
        )

        result = await self.session.execute(query)

        # Build result dictionary
        counts = {}
        for row in result:
            provider_id = row.provider_id
            model_type = row.model_type.value
            count = row.count

            if provider_id not in counts:
                counts[provider_id] = {}
            counts[provider_id][model_type] = count

        return counts


class PerformanceMetrics:
    """Track and measure query performance."""

    def __init__(self):
        """Initialize performance metrics."""
        self.query_times = {}
        self.query_counts = {}

    @asynccontextmanager
    async def measure_query(self, operation: str) -> AsyncGenerator[None, None]:
        """Context manager to measure query execution time.

        Args:
            operation: Name of the operation being measured
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Track metrics
            if operation not in self.query_times:
                self.query_times[operation] = []
                self.query_counts[operation] = 0

            self.query_times[operation].append(duration)
            self.query_counts[operation] += 1

            # Keep only last 100 measurements
            if len(self.query_times[operation]) > 100:
                self.query_times[operation] = self.query_times[operation][-100:]

            # Log slow queries
            if duration > 1000:  # Log queries over 1 second
                logger.warning(
                    "Slow query detected",
                    operation=operation,
                    duration_ms=duration,
                )

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance metrics summary.

        Returns:
            Performance metrics dictionary
        """
        summary = {}

        for operation, times in self.query_times.items():
            if not times:
                continue

            summary[operation] = {
                'count': self.query_counts[operation],
                'avg_ms': sum(times) / len(times),
                'min_ms': min(times),
                'max_ms': max(times),
                'p95_ms': sorted(times)[int(len(times) * 0.95)] if len(times) > 20 else max(times),
            }

        return summary


class BulkOperations:
    """Efficient bulk database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize bulk operations.

        Args:
            session: Database session
        """
        self.session = session

    async def bulk_update_model_status(
        self,
        model_ids: list[str],
        is_active: bool,
    ) -> int:
        """Bulk update model active status.

        Args:
            model_ids: List of model IDs to update
            is_active: New active status

        Returns:
            Number of models updated
        """
        if not model_ids:
            return 0

        # Use bulk update for efficiency
        from sqlalchemy import update

        result = await self.session.execute(
            update(ModelDef)
            .where(ModelDef.id.in_(model_ids))
            .values(is_active=is_active)
        )

        await self.session.commit()
        return result.rowcount

    async def bulk_update_provider_status(
        self,
        provider_ids: list[str],
        is_active: bool,
    ) -> int:
        """Bulk update provider active status.

        Args:
            provider_ids: List of provider IDs to update
            is_active: New active status

        Returns:
            Number of providers updated
        """
        if not provider_ids:
            return 0

        from sqlalchemy import update

        result = await self.session.execute(
            update(Provider)
            .where(Provider.id.in_(provider_ids))
            .values(is_active=is_active)
        )

        await self.session.commit()
        return result.rowcount

    async def bulk_create_models(
        self,
        model_data_list: list[dict[str, Any]],
    ) -> list[str]:
        """Bulk create multiple models efficiently.

        Args:
            model_data_list: List of model data dictionaries

        Returns:
            List of created model IDs
        """
        if not model_data_list:
            return []

        # Validate all models first
        created_ids = []
        models_to_create = []

        for model_data in model_data_list:
            # Create model instance
            model = ModelDef(**model_data)
            models_to_create.append(model)
            created_ids.append(model.id)

        # Bulk insert
        self.session.add_all(models_to_create)
        await self.session.commit()

        return created_ids


# Global performance metrics instance
_performance_metrics = PerformanceMetrics()


def get_performance_metrics() -> PerformanceMetrics:
    """Get the global performance metrics instance.

    Returns:
        PerformanceMetrics instance
    """
    return _performance_metrics


class DatabaseIndexRecommendations:
    """Generate database index recommendations based on query patterns."""

    @staticmethod
    def get_recommended_indexes() -> list[str]:
        """Get recommended database indexes for performance.

        Returns:
            List of SQL CREATE INDEX statements
        """
        return [
            # Model queries optimization
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_models_provider_type_active
               ON model_defs(provider_id, model_type, is_active);""",

            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_models_default_type
               ON model_defs(model_type, is_default) WHERE is_active = true;""",

            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_models_list_query
               ON model_defs(provider_id, model_type, is_active, is_default, display_name);""",

            # Provider queries optimization
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_providers_type_active
               ON providers(provider_type, is_active);""",

            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_providers_list_query
               ON providers(provider_type, is_active, is_default, display_name);""",

            # Embedding space queries optimization
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_embedding_spaces_model_active
               ON embedding_spaces(model_id, is_active);""",

            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_embedding_spaces_list_query
               ON embedding_spaces(model_id, is_active, is_default, display_name);""",

            # Audit logging optimization
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp_type
               ON audit_logs(timestamp, event_type);""",

            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_timestamp
               ON audit_logs(user_id, timestamp);""",

            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_resource
               ON audit_logs(resource_type, resource_id);""",
        ]

    @staticmethod
    async def apply_recommended_indexes(session: AsyncSession) -> list[str]:
        """Apply recommended indexes to the database.

        Args:
            session: Database session

        Returns:
            List of successfully applied indexes
        """
        applied = []
        indexes = DatabaseIndexRecommendations.get_recommended_indexes()

        for index_sql in indexes:
            try:
                await session.execute(index_sql)
                applied.append(index_sql)
                logger.info(f"Applied index: {index_sql[:50]}...")
            except Exception as e:
                logger.warning(f"Failed to apply index: {e}")

        await session.commit()
        return applied
