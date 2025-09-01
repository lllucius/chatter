"""Tests for database utilities and connection management."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.exc import OperationalError, DatabaseError

from chatter.utils.database import (
    get_engine,
    get_session_maker,
    get_session,
    create_tables,
    drop_tables,
    health_check,
    DatabaseConnectionManager,
    QueryOptimizer
)


@pytest.mark.unit
class TestDatabaseUtilities:
    """Test database utility functions."""

    def test_get_engine_singleton(self):
        """Test that get_engine returns singleton instance."""
        # Act
        engine1 = get_engine()
        engine2 = get_engine()
        
        # Assert
        assert engine1 is engine2
        assert isinstance(engine1, AsyncEngine)

    @pytest.mark.asyncio
    async def test_get_session_context_manager(self):
        """Test database session context manager."""
        # Arrange
        with patch('chatter.utils.database.get_session_maker') as mock_get_maker:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session_maker = MagicMock()
            mock_session_maker.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_maker.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_get_maker.return_value = mock_session_maker
            
            # Act
            async with get_session() as session:
                # Assert
                assert session is mock_session
                
            # Verify session maker was called
            mock_session_maker.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_tables_success(self):
        """Test successful table creation."""
        # Arrange
        with patch('chatter.utils.database.get_engine') as mock_get_engine:
            mock_engine = AsyncMock(spec=AsyncEngine)
            mock_get_engine.return_value = mock_engine
            
            with patch('chatter.models.base.Base.metadata') as mock_metadata:
                mock_metadata.create_all = AsyncMock()
                
                # Act
                result = await create_tables()
                
                # Assert
                assert result is True
                mock_metadata.create_all.assert_called_once_with(mock_engine)

    @pytest.mark.asyncio
    async def test_create_tables_failure(self):
        """Test table creation failure."""
        # Arrange
        with patch('chatter.utils.database.get_engine') as mock_get_engine:
            mock_engine = AsyncMock(spec=AsyncEngine)
            mock_get_engine.return_value = mock_engine
            
            with patch('chatter.models.base.Base.metadata') as mock_metadata:
                mock_metadata.create_all = AsyncMock(side_effect=OperationalError("Connection failed", None, None))
                
                # Act
                result = await create_tables()
                
                # Assert
                assert result is False

    @pytest.mark.asyncio
    async def test_drop_tables_success(self):
        """Test successful table dropping."""
        # Arrange
        with patch('chatter.utils.database.get_engine') as mock_get_engine:
            mock_engine = AsyncMock(spec=AsyncEngine)
            mock_get_engine.return_value = mock_engine
            
            with patch('chatter.models.base.Base.metadata') as mock_metadata:
                mock_metadata.drop_all = AsyncMock()
                
                # Act
                result = await drop_tables()
                
                # Assert
                assert result is True
                mock_metadata.drop_all.assert_called_once_with(mock_engine)

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful database health check."""
        # Arrange
        with patch('chatter.utils.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(return_value=MagicMock(scalar=MagicMock(return_value=1)))
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Act
            health = await health_check()
            
            # Assert
            assert health["status"] == "healthy"
            assert health["connected"] is True
            assert "response_time_ms" in health
            assert health["response_time_ms"] >= 0

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test database health check failure."""
        # Arrange
        with patch('chatter.utils.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(side_effect=OperationalError("Connection failed", None, None))
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Act
            health = await health_check()
            
            # Assert
            assert health["status"] == "unhealthy"
            assert health["connected"] is False
            assert "error" in health

    def test_database_url_configuration(self):
        """Test database URL configuration from settings."""
        # Arrange
        with patch('chatter.utils.database.settings') as mock_settings:
            mock_settings.database_url_for_env = "postgresql+asyncpg://user:pass@localhost/testdb"
            mock_settings.debug_database_queries = True
            
            # Act
            with patch('chatter.utils.database.create_async_engine') as mock_create_engine:
                mock_engine = MagicMock()
                mock_create_engine.return_value = mock_engine
                
                engine = get_engine()
                
                # Assert
                mock_create_engine.assert_called_once()
                args, kwargs = mock_create_engine.call_args
                assert args[0] == "postgresql+asyncpg://user:pass@localhost/testdb"
                assert kwargs["echo"] is True


@pytest.mark.unit
class TestDatabaseConnectionManager:
    """Test database connection management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.connection_manager = DatabaseConnectionManager()

    @pytest.mark.asyncio
    async def test_connection_pool_management(self):
        """Test connection pool management."""
        # Arrange
        with patch.object(self.connection_manager, 'engine') as mock_engine:
            mock_pool = MagicMock()
            mock_pool.size.return_value = 5
            mock_pool.checked_in.return_value = 3
            mock_pool.checked_out.return_value = 2
            mock_engine.pool = mock_pool
            
            # Act
            pool_stats = await self.connection_manager.get_pool_stats()
            
            # Assert
            assert pool_stats["pool_size"] == 5
            assert pool_stats["checked_out"] == 2
            assert pool_stats["checked_in"] == 3
            assert pool_stats["available"] == 3

    @pytest.mark.asyncio
    async def test_connection_retry_mechanism(self):
        """Test connection retry mechanism."""
        # Arrange
        attempt_count = 0
        
        async def mock_connect():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise OperationalError("Connection failed", None, None)
            return MagicMock()
        
        with patch.object(self.connection_manager, '_attempt_connection', side_effect=mock_connect):
            # Act
            connection = await self.connection_manager.get_connection_with_retry(max_retries=3)
            
            # Assert
            assert connection is not None
            assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_connection_timeout_handling(self):
        """Test connection timeout handling."""
        # Arrange
        async def slow_connection():
            await asyncio.sleep(2)  # Simulate slow connection
            return MagicMock()
        
        with patch.object(self.connection_manager, '_attempt_connection', side_effect=slow_connection):
            # Act & Assert
            with pytest.raises(asyncio.TimeoutError):
                await self.connection_manager.get_connection_with_timeout(timeout_seconds=1)

    @pytest.mark.asyncio
    async def test_transaction_management(self):
        """Test transaction management utilities."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.begin = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        
        # Act - Successful transaction
        async with self.connection_manager.transaction(mock_session) as tx:
            # Simulate successful operation
            pass
        
        # Assert - Transaction committed
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self):
        """Test transaction rollback on error."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.begin = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        
        # Act & Assert - Transaction with error
        with pytest.raises(ValueError):
            async with self.connection_manager.transaction(mock_session):
                raise ValueError("Test error")
        
        # Assert - Transaction rolled back
        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_connection_leak_detection(self):
        """Test connection leak detection."""
        # Arrange
        mock_sessions = [AsyncMock() for _ in range(3)]
        for session in mock_sessions:
            session.is_active = True
            session.created_at = asyncio.get_event_loop().time() - 3600  # 1 hour ago
        
        self.connection_manager.active_sessions = mock_sessions
        
        # Act
        leaked_sessions = await self.connection_manager.detect_connection_leaks(max_age_seconds=1800)
        
        # Assert
        assert len(leaked_sessions) == 3  # All sessions are older than 30 minutes


@pytest.mark.unit
class TestQueryOptimizer:
    """Test query optimization utilities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = QueryOptimizer()

    def test_query_analysis(self):
        """Test SQL query analysis."""
        # Arrange
        query = "SELECT * FROM users WHERE email = %s AND active = true"
        
        # Act
        analysis = self.optimizer.analyze_query(query)
        
        # Assert
        assert analysis["has_where_clause"] is True
        assert analysis["table_count"] == 1
        assert "users" in analysis["tables"]
        assert analysis["has_wildcards"] is True

    def test_query_optimization_suggestions(self):
        """Test query optimization suggestions."""
        # Arrange
        slow_query = "SELECT * FROM large_table WHERE column1 LIKE '%search%'"
        
        # Act
        suggestions = self.optimizer.get_optimization_suggestions(slow_query)
        
        # Assert
        assert len(suggestions) > 0
        assert any("wildcard" in suggestion.lower() for suggestion in suggestions)
        assert any("index" in suggestion.lower() for suggestion in suggestions)

    def test_query_execution_plan_analysis(self):
        """Test query execution plan analysis."""
        # Arrange
        mock_explain_result = [
            {"Plan": {"Node Type": "Seq Scan", "Total Cost": 100.5, "Rows": 1000}}
        ]
        
        # Act
        analysis = self.optimizer.analyze_execution_plan(mock_explain_result)
        
        # Assert
        assert analysis["total_cost"] == 100.5
        assert analysis["estimated_rows"] == 1000
        assert analysis["has_sequential_scan"] is True
        assert analysis["performance_score"] < 0.8  # Sequential scan should score lower

    def test_index_recommendation(self):
        """Test index recommendation based on query patterns."""
        # Arrange
        queries = [
            "SELECT * FROM users WHERE email = %s",
            "SELECT * FROM users WHERE email = %s AND status = %s",
            "SELECT name FROM users WHERE email = %s"
        ]
        
        # Act
        recommendations = self.optimizer.recommend_indexes(queries)
        
        # Assert
        assert len(recommendations) > 0
        email_index = next((rec for rec in recommendations if "email" in rec["columns"]), None)
        assert email_index is not None
        assert email_index["table"] == "users"

    def test_query_caching_suggestions(self):
        """Test query caching suggestions."""
        # Arrange
        frequent_query = "SELECT COUNT(*) FROM posts WHERE published = true"
        execution_count = 100
        avg_execution_time = 50.0  # milliseconds
        
        # Act
        cache_suggestion = self.optimizer.suggest_caching(
            query=frequent_query,
            execution_count=execution_count,
            avg_execution_time_ms=avg_execution_time
        )
        
        # Assert
        assert cache_suggestion["should_cache"] is True
        assert cache_suggestion["cache_duration_seconds"] > 0
        assert cache_suggestion["reason"] is not None

    def test_query_performance_scoring(self):
        """Test query performance scoring."""
        # Arrange
        fast_query_stats = {
            "execution_time_ms": 5.0,
            "rows_examined": 1,
            "rows_returned": 1,
            "has_index_usage": True
        }
        
        slow_query_stats = {
            "execution_time_ms": 500.0,
            "rows_examined": 10000,
            "rows_returned": 10,
            "has_index_usage": False
        }
        
        # Act
        fast_score = self.optimizer.calculate_performance_score(fast_query_stats)
        slow_score = self.optimizer.calculate_performance_score(slow_query_stats)
        
        # Assert
        assert 0 <= fast_score <= 1
        assert 0 <= slow_score <= 1
        assert fast_score > slow_score


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database functionality."""

    @pytest.mark.asyncio
    async def test_database_lifecycle_management(self):
        """Test complete database lifecycle management."""
        # Arrange
        with patch('chatter.utils.database.get_engine') as mock_get_engine:
            mock_engine = AsyncMock()
            mock_get_engine.return_value = mock_engine
            
            with patch('chatter.models.base.Base.metadata') as mock_metadata:
                mock_metadata.create_all = AsyncMock()
                mock_metadata.drop_all = AsyncMock()
                
                # Act - Create tables
                create_result = await create_tables()
                
                # Act - Health check
                with patch('chatter.utils.database.get_session') as mock_get_session:
                    mock_session = AsyncMock()
                    mock_session.execute = AsyncMock(return_value=MagicMock(scalar=MagicMock(return_value=1)))
                    mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
                    
                    health = await health_check()
                
                # Act - Drop tables
                drop_result = await drop_tables()
                
                # Assert
                assert create_result is True
                assert health["status"] == "healthy"
                assert drop_result is True

    @pytest.mark.asyncio
    async def test_concurrent_database_operations(self):
        """Test concurrent database operations."""
        # Arrange
        with patch('chatter.utils.database.get_session') as mock_get_session:
            mock_sessions = [AsyncMock() for _ in range(3)]
            for session in mock_sessions:
                session.execute = AsyncMock(return_value=MagicMock(scalar=MagicMock(return_value=1)))
            
            mock_get_session.side_effect = [
                AsyncMock(__aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock(return_value=None))
                for session in mock_sessions
            ]
            
            # Act - Concurrent operations
            tasks = [health_check() for _ in range(3)]
            results = await asyncio.gather(*tasks)
            
            # Assert
            assert len(results) == 3
            assert all(result["status"] == "healthy" for result in results)

    @pytest.mark.asyncio
    async def test_database_error_recovery(self):
        """Test database error recovery mechanisms."""
        # Arrange
        connection_manager = DatabaseConnectionManager()
        
        # Simulate connection failures followed by success
        call_count = 0
        
        async def mock_connection():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise OperationalError("Connection failed", None, None)
            return MagicMock()
        
        with patch.object(connection_manager, '_attempt_connection', side_effect=mock_connection):
            # Act
            connection = await connection_manager.get_connection_with_retry(max_retries=3)
            
            # Assert
            assert connection is not None
            assert call_count == 3  # Should retry and eventually succeed

    @pytest.mark.asyncio
    async def test_database_performance_monitoring(self):
        """Test database performance monitoring."""
        # Arrange
        optimizer = QueryOptimizer()
        
        # Simulate query execution monitoring
        queries = [
            ("SELECT * FROM users WHERE id = %s", 5.0, 1, 1),
            ("SELECT * FROM posts WHERE user_id = %s", 50.0, 100, 10),
            ("SELECT COUNT(*) FROM comments", 200.0, 10000, 1)
        ]
        
        # Act - Analyze multiple queries
        analyses = []
        for query, exec_time, rows_examined, rows_returned in queries:
            stats = {
                "execution_time_ms": exec_time,
                "rows_examined": rows_examined,
                "rows_returned": rows_returned,
                "has_index_usage": exec_time < 100  # Assume fast queries use indexes
            }
            
            analysis = {
                "query": query,
                "performance_score": optimizer.calculate_performance_score(stats),
                "optimization_suggestions": optimizer.get_optimization_suggestions(query)
            }
            analyses.append(analysis)
        
        # Assert - Performance analysis results
        assert len(analyses) == 3
        
        # Fast query should have high performance score
        fast_query_analysis = analyses[0]
        assert fast_query_analysis["performance_score"] > 0.8
        
        # Slow query should have lower performance score and suggestions
        slow_query_analysis = analyses[2]
        assert slow_query_analysis["performance_score"] < 0.5
        assert len(slow_query_analysis["optimization_suggestions"]) > 0