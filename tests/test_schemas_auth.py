"""Tests for authentication schema classes."""

from datetime import datetime
from typing import Optional

import pytest
from pydantic import ValidationError

from chatter.schemas.auth import (
    UserRegistration,
    UserLogin,
    UserResponse,
    TokenResponse,
    PasswordReset,
    PasswordChange,
    RefreshTokenRequest,
    UserUpdate,
    UserPreferences,
)


class TestUserRegistration:
    """Test UserRegistration schema."""

    def test_user_registration_valid(self):
        """Test valid user registration data."""
        registration = UserRegistration(
            email="user@example.com",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        assert registration.email == "user@example.com"
        assert registration.username == "testuser"
        assert registration.password == "SecurePass123!"
        assert registration.full_name == "Test User"

    def test_user_registration_minimal(self):
        """Test user registration with minimal required fields."""
        registration = UserRegistration(
            email="user@example.com",
            username="testuser",
            password="SecurePass123!"
        )
        
        assert registration.email == "user@example.com"
        assert registration.username == "testuser"
        assert registration.password == "SecurePass123!"
        assert registration.full_name is None

    def test_user_registration_email_validation(self):
        """Test email validation in registration."""
        # Invalid email format
        with pytest.raises(ValidationError):
            UserRegistration(
                email="invalid-email",
                username="testuser",
                password="SecurePass123!"
            )
        
        # Empty email
        with pytest.raises(ValidationError):
            UserRegistration(
                email="",
                username="testuser",
                password="SecurePass123!"
            )

    def test_user_registration_username_validation(self):
        """Test username validation in registration."""
        # Username too short
        with pytest.raises(ValidationError):
            UserRegistration(
                email="user@example.com",
                username="ab",
                password="SecurePass123!"
            )
        
        # Username with invalid characters
        with pytest.raises(ValidationError):
            UserRegistration(
                email="user@example.com",
                username="test@user",
                password="SecurePass123!"
            )

    def test_user_registration_password_validation(self):
        """Test password validation in registration."""
        # Password too short
        with pytest.raises(ValidationError):
            UserRegistration(
                email="user@example.com",
                username="testuser",
                password="weak"
            )
        
        # Password without required complexity
        with pytest.raises(ValidationError):
            UserRegistration(
                email="user@example.com",
                username="testuser",
                password="password123"  # No uppercase or special chars
            )

    def test_user_registration_optional_fields(self):
        """Test registration with optional fields."""
        registration = UserRegistration(
            email="user@example.com",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User",
            phone_number="+1234567890",
            timezone="UTC"
        )
        
        assert registration.phone_number == "+1234567890"
        assert registration.timezone == "UTC"

    def test_user_registration_serialization(self):
        """Test registration serialization."""
        registration = UserRegistration(
            email="user@example.com",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        data = registration.dict()
        assert "email" in data
        assert "username" in data
        assert "password" in data  # Should include password for processing
        assert "full_name" in data

    def test_user_registration_exclude_password(self):
        """Test registration serialization excluding password."""
        registration = UserRegistration(
            email="user@example.com",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        # Should be able to exclude password from serialization
        data = registration.dict(exclude={"password"})
        assert "password" not in data
        assert "email" in data


class TestUserLogin:
    """Test UserLogin schema."""

    def test_user_login_with_email(self):
        """Test login with email."""
        login = UserLogin(
            email="user@example.com",
            password="SecurePass123!"
        )
        
        assert login.email == "user@example.com"
        assert login.password == "SecurePass123!"
        assert login.username is None

    def test_user_login_with_username(self):
        """Test login with username."""
        login = UserLogin(
            username="testuser",
            password="SecurePass123!"
        )
        
        assert login.username == "testuser"
        assert login.password == "SecurePass123!"
        assert login.email is None

    def test_user_login_validation_requires_identifier(self):
        """Test that login requires either email or username."""
        # Should fail without email or username
        with pytest.raises(ValidationError):
            UserLogin(password="SecurePass123!")

    def test_user_login_validation_password_required(self):
        """Test that password is required for login."""
        with pytest.raises(ValidationError):
            UserLogin(email="user@example.com")

    def test_user_login_with_remember_me(self):
        """Test login with remember me option."""
        login = UserLogin(
            email="user@example.com",
            password="SecurePass123!",
            remember_me=True
        )
        
        assert login.remember_me is True

    def test_user_login_defaults(self):
        """Test login with default values."""
        login = UserLogin(
            email="user@example.com",
            password="SecurePass123!"
        )
        
        assert login.remember_me is False  # Default value


class TestUserResponse:
    """Test UserResponse schema."""

    def test_user_response_creation(self):
        """Test user response creation."""
        now = datetime.utcnow()
        user = UserResponse(
            id="user-123",
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=now,
            updated_at=now
        )
        
        assert user.id == "user-123"
        assert user.email == "user@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_verified is True

    def test_user_response_no_sensitive_data(self):
        """Test that user response doesn't contain sensitive data."""
        user = UserResponse(
            id="user-123",
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            is_verified=False
        )
        
        # Should not have password or other sensitive fields
        data = user.dict()
        assert "password" not in data
        assert "password_hash" not in data

    def test_user_response_optional_fields(self):
        """Test user response with optional fields."""
        user = UserResponse(
            id="user-123",
            email="user@example.com",
            username="testuser",
            is_active=True,
            is_verified=True
        )
        
        # Optional fields should be None or have defaults
        assert user.full_name is None
        assert user.phone_number is None
        assert user.avatar_url is None

    def test_user_response_with_metadata(self):
        """Test user response with additional metadata."""
        now = datetime.utcnow()
        user = UserResponse(
            id="user-123",
            email="user@example.com",
            username="testuser",
            is_active=True,
            is_verified=True,
            last_login_at=now,
            timezone="America/New_York",
            language="en",
            role="user"
        )
        
        assert user.last_login_at == now
        assert user.timezone == "America/New_York"
        assert user.language == "en"
        assert user.role == "user"


class TestTokenResponse:
    """Test TokenResponse schema."""

    def test_token_response_creation(self):
        """Test token response creation."""
        token = TokenResponse(
            access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            token_type="bearer",
            expires_in=3600
        )
        
        assert token.access_token.startswith("eyJ")
        assert token.token_type == "bearer"
        assert token.expires_in == 3600

    def test_token_response_with_refresh_token(self):
        """Test token response with refresh token."""
        token = TokenResponse(
            access_token="access_token_here",
            token_type="bearer",
            expires_in=3600,
            refresh_token="refresh_token_here"
        )
        
        assert token.refresh_token == "refresh_token_here"

    def test_token_response_defaults(self):
        """Test token response with default values."""
        token = TokenResponse(
            access_token="access_token_here"
        )
        
        assert token.token_type == "bearer"  # Default value
        assert token.expires_in == 3600  # Default value

    def test_token_response_validation(self):
        """Test token response validation."""
        # Access token is required
        with pytest.raises(ValidationError):
            TokenResponse()
        
        # Expires in should be positive
        with pytest.raises(ValidationError):
            TokenResponse(
                access_token="token",
                expires_in=-1
            )

    def test_token_response_serialization(self):
        """Test token response serialization."""
        token = TokenResponse(
            access_token="access_token_here",
            token_type="bearer",
            expires_in=3600,
            refresh_token="refresh_token_here"
        )
        
        data = token.dict()
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "refresh_token" in data


class TestPasswordReset:
    """Test PasswordReset schema."""

    def test_password_reset_request(self):
        """Test password reset request."""
        reset_request = PasswordReset(
            email="user@example.com"
        )
        
        assert reset_request.email == "user@example.com"

    def test_password_reset_email_validation(self):
        """Test email validation in password reset."""
        with pytest.raises(ValidationError):
            PasswordReset(email="invalid-email")

    def test_password_reset_with_token(self):
        """Test password reset with token and new password."""
        reset = PasswordReset(
            email="user@example.com",
            token="reset-token-123",
            new_password="NewSecurePass123!"
        )
        
        assert reset.token == "reset-token-123"
        assert reset.new_password == "NewSecurePass123!"

    def test_password_reset_new_password_validation(self):
        """Test new password validation in reset."""
        with pytest.raises(ValidationError):
            PasswordReset(
                email="user@example.com",
                token="reset-token-123",
                new_password="weak"
            )


class TestPasswordChange:
    """Test PasswordChange schema."""

    def test_password_change_creation(self):
        """Test password change creation."""
        change = PasswordChange(
            current_password="OldPass123!",
            new_password="NewPass123!"
        )
        
        assert change.current_password == "OldPass123!"
        assert change.new_password == "NewPass123!"

    def test_password_change_validation(self):
        """Test password change validation."""
        # Both passwords required
        with pytest.raises(ValidationError):
            PasswordChange(current_password="OldPass123!")
        
        with pytest.raises(ValidationError):
            PasswordChange(new_password="NewPass123!")

    def test_password_change_new_password_strength(self):
        """Test new password strength validation."""
        with pytest.raises(ValidationError):
            PasswordChange(
                current_password="OldPass123!",
                new_password="weak"
            )

    def test_password_change_different_passwords(self):
        """Test that new password must be different from current."""
        # Depending on implementation, might validate passwords are different
        same_password = "SamePass123!"
        
        try:
            change = PasswordChange(
                current_password=same_password,
                new_password=same_password
            )
            # If no validation, check manually or implement custom validation
            assert change.current_password != change.new_password, "Passwords should be different"
        except ValidationError:
            # Expected if validation is implemented
            pass


class TestRefreshTokenRequest:
    """Test RefreshTokenRequest schema."""

    def test_refresh_token_request_creation(self):
        """Test refresh token request creation."""
        request = RefreshTokenRequest(
            refresh_token="refresh_token_here"
        )
        
        assert request.refresh_token == "refresh_token_here"

    def test_refresh_token_validation(self):
        """Test refresh token validation."""
        # Refresh token is required
        with pytest.raises(ValidationError):
            RefreshTokenRequest()
        
        # Empty token should fail
        with pytest.raises(ValidationError):
            RefreshTokenRequest(refresh_token="")


class TestUserUpdate:
    """Test UserUpdate schema."""

    def test_user_update_partial(self):
        """Test partial user update."""
        update = UserUpdate(
            full_name="Updated Name"
        )
        
        assert update.full_name == "Updated Name"
        assert update.email is None  # Other fields not provided

    def test_user_update_multiple_fields(self):
        """Test updating multiple fields."""
        update = UserUpdate(
            full_name="Updated Name",
            phone_number="+1987654321",
            timezone="America/Los_Angeles"
        )
        
        assert update.full_name == "Updated Name"
        assert update.phone_number == "+1987654321"
        assert update.timezone == "America/Los_Angeles"

    def test_user_update_email_validation(self):
        """Test email validation in user update."""
        with pytest.raises(ValidationError):
            UserUpdate(email="invalid-email")

    def test_user_update_all_fields_optional(self):
        """Test that all fields in update are optional."""
        # Should be able to create empty update
        update = UserUpdate()
        assert isinstance(update, UserUpdate)

    def test_user_update_exclude_none(self):
        """Test user update excluding None values."""
        update = UserUpdate(
            full_name="Updated Name",
            email=None
        )
        
        # Should be able to exclude None values
        data = update.dict(exclude_none=True)
        assert "full_name" in data
        assert "email" not in data


class TestUserPreferences:
    """Test UserPreferences schema."""

    def test_user_preferences_creation(self):
        """Test user preferences creation."""
        prefs = UserPreferences(
            language="en",
            timezone="UTC",
            email_notifications=True,
            push_notifications=False
        )
        
        assert prefs.language == "en"
        assert prefs.timezone == "UTC"
        assert prefs.email_notifications is True
        assert prefs.push_notifications is False

    def test_user_preferences_defaults(self):
        """Test user preferences with default values."""
        prefs = UserPreferences()
        
        # Should have sensible defaults
        assert prefs.language == "en"  # Default language
        assert prefs.timezone == "UTC"  # Default timezone
        assert prefs.email_notifications is True  # Default notification setting

    def test_user_preferences_language_validation(self):
        """Test language code validation."""
        # Valid language codes
        valid_languages = ["en", "es", "fr", "de", "ja", "zh"]
        
        for lang in valid_languages:
            prefs = UserPreferences(language=lang)
            assert prefs.language == lang
        
        # Invalid language code
        with pytest.raises(ValidationError):
            UserPreferences(language="invalid")

    def test_user_preferences_timezone_validation(self):
        """Test timezone validation."""
        # Valid timezones
        valid_timezones = [
            "UTC",
            "America/New_York",
            "Europe/London",
            "Asia/Tokyo"
        ]
        
        for tz in valid_timezones:
            prefs = UserPreferences(timezone=tz)
            assert prefs.timezone == tz
        
        # Invalid timezone
        with pytest.raises(ValidationError):
            UserPreferences(timezone="Invalid/Timezone")

    def test_user_preferences_optional_fields(self):
        """Test user preferences optional fields."""
        prefs = UserPreferences(
            language="en",
            timezone="UTC"
        )
        
        # Notification settings should have defaults
        assert isinstance(prefs.email_notifications, bool)
        assert isinstance(prefs.push_notifications, bool)

    def test_user_preferences_serialization(self):
        """Test user preferences serialization."""
        prefs = UserPreferences(
            language="en",
            timezone="America/New_York",
            email_notifications=True,
            push_notifications=False,
            theme="dark"
        )
        
        data = prefs.dict()
        assert "language" in data
        assert "timezone" in data
        assert "email_notifications" in data
        assert "push_notifications" in data
        assert "theme" in data


class TestAuthSchemaIntegration:
    """Test integration between auth schemas."""

    def test_registration_to_user_response(self):
        """Test converting registration to user response."""
        registration = UserRegistration(
            email="user@example.com",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        # Simulate creating user response from registration
        user_data = registration.dict(exclude={"password"})
        user_data.update({
            "id": "user-123",
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        user = UserResponse(**user_data)
        assert user.email == registration.email
        assert user.username == registration.username
        assert user.full_name == registration.full_name

    def test_login_response_flow(self):
        """Test login request to token response flow."""
        login = UserLogin(
            email="user@example.com",
            password="SecurePass123!"
        )
        
        # Simulate successful login response
        token = TokenResponse(
            access_token="access_token_here",
            token_type="bearer",
            expires_in=3600,
            refresh_token="refresh_token_here"
        )
        
        assert login.email == "user@example.com"
        assert token.access_token == "access_token_here"

    def test_user_update_flow(self):
        """Test user update flow."""
        # Current user
        current_user = UserResponse(
            id="user-123",
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            is_verified=True
        )
        
        # Update request
        update = UserUpdate(
            full_name="Updated Test User",
            phone_number="+1234567890"
        )
        
        # Simulate applying update
        update_data = update.dict(exclude_none=True)
        updated_user_data = current_user.dict()
        updated_user_data.update(update_data)
        
        updated_user = UserResponse(**updated_user_data)
        assert updated_user.full_name == "Updated Test User"
        assert updated_user.phone_number == "+1234567890"
        assert updated_user.email == current_user.email  # Unchanged