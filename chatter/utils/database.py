"""Database utilities and connection management."""

import asyncio
from collections.abc import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from chatter.config import settings
from chatter.models.base import Base
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

# Global database engine and session maker
_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get the database engine, creating it if necessary."""
    global _engine

    if _engine is None:
        database_url = settings.database_url_for_env

        # Engine configuration
        engine_kwargs = {
            "echo": settings.debug_database_queries,
            "future": True,
        }

        # PostgreSQL-specific settings
        engine_kwargs.update(
            {
                "pool_size": settings.db_pool_size,
                "max_overflow": settings.db_max_overflow,
                "pool_pre_ping": settings.db_pool_pre_ping,
                "pool_recycle": settings.db_pool_recycle,
            }
        )

        _engine = create_async_engine(database_url, **engine_kwargs)

        # Add query logging event listener
        if settings.debug_database_queries:
            try:

                @event.listens_for(
                    _engine.sync_engine, "before_cursor_execute"
                )
                def receive_before_cursor_execute(
                    conn,
                    cursor,
                    statement,
                    parameters,
                    context,
                    executemany,
                ):
                    """Log SQL queries when debug mode is enabled."""
                    logger.debug(
                        "SQL Query",
                        statement=statement,
                        parameters=parameters,
                    )

            except Exception as e:
                # Ignore event listener setup errors (e.g., in tests with mocked engines)
                logger.debug(
                    "Could not set up query logging", error=str(e)
                )

    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get the session maker, creating it if necessary."""
    global _session_maker

    if _session_maker is None:
        engine = get_engine()
        _session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    return _session_maker


async def get_session_generator() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session as generator (for FastAPI dependency injection).

    This is typically used as a dependency in FastAPI endpoints.

    Yields:
        AsyncSession: Database session
    """
    session_maker = get_session_maker()
    session = session_maker()

    try:
        yield session
    except GeneratorExit:
        # Handle generator cleanup gracefully
        # On GeneratorExit, avoid operations that might conflict with ongoing transactions
        logger.debug("Database session generator closed")
        try:
            # Check if session is still usable before attempting cleanup
            if session:
                # Be very conservative on GeneratorExit - don't do anything that might hang
                # Just expunge objects to clear the session state
                try:
                    session.expunge_all()
                except Exception:
                    # Even expunge_all might fail, so be defensive
                    pass
        except Exception as e:
            logger.debug(
                "Session cleanup during generator exit", error=str(e)
            )
        raise
    except Exception:
        # On other exceptions, attempt rollback
        try:
            if session:
                await session.rollback()
        except Exception as e:
            logger.warning("Error rolling back session", error=str(e))
        raise
    else:
        # Normal completion - commit the transaction
        try:
            if session:
                await session.commit()
        except Exception as e:
            logger.warning("Error committing session", error=str(e))
            try:
                await session.rollback()
            except Exception:
                pass
            raise
    finally:
        # Final cleanup - close the session if it's still open and safe to do so
        try:
            if session:
                # Be more defensive about session cleanup to avoid hangs
                # Check if the session is still bound and usable before attempting operations
                try:
                    # Only attempt close if the session is not in an active transaction
                    # and we actually own the session lifecycle
                    if (
                        hasattr(session, "_connection")
                        and session._connection is not None
                    ):
                        # Check if we're in a transaction - but be more defensive
                        in_transaction = False
                        try:
                            in_transaction = session.in_transaction()
                        except Exception:
                            # If we can't determine transaction state, assume we're in one
                            in_transaction = True

                        if not in_transaction:
                            await session.close()
                        else:
                            # If in transaction, just expunge to avoid cleanup conflicts
                            session.expunge_all()
                    else:
                        # Session is already detached/closed, nothing to do
                        pass
                except Exception as cleanup_error:
                    # Log but don't re-raise cleanup errors to avoid masking original issues
                    logger.debug(
                        "Session cleanup skipped due to error",
                        error=str(cleanup_error),
                    )
        except Exception as e:
            logger.debug("Error in final session cleanup", error=str(e))


async def init_database() -> None:
    """Initialize the database and create tables."""
    engine = get_engine()

    # Import all models to ensure they're registered
    import chatter.models  # noqa: F401

    logger.info("Creating database tables")

    # For PostgreSQL, ensure pgvector extension is installed
    # Execute this in a separate connection to avoid statement concatenation issues
    async with engine.connect() as conn:
        try:
            # Use a separate transaction for extension creation to prevent
            # conflicts with any advisory locks or other statements
            async with conn.begin():
                await conn.execute(
                    text("CREATE EXTENSION IF NOT EXISTS vector")
                )
            logger.info("Ensured pgvector extension is installed")
        except Exception as e:
            logger.warning(
                "Could not install pgvector extension", error=str(e)
            )

    # Create all tables in a separate transaction
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created")

    logger.info("Database initialization completed")


async def check_database_connection() -> bool:
    """Check if database connection is working.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database connection check failed", error=str(e))
        return False


async def close_database() -> None:
    """Close database connections."""
    global _engine, _session_maker

    if _engine:
        await _engine.dispose()
        _engine = None

    _session_maker = None
    logger.info("Database connections closed")


class DatabaseManager:
    """Context manager for database operations."""

    def __init__(self) -> None:
        """Initialize database session context."""
        self.session: AsyncSession | None = None
        self.active_sessions: dict = {}
        # Allow engine to be overridden for testing
        self.engine = get_engine()

    async def __aenter__(self) -> AsyncSession:
        """Enter async context and create session."""
        session_maker = get_session_maker()
        self.session = session_maker()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context and close session."""
        if self.session:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
            await self.session.close()

    async def get_pool_stats(self) -> dict:
        """Get connection pool statistics."""
        engine = self.engine
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_out": pool.checked_out(),
            "checked_in": pool.checked_in(),
            "available": pool.checked_in(),
        }



    async def transaction(self, session: AsyncSession):
        """Context manager for database transactions."""

        class TransactionContext:
            def __init__(self, session):
                self.session = session

            async def __aenter__(self):
                await self.session.begin()
                return self.session

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if exc_type:
                    await self.session.rollback()
                else:
                    await self.session.commit()

        return TransactionContext(session)

    async def detect_connection_leaks(
        self, max_age_seconds: int = 1800
    ):
        """Detect connection leaks based on session age."""
        import time

        current_time = time.time()
        leaked_sessions = []

        for _session_id, session_info in self.active_sessions.items():
            session_age = current_time - session_info.get(
                "created_at", current_time
            )
            if session_age > max_age_seconds:
                leaked_sessions.append(session_info)

        return leaked_sessions


async def execute_query(query: str, **params) -> any:
    """Execute a raw SQL query.

    Args:
        query: SQL query string
        **params: Query parameters

    Returns:
        Query result
    """
    async with DatabaseManager() as session:
        result = await session.execute(text(query), params)
        return result


async def health_check(session: AsyncSession | None = None) -> dict:
    """Perform database health check.

    Args:
        session: Optional database session to use. If None, creates a new one.

    Returns:
        dict: Health check results
    """
    try:
        start_time = asyncio.get_event_loop().time()
        is_connected = False

        if session is not None:
            # Use the provided session
            await session.execute(text("SELECT 1"))
            is_connected = True

            # Test query performance with a simple query
            await session.execute(text("SELECT 1"))
        else:
            # Create a new session using DatabaseManager
            async with DatabaseManager() as db_session:
                # Test basic connection
                await db_session.execute(text("SELECT 1"))
                is_connected = True

                # Test query performance with a simple query
                await db_session.execute(text("SELECT 1"))

        end_time = asyncio.get_event_loop().time()
        response_time = round((end_time - start_time) * 1000, 2)  # ms

        return {
            "status": "healthy" if is_connected else "unhealthy",
            "connected": is_connected,
            "response_time_ms": response_time,
            # Don't expose full database URL for security
            "database_type": "postgresql",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
        }


async def create_tables() -> bool:
    """Create database tables.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return True
    except Exception as e:
        logger.error("Failed to create tables", error=str(e))
        return False


async def drop_tables() -> bool:
    """Drop database tables.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        return True
    except Exception as e:
        logger.error("Failed to drop tables", error=str(e))
        return False
