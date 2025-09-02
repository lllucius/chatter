"""Tests for authentication API endpoints."""

from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_auth_service, get_current_user
from chatter.core.auth import AuthService
from chatter.main import app
from chatter.models.user import User


@pytest.mark.unit
class TestAuthEndpoints:
    """Test authentication endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_auth_service = AsyncMock(spec=AuthService)
        self.mock_session = AsyncMock(spec=AsyncSession)

        # Override dependencies
        app.dependency_overrides[get_auth_service] = (
            lambda: self.mock_auth_service
        )

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def _create_mock_user(self, **kwargs):
        """Helper to create a mock user with required fields."""
        from datetime import datetime
        
        defaults = {
            "id": "test-user-id",
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password",
            "is_active": True,
            "is_verified": False,
            "is_superuser": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        defaults.update(kwargs)
        return User(**defaults)

    def test_register_user_success(self):
        """Test successful user registration."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
        }

        mock_user = self._create_mock_user(
            email=user_data["email"],
            username=user_data["username"]
        )

        self.mock_auth_service.create_user.return_value = mock_user
        self.mock_auth_service.create_tokens.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600
        }

        # Act
        response = self.client.post(
            "/api/v1/auth/register", json=user_data
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["user"]["email"] == user_data["email"]
        assert response_data["user"]["username"] == user_data["username"]
        assert "password" not in response_data["user"]
        assert response_data["access_token"] == "test_access_token"
        assert response_data["token_type"] == "bearer"

    def test_register_user_duplicate_email(self):
        """Test user registration with duplicate email."""
        # Arrange
        user_data = {
            "email": "existing@example.com",
            "username": "testuser",
            "password": "securepassword123",
        }

        from chatter.core.auth import UserAlreadyExistsError

        self.mock_auth_service.create_user.side_effect = (
            UserAlreadyExistsError("Email already exists")
        )

        # Act
        response = self.client.post(
            "/api/v1/auth/register", json=user_data
        )

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_register_user_invalid_data(self):
        """Test user registration with invalid data."""
        # Arrange
        invalid_data = {
            "email": "not-an-email",
            "username": "",
            "password": "short",
        }

        # Act
        response = self.client.post(
            "/api/v1/auth/register", json=invalid_data
        )

        # Assert
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    def test_login_success(self):
        """Test successful user login."""
        # Arrange
        login_data = {
            "email": "test@example.com",
            "password": "securepassword123",
        }

        mock_user = self._create_mock_user()
        
        mock_token_response = {
            "access_token": "mock-access-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "mock-refresh-token",
        }

        self.mock_auth_service.authenticate_user.return_value = mock_user
        self.mock_auth_service.create_tokens.return_value = mock_token_response

        # Act
        response = self.client.post(
            "/api/v1/auth/login", json=login_data
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["access_token"] == "mock-access-token"
        assert response_data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Arrange
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword",
        }

        self.mock_auth_service.authenticate_user.return_value = None

        # Act
        response = self.client.post(
            "/api/v1/auth/login", json=login_data
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_success(self):
        """Test successful token refresh."""
        # Arrange
        refresh_data = {"refresh_token": "valid-refresh-token"}

        mock_token_response = {
            "access_token": "new-access-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "new-refresh-token",
        }

        self.mock_auth_service.refresh_access_token.return_value = (
            mock_token_response
        )

        # Act
        response = self.client.post(
            "/api/v1/auth/refresh", json=refresh_data
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["access_token"] == "new-access-token"

    def test_logout_success(self):
        """Test successful logout."""
        # Arrange
        headers = {"Authorization": "Bearer valid-token"}
        self.mock_auth_service.revoke_token.return_value = True

        # Mock get_current_user dependency
        mock_user = self._create_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        # Act
        response = self.client.post(
            "/api/v1/auth/logout", headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["message"] == "Logged out successfully"

    def test_get_user_profile_success(self):
        """Test getting current user profile."""
        # Arrange
        headers = {"Authorization": "Bearer valid-token"}
        mock_user = self._create_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        # Act
        response = self.client.get("/api/v1/auth/me", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["email"] == "test@example.com"
        assert response_data["username"] == "testuser"

    def test_update_user_profile_success(self):
        """Test updating user profile."""
        # Arrange
        headers = {"Authorization": "Bearer valid-token"}
        update_data = {
            "username": "newusername",
            "email": "new@example.com",
        }

        mock_user = self._create_mock_user()
        updated_user = self._create_mock_user(
            email="new@example.com",
            username="newusername"
        )

        app.dependency_overrides[get_current_user] = lambda: mock_user
        self.mock_auth_service.update_user.return_value = updated_user

        # Act
        response = self.client.put(
            "/api/v1/auth/me", json=update_data, headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["email"] == "new@example.com"
        assert response_data["username"] == "newusername"

    def test_change_password_success(self):
        """Test successful password change."""
        # Arrange
        headers = {"Authorization": "Bearer valid-token"}
        password_data = {
            "current_password": "oldpassword",
            "new_password": "newpassword123",
        }

        mock_user = self._create_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user
        self.mock_auth_service.change_password.return_value = True

        # Act
        response = self.client.post(
            "/api/v1/auth/change-password",
            json=password_data,
            headers=headers,
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert (
            response_data["message"] == "Password changed successfully"
        )

    def test_change_password_invalid_current(self):
        """Test password change with invalid current password."""
        # Arrange
        headers = {"Authorization": "Bearer valid-token"}
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
        }

        mock_user = self._create_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        from chatter.utils.problem import AuthenticationProblem

        self.mock_auth_service.change_password.side_effect = (
            AuthenticationProblem("Invalid current password")
        )

        # Act
        response = self.client.post(
            "/api/v1/auth/change-password",
            json=password_data,
            headers=headers,
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestAuthIntegration:
    """Integration tests for authentication flow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def _create_mock_user(self, **kwargs):
        """Helper to create a mock user with required fields."""
        from datetime import datetime
        
        defaults = {
            "id": "test-user-id",
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password",
            "is_active": True,
            "is_verified": False,
            "is_superuser": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        defaults.update(kwargs)
        return User(**defaults)

    def test_full_auth_flow(self):
        """Test complete authentication flow."""
        # This would require a test database setup
        # For now, we'll mock the dependencies

        # Setup mocks
        mock_auth_service = AsyncMock(spec=AuthService)
        app.dependency_overrides[get_auth_service] = (
            lambda: mock_auth_service
        )

        # Mock registration
        user_data = {
            "email": "integration@example.com",
            "username": "integrationuser",
            "password": "securepassword123",
        }

        mock_user = self._create_mock_user(
            id="integration-user-id",
            email=user_data["email"],
            username=user_data["username"]
        )

        mock_auth_service.create_user.return_value = mock_user
        mock_auth_service.create_tokens.return_value = {
            "access_token": "integration-access-token",
            "token_type": "bearer", 
            "expires_in": 3600,
            "refresh_token": "integration-refresh-token",
        }

        # Test registration
        response = self.client.post(
            "/api/v1/auth/register", json=user_data
        )
        assert response.status_code == status.HTTP_201_CREATED

        # Mock login - same user and tokens for login
        mock_auth_service.authenticate_user.return_value = mock_user

        # Test login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"],
        }

        response = self.client.post(
            "/api/v1/auth/login", json=login_data
        )
        assert response.status_code == status.HTTP_200_OK

        token_data = response.json()
        assert "access_token" in token_data

        # Test authenticated request
        headers = {
            "Authorization": f"Bearer {token_data['access_token']}"
        }
        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = self.client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        app.dependency_overrides.clear()
