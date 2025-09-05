"""Test configuration and shared fixtures."""

import asyncio
import os
from collections.abc import AsyncGenerator

# Set up test environment before any other imports
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test_user:test_password@localhost:5432/chatter_test")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing")
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("REDIS_ENABLED", "false")  # Disable Redis for tests to avoid connection issues
os.environ.setdefault("CACHE_BACKEND", "memory")  # Use memory cache instead of Redis

# Ensure asyncio uses the default policy for tests (not uvloop)
# This prevents conflicts with pytest-asyncio
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from chatter.utils.database import Base, get_session_generator


@pytest.fixture(scope="function") 
def app(db_session: AsyncSession):
    """
    Create a FastAPI application with test database session override.
    
    This fixture creates the FastAPI application and overrides the
    get_session_generator dependency to use the test database session
    instead of the production database. This ensures that all API
    endpoints use the test database with proper transaction isolation.
    
    Uses lazy import to avoid hanging during test collection.
    
    Args:
        db_session: The test database session
        
    Returns:
        FastAPI application configured for testing
    """
    # Reset asyncio event loop policy to default for testing
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    
    # Create a minimal FastAPI application for testing without lifespan
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from chatter.config import settings
    from chatter.utils.logging import setup_logging
    
    # Set up logging first
    setup_logging()
    
    # Create minimal FastAPI app without lifespan to avoid initialization issues
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        debug=settings.debug,
        # Don't use lifespan for tests to avoid database initialization conflicts
        lifespan=None,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_version="3.0.3",
        openapi_url="/openapi.json",
    )
    
    # Add minimal CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Override the database session dependency
    def get_test_session():
        """Override database session for testing."""
        return db_session

    # Replace the production dependency with our test version
    app.dependency_overrides[get_session_generator] = get_test_session
    
    # Include all routes needed for comprehensive testing
    from chatter.api import (
        ab_testing,
        agents,
        analytics,
        auth,
        chat,
        data_management,
        documents,
        events,
        health,
        jobs,
        model_registry,
        plugins,
        profiles,
        prompts,
        toolserver,
    )

    # Add all routes for testing
    app.include_router(health.router, tags=["Health"])
    app.include_router(
        auth.router,
        prefix=f"{settings.api_prefix}/auth",
        tags=["Authentication"],
    )
    app.include_router(
        chat.router,
        prefix=f"{settings.api_prefix}/chat",
        tags=["Chat"]
    )
    app.include_router(
        documents.router,
        prefix=f"{settings.api_prefix}/documents",
        tags=["Documents"],
    )
    app.include_router(
        profiles.router,
        prefix=f"{settings.api_prefix}/profiles",
        tags=["Profiles"],
    )
    app.include_router(
        prompts.router,
        prefix=f"{settings.api_prefix}/prompts",
        tags=["Prompts"],
    )
    app.include_router(
        analytics.router,
        prefix=f"{settings.api_prefix}/analytics",
        tags=["Analytics"],
    )
    app.include_router(
        toolserver.router,
        prefix=f"{settings.api_prefix}/toolservers",
        tags=["Tool Servers"],
    )
    app.include_router(
        agents.router,
        prefix=f"{settings.api_prefix}/agents",
        tags=["Agents"],
    )
    app.include_router(
        ab_testing.router,
        prefix=f"{settings.api_prefix}/ab-tests",
        tags=["A/B Testing"],
    )
    app.include_router(
        events.router,
        prefix=f"{settings.api_prefix}/events",
        tags=["Events"],
    )
    app.include_router(
        plugins.router,
        prefix=f"{settings.api_prefix}/plugins",
        tags=["Plugins"],
    )
    app.include_router(
        jobs.router,
        prefix=f"{settings.api_prefix}/jobs",
        tags=["Jobs"],
    )
    app.include_router(
        data_management.router,
        prefix=f"{settings.api_prefix}/data",
        tags=["Data Management"],
    )
    app.include_router(
        model_registry.router,
        prefix=f"{settings.api_prefix}/models",
        tags=["Model Registry"],
    )

    return app


# =============================================================================
# POSTGRESQL FIXTURES using real PostgreSQL server
# =============================================================================

@pytest.fixture(scope="function")
async def db_engine():
    """
    Create a function-scoped database engine for testing.
    
    Uses real PostgreSQL server for testing, providing full database functionality
    including constraints, extensions, and optimizations.
    """
    # Lazy import to avoid hanging during test collection
    from chatter.config import settings

    # Import all models to ensure they're registered with Base.metadata
    import chatter.models  # This will import all models
    from sqlalchemy import text

    # Use the test database URL from configuration
    db_url = settings.test_database_url

    # Create async engine with test-appropriate settings
    # Set poolclass to NullPool to avoid event loop attachment issues
    engine = create_async_engine(
        db_url,
        echo=False,  # Set to True for SQL query debugging
        poolclass=NullPool,  # Use NullPool to avoid connection reuse across event loops
        pool_pre_ping=False,  # Disable pre-ping for NullPool
    )

    # Create all tables and ensure pgvector extension is available
    try:
        async with engine.begin() as conn:
            # Try to install pgvector extension (fail silently if not available)
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            except Exception:
                # pgvector may not be available in test environment
                pass

            # Create tables if they don't exist (idempotent operation)
            await conn.run_sync(Base.metadata.create_all)

    except Exception:
        # If anything fails, try without the vector extension
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="function")
async def db_setup(db_engine):
    """
    Set up database schema once per test session.
    
    This fixture applies SQLAlchemy models to create the database schema.
    It runs once per test session to set up all tables and relationships.
    Uses real PostgreSQL server for full database constraints and functionality.
    
    Args:
        db_engine: The database engine from db_engine fixture
        
    Returns:
        AsyncGenerator yielding after schema setup is complete
    """
    # Schema is already created in db_engine fixture for PostgreSQL
    yield


@pytest.fixture(scope="function")
async def db_session(db_engine, db_setup) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session with transaction rollback per test.
    
    This fixture creates a new database session for each test and ensures
    that all changes are rolled back after the test completes. This provides
    test isolation - each test starts with a clean database state.
    
    Args:
        db_engine: The database engine
        db_setup: Ensures database schema is set up
        
    Returns:
        AsyncGenerator yielding a database session
    """
    # Import all models to ensure they're available for cleanup
    import chatter.models  # This will import all models
    from sqlalchemy import text
    
    # Create a session maker bound to the engine
    session_maker = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,  # Disable autoflush for better control in tests
        autocommit=False,  # Ensure we're in a transaction
    )
    
    # Create a new session
    session = session_maker()
    session.info["_in_test"] = True  # Mark session as being used in tests
    
    try:
        # Clean up existing data before the test (only tables that exist)
        try:
            # Get list of existing tables  
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """))
            tables = [row[0] for row in result.fetchall()]
            
            # Truncate tables with CASCADE to handle foreign keys
            if tables:
                await session.execute(text("TRUNCATE TABLE " + ", ".join(tables) + " CASCADE;"))
                await session.commit()
        except Exception:
            # If cleanup fails, rollback and continue - test will still be isolated
            await session.rollback()
        
        yield session
    except Exception:
        # Rollback on any exception
        try:
            await session.rollback()
        except Exception:
            pass  # Ignore rollback errors during exception handling
        raise
    finally:
        # Always rollback and close to ensure cleanup
        try:
            await session.rollback()
        except Exception:
            pass  # Ignore rollback errors during cleanup
        try:
            await session.close()
        except Exception:
            pass  # Ignore close errors during cleanup


@pytest.fixture
async def client(app) -> AsyncGenerator:
    """
    Create an async HTTP client for testing FastAPI routes.
    
    Args:
        app: The FastAPI application
        
    Returns:
        AsyncGenerator yielding an HTTP client
    """
    # Lazy import to avoid hanging issues
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture
async def auth_headers(client) -> dict[str, str]:
    """
    Create authentication headers for testing protected endpoints.
    
    Args:
        client: The HTTP client for making requests
        
    Returns:
        Dictionary with Authorization header
    """
    import uuid
    import string
    import random
    
    # Generate a more username-friendly unique identifier
    # Use only lowercase letters and numbers, starting with a letter
    unique_base = str(uuid.uuid4()).replace('-', '')[:8]
    # Ensure it starts with a letter and only contains alphanumeric characters
    safe_id = 'user' + ''.join(c for c in unique_base if c.isalnum()).lower()
    
    user_data = {
        "username": safe_id,
        "email": f"{safe_id}@example.com", 
        "password": "SecureP@ssw0rd!",
        "full_name": f"Test User {safe_id}",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    auth_response = response.json()
    access_token = auth_response["access_token"]
    print("ACCESS TOKEN", access_token)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_user_data() -> dict:
    """Test user data for registration."""
    return {
        "username": "alice",
        "email": "alice@example.com",
        "password": "SecureP@ssw0rd!",
        "full_name": "Alice User",
    }


@pytest.fixture
def test_login_data() -> dict:
    """Test login data."""
    return {
        "username": "alice", 
        "password": "SecureP@ssw0rd!",
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    # These are already set at the top of the file, but keep for compatibility
    pass
