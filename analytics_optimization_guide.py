"""Analytics database optimization suggestions and index recommendations."""

from typing import Dict, List

def get_analytics_index_recommendations() -> Dict[str, List[str]]:
    """Get recommended database indexes for analytics performance.
    
    Returns:
        Dictionary mapping table names to list of recommended indexes
    """
    return {
        "conversations": [
            "CREATE INDEX IF NOT EXISTS idx_conversations_user_created_at ON conversations(user_id, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);",
            "CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);",
        ],
        "messages": [
            "CREATE INDEX IF NOT EXISTS idx_messages_conversation_role ON messages(conversation_id, role);",
            "CREATE INDEX IF NOT EXISTS idx_messages_role_created_at ON messages(role, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_messages_provider_model ON messages(provider_used, model_used);",
            "CREATE INDEX IF NOT EXISTS idx_messages_response_time ON messages(response_time_ms) WHERE response_time_ms IS NOT NULL;",
        ],
        "documents": [
            "CREATE INDEX IF NOT EXISTS idx_documents_owner_created_at ON documents(owner_id, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);",
            "CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);",
            "CREATE INDEX IF NOT EXISTS idx_documents_processing_times ON documents(processing_started_at, processing_completed_at);",
        ],
        "toolservers": [
            "CREATE INDEX IF NOT EXISTS idx_toolservers_status ON toolservers(status);",
        ],
        "servertools": [
            "CREATE INDEX IF NOT EXISTS idx_servertools_server_status ON servertools(toolserver_id, status);",
        ],
        "tool_usage": [
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_user_called_at ON tool_usage(user_id, called_at);",
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_tool_called_at ON tool_usage(servertool_id, called_at);",
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_success ON tool_usage(success);",
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_response_time ON tool_usage(response_time_ms) WHERE response_time_ms IS NOT NULL;",
        ],
        "analytics_models": [
            "CREATE INDEX IF NOT EXISTS idx_conversation_stats_user_date ON conversation_stats(user_id, date);",
            "CREATE INDEX IF NOT EXISTS idx_document_stats_user_date ON document_stats(user_id, date);",
            "CREATE INDEX IF NOT EXISTS idx_prompt_stats_user_date ON prompt_stats(user_id, date);",
            "CREATE INDEX IF NOT EXISTS idx_profile_stats_user_date ON profile_stats(user_id, date);",
        ]
    }

def get_analytics_query_optimizations() -> Dict[str, str]:
    """Get analytics query optimization suggestions.
    
    Returns:
        Dictionary mapping optimization categories to descriptions
    """
    return {
        "aggregation_queries": """
        For analytics aggregation queries:
        1. Use partial indexes for filtered aggregations (e.g., WHERE role = 'assistant')
        2. Consider materialized views for complex recurring aggregations
        3. Use query hints for large aggregations: 
           - SET work_mem = '256MB' for heavy sorts/aggregations
           - Use LIMIT with proper ORDER BY for pagination
        """,
        
        "time_range_queries": """
        For time-based analytics:
        1. Always use proper date/time indexes
        2. Consider partitioning large tables by date
        3. Use date_trunc() for grouping by time periods
        4. Avoid timezone conversions in WHERE clauses
        """,
        
        "user_analytics": """
        For user-specific analytics:
        1. Use composite indexes (user_id, created_at)
        2. Consider row-level security for user isolation
        3. Use proper LIMIT clauses to prevent large result sets
        4. Cache frequently requested user analytics
        """,
        
        "performance_monitoring": """
        For performance analytics:
        1. Use separate analytics database/schema for heavy queries
        2. Implement read replicas for analytics workloads
        3. Use connection pooling with appropriate pool sizes
        4. Monitor slow query logs and optimize accordingly
        """,
        
        "real_time_analytics": """
        For real-time analytics:
        1. Use streaming aggregations where possible
        2. Implement incremental refresh strategies
        3. Consider time-series databases for metrics
        4. Use proper caching layers (Redis) for hot data
        """
    }

def get_analytics_performance_tips() -> List[str]:
    """Get general performance tips for analytics workloads.
    
    Returns:
        List of performance optimization tips
    """
    return [
        "Use EXPLAIN ANALYZE to understand query execution plans",
        "Implement proper connection pooling (recommended: 10-20 connections)",
        "Set appropriate PostgreSQL configuration for analytics workloads",
        "Use bulk operations for inserting analytics data",
        "Implement proper retry logic for transient database failures",
        "Monitor database metrics: query time, connection count, cache hit ratio",
        "Use read replicas for heavy analytics queries to reduce load on primary",
        "Implement query timeouts to prevent runaway queries",
        "Consider using PostgreSQL extensions: pg_stat_statements, pg_hint_plan",
        "Use proper data types (avoid TEXT for numeric data)",
        "Implement archiving strategy for old analytics data",
        "Use database-level pagination instead of application-level",
    ]

def generate_analytics_schema_migration() -> str:
    """Generate a migration script for analytics schema optimizations.
    
    Returns:
        SQL migration script
    """
    indexes = get_analytics_index_recommendations()
    
    migration_sql = """
-- Analytics Schema Optimization Migration
-- Generated automatically - review before applying

BEGIN;

-- Add analytics-specific indexes for better query performance
"""
    
    for table, index_queries in indexes.items():
        migration_sql += f"\n-- Indexes for {table} table\n"
        for index_query in index_queries:
            migration_sql += f"{index_query}\n"
    
    migration_sql += """
-- Add analytics configuration
-- Increase work_mem for analytics queries
SET work_mem = '256MB';

-- Enable query plan caching
SET shared_preload_libraries = 'pg_stat_statements';

-- Analytics-specific table settings
ALTER TABLE conversations SET (fillfactor = 90);
ALTER TABLE messages SET (fillfactor = 85);
ALTER TABLE documents SET (fillfactor = 90);

COMMIT;

-- Post-migration recommendations:
-- 1. ANALYZE all tables after creating indexes
-- 2. Monitor query performance with pg_stat_statements
-- 3. Adjust PostgreSQL configuration for analytics workloads
-- 4. Consider partitioning for very large tables
"""
    
    return migration_sql