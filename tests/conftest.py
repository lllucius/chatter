"""Test configuration and shared fixtures."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from sqlalchemy import text
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


@pytest.fixture(scope="session")
async def db_engine():
    """
    Create a session-scoped database engine for testing.
    
    The hanging issue has been resolved by using lazy imports in the fixtures.
    Using SQLite for simplicity in tests, but the approach works for PostgreSQL too.
    """
    # Use SQLite in-memory database for testing
    db_url = "sqlite+aiosqlite:///:memory:"
    
    # Create async engine with test-appropriate settings
    engine = create_async_engine(
        db_url,
        echo=False,  # Set to True for SQL query debugging
    )
    
    # Create all tables, but skip PostgreSQL-specific constraints for SQLite
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
    
    Args:
        db_engine: The database engine from db_engine fixture
        
    Returns:
        AsyncGenerator yielding after schema setup is complete
    """
    # Schema is already created in db_engine fixture for SQLite
    yield


@pytest.fixture
async def db_session(db_engine, db_setup) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session with clean state per test.
    
    For in-memory SQLite, we simply create a fresh session for each test.
    Foreign key constraints are disabled for SQLite to avoid circular dependency issues.
    
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
    
    async with session_maker() as session:
        # For SQLite, disable foreign key constraints to avoid circular dependency issues
        if "sqlite" in str(db_engine.url):
            await session.execute(text("PRAGMA foreign_keys=OFF"))
            await session.commit()
        
        try:
            yield session
        finally:
            # Clean up: delete all data from all tables to ensure test isolation
            if "sqlite" in str(db_engine.url):
                # Get all table names and clear them
                for table in reversed(Base.metadata.sorted_tables):
                    await session.execute(text(f"DELETE FROM {table.name}"))
                await session.commit()
            
            # Close the session to clean up
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
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing")
    os.environ.setdefault("ENVIRONMENT", "testing")