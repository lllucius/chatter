"""Abstract interfaces for tool services to break circular dependencies."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ToolInfo:
    """Tool information structure."""
    name: str
    description: str
    parameters: Dict[str, Any]
    tool_type: str


class ToolServiceInterface(ABC):
    """Abstract interface for MCP tool services."""
    
    @abstractmethod
    async def get_tools(self, server_names: Optional[List[str]] = None) -> List[Any]:
        """Get available tools.
        
        Args:
            server_names: Optional list of server names to filter tools
            
        Returns:
            List of available tools
        """
        pass
    
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        pass
    
    @abstractmethod
    async def register_external_tools(self, tools: List[ToolInfo]) -> None:
        """Register external tools.
        
        Args:
            tools: List of tools to register
        """
        pass


class ToolServerInterface(ABC):
    """Abstract interface for tool server management."""
    
    @abstractmethod
    async def register_tool_server(
        self, 
        name: str, 
        config: Dict[str, Any]
    ) -> bool:
        """Register a new tool server.
        
        Args:
            name: Server name
            config: Server configuration
            
        Returns:
            True if registration successful
        """
        pass
    
    @abstractmethod
    async def get_server_tools(self, server_name: str) -> List[ToolInfo]:
        """Get tools from a specific server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            List of tools from the server
        """
        pass
    
    @abstractmethod
    async def health_check(self, server_name: str) -> bool:
        """Check if a server is healthy.
        
        Args:
            server_name: Name of the server to check
            
        Returns:
            True if server is healthy
        """
        pass