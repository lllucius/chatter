"""Enhanced authentication endpoints with comprehensive security."""

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.auth import AuthService
from chatter.core.exceptions import AuthenticationError
from chatter.core.monitoring import (
    log_api_key_created,
    log_login_failure,
    log_login_success,
    log_password_change,
)
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
from chatter.utils.database import get_session_generator
from chatter.utils.logging import get_logger
from chatter.utils.problem import AuthenticationProblem

logger = get_logger(__name__)
router = APIRouter()


class CustomHTTPBearer(HTTPBearer):
    """Custom HTTPBearer that raises AuthenticationError with 401 status."""

    async def __call__(
        self, request: Request
    ) -> HTTPAuthorizationCredentials:
        """Extract credentials and raise 401 for missing/invalid auth."""
        try:
            return await super().__call__(request)
        except Exception as e:
            # Convert any authentication failure to 401
            raise AuthenticationError(
                "Authentication credentials required"
            ) from e


security = CustomHTTPBearer()


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    # Check for forwarded headers (load balancer/proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct connection IP
    return request.client.host if request.client else "unknown"


async def get_auth_service(
    session: AsyncSession = Depends(get_session_generator),
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


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current authenticated admin user.

    Args:
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Current admin user

    Raises:
        AuthorizationProblem: If user is not an admin
    """
    is_admin = await auth_service.is_admin(current_user.id)
    if not is_admin:
        from chatter.utils.problem import AuthorizationProblem

        raise AuthorizationProblem(
            detail="Admin privileges required for this operation"
        )

    return current_user


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Register a new user with enhanced security validation.

    Args:
        user_data: User registration data
        request: HTTP request for security logging
        auth_service: Authentication service

    Returns:
        User data and authentication tokens
    """
    client_ip = get_client_ip(request)

    try:
        user = await auth_service.create_user(user_data)
        tokens = auth_service.create_tokens(user)

        # Log successful registration
        from chatter.core.monitoring import (
            SecurityEvent,
            SecurityEventSeverity,
            SecurityEventType,
            get_monitoring_service,
        )

        monitoring_service = await get_monitoring_service()
        event = SecurityEvent(
            event_type=SecurityEventType.ACCOUNT_CREATED,
            severity=SecurityEventSeverity.LOW,
            user_id=user.id,
            ip_address=client_ip,
            user_agent=request.headers.get("User-Agent"),
            details={
                "username": user.username,
                "email": (
                    user.email[:20] + "..."
                    if len(user.email) > 20
                    else user.email
                ),
            },
        )
        await monitoring_service.log_security_event(event)

        return TokenResponse(
            **tokens, user=UserResponse.model_validate(user)
        )

    except Exception as e:
        # Log failed registration attempt for security monitoring
        logger.warning(
            "Registration failed",
            email=(
                user_data.email[:20] + "..."
                if len(user_data.email) > 20
                else user_data.email
            ),
            username=user_data.username,
            ip_address=client_ip,
            error=str(e),
        )
        raise


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate user and return tokens with enhanced security.

    Args:
        user_data: User login data
        request: HTTP request for security logging
        response: HTTP response for cookie setting
        auth_service: Authentication service

    Returns:
        User data and authentication tokens
    """
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    # Use email or username for authentication
    identifier = user_data.username or user_data.email
    if not identifier:
        await log_login_failure("", client_ip, user_agent)
        raise AuthenticationProblem(
            detail="Username or email is required"
        ) from None

    user = await auth_service.authenticate_user(
        identifier, user_data.password
    )

    if not user:
        # Log failed login attempt
        await log_login_failure(identifier, client_ip, user_agent)
        raise AuthenticationProblem(
            detail="Invalid username or password"
        ) from None

    # Log successful login
    await log_login_success(user.id, client_ip, user_agent)

    tokens = auth_service.create_tokens(user)
    
    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="strict",
        max_age=60 * 60 * 24 * 7,  # 7 days (should match settings.refresh_token_expire_days)
        path="/"
    )

    # Return only access token in response body (remove refresh_token from response)
    response_data = {k: v for k, v in tokens.items() if k != "refresh_token"}
    
    return TokenResponse(
        **response_data, user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenRefreshResponse:
    """Refresh access token with enhanced security validation.

    Args:
        request: HTTP request for security logging and cookie reading
        response: HTTP response for setting new refresh token cookie
        auth_service: Authentication service

    Returns:
        New access token (refresh token set in HttpOnly cookie)
    """
    client_ip = get_client_ip(request)
    
    # Read refresh token from HttpOnly cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise AuthenticationProblem(
            detail="Refresh token not found"
        ) from None

    try:
        result = await auth_service.refresh_access_token(refresh_token)
        
        # Set new refresh token as HttpOnly cookie if provided
        if "refresh_token" in result:
            response.set_cookie(
                key="refresh_token",
                value=result["refresh_token"],
                httponly=True,
                secure=True,  # HTTPS only in production
                samesite="strict",
                max_age=60 * 60 * 24 * 7,  # 7 days
                path="/"
            )
            # Remove refresh token from response body
            result = {k: v for k, v in result.items() if k != "refresh_token"}

        # Log token refresh
        from chatter.core.monitoring import (
            SecurityEvent,
            SecurityEventSeverity,
            SecurityEventType,
            get_monitoring_service,
        )
        from chatter.utils.security_enhanced import verify_token

        # Extract user ID for logging
        payload = verify_token(refresh_token)
        user_id = payload.get("sub") if payload else None

        if user_id:
            monitoring_service = await get_monitoring_service()
            event = SecurityEvent(
                event_type=SecurityEventType.TOKEN_REFRESHED,
                severity=SecurityEventSeverity.LOW,
                user_id=user_id,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
            )
            await monitoring_service.log_security_event(event)

        return TokenRefreshResponse(**result)

    except Exception as e:
        logger.warning(
            "Token refresh failed", ip_address=client_ip, error=str(e)
        )
        raise


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> PasswordChangeResponse:
    """Change user password with enhanced security logging.

    Args:
        password_data: Password change data
        request: HTTP request for security logging
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message
    """
    client_ip = get_client_ip(request)

    await auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password,
    )

    # Log password change for security monitoring
    await log_password_change(current_user.id, client_ip)

    return PasswordChangeResponse(
        message="Password changed successfully"
    )


@router.post("/api-key", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> APIKeyResponse:
    """Create API key for current user with enhanced security.

    Args:
        key_data: API key creation data
        request: HTTP request for security logging
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Created API key
    """
    client_ip = get_client_ip(request)

    api_key = await auth_service.create_api_key(
        current_user.id, key_data.name
    )

    # Log API key creation for security monitoring
    await log_api_key_created(current_user.id, key_data.name, client_ip)

    return APIKeyResponse(
        id=current_user.id,
        api_key=api_key,
        api_key_name=key_data.name,
    )


@router.delete("/api-key", response_model=APIKeyRevokeResponse)
async def revoke_api_key(
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> APIKeyRevokeResponse:
    """Revoke current user's API key with security logging.

    Args:
        request: HTTP request for security logging
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message
    """
    client_ip = get_client_ip(request)

    await auth_service.revoke_api_key(current_user.id)

    # Log API key revocation
    from chatter.core.monitoring import (
        SecurityEvent,
        SecurityEventSeverity,
        SecurityEventType,
        get_monitoring_service,
    )

    monitoring_service = await get_monitoring_service()
    event = SecurityEvent(
        event_type=SecurityEventType.API_KEY_REVOKED,
        severity=SecurityEventSeverity.MEDIUM,
        user_id=current_user.id,
        ip_address=client_ip,
        user_agent=request.headers.get("User-Agent"),
    )
    await monitoring_service.log_security_event(event)

    return APIKeyRevokeResponse(message="API key revoked successfully")


@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
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
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    """Logout and revoke current token with enhanced security.

    Args:
        request: HTTP request for security logging
        response: HTTP response for cookie clearing
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message
    """
    client_ip = get_client_ip(request)

    await auth_service.revoke_token(current_user.id)
    
    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="strict"
    )

    # Log logout for security monitoring
    from chatter.core.monitoring import (
        SecurityEvent,
        SecurityEventSeverity,
        SecurityEventType,
        get_monitoring_service,
    )

    monitoring_service = await get_monitoring_service()
    event = SecurityEvent(
        event_type=SecurityEventType.TOKEN_REVOKED,
        severity=SecurityEventSeverity.LOW,
        user_id=current_user.id,
        ip_address=client_ip,
        user_agent=request.headers.get("User-Agent"),
        details={"action": "logout"},
    )
    await monitoring_service.log_security_event(event)

    return LogoutResponse(message="Logged out successfully")


@router.post(
    "/password-reset/request",
    response_model=PasswordResetRequestResponse,
)
async def request_password_reset(
    email: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> PasswordResetRequestResponse:
    """Request password reset with enhanced security logging.

    Args:
        email: User email
        request: HTTP request for security logging
        auth_service: Authentication service

    Returns:
        Success message
    """
    client_ip = get_client_ip(request)

    await auth_service.request_password_reset(email)

    # Log password reset request
    from chatter.core.monitoring import (
        SecurityEvent,
        SecurityEventSeverity,
        SecurityEventType,
        get_monitoring_service,
    )

    monitoring_service = await get_monitoring_service()
    event = SecurityEvent(
        event_type=SecurityEventType.PASSWORD_RESET_REQUESTED,
        severity=SecurityEventSeverity.MEDIUM,
        ip_address=client_ip,
        user_agent=request.headers.get("User-Agent"),
        details={
            "email": email[:20] + "..." if len(email) > 20 else email
        },
    )
    await monitoring_service.log_security_event(event)

    return PasswordResetRequestResponse(
        message="Password reset email sent if account exists"
    )


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetConfirmResponse,
)
async def confirm_password_reset(
    token: str,
    new_password: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> PasswordResetConfirmResponse:
    """Confirm password reset with enhanced security logging.

    Args:
        token: Reset token
        new_password: New password
        request: HTTP request for security logging
        auth_service: Authentication service

    Returns:
        Success message
    """
    client_ip = get_client_ip(request)

    await auth_service.confirm_password_reset(token, new_password)

    # Log password reset completion
    from chatter.core.monitoring import (
        SecurityEvent,
        SecurityEventSeverity,
        SecurityEventType,
        get_monitoring_service,
    )

    monitoring_service = await get_monitoring_service()
    event = SecurityEvent(
        event_type=SecurityEventType.PASSWORD_RESET_COMPLETED,
        severity=SecurityEventSeverity.MEDIUM,
        ip_address=client_ip,
        user_agent=request.headers.get("User-Agent"),
        details={
            "token_prefix": (
                token[:8] + "..." if len(token) > 8 else token
            )
        },
    )
    await monitoring_service.log_security_event(event)

    return PasswordResetConfirmResponse(
        message="Password reset successfully"
    )


@router.delete("/account", response_model=AccountDeactivateResponse)
async def deactivate_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AccountDeactivateResponse:
    """Deactivate current user account with enhanced security logging.

    Args:
        request: HTTP request for security logging
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message
    """
    client_ip = get_client_ip(request)

    await auth_service.deactivate_user(current_user.id)

    # Log account deactivation
    from chatter.core.monitoring import (
        SecurityEvent,
        SecurityEventSeverity,
        SecurityEventType,
        get_monitoring_service,
    )

    monitoring_service = await get_monitoring_service()
    event = SecurityEvent(
        event_type=SecurityEventType.ACCOUNT_DEACTIVATED,
        severity=SecurityEventSeverity.MEDIUM,
        user_id=current_user.id,
        ip_address=client_ip,
        user_agent=request.headers.get("User-Agent"),
    )
    await monitoring_service.log_security_event(event)

    return AccountDeactivateResponse(
        message="Account deactivated successfully"
    )
