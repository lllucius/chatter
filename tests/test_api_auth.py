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

    def test_register_user_success(self):
        """Test successful user registration."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
        }

        mock_user = User(
            id="test-user-id",
            email=user_data["email"],
            username=user_data["username"],
            is_active=True,
        )

        self.mock_auth_service.register_user.return_value = mock_user

        # Act
        response = self.client.post(
            "/api/v1/auth/register", json=user_data
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["email"] == user_data["email"]
        assert response_data["username"] == user_data["username"]
        assert "password" not in response_data

    def test_register_user_duplicate_email(self):
        """Test user registration with duplicate email."""
        # Arrange
        user_data = {
            "email": "existing@example.com",
            "username": "testuser",
            "password": "securepassword123",
        }

        from chatter.core.exceptions import ConflictError

        self.mock_auth_service.register_user.side_effect = (
            ConflictError("Email already exists")
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

        mock_token_response = {
            "access_token": "mock-access-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "mock-refresh-token",
        }

        self.mock_auth_service.authenticate_user.return_value = (
            mock_token_response
        )

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

        from chatter.core.exceptions import AuthenticationError

        self.mock_auth_service.authenticate_user.side_effect = (
            AuthenticationError("Invalid credentials")
        )

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
        }

        self.mock_auth_service.refresh_token.return_value = (
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
        self.mock_auth_service.logout_user.return_value = True

        # Mock get_current_user dependency
        mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
        )
        app.dependency_overrides[get_current_user] = lambda: mock_user

        # Act
        response = self.client.post(
            "/api/v1/auth/logout", headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["message"] == "Successfully logged out"

    def test_get_user_profile_success(self):
        """Test getting current user profile."""
        # Arrange
        headers = {"Authorization": "Bearer valid-token"}
        mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True,
        )
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

        mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
        )
        updated_user = User(
            id="test-user-id",
            email="new@example.com",
            username="newusername",
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

        mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
        )
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

        mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
        )
        app.dependency_overrides[get_current_user] = lambda: mock_user

        from chatter.core.exceptions import AuthenticationError

        self.mock_auth_service.change_password.side_effect = (
            AuthenticationError("Invalid current password")
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

        mock_user = User(
            id="integration-user-id",
            email=user_data["email"],
            username=user_data["username"],
            is_active=True,
        )

        mock_auth_service.register_user.return_value = mock_user

        # Test registration
        response = self.client.post(
            "/api/v1/auth/register", json=user_data
        )
        assert response.status_code == status.HTTP_201_CREATED

        # Mock login
        mock_token_response = {
            "access_token": "integration-access-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "integration-refresh-token",
        }

        mock_auth_service.authenticate_user.return_value = (
            mock_token_response
        )

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
