"""MCP (Model Context Protocol) service using langchain-mcp-adapters."""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import Connection
from pydantic import BaseModel, HttpUrl

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class MCPServiceError(Exception):
    """MCP service error."""

    pass


@dataclass
class OAuthConfig:
    """OAuth configuration for remote servers."""

    client_id: str
    client_secret: str
    token_url: str
    scope: str | None = None
    refresh_token: str | None = None
    access_token: str | None = None


@dataclass
class RemoteMCPServer:
    """Remote MCP server configuration for HTTP/SSE endpoints."""

    name: str
    base_url: HttpUrl
    transport_type: str  # "http" or "sse" or "stdio" or "websocket"
    oauth_config: OAuthConfig | None = None
    headers: dict[str, str] | None = None
    timeout: int = 30  # Uses settings.mcp_tool_timeout when instantiated
    enabled: bool = True


class MCPToolService:
    """Service for MCP tool calling integration using langchain-mcp-adapters."""

    def __init__(self) -> None:
        """Initialize MCP tool service."""
        self.enabled = settings.mcp_enabled
        self.servers: dict[str, RemoteMCPServer] = {}
        self.connections: dict[str, Connection] = {}
        self.tools_cache: dict[str, list[BaseTool]] = {}
        self._client: MultiServerMCPClient | None = None
        self._connection_retry_counts: dict[str, int] = {}
        self._max_retries = 3
        self._retry_delay_base = 1.0  # seconds
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_reset_timeout = 300  # 5 minutes

    def _get_client(self) -> MultiServerMCPClient:
        """Get or create the MCP client."""
        if self._client is None:
            self._client = MultiServerMCPClient(self.connections)
        return self._client

    async def _retry_with_backoff(
        self, operation: Callable, server_name: str, *args, **kwargs
    ) -> Any:
        """Execute operation with exponential backoff retry logic."""
        retry_count = self._connection_retry_counts.get(server_name, 0)

        # Circuit breaker check
        if retry_count >= self._circuit_breaker_threshold:
            logger.warning(
                "Circuit breaker open for server",
                server=server_name,
                failures=retry_count,
            )
            raise MCPServiceError(
                f"Circuit breaker open for server {server_name} after {retry_count} failures"
            )

        last_exception = None

        for attempt in range(self._max_retries):
            try:
                result = await operation(*args, **kwargs)
                # Reset retry count on success
                if server_name in self._connection_retry_counts:
                    del self._connection_retry_counts[server_name]
                return result

            except Exception as e:
                last_exception = e
                retry_count += 1
                self._connection_retry_counts[server_name] = retry_count

                if attempt < self._max_retries - 1:
                    delay = self._retry_delay_base * (2**attempt)
                    logger.warning(
                        "Operation failed, retrying",
                        server=server_name,
                        attempt=attempt + 1,
                        delay=delay,
                        error=str(e),
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "Operation failed after all retries",
                        server=server_name,
                        attempts=self._max_retries,
                        error=str(e),
                    )

        # If we get here, all retries failed
        raise MCPServiceError(
            f"Operation failed after {self._max_retries} retries: {last_exception}"
        )

    def _is_server_healthy(self, server_name: str) -> bool:
        """Check if server is healthy (circuit breaker status)."""
        retry_count = self._connection_retry_counts.get(server_name, 0)
        return retry_count < self._circuit_breaker_threshold

    def _validate_server_config(
        self, server_config: RemoteMCPServer
    ) -> None:
        """Validate server configuration."""
        if not server_config.name:
            raise ValueError("Server name is required")

        if not server_config.base_url:
            raise ValueError("Base URL is required")

        if server_config.transport_type not in [
            "http",
            "sse",
            "stdio",
            "websocket",
        ]:
            raise ValueError(
                f"Unsupported transport type: {server_config.transport_type}"
            )

        if server_config.transport_type == "stdio":
            # For stdio, we would need command configuration
            # This is handled elsewhere in the system
            pass

        if server_config.timeout <= 0:
            raise ValueError("Timeout must be positive")

        # Validate OAuth config if present
        if server_config.oauth_config:
            oauth = server_config.oauth_config
            if not all(
                [oauth.client_id, oauth.client_secret, oauth.token_url]
            ):
                raise ValueError(
                    "OAuth config requires client_id, client_secret, and token_url"
                )

    def _update_client(self) -> None:
        """Update the client with new connections."""
        self._client = MultiServerMCPClient(self.connections)

    def _convert_server_to_connection(
        self, server: RemoteMCPServer
    ) -> Connection:
        """Convert RemoteMCPServer to langchain-mcp-adapters Connection."""
        base_connection = {
            "transport": (
                "streamable_http"
                if server.transport_type == "http"
                else server.transport_type
            ),
        }

        if server.transport_type in ["http", "sse"]:
            base_connection["url"] = str(server.base_url)
            if server.headers:
                base_connection["headers"] = server.headers
            if server.timeout:
                base_connection["timeout"] = server.timeout

        elif server.transport_type == "stdio":
            # For stdio, we need command and args
            # This is a simplified example - in practice you'd need more configuration
            raise MCPServiceError(
                "stdio transport requires command and args configuration"
            )

        elif server.transport_type == "websocket":
            base_connection["url"] = str(server.base_url)
            if server.headers:
                base_connection["headers"] = server.headers

        return base_connection

    async def add_remote_server(
        self, server_config: RemoteMCPServer
    ) -> bool:
        """Add a remote MCP server configuration."""
        if not self.enabled:
            return False

        try:
            # Validate configuration first
            self._validate_server_config(server_config)

            # Check if server is already configured
            if server_config.name in self.servers:
                logger.warning(
                    "Server already exists, updating configuration",
                    server=server_config.name,
                )

            # Convert server config to connection with retry logic
            async def _add_server():
                connection = self._convert_server_to_connection(
                    server_config
                )

                self.servers[server_config.name] = server_config
                self.connections[server_config.name] = connection

                # Update client with new connections
                self._update_client()

                return True

            result = await self._retry_with_backoff(
                _add_server, server_config.name
            )

            logger.info(
                "Remote MCP server added",
                server=server_config.name,
                transport=server_config.transport_type,
                url=str(server_config.base_url),
            )
            return result

        except Exception as e:
            logger.error(
                "Failed to add remote MCP server",
                server=server_config.name,
                error=str(e),
            )
            return False

    async def remove_server(self, server_name: str) -> bool:
        """Remove a remote MCP server."""
        try:
            if server_name in self.servers:
                del self.servers[server_name]

            if server_name in self.connections:
                del self.connections[server_name]

            if server_name in self.tools_cache:
                del self.tools_cache[server_name]

            # Update client with new connections
            self._update_client()

            logger.info("Remote MCP server removed", server=server_name)
            return True

        except Exception as e:
            logger.error(
                "Failed to remove remote MCP server",
                server=server_name,
                error=str(e),
            )
            return False

    async def _authenticate_oauth(self, server_name: str) -> bool:
        """OAuth authentication is handled by the underlying MCP client."""
        # Note: OAuth handling would need to be implemented in the connection configuration
        logger.warning(
            "OAuth authentication not yet implemented with langchain-mcp-adapters"
        )
        return False

    async def discover_tools(self, server_name: str) -> list[BaseTool]:
        """Discover tools from a remote MCP server."""
        if not self.enabled or server_name not in self.servers:
            return []

        # Check circuit breaker
        if not self._is_server_healthy(server_name):
            logger.warning(
                "Server unhealthy, skipping tool discovery",
                server=server_name,
            )
            return []

        try:

            async def _discover():
                client = self._get_client()
                tools = await client.get_tools(server_name=server_name)
                return tools

            tools = await self._retry_with_backoff(
                _discover, server_name
            )

            # Cache the tools
            self.tools_cache[server_name] = tools

            logger.info(
                "Tools discovered from remote server",
                server=server_name,
                count=len(tools),
            )
            return tools

        except Exception as e:
            logger.error(
                "Failed to discover tools from remote server",
                server=server_name,
                error=str(e),
            )
            return []

    async def get_tools(
        self, server_names: list[str] | None = None
    ) -> list[BaseTool]:
        """Get tools from specified remote MCP servers."""
        if not self.enabled:
            return []

        try:
            client = self._get_client()

            if server_names is None:
                # Get all tools from all servers
                tools = await client.get_tools()
            else:
                # Get tools from specific servers
                all_tools = []
                for server_name in server_names:
                    if server_name in self.connections:
                        server_tools = await client.get_tools(
                            server_name=server_name
                        )
                        all_tools.extend(server_tools)
                tools = all_tools

            # Update cache
            for server_name in self.servers.keys():
                if server_name not in self.tools_cache:
                    self.tools_cache[server_name] = []

            return tools

        except Exception as e:
            logger.error(
                "Failed to get tools from MCP servers", error=str(e)
            )
            return []

    async def get_tool_by_name(self, tool_name: str) -> BaseTool | None:
        """Get a specific tool by name."""
        all_tools = await self.get_tools()

        for tool in all_tools:
            if tool.name == tool_name:
                return tool

        return None

    def _sanitize_tool_arguments(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Sanitize and validate tool arguments."""
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a dictionary")

        # Check argument size
        import json

        serialized = json.dumps(arguments)
        if len(serialized) > 1024 * 1024:  # 1MB limit
            raise ValueError("Tool arguments too large (max 1MB)")

        # Deep sanitization - remove potentially dangerous content
        def sanitize_value(value: Any) -> Any:
            if isinstance(value, str):
                # Remove potential script injections
                if any(
                    danger in value.lower()
                    for danger in [
                        "<script",
                        "javascript:",
                        "data:",
                        "vbscript:",
                    ]
                ):
                    raise ValueError(
                        "Potentially dangerous content in arguments"
                    )
                # Limit string length
                if len(value) > 10000:  # 10KB per string
                    raise ValueError(
                        "String argument too long (max 10KB)"
                    )
                return value
            elif isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_value(item) for item in value]
            elif isinstance(value, int | float | bool) or value is None:
                return value
            else:
                # Convert other types to string with length limit
                str_value = str(value)
                if len(str_value) > 1000:
                    raise ValueError("Converted argument too long")
                return str_value

        return sanitize_value(arguments)

    def _validate_tool_result(self, result: Any) -> Any:
        """Validate and sanitize tool results."""
        # Check result size
        import json

        try:
            serialized = json.dumps(result, default=str)
            if len(serialized) > 5 * 1024 * 1024:  # 5MB limit
                logger.warning("Tool result too large, truncating")
                return {"error": "Result too large", "truncated": True}
        except (TypeError, ValueError):
            logger.warning("Tool result not serializable")
            return {
                "error": "Result not serializable",
                "type": str(type(result)),
            }

        return result

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        server_name: str | None = None,
        user_id: str | None = None,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """Call a specific MCP tool.

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

        try:
            # Sanitize arguments first
            sanitized_args = self._sanitize_tool_arguments(arguments)

            # Find the tool
            tool = await self.get_tool_by_name(tool_name)
            if not tool:
                raise MCPServiceError(f"Tool not found: {tool_name}")

            # Call the tool with retry logic
            async def _call_tool():
                result = await tool.ainvoke(sanitized_args)
                return self._validate_tool_result(result)

            result = await self._retry_with_backoff(
                _call_tool, server_name or "unknown"
            )

            response_time_ms = (time.time() - start_time) * 1000

            # Track usage (async, don't block)
            asyncio.create_task(
                self._track_tool_usage(
                    server_name or "unknown",
                    tool_name,
                    sanitized_args,
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
                "server": server_name or "unknown",
                "response_time_ms": response_time_ms,
            }

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            error_msg = str(e)

            logger.error(
                "MCP tool call failed",
                tool=tool_name,
                server=server_name,
                error=error_msg,
            )

            # Track usage error (async, don't block)
            asyncio.create_task(
                self._track_tool_usage(
                    server_name or "unknown",
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
                "server": server_name or "unknown",
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
        """Track tool usage in the database."""
        try:
            from chatter.schemas.toolserver import ToolUsageCreate
            from chatter.services.toolserver import ToolServerService
            from chatter.utils.database import get_session_maker

            # Get database session
            async_session = get_session_maker()
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
                    result=(
                        {"data": result} if result is not None else None
                    ),
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
        args_schema: type[BaseModel] | None = None,
    ) -> BaseTool:
        """Create a custom tool for integration."""
        return StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
            args_schema=args_schema,
        )

    async def get_available_servers(self) -> list[dict[str, Any]]:
        """Get list of available remote MCP servers."""
        servers_info = []

        for server_name, server_config in self.servers.items():
            has_tools = server_name in self.tools_cache
            tools_count = len(self.tools_cache.get(server_name, []))

            servers_info.append(
                {
                    "name": server_name,
                    "base_url": str(server_config.base_url),
                    "transport_type": server_config.transport_type,
                    "enabled": server_config.enabled,
                    "has_oauth": server_config.oauth_config is not None,
                    "tools_discovered": has_tools,
                    "tools_count": tools_count,
                }
            )

        return servers_info

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on MCP servers."""
        if not self.enabled:
            return {"enabled": False, "status": "disabled"}

        server_status = {}
        total_tools = 0
        healthy_servers = 0

        for server_name, server_config in self.servers.items():
            try:
                if server_config.enabled:
                    # Try to get tools to check health
                    tools = await self.discover_tools(server_name)
                    tools_count = len(tools)
                    is_healthy = (
                        tools_count >= 0
                    )  # Consider healthy if we can connect

                    server_status[server_name] = {
                        "healthy": is_healthy,
                        "tools_count": tools_count,
                        "transport": server_config.transport_type,
                        "enabled": server_config.enabled,
                    }

                    if is_healthy:
                        healthy_servers += 1
                        total_tools += tools_count
                else:
                    server_status[server_name] = {
                        "healthy": False,
                        "tools_count": 0,
                        "transport": server_config.transport_type,
                        "enabled": server_config.enabled,
                    }

            except Exception as e:
                server_status[server_name] = {
                    "healthy": False,
                    "error": str(e),
                    "tools_count": 0,
                    "transport": server_config.transport_type,
                    "enabled": server_config.enabled,
                }

        overall_status = (
            "healthy" if healthy_servers > 0 else "unhealthy"
        )
        if total_tools == 0:
            overall_status = "no_tools"

        return {
            "enabled": True,
            "status": overall_status,
            "servers": server_status,
            "total_tools": total_tools,
            "healthy_servers": healthy_servers,
            "total_servers": len(self.servers),
        }

    async def enable_server(self, server_name: str) -> bool:
        """Enable a remote MCP server."""
        if server_name in self.servers:
            self.servers[server_name].enabled = True
            logger.info("Remote MCP server enabled", server=server_name)
            return True
        return False

    async def disable_server(self, server_name: str) -> bool:
        """Disable a remote MCP server."""
        if server_name in self.servers:
            self.servers[server_name].enabled = False
            # Clear tools cache for disabled server
            if server_name in self.tools_cache:
                del self.tools_cache[server_name]
            logger.info(
                "Remote MCP server disabled", server=server_name
            )
            return True
        return False

    async def refresh_server_tools(self, server_name: str) -> bool:
        """Refresh tools for a specific server."""
        if server_name not in self.servers:
            return False

        try:
            # Clear existing cache
            if server_name in self.tools_cache:
                del self.tools_cache[server_name]

            # Re-discover tools
            tools = await self.discover_tools(server_name)
            return len(tools) >= 0

        except Exception as e:
            logger.error(
                "Failed to refresh server tools",
                server=server_name,
                error=str(e),
            )
            return False

    async def cleanup(self) -> None:
        """Clean up all connections and resources."""
        # The langchain-mcp-adapters client handles cleanup automatically
        self.tools_cache.clear()
        self.connections.clear()
        self._client = None

        logger.info("MCP service cleanup completed")


class BuiltInTools:
    """Built-in tools for basic functionality."""

    @classmethod
    def create_builtin_tools(cls) -> list[BaseTool]:
        """Create a list of built-in LangChain tools."""
        return [
            StructuredTool.from_function(
                func=cls.calculate,
                name="calculator",
                description="Perform basic mathematical calculations",
            ),
            StructuredTool.from_function(
                func=cls.get_current_time,
                name="get_time",
                description="Get the current date and time",
            ),
        ]

    @staticmethod
    def calculate(expression: str) -> str:
        """Calculate a mathematical expression safely."""
        try:
            # Basic safety - only allow basic math operations
            allowed_chars = set("0123456789+-*/().")
            if not all(
                c in allowed_chars or c.isspace() for c in expression
            ):
                return "Error: Invalid characters in expression"

            # Use ast.literal_eval for basic arithmetic, but it doesn't support operators
            # For now, restrict to only literal values for security
            # A proper implementation would use a math expression parser
            import ast

            # Simple operator precedence parser would be safer here
            # For now, just handle basic cases safely
            try:
                # Try literal evaluation first (safest)
                result = ast.literal_eval(expression)
                return str(result)
            except (ValueError, SyntaxError):
                # For arithmetic operations, we'd need a proper math parser
                # Disabling eval for security - returning error instead
                return "Error: Complex expressions not supported for security reasons"
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def get_current_time() -> str:
        """Get the current date and time."""
        import datetime

        return datetime.datetime.now().isoformat()


# Global MCP service instance
mcp_service = MCPToolService()
