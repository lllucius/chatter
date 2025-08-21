"""Authentication schemas for request/response models."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: str | None = Field(None, max_length=255, description="Full name")
    bio: str | None = Field(None, max_length=1000, description="User bio")
    avatar_url: str | None = Field(None, max_length=500, description="Avatar URL")


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=128, description="Password")


class UserUpdate(BaseModel):
    """Schema for user profile updates."""
    full_name: str | None = Field(None, max_length=255, description="Full name")
    bio: str | None = Field(None, max_length=1000, description="User bio")
    avatar_url: str | None = Field(None, max_length=500, description="Avatar URL")
    default_llm_provider: str | None = Field(None, description="Default LLM provider")
    default_profile_id: str | None = Field(None, description="Default profile ID")


class UserResponse(UserBase):
    """Schema for user response."""
    id: str = Field(..., description="User ID")
    is_active: bool = Field(..., description="Is user active")
    is_verified: bool = Field(..., description="Is user email verified")
    default_llm_provider: str | None = Field(None, description="Default LLM provider")
    default_profile_id: str | None = Field(None, description="Default profile ID")
    created_at: datetime = Field(..., description="Account creation date")
    updated_at: datetime = Field(..., description="Last update date")
    last_login_at: datetime | None = Field(None, description="Last login date")

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="Refresh token")


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")


class EmailVerification(BaseModel):
    """Schema for email verification."""
    token: str = Field(..., description="Email verification token")


class APIKeyCreate(BaseModel):
    """Schema for API key creation."""
    name: str = Field(..., min_length=1, max_length=100, description="API key name")


class APIKeyResponse(BaseModel):
    """Schema for API key response."""
    id: str = Field(..., description="User ID")
    api_key: str = Field(..., description="API key")
    api_key_name: str = Field(..., description="API key name")
    created_at: datetime = Field(..., description="Creation date")

    class Config:
        from_attributes = True
