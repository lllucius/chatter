"""Test configuration and shared fixtures."""

import asyncio
import os
from collections.abc import AsyncGenerator

# Set up test environment before any other imports  
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing")
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test_user:test_password@localhost:5432/chatter_test")
os.environ.setdefault("REDIS_ENABLED", "false")  # Disable Redis for tests to avoid connection issues
os.environ.setdefault("CACHE_BACKEND", "memory")  # Use memory cache instead of Redis
os.environ.setdefault("CHATTER_ENCRYPTION_KEY", "m7y0DnHHivzNFy4GH8VbiBSrG6r-NAA8KDyfB5CzUEo=")  # Set proper Fernet key for crypto tests

# Ensure asyncio uses the default policy for tests (not uvloop)
# This prevents conflicts with pytest-asyncio
_original_policy = None
try:
    _original_policy = asyncio.get_event_loop_policy()
    import uvloop
    # If uvloop is installed, we need to reset to default policy for tests
    if isinstance(_original_policy, uvloop.EventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
except ImportError:
    # uvloop not installed, just ensure default policy
    if not isinstance(asyncio.get_event_loop_policy(), asyncio.DefaultEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

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
    Create a function-scoped PostgreSQL database engine for testing.
    
    Uses PostgreSQL test database for realistic testing that matches production.
    Uses simple table cleanup instead of full schema recreation to avoid transaction issues.
    """
    from chatter.config import settings
    from sqlalchemy import text
    
    # Import all models to ensure they're registered with Base.metadata
    import chatter.models
    
    # Use PostgreSQL test database 
    db_url = settings.database_url_for_env
    
    # Create async engine for PostgreSQL
    engine = create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    
    # Ensure tables exist (create once, reuse)
    async with engine.begin() as conn:
        try:
            # Try to enable pgvector extension if available (graceful fallback)
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            except Exception:
                # Ignore if pgvector is not available
                pass
            
            # Create all tables if they don't exist (idempotent)
            await conn.run_sync(Base.metadata.create_all)
            
        except Exception as e:
            print(f"Schema setup error (may be normal if tables exist): {e}")
            # Don't fail if tables already exist
    
    try:
        yield engine
    finally:
        # Just dispose, don't try to drop tables
        try:
            await engine.dispose()
        except Exception:
            pass


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
    Provide a database session with clean state per test.
    
    Cleans up test data before each test to ensure isolation.
    """
    import chatter.models
    from sqlalchemy import text
    
    # Create a session maker bound to the engine
    session_maker = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    
    # Create a new session
    session = session_maker()
    session.info["_in_test"] = True
    
    # Clean up any existing data before the test
    try:
        # Use a separate connection for cleanup to avoid transaction conflicts
        async with db_engine.begin() as cleanup_conn:
            # Get all table names
            result = await cleanup_conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename NOT LIKE 'pg_%'
                ORDER BY tablename
            """))
            table_names = [row[0] for row in result.fetchall()]
            
            # Disable foreign key checks temporarily, truncate, then re-enable
            if table_names:
                # Truncate all tables
                for table in table_names:
                    try:
                        await cleanup_conn.execute(text(f'TRUNCATE TABLE "{table}" CASCADE;'))
                    except Exception:
                        # Table might not exist or have dependencies, ignore
                        pass
                        
    except Exception as e:
        print(f"Cleanup warning (continuing): {e}")
    
    try:
        yield session
    except Exception as e:
        print(f"Database session error: {e}")
        try:
            await session.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            await session.close()
        except Exception:
            pass


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
    # Use only lowercase letters to avoid sequential pattern validation
    unique_base = str(uuid.uuid4()).replace('-', '')
    # Filter out numbers and use only letters to avoid validation issues
    safe_chars = ''.join(c for c in unique_base if c.isalpha()).lower()[:8]
    # Ensure we have enough characters, pad with random letters if needed
    while len(safe_chars) < 6:
        safe_chars += random.choice(string.ascii_lowercase)
    safe_id = 'testuser' + safe_chars[:6]
    
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
    """Setup test environment variables and reset global state."""
    # Store original values
    original_env = dict(os.environ)
    
    # Set test environment variables
    test_env = {
        "DATABASE_URL": "sqlite:///test.db",
        "SECRET_KEY": "test_secret_key_for_testing", 
        "ENVIRONMENT": "testing",
        "REDIS_ENABLED": "false",
        "CACHE_BACKEND": "memory",
        "CHATTER_ENCRYPTION_KEY": "m7y0DnHHivzNFy4GH8VbiBSrG6r-NAA8KDyfB5CzUEo=",
    }
    
    # Update environment
    os.environ.update(test_env)
    
    # Reset asyncio policy for this test
    original_policy = asyncio.get_event_loop_policy()
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    
    # Reset any global settings that might be cached
    import sys
    config_modules = [name for name in sys.modules.keys() if name and name.startswith('chatter.config')]
    for module_name in config_modules:
        module = sys.modules[module_name]
        # Force reload of settings if present
        if hasattr(module, 'settings'):
            # Clear the cached settings to force recreation
            try:
                # Create new settings with current environment
                from chatter.config import Settings
                module.settings = Settings()
            except Exception:
                # If settings creation fails, don't fail the test
                pass
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
    
    # Restore original event loop policy
    try:
        asyncio.set_event_loop_policy(original_policy)
    except Exception:
        pass
