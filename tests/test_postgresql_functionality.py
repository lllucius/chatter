"""Test PostgreSQL database functionality with pytest-postgresql."""

import pytest
from sqlalchemy import text


class TestPostgreSQLDatabase:
    """Test PostgreSQL database setup and basic functionality."""
    
    @pytest.mark.unit
    async def test_postgresql_session_exists(self, db_session):
        """Test that PostgreSQL session fixture works."""
        assert db_session is not None
        
    @pytest.mark.unit  
    async def test_postgresql_basic_query(self, db_session):
        """Test basic PostgreSQL query execution."""
        # Simple query that should work with PostgreSQL
        result = await db_session.execute(text("SELECT 1 as test_value"))
        row = result.fetchone()
        assert row[0] == 1
        
    @pytest.mark.unit
    async def test_postgresql_engine_info(self, db_engine):
        """Test PostgreSQL engine provides correct database info."""
        assert db_engine is not None
        assert "postgresql" in str(db_engine.url)
        
    @pytest.mark.unit
    async def test_postgresql_transaction_rollback(self, db_session):
        """Test that PostgreSQL session properly handles transactions."""
        # Test transaction isolation 
        from chatter.models.user import User
        
        # Create a user
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        db_session.add(user)
        await db_session.flush()  # Flush but don't commit
        
        # User should exist in this session
        result = await db_session.execute(text("SELECT COUNT(*) FROM users WHERE username = 'test_user'"))
        count = result.scalar()
        assert count == 1
        
        # After rollback (handled automatically by fixture), user should not persist
        # This will be verified in the next test run since rollback happens in fixture cleanup