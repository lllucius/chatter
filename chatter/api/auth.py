"""Authentication endpoints."""

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.auth import AuthService
from chatter.models.user import User
from chatter.schemas.auth import (
    AccountDeactivateResponse,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyRevokeResponse,
    LogoutResponse,
    PasswordChange,
    PasswordChangeResponse,
    PasswordResetConfirmResponse,
    PasswordResetRequestResponse,
    TokenRefresh,
    TokenRefreshResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger
from chatter.utils.problem import AuthenticationProblem

logger = get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


async def get_auth_service(
    session: AsyncSession = Depends(get_session)
) -> AuthService:
    """Get authentication service instance.

    Args:
        session: Database session

    Returns:
        AuthService instance
    """
    return AuthService(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current authenticated user.

    Args:
        credentials: Authorization credentials
        auth_service: Authentication service

    Returns:
        Current user
    """
    return await auth_service.get_current_user(credentials.credentials)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Register a new user.

    Args:
        user_data: User registration data
        auth_service: Authentication service

    Returns:
        User data and authentication tokens
    """
    user = await auth_service.create_user(user_data)
    tokens = auth_service.create_tokens(user)

    return TokenResponse(
        **tokens, user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate user and return tokens.

    Args:
        user_data: User login data
        auth_service: Authentication service

    Returns:
        User data and authentication tokens
    """
    user = await auth_service.authenticate_user(
        user_data.username, user_data.password
    )
    if not user:
        raise AuthenticationProblem(
            detail="Invalid username or password"
        ) from None

    tokens = auth_service.create_tokens(user)

    return TokenResponse(
        **tokens, user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    token_data: TokenRefresh,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenRefreshResponse:
    """Refresh access token.

    Args:
        token_data: Refresh token data
        auth_service: Authentication service

    Returns:
        New access and refresh tokens
    """
    result = await auth_service.refresh_access_token(
        token_data.refresh_token
    )
    return TokenRefreshResponse(**result)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user=Depends(get_current_user)
) -> UserResponse:
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user data
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user=Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Update current user profile.

    Args:
        user_data: Profile update data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Updated user data
    """
    updated_user = await auth_service.update_user(
        current_user.id, user_data
    )
    return UserResponse.model_validate(updated_user)


@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    password_data: PasswordChange,
    current_user=Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> PasswordChangeResponse:
    """Change user password.

    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message
    """
    await auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password,
    )

    return PasswordChangeResponse(
        message="Password changed successfully"
    )


@router.post("/api-key", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user=Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> APIKeyResponse:
    """Create API key for current user.

    Args:
        key_data: API key creation data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Created API key
    """
    api_key = await auth_service.create_api_key(
        current_user.id, key_data.name
    )

    return APIKeyResponse(
        id=current_user.id,
        api_key=api_key,
        api_key_name=key_data.name,
        created_at=current_user.updated_at,
    )


@router.delete("/api-key", response_model=APIKeyRevokeResponse)
async def revoke_api_key(
    current_user=Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> APIKeyRevokeResponse:
    """Revoke current user's API key.

    Args:
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message
    """
    await auth_service.revoke_api_key(current_user.id)
    return APIKeyRevokeResponse(message="API key revoked successfully")


@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    current_user=Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> list[APIKeyResponse]:
    """List user's API keys.

    Args:
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        List of API keys
    """
    api_keys = await auth_service.list_api_keys(current_user.id)
    return [APIKeyResponse.model_validate(key) for key in api_keys]


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user=Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    """Logout and revoke current token.

    Args:
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message
    """
    await auth_service.revoke_token(current_user.id)
    return LogoutResponse(message="Logged out successfully")


@router.post("/password-reset/request", response_model=PasswordResetRequestResponse)
async def request_password_reset(
    email: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> PasswordResetRequestResponse:
    """Request password reset.

    Args:
        email: User email
        auth_service: Authentication service

    Returns:
        Success message
    """
    await auth_service.request_password_reset(email)
    return PasswordResetRequestResponse(message="Password reset email sent if account exists")


@router.post("/password-reset/confirm", response_model=PasswordResetConfirmResponse)
async def confirm_password_reset(
    token: str,
    new_password: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> PasswordResetConfirmResponse:
    """Confirm password reset.

    Args:
        token: Reset token
        new_password: New password
        auth_service: Authentication service

    Returns:
        Success message
    """
    await auth_service.confirm_password_reset(token, new_password)
    return PasswordResetConfirmResponse(message="Password reset successfully")


@router.delete("/account", response_model=AccountDeactivateResponse)
async def deactivate_account(
    current_user=Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AccountDeactivateResponse:
    """Deactivate current user account.

    Args:
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message
    """
    await auth_service.deactivate_user(current_user.id)
    return AccountDeactivateResponse(
        message="Account deactivated successfully"
    )
