"""Test transaction rollback fixes for seeding."""

import pytest
from unittest.mock import AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError

from chatter.utils.seeding import DatabaseSeeder, SeedingMode


class TestTransactionRollbackFixes:
    """Test that transaction rollback fixes work correctly."""

    @pytest.mark.asyncio
    async def test_count_users_rollback_on_table_not_exists(self):
        """Test that _count_users properly rolls back when table doesn't exist."""
        mock_session = AsyncMock(spec=AsyncSession)

        # Mock execute to raise ProgrammingError (table doesn't exist)
        mock_session.execute.side_effect = ProgrammingError(
            "relation \"users\" does not exist", None, None
        )

        seeder = DatabaseSeeder(session=mock_session)

        # Should return 0 and rollback transaction
        count = await seeder._count_users()

        assert count == 0
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_users_rollback_on_other_errors(self):
        """Test that _count_users rolls back on other database errors."""
        mock_session = AsyncMock(spec=AsyncSession)

        # Mock execute to raise general SQLAlchemy error
        mock_session.execute.side_effect = SQLAlchemyError(
            "Database connection failed"
        )

        seeder = DatabaseSeeder(session=mock_session)

        # Should raise exception and rollback transaction
        with pytest.raises(SQLAlchemyError):
            await seeder._count_users()

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_admin_user_rollback_on_query_error(self):
        """Test that _create_admin_user properly handles query errors."""
        mock_session = AsyncMock(spec=AsyncSession)

        # Mock execute to raise error on first call (existing user check)
        mock_session.execute.side_effect = [
            ProgrammingError(
                "relation \"users\" does not exist", None, None
            ),
            AsyncMock(),  # Second call (if any) should succeed
        ]

        seeder = DatabaseSeeder(session=mock_session)

        # Should handle the error and continue to create user
        admin_user = await seeder._create_admin_user(skip_existing=True)

        # Should have rolled back after failed query
        mock_session.rollback.assert_called()
        # Should have continued to create user
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_seed_database_rollback_on_count_error(self):
        """Test main seeding method handles count error gracefully."""
        mock_session = AsyncMock(spec=AsyncSession)

        seeder = DatabaseSeeder(session=mock_session)

        # Mock _count_users to raise error
        seeder._count_users = AsyncMock(
            side_effect=SQLAlchemyError("Database error")
        )
        # Mock seeding methods
        seeder._seed_minimal_data = AsyncMock()

        # Should handle count error and continue seeding
        result = await seeder.seed_database(
            SeedingMode.MINIMAL, force=False
        )

        # Should have tried to rollback after count error
        mock_session.rollback.assert_called()
        # Should have continued to seed data
        seeder._seed_minimal_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_seed_database_rollback_on_seeding_error(self):
        """Test main seeding method rolls back on seeding errors."""
        mock_session = AsyncMock(spec=AsyncSession)

        seeder = DatabaseSeeder(session=mock_session)

        # Mock _count_users to return 0 (allow seeding)
        seeder._count_users = AsyncMock(return_value=0)
        # Mock seeding method to raise error
        seeder._seed_minimal_data = AsyncMock(
            side_effect=SQLAlchemyError("Seeding failed")
        )

        # Should raise exception and rollback
        with pytest.raises(SQLAlchemyError):
            await seeder.seed_database(SeedingMode.MINIMAL, force=False)

        # Should have rolled back transaction
        mock_session.rollback.assert_called()

    @pytest.mark.asyncio
    async def test_development_users_query_error_handling(self):
        """Test development users creation handles query errors."""
        mock_session = AsyncMock(spec=AsyncSession)

        seeder = DatabaseSeeder(session=mock_session)

        # Mock execute to fail on user existence check but succeed on creation
        mock_session.execute.side_effect = [
            ProgrammingError(
                "relation \"users\" does not exist", None, None
            ),
            AsyncMock(),  # For the second user check (if any)
        ]

        # Should handle query error and continue
        users = await seeder._create_development_users(
            skip_existing=True
        )

        # Should have rolled back after failed query
        mock_session.rollback.assert_called()
        # Should have added users
        assert mock_session.add.call_count > 0
        mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_test_users_query_error_handling(self):
        """Test test users creation handles query errors."""
        mock_session = AsyncMock(spec=AsyncSession)

        seeder = DatabaseSeeder(session=mock_session)

        # Mock execute to fail on user existence check
        mock_session.execute.side_effect = ProgrammingError(
            "relation \"users\" does not exist", None, None
        )

        # Should handle query error and continue
        users = await seeder._create_test_users(skip_existing=True)

        # Should have rolled back after failed query
        mock_session.rollback.assert_called()
        # Should have added users
        assert mock_session.add.call_count > 0
        mock_session.commit.assert_called()
