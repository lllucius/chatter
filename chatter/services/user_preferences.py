"""User preferences service for storing workflow and tool configurations.

Database-backed implementation for persistent user preferences storage.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.user_preference import UserPreference
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class UserPreferencesService:
    """Service for managing user preferences.

    Database-backed implementation with support for memory and tool configurations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize service with database session.
        
        Args:
            session: Async database session
        """
        self.session = session

    async def save_memory_config(
        self, user_id: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Save memory configuration for user.

        Args:
            user_id: User ID
            config: Memory configuration data

        Returns:
            Saved configuration with metadata
        """
        try:
            # Check if preference already exists
            stmt = select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == "memory",
            )
            result = await self.session.execute(stmt)
            preference = result.scalar_one_or_none()

            if preference:
                # Update existing preference
                preference.config = config
                preference.updated_at = datetime.now()
            else:
                # Create new preference
                preference = UserPreference(
                    user_id=user_id,
                    preference_type="memory",
                    config=config,
                )
                self.session.add(preference)

            await self.session.commit()
            await self.session.refresh(preference)

            logger.info(
                f"Saved memory configuration for user {user_id}"
            )
            return {
                "status": "success",
                "message": "Memory configuration saved",
                "config": preference.config,
                "saved_at": preference.updated_at.isoformat(),
            }

        except Exception as e:
            await self.session.rollback()
            logger.error(
                f"Failed to save memory config for user {user_id}: {e}"
            )
            return {
                "status": "error",
                "message": f"Failed to save memory configuration: {str(e)}",
                "config": config,
            }

    async def save_tool_config(
        self, user_id: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Save tool configuration for user.

        Args:
            user_id: User ID
            config: Tool configuration data

        Returns:
            Saved configuration with metadata
        """
        try:
            # Check if preference already exists
            stmt = select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == "tool",
            )
            result = await self.session.execute(stmt)
            preference = result.scalar_one_or_none()

            if preference:
                # Update existing preference
                preference.config = config
                preference.updated_at = datetime.now()
            else:
                # Create new preference
                preference = UserPreference(
                    user_id=user_id,
                    preference_type="tool",
                    config=config,
                )
                self.session.add(preference)

            await self.session.commit()
            await self.session.refresh(preference)

            logger.info(f"Saved tool configuration for user {user_id}")
            return {
                "status": "success",
                "message": "Tool configuration saved",
                "config": preference.config,
                "saved_at": preference.updated_at.isoformat(),
            }

        except Exception as e:
            await self.session.rollback()
            logger.error(
                f"Failed to save tool config for user {user_id}: {e}"
            )
            return {
                "status": "error",
                "message": f"Failed to save tool configuration: {str(e)}",
                "config": config,
            }

    async def get_memory_config(
        self, user_id: str
    ) -> dict[str, Any] | None:
        """Get memory configuration for user.

        Args:
            user_id: User ID

        Returns:
            Memory configuration or None if not found
        """
        try:
            stmt = select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == "memory",
            )
            result = await self.session.execute(stmt)
            preference = result.scalar_one_or_none()
            
            if preference:
                return preference.config
            return None
            
        except Exception as e:
            logger.error(
                f"Failed to get memory config for user {user_id}: {e}"
            )
            return None

    async def get_tool_config(
        self, user_id: str
    ) -> dict[str, Any] | None:
        """Get tool configuration for user.

        Args:
            user_id: User ID

        Returns:
            Tool configuration or None if not found
        """
        try:
            stmt = select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == "tool",
            )
            result = await self.session.execute(stmt)
            preference = result.scalar_one_or_none()
            
            if preference:
                return preference.config
            return None
            
        except Exception as e:
            logger.error(
                f"Failed to get tool config for user {user_id}: {e}"
            )
            return None
