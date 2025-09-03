"""Test configuration and shared fixtures."""

import asyncio
import os
from typing import AsyncGenerator, Generator

# Set up test environment before any other imports
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test_user:test_password@localhost:5432/chatter_test")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing")
os.environ.setdefault("ENVIRONMENT", "testing")

import pytest
from pytest_postgresql import factories
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from chatter.utils.database import Base, get_session_generator


@pytest.fixture
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
    # Lazy import to avoid hanging during test collection
    from chatter.main import create_app
    from fastapi import FastAPI
    
    # Create the FastAPI application
    app = create_app()
    
    # Override the database session dependency
    async def get_test_session():
        """Override database session for testing."""
        yield db_session
    
    # Replace the production dependency with our test version
    app.dependency_overrides[get_session_generator] = get_test_session
    
    return app


# =============================================================================
# POSTGRESQL FIXTURES using pytest-postgresql
# =============================================================================

# Create a PostgreSQL test database factory
postgresql_proc = factories.postgresql_proc(
    port=None,  # Use any available port
    unixsocketdir="/tmp",  # Use tmp directory for socket
)

# Create session-scoped postgresql fixture using the proc
@pytest.fixture(scope="session")
def postgresql_session(postgresql_proc):
    """Session-scoped PostgreSQL database connection."""
    from pytest_postgresql.janitor import DatabaseJanitor
    import psycopg

    pg_host = postgresql_proc.host
    pg_port = postgresql_proc.port
    pg_user = postgresql_proc.user
    pg_db = postgresql_proc.dbname

    janitor = DatabaseJanitor(
        user=pg_user,
        host=pg_host,
        port=pg_port,
        dbname=pg_db,
        template_dbname="template1",
        version=postgresql_proc.version,
    )
    
    # Ensure database exists
    with janitor:
        # Create database connection
        db_connection = psycopg.connect(
            dbname=pg_db,
            user=pg_user,
            host=pg_host,
            port=pg_port,
            connect_timeout=10,
        )
        try:
            yield db_connection
        finally:
            db_connection.close()


@pytest.fixture(scope="session") 
async def db_engine(postgresql_proc, postgresql_session):
    """
    Create a session-scoped database engine for testing.
    
    Uses pytest-postgresql to create an embedded PostgreSQL instance
    for testing, eliminating the need for external PostgreSQL setup.
    """
    # Get connection details from postgresql_proc
    pg_host = postgresql_proc.host
    pg_port = postgresql_proc.port
    pg_user = postgresql_proc.user
    pg_db = postgresql_proc.dbname
    
    # Build the database URL for async operation (no password needed)
    db_url = f"postgresql+asyncpg://{pg_user}@{pg_host}:{pg_port}/{pg_db}"
    
    # Create async engine with test-appropriate settings
    engine = create_async_engine(
        db_url,
        echo=False,  # Set to True for SQL query debugging
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )
    
    # Create all tables and ensure pgvector extension is available
    try:
        async with engine.begin() as conn:
            # Try to install pgvector extension (fail silently if not available)
            try:
                from sqlalchemy import text
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            except Exception:
                # pgvector may not be available in test environment
                # Roll back the transaction and continue
                await conn.rollback()
                pass
        
        # Create tables in a separate transaction
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    except Exception as e:
        # If anything fails, try without the vector extension
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
async def db_setup(db_engine):
    """
    Set up database schema once per test session.
    
    This fixture applies SQLAlchemy models to create the database schema.
    It runs once per test session to set up all tables and relationships.
    Uses pytest-postgresql for real database constraints and functionality.
    
    Args:
        db_engine: The database engine from db_engine fixture
        
    Returns:
        AsyncGenerator yielding after schema setup is complete
    """
    # Schema is already created in db_engine fixture for PostgreSQL
    yield


@pytest.fixture
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
    # Create a session maker
    session_maker = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Create a session for the test
    async with session_maker() as session:
        try:
            yield session
        finally:
            # Always rollback to ensure clean state
            await session.rollback()
            await session.close()


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
    # Register a test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com", 
        "password": "TestPassword123!",
        "full_name": "Test User",
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    auth_response = response.json()
    access_token = auth_response["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_user_data() -> dict:
    """Test user data for registration."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    }


@pytest.fixture
def test_login_data() -> dict:
    """Test login data."""
    return {
        "username": "testuser",
        "password": "TestPassword123!",
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    # These are already set at the top of the file, but keep for compatibility
    pass