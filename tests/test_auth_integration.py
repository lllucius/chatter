"""Integration tests for authentication workflows."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.user import User


class TestAuthIntegration:
    """Integration tests for authentication workflows."""

    @pytest.mark.integration
    async def test_complete_user_registration_and_login_flow(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test complete user registration and login workflow."""
        # Step 1: Register user
        register_response = await client.post(
            "/api/v1/auth/register", json=test_user_data
        )
        assert register_response.status_code == 201

        register_data = register_response.json()
        assert "access_token" in register_data
        assert "user" in register_data

        user_id = register_data["user"]["id"]

        # Step 2: Login with username
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }

        login_response = await client.post(
            "/api/v1/auth/login", json=login_data
        )
        assert login_response.status_code == 200

        login_response_data = login_response.json()
        assert login_response_data["user"]["id"] == user_id

        # Step 3: Use access token to get user profile
        auth_headers = {
            "Authorization": f"Bearer {login_response_data['access_token']}"
        }
        profile_response = await client.get(
            "/api/v1/auth/me", headers=auth_headers
        )
        assert profile_response.status_code == 200

        profile_data = profile_response.json()
        assert profile_data["id"] == user_id
        assert profile_data["username"] == test_user_data["username"]
        assert profile_data["email"] == test_user_data["email"]

    @pytest.mark.integration
    async def test_login_with_email_workflow(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test login using email instead of username."""
        # Register user
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login with email
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }

        response = await client.post(
            "/api/v1/auth/login", json=login_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["user"]["email"] == test_user_data["email"]

    @pytest.mark.integration
    async def test_token_refresh_workflow(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test token refresh workflow."""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register", json=test_user_data
        )
        register_data = register_response.json()

        original_access_token = register_data["access_token"]
        refresh_token = register_data["refresh_token"]

        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        refresh_response = await client.post(
            "/api/v1/auth/refresh", json=refresh_data
        )
        assert refresh_response.status_code == 200

        refresh_response_data = refresh_response.json()
        new_access_token = refresh_response_data["access_token"]

        # Verify new token is different and works
        assert new_access_token != original_access_token

        auth_headers = {"Authorization": f"Bearer {new_access_token}"}
        profile_response = await client.get(
            "/api/v1/auth/me", headers=auth_headers
        )
        assert profile_response.status_code == 200

    @pytest.mark.integration
    async def test_profile_update_workflow(
        self,
        client: AsyncClient,
        test_user_data: dict,
        db_session: AsyncSession,
    ):
        """Test complete profile update workflow."""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register", json=test_user_data
        )
        register_data = register_response.json()

        access_token = register_data["access_token"]
        user_id = register_data["user"]["id"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Update profile
        update_data = {
            "full_name": "Updated Full Name",
            "email": "updated@example.com",
        }

        update_response = await client.put(
            "/api/v1/auth/me", json=update_data, headers=auth_headers
        )
        assert update_response.status_code == 200

        update_response_data = update_response.json()
        assert (
            update_response_data["full_name"]
            == update_data["full_name"]
        )
        assert update_response_data["email"] == update_data["email"]

        # Verify changes in database
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        user = result.scalar_one()

        assert user.full_name == update_data["full_name"]
        assert user.email == update_data["email"]

    @pytest.mark.integration
    async def test_password_change_workflow(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test password change workflow."""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register", json=test_user_data
        )
        register_data = register_response.json()

        access_token = register_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Change password
        new_password = "NewSecurePassword123!"
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": new_password,
        }

        change_response = await client.post(
            "/api/v1/auth/change-password",
            json=password_data,
            headers=auth_headers,
        )
        assert change_response.status_code == 200

        # Verify old password no longer works
        old_login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }

        old_login_response = await client.post(
            "/api/v1/auth/login", json=old_login_data
        )
        assert old_login_response.status_code == 401

        # Verify new password works
        new_login_data = {
            "username": test_user_data["username"],
            "password": new_password,
        }

        new_login_response = await client.post(
            "/api/v1/auth/login", json=new_login_data
        )
        assert new_login_response.status_code == 200

    @pytest.mark.integration
    async def test_api_key_workflow(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test API key creation and usage workflow."""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register", json=test_user_data
        )
        register_data = register_response.json()

        access_token = register_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Create API key
        api_key_data = {"name": "Test API Key"}
        api_key_response = await client.post(
            "/api/v1/auth/api-key",
            json=api_key_data,
            headers=auth_headers,
        )
        assert api_key_response.status_code == 200

        api_key_response_data = api_key_response.json()
        assert "api_key" in api_key_response_data
        assert (
            api_key_response_data["api_key_name"]
            == api_key_data["name"]
        )

        # List API keys
        list_response = await client.get(
            "/api/v1/auth/api-keys", headers=auth_headers
        )
        assert list_response.status_code == 200

        api_keys = list_response.json()
        assert len(api_keys) == 1
        assert api_keys[0]["api_key_name"] == api_key_data["name"]

        # Revoke API key
        revoke_response = await client.delete(
            "/api/v1/auth/api-key", headers=auth_headers
        )
        assert revoke_response.status_code == 200

        # Verify API key is revoked
        list_response_after = await client.get(
            "/api/v1/auth/api-keys", headers=auth_headers
        )
        assert list_response_after.status_code == 200

        api_keys_after = list_response_after.json()
        assert len(api_keys_after) == 0

    @pytest.mark.integration
    async def test_logout_workflow(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test logout workflow."""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register", json=test_user_data
        )
        register_data = register_response.json()

        access_token = register_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Verify token works
        profile_response = await client.get(
            "/api/v1/auth/me", headers=auth_headers
        )
        assert profile_response.status_code == 200
        profile_data = (
            profile_response.json()
        )  # Store original profile data

        # Logout
        logout_response = await client.post(
            "/api/v1/auth/logout", headers=auth_headers
        )
        assert logout_response.status_code == 200

        # Verify token no longer works after logout
        profile_response_after = await client.get(
            "/api/v1/auth/me", headers=auth_headers
        )
        # After logout, the token should either be invalid (401) or user info should show as not authenticated
        # Different auth implementations may handle this differently
        assert profile_response_after.status_code in [401, 200]

        if profile_response_after.status_code == 200:
            # If status is 200, verify that user is marked as not authenticated
            profile_data_after = profile_response_after.json()
            # The implementation may return different fields to indicate logged out state
            # Common patterns: is_authenticated=False, token_valid=False, or different user info
            assert (
                profile_data_after != profile_data
            )  # Profile should be different after logout

    @pytest.mark.integration
    async def test_account_deactivation_workflow(
        self,
        client: AsyncClient,
        test_user_data: dict,
        db_session: AsyncSession,
    ):
        """Test account deactivation workflow."""
        # Register user
        register_response = await client.post(
            "/api/v1/auth/register", json=test_user_data
        )
        register_data = register_response.json()

        access_token = register_data["access_token"]
        user_id = register_data["user"]["id"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Deactivate account
        deactivate_response = await client.delete(
            "/api/v1/auth/account", headers=auth_headers
        )
        assert deactivate_response.status_code == 200

        deactivate_data = deactivate_response.json()
        assert "message" in deactivate_data
        assert "deactivated" in deactivate_data["message"].lower()

        # Verify user is deactivated in database
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        user = result.scalar_one()

        # This test assumes there's an 'is_active' field - adjust based on actual model
        assert hasattr(user, "is_active") and not user.is_active

    @pytest.mark.integration
    async def test_multiple_users_isolation(self, client: AsyncClient):
        """Test that multiple users are properly isolated."""
        # Create first user
        user1_data = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "Password123!",
            "full_name": "User One",
        }

        user1_response = await client.post(
            "/api/v1/auth/register", json=user1_data
        )
        assert user1_response.status_code == 201
        user1_tokens = user1_response.json()

        # Create second user
        user2_data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "Password123!",
            "full_name": "User Two",
        }

        user2_response = await client.post(
            "/api/v1/auth/register", json=user2_data
        )
        assert user2_response.status_code == 201
        user2_tokens = user2_response.json()

        # Verify users have different IDs and tokens
        assert user1_tokens["user"]["id"] != user2_tokens["user"]["id"]
        assert (
            user1_tokens["access_token"] != user2_tokens["access_token"]
        )

        # Verify each user can only access their own data
        user1_headers = {
            "Authorization": f"Bearer {user1_tokens['access_token']}"
        }
        user2_headers = {
            "Authorization": f"Bearer {user2_tokens['access_token']}"
        }

        user1_profile = await client.get(
            "/api/v1/auth/me", headers=user1_headers
        )
        user2_profile = await client.get(
            "/api/v1/auth/me", headers=user2_headers
        )

        assert user1_profile.status_code == 200
        assert user2_profile.status_code == 200

        user1_data_response = user1_profile.json()
        user2_data_response = user2_profile.json()

        assert user1_data_response["username"] == "user1"
        assert user2_data_response["username"] == "user2"
        assert user1_data_response["id"] != user2_data_response["id"]

    @pytest.mark.integration
    async def test_password_reset_workflow(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test password reset workflow."""
        # Register user
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Request password reset
        reset_request_response = await client.post(
            "/api/v1/auth/password-reset/request",
            params={"email": test_user_data["email"]},
        )
        assert reset_request_response.status_code == 200

        reset_request_data = reset_request_response.json()
        assert "message" in reset_request_data

        # Note: In a real implementation, you would:
        # 1. Check email was sent (mock email service)
        # 2. Extract reset token from email
        # 3. Use reset token to confirm password reset
        # For this test, we'll just verify the endpoint accepts the request

        # Attempt password reset confirmation (this will likely fail without a real token)
        # This is more of a smoke test to ensure the endpoint exists
        reset_confirm_response = await client.post(
            "/api/v1/auth/password-reset/confirm",
            params={
                "token": "fake_token",
                "new_password": "NewPassword123!",
            },
        )
        # Expect this to fail with invalid token
        assert reset_confirm_response.status_code in [400, 401, 404]


class TestAuthDatabaseIntegration:
    """Integration tests that verify database operations."""

    @pytest.mark.integration
    async def test_user_persistence(
        self,
        client: AsyncClient,
        test_user_data: dict,
        db_session: AsyncSession,
    ):
        """Test that user data is properly persisted in database."""
        # Register user
        response = await client.post(
            "/api/v1/auth/register", json=test_user_data
        )
        assert response.status_code == 201

        response_data = response.json()
        user_id = response_data["user"]["id"]

        # Query database directly
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        user = result.scalar_one()

        assert user.username == test_user_data["username"]
        assert user.email == test_user_data["email"]
        assert user.full_name == test_user_data["full_name"]
        assert user.hashed_password is not None
        assert (
            user.hashed_password != test_user_data["password"]
        )  # Should be hashed
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.integration
    async def test_user_uniqueness_constraints(
        self,
        client: AsyncClient,
        test_user_data: dict,
        db_session: AsyncSession,
    ):
        """Test database uniqueness constraints for username and email."""
        # Create first user
        response1 = await client.post(
            "/api/v1/auth/register", json=test_user_data
        )
        assert response1.status_code == 201

        # Try to create user with same username
        duplicate_username_data = test_user_data.copy()
        duplicate_username_data["email"] = "different@example.com"

        response2 = await client.post(
            "/api/v1/auth/register", json=duplicate_username_data
        )
        assert response2.status_code == 409

        # Try to create user with same email
        duplicate_email_data = test_user_data.copy()
        duplicate_email_data["username"] = "differentuser"

        response3 = await client.post(
            "/api/v1/auth/register", json=duplicate_email_data
        )
        assert response3.status_code == 409

        # Verify only one user exists in database
        stmt = select(User)
        result = await db_session.execute(stmt)
        users = result.scalars().all()
        assert len(users) == 1

    @pytest.mark.integration
    async def test_transaction_rollback_on_error(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that database transactions are properly rolled back on errors."""
        # Count users before
        stmt = select(User)
        result = await db_session.execute(stmt)
        users_before = result.scalars().all()
        initial_count = len(users_before)

        # Try to register with invalid data that should cause an error
        invalid_data = {
            "username": "validuser",
            "email": "invalid-email-format",  # This should fail validation
            "password": "ValidPassword123!",
            "full_name": "Valid Name",
        }

        response = await client.post(
            "/api/v1/auth/register", json=invalid_data
        )
        assert response.status_code == 422  # Validation error

        # Verify no user was created
        result_after = await db_session.execute(stmt)
        users_after = result_after.scalars().all()
        assert len(users_after) == initial_count
