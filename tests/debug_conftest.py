"""Step by step conftest debugging."""

import asyncio
import os
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from chatter.utils.database import Base


# Test 1: Simple fixture
@pytest.fixture
def simple_test_fixture():
    return "simple_value"


# Test 2: Async fixture
@pytest.fixture
async def simple_async_fixture():
    return "async_value"


# Test 3: Session-scoped async fixture
@pytest.fixture(scope="session")
async def session_async_fixture():
    return "session_async_value"


# Test 4: Database engine fixture  
@pytest.fixture(scope="session")
async def test_db_engine():
    """Simple database engine fixture using PostgreSQL."""
    # Lazy import to avoid hanging during test collection
    from chatter.config import settings
    
    # Use PostgreSQL test database
    db_url = settings.database_url_for_env
    
    engine = create_async_engine(
        db_url, 
        echo=False,
        pool_size=5,
        max_overflow=10,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        yield engine
    finally:
        await engine.dispose()


# Test 5: Database session fixture
@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Simple database session fixture."""
    session_maker = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with session_maker() as session:
        await session.begin()
        try:
            yield session
        finally:
            await session.rollback()


def test_simple(simple_test_fixture):
    """Test simple fixture."""
    assert simple_test_fixture == "simple_value"


async def test_simple_async(simple_async_fixture):
    """Test async fixture."""
    assert simple_async_fixture == "async_value"


async def test_session_async(session_async_fixture):
    """Test session async fixture."""
    assert session_async_fixture == "session_async_value"


async def test_db_engine(test_db_engine):
    """Test database engine fixture."""
    assert test_db_engine is not None


async def test_db_session(test_db_session):
    """Test database session fixture."""
    from sqlalchemy import text
    result = await test_db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1