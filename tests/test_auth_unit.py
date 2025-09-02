"""Unit tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.auth import AuthService
from chatter.models.user import User
from chatter.schemas.auth import UserCreate, UserLogin


class TestAuthUnitTests:
    """Unit tests for authentication functionality."""
    
    @pytest.mark.unit
    async def test_user_registration(self, client: AsyncClient, test_user_data: dict):
        """Test user registration endpoint."""
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["token_type"] == "bearer"
        
        # Verify user data
        user_data = data["user"]
        assert user_data["username"] == test_user_data["username"]
        assert user_data["email"] == test_user_data["email"]
        assert user_data["full_name"] == test_user_data["full_name"]
        assert "password" not in user_data  # Password should not be returned
        
    @pytest.mark.unit
    async def test_user_registration_duplicate_username(self, client: AsyncClient, test_user_data: dict):
        """Test that duplicate username registration fails."""
        # Register first user
        response1 = await client.post("/api/v1/auth/register", json=test_user_data)
        assert response1.status_code == 201
        
        # Try to register with same username
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        
        response2 = await client.post("/api/v1/auth/register", json=duplicate_data)
        assert response2.status_code == 409  # Conflict
        
    @pytest.mark.unit
    async def test_user_registration_duplicate_email(self, client: AsyncClient, test_user_data: dict):
        """Test that duplicate email registration fails."""
        # Register first user
        response1 = await client.post("/api/v1/auth/register", json=test_user_data)
        assert response1.status_code == 201
        
        # Try to register with same email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "differentuser"
        
        response2 = await client.post("/api/v1/auth/register", json=duplicate_data)
        assert response2.status_code == 409  # Conflict
        
    @pytest.mark.unit
    async def test_user_registration_invalid_data(self, client: AsyncClient):
        """Test user registration with invalid data."""
        invalid_data = {
            "username": "",  # Empty username
            "email": "invalid-email",  # Invalid email format
            "password": "123",  # Too short password
            "full_name": "",
        }
        
        response = await client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
    @pytest.mark.unit
    async def test_user_login_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful user login."""
        # First register a user
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Now login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["token_type"] == "bearer"
        
    @pytest.mark.unit
    async def test_user_login_with_email(self, client: AsyncClient, test_user_data: dict):
        """Test user login using email instead of username."""
        # First register a user
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login with email
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
    @pytest.mark.unit
    async def test_user_login_invalid_credentials(self, client: AsyncClient, test_user_data: dict):
        """Test login with invalid credentials."""
        # First register a user
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try login with wrong password
        login_data = {
            "username": test_user_data["username"],
            "password": "wrong_password",
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401  # Unauthorized
        
    @pytest.mark.unit
    async def test_user_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "password123",
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401  # Unauthorized
        
    @pytest.mark.unit
    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict):
        """Test getting current user information."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "full_name" in data
        assert "password" not in data  # Password should not be returned
        
    @pytest.mark.unit
    async def test_get_current_user_without_auth(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403  # Forbidden
        
    @pytest.mark.unit
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401  # Unauthorized
        
    @pytest.mark.unit
    async def test_token_refresh(self, client: AsyncClient, test_user_data: dict):
        """Test refreshing access token."""
        # Register and login to get tokens
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        login_data_response = login_response.json()
        
        # Use refresh token to get new access token
        refresh_data = {
            "refresh_token": login_data_response["refresh_token"]
        }
        
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        
    @pytest.mark.unit
    async def test_token_refresh_invalid_token(self, client: AsyncClient):
        """Test token refresh with invalid refresh token."""
        refresh_data = {
            "refresh_token": "invalid_refresh_token"
        }
        
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 401  # Unauthorized
        
    @pytest.mark.unit
    async def test_update_profile(self, client: AsyncClient, auth_headers: dict):
        """Test updating user profile."""
        update_data = {
            "full_name": "Updated Full Name",
            "email": "updated@example.com",
        }
        
        response = await client.put("/api/v1/auth/me", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["email"] == update_data["email"]
        
    @pytest.mark.unit
    async def test_update_profile_without_auth(self, client: AsyncClient):
        """Test updating profile without authentication."""
        update_data = {
            "full_name": "Updated Full Name",
        }
        
        response = await client.put("/api/v1/auth/me", json=update_data)
        assert response.status_code == 403  # Forbidden
        
    @pytest.mark.unit
    async def test_change_password(self, client: AsyncClient, auth_headers: dict, test_user_data: dict):
        """Test changing user password."""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewSecurePassword123!",
        }
        
        response = await client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "successfully" in data["message"].lower()
        
    @pytest.mark.unit
    async def test_change_password_wrong_current(self, client: AsyncClient, auth_headers: dict):
        """Test changing password with wrong current password."""
        password_data = {
            "current_password": "wrong_current_password",
            "new_password": "NewSecurePassword123!",
        }
        
        response = await client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        assert response.status_code == 401  # Unauthorized
        
    @pytest.mark.unit
    async def test_logout(self, client: AsyncClient, auth_headers: dict):
        """Test user logout."""
        response = await client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "successfully" in data["message"].lower()


class TestAuthServiceUnit:
    """Unit tests for AuthService class."""
    
    @pytest.mark.unit
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user through AuthService."""
        auth_service = AuthService(db_session)
        
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="SecurePassword123!",
            full_name="Test User",
        )
        
        user = await auth_service.create_user(user_data)
        
        assert user.username == user_data.username
        assert user.email == user_data.email
        assert user.full_name == user_data.full_name
        assert user.hashed_password is not None
        assert user.hashed_password != user_data.password  # Should be hashed
        
    @pytest.mark.unit
    async def test_authenticate_user(self, db_session: AsyncSession):
        """Test user authentication through AuthService."""
        auth_service = AuthService(db_session)
        
        # Create a user first
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="SecurePassword123!",
            full_name="Test User",
        )
        
        created_user = await auth_service.create_user(user_data)
        
        # Now authenticate
        authenticated_user = await auth_service.authenticate_user(
            "testuser", "SecurePassword123!"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.username == created_user.username
        
    @pytest.mark.unit
    async def test_authenticate_user_wrong_password(self, db_session: AsyncSession):
        """Test authentication with wrong password."""
        auth_service = AuthService(db_session)
        
        # Create a user first
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="SecurePassword123!",
            full_name="Test User",
        )
        
        await auth_service.create_user(user_data)
        
        # Try to authenticate with wrong password
        authenticated_user = await auth_service.authenticate_user(
            "testuser", "WrongPassword"
        )
        
        assert authenticated_user is None
        
    @pytest.mark.unit
    async def test_authenticate_user_nonexistent(self, db_session: AsyncSession):
        """Test authentication with non-existent user."""
        auth_service = AuthService(db_session)
        
        authenticated_user = await auth_service.authenticate_user(
            "nonexistent", "password"
        )
        
        assert authenticated_user is None
        
    @pytest.mark.unit
    def test_create_tokens(self, db_session: AsyncSession):
        """Test JWT token creation."""
        auth_service = AuthService(db_session)
        
        # Create a mock user object
        user = User(
            id="test_user_id",
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
        )
        
        tokens = auth_service.create_tokens(user)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"
        assert isinstance(tokens["access_token"], str)
        assert isinstance(tokens["refresh_token"], str)
        assert len(tokens["access_token"]) > 0
        assert len(tokens["refresh_token"]) > 0