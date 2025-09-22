"""Centralized tool registry for unified tool management.

This registry provides a single source of truth for all available tools,
with proper validation, security, and metadata management.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    name: str
    description: str
    version: str = "1.0.0"
    category: str = "general"
    required_permissions: List[str] = field(default_factory=list)
    max_calls_per_session: Optional[int] = None
    timeout_seconds: int = 30
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    usage_count: int = 0


class ToolRegistry:
    """Centralized registry for all tools."""
    
    def __init__(self):
        self._tools: Dict[str, Any] = {}
        self._metadata: Dict[str, ToolMetadata] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def register_tool(
        self, 
        tool: Any, 
        metadata: ToolMetadata
    ) -> None:
        """Register a tool with metadata."""
        if metadata.name in self._tools:
            logger.warning(f"Tool {metadata.name} is already registered, overwriting")
        
        # Validate tool has required methods
        if not (hasattr(tool, 'ainvoke') or hasattr(tool, 'invoke') or callable(tool)):
            raise ValueError(f"Tool {metadata.name} must be callable or have invoke/ainvoke methods")
        
        self._tools[metadata.name] = tool
        self._metadata[metadata.name] = metadata
        
        # Update category index
        if metadata.category not in self._categories:
            self._categories[metadata.category] = []
        if metadata.name not in self._categories[metadata.category]:
            self._categories[metadata.category].append(metadata.name)
        
        logger.info(f"Registered tool: {metadata.name} (category: {metadata.category})")
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name."""
        tool = self._tools.get(name)
        if tool and name in self._metadata:
            # Update usage stats
            self._metadata[name].last_used = datetime.utcnow()
            self._metadata[name].usage_count += 1
        return tool
    
    def get_tools_for_workspace(
        self, 
        workspace_id: str,
        user_permissions: Optional[List[str]] = None
    ) -> List[Any]:
        """Get all tools available for a workspace with permission filtering."""
        available_tools = []
        user_permissions = user_permissions or []
        
        for name, tool in self._tools.items():
            metadata = self._metadata[name]
            
            # Check permissions
            if metadata.required_permissions:
                if not all(perm in user_permissions for perm in metadata.required_permissions):
                    logger.debug(f"Tool {name} filtered out due to insufficient permissions")
                    continue
            
            available_tools.append(tool)
        
        return available_tools
    
    def get_tools_by_category(self, category: str) -> List[Any]:
        """Get all tools in a specific category."""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_tool_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Get metadata for a tool."""
        return self._metadata.get(name)
    
    def list_all_tools(self) -> Dict[str, ToolMetadata]:
        """List all registered tools with their metadata."""
        return self._metadata.copy()
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool."""
        if name not in self._tools:
            return False
        
        metadata = self._metadata[name]
        
        # Remove from category index
        if metadata.category in self._categories:
            if name in self._categories[metadata.category]:
                self._categories[metadata.category].remove(name)
            if not self._categories[metadata.category]:
                del self._categories[metadata.category]
        
        # Remove tool and metadata
        del self._tools[name]
        del self._metadata[name]
        
        logger.info(f"Unregistered tool: {name}")
        return True
    
    def validate_tool_call(
        self, 
        tool_name: str, 
        args: Dict[str, Any],
        user_permissions: Optional[List[str]] = None
    ) -> bool:
        """Validate if a tool call is allowed."""
        if tool_name not in self._tools:
            logger.error(f"Tool {tool_name} not found in registry")
            return False
        
        metadata = self._metadata[tool_name]
        user_permissions = user_permissions or []
        
        # Check permissions
        if metadata.required_permissions:
            if not all(perm in user_permissions for perm in metadata.required_permissions):
                logger.warning(f"Tool {tool_name} call denied: insufficient permissions")
                return False
        
        # Check rate limits (basic implementation)
        if metadata.max_calls_per_session:
            # In a real implementation, this would check session-specific call counts
            if metadata.usage_count >= metadata.max_calls_per_session:
                logger.warning(f"Tool {tool_name} call denied: rate limit exceeded")
                return False
        
        return True
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all tools."""
        stats = {
            "total_tools": len(self._tools),
            "categories": {
                category: len(tools) 
                for category, tools in self._categories.items()
            },
            "most_used": [],
            "never_used": []
        }
        
        # Sort by usage count
        by_usage = sorted(
            self._metadata.items(), 
            key=lambda x: x[1].usage_count, 
            reverse=True
        )
        
        stats["most_used"] = [
            {"name": name, "usage_count": meta.usage_count}
            for name, meta in by_usage[:5]
            if meta.usage_count > 0
        ]
        
        stats["never_used"] = [
            name for name, meta in self._metadata.items()
            if meta.usage_count == 0
        ]
        
        return stats


# Global tool registry instance
tool_registry = ToolRegistry()


def register_builtin_tools() -> None:
    """Register built-in tools with the registry."""
    try:
        from chatter.core.dependencies import get_builtin_tools
        
        builtin_tools = get_builtin_tools()
        if builtin_tools:
            for tool in builtin_tools:
                # Extract tool name
                tool_name = (
                    getattr(tool, 'name', None) or
                    getattr(tool, 'name_', None) or
                    getattr(tool, '__name__', 'unknown_tool')
                )
                
                # Create metadata
                metadata = ToolMetadata(
                    name=tool_name,
                    description=getattr(tool, 'description', f"Built-in tool: {tool_name}"),
                    category="builtin",
                    version="1.0.0"
                )
                
                tool_registry.register_tool(tool, metadata)
                
        logger.info(f"Registered {len(builtin_tools or [])} built-in tools")
        
    except Exception as e:
        logger.error(f"Failed to register built-in tools: {e}")


# Auto-register built-in tools on import
register_builtin_tools()