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
        """Pydantic configuration."""
        from_attributes = True

    @classmethod  
    def model_validate_user(cls, user) -> "UserResponse":
        """Safely validate a User object for UserResponse.
        
        This method handles potential MissingGreenlet errors that can occur
        when SQLAlchemy objects are accessed outside of an active session context.
        
        Args:
            user: SQLAlchemy User object
            
        Returns:
            UserResponse instance
        """
        try:
            # Try the standard model_validate first
            return cls.model_validate(user)
        except Exception as e:
            error_str = str(e)
            # Check if this is the specific MissingGreenlet error we're trying to fix
            if ("MissingGreenlet" in error_str or 
                "greenlet_spawn" in error_str or
                "await_only" in error_str):
                
                # Fallback: manually construct the response by accessing attributes carefully
                # Using getattr with defaults to avoid errors on timestamp fields
                try:
                    # Basic attributes that should always be accessible
                    response_data = {
                        "email": user.email,
                        "username": user.username,
                        "full_name": user.full_name,
                        "bio": user.bio,
                        "avatar_url": user.avatar_url,
                        "id": user.id,
                        "is_active": user.is_active,
                        "is_verified": user.is_verified,
                        "default_llm_provider": user.default_llm_provider,
                        "default_profile_id": user.default_profile_id,
                        "last_login_at": user.last_login_at,
                    }
                    
                    # Handle timestamp fields more carefully
                    try:
                        response_data["created_at"] = user.created_at
                    except Exception:
                        # Fallback to current time if we can't access created_at
                        response_data["created_at"] = datetime.now()
                        
                    try:
                        response_data["updated_at"] = user.updated_at
                    except Exception:
                        # Fallback to current time if we can't access updated_at
                        response_data["updated_at"] = datetime.now()
                    
                    return cls(**response_data)
                    
                except Exception:
                    # If manual construction also fails, raise the original error
                    # with additional context
                    raise ValueError(
                        f"Unable to convert User object to UserResponse due to session context issues. "
                        f"Original error: {error_str}. "
                        f"This typically occurs when the User object is accessed outside of an active "
                        f"database session. Ensure the conversion happens within the same session "
                        f"context where the User object was retrieved."
                    ) from e
            else:
                # For other validation errors, re-raise as-is
                raise


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
        """Pydantic configuration."""
        from_attributes = True
