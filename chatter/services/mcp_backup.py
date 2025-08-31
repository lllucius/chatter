"""MCP (Model Context Protocol) service using langchain-mcp-adapters."""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional

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
    scope: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None


@dataclass
class RemoteMCPServer:
    """Remote MCP server configuration for HTTP/SSE endpoints."""

    name: str
    base_url: HttpUrl
    transport_type: str  # "http" or "sse" or "stdio" or "websocket"
    oauth_config: Optional[OAuthConfig] = None
    headers: Optional[dict[str, str]] = None
    timeout: int = 30
    enabled: bool = True


class MCPToolService:
    """Service for MCP tool calling integration using langchain-mcp-adapters."""

    def __init__(self) -> None:
        """Initialize MCP tool service."""
        self.enabled = settings.mcp_enabled
        self.servers: dict[str, RemoteMCPServer] = {}
        self.connections: dict[str, Connection] = {}
        self.tools_cache: dict[str, list[BaseTool]] = {}
        self._client: Optional[MultiServerMCPClient] = None

    def _get_client(self) -> MultiServerMCPClient:
        """Get or create the MCP client."""
        if self._client is None:
            self._client = MultiServerMCPClient(self.connections)
        return self._client

    def _update_client(self) -> None:
        """Update the client with new connections."""
        self._client = MultiServerMCPClient(self.connections)

    def _convert_server_to_connection(self, server: RemoteMCPServer) -> Connection:
        """Convert RemoteMCPServer to langchain-mcp-adapters Connection."""
        base_connection = {
            "transport": "streamable_http" if server.transport_type == "http" else server.transport_type,
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
            raise MCPServiceError("stdio transport requires command and args configuration")
            
        elif server.transport_type == "websocket":
            base_connection["url"] = str(server.base_url)
            if server.headers:
                base_connection["headers"] = server.headers
                
        return base_connection

    async def add_remote_server(
        self, 
        server_config: RemoteMCPServer
    ) -> bool:
        """Add a remote MCP server configuration."""
        if not self.enabled:
            return False

        try:
            # Convert server config to connection
            connection = self._convert_server_to_connection(server_config)
            
            self.servers[server_config.name] = server_config
            self.connections[server_config.name] = connection
            
            # Update client with new connections
            self._update_client()

            logger.info(
                "Remote MCP server added",
                server=server_config.name,
                transport=server_config.transport_type,
                url=str(server_config.base_url),
            )
            return True

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
        """Authenticate with OAuth for a server."""
        server = self.servers.get(server_name)
        if not server or not server.oauth_config:
            return False

        oauth_config = server.oauth_config
        
        try:
            async with httpx.AsyncClient() as client:
                # Prepare OAuth token request
                token_data = {
                    "grant_type": "client_credentials",
                    "client_id": oauth_config.client_id,
                    "client_secret": oauth_config.client_secret,
                }
                
                if oauth_config.scope:
                    token_data["scope"] = oauth_config.scope

                # Request token
                response = await client.post(
                    oauth_config.token_url,
                    data=token_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()

                token_info = response.json()
                access_token = token_info.get("access_token")
                
                if not access_token:
                    raise MCPServiceError("No access token in OAuth response")

                # Update server client with new token
                oauth_config.access_token = access_token
                if server_name in self.clients:
                    self.clients[server_name].headers["Authorization"] = f"Bearer {access_token}"

                # Store token info for refresh
                self._oauth_tokens[server_name] = {
                    "access_token": access_token,
                    "expires_in": token_info.get("expires_in"),
                    "refresh_token": token_info.get("refresh_token"),
                }

                logger.info("OAuth authentication successful", server=server_name)
                return True

        except Exception as e:
            logger.error(
                "OAuth authentication failed",
                server=server_name,
                error=str(e),
            )
            return False

    async def discover_tools(self, server_name: str) -> list[dict[str, Any]]:
        """Discover tools from a remote MCP server."""
        if not self.enabled or server_name not in self.servers:
            return []

        server = self.servers[server_name]
        client = self.clients.get(server_name)
        
        if not client:
            return []

        try:
            if server.transport_type == "http":
                response = await client.get("/tools")
                response.raise_for_status()
                tools_data = response.json()
                
            elif server.transport_type == "sse":
                tools_data = await self._discover_tools_sse(server_name)
                
            else:
                raise MCPServiceError(f"Unsupported transport type: {server.transport_type}")

            # Normalize tools data
            tools = tools_data.get("tools", []) if isinstance(tools_data, dict) else tools_data
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

    async def _discover_tools_sse(self, server_name: str) -> list[dict[str, Any]]:
        """Discover tools using SSE connection."""
        server = self.servers[server_name]
        client = self.clients[server_name]
        
        tools = []
        sse_url = f"{server.base_url}/tools/stream"
        
        async with aconnect_sse(client, "GET", sse_url) as event_source:
            async for sse in event_source.aiter_sse():
                if sse.event == "tool":
                    tool_data = sse.json()
                    tools.append(tool_data)
                elif sse.event == "end":
                    break
                    
        return tools

    async def get_tools(
        self, server_names: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Get tools from specified remote MCP servers."""
        if not self.enabled:
            return []

        if server_names is None:
            server_names = list(self.servers.keys())

        all_tools = []

        for server_name in server_names:
            if server_name not in self.tools_cache:
                # Discover tools from the server
                await self.discover_tools(server_name)

            if server_name in self.tools_cache:
                tools = self.tools_cache[server_name]
                all_tools.extend(tools)
                logger.debug(
                    "Retrieved tools from remote server",
                    server=server_name,
                    count=len(tools),
                )

        return all_tools

    async def get_tool_by_name(self, tool_name: str) -> dict[str, Any] | None:
        """Get a specific tool by name."""
        all_tools = await self.get_tools()

        for tool in all_tools:
            if tool.get("name") == tool_name:
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
        """Call a specific remote MCP tool with usage tracking.

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
        
        # Find the tool and its server
        tool = await self.get_tool_by_name(tool_name)
        if not tool:
            raise MCPServiceError(f"Tool not found: {tool_name}")

        # Find which server provides this tool
        found_server = None
        for srv_name, tools in self.tools_cache.items():
            if any(t.get("name") == tool_name for t in tools):
                found_server = srv_name
                break

        if not found_server:
            raise MCPServiceError(f"Server not found for tool: {tool_name}")

        server = self.servers[found_server]
        client = self.clients[found_server]

        try:
            # Make HTTP call to tool endpoint
            if server.transport_type == "http":
                response = await client.post(
                    f"/tools/{tool_name}/call",
                    json={"arguments": arguments},
                )
                response.raise_for_status()
                result_data = response.json()
                
            elif server.transport_type == "sse":
                result_data = await self._call_tool_sse(
                    found_server, tool_name, arguments
                )
            else:
                raise MCPServiceError(f"Unsupported transport type: {server.transport_type}")

            response_time_ms = (time.time() - start_time) * 1000

            # Track usage (async, don't block)
            asyncio.create_task(
                self._track_tool_usage(
                    found_server,
                    tool_name,
                    arguments,
                    result_data,
                    response_time_ms,
                    True,
                    None,
                    user_id,
                    conversation_id,
                )
            )

            return {
                "success": True,
                "result": result_data,
                "tool": tool_name,
                "server": found_server,
                "response_time_ms": response_time_ms,
            }

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            error_msg = str(e)

            logger.error(
                "Remote tool call failed",
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

    async def _call_tool_sse(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Call a tool using SSE connection."""
        server = self.servers[server_name]
        client = self.clients[server_name]
        
        sse_url = f"{server.base_url}/tools/{tool_name}/call"
        
        result = None
        async with aconnect_sse(
            client, 
            "POST", 
            sse_url,
            json={"arguments": arguments}
        ) as event_source:
            async for sse in event_source.aiter_sse():
                if sse.event == "result":
                    result = sse.json()
                    break
                elif sse.event == "error":
                    error_data = sse.json()
                    raise MCPServiceError(error_data.get("message", "Tool call failed"))
                    
        if result is None:
            raise MCPServiceError("No result received from SSE tool call")
            
        return result

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
        """Perform health check on remote MCP servers."""
        if not self.enabled:
            return {"enabled": False, "status": "disabled"}

        server_status = {}
        total_tools = 0
        healthy_servers = 0

        for server_name, server_config in self.servers.items():
            try:
                client = self.clients.get(server_name)
                if client and server_config.enabled:
                    # Check server health
                    response = await client.get("/health", timeout=5)
                    is_healthy = response.status_code == 200
                    
                    tools_count = len(self.tools_cache.get(server_name, []))
                    
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

        overall_status = "healthy" if healthy_servers > 0 else "unhealthy"
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
            logger.info("Remote MCP server disabled", server=server_name)
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
            return len(tools) > 0
            
        except Exception as e:
            logger.error(
                "Failed to refresh server tools",
                server=server_name,
                error=str(e),
            )
            return False

    async def cleanup(self) -> None:
        """Clean up all connections and resources."""
        for client in self.clients.values():
            try:
                await client.aclose()
            except Exception as e:
                logger.warning("Error closing HTTP client", error=str(e))
                
        self.clients.clear()
        self.tools_cache.clear()
        self._oauth_tokens.clear()
        
        logger.info("MCP service cleanup completed")

# Global MCP service instance
mcp_service = MCPToolService()


class BuiltInTools:
    """Built-in tools for basic functionality."""
    
    @classmethod
    def create_builtin_tools(cls) -> list[BaseTool]:
        """Create a list of built-in LangChain tools."""
        return [
            StructuredTool.from_function(
                func=cls.calculate,
                name="calculator",
                description="Perform basic mathematical calculations"
            ),
            StructuredTool.from_function(
                func=cls.get_current_time,
                name="get_time",
                description="Get the current date and time"
            ),
        ]
    
    @staticmethod
    def calculate(expression: str) -> str:
        """Calculate a mathematical expression."""
        try:
            # Basic safety - only allow basic math operations
            allowed_chars = set('0123456789+-*/().')
            if not all(c in allowed_chars or c.isspace() for c in expression):
                return "Error: Invalid characters in expression"
            
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def get_current_time() -> str:
        """Get the current date and time."""
        import datetime
        return datetime.datetime.now().isoformat()
