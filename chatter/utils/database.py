"""Database utilities and connection management."""

import asyncio
from typing import AsyncGenerator, Optional

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

# Global database engine and session maker
_engine: Optional[AsyncEngine] = None
_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


def get_engine() -> AsyncEngine:
    """Get the database engine, creating it if necessary."""
    global _engine
    
    if _engine is None:
        database_url = settings.database_url_for_env
        
        # Engine configuration
        engine_kwargs = {
            "echo": settings.debug_database_queries,
            "future": True,
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_pre_ping": settings.db_pool_pre_ping,
            "pool_recycle": settings.db_pool_recycle,
        }
        
        # Use StaticPool for SQLite databases (testing)
        if database_url.startswith("sqlite"):
            engine_kwargs.update({
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False},
            })
        
        _engine = create_async_engine(database_url, **engine_kwargs)
        
        # Add query logging event listener
        if settings.debug_database_queries:
            @event.listens_for(_engine.sync_engine, "before_cursor_execute")
            def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                logger.debug("SQL Query", statement=statement, parameters=parameters)
    
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


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.
    
    This is typically used as a dependency in FastAPI endpoints.
    
    Yields:
        AsyncSession: Database session
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """Initialize the database and create tables."""
    engine = get_engine()
    
    # Import all models to ensure they're registered
    from chatter.models.user import User
    from chatter.models.conversation import Conversation, Message
    from chatter.models.document import Document, DocumentChunk
    from chatter.models.analytics import ConversationStats, DocumentStats, PromptStats, ProfileStats
    from chatter.models.profile import Profile
    from chatter.models.prompt import Prompt
    
    logger.info("Creating database tables")
    
    # For PostgreSQL, ensure pgvector extension is installed
    if "postgresql" in settings.database_url_for_env:
        async with engine.begin() as conn:
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                logger.info("Ensured pgvector extension is installed")
            except Exception as e:
                logger.warning("Could not install pgvector extension", error=str(e))
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
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
    
    def __init__(self):
        self.session: Optional[AsyncSession] = None
    
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


async def health_check() -> dict:
    """Perform database health check.
    
    Returns:
        dict: Health check results
    """
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Test basic connection
        is_connected = await check_database_connection()
        
        # Test query performance
        async with DatabaseManager() as session:
            await session.execute(text("SELECT version()"))
        
        end_time = asyncio.get_event_loop().time()
        response_time = round((end_time - start_time) * 1000, 2)  # ms
        
        return {
            "status": "healthy" if is_connected else "unhealthy",
            "connected": is_connected,
            "response_time_ms": response_time,
            "database_url": settings.database_url_for_env.split("@")[-1],  # Hide credentials
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
        }