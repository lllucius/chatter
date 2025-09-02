"""Database query optimization utilities for eager loading and performance enhancement."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import Select

from chatter.models.conversation import Conversation, Message
from chatter.models.document import Document
from chatter.models.user import User
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class QueryOptimizer:
    """Utility class for optimizing database queries with eager loading."""

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

    def analyze_query(self, query: str) -> dict:
        """Analyze SQL query and extract information.
        
        Args:
            query: SQL query string to analyze
            
        Returns:
            Dictionary with query analysis results
        """
        import re
        
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
            "has_aggregates": any(agg in query_lower for agg in ["count", "sum", "avg", "max", "min"]),
            "has_order_by": "order by" in query_lower,
            "has_group_by": "group by" in query_lower,
            "has_limit": "limit" in query_lower
        }
        
        return analysis

    def analyze_execution_plan(self, explain_result: list) -> dict:
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
            "performance_score": performance_score
        }
        
        return analysis

    def recommend_indexes(self, queries: list) -> list:
        """Recommend indexes based on query patterns.
        
        Args:
            queries: List of SQL query strings to analyze
            
        Returns:
            List of index recommendations
        """
        import re
        
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
            where_match = re.search(r'\bwhere\s+(.+?)(?:\s+(?:order\s+by|group\s+by|limit)|$)', query_lower)
            if where_match:
                where_clause = where_match.group(1)
                
                # Find column references in WHERE clause
                column_matches = re.findall(r'\b(\w+)\s*=', where_clause)
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
                if column_usage.get(key, 0) >= 2:  # Used in multiple queries
                    recommendations.append({
                        "table": table,
                        "columns": [column],
                        "type": "btree",
                        "reason": f"Column '{column}' is frequently used in WHERE clauses",
                        "usage_count": column_usage[key]
                    })
        
        return recommendations

    def calculate_performance_score(self, stats: dict) -> float:
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

    def get_optimization_suggestions(self, query: str) -> list:
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
            suggestions.append("Avoid SELECT * - specify only needed columns")
            
        if "like '%" in query_lower:
            suggestions.append("Leading wildcard in LIKE can't use indexes effectively")
            
        if "or" in query_lower:
            suggestions.append("Consider splitting OR conditions into separate queries with UNION")
            
        if "order by" in query_lower and "limit" not in query_lower:
            suggestions.append("Consider adding LIMIT when using ORDER BY to reduce sorting overhead")
            
        if "where" not in query_lower and "from" in query_lower:
            suggestions.append("Query lacks WHERE clause - consider if you need all rows")
            
        if len(query_lower.split("join")) > 3:
            suggestions.append("Complex joins detected - consider breaking into smaller queries")
            
        # Suggest indexes for WHERE conditions
        import re
        where_match = re.search(r'\bwhere\s+(.+?)(?:\s+(?:order\s+by|group\s+by|limit)|$)', query_lower)
        if where_match:
            where_clause = where_match.group(1)
            column_matches = re.findall(r'\b(\w+)\s*=', where_clause)
            if column_matches:
                suggestions.append(f"Consider adding indexes on columns: {', '.join(set(column_matches))}")
                
        return suggestions

    def suggest_caching(self, query: str, execution_count: int, avg_execution_time_ms: float) -> dict:
        """Suggest query caching based on usage patterns.
        
        Args:
            query: SQL query string
            execution_count: Number of times query has been executed
            avg_execution_time_ms: Average execution time in milliseconds
            
        Returns:
            Dictionary with caching recommendation
        """
        # Calculate caching score based on frequency and execution time
        frequency_score = min(execution_count / 50, 1.0)  # Normalize to 0-1
        time_score = min(avg_execution_time_ms / 100, 1.0)  # Normalize to 0-1
        
        # Queries with low variability are good candidates for caching
        query_lower = query.lower()
        has_parameters = "%" in query or "?" in query or "$" in query
        
        # Calculate final caching score
        cache_score = (frequency_score * 0.4 + time_score * 0.4 + (0.2 if has_parameters else 0.0))
        
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
            reason = f"High frequency ({execution_count} executions) and "
            reason += f"execution time ({avg_execution_time_ms:.1f}ms) suggest caching would be beneficial"
        else:
            reason = "Low frequency or fast execution time - caching may not provide significant benefit"
        
        return {
            "should_cache": should_cache,
            "cache_duration_seconds": cache_duration if should_cache else 0,
            "cache_score": cache_score,
            "reason": reason
        }


class ConversationQueryService:
    """Specialized service for optimized conversation queries."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

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

        # Manually assign messages to avoid additional query
        conversation.messages = messages

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
            # Load conversations with a single recent message each
            query = QueryOptimizer.optimize_conversation_query(
                query,
                include_messages=False,  # We'll handle this specially
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
                    Message.conversation_id, Message.created_at.desc()
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

            # Assign recent messages to conversations
            for conv in conversations:
                if conv.id in recent_messages:
                    conv.messages = [recent_messages[conv.id]]
                else:
                    conv.messages = []

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
                        Conversation.title.ilike(f"%{search_term}%"),
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


# Utility functions for common optimized queries
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
    service = ConversationQueryService(session)

    if include_messages and message_limit:
        return await service.get_conversation_with_recent_messages(
            conversation_id, message_limit, user_id
        )
    else:
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
    service = ConversationQueryService(session)
    return await service.get_conversations_for_user(
        user_id, limit, offset, include_recent_message=True
    )
