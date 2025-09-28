"""User preferences service for storing workflow and tool configurations.

This is a minimal implementation that stores preferences in memory.
TODO: Replace with proper database persistence using a UserPreferences table.
"""

from datetime import datetime
from typing import Any, Dict
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class UserPreferencesService:
    """Service for managing user preferences.
    
    This is a temporary in-memory implementation.
    TODO: Replace with database-backed implementation.
    """
    
    def __init__(self):
        # In-memory storage - should be replaced with database
        self._memory_preferences: Dict[str, Dict[str, Any]] = {}
        self._tool_preferences: Dict[str, Dict[str, Any]] = {}
    
    async def save_memory_config(
        self, 
        user_id: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save memory configuration for user.
        
        Args:
            user_id: User ID
            config: Memory configuration data
            
        Returns:
            Saved configuration with metadata
        """
        try:
            # Add metadata
            config_with_meta = {
                **config,
                "saved_at": datetime.now().isoformat(),
                "user_id": user_id,
            }
            
            # Store in memory (TODO: Replace with database)
            self._memory_preferences[user_id] = config_with_meta
            
            logger.info(f"Saved memory configuration for user {user_id}")
            return {
                "status": "success",
                "message": "Memory configuration saved",
                "config": config_with_meta
            }
            
        except Exception as e:
            logger.error(f"Failed to save memory config for user {user_id}: {e}")
            return {
                "status": "error",
                "message": f"Failed to save memory configuration: {str(e)}",
                "config": config
            }
    
    async def save_tool_config(
        self, 
        user_id: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save tool configuration for user.
        
        Args:
            user_id: User ID
            config: Tool configuration data
            
        Returns:
            Saved configuration with metadata
        """
        try:
            # Add metadata
            config_with_meta = {
                **config,
                "saved_at": datetime.now().isoformat(),
                "user_id": user_id,
            }
            
            # Store in memory (TODO: Replace with database)
            self._tool_preferences[user_id] = config_with_meta
            
            logger.info(f"Saved tool configuration for user {user_id}")
            return {
                "status": "success", 
                "message": "Tool configuration saved",
                "config": config_with_meta
            }
            
        except Exception as e:
            logger.error(f"Failed to save tool config for user {user_id}: {e}")
            return {
                "status": "error",
                "message": f"Failed to save tool configuration: {str(e)}",
                "config": config
            }
    
    async def get_memory_config(self, user_id: str) -> Dict[str, Any] | None:
        """Get memory configuration for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Memory configuration or None if not found
        """
        return self._memory_preferences.get(user_id)
    
    async def get_tool_config(self, user_id: str) -> Dict[str, Any] | None:
        """Get tool configuration for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Tool configuration or None if not found
        """
        return self._tool_preferences.get(user_id)


# Global service instance
_user_preferences_service: UserPreferencesService | None = None


def get_user_preferences_service() -> UserPreferencesService:
    """Get user preferences service instance."""
    global _user_preferences_service
    if _user_preferences_service is None:
        _user_preferences_service = UserPreferencesService()
    return _user_preferences_service