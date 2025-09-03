#!/usr/bin/env python3
"""
Script to verify PostgreSQL test database setup.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test_user:test_password@localhost:5432/chatter_test")


async def verify_postgresql_setup():
    """Verify PostgreSQL test database setup."""
    print("🔍 Verifying PostgreSQL test database setup...")

    try:
        from chatter.config import settings
        print("✅ Configuration loaded")
        print(f"   Environment: {settings.environment}")
        print(f"   Test DB URL: {settings.test_database_url}")
        print(f"   DB URL for env: {settings.database_url_for_env}")

        # Test basic connection
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine(
            settings.database_url_for_env,
            echo=False,
            pool_size=5,
            max_overflow=10,
        )

        print("🔌 Testing database connection...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print("✅ PostgreSQL connection successful")
            print(f"   Version: {version}")

            # Test pgvector extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await conn.execute(text("SELECT vector_extension_version()"))
                print("✅ pgvector extension available")
            except Exception as e:
                print(f"⚠️  pgvector extension not available: {e}")
                print("   This is optional but recommended for vector store tests")

            # Test table creation
            from chatter.utils.database import Base
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database schema creation successful")

            # Test basic query
            result = await conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.scalar()
            print(f"✅ Created {table_count} tables in public schema")

        await engine.dispose()
        print("✅ Database verification completed successfully!")
        print("")
        print("🧪 You can now run tests with:")
        print("   pytest tests/ -v")

    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        print("")
        print("🔧 Troubleshooting:")
        print("1. Ensure PostgreSQL is running:")
        print("   sudo systemctl status postgresql")
        print("")
        print("2. Create test database and user:")
        print("   sudo -u postgres psql")
        print("   CREATE USER test_user WITH PASSWORD 'test_password';")
        print("   CREATE DATABASE chatter_test OWNER test_user;")
        print("   GRANT ALL PRIVILEGES ON DATABASE chatter_test TO test_user;")
        print("")
        print("3. Test connection manually:")
        print("   psql postgresql://test_user:test_password@localhost:5432/chatter_test")

        return False

    return True


def main():
    """Main function."""
    success = asyncio.run(verify_postgresql_setup())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
