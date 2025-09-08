"""Database performance optimization and monitoring utilities.

Consolidated module for all database query optimization, performance monitoring,
and index management functionality.
"""

import re
import time
from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import Select

# Import all models that we optimize queries for
from chatter.models.conversation import Conversation, Message
from chatter.models.document import Document
from chatter.models.registry import ModelDef, ModelType, Provider
from chatter.models.user import User
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class QueryOptimizer:
    """Unified database query optimization and analysis utility.

    Combines both static query optimization methods and session-based
    optimizations for comprehensive database performance improvement.
    """

    def __init__(self, session: AsyncSession | None = None):
        """Initialize query optimizer.

        Args:
            session: Database session (optional for static methods)
        """
        self.session = session

    # ========================================================================
    # Static Query Optimization Methods (from database_optimization.py)
    # ========================================================================

    @staticmethod
    def optimize_conversation_query(
        query: Select[tuple[Conversation]],
        include_messages: bool = True,
        include_user: bool = True,
        include_profile: bool = True,
        message_limit: int | None = None,
    ) -> Select[tuple[Conversation]]:
        """Optimize conversation query with eager loading.

        Args:
            query: Base query to optimize
            include_messages: Whether to include messages
            include_user: Whether to include user data
            include_profile: Whether to include profile data
            message_limit: Limit number of messages to load

        Returns:
            Optimized query with eager loading
        """
        # Use joinedload for small related objects (user, profile)
        if include_user:
            query = query.options(joinedload(Conversation.user))

        if include_profile:
            query = query.options(joinedload(Conversation.profile))

        # Use selectinload for potentially large collections (messages)
        if include_messages:
            if message_limit:
                # For limited messages, we need a subquery approach
                message_options = selectinload(
                    Conversation.messages
                ).options(
                    # Order by created_at desc to get most recent messages
                    # Note: This requires a separate optimization in the service layer
                )
            else:
                message_options = selectinload(Conversation.messages)

            query = query.options(message_options)

        return query

    @staticmethod
    def optimize_message_query(
        query: Select[tuple[Message]],
        include_conversation: bool = True,
        include_user: bool = False,
    ) -> Select[tuple[Message]]:
        """Optimize message query with eager loading.

        Args:
            query: Base query to optimize
            include_conversation: Whether to include conversation data
            include_user: Whether to include user data through conversation

        Returns:
            Optimized query with eager loading
        """
        if include_conversation:
            query = query.options(joinedload(Message.conversation))

            if include_user:
                query = query.options(
                    joinedload(Message.conversation).joinedload(
                        Conversation.user
                    )
                )

        return query

    @staticmethod
    def optimize_user_query(
        query: Select[tuple[User]],
        include_conversations: bool = False,
        include_profiles: bool = True,
    ) -> Select[tuple[User]]:
        """Optimize user query with eager loading.

        Args:
            query: Base query to optimize
            include_conversations: Whether to include conversations (use sparingly)
            include_profiles: Whether to include profiles

        Returns:
            Optimized query with eager loading
        """
        if include_profiles:
            query = query.options(selectinload(User.profiles))

        if include_conversations:
            # Only include conversations if explicitly requested (can be large)
            query = query.options(selectinload(User.conversations))

        return query

    @staticmethod
    def optimize_document_query(
        query: Select[tuple[Document]],
        include_user: bool = True,
        include_chunks: bool = False,
    ) -> Select[tuple[Document]]:
        """Optimize document query with eager loading.

        Args:
            query: Base query to optimize
            include_user: Whether to include user data
            include_chunks: Whether to include document chunks

        Returns:
            Optimized query with eager loading
        """
        if include_user:
            query = query.options(joinedload(Document.owner))

        if include_chunks:
            # Use selectinload for potentially large chunk collections
            query = query.options(selectinload(Document.chunks))

        return query

    # ========================================================================
    # Query Analysis Methods (from database_optimization.py)
    # ========================================================================

    def analyze_query(self, query: str) -> dict[str, Any]:
        """Analyze SQL query and extract information.

        Args:
            query: SQL query string to analyze

        Returns:
            Dictionary with query analysis results
        """
        query_lower = query.lower()

        # Extract tables from FROM clause
        tables = []
        from_match = re.search(r'\bfrom\s+(\w+)', query_lower)
        if from_match:
            tables.append(from_match.group(1))

        # Check for JOIN clauses to find additional tables
        join_matches = re.findall(r'\bjoin\s+(\w+)', query_lower)
        tables.extend(join_matches)

        # Analyze query characteristics
        analysis = {
            "has_where_clause": "where" in query_lower,
            "table_count": len(tables),
            "tables": tables,
            "has_wildcards": "*" in query,
            "has_joins": "join" in query_lower,
            "has_subqueries": "(" in query and "select" in query_lower,
            "has_aggregates": any(
                agg in query_lower
                for agg in ["count", "sum", "avg", "max", "min"]
            ),
            "has_order_by": "order by" in query_lower,
            "has_group_by": "group by" in query_lower,
            "has_limit": "limit" in query_lower,
        }

        return analysis

    def analyze_execution_plan(
        self, explain_result: list
    ) -> dict[str, Any]:
        """Analyze query execution plan.

        Args:
            explain_result: List containing execution plan from EXPLAIN

        Returns:
            Dictionary with execution plan analysis
        """
        if not explain_result or not isinstance(explain_result, list):
            return {"error": "Invalid execution plan data"}

        plan = explain_result[0].get("Plan", {})

        total_cost = plan.get("Total Cost", 0)
        estimated_rows = plan.get("Rows", 0)
        node_type = plan.get("Node Type", "Unknown")

        # Check for performance indicators
        has_sequential_scan = "Seq Scan" in node_type
        has_index_scan = "Index" in node_type

        # Calculate performance score (0-1, higher is better)
        performance_score = 1.0
        if has_sequential_scan:
            performance_score *= 0.5  # Sequential scans are slower
        if total_cost > 1000:
            performance_score *= 0.7  # High cost queries
        if estimated_rows > 10000:
            performance_score *= 0.8  # Large result sets

        analysis = {
            "total_cost": total_cost,
            "estimated_rows": estimated_rows,
            "node_type": node_type,
            "has_sequential_scan": has_sequential_scan,
            "has_index_scan": has_index_scan,
            "performance_score": performance_score,
        }

        return analysis

    def calculate_performance_score(
        self, stats: dict[str, Any]
    ) -> float:
        """Calculate query performance score.

        Args:
            stats: Dictionary with query execution statistics

        Returns:
            Performance score between 0 and 1 (higher is better)
        """
        execution_time = stats.get("execution_time_ms", 100)
        rows_examined = stats.get("rows_examined", 1000)
        rows_returned = stats.get("rows_returned", 1)
        has_index_usage = stats.get("has_index_usage", False)

        # Base score
        score = 1.0

        # Penalize slow execution times
        if execution_time > 100:
            score *= 0.7
        elif execution_time > 50:
            score *= 0.85
        elif execution_time < 10:
            score *= 1.1  # Bonus for fast queries

        # Penalize inefficient row examination
        if rows_examined > 0 and rows_returned > 0:
            efficiency = rows_returned / rows_examined
            score *= efficiency

        # Bonus for index usage
        if has_index_usage:
            score *= 1.2
        else:
            score *= 0.8

        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))

    def get_optimization_suggestions(self, query: str) -> list[str]:
        """Get optimization suggestions for a query.

        Args:
            query: SQL query string to analyze

        Returns:
            List of optimization suggestions
        """
        suggestions = []
        query_lower = query.lower()

        # Check for common anti-patterns
        if "select *" in query_lower:
            suggestions.append(
                "Avoid SELECT * - specify only needed columns"
            )

        if "like '%" in query_lower:
            suggestions.append(
                "Leading wildcard in LIKE can't use indexes effectively"
            )

        if "or" in query_lower:
            suggestions.append(
                "Consider splitting OR conditions into separate queries with UNION"
            )

        if "order by" in query_lower and "limit" not in query_lower:
            suggestions.append(
                "Consider adding LIMIT when using ORDER BY to reduce sorting overhead"
            )

        if "where" not in query_lower and "from" in query_lower:
            suggestions.append(
                "Query lacks WHERE clause - consider if you need all rows"
            )

        if len(query_lower.split("join")) > 3:
            suggestions.append(
                "Complex joins detected - consider breaking into smaller queries"
            )

        # Suggest indexes for WHERE conditions
        where_match = re.search(
            r'\bwhere\s+(.+?)(?:\s+(?:order\s+by|group\s+by|limit)|$)',
            query_lower,
        )
        if where_match:
            where_clause = where_match.group(1)
            column_matches = re.findall(r'\b(\w+)\s*=', where_clause)
            if column_matches:
                suggestions.append(
                    f"Consider adding indexes on columns: {', '.join(set(column_matches))}"
                )

        return suggestions

    def suggest_caching(
        self,
        query: str,
        execution_count: int,
        avg_execution_time_ms: float,
    ) -> dict[str, Any]:
        """Suggest query caching based on usage patterns.

        Args:
            query: SQL query string
            execution_count: Number of times query has been executed
            avg_execution_time_ms: Average execution time in milliseconds

        Returns:
            Dictionary with caching recommendation
        """
        # Calculate caching score based on frequency and execution time
        frequency_score = min(
            execution_count / 50, 1.0
        )  # Normalize to 0-1
        time_score = min(
            avg_execution_time_ms / 100, 1.0
        )  # Normalize to 0-1

        # Queries with low variability are good candidates for caching
        query_lower = query.lower()
        has_parameters = "%" in query or "?" in query or "$" in query

        # Calculate final caching score
        cache_score = (
            frequency_score * 0.4
            + time_score * 0.4
            + (0.2 if has_parameters else 0.0)
        )

        should_cache = cache_score > 0.6

        # Determine cache duration based on query characteristics
        if "count" in query_lower or "sum" in query_lower:
            # Aggregate queries can be cached longer
            cache_duration = 300  # 5 minutes
        elif "select" in query_lower and "where" in query_lower:
            # Filtered queries
            cache_duration = 180  # 3 minutes
        else:
            # Default caching
            cache_duration = 60  # 1 minute

        # Generate reason
        if should_cache:
            reason = (
                f"High frequency ({execution_count} executions) and "
            )
            reason += f"execution time ({avg_execution_time_ms:.1f}ms) suggest caching would be beneficial"
        else:
            reason = "Low frequency or fast execution time - caching may not provide significant benefit"

        return {
            "should_cache": should_cache,
            "cache_duration_seconds": (
                cache_duration if should_cache else 0
            ),
            "cache_score": cache_score,
            "reason": reason,
        }

    # ========================================================================
    # Session-based Model Registry Optimizations (existing methods)
    # ========================================================================

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
        if not self.session:
            raise ValueError("Session required for model operations")

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

        data_query = data_query.offset((page - 1) * per_page).limit(
            per_page
        )

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
        if not self.session:
            raise ValueError("Session required for provider operations")

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

        data_query = data_query.offset((page - 1) * per_page).limit(
            per_page
        )

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
        if not self.session:
            raise ValueError("Session required for provider operations")

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
                ),
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
        if not self.session:
            raise ValueError("Session required for provider operations")

        if not provider_ids:
            return {}

        # Single query to get all counts
        query = (
            select(
                ModelDef.provider_id,
                ModelDef.model_type,
                func.count(ModelDef.id).label('count'),
            )
            .where(
                ModelDef.provider_id.in_(provider_ids),
                ModelDef.is_active,
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

    # ========================================================================
    # Index Recommendation Methods (consolidated from both modules)
    # ========================================================================

    def recommend_indexes(
        self, queries: list[str]
    ) -> list[dict[str, Any]]:
        """Recommend indexes based on query patterns.

        Args:
            queries: List of SQL query strings to analyze

        Returns:
            List of index recommendations
        """
        column_usage = {}
        table_columns = {}

        for query in queries:
            query_lower = query.lower()

            # Extract table from FROM clause
            from_match = re.search(r'\bfrom\s+(\w+)', query_lower)
            if not from_match:
                continue
            table = from_match.group(1)

            # Extract WHERE clause columns
            where_match = re.search(
                r'\bwhere\s+(.+?)(?:\s+(?:order\s+by|group\s+by|limit)|$)',
                query_lower,
            )
            if where_match:
                where_clause = where_match.group(1)

                # Find column references in WHERE clause
                column_matches = re.findall(
                    r'\b(\w+)\s*=', where_clause
                )
                for column in column_matches:
                    if table not in table_columns:
                        table_columns[table] = set()
                    table_columns[table].add(column)

                    key = f"{table}.{column}"
                    column_usage[key] = column_usage.get(key, 0) + 1

        # Generate recommendations for frequently used columns
        recommendations = []
        for table, columns in table_columns.items():
            for column in columns:
                key = f"{table}.{column}"
                if (
                    column_usage.get(key, 0) >= 2
                ):  # Used in multiple queries
                    recommendations.append(
                        {
                            "table": table,
                            "columns": [column],
                            "type": "btree",
                            "reason": f"Column '{column}' is frequently used in WHERE clauses",
                            "usage_count": column_usage[key],
                        }
                    )

        return recommendations


class PerformanceMonitor:
    """Enhanced performance tracking and monitoring for database operations.

    Tracks query execution times, identifies slow queries, and provides
    comprehensive performance analytics across all database operations.
    """

    def __init__(self):
        """Initialize performance monitor."""
        self.query_times = {}
        self.query_counts = {}
        self.slow_query_threshold_ms = 1000  # 1 second

    @asynccontextmanager
    async def measure_query(
        self, operation: str
    ) -> AsyncGenerator[None, None]:
        """Context manager to measure query execution time.

        Args:
            operation: Name of the operation being measured
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = (
                time.time() - start_time
            ) * 1000  # Convert to milliseconds

            # Track metrics
            if operation not in self.query_times:
                self.query_times[operation] = []
                self.query_counts[operation] = 0

            self.query_times[operation].append(duration)
            self.query_counts[operation] += 1

            # Keep only last 100 measurements
            if len(self.query_times[operation]) > 100:
                self.query_times[operation] = self.query_times[
                    operation
                ][-100:]

            # Log slow queries with more context
            if duration > self.slow_query_threshold_ms:
                logger.warning(
                    "Slow query detected",
                    operation=operation,
                    duration_ms=duration,
                    avg_duration_ms=sum(self.query_times[operation])
                    / len(self.query_times[operation]),
                    count=self.query_counts[operation],
                )

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance metrics summary.

        Returns:
            Performance metrics dictionary with enhanced analytics
        """
        summary = {}

        for operation, times in self.query_times.items():
            if not times:
                continue

            # Basic statistics
            avg_ms = sum(times) / len(times)
            min_ms = min(times)
            max_ms = max(times)

            # Percentile calculations
            sorted_times = sorted(times)
            count = len(sorted_times)
            p50_ms = sorted_times[count // 2] if count > 0 else 0
            p95_ms = (
                sorted_times[int(count * 0.95)]
                if count > 20
                else max_ms
            )
            p99_ms = (
                sorted_times[int(count * 0.99)]
                if count > 100
                else max_ms
            )

            # Performance assessment
            slow_queries = sum(
                1 for t in times if t > self.slow_query_threshold_ms
            )
            performance_grade = self._calculate_performance_grade(
                avg_ms, p95_ms, slow_queries, count
            )

            summary[operation] = {
                'count': self.query_counts[operation],
                'avg_ms': round(avg_ms, 2),
                'min_ms': round(min_ms, 2),
                'max_ms': round(max_ms, 2),
                'p50_ms': round(p50_ms, 2),
                'p95_ms': round(p95_ms, 2),
                'p99_ms': round(p99_ms, 2),
                'slow_queries': slow_queries,
                'performance_grade': performance_grade,
                'throughput_per_sec': (
                    round(count / (sum(times) / 1000), 2)
                    if times
                    else 0
                ),
            }

        return summary

    def _calculate_performance_grade(
        self,
        avg_ms: float,
        p95_ms: float,
        slow_queries: int,
        total_queries: int,
    ) -> str:
        """Calculate performance grade based on query metrics."""
        slow_query_ratio = (
            slow_queries / total_queries if total_queries > 0 else 0
        )

        if avg_ms < 50 and p95_ms < 200 and slow_query_ratio < 0.01:
            return "A"
        elif avg_ms < 100 and p95_ms < 500 and slow_query_ratio < 0.05:
            return "B"
        elif avg_ms < 250 and p95_ms < 1000 and slow_query_ratio < 0.1:
            return "C"
        elif avg_ms < 500 and p95_ms < 2000 and slow_query_ratio < 0.2:
            return "D"
        else:
            return "F"

    def get_slow_query_analysis(self) -> dict[str, Any]:
        """Analyze slow queries and provide optimization recommendations."""
        slow_operations = []

        for operation, times in self.query_times.items():
            slow_count = sum(
                1 for t in times if t > self.slow_query_threshold_ms
            )
            if slow_count > 0:
                avg_slow_time = (
                    sum(
                        t
                        for t in times
                        if t > self.slow_query_threshold_ms
                    )
                    / slow_count
                )
                slow_operations.append(
                    {
                        'operation': operation,
                        'slow_query_count': slow_count,
                        'avg_slow_time_ms': round(avg_slow_time, 2),
                        'slow_query_ratio': round(
                            slow_count / len(times), 3
                        ),
                        'recommendations': self._get_optimization_recommendations(
                            operation, avg_slow_time
                        ),
                    }
                )

        return {
            'slow_operations': sorted(
                slow_operations,
                key=lambda x: x['avg_slow_time_ms'],
                reverse=True,
            ),
            'total_slow_queries': sum(
                op['slow_query_count'] for op in slow_operations
            ),
        }

    def _get_optimization_recommendations(
        self, operation: str, avg_time_ms: float
    ) -> list[str]:
        """Get optimization recommendations for slow operations."""
        recommendations = []

        if "list_" in operation:
            recommendations.append(
                "Consider adding database indexes on filter columns"
            )
            recommendations.append(
                "Implement query result caching for frequently accessed lists"
            )
            if avg_time_ms > 2000:
                recommendations.append(
                    "Consider implementing pagination with smaller page sizes"
                )

        if "get_" in operation and avg_time_ms > 500:
            recommendations.append(
                "Review eager loading strategy to avoid N+1 queries"
            )
            recommendations.append(
                "Consider caching frequently accessed entities"
            )

        if avg_time_ms > 5000:
            recommendations.append(
                "This query is extremely slow - urgent optimization needed"
            )
            recommendations.append(
                "Consider query rewrite or data denormalization"
            )

        return recommendations

    def get_database_response_time(self) -> float:
        """Get average database response time across all operations.
        
        Returns:
            Average response time in milliseconds
        """
        summary = self.get_performance_summary()
        
        # Calculate weighted average of database operations
        db_operations = [
            "get_conversation_stats", "get_usage_metrics",
            "get_performance_metrics", "get_document_analytics",
            "list_providers", "get_default_provider", "get_default_model",
            "get_conversation_optimized", "get_user_conversations_optimized"
        ]
        
        total_time = 0.0
        total_count = 0
        
        for operation in db_operations:
            if operation in summary:
                op_data = summary[operation]
                total_time += op_data.get('avg_ms', 0) * op_data.get('count', 0)
                total_count += op_data.get('count', 0)
        
        return total_time / total_count if total_count > 0 else 0.0

    def get_vector_search_time(self) -> float:
        """Get average vector search time across all operations.
        
        Returns:
            Average vector search time in milliseconds
        """
        summary = self.get_performance_summary()
        
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

    def get_performance_health_metrics(self) -> dict[str, Any]:
        """Get comprehensive health metrics for monitoring dashboards.
        
        Returns:
            Dictionary with health metrics including database and vector performance
        """
        return {
            "database_response_time_ms": self.get_database_response_time(),
            "vector_search_time_ms": self.get_vector_search_time(),
            "slow_query_analysis": self.get_slow_query_analysis(),
            "performance_grade": self._calculate_performance_grade(),
            "total_queries": sum(self.query_counts.values()),
            "active_operations": len([op for op, times in self.query_times.items() if times])
        }


class BulkOperations:
    """Efficient bulk database operations with performance monitoring."""

    def __init__(
        self,
        session: AsyncSession,
        performance_monitor: PerformanceMonitor | None = None,
    ):
        """Initialize bulk operations.

        Args:
            session: Database session
            performance_monitor: Optional performance monitor for tracking
        """
        self.session = session
        self.performance_monitor = (
            performance_monitor or _performance_monitor
        )

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

        async with self.performance_monitor.measure_query(
            "bulk_update_model_status"
        ):
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

        async with self.performance_monitor.measure_query(
            "bulk_update_provider_status"
        ):
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

        async with self.performance_monitor.measure_query(
            "bulk_create_models"
        ):
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


class DatabaseIndexManager:
    """Comprehensive database index management and recommendations.

    Consolidates index recommendations from both query analysis and
    predefined performance optimizations.
    """

    @staticmethod
    def get_comprehensive_index_recommendations() -> list[str]:
        """Get comprehensive database index recommendations for optimal performance.

        Returns:
            List of SQL CREATE INDEX statements with explanations
        """
        return [
            # Model registry optimization indexes
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_models_provider_type_active
               ON model_defs(provider_id, model_type, is_active)
               -- Optimizes model listing filtered by provider and type""",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_models_default_type
               ON model_defs(model_type, is_default) WHERE is_active = true
               -- Optimizes finding default models by type""",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_models_list_query
               ON model_defs(provider_id, model_type, is_active, is_default, display_name)
               -- Covers common model listing queries""",
            # Provider queries optimization
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_providers_type_active
               ON providers(provider_type, is_active)
               -- Optimizes provider filtering""",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_providers_list_query
               ON providers(provider_type, is_active, is_default, display_name)
               -- Covers common provider listing queries""",
            # Conversation optimization indexes
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_user_status_updated
               ON conversations(user_id, status, updated_at DESC)
               -- Optimizes user conversation listing""",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_search
               ON conversations USING GIN(to_tsvector('english', title))
               -- Enables full-text search on conversation titles""",
            # Message optimization indexes
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_conversation_created
               ON messages(conversation_id, created_at DESC)
               -- Optimizes message ordering within conversations""",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_search
               ON messages USING GIN(to_tsvector('english', content))
               -- Enables full-text search on message content""",
            # Document optimization indexes
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_owner_created
               ON documents(owner_id, created_at DESC)
               -- Optimizes user document listing""",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_chunks_document_vector
               ON document_chunks(document_id) INCLUDE (embedding_vector)
               -- Optimizes vector similarity searches""",
            # User and profile indexes
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_unique
               ON users(email) WHERE email IS NOT NULL
               -- Ensures fast user lookup by email""",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_profiles_user_active
               ON profiles(user_id, is_active)
               -- Optimizes active profile lookup""",
            # Audit and monitoring indexes
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp_type
               ON audit_logs(timestamp DESC, event_type)
               -- Optimizes audit log queries""",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_timestamp
               ON audit_logs(user_id, timestamp DESC)
               -- Optimizes user-specific audit queries""",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_resource
               ON audit_logs(resource_type, resource_id)
               -- Optimizes resource-specific audit queries""",
        ]

    @staticmethod
    async def apply_recommended_indexes(
        session: AsyncSession,
        performance_monitor: PerformanceMonitor | None = None,
    ) -> dict[str, Any]:
        """Apply recommended indexes to the database with comprehensive tracking.

        Args:
            session: Database session
            performance_monitor: Optional performance monitor

        Returns:
            Dictionary with application results and timing
        """
        monitor = performance_monitor or _performance_monitor
        applied = []
        failed = []
        indexes = (
            DatabaseIndexManager.get_comprehensive_index_recommendations()
        )

        async with monitor.measure_query("apply_database_indexes"):
            for index_sql in indexes:
                try:
                    # Extract index name for logging
                    index_name_match = re.search(r'idx_\w+', index_sql)
                    index_name = (
                        index_name_match.group(0)
                        if index_name_match
                        else "unknown"
                    )

                    start_time = time.time()
                    await session.execute(index_sql)
                    duration = time.time() - start_time

                    applied.append(
                        {
                            "name": index_name,
                            "sql": (
                                index_sql[:100] + "..."
                                if len(index_sql) > 100
                                else index_sql
                            ),
                            "duration_ms": round(duration * 1000, 2),
                        }
                    )

                    logger.info(
                        f"Applied index: {index_name} in {duration:.2f}s"
                    )

                except Exception as e:
                    failed.append(
                        {
                            "name": (
                                index_name
                                if 'index_name' in locals()
                                else "unknown"
                            ),
                            "error": str(e),
                            "sql": index_sql[:100] + "...",
                        }
                    )
                    logger.warning(
                        f"Failed to apply index {index_name if 'index_name' in locals() else 'unknown'}: {e}"
                    )

            await session.commit()

        return {
            "applied_count": len(applied),
            "failed_count": len(failed),
            "applied_indexes": applied,
            "failed_indexes": failed,
            "total_indexes": len(indexes),
        }

    @staticmethod
    def analyze_query_for_indexes(query: str) -> list[dict[str, Any]]:
        """Analyze a specific query and recommend indexes.

        Args:
            query: SQL query string to analyze

        Returns:
            List of specific index recommendations for this query
        """
        recommendations = []
        query_lower = query.lower()

        # Extract table and conditions
        table_match = re.search(r'\bfrom\s+(\w+)', query_lower)
        if not table_match:
            return recommendations

        table = table_match.group(1)

        # Analyze WHERE conditions
        where_match = re.search(
            r'\bwhere\s+(.+?)(?:\s+(?:order\s+by|group\s+by|limit)|$)',
            query_lower,
        )
        if where_match:
            where_clause = where_match.group(1)

            # Find equality conditions
            eq_columns = re.findall(r'\b(\w+)\s*=', where_clause)

            # Find range conditions
            range_columns = re.findall(r'\b(\w+)\s*[<>]', where_clause)

            # Find IN conditions
            in_columns = re.findall(r'\b(\w+)\s+in\s*\(', where_clause)

            all_columns = list(
                set(eq_columns + range_columns + in_columns)
            )

            if all_columns:
                recommendations.append(
                    {
                        "table": table,
                        "columns": all_columns,
                        "type": "btree",
                        "reason": f"WHERE clause filtering on: {', '.join(all_columns)}",
                        "priority": (
                            "high"
                            if len(all_columns) <= 3
                            else "medium"
                        ),
                    }
                )

        # Analyze ORDER BY
        order_match = re.search(
            r'\border\s+by\s+([^)]+?)(?:\s+(?:limit|group\s+by)|$)',
            query_lower,
        )
        if order_match:
            order_clause = order_match.group(1)
            order_columns = re.findall(r'\b(\w+)', order_clause)

            if order_columns:
                recommendations.append(
                    {
                        "table": table,
                        "columns": order_columns,
                        "type": "btree",
                        "reason": f"ORDER BY optimization for: {', '.join(order_columns)}",
                        "priority": "medium",
                    }
                )

        return recommendations


# ============================================================================
# Specialized Query Services (from database_optimization.py)
# ============================================================================


class ConversationQueryService:
    """Specialized service for optimized conversation queries with performance monitoring."""

    def __init__(
        self,
        session: AsyncSession,
        performance_monitor: PerformanceMonitor | None = None,
    ):
        """Initialize with database session and optional performance monitor."""
        self.session = session
        self.performance_monitor = (
            performance_monitor or _performance_monitor
        )

    async def get_conversation_with_recent_messages(
        self,
        conversation_id: str,
        message_limit: int = 50,
        user_id: str | None = None,
    ) -> Conversation | None:
        """Get conversation with most recent messages using optimized query.

        Args:
            conversation_id: Conversation ID
            message_limit: Maximum number of recent messages to load
            user_id: Optional user ID for access control

        Returns:
            Conversation with recent messages or None
        """
        async with self.performance_monitor.measure_query(
            "get_conversation_with_recent_messages"
        ):
            # First, get the conversation with user and profile
            conv_query = select(Conversation).where(
                Conversation.id == conversation_id
            )

            if user_id:
                conv_query = conv_query.where(
                    Conversation.user_id == user_id
                )

            conv_query = QueryOptimizer.optimize_conversation_query(
                conv_query,
                include_messages=False,  # We'll load messages separately
                include_user=True,
                include_profile=True,
            )

            result = await self.session.execute(conv_query)
            conversation = result.scalar_one_or_none()

            if not conversation:
                return None

            # Then load recent messages separately for better performance
            messages_query = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(message_limit)
            )

            messages_result = await self.session.execute(messages_query)
            messages = list(messages_result.scalars().all())

            # Reverse to get chronological order
            messages.reverse()

            # Manually assign messages to avoid additional query and lazy loading
            from sqlalchemy.orm.attributes import set_committed_value
            set_committed_value(conversation, 'messages', messages)

            return conversation

    async def get_conversations_for_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        include_recent_message: bool = True,
    ) -> Sequence[Conversation]:
        """Get conversations for user with optimization.

        Args:
            user_id: User ID
            limit: Maximum conversations to return
            offset: Number of conversations to skip
            include_recent_message: Whether to include most recent message

        Returns:
            List of conversations
        """
        async with self.performance_monitor.measure_query(
            "get_conversations_for_user"
        ):
            query = (
                select(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.status != "deleted",
                    )
                )
                .order_by(Conversation.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )

            # Optimize based on what we need
            if include_recent_message:
                # Load conversations without messages, we'll populate manually
                query = QueryOptimizer.optimize_conversation_query(
                    query,
                    include_messages=False,
                    include_user=False,  # User is known
                    include_profile=True,
                )
            else:
                query = QueryOptimizer.optimize_conversation_query(
                    query,
                    include_messages=False,
                    include_user=False,
                    include_profile=True,
                )

            result = await self.session.execute(query)
            conversations = list(result.scalars().all())

            if include_recent_message and conversations:
                # Load most recent message for each conversation in a single query
                conv_ids = [conv.id for conv in conversations]

                # Get most recent message for each conversation
                recent_messages_query = (
                    select(Message)
                    .where(Message.conversation_id.in_(conv_ids))
                    .order_by(
                        Message.conversation_id,
                        Message.created_at.desc(),
                    )
                    .distinct(Message.conversation_id)
                )

                recent_messages_result = await self.session.execute(
                    recent_messages_query
                )
                recent_messages = {
                    msg.conversation_id: msg
                    for msg in recent_messages_result.scalars().all()
                }

                # Assign recent messages to conversations without triggering lazy loading
                from sqlalchemy.orm.attributes import set_committed_value
                for conv in conversations:
                    if conv.id in recent_messages:
                        # Set messages without triggering lazy loading
                        set_committed_value(conv, 'messages', [recent_messages[conv.id]])
                    else:
                        # Set empty messages without triggering lazy loading
                        set_committed_value(conv, 'messages', [])

            return conversations

    async def search_conversations(
        self, user_id: str, search_term: str, limit: int = 20
    ) -> Sequence[Conversation]:
        """Search conversations by title or content with optimization.

        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum results to return

        Returns:
            List of matching conversations
        """
        async with self.performance_monitor.measure_query(
            "search_conversations"
        ):
            # Search in conversation title or message content
            query = (
                select(Conversation)
                .join(
                    Message,
                    Message.conversation_id == Conversation.id,
                    isouter=True,
                )
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.status != "deleted",
                        or_(
                            Conversation.title.ilike(
                                f"%{search_term}%"
                            ),
                            Message.content.ilike(f"%{search_term}%"),
                        ),
                    )
                )
                .distinct()
                .order_by(Conversation.updated_at.desc())
                .limit(limit)
            )

            query = QueryOptimizer.optimize_conversation_query(
                query,
                include_messages=False,
                include_user=False,
                include_profile=True,
            )

            result = await self.session.execute(query)
            return result.scalars().all()


# ============================================================================
# Utility Functions (from database_optimization.py)
# ============================================================================


async def get_conversation_optimized(
    session: AsyncSession,
    conversation_id: str,
    user_id: str | None = None,
    include_messages: bool = True,
    message_limit: int | None = None,
) -> Conversation | None:
    """Get conversation with optimized loading.

    Args:
        session: Database session
        conversation_id: Conversation ID
        user_id: Optional user ID for access control
        include_messages: Whether to include messages
        message_limit: Optional limit on messages

    Returns:
        Conversation or None
    """
    service = ConversationQueryService(session, _performance_monitor)

    if include_messages and message_limit:
        return await service.get_conversation_with_recent_messages(
            conversation_id, message_limit, user_id
        )
    else:
        async with _performance_monitor.measure_query(
            "get_conversation_optimized"
        ):
            query = select(Conversation).where(
                Conversation.id == conversation_id
            )

            if user_id:
                query = query.where(Conversation.user_id == user_id)

            query = QueryOptimizer.optimize_conversation_query(
                query,
                include_messages=include_messages,
                include_user=True,
                include_profile=True,
            )

            result = await session.execute(query)
            return result.scalar_one_or_none()


async def get_user_conversations_optimized(
    session: AsyncSession,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
) -> Sequence[Conversation]:
    """Get user conversations with optimization.

    Args:
        session: Database session
        user_id: User ID
        limit: Maximum conversations to return
        offset: Number of conversations to skip

    Returns:
        List of conversations
    """
    service = ConversationQueryService(session, _performance_monitor)
    return await service.get_conversations_for_user(
        user_id, limit, offset, include_recent_message=True
    )


# ============================================================================
# Global Instances
# ============================================================================

# Global performance monitor instance - initialized on first access
_performance_monitor = PerformanceMonitor()


def get_performance_metrics() -> PerformanceMonitor:
    """Get the global performance monitor instance.

    Returns:
        PerformanceMonitor instance
    """
    return _performance_monitor


# Keep backward compatibility alias
def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance.

    Returns:
        PerformanceMonitor instance
    """
    return _performance_monitor
