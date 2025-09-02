"""Tests for database utilities and connection management."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import text

from chatter.utils.database import (
    DatabaseConnectionManager,
    QueryOptimizer,
    create_tables,
    drop_tables,
    get_engine,
    get_session,
    health_check,
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
        with patch(
            'chatter.utils.database.get_session_maker'
        ) as mock_get_maker:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session_maker = MagicMock()
            mock_session_maker.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_maker.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
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
        with patch(
            'chatter.utils.database.get_engine'
        ) as mock_get_engine:
            mock_engine = AsyncMock(spec=AsyncEngine)
            mock_get_engine.return_value = mock_engine

            with patch(
                'chatter.models.base.Base.metadata'
            ) as mock_metadata:
                mock_metadata.create_all = AsyncMock()

                # Act
                result = await create_tables()

                # Assert
                assert result is True
                mock_metadata.create_all.assert_called_once_with(
                    mock_engine
                )

    @pytest.mark.asyncio
    async def test_create_tables_failure(self):
        """Test table creation failure."""
        # Arrange
        with patch(
            'chatter.utils.database.get_engine'
        ) as mock_get_engine:
            mock_engine = AsyncMock(spec=AsyncEngine)
            mock_get_engine.return_value = mock_engine

            with patch(
                'chatter.models.base.Base.metadata'
            ) as mock_metadata:
                mock_metadata.create_all = AsyncMock(
                    side_effect=OperationalError(
                        "Connection failed", None, None
                    )
                )

                # Act
                result = await create_tables()

                # Assert
                assert result is False

    @pytest.mark.asyncio
    async def test_drop_tables_success(self):
        """Test successful table dropping."""
        # Arrange
        with patch(
            'chatter.utils.database.get_engine'
        ) as mock_get_engine:
            mock_engine = AsyncMock(spec=AsyncEngine)
            mock_get_engine.return_value = mock_engine

            with patch(
                'chatter.models.base.Base.metadata'
            ) as mock_metadata:
                mock_metadata.drop_all = AsyncMock()

                # Act
                result = await drop_tables()

                # Assert
                assert result is True
                mock_metadata.drop_all.assert_called_once_with(
                    mock_engine
                )

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful database health check."""
        # Arrange
        with patch(
            'chatter.utils.database.get_session'
        ) as mock_get_session:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(
                return_value=MagicMock(scalar=MagicMock(return_value=1))
            )
            mock_get_session.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_get_session.return_value.__aexit__ = AsyncMock(
                return_value=None
            )

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
        with patch(
            'chatter.utils.database.get_session'
        ) as mock_get_session:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(
                side_effect=OperationalError(
                    "Connection failed", None, None
                )
            )
            mock_get_session.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_get_session.return_value.__aexit__ = AsyncMock(
                return_value=None
            )

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
            mock_settings.database_url_for_env = (
                "postgresql+asyncpg://user:pass@localhost/testdb"
            )
            mock_settings.debug_database_queries = True

            # Act
            with patch(
                'chatter.utils.database.create_async_engine'
            ) as mock_create_engine:
                mock_engine = MagicMock()
                mock_create_engine.return_value = mock_engine

                get_engine()

                # Assert
                mock_create_engine.assert_called_once()
                args, kwargs = mock_create_engine.call_args
                assert (
                    args[0]
                    == "postgresql+asyncpg://user:pass@localhost/testdb"
                )
                assert kwargs["echo"] is True


@pytest.mark.unit
class TestRealDatabaseUtilities:
    """Test database utility functions with real PostgreSQL database."""

    @pytest.mark.asyncio
    async def test_real_database_connection(self, test_db_session):
        """Test that we can connect to a real database."""
        # Test basic database connectivity with real PostgreSQL
        result = await test_db_session.execute(text("SELECT 1 as test_col"))
        row = result.fetchone()
        assert row[0] == 1

    @pytest.mark.asyncio
    async def test_real_database_tables_exist(self, test_db_session):
        """Test that tables are created in the real database."""
        # Test that tables exist in the real PostgreSQL instance
        # Use test_db_session since it already has tables created
        result = await test_db_session.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
        ))
        tables = [row[0] for row in result.fetchall()]
        
        # Check for some expected tables
        expected_tables = ["users", "conversations", "documents", "profiles"]
        for table in expected_tables:
            assert table in tables, f"Table {table} should exist"

    @pytest.mark.asyncio
    async def test_real_database_session_operations(self, test_db_session):
        """Test basic database operations with real session."""
        # Test that we can create and query a user with real database
        from chatter.models.user import User
        
        # Create a test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_here",
            full_name="Test User",
        )
        
        # Add user to session
        test_db_session.add(test_user)
        await test_db_session.commit()
        await test_db_session.refresh(test_user)
        
        # Verify user was created
        assert test_user.id is not None
        assert test_user.email == "test@example.com"
        assert test_user.username == "testuser"

    @pytest.mark.asyncio
    async def test_real_database_transaction_rollback(self, test_db_session):
        """Test transaction rollback with real database."""
        from chatter.models.user import User
        
        # Create a test user but don't commit
        test_user = User(
            email="rollback@example.com",
            username="rollbackuser",
            hashed_password="hashed_password_here",
            full_name="Rollback User",
        )
        
        test_db_session.add(test_user)
        # Intentionally rollback
        await test_db_session.rollback()
        
        # Verify user was not saved
        result = await test_db_session.execute(
            text("SELECT COUNT(*) FROM users WHERE email = 'rollback@example.com'")
        )
        count = result.scalar()
        assert count == 0


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
        with patch.object(
            self.connection_manager, 'engine'
        ) as mock_engine:
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

        with patch.object(
            self.connection_manager,
            '_attempt_connection',
            side_effect=mock_connect,
        ):
            # Act
            connection = (
                await self.connection_manager.get_connection_with_retry(
                    max_retries=3
                )
            )

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

        with patch.object(
            self.connection_manager,
            '_attempt_connection',
            side_effect=slow_connection,
        ):
            # Act & Assert
            with pytest.raises(asyncio.TimeoutError):
                await self.connection_manager.get_connection_with_timeout(
                    timeout_seconds=1
                )

    @pytest.mark.asyncio
    async def test_transaction_management(self):
        """Test transaction management utilities."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.begin = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        # Act - Successful transaction
        async with self.connection_manager.transaction(mock_session):
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
            async with self.connection_manager.transaction(
                mock_session
            ):
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
            session.created_at = (
                asyncio.get_event_loop().time() - 3600
            )  # 1 hour ago

        self.connection_manager.active_sessions = mock_sessions

        # Act
        leaked_sessions = (
            await self.connection_manager.detect_connection_leaks(
                max_age_seconds=1800
            )
        )

        # Assert
        assert (
            len(leaked_sessions) == 3
        )  # All sessions are older than 30 minutes


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
        slow_query = (
            "SELECT * FROM large_table WHERE column1 LIKE '%search%'"
        )

        # Act
        suggestions = self.optimizer.get_optimization_suggestions(
            slow_query
        )

        # Assert
        assert len(suggestions) > 0
        assert any(
            "wildcard" in suggestion.lower()
            for suggestion in suggestions
        )
        assert any(
            "index" in suggestion.lower() for suggestion in suggestions
        )

    def test_query_execution_plan_analysis(self):
        """Test query execution plan analysis."""
        # Arrange
        mock_explain_result = [
            {
                "Plan": {
                    "Node Type": "Seq Scan",
                    "Total Cost": 100.5,
                    "Rows": 1000,
                }
            }
        ]

        # Act
        analysis = self.optimizer.analyze_execution_plan(
            mock_explain_result
        )

        # Assert
        assert analysis["total_cost"] == 100.5
        assert analysis["estimated_rows"] == 1000
        assert analysis["has_sequential_scan"] is True
        assert (
            analysis["performance_score"] < 0.8
        )  # Sequential scan should score lower

    def test_index_recommendation(self):
        """Test index recommendation based on query patterns."""
        # Arrange
        queries = [
            "SELECT * FROM users WHERE email = %s",
            "SELECT * FROM users WHERE email = %s AND status = %s",
            "SELECT name FROM users WHERE email = %s",
        ]

        # Act
        recommendations = self.optimizer.recommend_indexes(queries)

        # Assert
        assert len(recommendations) > 0
        email_index = next(
            (
                rec
                for rec in recommendations
                if "email" in rec["columns"]
            ),
            None,
        )
        assert email_index is not None
        assert email_index["table"] == "users"

    def test_query_caching_suggestions(self):
        """Test query caching suggestions."""
        # Arrange
        frequent_query = (
            "SELECT COUNT(*) FROM posts WHERE published = true"
        )
        execution_count = 100
        avg_execution_time = 50.0  # milliseconds

        # Act
        cache_suggestion = self.optimizer.suggest_caching(
            query=frequent_query,
            execution_count=execution_count,
            avg_execution_time_ms=avg_execution_time,
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
            "has_index_usage": True,
        }

        slow_query_stats = {
            "execution_time_ms": 500.0,
            "rows_examined": 10000,
            "rows_returned": 10,
            "has_index_usage": False,
        }

        # Act
        fast_score = self.optimizer.calculate_performance_score(
            fast_query_stats
        )
        slow_score = self.optimizer.calculate_performance_score(
            slow_query_stats
        )

        # Assert
        assert 0 <= fast_score <= 1
        assert 0 <= slow_score <= 1
        assert fast_score > slow_score


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database functionality."""

    @pytest.mark.asyncio
    async def test_database_lifecycle_management(self, test_db_engine, test_db_session):
        """Test complete database lifecycle management with real database."""
        # Act - Test that tables are created (already done by test_db_session fixture)
        # Verify tables exist by querying information_schema
        result = await test_db_session.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
        ))
        table_count = result.scalar()
        
        # Act - Health check with real database
        # Test database connectivity
        health_result = await test_db_session.execute(text("SELECT 1"))
        health_value = health_result.scalar()
        
        # Act - Test connection management
        # Verify the engine is properly configured
        assert test_db_engine is not None
        
        # Assert
        assert table_count > 0, "Tables should be created in the database"
        assert health_value == 1, "Database health check should succeed"

    @pytest.mark.asyncio
    async def test_concurrent_database_operations(self, test_db_engine):
        """Test concurrent database operations with real database."""
        # Use real database engine to create multiple sessions
        from sqlalchemy.ext.asyncio import async_sessionmaker
        
        session_maker = async_sessionmaker(
            test_db_engine,
            expire_on_commit=False,
        )
        
        # Act - Concurrent database operations
        async def perform_database_operation(session_id):
            async with session_maker() as session:
                # Perform a simple query
                result = await session.execute(text(f"SELECT {session_id} as session_id"))
                return result.scalar()
        
        # Execute concurrent operations
        tasks = [perform_database_operation(i + 1) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Assert
        assert len(results) == 3
        assert results == [1, 2, 3], "All concurrent operations should complete successfully"

    @pytest.mark.asyncio
    async def test_database_error_recovery(self, test_db_session):
        """Test database error recovery mechanisms with real database."""
        # Test that database recovers from transaction errors
        from chatter.models.user import User
        from sqlalchemy.exc import IntegrityError
        
        # First, create a user to establish a valid state
        user1 = User(
            email="test1@example.com",
            username="testuser1",
            hashed_password="hashed_password_here",
            full_name="Test User 1",
        )
        test_db_session.add(user1)
        await test_db_session.commit()
        
        # Attempt to create a user with duplicate email (should cause error)
        user2 = User(
            email="test1@example.com",  # Same email as user1
            username="testuser2",
            hashed_password="hashed_password_here",
            full_name="Test User 2",
        )
        test_db_session.add(user2)
        
        # This should raise an IntegrityError due to unique constraint
        with pytest.raises(IntegrityError):
            await test_db_session.commit()
        
        # Rollback and verify session is still usable
        await test_db_session.rollback()
        
        # Verify we can still perform operations after error recovery
        result = await test_db_session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        
        # Assert - Database should have recovered and be operational
        assert user_count == 1, "Should have one user after error recovery"

    @pytest.mark.asyncio
    async def test_database_performance_monitoring(self, test_db_session):
        """Test database performance monitoring with real database."""
        import time
        from chatter.models.user import User
        
        # Create some test data for performance testing
        users = []
        for i in range(5):
            user = User(
                email=f"perftest{i}@example.com",
                username=f"perfuser{i}",
                hashed_password="hashed_password_here",
                full_name=f"Performance User {i}",
            )
            users.append(user)
            test_db_session.add(user)
        
        await test_db_session.commit()
        
        # Test query performance with real database operations
        queries_and_performance = []
        
        # Fast query - single user lookup
        start_time = time.time()
        result = await test_db_session.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": "perftest0@example.com"}
        )
        end_time = time.time()
        fast_query_time = (end_time - start_time) * 1000  # Convert to milliseconds
        queries_and_performance.append({
            "query": "SELECT * FROM users WHERE email = %s",
            "execution_time_ms": fast_query_time,
            "rows_returned": len(result.fetchall()),
        })
        
        # Slower query - count all users
        start_time = time.time()
        result = await test_db_session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        end_time = time.time()
        count_query_time = (end_time - start_time) * 1000
        queries_and_performance.append({
            "query": "SELECT COUNT(*) FROM users",
            "execution_time_ms": count_query_time,
            "rows_returned": 1,
        })
        
        # Assert - Performance monitoring results
        assert len(queries_and_performance) == 2
        
        # All queries should complete in reasonable time (less than 1 second)
        for query_perf in queries_and_performance:
            assert query_perf["execution_time_ms"] < 1000, f"Query too slow: {query_perf['query']}"
        
        # Verify we got the expected data
        assert count == 5, "Should have 5 test users"
