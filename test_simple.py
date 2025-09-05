#!/usr/bin/env python3
"""Simple test to verify basic functionality without complex fixtures."""

import asyncio
import os

# Set up test environment
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test_user:test_password@localhost:5432/chatter_test")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing")
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("REDIS_ENABLED", "false")
os.environ.setdefault("CACHE_BACKEND", "memory")

async def test_basic_database():
    """Test basic database connection."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    engine = create_async_engine(
        "postgresql+asyncpg://test_user:test_password@localhost:5432/chatter_test",
        echo=False,
    )
    
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        value = result.scalar()
        print(f"Database test: {value}")
    
    await engine.dispose()
    return value == 1

async def test_user_model():
    """Test user model creation."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from chatter.models.user import User
    from chatter.core.auth import hash_password
    
    engine = create_async_engine(
        "postgresql+asyncpg://test_user:test_password@localhost:5432/chatter_test",
        echo=False,
    )
    
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with session_maker() as session:
        # Create a test user
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password=hash_password("password123"),
        )
        session.add(user)
        await session.commit()
        print(f"Created user: {user.username}")
    
    await engine.dispose()
    return True

async def main():
    """Run simple tests."""
    print("Testing basic database connection...")
    db_result = await test_basic_database()
    print(f"Database test: {'PASS' if db_result else 'FAIL'}")
    
    print("Testing user model...")
    user_result = await test_user_model()
    print(f"User model test: {'PASS' if user_result else 'FAIL'}")

if __name__ == "__main__":
    asyncio.run(main())