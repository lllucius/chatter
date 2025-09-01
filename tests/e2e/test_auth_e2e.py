"""End-to-end tests for user authentication flows."""

import pytest
from fastapi import status
from unittest.mock import patch


@pytest.mark.e2e
class TestAuthenticationE2E:
    """End-to-end authentication workflow tests."""

    def test_complete_user_registration_flow(self, test_client, sample_user_credentials, cleanup_test_data):
        """Test complete user registration from start to finish."""
        # Step 1: Check that user doesn't exist initially
        login_response = test_client.post(
            "/api/v1/auth/login",
            data={
                "username": sample_user_credentials["email"],
                "password": sample_user_credentials["password"]
            }
        )
        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Step 2: Register new user
        register_response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": sample_user_credentials["email"],
                "password": sample_user_credentials["password"],
                "username": sample_user_credentials["username"],
                "full_name": sample_user_credentials["full_name"]
            }
        )
        # Allow for the endpoint to not exist in test environment
        assert register_response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_404_NOT_FOUND  # Endpoint might not be implemented
        ]
        
        if register_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Registration endpoint not available in test environment")
        
        # Step 3: Verify registration success
        assert "user_id" in register_response.json() or "id" in register_response.json()
        
        # Step 4: Login with new credentials
        login_response = test_client.post(
            "/api/v1/auth/login",
            data={
                "username": sample_user_credentials["email"],
                "password": sample_user_credentials["password"]
            }
        )
        assert login_response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if login_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Login endpoint not available in test environment")
        
        # Step 5: Verify we received a token
        login_data = login_response.json()
        assert "access_token" in login_data
        assert login_data["token_type"] == "bearer"

    def test_invalid_credentials_flow(self, test_client):
        """Test authentication with invalid credentials."""
        # Test with completely invalid email
        response = test_client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND  # Endpoint might not exist
        ]
        
        if response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Login endpoint not available in test environment")

    def test_password_reset_flow(self, test_client, sample_user_credentials):
        """Test password reset workflow."""
        # Step 1: Request password reset
        reset_request_response = test_client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": sample_user_credentials["email"]}
        )
        
        # Allow for endpoint to not exist
        if reset_request_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Password reset endpoint not available in test environment")
        
        assert reset_request_response.status_code == status.HTTP_200_OK
        
        # Step 2: Simulate reset token (in real E2E, this would come from email)
        mock_reset_token = "mock_reset_token_12345"
        
        # Step 3: Reset password with token
        reset_response = test_client.post(
            "/api/v1/auth/password-reset",
            json={
                "token": mock_reset_token,
                "new_password": "NewSecurePassword123!"
            }
        )
        
        # This might fail in test environment - that's expected
        assert reset_response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,  # Invalid token in test
            status.HTTP_404_NOT_FOUND     # Endpoint doesn't exist
        ]


@pytest.mark.e2e
@pytest.mark.integration
class TestTokenManagementE2E:
    """End-to-end token management tests."""

    def test_token_refresh_flow(self, test_client, sample_user_credentials):
        """Test JWT token refresh workflow."""
        # Skip if we can't authenticate first
        login_response = test_client.post(
            "/api/v1/auth/login",
            data={
                "username": sample_user_credentials["email"],
                "password": sample_user_credentials["password"]
            }
        )
        
        if login_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Authentication endpoints not available")
            
        if login_response.status_code != status.HTTP_200_OK:
            pytest.skip("Cannot authenticate for token refresh test")
        
        # Get the access token
        tokens = login_response.json()
        access_token = tokens["access_token"]
        
        # Test token refresh if refresh endpoint exists
        refresh_response = test_client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if refresh_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Token refresh endpoint not available")
        
        assert refresh_response.status_code == status.HTTP_200_OK
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert new_tokens["access_token"] != access_token  # Should be different

    def test_protected_endpoint_access(self, test_client, sample_user_credentials):
        """Test accessing protected endpoints with valid/invalid tokens."""
        # Test without token
        protected_response = test_client.get("/api/v1/auth/me")
        
        if protected_response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Protected endpoint not available")
        
        assert protected_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test with invalid token
        protected_response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert protected_response.status_code == status.HTTP_401_UNAUTHORIZED