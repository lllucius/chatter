"""Authentication schemas for request/response models."""

from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(
        ..., min_length=3, max_length=50, description="Username"
    )
    full_name: str | None = Field(
        None, max_length=255, description="Full name"
    )
    bio: str | None = Field(
        None, max_length=1000, description="User bio"
    )
    avatar_url: str | None = Field(
        None, max_length=500, description="Avatar URL"
    )
    phone_number: str | None = Field(
        None, max_length=20, description="Phone number"
    )


class UserRegistration(UserBase):
    """Schema for user registration."""

    password: str = Field(
        ..., min_length=8, max_length=128, description="Password"
    )


class UserCreate(UserBase):
    """Schema for user creation (alias for UserRegistration)."""

    password: str = Field(
        ..., min_length=8, max_length=128, description="Password"
    )


class UserUpdate(BaseModel):
    """Schema for user profile updates."""

    email: EmailStr | None = Field(
        None, description="User email address"
    )
    full_name: str | None = Field(
        None, max_length=255, description="Full name"
    )
    bio: str | None = Field(
        None, max_length=1000, description="User bio"
    )
    avatar_url: str | None = Field(
        None, max_length=500, description="Avatar URL"
    )
    phone_number: str | None = Field(
        None, max_length=20, description="Phone number"
    )
    default_llm_provider: str | None = Field(
        None, description="Default LLM provider"
    )
    default_profile_id: str | None = Field(
        None, description="Default profile ID"
    )


class UserResponse(UserBase):
    """Schema for user response."""

    id: str = Field(..., description="User ID")
    is_active: bool = Field(..., description="Is user active")
    is_verified: bool = Field(..., description="Is user email verified")
    is_superuser: bool = Field(..., description="Is user a superuser")
    default_llm_provider: str | None = Field(
        None, description="Default LLM provider"
    )
    default_profile_id: str | None = Field(
        None, description="Default profile ID"
    )

    # Usage limits (non-sensitive)
    daily_message_limit: int | None = Field(
        None, description="Daily message limit"
    )
    monthly_message_limit: int | None = Field(
        None, description="Monthly message limit"
    )
    max_file_size_mb: int | None = Field(
        None, description="Max file size in MB"
    )

    # API key name (but not the actual key for security)
    api_key_name: str | None = Field(None, description="API key name")

    created_at: datetime = Field(
        ..., description="Account creation date"
    )
    updated_at: datetime = Field(..., description="Last update date")
    last_login_at: datetime | None = Field(
        None, description="Last login date"
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr | None = Field(
        None, description="User email address"
    )
    username: str | None = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Remember login")

    @model_validator(mode="after")
    def validate_email_or_username(self):
        """Ensure either email or username is provided."""
        if not self.email and not self.username:
            raise ValueError(
                "Either email or username must be provided"
            )
        return self


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str | None = Field(
        None, description="JWT refresh token"
    )
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(
        ..., description="Token expiration time in seconds"
    )
    user: UserResponse = Field(..., description="User information")


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="Refresh token")


class PasswordChange(BaseModel):
    """Schema for password change."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )


class PasswordReset(BaseModel):
    """Schema for password reset request."""

    email: EmailStr = Field(..., description="User email address")
    token: str | None = Field(None, description="Password reset token")
    new_password: str | None = Field(
        None, min_length=8, max_length=128, description="New password"
    )


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )


class EmailVerification(BaseModel):
    """Schema for email verification."""

    token: str = Field(..., description="Email verification token")


class APIKeyCreate(BaseModel):
    """Schema for API key creation."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="API key name"
    )


class APIKeyResponse(BaseModel):
    """Schema for API key response."""

    id: str = Field(..., description="User ID")
    api_key: str = Field(..., description="API key")
    api_key_name: str = Field(..., description="API key name")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str = Field(..., description="Refresh token")


class UserPreferences(BaseModel):
    """Schema for user preferences."""

    user_id: str = Field(..., description="User ID")
    language: str = Field("en", description="Preferred language")
    timezone: str = Field("UTC", description="Preferred timezone")
    theme: str = Field("light", description="UI theme preference")
    notifications_enabled: bool = Field(
        True, description="Enable notifications"
    )
    email_notifications: bool = Field(
        True, description="Enable email notifications"
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        """Validate language code."""
        valid_languages = [
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "ru",
            "zh",
            "ja",
            "ko",
        ]
        if v not in valid_languages:
            raise ValueError(
                f"Language must be one of: {valid_languages}"
            )
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v):
        """Validate timezone."""
        # Basic timezone validation
        if not v or len(v) < 3:
            raise ValueError("Invalid timezone")
        return v

    # Remove duplicate UserRegistration class and clean up

    theme: str = Field(
        default="light", description="UI theme preference"
    )
    language: str = Field(
        default="en", description="Language preference"
    )
    timezone: str = Field(
        default="UTC", description="Timezone preference"
    )
    email_notifications: bool = Field(
        default=True, description="Email notifications enabled"
    )
    push_notifications: bool = Field(
        default=True, description="Push notifications enabled"
    )
    default_model: str | None = Field(
        None, description="Default AI model preference"
    )
    created_at: datetime = Field(..., description="Creation date")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TokenRefreshResponse(BaseModel):
    """Schema for token refresh response."""

    access_token: str = Field(..., description="New access token")
    refresh_token: str | None = Field(
        None,
        description="New refresh token (may be sent as HttpOnly cookie)",
    )
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(
        ..., description="Token expiration time in seconds"
    )


class PasswordChangeResponse(BaseModel):
    """Schema for password change response."""

    message: str = Field(..., description="Success message")


class APIKeyRevokeResponse(BaseModel):
    """Schema for API key revoke response."""

    message: str = Field(..., description="Success message")


class AccountDeactivateResponse(BaseModel):
    """Schema for account deactivation response."""

    message: str = Field(..., description="Success message")


class LogoutResponse(BaseModel):
    """Schema for logout response."""

    message: str = Field(..., description="Success message")


class PasswordResetRequestResponse(BaseModel):
    """Schema for password reset request response."""

    message: str = Field(..., description="Success message")


class PasswordResetConfirmResponse(BaseModel):
    """Schema for password reset confirmation response."""

    message: str = Field(..., description="Success message")
