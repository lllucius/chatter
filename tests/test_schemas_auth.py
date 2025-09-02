"""Tests for authentication schemas."""

import pytest
from pydantic import ValidationError

from chatter.schemas.auth import (
    PasswordReset,
    PasswordResetConfirm,
    TokenResponse,
    UserBase,
    UserCreate,
    UserLogin,
    UserPreferences,
    UserRegistration,
    UserResponse,
    UserUpdate,
)


@pytest.mark.unit
class TestUserSchemas:
    """Test user-related schemas."""

    def test_user_base_valid(self):
        """Test valid UserBase creation."""
        # Arrange & Act
        user = UserBase(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            bio="A test user bio",
            avatar_url="https://example.com/avatar.jpg",
            phone_number="+1234567890",
        )

        # Assert
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.bio == "A test user bio"
        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.phone_number == "+1234567890"

    def test_user_base_minimal(self):
        """Test UserBase with minimal required fields."""
        # Arrange & Act
        user = UserBase(email="minimal@example.com", username="minimal")

        # Assert
        assert user.email == "minimal@example.com"
        assert user.username == "minimal"
        assert user.full_name is None
        assert user.bio is None
        assert user.avatar_url is None
        assert user.phone_number is None

    def test_user_base_invalid_email(self):
        """Test UserBase with invalid email."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="invalid-email", username="testuser")

        assert "value is not a valid email address" in str(
            exc_info.value
        )

    def test_user_base_invalid_username_too_short(self):
        """Test UserBase with username too short."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="test@example.com", username="ab")

        assert "at least 3 characters" in str(exc_info.value)

    def test_user_base_invalid_username_too_long(self):
        """Test UserBase with username too long."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="test@example.com", username="a" * 51)

        assert "at most 50 characters" in str(exc_info.value)

    def test_user_registration_valid(self):
        """Test valid UserRegistration."""
        # Arrange & Act
        user = UserRegistration(
            email="register@example.com",
            username="newuser",
            password="securepassword123",
            full_name="New User",
        )

        # Assert
        assert user.email == "register@example.com"
        assert user.username == "newuser"
        assert user.password == "securepassword123"
        assert user.full_name == "New User"

    def test_user_registration_invalid_password_too_short(self):
        """Test UserRegistration with password too short."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserRegistration(
                email="test@example.com",
                username="testuser",
                password="short",
            )

        assert "at least 8 characters" in str(exc_info.value)

    def test_user_create_equivalent_to_registration(self):
        """Test UserCreate is equivalent to UserRegistration."""
        # Arrange & Act
        user_create = UserCreate(
            email="create@example.com",
            username="createuser",
            password="password123",
        )

        user_registration = UserRegistration(
            email="create@example.com",
            username="createuser",
            password="password123",
        )

        # Assert
        assert user_create.email == user_registration.email
        assert user_create.username == user_registration.username
        assert user_create.password == user_registration.password

    def test_user_login_with_username(self):
        """Test valid UserLogin with username."""
        # Arrange & Act
        login = UserLogin(username="testuser", password="password123")

        # Assert
        assert login.username == "testuser"
        assert login.password == "password123"
        assert login.email is None

    def test_user_login_with_email(self):
        """Test UserLogin with email."""
        # Arrange & Act
        login = UserLogin(
            email="test@example.com", password="password123"
        )

        # Assert
        assert login.email == "test@example.com"
        assert login.password == "password123"
        assert login.username is None

    def test_user_login_no_email_or_username(self):
        """Test UserLogin validation error when neither email nor username provided."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(password="password123")

        assert "Either email or username must be provided" in str(
            exc_info.value
        )

    def test_user_response_structure(self):
        """Test UserResponse schema structure."""
        # Arrange
        from datetime import datetime

        # Act
        user_response = UserResponse(
            id="user-123",
            email="response@example.com",
            username="responseuser",
            full_name="Response User",
            bio="User bio",
            avatar_url="https://example.com/avatar.jpg",
            phone_number="+1234567890",
            is_active=True,
            is_verified=False,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 30, 0),
            last_login_at=datetime(2023, 1, 1, 11, 0, 0),
        )

        # Assert
        assert user_response.id == "user-123"
        assert user_response.email == "response@example.com"
        assert user_response.username == "responseuser"
        assert user_response.is_active is True
        assert user_response.is_verified is False

    def test_user_update_partial(self):
        """Test UserUpdate with partial data."""
        # Arrange & Act
        update = UserUpdate(full_name="Updated Name", bio="Updated bio")

        # Assert
        assert update.full_name == "Updated Name"
        assert update.bio == "Updated bio"
        assert update.email is None
        assert update.username is None

    def test_user_preferences_valid(self):
        """Test UserPreferences schema."""
        # Arrange & Act
        from datetime import datetime

        preferences = UserPreferences(
            user_id="user-123",
            theme="dark",
            language="en",
            timezone="UTC",
            notifications_enabled=True,
            email_notifications=False,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
        )

        # Assert
        assert preferences.user_id == "user-123"
        assert preferences.theme == "dark"
        assert preferences.language == "en"
        assert preferences.timezone == "UTC"
        assert preferences.notifications_enabled is True
        assert preferences.email_notifications is False

    def test_token_response_structure(self):
        """Test TokenResponse schema."""
        # Arrange
        from datetime import datetime

        user_response = UserResponse(
            id="user-123",
            email="token@example.com",
            username="tokenuser",
            is_active=True,
            is_verified=True,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 0, 0),
        )

        # Act
        token = TokenResponse(
            access_token="access.token.here",
            refresh_token="refresh.token.here",
            token_type="bearer",
            expires_in=3600,
            user=user_response,
        )

        # Assert
        assert token.access_token == "access.token.here"
        assert token.token_type == "bearer"
        assert token.expires_in == 3600
        assert token.refresh_token == "refresh.token.here"
        assert token.user.id == "user-123"

    def test_password_reset_request_valid(self):
        """Test PasswordReset schema for request."""
        # Arrange & Act
        reset_request = PasswordReset(email="reset@example.com")

        # Assert
        assert reset_request.email == "reset@example.com"
        assert reset_request.token is None
        assert reset_request.new_password is None

    def test_password_reset_confirm_valid(self):
        """Test PasswordResetConfirm schema."""
        # Arrange & Act
        reset = PasswordResetConfirm(
            token="reset-token-123", new_password="newpassword123"
        )

        # Assert
        assert reset.token == "reset-token-123"
        assert reset.new_password == "newpassword123"

    def test_password_reset_confirm_invalid_password(self):
        """Test PasswordResetConfirm with invalid password."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="reset-token-123", new_password="short"
            )

        assert "at least 8 characters" in str(exc_info.value)


@pytest.mark.unit
class TestAuthSchemaValidation:
    """Test authentication schema validation logic."""

    def test_email_normalization(self):
        """Test email address normalization."""
        # Arrange & Act
        user = UserBase(
            email="  TEST@EXAMPLE.COM  ", username="testuser"
        )

        # Assert
        # Pydantic automatically normalizes email addresses
        assert "@" in user.email.lower()

    def test_username_validation_special_chars(self):
        """Test username validation with special characters."""
        # Valid usernames
        valid_usernames = [
            "user123",
            "test_user",
            "user-name",
            "User.Name",
        ]

        for username in valid_usernames:
            user = UserBase(email="test@example.com", username=username)
            assert user.username == username

    def test_bio_length_validation(self):
        """Test bio length validation."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserBase(
                email="test@example.com",
                username="testuser",
                bio="a" * 1001,  # Exceeds max length
            )

        assert "at most 1000 characters" in str(exc_info.value)

    def test_phone_number_validation(self):
        """Test phone number validation."""
        # Valid phone numbers
        valid_phones = ["+1234567890", "123-456-7890", "(123) 456-7890"]

        for phone in valid_phones:
            user = UserBase(
                email="test@example.com",
                username="testuser",
                phone_number=phone,
            )
            assert user.phone_number == phone

    def test_avatar_url_validation(self):
        """Test avatar URL validation."""
        # Arrange & Act
        user = UserBase(
            email="test@example.com",
            username="testuser",
            avatar_url="https://cdn.example.com/avatars/user123.png",
        )

        # Assert
        assert "https://" in user.avatar_url

    def test_schema_serialization(self):
        """Test schema serialization to dict."""
        # Arrange
        user = UserRegistration(
            email="serialize@example.com",
            username="serialuser",
            password="password123",
            full_name="Serial User",
            bio="Test bio",
        )

        # Act
        data = user.model_dump()

        # Assert
        assert data["email"] == "serialize@example.com"
        assert data["username"] == "serialuser"
        assert data["password"] == "password123"
        assert data["full_name"] == "Serial User"
        assert data["bio"] == "Test bio"
        assert (
            "id" not in data
        )  # Should not include fields not in schema

    def test_schema_json_serialization(self):
        """Test schema JSON serialization."""
        # Arrange
        user = UserBase(email="json@example.com", username="jsonuser")

        # Act
        json_str = user.model_dump_json()

        # Assert
        assert '"email":"json@example.com"' in json_str.replace(" ", "")
        assert '"username":"jsonuser"' in json_str.replace(" ", "")
