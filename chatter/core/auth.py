"""Authentication service for user management."""

from datetime import UTC, datetime, timedelta

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
from chatter.utils.security import (
    create_access_token,
    create_refresh_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    validate_email,
    validate_password_strength,
    verify_api_key,
    verify_password,
    verify_token,
)

logger = get_logger(__name__)


# Use RFC 9457 compliant problem classes instead of HTTPException subclasses
AuthenticationError = AuthenticationProblem
AuthorizationError = AuthorizationProblem


def UserAlreadyExistsError(detail="User already exists"):
    return ConflictProblem(detail=detail, conflicting_resource="user")


def UserNotFoundError(detail="User not found"):
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
        """Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user

        Raises:
            UserAlreadyExistsError: If user already exists
            HTTPException: If validation fails
        """
        # Validate email format
        if not validate_email(user_data.email):
            raise BadRequestProblem(
                detail="Invalid email format"
            ) from None

        # Validate password strength
        password_validation = validate_password_strength(
            user_data.password
        )
        if not password_validation["valid"]:
            raise BadRequestProblem(
                detail="Password does not meet requirements",
                errors=password_validation["errors"],
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

        # Create user
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
        """Authenticate user with userid and password.

        Args:
            username: User username
            password: User password

        Returns:
            User if authentication successful, None otherwise
        """
        user = await self.get_user_by_username(username)
        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(user)

        logger.info(
            "User authenticated", user_id=user.id, username=user.username
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
            from chatter.services.cache import get_cache_service
            cache_service = await get_cache_service()
            
            if cache_service.is_connected():
                cache_key = f"user:{user_id}"
                cached_user = await cache_service.get(cache_key)
                if cached_user:
                    # Convert back to User object (simplified caching)
                    logger.debug("User found in cache", user_id=user_id)
                    # For now, fall through to database - can enhance later
        except Exception as cache_error:
            logger.debug("Cache lookup failed, using database", 
                        user_id=user_id, error=str(cache_error))
        
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        # Cache the result for future lookups
        if user:
            try:
                from chatter.services.cache import get_cache_service
                from datetime import timedelta
                
                cache_service = await get_cache_service()
                if cache_service.is_connected():
                    cache_key = f"user:{user_id}"
                    # Cache for 15 minutes
                    await cache_service.set(cache_key, "cached", timedelta(minutes=15))
                    logger.debug("User cached", user_id=user_id)
            except Exception as cache_error:
                logger.debug("Cache storage failed", 
                            user_id=user_id, error=str(cache_error))
        
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
        return result.scalar_one_or_none()

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
        return result.scalar_one_or_none()

    async def get_user_by_api_key(self, api_key: str) -> User | None:
        """Get user by API key.

        Args:
            api_key: API key (plaintext)

        Returns:
            User if found and API key is valid, None otherwise
        """
        # Get all users with API keys to verify the hash
        result = await self.session.execute(
            select(User).where(User.api_key.isnot(None))
        )
        users_with_keys = result.scalars().all()

        # Check each user's hashed API key
        for user in users_with_keys:
            if user.api_key and verify_api_key(api_key, user.api_key):
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
        """Change user password.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully

        Raises:
            UserNotFoundError: If user not found
            AuthenticationError: If current password is invalid
            HTTPException: If new password is invalid
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError() from None

        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationError(
                "Current password is incorrect"
            ) from None

        # Validate new password
        password_validation = validate_password_strength(new_password)
        if not password_validation["valid"]:
            raise BadRequestProblem(
                detail="New password does not meet requirements",
                errors=password_validation["errors"],
            ) from None

        # Update password
        user.hashed_password = hash_password(new_password)
        await self.session.commit()
        await self.session.refresh(user)

        logger.info("Password changed", user_id=user.id)
        return True

    async def create_api_key(self, user_id: str, key_name: str) -> str:
        """Create API key for user.

        Args:
            user_id: User ID
            key_name: API key name

        Returns:
            Generated API key (plaintext, only returned once)

        Raises:
            UserNotFoundError: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError() from None

        # Generate API key and hash it before storage
        api_key = generate_api_key()
        hashed_api_key = hash_api_key(api_key)

        # Store only the hash in the database
        user.api_key = hashed_api_key
        user.api_key_name = key_name

        await self.session.commit()
        await self.session.refresh(user)

        logger.info(
            "API key created", user_id=user.id, key_name=key_name
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

    def create_tokens(self, user: User) -> dict:
        """Create access and refresh tokens for user.

        Args:
            user: User object

        Returns:
            Dictionary with tokens and expiration info
        """
        access_token_expires = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        refresh_token_expires = timedelta(
            days=settings.refresh_token_expire_days
        )

        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires,
        )

        refresh_token = create_refresh_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=refresh_token_expires,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
        }

    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token.

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

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token.

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

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid refresh token") from None

        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError(
                "User not found or inactive"
            ) from None

        return self.create_tokens(user)
