"""Tests for authentication core functionality."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.auth import AuthService
from chatter.models.user import User


@pytest.mark.unit
class TestAuthService:
    """Test authentication service core functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.auth_service = AuthService(self.mock_session)

    @pytest.mark.asyncio
    async def test_register_user_success(self):
        """Test successful user registration."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
        }

        expected_user = User(
            id="new-user-id",
            email=user_data["email"],
            username=user_data["username"],
            is_active=True,
            created_at=datetime.utcnow(),
        )

        with patch.object(
            self.auth_service, '_check_user_exists'
        ) as mock_check:
            mock_check.return_value = False

            with patch.object(
                self.auth_service, '_hash_password'
            ) as mock_hash:
                mock_hash.return_value = "hashed_password"

                with patch.object(
                    self.auth_service, '_create_user_record'
                ) as mock_create:
                    mock_create.return_value = expected_user

                    # Act
                    result = await self.auth_service.register_user(
                        **user_data
                    )

                    # Assert
                    assert result.email == user_data["email"]
                    assert result.username == user_data["username"]
                    assert result.is_active is True
                    mock_check.assert_called_once()
                    mock_hash.assert_called_once_with(
                        user_data["password"]
                    )

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self):
        """Test user registration with duplicate email."""
        # Arrange
        user_data = {
            "email": "existing@example.com",
            "username": "testuser",
            "password": "securepassword123",
        }

        with patch.object(
            self.auth_service, '_check_user_exists'
        ) as mock_check:
            mock_check.return_value = True

            # Act & Assert
            from chatter.core.exceptions import ConflictError

            with pytest.raises(ConflictError) as exc_info:
                await self.auth_service.register_user(**user_data)

            assert "already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        """Test successful user authentication."""
        # Arrange
        login_data = {
            "email": "test@example.com",
            "password": "correctpassword",
        }

        mock_user = User(
            id="auth-user-id",
            email=login_data["email"],
            username="testuser",
            password_hash="hashed_password",
            is_active=True,
        )

        expected_token_response = {
            "access_token": "jwt_access_token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "jwt_refresh_token",
        }

        with patch.object(
            self.auth_service, '_get_user_by_email'
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            with patch.object(
                self.auth_service, '_verify_password'
            ) as mock_verify:
                mock_verify.return_value = True

                with patch.object(
                    self.auth_service, '_generate_tokens'
                ) as mock_tokens:
                    mock_tokens.return_value = expected_token_response

                    # Act
                    result = await self.auth_service.authenticate_user(
                        **login_data
                    )

                    # Assert
                    assert (
                        result["access_token"]
                        == expected_token_response["access_token"]
                    )
                    assert result["token_type"] == "bearer"
                    mock_verify.assert_called_once_with(
                        login_data["password"], "hashed_password"
                    )

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_email(self):
        """Test authentication with invalid email."""
        # Arrange
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword",
        }

        with patch.object(
            self.auth_service, '_get_user_by_email'
        ) as mock_get_user:
            mock_get_user.return_value = None

            # Act & Assert
            from chatter.core.exceptions import AuthenticationError

            with pytest.raises(AuthenticationError) as exc_info:
                await self.auth_service.authenticate_user(**login_data)

            assert "Invalid credentials" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self):
        """Test authentication with invalid password."""
        # Arrange
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword",
        }

        mock_user = User(
            id="auth-user-id",
            email=login_data["email"],
            username="testuser",
            password_hash="hashed_password",
            is_active=True,
        )

        with patch.object(
            self.auth_service, '_get_user_by_email'
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            with patch.object(
                self.auth_service, '_verify_password'
            ) as mock_verify:
                mock_verify.return_value = False

                # Act & Assert
                from chatter.core.exceptions import AuthenticationError

                with pytest.raises(AuthenticationError) as exc_info:
                    await self.auth_service.authenticate_user(
                        **login_data
                    )

                assert "Invalid credentials" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self):
        """Test authentication with inactive user."""
        # Arrange
        login_data = {
            "email": "inactive@example.com",
            "password": "correctpassword",
        }

        mock_user = User(
            id="inactive-user-id",
            email=login_data["email"],
            username="inactiveuser",
            password_hash="hashed_password",
            is_active=False,
        )

        with patch.object(
            self.auth_service, '_get_user_by_email'
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            with patch.object(
                self.auth_service, '_verify_password'
            ) as mock_verify:
                mock_verify.return_value = True

                # Act & Assert
                from chatter.core.exceptions import AuthenticationError

                with pytest.raises(AuthenticationError) as exc_info:
                    await self.auth_service.authenticate_user(
                        **login_data
                    )

                assert "account is deactivated" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        """Test successful token refresh."""
        # Arrange
        refresh_token = "valid_refresh_token"

        mock_user = User(
            id="refresh-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True,
        )

        expected_token_response = {
            "access_token": "new_access_token",
            "token_type": "bearer",
            "expires_in": 3600,
        }

        with patch.object(
            self.auth_service, '_validate_refresh_token'
        ) as mock_validate:
            mock_validate.return_value = mock_user

            with patch.object(
                self.auth_service, '_generate_access_token'
            ) as mock_generate:
                mock_generate.return_value = expected_token_response

                # Act
                result = await self.auth_service.refresh_token(
                    refresh_token
                )

                # Assert
                assert (
                    result["access_token"]
                    == expected_token_response["access_token"]
                )
                mock_validate.assert_called_once_with(refresh_token)

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self):
        """Test token refresh with invalid token."""
        # Arrange
        invalid_token = "invalid_refresh_token"

        with patch.object(
            self.auth_service, '_validate_refresh_token'
        ) as mock_validate:
            mock_validate.return_value = None

            # Act & Assert
            from chatter.core.exceptions import AuthenticationError

            with pytest.raises(AuthenticationError) as exc_info:
                await self.auth_service.refresh_token(invalid_token)

            assert "Invalid refresh token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test successful current user retrieval."""
        # Arrange
        access_token = "valid_access_token"

        mock_user = User(
            id="current-user-id",
            email="current@example.com",
            username="currentuser",
            is_active=True,
        )

        with patch.object(
            self.auth_service, '_validate_access_token'
        ) as mock_validate:
            mock_validate.return_value = "current-user-id"

            with patch.object(
                self.auth_service, '_get_user_by_id'
            ) as mock_get_user:
                mock_get_user.return_value = mock_user

                # Act
                result = await self.auth_service.get_current_user(
                    access_token
                )

                # Assert
                assert result.id == mock_user.id
                assert result.email == mock_user.email
                mock_validate.assert_called_once_with(access_token)

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test current user retrieval with invalid token."""
        # Arrange
        invalid_token = "invalid_access_token"

        with patch.object(
            self.auth_service, '_validate_access_token'
        ) as mock_validate:
            mock_validate.return_value = None

            # Act & Assert
            from chatter.core.exceptions import AuthenticationError

            with pytest.raises(AuthenticationError) as exc_info:
                await self.auth_service.get_current_user(invalid_token)

            assert "Invalid access token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_success(self):
        """Test successful user update."""
        # Arrange
        user_id = "update-user-id"
        update_data = {
            "username": "newusername",
            "email": "new@example.com",
        }

        mock_user = User(
            id=user_id,
            email="old@example.com",
            username="oldusername",
            is_active=True,
        )

        updated_user = User(
            id=user_id,
            email=update_data["email"],
            username=update_data["username"],
            is_active=True,
        )

        with patch.object(
            self.auth_service, '_get_user_by_id'
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            with patch.object(
                self.auth_service, '_update_user_record'
            ) as mock_update:
                mock_update.return_value = updated_user

                # Act
                result = await self.auth_service.update_user(
                    user_id, **update_data
                )

                # Assert
                assert result.email == update_data["email"]
                assert result.username == update_data["username"]

    @pytest.mark.asyncio
    async def test_change_password_success(self):
        """Test successful password change."""
        # Arrange
        user_id = "password-user-id"
        current_password = "oldpassword"
        new_password = "newpassword123"

        mock_user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="old_hashed_password",
            is_active=True,
        )

        with patch.object(
            self.auth_service, '_get_user_by_id'
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            with patch.object(
                self.auth_service, '_verify_password'
            ) as mock_verify:
                mock_verify.return_value = True

                with patch.object(
                    self.auth_service, '_hash_password'
                ) as mock_hash:
                    mock_hash.return_value = "new_hashed_password"

                    with patch.object(
                        self.auth_service, '_update_user_password'
                    ) as mock_update:
                        mock_update.return_value = True

                        # Act
                        result = (
                            await self.auth_service.change_password(
                                user_id, current_password, new_password
                            )
                        )

                        # Assert
                        assert result is True
                        mock_verify.assert_called_once_with(
                            current_password, "old_hashed_password"
                        )
                        mock_hash.assert_called_once_with(new_password)

    @pytest.mark.asyncio
    async def test_change_password_invalid_current(self):
        """Test password change with invalid current password."""
        # Arrange
        user_id = "password-user-id"
        current_password = "wrongpassword"
        new_password = "newpassword123"

        mock_user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=True,
        )

        with patch.object(
            self.auth_service, '_get_user_by_id'
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            with patch.object(
                self.auth_service, '_verify_password'
            ) as mock_verify:
                mock_verify.return_value = False

                # Act & Assert
                from chatter.core.exceptions import AuthenticationError

                with pytest.raises(AuthenticationError) as exc_info:
                    await self.auth_service.change_password(
                        user_id, current_password, new_password
                    )

                assert "Invalid current password" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_logout_user_success(self):
        """Test successful user logout."""
        # Arrange
        user_id = "logout-user-id"
        access_token = "valid_access_token"

        with patch.object(
            self.auth_service, '_invalidate_token'
        ) as mock_invalidate:
            mock_invalidate.return_value = True

            # Act
            result = await self.auth_service.logout_user(
                user_id, access_token
            )

            # Assert
            assert result is True
            mock_invalidate.assert_called_once_with(access_token)

    @pytest.mark.asyncio
    async def test_create_api_key_success(self):
        """Test successful API key creation."""
        # Arrange
        user_id = "api-key-user-id"
        key_name = "Test API Key"

        expected_api_key = {
            "id": "api-key-id",
            "name": key_name,
            "key": "ak_1234567890abcdef",
            "user_id": user_id,
            "created_at": datetime.utcnow(),
        }

        with patch.object(
            self.auth_service, '_generate_api_key'
        ) as mock_generate:
            mock_generate.return_value = expected_api_key

            # Act
            result = await self.auth_service.create_api_key(
                user_id, key_name
            )

            # Assert
            assert result["name"] == key_name
            assert result["key"].startswith("ak_")
            assert result["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_validate_api_key_success(self):
        """Test successful API key validation."""
        # Arrange
        api_key = "ak_1234567890abcdef"

        mock_user = User(
            id="api-key-user-id",
            email="api@example.com",
            username="apiuser",
            is_active=True,
        )

        with patch.object(
            self.auth_service, '_get_user_by_api_key'
        ) as mock_get_user:
            mock_get_user.return_value = mock_user

            # Act
            result = await self.auth_service.validate_api_key(api_key)

            # Assert
            assert result.id == mock_user.id
            assert result.email == mock_user.email

    @pytest.mark.asyncio
    async def test_validate_api_key_invalid(self):
        """Test API key validation with invalid key."""
        # Arrange
        invalid_api_key = "ak_invalid_key"

        with patch.object(
            self.auth_service, '_get_user_by_api_key'
        ) as mock_get_user:
            mock_get_user.return_value = None

            # Act & Assert
            from chatter.core.exceptions import AuthenticationError

            with pytest.raises(AuthenticationError) as exc_info:
                await self.auth_service.validate_api_key(
                    invalid_api_key
                )

            assert "Invalid API key" in str(exc_info.value)


@pytest.mark.integration
class TestAuthServiceIntegration:
    """Integration tests for authentication service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.auth_service = AuthService(self.mock_session)

    @pytest.mark.asyncio
    async def test_full_auth_flow(self):
        """Test complete authentication flow."""
        # Register user
        user_data = {
            "email": "integration@example.com",
            "username": "integrationuser",
            "password": "securepassword123",
        }

        # Mock all the required methods for registration
        with patch.object(
            self.auth_service, '_check_user_exists'
        ) as mock_check:
            mock_check.return_value = False

            with patch.object(
                self.auth_service, '_hash_password'
            ) as mock_hash:
                mock_hash.return_value = "hashed_password"

                with patch.object(
                    self.auth_service, '_create_user_record'
                ) as mock_create:
                    registered_user = User(
                        id="integration-user-id",
                        email=user_data["email"],
                        username=user_data["username"],
                        password_hash="hashed_password",
                        is_active=True,
                    )
                    mock_create.return_value = registered_user

                    # Register user
                    user = await self.auth_service.register_user(
                        **user_data
                    )
                    assert user.email == user_data["email"]

                    # Mock authentication
                    with patch.object(
                        self.auth_service, '_get_user_by_email'
                    ) as mock_get_user:
                        mock_get_user.return_value = registered_user

                        with patch.object(
                            self.auth_service, '_verify_password'
                        ) as mock_verify:
                            mock_verify.return_value = True

                            with patch.object(
                                self.auth_service, '_generate_tokens'
                            ) as mock_tokens:
                                token_response = {
                                    "access_token": "integration_access_token",
                                    "token_type": "bearer",
                                    "expires_in": 3600,
                                    "refresh_token": "integration_refresh_token",
                                }
                                mock_tokens.return_value = (
                                    token_response
                                )

                                # Authenticate user
                                tokens = await self.auth_service.authenticate_user(
                                    email=user_data["email"],
                                    password=user_data["password"],
                                )

                                assert "access_token" in tokens
                                assert tokens["token_type"] == "bearer"

                                # Mock token validation for getting current user
                                with patch.object(
                                    self.auth_service,
                                    '_validate_access_token',
                                ) as mock_validate:
                                    mock_validate.return_value = (
                                        registered_user.id
                                    )

                                    with patch.object(
                                        self.auth_service,
                                        '_get_user_by_id',
                                    ) as mock_get_by_id:
                                        mock_get_by_id.return_value = (
                                            registered_user
                                        )

                                        # Get current user
                                        current_user = await self.auth_service.get_current_user(
                                            tokens["access_token"]
                                        )

                                        assert (
                                            current_user.id
                                            == registered_user.id
                                        )
                                        assert (
                                            current_user.email
                                            == user_data["email"]
                                        )

    @pytest.mark.asyncio
    async def test_concurrent_user_operations(self):
        """Test concurrent user operations."""
        # Test concurrent user registrations
        user_data_list = [
            {
                "email": f"user{i}@example.com",
                "username": f"user{i}",
                "password": "password123",
            }
            for i in range(3)
        ]

        # Mock the required methods
        with patch.object(
            self.auth_service, '_check_user_exists'
        ) as mock_check:
            mock_check.return_value = False

            with patch.object(
                self.auth_service, '_hash_password'
            ) as mock_hash:
                mock_hash.return_value = "hashed_password"

                with patch.object(
                    self.auth_service, '_create_user_record'
                ) as mock_create:
                    mock_create.side_effect = [
                        User(
                            id=f"user-{i}-id",
                            email=data["email"],
                            username=data["username"],
                            is_active=True,
                        )
                        for i, data in enumerate(user_data_list)
                    ]

                    # Register users concurrently
                    tasks = [
                        self.auth_service.register_user(**user_data)
                        for user_data in user_data_list
                    ]

                    users = await asyncio.gather(*tasks)

                    # All users should be registered successfully
                    assert len(users) == 3
                    for i, user in enumerate(users):
                        assert user.email == f"user{i}@example.com"


@pytest.mark.unit
class TestAuthServiceHelpers:
    """Test authentication service helper methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.auth_service = AuthService(self.mock_session)

    def test_password_hashing(self):
        """Test password hashing functionality."""
        # Arrange
        password = "testpassword123"

        # Act
        with patch('chatter.core.auth.pwd_context') as mock_pwd_context:
            mock_pwd_context.hash.return_value = "hashed_password"
            hashed = self.auth_service._hash_password(password)

            # Assert
            assert hashed == "hashed_password"
            mock_pwd_context.hash.assert_called_once_with(password)

    def test_password_verification(self):
        """Test password verification functionality."""
        # Arrange
        password = "testpassword123"
        hashed_password = "hashed_password"

        # Act
        with patch('chatter.core.auth.pwd_context') as mock_pwd_context:
            mock_pwd_context.verify.return_value = True
            result = self.auth_service._verify_password(
                password, hashed_password
            )

            # Assert
            assert result is True
            mock_pwd_context.verify.assert_called_once_with(
                password, hashed_password
            )

    def test_jwt_token_generation(self):
        """Test JWT token generation."""
        # Arrange
        user_data = {
            "user_id": "test-user-id",
            "email": "test@example.com",
        }

        # Act
        with patch('chatter.core.auth.jwt.encode') as mock_encode:
            mock_encode.return_value = "jwt_token"
            token = self.auth_service._generate_jwt_token(user_data)

            # Assert
            assert token == "jwt_token"
            mock_encode.assert_called_once()

    def test_jwt_token_validation(self):
        """Test JWT token validation."""
        # Arrange
        token = "valid_jwt_token"
        expected_payload = {
            "user_id": "test-user-id",
            "exp": 1234567890,
        }

        # Act
        with patch('chatter.core.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = expected_payload
            payload = self.auth_service._validate_jwt_token(token)

            # Assert
            assert payload == expected_payload
            mock_decode.assert_called_once()

    def test_api_key_generation(self):
        """Test API key generation."""
        # Arrange

        # Act
        with patch(
            'chatter.core.auth.secrets.token_urlsafe'
        ) as mock_token:
            mock_token.return_value = "random_token"
            api_key = self.auth_service._generate_api_key_string()

            # Assert
            assert api_key.startswith("ak_")
            mock_token.assert_called_once()
