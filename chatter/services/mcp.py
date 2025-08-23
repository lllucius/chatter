"""MCP (Model Context Protocol) service for tool calling integration."""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
    create_session,
)
from langchain_mcp_adapters.tools import (
    convert_mcp_tool_to_langchain_tool,
    load_mcp_tools,
)
from pydantic import BaseModel

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
    args: list[str]
    env: dict[str, str] | None = None


class MCPToolService:
    """Service for MCP tool calling integration."""

    def __init__(self) -> None:
        """Initialize MCP tool service."""
        self.enabled = settings.mcp_enabled
        self.servers: dict[str, MCPServer] = {}
        self.clients: dict[str, MultiServerMCPClient] = {}
        self.tools_cache: dict[str, list[BaseTool]] = {}

        if self.enabled:
            self._initialize_servers()

    def _initialize_servers(self) -> None:
        """Initialize MCP servers from configuration."""
        # Default MCP servers based on configuration
        default_servers = {
            "filesystem": MCPServer(
                name="filesystem",
                command="npx",
                args=[
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "/tmp",
                ],
                env=None,
            ),
            "browser": MCPServer(
                name="browser",
                command="npx",
                args=[
                    "-y",
                    "@modelcontextprotocol/server-brave-search",
                ],
                env={"BRAVE_API_KEY": "your_brave_api_key"},
            ),
            "calculator": MCPServer(
                name="calculator",
                command="python",
                args=["-m", "mcp_math_server"],
                env=None,
            ),
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
                env=server_config.env,
            )

            # Load tools from the session
            tools = await load_mcp_tools(session)

            # Convert to LangChain tools
            langchain_tools = []
            for tool in tools:
                lc_tool = convert_mcp_tool_to_langchain_tool(tool)
                langchain_tools.append(lc_tool)

            self.tools_cache[server_name] = langchain_tools

            logger.info(
                "MCP server started",
                server=server_name,
                tools_count=len(langchain_tools),
            )
            return True

        except Exception as e:
            logger.error(
                "Failed to start MCP server",
                server=server_name,
                error=str(e),
            )
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
            logger.error(
                "Failed to stop MCP server",
                server=server_name,
                error=str(e),
            )
            return False

    async def get_tools(
        self, server_names: list[str] | None = None
    ) -> list[BaseTool]:
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
                logger.debug(
                    "Retrieved tools from server",
                    server=server_name,
                    count=len(tools),
                )

        return all_tools

    async def get_tool_by_name(self, tool_name: str) -> BaseTool | None:
        """Get a specific tool by name."""
        all_tools = await self.get_tools()

        for tool in all_tools:
            if tool.name == tool_name:
                return tool

        return None

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        server_name: str | None = None,
        user_id: str | None = None,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """Call a specific MCP tool with usage tracking.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            server_name: Specific server name (optional)
            user_id: User ID for tracking
            conversation_id: Conversation ID for tracking

        Returns:
            Tool result with success/error information
        """
        start_time = time.time()
        tool = await self.get_tool_by_name(tool_name)

        if not tool:
            raise MCPServiceError(
                f"Tool not found: {tool_name}"
            ) from None

        # Find which server provides this tool
        found_server = None
        for server_name_check, tools in self.tools_cache.items():
            if any(t.name == tool_name for t in tools):
                found_server = server_name_check
                break

        if not found_server:
            raise MCPServiceError(
                f"Server not found for tool: {tool_name}"
            ) from None

        try:
            result = await tool.arun(arguments)
            response_time_ms = (time.time() - start_time) * 1000

            # Track usage (async, don't block)
            asyncio.create_task(
                self._track_tool_usage(
                    found_server,
                    tool_name,
                    arguments,
                    result,
                    response_time_ms,
                    True,
                    None,
                    user_id,
                    conversation_id,
                )
            )

            return {
                "success": True,
                "result": result,
                "tool": tool_name,
                "server": found_server,
                "response_time_ms": response_time_ms,
            }
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            error_msg = str(e)

            logger.error(
                "Tool call failed",
                tool=tool_name,
                server=found_server,
                error=error_msg,
            )

            # Track usage error (async, don't block)
            asyncio.create_task(
                self._track_tool_usage(
                    found_server,
                    tool_name,
                    arguments,
                    None,
                    response_time_ms,
                    False,
                    error_msg,
                    user_id,
                    conversation_id,
                )
            )

            return {
                "success": False,
                "error": error_msg,
                "tool": tool_name,
                "server": found_server,
                "response_time_ms": response_time_ms,
            }

    async def _track_tool_usage(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any],
        result: Any,
        response_time_ms: float,
        success: bool,
        error_message: str | None,
        user_id: str | None,
        conversation_id: str | None,
    ) -> None:
        """Track tool usage in the database.

        Args:
            server_name: Server name
            tool_name: Tool name
            arguments: Tool arguments
            result: Tool result
            response_time_ms: Response time in milliseconds
            success: Whether the call was successful
            error_message: Error message if failed
            user_id: User ID
            conversation_id: Conversation ID
        """
        try:
            from chatter.schemas.toolserver import ToolUsageCreate
            from chatter.services.toolserver import ToolServerService
            from chatter.utils.database import get_session_factory

            # Get database session
            async_session = get_session_factory()
            async with async_session() as session:
                tool_server_service = ToolServerService(session)

                # Find server by name
                server = await tool_server_service.get_server_by_name(
                    server_name
                )
                if not server:
                    logger.warning(
                        "Server not found for usage tracking",
                        server_name=server_name,
                    )
                    return

                # Create usage record
                usage_data = ToolUsageCreate(
                    tool_name=tool_name,
                    arguments=arguments,
                    result={"data": result}
                    if result is not None
                    else None,
                    response_time_ms=response_time_ms,
                    success=success,
                    error_message=error_message,
                    user_id=user_id,
                    conversation_id=conversation_id,
                )

                await tool_server_service.record_tool_usage(
                    server.id, tool_name, usage_data
                )

        except Exception as e:
            logger.error("Failed to track tool usage", error=str(e))
            # Don't raise - usage tracking shouldn't break tool calls

    def create_custom_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        args_schema: BaseModel | None = None,
    ) -> BaseTool:
        """Create a custom tool for integration."""
        return StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
            args_schema=args_schema,
        )

    async def get_available_servers(self) -> list[dict[str, Any]]:
        """Get list of available MCP servers."""
        servers_info = []

        for server_name, server_config in self.servers.items():
            is_running = server_name in self.tools_cache
            tools_count = len(self.tools_cache.get(server_name, []))

            servers_info.append(
                {
                    "name": server_name,
                    "command": server_config.command,
                    "args": server_config.args,
                    "running": is_running,
                    "tools_count": tools_count,
                }
            )

        return servers_info

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on MCP service."""
        if not self.enabled:
            return {"enabled": False, "status": "disabled"}

        server_status = {}
        total_tools = 0

        for server_name in self.servers:
            is_running = server_name in self.tools_cache
            tools_count = len(self.tools_cache.get(server_name, []))

            server_status[server_name] = {
                "running": is_running,
                "tools_count": tools_count,
            }
            total_tools += tools_count

        return {
            "enabled": True,
            "status": "healthy" if total_tools > 0 else "no_tools",
            "servers": server_status,
            "total_tools": total_tools,
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
    def calculate(expression: str) -> float | str:
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
                """Safely evaluate an AST node."""
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    return ops[type(node.op)](
                        eval_expr(node.left), eval_expr(node.right)
                    )
                elif isinstance(node, ast.UnaryOp):
                    return ops[type(node.op)](eval_expr(node.operand))
                else:
                    raise TypeError(node) from None

            return eval_expr(ast.parse(expression, mode="eval").body)
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def create_builtin_tools() -> list[BaseTool]:
        """Create built-in tools."""
        tools = []

        # Time tool
        time_tool = StructuredTool.from_function(
            func=BuiltInTools.get_current_time,
            name="get_current_time",
            description="Get the current date and time in ISO format",
        )
        tools.append(time_tool)

        # Calculator tool
        calc_tool = StructuredTool.from_function(
            func=BuiltInTools.calculate,
            name="calculate",
            description="Calculate a mathematical expression (supports +, -, *, /, **)",
        )
        tools.append(calc_tool)

        return tools


# Global MCP service instance
mcp_service = MCPToolService()
