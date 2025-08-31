"""Core chat service - DEPRECATED

MIGRATION NOTICE:
The original ChatService has been replaced by RefactoredChatService.
Please use: from chatter.services.chat_refactored import RefactoredChatService

The legacy ChatService implementation has been moved to chat_backup.py
for reference purposes only.
"""

from __future__ import annotations


class ChatError(Exception):
    """Chat error for invalid operations or failed processing."""


class ConversationNotFoundError(Exception):
    """Raised when a conversation is not found or inaccessible."""


# For backward compatibility during transition period
def _deprecated_import_warning():
    """Issue deprecation warning for ChatService imports."""
    import warnings
    warnings.warn(
        "ChatService is deprecated. Use RefactoredChatService from "
        "chatter.services.chat_refactored instead.",
        DeprecationWarning,
        stacklevel=3
    )


class ChatService:
    """DEPRECATED: Use RefactoredChatService instead."""
    
    def __init__(self, *args, **kwargs):
        _deprecated_import_warning()
        raise NotImplementedError(
            "ChatService is deprecated. Use RefactoredChatService from "
            "chatter.services.chat_refactored instead."
        )
