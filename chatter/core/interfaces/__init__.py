"""Core interfaces for breaking circular dependencies."""

from .tool_service import ToolServiceInterface, ToolServerInterface

__all__ = ["ToolServiceInterface", "ToolServerInterface"]