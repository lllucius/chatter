"""MCP (Model Context Protocol) service for tool calling integration."""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field
from langchain_mcp_adapters.tools import load_mcp_tools, convert_mcp_tool_to_langchain_tool
from langchain_mcp_adapters.client import create_session, MultiServerMCPClient
from mcp import StdioServerParameters

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class MCPServiceError(Exception):
    """MCP service error."""
    pass


@dataclass
class MCPServer:
    """MCP server configuration."""
    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None


class MCPToolService:
    """Service for MCP tool calling integration."""
    
    def __init__(self):
        """Initialize MCP tool service."""
        self.enabled = settings.mcp_enabled
        self.servers: Dict[str, MCPServer] = {}
        self.clients: Dict[str, MultiServerMCPClient] = {}
        self.tools_cache: Dict[str, List[BaseTool]] = {}
        
        if self.enabled:
            self._initialize_servers()
    
    def _initialize_servers(self) -> None:
        """Initialize MCP servers from configuration."""
        # Default MCP servers based on configuration
        default_servers = {
            "filesystem": MCPServer(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                env=None
            ),
            "browser": MCPServer(
                name="browser",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-brave-search"],
                env={"BRAVE_API_KEY": "your_brave_api_key"}
            ),
            "calculator": MCPServer(
                name="calculator",
                command="python",
                args=["-m", "mcp_math_server"],
                env=None
            )
        }
        
        # Initialize configured servers
        for server_name in settings.mcp_servers:
            if server_name in default_servers:
                self.servers[server_name] = default_servers[server_name]
                logger.info("MCP server configured", server=server_name)
    
    async def start_server(self, server_name: str) -> bool:
        """Start an MCP server."""
        if not self.enabled or server_name not in self.servers:
            return False
        
        server_config = self.servers[server_name]
        
        try:
            # Create session for the server
            session = await create_session(
                command=server_config.command,
                args=server_config.args,
                env=server_config.env
            )
            
            # Load tools from the session
            tools = await load_mcp_tools(session)
            
            # Convert to LangChain tools
            langchain_tools = []
            for tool in tools:
                lc_tool = convert_mcp_tool_to_langchain_tool(tool)
                langchain_tools.append(lc_tool)
            
            self.tools_cache[server_name] = langchain_tools
            
            logger.info("MCP server started", server=server_name, tools_count=len(langchain_tools))
            return True
            
        except Exception as e:
            logger.error("Failed to start MCP server", server=server_name, error=str(e))
            return False
    
    async def stop_server(self, server_name: str) -> bool:
        """Stop an MCP server."""
        if server_name not in self.clients:
            return False
        
        try:
            # Clean up
            if server_name in self.clients:
                del self.clients[server_name]
            if server_name in self.tools_cache:
                del self.tools_cache[server_name]
            
            logger.info("MCP server stopped", server=server_name)
            return True
            
        except Exception as e:
            logger.error("Failed to stop MCP server", server=server_name, error=str(e))
            return False
    
    async def get_tools(self, server_names: Optional[List[str]] = None) -> List[BaseTool]:
        """Get tools from specified MCP servers."""
        if not self.enabled:
            return []
        
        if server_names is None:
            server_names = list(self.servers.keys())
        
        all_tools = []
        
        for server_name in server_names:
            if server_name not in self.tools_cache:
                # Try to start the server
                await self.start_server(server_name)
            
            if server_name in self.tools_cache:
                tools = self.tools_cache[server_name]
                all_tools.extend(tools)
                logger.debug("Retrieved tools from server", server=server_name, count=len(tools))
        
        return all_tools
    
    async def get_tool_by_name(self, tool_name: str) -> Optional[BaseTool]:
        """Get a specific tool by name."""
        all_tools = await self.get_tools()
        
        for tool in all_tools:
            if tool.name == tool_name:
                return tool
        
        return None
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        server_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call a specific MCP tool."""
        tool = await self.get_tool_by_name(tool_name)
        
        if not tool:
            raise MCPServiceError(f"Tool not found: {tool_name}")
        
        try:
            result = await tool.arun(arguments)
            return {
                "success": True,
                "result": result,
                "tool": tool_name
            }
        except Exception as e:
            logger.error("Tool call failed", tool=tool_name, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    def create_custom_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        args_schema: Optional[BaseModel] = None
    ) -> BaseTool:
        """Create a custom tool for integration."""
        return StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
            args_schema=args_schema
        )
    
    async def get_available_servers(self) -> List[Dict[str, Any]]:
        """Get list of available MCP servers."""
        servers_info = []
        
        for server_name, server_config in self.servers.items():
            is_running = server_name in self.tools_cache
            tools_count = len(self.tools_cache.get(server_name, []))
            
            servers_info.append({
                "name": server_name,
                "command": server_config.command,
                "args": server_config.args,
                "running": is_running,
                "tools_count": tools_count
            })
        
        return servers_info
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on MCP service."""
        if not self.enabled:
            return {
                "enabled": False,
                "status": "disabled"
            }
        
        server_status = {}
        total_tools = 0
        
        for server_name in self.servers:
            is_running = server_name in self.tools_cache
            tools_count = len(self.tools_cache.get(server_name, []))
            
            server_status[server_name] = {
                "running": is_running,
                "tools_count": tools_count
            }
            total_tools += tools_count
        
        return {
            "enabled": True,
            "status": "healthy" if total_tools > 0 else "no_tools",
            "servers": server_status,
            "total_tools": total_tools
        }
    
    async def restart_all_servers(self) -> bool:
        """Restart all MCP servers."""
        success = True
        
        # Stop all servers
        for server_name in list(self.tools_cache.keys()):
            if not await self.stop_server(server_name):
                success = False
        
        # Start all configured servers
        for server_name in self.servers:
            if not await self.start_server(server_name):
                success = False
        
        return success


# Built-in tools that don't require MCP servers
class BuiltInTools:
    """Built-in tools for common operations."""
    
    @staticmethod
    def get_current_time() -> str:
        """Get the current time."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    @staticmethod
    def calculate(expression: str) -> Union[float, str]:
        """Calculate a mathematical expression safely."""
        try:
            # Safe evaluation of mathematical expressions
            import ast
            import operator
            
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return ops[type(node.op)](eval_expr(node.operand))
                else:
                    raise TypeError(node)
            
            return eval_expr(ast.parse(expression, mode='eval').body)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def create_builtin_tools() -> List[BaseTool]:
        """Create built-in tools."""
        tools = []
        
        # Time tool
        time_tool = StructuredTool.from_function(
            func=BuiltInTools.get_current_time,
            name="get_current_time",
            description="Get the current date and time in ISO format"
        )
        tools.append(time_tool)
        
        # Calculator tool
        calc_tool = StructuredTool.from_function(
            func=BuiltInTools.calculate,
            name="calculate",
            description="Calculate a mathematical expression (supports +, -, *, /, **)"
        )
        tools.append(calc_tool)
        
        return tools


# Global MCP service instance
mcp_service = MCPToolService()