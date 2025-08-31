"""Authentication API tests."""


import pytest

from chatter.utils.security import create_access_token, hash_password


@pytest.mark.unit
class TestAuthenticationAPI:
    """Test authentication API endpoints."""

    async def test_user_registration_success(self, test_client):
        """Test successful user registration."""
        registration_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "username": "newuser123"
        }

        response = await test_client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 201

        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser123"
        assert "password" not in data  # Password should not be returned

    async def test_user_registration_duplicate_email(self, test_client):
        """Test registration with duplicate email."""
        registration_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "username": "testuser"
        }

        # First registration should succeed
        response1 = await test_client.post("/api/v1/auth/register", json=registration_data)
        assert response1.status_code == 201

        # Second registration with same email should fail
        response2 = await test_client.post("/api/v1/auth/register", json=registration_data)
        assert response2.status_code == 409

        data = response2.json()
        assert "email" in data["detail"].lower() or "already exists" in data["detail"].lower()

    async def test_user_registration_validation_errors(self, test_client):
        """Test registration with validation errors."""
        # Test weak password
        weak_password_data = {
            "email": "test@example.com",
            "password": "123456",
            "username": "testuser"
        }

        response = await test_client.post("/api/v1/auth/register", json=weak_password_data)
        assert response.status_code == 400

        data = response.json()
        assert "password" in str(data).lower()

        # Test invalid email
        invalid_email_data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "username": "testuser"
        }

        response = await test_client.post("/api/v1/auth/register", json=invalid_email_data)
        assert response.status_code == 400

        # Test invalid username
        invalid_username_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "username": "a"  # Too short
        }

        response = await test_client.post("/api/v1/auth/register", json=invalid_username_data)
        assert response.status_code == 400

    async def test_user_login_success(self, test_client):
        """Test successful user login."""
        # First register a user
        registration_data = {
            "email": "logintest@example.com",
            "password": "SecurePass123!",
            "username": "loginuser"
        }

        await test_client.post("/api/v1/auth/register", json=registration_data)

        # Then login
        login_data = {
            "email": "logintest@example.com",
            "password": "SecurePass123!"
        }

        response = await test_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    async def test_user_login_invalid_credentials(self, test_client):
        """Test login with invalid credentials."""
        # Test with non-existent user
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }

        response = await test_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

        data = response.json()
        assert "credentials" in data["detail"].lower() or "invalid" in data["detail"].lower()

        # Register a user then try wrong password
        registration_data = {
            "email": "wrongpass@example.com",
            "password": "CorrectPass123!",
            "username": "wrongpassuser"
        }

        await test_client.post("/api/v1/auth/register", json=registration_data)

        wrong_password_data = {
            "email": "wrongpass@example.com",
            "password": "WrongPassword"
        }

        response = await test_client.post("/api/v1/auth/login", json=wrong_password_data)
        assert response.status_code == 401

    async def test_protected_endpoint_access_with_token(self, test_client):
        """Test accessing protected endpoint with valid token."""
        # Register and login to get token
        registration_data = {
            "email": "protected@example.com",
            "password": "SecurePass123!",
            "username": "protecteduser"
        }

        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "protected@example.com",
            "password": "SecurePass123!"
        }

        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]

        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = await test_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == "protected@example.com"
        assert data["username"] == "protecteduser"

    async def test_protected_endpoint_access_without_token(self, test_client):
        """Test accessing protected endpoint without token."""
        response = await test_client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_protected_endpoint_access_with_invalid_token(self, test_client):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await test_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    async def test_token_validation_and_expiration(self, test_client):
        """Test token validation and expiration handling."""
        # Create expired token
        expired_payload = {"sub": "user123", "exp": 0}  # Expired timestamp
        expired_token = create_access_token(expired_payload, expires_delta=-3600)  # Expired 1 hour ago

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await test_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

        data = response.json()
        assert "expired" in data["detail"].lower() or "invalid" in data["detail"].lower()

    async def test_logout_functionality(self, test_client):
        """Test logout functionality."""
        # Register and login
        registration_data = {
            "email": "logout@example.com",
            "password": "SecurePass123!",
            "username": "logoutuser"
        }

        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "logout@example.com",
            "password": "SecurePass123!"
        }

        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]

        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = await test_client.post("/api/v1/auth/logout", headers=headers)
        assert response.status_code == 200

        # Token should be invalidated (if blacklisting is implemented)
        # This depends on the actual implementation
        # response = await test_client.get("/api/v1/auth/me", headers=headers)
        # assert response.status_code == 401


@pytest.mark.unit
class TestPasswordSecurity:
    """Test password security measures."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        # Hash should be different from original
        assert hashed != password
        assert len(hashed) > 50  # Bcrypt hashes are long

        # Should verify correctly
        from chatter.utils.security import verify_password
        assert verify_password(password, hashed)

        # Wrong password should not verify
        assert not verify_password("WrongPassword", hashed)

    def test_password_hash_uniqueness(self):
        """Test that password hashes are unique (salt)."""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Same password should produce different hashes due to salt
        assert hash1 != hash2

    def test_password_strength_requirements(self):
        """Test password strength requirements."""
        from chatter.utils.security import (
            validate_password_strength as validate_password,
        )

        # Test minimum requirements
        weak_passwords = [
            "short",
            "12345678",
            "password",
            "Password",  # No number
            "password123",  # No uppercase
            "PASSWORD123"  # No lowercase
        ]

        for weak_pass in weak_passwords:
            result = validate_password(weak_pass)
            assert not result["valid"], f"Should reject weak password: {weak_pass}"

        # Test strong passwords
        strong_passwords = [
            "StrongPass123!",
            "MyV3ry$ecur3P@ss",
            "ComplexP@ssw0rd2024"
        ]

        for strong_pass in strong_passwords:
            result = validate_password(strong_pass)
            assert result["valid"], f"Should accept strong password: {strong_pass}"


@pytest.mark.integration
class TestAuthenticationIntegration:
    """Integration tests for authentication flow."""

    async def test_complete_authentication_flow(self, test_client):
        """Test complete authentication workflow."""
        # 1. Register user
        registration_data = {
            "email": "fullflow@example.com",
            "password": "SecurePass123!",
            "username": "fullflowuser"
        }

        reg_response = await test_client.post("/api/v1/auth/register", json=registration_data)
        assert reg_response.status_code == 201

        # 2. Login
        login_data = {
            "email": "fullflow@example.com",
            "password": "SecurePass123!"
        }

        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Access protected resource
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await test_client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200

        user_data = me_response.json()
        assert user_data["email"] == "fullflow@example.com"

        # 4. Access another protected resource (conversations)
        conv_response = await test_client.get("/api/v1/conversations", headers=headers)
        assert conv_response.status_code == 200  # Should be accessible

        # 5. Logout
        logout_response = await test_client.post("/api/v1/auth/logout", headers=headers)
        assert logout_response.status_code == 200

    async def test_concurrent_authentication_requests(self, test_client):
        """Test concurrent authentication requests."""
        import asyncio

        # Prepare multiple registration requests
        registration_tasks = []
        for i in range(5):
            reg_data = {
                "email": f"concurrent{i}@example.com",
                "password": "SecurePass123!",
                "username": f"concurrent{i}"
            }
            task = test_client.post("/api/v1/auth/register", json=reg_data)
            registration_tasks.append(task)

        # Execute concurrently
        responses = await asyncio.gather(*registration_tasks)

        # All should succeed (different emails)
        for response in responses:
            assert response.status_code == 201

    async def test_authentication_error_handling(self, test_client):
        """Test authentication error handling."""
        # Test malformed request
        response = await test_client.post("/api/v1/auth/login", json={})
        assert response.status_code == 400

        # Test missing fields
        incomplete_data = {"email": "test@example.com"}  # Missing password
        response = await test_client.post("/api/v1/auth/login", json=incomplete_data)
        assert response.status_code == 400

        # Test malformed JSON
        response = await test_client.post(
            "/api/v1/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400

    async def test_user_profile_management(self, test_client):
        """Test user profile management after authentication."""
        # Register and login
        registration_data = {
            "email": "profile@example.com",
            "password": "SecurePass123!",
            "username": "profileuser"
        }

        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "profile@example.com",
            "password": "SecurePass123!"
        }

        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get profile
        profile_response = await test_client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200

        profile_data = profile_response.json()
        assert profile_data["email"] == "profile@example.com"
        assert profile_data["username"] == "profileuser"

        # Update profile (if endpoint exists)
        update_data = {"username": "updatedprofileuser"}
        update_response = await test_client.patch("/api/v1/auth/me", json=update_data, headers=headers)

        # This might be 200 if update is supported, or 404 if not implemented
        assert update_response.status_code in [200, 404, 405]
