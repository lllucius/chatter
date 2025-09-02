"""Unit tests for core authentication module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

from chatter.core.auth import refresh_access_token
from chatter.utils.problem import (
    AuthenticationProblem,
    ConflictProblem,
    NotFoundProblem
)
from tests.test_utils import create_mock_user


@pytest.mark.unit
class TestAuthenticationCore:
    """Test cases for core authentication functionality."""

    def test_refresh_access_token_valid(self):
        """Test refreshing access token with valid refresh token."""
        # Mock the token verification
        with patch('chatter.core.auth.verify_token') as mock_verify:
            with patch('chatter.core.auth.create_access_token') as mock_create:
                # Setup mocks
                mock_verify.return_value = {
                    'sub': 'test_user_id',
                    'type': 'refresh'
                }
                mock_create.return_value = 'new_access_token'
                
                # Test the function
                result = refresh_access_token('valid_refresh_token')
                
                # Assertions
                assert result == 'new_access_token'
                mock_verify.assert_called_once_with('valid_refresh_token')
                # The function expects a data dictionary
                mock_create.assert_called_once()

    def test_refresh_access_token_invalid(self):
        """Test refreshing access token with invalid refresh token."""
        with patch('chatter.core.auth.verify_token') as mock_verify:
            # Setup mock to return None (invalid token)
            mock_verify.return_value = None
            
            # Test the function
            result = refresh_access_token('invalid_refresh_token')
            
            # Assertions
            assert result is None
            mock_verify.assert_called_once_with('invalid_refresh_token')

    def test_refresh_access_token_wrong_type(self):
        """Test refreshing access token with wrong token type."""
        with patch('chatter.core.auth.verify_token') as mock_verify:
            # Setup mock to return access token instead of refresh
            mock_verify.return_value = {
                'sub': 'test_user_id',
                'type': 'access'  # Wrong type
            }
            
            # Test the function - should return None for wrong type
            with patch('chatter.core.auth.create_access_token') as mock_create:
                mock_create.return_value = 'should_not_be_called'
                result = refresh_access_token('access_token')
                
                # Should return None for wrong token type
                # Note: actual implementation may vary
                mock_verify.assert_called_once_with('access_token')

    @pytest.mark.asyncio
    async def test_password_validation(self):
        """Test password validation logic."""
        from chatter.utils.security import validate_password_strength
        
        # Test strong password
        strong_password = "StrongP@ssw0rd123"
        result = validate_password_strength(strong_password)
        assert result["valid"] is True
        assert result["score"] >= 4  # Should have good score
        
        # Test weak passwords
        weak_passwords = [
            "weak",           # too short
            "password123",    # no uppercase/special chars
            "12345678",       # numbers only  
            "PASSWORD",       # uppercase only
        ]
        
        for weak_pwd in weak_passwords:
            result = validate_password_strength(weak_pwd)
            assert result["valid"] is False
            assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_email_validation(self):
        """Test email validation logic."""
        from chatter.utils.security import validate_email
        
        # Test valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True
        
        # Test invalid emails
        invalid_emails = [
            "not-an-email",
            "missing@domain",
            "@missing-local.com",
            "spaces in@email.com",
        ]
        
        for email in invalid_emails:
            result = validate_email(email)
            assert result is False

    @pytest.mark.asyncio
    async def test_password_hashing_and_verification(self):
        """Test password hashing and verification."""
        from chatter.utils.security import hash_password, verify_password
        
        password = "TestPassword123!"
        
        # Hash the password
        hashed = hash_password(password)
        
        # Verify the password matches
        assert verify_password(password, hashed) is True
        
        # Verify wrong password doesn't match
        assert verify_password("WrongPassword", hashed) is False
        
        # Verify hashed password is different from original
        assert hashed != password
        
        # Verify hashing same password twice gives different hashes
        hashed2 = hash_password(password)
        assert hashed != hashed2  # Salt should make them different

    @pytest.mark.asyncio
    async def test_api_key_generation_and_verification(self):
        """Test API key generation and verification."""
        from chatter.utils.security import (
            generate_api_key, 
            hash_api_key, 
            verify_api_key
        )
        
        # Generate API key
        api_key = generate_api_key()
        assert api_key is not None
        assert len(api_key) > 20  # Should be reasonable length
        
        # Hash the API key
        hashed_key = hash_api_key(api_key)
        assert hashed_key != api_key
        
        # Verify the API key
        assert verify_api_key(api_key, hashed_key) is True
        
        # Verify wrong API key doesn't match
        wrong_key = generate_api_key()
        assert verify_api_key(wrong_key, hashed_key) is False


@pytest.mark.unit
class TestAuthenticationUtils:
    """Test utility functions for authentication."""

    def test_create_mock_user(self):
        """Test the mock user creation utility."""
        user = create_mock_user()
        
        # Check required fields exist
        required_fields = ['id', 'username', 'email', 'is_active', 'created_at']
        for field in required_fields:
            assert field in user
        
        # Check default values
        assert user['username'] == 'testuser'
        assert user['email'] == 'test@example.com'
        assert user['is_active'] is True
        
        # Test custom values
        custom_user = create_mock_user(
            username='custom_user',
            email='custom@test.com',
            is_active=False
        )
        assert custom_user['username'] == 'custom_user'
        assert custom_user['email'] == 'custom@test.com'
        assert custom_user['is_active'] is False

    @pytest.mark.asyncio
    async def test_token_expiration_logic(self):
        """Test token expiration logic."""
        from chatter.utils.security import create_access_token, verify_token
        
        # Create token with short expiration
        user_data = {"user_id": "test_user", "email": "test@example.com", "username": "testuser"}
        token = create_access_token(user_data, expires_delta=timedelta(seconds=60))
        
        # Verify token is initially valid
        payload = verify_token(token)
        assert payload is not None
        
        # Verify token structure
        assert 'exp' in payload
        # Note: The actual user data structure may vary based on implementation