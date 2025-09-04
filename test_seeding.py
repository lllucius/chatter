"""Test the database seeding system."""

import asyncio
from sqlalchemy import text

from chatter.utils.database import DatabaseManager, init_database
from chatter.utils.seeding import DatabaseSeeder, SeedingMode, seed_database
from chatter.models.user import User
from chatter.models.conversation import Conversation
from chatter.models.document import Document
from chatter.models.profile import Profile
from chatter.models.prompt import Prompt
from chatter.models.registry import Provider, ModelDef, EmbeddingSpace


async def test_minimal_seeding():
    """Test minimal seeding mode."""
    # Initialize database
    await init_database()
    
    # Clear any existing data
    async with DatabaseManager() as session:
        await session.execute(text("DELETE FROM users"))
        await session.commit()
    
    # Test seeding
    results = await seed_database(mode=SeedingMode.MINIMAL, force=True)
    
    # Verify results
    assert results["mode"] == SeedingMode.MINIMAL
    assert results["created"]["users"] == 1
    assert results["created"]["providers"] == 1
    assert results["created"]["models"] == 2
    assert results["created"]["profiles"] >= 1
    assert results["created"]["prompts"] >= 1
    
    # Verify data in database
    async with DatabaseManager() as session:
        # Check admin user exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        admin_user = result.scalar_one_or_none()
        assert admin_user is not None
        assert admin_user.is_superuser is True
        
        # Check provider exists
        result = await session.execute(select(Provider).where(Provider.name == "openai"))
        provider = result.scalar_one_or_none()
        assert provider is not None


async def test_development_seeding():
    """Test development seeding mode."""
    # Initialize database
    await init_database()
    
    # Clear any existing data
    async with DatabaseManager() as session:
        await session.execute(text("DELETE FROM users"))
        await session.commit()
    
    # Test seeding
    results = await seed_database(mode=SeedingMode.DEVELOPMENT, force=True)
    
    # Verify results
    assert results["mode"] == SeedingMode.DEVELOPMENT
    assert results["created"]["users"] >= 3  # admin + development users
    assert "conversations" in results["created"]
    assert "documents" in results["created"]


async def test_seeder_context_manager():
    """Test DatabaseSeeder as context manager."""
    await init_database()
    
    async with DatabaseSeeder() as seeder:
        # Test that we can use the seeder
        count = await seeder._count_users()
        assert isinstance(count, int)


async def test_skip_existing():
    """Test skip_existing functionality."""
    await init_database()
    
    # First seeding
    results1 = await seed_database(mode=SeedingMode.MINIMAL, force=True)
    user_count1 = results1["created"]["users"]
    
    # Second seeding with skip_existing=True (default)
    results2 = await seed_database(mode=SeedingMode.MINIMAL, force=True, skip_existing=True)
    
    # Should not create duplicate users
    assert results2["created"]["users"] == 0  # Admin already exists


if __name__ == "__main__":
    # Run a simple test
    async def main():
        print("Testing minimal seeding...")
        await test_minimal_seeding()
        print("✅ Minimal seeding test passed")
        
        print("Testing development seeding...")
        await test_development_seeding()
        print("✅ Development seeding test passed")
        
        print("All tests passed!")
    
    asyncio.run(main())