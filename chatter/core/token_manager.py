"""Enhanced token management with proper security features."""

from datetime import UTC, datetime, timedelta
from typing import Any

from chatter.config import settings
from chatter.models.base import generate_ulid
from chatter.models.user import User
from chatter.utils.logging import get_logger
from chatter.utils.security_enhanced import (
    create_access_token,
    create_refresh_token,
)

logger = get_logger(__name__)


class TokenManager:
    """Enhanced token manager with blacklisting and security features."""

    def __init__(self, cache_service=None):
        """Initialize token manager with cache service."""
        self.cache = cache_service

    async def create_tokens(self, user: User) -> dict[str, Any]:
        """Create JWT tokens with proper security features.

        Args:
            user: User object

        Returns:
            Dictionary with tokens and metadata
        """
        # Generate unique JWT ID for tracking
        jti = generate_ulid()
        issued_at = datetime.now(UTC)

        # Create access token payload
        access_payload = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "jti": jti,
            "type": "access",
            "iat": issued_at,
            "permissions": await self._get_user_permissions(user),
            "session_id": generate_ulid(),  # Unique session identifier
        }

        # Create refresh token payload
        refresh_payload = {
            "sub": user.id,
            "jti": jti,
            "type": "refresh",
            "iat": issued_at,
            "session_id": access_payload["session_id"],
        }

        # Calculate expiration times
        access_expires = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        refresh_expires = timedelta(
            days=settings.refresh_token_expire_days
        )

        # Create tokens
        access_token = create_access_token(
            access_payload, access_expires
        )
        refresh_token = create_refresh_token(
            refresh_payload, refresh_expires
        )

        # Store token metadata for revocation tracking
        await self._store_token_metadata(
            jti, user.id, str(access_payload["session_id"])
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_expires.total_seconds()),
            "jti": jti,
            "session_id": access_payload["session_id"],
        }

    async def revoke_token(
        self, jti: str, reason: str = "logout"
    ) -> bool:
        """Properly revoke tokens by blacklisting.

        Args:
            jti: JWT ID to revoke
            reason: Reason for revocation

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.cache:
                logger.warning(
                    "No cache service available for token revocation"
                )
                return False

            # Add to blacklist with expiration (longest possible token lifetime)
            expire_time = timedelta(
                days=settings.refresh_token_expire_days
            )
            blacklist_data = {
                "revoked_at": datetime.now(UTC).isoformat(),
                "reason": reason,
                "jti": jti,
            }

            await self.cache.set(
                f"blacklist:{jti}", blacklist_data, int(expire_time.total_seconds())
            )

            # Remove token metadata
            await self.cache.delete(f"token_meta:{jti}")

            logger.info("Token revoked", jti=jti, reason=reason)
            return True

        except Exception as e:
            logger.error(f"Token revocation failed: {e}", jti=jti)
            return False

    async def revoke_all_user_tokens(
        self, user_id: str, reason: str = "security"
    ) -> int:
        """Revoke all tokens for a specific user.

        Args:
            user_id: User ID
            reason: Reason for revocation

        Returns:
            Number of tokens revoked
        """
        try:
            if not self.cache:
                return 0

            # Get all token metadata for user
            user_tokens = await self._get_user_tokens(user_id)
            revoked_count = 0

            for jti in user_tokens:
                if await self.revoke_token(jti, reason):
                    revoked_count += 1

            logger.info(
                f"Revoked {revoked_count} tokens for user",
                user_id=user_id,
                reason=reason,
            )
            return revoked_count

        except Exception as e:
            logger.error(
                f"Bulk token revocation failed: {e}", user_id=user_id
            )
            return 0

    async def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted.

        Args:
            jti: JWT ID to check

        Returns:
            True if blacklisted, False otherwise
        """
        try:
            if not self.cache:
                # Fail secure - if cache is down, consider token invalid
                logger.warning(
                    "No cache service available for blacklist check"
                )
                return True

            result = await self.cache.get(f"blacklist:{jti}")
            return result is not None

        except Exception as e:
            logger.error(f"Blacklist check failed: {e}", jti=jti)
            # Fail secure - if check fails, consider token invalid
            return True

    async def validate_token_security(
        self, token_payload: dict
    ) -> bool:
        """Validate token security properties.

        Args:
            token_payload: Decoded JWT payload

        Returns:
            True if token is valid and secure, False otherwise
        """
        try:
            # Check if token has required claims
            required_claims = ["sub", "jti", "iat", "exp", "type"]
            for claim in required_claims:
                if claim not in token_payload:
                    logger.warning(
                        f"Token missing required claim: {claim}"
                    )
                    return False

            # Check if token is blacklisted
            jti = token_payload.get("jti")
            if await self.is_token_blacklisted(jti):
                logger.info("Token is blacklisted", jti=jti)
                return False

            # Check token age
            issued_at = token_payload.get("iat")
            if issued_at:
                token_age = datetime.now(UTC) - datetime.fromtimestamp(
                    issued_at, UTC
                )
                max_age = timedelta(
                    days=settings.refresh_token_expire_days
                )

                if token_age > max_age:
                    logger.warning(
                        "Token is too old",
                        jti=jti,
                        age_days=token_age.days,
                    )
                    return False

            # Additional security checks can be added here

            return True

        except Exception as e:
            logger.error(f"Token security validation failed: {e}")
            return False

    async def refresh_access_token(
        self, refresh_token_payload: dict
    ) -> dict[str, Any]:
        """Refresh access token using refresh token.

        Args:
            refresh_token_payload: Decoded refresh token payload

        Returns:
            New token pair
        """
        # Validate refresh token security
        if not await self.validate_token_security(
            refresh_token_payload
        ):
            raise ValueError("Invalid refresh token")

        user_id = refresh_token_payload.get("sub")
        old_jti = refresh_token_payload.get("jti")
        session_id = refresh_token_payload.get("session_id")

        # Get user (this would need to be injected or accessed differently)
        # For now, we'll create a basic user object
        # This is a simplified version - in practice, you'd inject the auth service

        # Create new tokens with same session but new JTI
        new_jti = generate_ulid()
        issued_at = datetime.now(UTC)

        access_payload = {
            "sub": user_id,
            "jti": new_jti,
            "type": "access",
            "iat": issued_at,
            "session_id": session_id,
        }

        refresh_payload = {
            "sub": user_id,
            "jti": new_jti,
            "type": "refresh",
            "iat": issued_at,
            "session_id": session_id,
        }

        # Calculate expiration times
        access_expires = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        refresh_expires = timedelta(
            days=settings.refresh_token_expire_days
        )

        # Create new tokens
        new_access_token = create_access_token(
            access_payload, access_expires
        )
        new_refresh_token = create_refresh_token(
            refresh_payload, refresh_expires
        )

        # Revoke old tokens
        await self.revoke_token(old_jti, "token_refresh")

        # Store new token metadata
        await self._store_token_metadata(new_jti, user_id, session_id)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_expires.total_seconds()),
            "jti": new_jti,
        }

    async def _get_user_permissions(self, user: User) -> list[str]:
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

    async def _store_token_metadata(
        self, jti: str, user_id: str, session_id: str
    ):
        """Store token metadata for tracking.

        Args:
            jti: JWT ID
            user_id: User ID
            session_id: Session ID
        """
        try:
            if not self.cache:
                return

            metadata = {
                "user_id": user_id,
                "session_id": session_id,
                "created_at": datetime.now(UTC).isoformat(),
                "jti": jti,
            }

            # Store token metadata
            expire_time = timedelta(
                days=settings.refresh_token_expire_days
            )
            await self.cache.set(
                f"token_meta:{jti}", metadata, int(expire_time.total_seconds())
            )

            # Update user's active tokens list
            await self._add_to_user_tokens(user_id, jti)

        except Exception as e:
            logger.error(
                f"Failed to store token metadata: {e}", jti=jti
            )

    async def _add_to_user_tokens(self, user_id: str, jti: str):
        """Add token to user's active tokens list.

        Args:
            user_id: User ID
            jti: JWT ID
        """
        try:
            if not self.cache:
                return

            user_tokens_key = f"user_tokens:{user_id}"
            user_tokens = await self.cache.get(user_tokens_key) or []

            # Add new token and limit to last 10 tokens
            user_tokens.append(jti)
            user_tokens = user_tokens[-10:]  # Keep only last 10 tokens

            # Store updated list
            expire_time = timedelta(
                days=settings.refresh_token_expire_days
            )
            await self.cache.set(
                user_tokens_key, user_tokens, int(expire_time.total_seconds())
            )

        except Exception as e:
            logger.debug(f"Failed to update user tokens list: {e}")

    async def _get_user_tokens(self, user_id: str) -> list[str]:
        """Get list of active tokens for user.

        Args:
            user_id: User ID

        Returns:
            List of JWT IDs
        """
        try:
            if not self.cache:
                return []

            user_tokens_key = f"user_tokens:{user_id}"
            return await self.cache.get(user_tokens_key) or []

        except Exception as e:
            logger.debug(f"Failed to get user tokens: {e}")
            return []


# Singleton instance
_token_manager: TokenManager | None = None


async def get_token_manager():
    """Get token manager instance."""
    global _token_manager

    if _token_manager is None:
        try:
            from chatter.core.cache_factory import get_general_cache

            cache_service = get_general_cache()
            _token_manager = TokenManager(cache_service)
        except Exception as e:
            logger.warning(
                f"Failed to initialize token manager with cache: {e}"
            )
            _token_manager = TokenManager()

    return _token_manager
