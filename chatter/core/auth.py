"""Enhanced authentication service for user management with security features."""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import settings
from chatter.models.user import User
from chatter.schemas.auth import UserCreate, UserUpdate
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    AuthenticationProblem,
    AuthorizationProblem,
    BadRequestProblem,
    ConflictProblem,
    NotFoundProblem,
)
from chatter.utils.security_enhanced import (
    contains_personal_info,
    create_access_token,
    create_refresh_token,
    generate_secure_api_key,
    hash_password,
    validate_email_advanced,
    validate_password_advanced,
    validate_username_secure,
    verify_api_key_secure,
    verify_password,
    verify_token,
)

logger = get_logger(__name__)


def refresh_access_token(refresh_token: str) -> str | None:
    """Refresh an access token using a refresh token.

    Args:
        refresh_token: The refresh token

    Returns:
        New access token if valid, None otherwise
    """
    try:
        # Verify the refresh token
        payload = verify_token(refresh_token)
        if not payload:
            return None

        # Create new access token with same user data
        user_data = {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "username": payload.get("username"),
        }

        return create_access_token(data=user_data)
    except Exception:
        return None


def validate_email_format(email: str) -> bool:
    """Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if email format is valid, False otherwise
    """
    import re

    # Basic email validation regex
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not email:
        return False

    return bool(re.match(email_pattern, email))


# Use RFC 9457 compliant problem classes instead of HTTPException subclasses
AuthenticationError = AuthenticationProblem
AuthorizationError = AuthorizationProblem


def UserAlreadyExistsError(detail: str = "User already exists"):
    return ConflictProblem(detail=detail, conflicting_resource="user")


def UserNotFoundError(detail: str = "User not found"):
    return NotFoundProblem(detail=detail, resource_type="user")


class AuthService:
    """Authentication service for user management."""

    def __init__(self, session: AsyncSession):
        """Initialize auth service with database session.

        Args:
            session: Database session
        """
        self.session = session

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with enhanced security validation.

        Args:
            user_data: User creation data

        Returns:
            Created user

        Raises:
            UserAlreadyExistsError: If user already exists
            BadRequestProblem: If validation fails
        """
        # Enhanced email validation with security checks
        if not validate_email_advanced(user_data.email):
            raise BadRequestProblem(
                detail="Invalid email format or disposable email domain"
            ) from None

        # Enhanced username validation
        if not validate_username_secure(user_data.username):
            raise BadRequestProblem(
                detail="Username format is invalid or contains prohibited patterns"
            ) from None

        # Enhanced password validation with entropy and security checks
        password_validation = validate_password_advanced(
            user_data.password
        )
        if not password_validation["valid"]:
            raise BadRequestProblem(
                detail="Password does not meet security requirements",
                errors=password_validation["errors"],
            ) from None

        # Check if password contains personal information
        user_data_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
        }
        if contains_personal_info(user_data.password, user_data_dict):
            raise BadRequestProblem(
                detail="Password should not contain personal information"
            ) from None

        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsError(
                "User with this email already exists"
            ) from None

        existing_user = await self.get_user_by_username(
            user_data.username
        )
        if existing_user:
            raise UserAlreadyExistsError(
                "User with this username already exists"
            ) from None

        # Create user with enhanced password hashing
        hashed_password = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            bio=user_data.bio,
            avatar_url=user_data.avatar_url,
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        logger.info("User created", user_id=user.id, email=user.email)
        return user

    async def authenticate_user(
        self, username: str, password: str
    ) -> User | None:
        """Authenticate user with enhanced security checks.

        Args:
            username: User username or email
            password: User password

        Returns:
            User if authentication successful, None otherwise
        """
        # Support both username and email authentication
        user = None
        if "@" in username:
            # Looks like an email
            user = await self.get_user_by_email(username)
        else:
            # Treat as username
            user = await self.get_user_by_username(username)

        if not user:
            # Log failed attempt for security monitoring
            logger.warning(
                "Authentication failed - user not found",
                identifier=(
                    username[:10] + "..."
                    if len(username) > 10
                    else username
                ),
            )
            return None

        if not user.is_active:
            logger.warning(
                "Authentication failed - user inactive", user_id=user.id
            )
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(
                "Authentication failed - invalid password",
                user_id=user.id,
            )
            return None

        # Update last login timestamp
        user.last_login_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(user)

        logger.info(
            "User authenticated successfully",
            user_id=user.id,
            username=user.username,
        )
        return user

    async def is_admin(self, user_id: str) -> bool:
        """Check if user has admin privileges.

        Args:
            user_id: User ID

        Returns:
            True if user is superuser, False otherwise
        """
        user = await self.get_user_by_id(user_id)
        return user is not None and user.is_superuser

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by ID with caching.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        # Try cache first for performance
        try:
            from chatter.core.cache_factory import get_general_cache

            cache_service = get_general_cache()

            # Check cache health instead of is_connected for unified cache
            health = await cache_service.health_check()
            if health.get("status") == "healthy":
                cache_key = f"user:{user_id}"
                cached_user = await cache_service.get(cache_key)
                if cached_user:
                    # Convert back to User object (simplified caching)
                    logger.debug("User found in cache", user_id=user_id)
                    # For now, fall through to database - can enhance later
        except Exception as cache_error:
            logger.debug(
                "Cache lookup failed, using database",
                user_id=user_id,
                error=str(cache_error),
            )

        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        # Refresh to ensure all database-generated fields are loaded
        if user:
            await self.session.refresh(user)

        # Cache the result for future lookups
        if user:
            try:

                from chatter.core.cache_factory import get_general_cache

                cache_service = get_general_cache()
                health = await cache_service.health_check()
                if health.get("status") == "healthy":
                    cache_key = f"user:{user_id}"
                    # Cache for 15 minutes
                    await cache_service.set(
                        cache_key,
                        "cached",
                        ttl=900,  # 15 minutes in seconds
                    )
                    logger.debug("User cached", user_id=user_id)
            except Exception as cache_error:
                logger.debug(
                    "Cache storage failed",
                    user_id=user_id,
                    error=str(cache_error),
                )

        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if user:
            # Refresh to ensure all database-generated fields are loaded
            await self.session.refresh(user)
        return user

    async def get_user_by_username(self, username: str) -> User | None:
        """Get user by username.

        Args:
            username: Username

        Returns:
            User if found, None otherwise
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        if user:
            # Refresh to ensure all database-generated fields are loaded
            await self.session.refresh(user)
        return user

    async def get_user_by_api_key(self, api_key: str) -> User | None:
        """Get user by API key with enhanced security.

        Args:
            api_key: API key (plaintext)

        Returns:
            User if found and API key is valid, None otherwise
        """
        # Use indexed query for better performance
        result = await self.session.execute(
            select(User).where(User.api_key.isnot(None)).limit(100)
        )
        users_with_keys = result.scalars().all()

        # Check each user's hashed API key using secure verification
        for user in users_with_keys:
            if user.api_key:
                # Try new secure verification first
                # Use secure API key verification
                if verify_api_key_secure(api_key, user.api_key):
                    return user

        return None

    async def update_user(
        self, user_id: str, user_data: UserUpdate
    ) -> User:
        """Update user profile.

        Args:
            user_id: User ID
            user_data: Update data

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError() from None

        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)

        logger.info("User updated", user_id=user.id)
        return user

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> bool:
        """Change user password with enhanced security validation.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully

        Raises:
            UserNotFoundError: If user not found
            AuthenticationError: If current password is invalid
            BadRequestProblem: If new password is invalid
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError() from None

        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            logger.warning(
                "Password change failed - incorrect current password",
                user_id=user.id,
            )
            raise AuthenticationError(
                "Current password is incorrect"
            ) from None

        # Enhanced password validation
        password_validation = validate_password_advanced(new_password)
        if not password_validation["valid"]:
            raise BadRequestProblem(
                detail="New password does not meet security requirements",
                errors=password_validation["errors"],
            ) from None

        # Check if new password contains personal information
        user_data_dict = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
        }
        if contains_personal_info(new_password, user_data_dict):
            raise BadRequestProblem(
                detail="Password should not contain personal information"
            ) from None

        # Check if new password is same as current
        if verify_password(new_password, user.hashed_password):
            raise BadRequestProblem(
                detail="New password must be different from current password"
            ) from None

        # Update password with enhanced hashing
        user.hashed_password = hash_password(new_password)
        await self.session.commit()
        await self.session.refresh(user)

        # Revoke all existing tokens for security
        try:
            from chatter.core.token_manager import get_token_manager

            token_manager = await get_token_manager()
            await token_manager.revoke_all_user_tokens(
                user_id, "password_change"
            )
        except Exception as e:
            logger.warning(
                f"Failed to revoke tokens after password change: {e}"
            )

        logger.info("Password changed successfully", user_id=user.id)
        return True

    async def create_api_key(self, user_id: str, key_name: str) -> str:
        """Create secure API key for user.

        Args:
            user_id: User ID
            key_name: API key name

        Returns:
            Generated API key (plaintext, only returned once)

        Raises:
            UserNotFoundError: If user not found
            ConflictProblem: If user already has an API key
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError() from None

        # Check if user already has an API key (limit one per user for now)
        if user.api_key:
            raise ConflictProblem(
                detail="User already has an API key. Revoke existing key first.",
                conflicting_resource="api_key",
            ) from None

        # Generate secure API key with proper hashing
        api_key, hashed_api_key = generate_secure_api_key()

        # Store only the hash in the database
        user.api_key = hashed_api_key
        user.api_key_name = key_name

        await self.session.commit()
        await self.session.refresh(user)

        logger.info(
            "Secure API key created",
            user_id=user.id,
            key_name=key_name,
            key_prefix=api_key[:20] + "...",
        )

        # Return the plaintext API key only once - it won't be stored
        return api_key

    async def revoke_api_key(self, user_id: str) -> bool:
        """Revoke user's API key.

        Args:
            user_id: User ID

        Returns:
            True if API key revoked successfully

        Raises:
            UserNotFoundError: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError() from None

        user.api_key = None
        user.api_key_name = None
        await self.session.commit()
        await self.session.refresh(user)

        logger.info("API key revoked", user_id=user.id)
        return True

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account.

        Args:
            user_id: User ID

        Returns:
            True if user deactivated successfully

        Raises:
            UserNotFoundError: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError() from None

        user.is_active = False
        await self.session.commit()
        await self.session.refresh(user)

        logger.info("User deactivated", user_id=user.id)
        return True

    def create_tokens(self, user: User) -> dict[str, Any]:
        """Create access and refresh tokens for user with enhanced security.

        Args:
            user: User object

        Returns:
            Dictionary with tokens and expiration info
        """
        import uuid

        # Generate unique JWT ID for token tracking
        jti = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        issued_at = datetime.now(UTC)

        access_token_expires = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        refresh_token_expires = timedelta(
            days=settings.refresh_token_expire_days
        )

        # Enhanced access token with security claims
        access_token_data = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "jti": jti,
            "type": "access",
            "iat": issued_at,
            "session_id": session_id,
            "permissions": self._get_user_permissions(user),
        }

        # Enhanced refresh token
        refresh_token_data = {
            "sub": user.id,
            "jti": jti,
            "type": "refresh",
            "iat": issued_at,
            "session_id": session_id,
        }

        access_token = create_access_token(
            data=access_token_data,
            expires_delta=access_token_expires,
        )

        refresh_token = create_refresh_token(
            data=refresh_token_data,
            expires_delta=refresh_token_expires,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "jti": jti,
            "session_id": session_id,
        }

    def _get_user_permissions(self, user: User) -> list[str]:
        """Get user permissions for token.

        Args:
            user: User object

        Returns:
            List of permission strings
        """
        permissions = ["read:profile", "write:profile"]

        if user.is_superuser:
            permissions.extend(
                ["admin:users", "admin:system", "read:all", "write:all"]
            )

        if user.is_verified:
            permissions.extend(
                [
                    "read:documents",
                    "write:documents",
                    "read:conversations",
                    "write:conversations",
                ]
            )

        return permissions

    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token with enhanced security validation.

        Args:
            token: JWT token

        Returns:
            Current user

        Raises:
            AuthenticationError: If token is invalid or user not found
        """
        payload = verify_token(token)
        if not payload:
            raise AuthenticationError("Invalid token") from None

        # Enhanced token validation
        jti = payload.get("jti")
        if jti:
            # Check if token is blacklisted
            try:
                from chatter.core.token_manager import get_token_manager

                token_manager = await get_token_manager()
                if await token_manager.is_token_blacklisted(jti):
                    raise AuthenticationError(
                        "Token has been revoked"
                    ) from None
            except Exception as e:
                logger.debug(f"Token blacklist check failed: {e}")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token") from None

        user = await self.get_user_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found") from None

        if not user.is_active:
            raise AuthenticationError(
                "User account is deactivated"
            ) from None

        return user

    async def refresh_access_token(
        self, refresh_token: str
    ) -> dict[str, Any]:
        """Refresh access token using refresh token with enhanced security.

        Args:
            refresh_token: Refresh token

        Returns:
            New token pair

        Raises:
            AuthenticationError: If refresh token is invalid
        """
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token") from None

        # Enhanced security validation
        jti = payload.get("jti")
        if jti:
            try:
                from chatter.core.token_manager import get_token_manager

                token_manager = await get_token_manager()

                # Check if token is blacklisted
                if await token_manager.is_token_blacklisted(jti):
                    raise AuthenticationError(
                        "Refresh token has been revoked"
                    ) from None

                # Use token manager for secure refresh
                return await token_manager.refresh_access_token(payload)

            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                raise AuthenticationError(
                    "Token refresh failed"
                ) from None

        # Fallback to basic refresh if token manager unavailable
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid refresh token") from None

        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError(
                "User not found or inactive"
            ) from None

        return self.create_tokens(user)

    async def list_api_keys(self, user_id: str) -> list[dict[str, Any]]:
        """List user's API keys."""
        try:
            # Get user with API key information
            from sqlalchemy import select

            from chatter.models.user import User

            result = await self.session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return []

            # Return API key information if exists
            api_keys = []
            if user.api_key and user.api_key_name:
                # Mask the actual API key for security
                masked_key = (
                    user.api_key[:8] + "..." + user.api_key[-4:]
                    if len(user.api_key) > 12
                    else "***"
                )
                api_keys.append(
                    {
                        "name": user.api_key_name,
                        "key_preview": masked_key,
                        "created_at": (
                            user.created_at.isoformat()
                            if user.created_at
                            else None
                        ),
                        "last_used": (
                            user.last_login_at.isoformat()
                            if user.last_login_at
                            else None
                        ),
                        "is_active": bool(user.api_key),
                    }
                )

            return api_keys

        except Exception as e:
            logger.error(
                f"Failed to list API keys for user {user_id}: {e}"
            )
            return []

    async def revoke_token(self, user_id: str) -> bool:
        """Revoke user's current tokens with enhanced security.

        Args:
            user_id: User ID

        Returns:
            True if successful
        """
        try:
            from chatter.core.token_manager import get_token_manager

            token_manager = await get_token_manager()
            revoked_count = await token_manager.revoke_all_user_tokens(
                user_id, "logout"
            )

            logger.info(
                f"Revoked {revoked_count} tokens for user",
                user_id=user_id,
            )
            return revoked_count > 0

        except Exception as e:
            logger.error(
                f"Token revocation failed: {e}", user_id=user_id
            )
            return False

    async def request_password_reset(self, email: str) -> bool:
        """Request password reset for user with enhanced security.

        Args:
            email: User email

        Returns:
            True (always, to prevent user enumeration)
        """
        # Always return success to prevent user enumeration attacks
        user = await self.get_user_by_email(email)

        if user and user.is_active:
            try:
                # Generate secure reset token
                import secrets

                reset_token = secrets.token_urlsafe(32)

                # Store token in cache with expiration (15 minutes)
                from chatter.core.cache_factory import get_general_cache

                cache_service = get_general_cache()

                health = await cache_service.health_check()
                if cache_service and health.get("status") == "healthy":
                    reset_data = {
                        "user_id": user.id,
                        "email": user.email,
                        "requested_at": datetime.now(UTC).isoformat(),
                        "ip_address": "unknown",  # Would be injected from request context
                    }

                    await cache_service.set(
                        f"password_reset:{reset_token}",
                        reset_data,
                        ttl=900,  # 15 minutes in seconds
                    )

                    # Here you would send the reset email
                    # await self.email_service.send_password_reset(user.email, reset_token)

                    logger.info(
                        "Password reset requested",
                        user_id=user.id,
                        email=user.email,
                        token_prefix=reset_token[:8] + "...",
                    )

            except Exception as e:
                logger.error(f"Password reset request failed: {e}")
        else:
            # Log attempt for security monitoring
            logger.warning(
                "Password reset requested for unknown/inactive user",
                email=email[:20] + "..." if len(email) > 20 else email,
            )

        # Always return True to prevent user enumeration
        return True

    async def confirm_password_reset(
        self, token: str, new_password: str
    ) -> bool:
        """Confirm password reset with token and enhanced security.

        Args:
            token: Reset token
            new_password: New password

        Returns:
            True if successful

        Raises:
            AuthenticationError: If token is invalid or expired
            BadRequestProblem: If password is invalid
        """
        try:
            # Validate token
            from chatter.core.cache_factory import get_general_cache

            cache_service = get_general_cache()

            health = await cache_service.health_check()
            if not cache_service or health.get("status") != "healthy":
                raise AuthenticationError(
                    "Password reset service unavailable"
                ) from None

            reset_data = await cache_service.get(
                f"password_reset:{token}"
            )
            if not reset_data:
                raise AuthenticationError(
                    "Invalid or expired reset token"
                ) from None

            # Validate new password with enhanced security
            password_validation = validate_password_advanced(
                new_password
            )
            if not password_validation["valid"]:
                raise BadRequestProblem(
                    detail="New password does not meet security requirements",
                    errors=password_validation["errors"],
                ) from None

            # Get user and validate
            user_id = reset_data["user_id"]
            user = await self.get_user_by_id(user_id)

            if not user or not user.is_active:
                raise AuthenticationError(
                    "Invalid reset request"
                ) from None

            # Check if new password contains personal information
            user_data_dict = {
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
            }
            if contains_personal_info(new_password, user_data_dict):
                raise BadRequestProblem(
                    detail="Password should not contain personal information"
                ) from None

            # Check if new password is same as current
            if verify_password(new_password, user.hashed_password):
                raise BadRequestProblem(
                    detail="New password must be different from current password"
                ) from None

            # Update password with enhanced hashing
            user.hashed_password = hash_password(new_password)
            await self.session.commit()

            # Invalidate reset token immediately
            await cache_service.delete(f"password_reset:{token}")

            # Revoke all existing tokens for security
            await self.revoke_token(user_id)

            logger.info(
                "Password reset completed successfully", user_id=user.id
            )

            return True

        except (AuthenticationError, BadRequestProblem):
            raise
        except Exception as e:
            logger.error(f"Password reset confirmation failed: {e}")
            raise AuthenticationError("Password reset failed") from None
