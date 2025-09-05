"""Simplified authentication test that bypasses FastAPI HTTP client."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.auth import AuthService
from chatter.models.user import User
from chatter.schemas.auth import UserCreate


class TestAuthServiceDirect:
    """Direct tests of auth service without FastAPI HTTP client."""

    @pytest.mark.asyncio
    async def test_auth_service_create_user(self, db_session: AsyncSession):
        """Test user creation directly through AuthService."""
        auth_service = AuthService(db_session)
        
        # Use unique identifiers to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        user_data = UserCreate(
            username=f"testuser_direct_{unique_id}",
            email=f"test_direct_{unique_id}@example.com",
            password="SecureP@ssw0rd!",
            full_name="Test User Direct"
        )
        
        # Create user
        result = await auth_service.create_user(user_data)
        
        # Verify user was created
        assert result.username == user_data.username
        assert result.email == user_data.email
        assert result.full_name == user_data.full_name
        assert result.hashed_password is not None
        assert result.hashed_password != user_data.password  # Should be hashed
        
        # Verify user exists in database
        user_in_db = await auth_service.get_user_by_email(user_data.email)
        assert user_in_db is not None
        assert user_in_db.id == result.id

    @pytest.mark.asyncio
    async def test_auth_service_authenticate(self, db_session: AsyncSession):
        """Test user authentication directly through AuthService."""
        auth_service = AuthService(db_session)
        
        # First create a user with unique identifiers
        unique_id = str(uuid.uuid4())[:8]
        user_data = UserCreate(
            username=f"testuser_auth_{unique_id}",
            email=f"test_auth_{unique_id}@example.com", 
            password="SecureP@ssw0rd!",
            full_name="Test User Auth"
        )
        
        created_user = await auth_service.create_user(user_data)
        
        # Test authentication with correct credentials
        authenticated_user = await auth_service.authenticate_user(
            user_data.username, user_data.password
        )
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        
        # Test authentication with wrong password
        wrong_auth = await auth_service.authenticate_user(
            user_data.username, "wrong_password"
        )
        assert wrong_auth is None