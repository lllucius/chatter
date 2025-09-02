"""Test configuration and shared fixtures."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pytest_postgresql import factories
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from chatter.config import settings
from chatter.main import create_app
from chatter.utils.database import Base, get_session_generator


# =============================================================================
# EVENT LOOP FIXTURE - Temporarily disabled to troubleshoot hanging
# =============================================================================

# @pytest.fixture(scope="session")
# def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
#     """
#     Create a session-scoped event loop for async tests.
#     
#     This fixture provides a single event loop that persists across the entire
#     test session, allowing for session-scoped async fixtures and better
#     performance by avoiding event loop creation/teardown overhead.
#     
#     Returns:
#         Generator yielding the event loop for the session
#     """
#     # Check if there's already an event loop running
#     try:
#         loop = asyncio.get_running_loop()
#         # If we're already in an event loop, just use it
#         yield loop
#     except RuntimeError:
#         # No event loop running, create a new one
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         try:
#             yield loop
#         finally:
#             # Only close the loop if we created it
#             try:
#                 # Make sure all tasks are complete before closing
#                 pending = asyncio.all_tasks(loop)
#                 if pending:
#                     loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
#             except Exception:
#                 pass
#             
#             # Close the loop safely
#             if not loop.is_closed():
#                 loop.close()


# =============================================================================
# POSTGRESQL FIXTURES - Temporarily disabled to troubleshoot hanging
# =============================================================================

# Create a PostgreSQL test database factory
# postgresql_proc = factories.postgresql_proc(
#     port=None,  # Use any available port
#     unixsocketdir="/tmp",  # Use tmp directory for socket
# )

# Create session-scoped postgresql fixture to match db_engine scope
def postgresql_session_factory(process_fixture_name: str):
    """
    Create a session-scoped postgresql fixture factory.
    
    This is needed because the default postgresql fixture from pytest-postgresql
    is function-scoped, but our db_engine fixture needs to be session-scoped
    to avoid creating multiple database engines per test session.
    
    Args:
        process_fixture_name: Name of the postgresql_proc fixture
        
    Returns:
        Session-scoped postgresql fixture function
    """
    
    @pytest.fixture(scope="session")
    def postgresql_session_fixture(request):
        """Session-scoped PostgreSQL database connection."""
        from pytest_postgresql.janitor import DatabaseJanitor
        import psycopg
        from pytest_postgresql.config import get_config
        
        proc_fixture = request.getfixturevalue(process_fixture_name)
        config = get_config(request)

        pg_host = proc_fixture.host
        pg_port = proc_fixture.port
        pg_user = proc_fixture.user
        pg_password = proc_fixture.password
        pg_options = proc_fixture.options
        pg_db = proc_fixture.dbname
        
        janitor = DatabaseJanitor(
            user=pg_user,
            host=pg_host,
            port=pg_port,
            dbname=pg_db,
            template_dbname=proc_fixture.template_dbname,
            version=proc_fixture.version,
            password=pg_password,
        )
        if config["drop_test_database"]:
            janitor.drop()
        with janitor:
            # Add timeout to connection to prevent hanging
            try:
                db_connection = psycopg.connect(
                    dbname=pg_db,
                    user=pg_user,
                    password=pg_password,
                    host=pg_host,
                    port=pg_port,
                    options=pg_options,
                    connect_timeout=10,  # Add 10 second timeout
                )
                try:
                    yield db_connection
                finally:
                    db_connection.close()
            except Exception as e:
                # Log connection errors for debugging
                print(f"PostgreSQL connection error: {e}")
                raise
    
    return postgresql_session_fixture

# Create the session-scoped postgresql fixture - Disabled
# postgresql = postgresql_session_factory("postgresql_proc")


@pytest.fixture(scope="session")
async def db_engine():
    """
    Create a session-scoped SQLite database engine for testing.
    
    Temporarily using SQLite instead of PostgreSQL to avoid hanging issues.
    """
    # Use SQLite in-memory database for testing
    db_url = "sqlite+aiosqlite:///:memory:"
    
    # Create async engine with test-appropriate settings
    engine = create_async_engine(
        db_url,
        echo=False,  # Set to True for SQL query debugging
    )
    
    # Create all tables
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
    You could alternatively use Alembic migrations here by running:
    `alembic upgrade head` against the test database.
    
    Args:
        db_engine: The database engine from db_engine fixture
        
    Returns:
        AsyncGenerator yielding after schema setup is complete
    """
    async with db_engine.begin() as conn:
        # Create all tables from SQLAlchemy models
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Clean up: drop all tables after tests complete
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(db_engine, db_setup) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session with transaction rollback per test.
    
    This fixture creates a new database session for each test and ensures
    that all changes are rolled back after the test completes. This provides
    test isolation - each test starts with a clean database state.
    
    The fixture uses a nested transaction pattern:
    1. Begin a transaction
    2. Create a session within that transaction
    3. Run the test
    4. Rollback the transaction (undoing all test changes)
    
    Args:
        db_engine: The database engine
        db_setup: Ensures database schema is set up
        
    Returns:
        AsyncGenerator yielding a database session
    """
    # Start a database transaction
    async with db_engine.begin() as connection:
        # Create a session bound to this connection
        session_maker = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        async with session_maker() as session:
            # Begin a nested transaction (savepoint)
            await session.begin()
            
            try:
                yield session
            finally:
                # Always rollback the nested transaction
                # This undoes all changes made during the test
                await session.rollback()


# =============================================================================
# FASTAPI APPLICATION FIXTURES
# =============================================================================

@pytest.fixture
def app(db_session: AsyncSession) -> FastAPI:
    """
    Create a FastAPI application with test database session override.
    
    This fixture creates the FastAPI application and overrides the
    get_session_generator dependency to use the test database session
    instead of the production database. This ensures that all API
    endpoints use the test database with proper transaction isolation.
    
    Args:
        db_session: The test database session
        
    Returns:
        FastAPI application configured for testing
    """
    # Create the FastAPI application
    app = create_app()
    
    # Override the database session dependency
    async def get_test_session():
        """Override database session for testing."""
        yield db_session
    
    # Replace the production dependency with our test version
    app.dependency_overrides[get_session_generator] = get_test_session
    
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing FastAPI routes.
    
    This fixture provides an httpx AsyncClient configured to make requests
    to the FastAPI application. It's the primary tool for testing API
    endpoints - you can use it to make GET, POST, PUT, DELETE requests
    and verify responses.
    
    Usage in tests:
        async def test_endpoint(client):
            response = await client.get("/api/v1/some-endpoint")
            assert response.status_code == 200
    
    Args:
        app: The FastAPI application
        
    Returns:
        AsyncGenerator yielding an HTTP client
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        follow_redirects=True,
    ) as client:
        yield client


# =============================================================================
# AUTHENTICATION FIXTURES
# =============================================================================

@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """
    Create authentication headers for testing protected endpoints.
    
    This fixture registers a test user and provides the authorization
    headers needed to access protected endpoints. It's a convenience
    fixture for tests that need to simulate authenticated requests.
    
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


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================

@pytest.fixture
def test_user_data() -> dict:
    """
    Provide test user data for registration/authentication tests.
    
    This fixture provides a consistent set of user data that can be
    used across multiple tests. It includes valid data that should
    pass validation requirements.
    
    Returns:
        Dictionary with test user data
    """
    return {
        "username": "testuser123",
        "email": "testuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User Full Name",
    }


@pytest.fixture
def test_login_data() -> dict:
    """
    Provide test login data for authentication tests.
    
    Returns:
        Dictionary with test login credentials
    """
    return {
        "username": "testuser123",
        "password": "SecurePassword123!",
    }


# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Set up test environment variables and configuration.
    
    This fixture runs automatically for every test (autouse=True) and
    ensures that the application is configured for testing. It sets
    environment variables that affect application behavior.
    """
    # Set test environment
    os.environ["TESTING"] = "true"
    
    # Override settings for testing if needed
    original_database_url = getattr(settings, "database_url", None)
    
    yield
    
    # Restore original settings
    if original_database_url:
        settings.database_url = original_database_url