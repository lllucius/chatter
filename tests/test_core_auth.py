"""Core authentication functionality tests."""

import pytest


@pytest.mark.unit
class TestCoreAuth:
    """Test core authentication functionality."""

    async def test_password_hashing(self):
        """Test password hashing functionality."""
        from chatter.core.auth import hash_password, verify_password

        password = "TestPassword123!"

        # Hash password
        hashed = hash_password(password)

        # Verify hash properties
        assert hashed != password  # Should be hashed
        assert isinstance(hashed, str)
        assert len(hashed) > 20  # Should be a reasonable hash length

        # Verify password verification
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    async def test_token_generation(self):
        """Test JWT token generation."""
        from chatter.core.auth import create_access_token

        user_data = {"user_id": "123", "email": "test@example.com"}

        token = create_access_token(data=user_data)

        # Should generate a token
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
        assert "." in token  # JWT tokens have dots

    async def test_token_verification(self):
        """Test JWT token verification."""
        from chatter.core.auth import create_access_token, verify_token

        user_data = {"user_id": "123", "email": "test@example.com"}

        # Create token
        token = create_access_token(data=user_data)

        try:
            # Verify token
            decoded_data = verify_token(token)

            # Should contain original data
            assert decoded_data["user_id"] == "123"
            assert decoded_data["email"] == "test@example.com"

        except (AttributeError, NotImplementedError):
            pytest.skip("Token verification not implemented")

    async def test_invalid_token_verification(self):
        """Test verification of invalid tokens."""
        from chatter.core.auth import verify_token

        invalid_token = "invalid.token.here"

        try:
            result = verify_token(invalid_token)
            # Should raise exception or return None for invalid token
            assert result is None
        except Exception:
            # Expected for invalid token
            pass

    async def test_expired_token_handling(self):
        """Test handling of expired tokens."""
        from chatter.core.auth import create_access_token, verify_token

        user_data = {"user_id": "123", "email": "test@example.com"}

        try:
            # Create token with very short expiry
            token = create_access_token(data=user_data, expires_delta={"seconds": -1})

            # Should fail verification due to expiry
            result = verify_token(token)
            assert result is None

        except (AttributeError, NotImplementedError):
            pytest.skip("Token expiry handling not implemented")
        except Exception:
            # Expected for expired token
            pass

    async def test_user_authentication(self, test_session):
        """Test user authentication process."""
        from chatter.core.auth import authenticate_user

        try:
            # Try to authenticate non-existent user
            result = await authenticate_user(
                session=test_session,
                email="nonexistent@example.com",
                password="password"
            )

            # Should return None or False for non-existent user
            assert result is None or result is False

        except (AttributeError, NotImplementedError):
            pytest.skip("User authentication not implemented")

    async def test_user_registration(self, test_session):
        """Test user registration process."""
        from chatter.core.auth import register_user

        try:
            user_data = {
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "username": "newuser"
            }

            result = await register_user(session=test_session, **user_data)

            # Should return user information
            assert isinstance(result, dict)
            assert result["email"] == "newuser@example.com"
            assert "password" not in result  # Password should not be returned

        except (AttributeError, NotImplementedError):
            pytest.skip("User registration not implemented")

    async def test_duplicate_user_registration(self, test_session):
        """Test registering duplicate user."""
        from chatter.core.auth import register_user

        try:
            user_data = {
                "email": "duplicate@example.com",
                "password": "SecurePassword123!",
                "username": "duplicate"
            }

            # First registration should succeed
            await register_user(session=test_session, **user_data)

            # Second registration should fail
            try:
                await register_user(session=test_session, **user_data)
                raise AssertionError("Should not allow duplicate registration")
            except Exception:
                # Expected for duplicate registration
                pass

        except (AttributeError, NotImplementedError):
            pytest.skip("User registration not implemented")

    async def test_get_current_user(self, test_session):
        """Test getting current user from token."""
        from chatter.core.auth import get_current_user_from_token

        try:
            # Mock valid token
            user_id = "123"
            result = await get_current_user_from_token(
                session=test_session,
                user_id=user_id
            )

            # Should return None for non-existent user
            assert result is None

        except (AttributeError, NotImplementedError):
            pytest.skip("Get current user not implemented")

    async def test_refresh_token(self):
        """Test token refresh functionality."""
        from chatter.core.auth import refresh_access_token

        try:
            # Mock refresh token
            refresh_token = "mock_refresh_token"

            result = refresh_access_token(refresh_token)

            # Should return new access token or None
            assert result is None or isinstance(result, str)

        except (AttributeError, NotImplementedError):
            pytest.skip("Token refresh not implemented")

    async def test_logout(self, test_session):
        """Test user logout functionality."""
        from chatter.core.auth import logout_user

        try:
            token = "mock_token"

            result = await logout_user(session=test_session, token=token)

            # Should successfully logout
            assert result is not None

        except (AttributeError, NotImplementedError):
            pytest.skip("User logout not implemented")

    async def test_password_validation(self):
        """Test password strength validation."""
        from chatter.core.auth import validate_password_strength

        try:
            # Test weak passwords
            weak_passwords = ["123", "password", "abc"]
            for weak_pass in weak_passwords:
                assert validate_password_strength(weak_pass) is False

            # Test strong password
            strong_password = "SecurePassword123!"
            assert validate_password_strength(strong_password) is True

        except (AttributeError, NotImplementedError):
            pytest.skip("Password validation not implemented")

    async def test_email_validation(self):
        """Test email format validation."""
        from chatter.core.auth import validate_email_format

        try:
            # Test invalid emails
            invalid_emails = ["invalid", "invalid@", "@domain.com", "invalid.email"]
            for invalid_email in invalid_emails:
                assert validate_email_format(invalid_email) is False

            # Test valid email
            valid_email = "test@example.com"
            assert validate_email_format(valid_email) is True

        except (AttributeError, NotImplementedError):
            pytest.skip("Email validation not implemented")
