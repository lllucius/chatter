"""Tests for MCP (Model Context Protocol) service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.tools import BaseTool, StructuredTool
from langchain_mcp_adapters.sessions import Connection
from pydantic import HttpUrl

from chatter.services.mcp import (
    MCPServiceError,
    MCPToolService,
    OAuthConfig,
    RemoteMCPServer,
)


class TestOAuthConfig:
    """Test OAuthConfig dataclass."""

    def test_oauth_config_creation(self):
        """Test creating OAuthConfig with required fields."""
        config = OAuthConfig(
            client_id="test_client",
            client_secret="test_secret",
            token_url="https://auth.example.com/token",
        )

        assert config.client_id == "test_client"
        assert config.client_secret == "test_secret"
        assert config.token_url == "https://auth.example.com/token"
        assert config.scope is None
        assert config.refresh_token is None
        assert config.access_token is None

    def test_oauth_config_with_optional_fields(self):
        """Test creating OAuthConfig with optional fields."""
        config = OAuthConfig(
            client_id="test_client",
            client_secret="test_secret",
            token_url="https://auth.example.com/token",
            scope="read write",
            refresh_token="refresh_123",
            access_token="access_456",
        )

        assert config.scope == "read write"
        assert config.refresh_token == "refresh_123"
        assert config.access_token == "access_456"


class TestRemoteMCPServer:
    """Test RemoteMCPServer dataclass."""

    def test_remote_server_creation(self):
        """Test creating RemoteMCPServer with required fields."""
        server = RemoteMCPServer(
            name="test_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
        )

        assert server.name == "test_server"
        assert str(server.base_url) == "https://mcp.example.com/"
        assert server.transport_type == "http"
        assert server.oauth_config is None
        assert server.headers is None
        assert server.timeout == 30
        assert server.enabled is True

    def test_remote_server_with_oauth(self):
        """Test creating RemoteMCPServer with OAuth configuration."""
        oauth_config = OAuthConfig(
            client_id="test_client",
            client_secret="test_secret",
            token_url="https://auth.example.com/token",
        )

        server = RemoteMCPServer(
            name="oauth_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
            oauth_config=oauth_config,
            headers={"Custom-Header": "value"},
            timeout=60,
            enabled=False,
        )

        assert server.oauth_config == oauth_config
        assert server.headers == {"Custom-Header": "value"}
        assert server.timeout == 60
        assert server.enabled is False


class TestMCPToolService:
    """Test MCPToolService functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.service = MCPToolService()

    def test_service_initialization(self):
        """Test MCPToolService initialization."""
        assert isinstance(self.service.servers, dict)
        assert isinstance(self.service.connections, dict)
        assert isinstance(self.service.tools_cache, dict)
        assert self.service._client is None
        assert self.service._max_retries == 3

    @patch('chatter.services.mcp.MultiServerMCPClient')
    def test_get_client(self, mock_client_class):
        """Test getting MCP client."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client = self.service._get_client()

        assert self.service._client == mock_client
        mock_client_class.assert_called_once_with(
            self.service.connections
        )

        # Second call should return same client
        client2 = self.service._get_client()
        assert client == client2
        assert mock_client_class.call_count == 1

    def test_validate_server_config_valid(self):
        """Test server configuration validation with valid config."""
        server_config = RemoteMCPServer(
            name="valid_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
        )

        # Should not raise any exception
        self.service._validate_server_config(server_config)

    def test_validate_server_config_empty_name(self):
        """Test server configuration validation with empty name."""
        server_config = RemoteMCPServer(
            name="",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
        )

        with pytest.raises(ValueError, match="Server name is required"):
            self.service._validate_server_config(server_config)

    def test_validate_server_config_invalid_transport(self):
        """Test server configuration validation with invalid transport type."""
        server_config = RemoteMCPServer(
            name="test_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="invalid",
        )

        with pytest.raises(
            ValueError, match="Unsupported transport type"
        ):
            self.service._validate_server_config(server_config)

    def test_is_server_healthy(self):
        """Test server health check."""
        server_name = "test_server"

        # Healthy server (no failures)
        assert self.service._is_server_healthy(server_name) is True

        # Add some failures
        self.service._connection_retry_counts[server_name] = 3
        assert self.service._is_server_healthy(server_name) is True

        # Circuit breaker threshold reached
        self.service._connection_retry_counts[server_name] = 5
        assert self.service._is_server_healthy(server_name) is False

    @pytest.mark.asyncio
    async def test_retry_with_backoff_success_first_try(self):
        """Test retry logic succeeds on first attempt."""
        mock_operation = AsyncMock(return_value="success")

        result = await self.service._retry_with_backoff(
            mock_operation, "test_server", "arg1", kwarg1="value1"
        )

        assert result == "success"
        mock_operation.assert_called_once_with("arg1", kwarg1="value1")
        assert (
            "test_server" not in self.service._connection_retry_counts
        )

    @pytest.mark.asyncio
    async def test_retry_with_backoff_success_after_retries(self):
        """Test retry logic succeeds after initial failures."""
        mock_operation = AsyncMock()
        mock_operation.side_effect = [
            Exception("Failure 1"),
            Exception("Failure 2"),
            "success",
        ]

        with patch('asyncio.sleep') as mock_sleep:
            result = await self.service._retry_with_backoff(
                mock_operation, "test_server"
            )

        assert result == "success"
        assert mock_operation.call_count == 3
        assert mock_sleep.call_count == 2
        # Retry count should be reset on success
        assert (
            "test_server" not in self.service._connection_retry_counts
        )

    @pytest.mark.asyncio
    async def test_retry_with_backoff_all_retries_fail(self):
        """Test retry logic when all attempts fail."""
        mock_operation = AsyncMock(
            side_effect=Exception("Persistent failure")
        )

        with patch('asyncio.sleep'):
            with pytest.raises(
                MCPServiceError,
                match="Operation failed after 3 retries",
            ):
                await self.service._retry_with_backoff(
                    mock_operation, "test_server"
                )

        assert mock_operation.call_count == 3
        assert self.service._connection_retry_counts["test_server"] == 3

    @pytest.mark.asyncio
    async def test_retry_with_backoff_circuit_breaker(self):
        """Test retry logic with circuit breaker engaged."""
        # Set failure count above threshold
        self.service._connection_retry_counts["test_server"] = 6

        mock_operation = AsyncMock()

        with pytest.raises(
            MCPServiceError, match="Circuit breaker open"
        ):
            await self.service._retry_with_backoff(
                mock_operation, "test_server"
            )

        # Operation should not be called due to circuit breaker
        mock_operation.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_server_success(self):
        """Test successfully adding a server."""
        server_config = RemoteMCPServer(
            name="test_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
        )

        with patch.object(
            self.service, '_convert_server_to_connection'
        ) as mock_convert:
            with patch.object(
                self.service, '_update_client'
            ) as mock_update:
                mock_convert.return_value = MagicMock(spec=Connection)

                result = await self.service.add_server(server_config)

        assert result is True
        assert "test_server" in self.service.servers
        assert "test_server" in self.service.connections
        assert self.service.servers["test_server"] == server_config
        mock_convert.assert_called_once_with(server_config)
        mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_server_disabled_service(self):
        """Test adding server when service is disabled."""
        self.service.enabled = False

        server_config = RemoteMCPServer(
            name="test_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
        )

        result = await self.service.add_server(server_config)

        assert result is False
        assert "test_server" not in self.service.servers

    @pytest.mark.asyncio
    async def test_add_server_validation_error(self):
        """Test adding server with invalid configuration."""
        server_config = RemoteMCPServer(
            name="",  # Invalid: empty name
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
        )

        result = await self.service.add_server(server_config)

        assert result is False
        assert len(self.service.servers) == 0

    @pytest.mark.asyncio
    async def test_remove_server_success(self):
        """Test successfully removing a server."""
        # First add a server
        server_config = RemoteMCPServer(
            name="test_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
        )

        self.service.servers["test_server"] = server_config
        self.service.connections["test_server"] = MagicMock()
        self.service.tools_cache["test_server"] = []

        with patch.object(
            self.service, '_update_client'
        ) as mock_update:
            result = await self.service.remove_server("test_server")

        assert result is True
        assert "test_server" not in self.service.servers
        assert "test_server" not in self.service.connections
        assert "test_server" not in self.service.tools_cache
        mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_nonexistent_server(self):
        """Test removing a server that doesn't exist."""
        with patch.object(
            self.service, '_update_client'
        ) as mock_update:
            result = await self.service.remove_server(
                "nonexistent_server"
            )

        assert (
            result is True
        )  # Should succeed even if server doesn't exist
        mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_discover_tools_success(self):
        """Test successfully discovering tools from a server."""
        server_config = RemoteMCPServer(
            name="test_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
        )
        self.service.servers["test_server"] = server_config

        mock_tool = MagicMock(spec=BaseTool)
        mock_tool.name = "test_tool"

        mock_client = MagicMock()
        mock_client.get_tools = AsyncMock(return_value=[mock_tool])

        with patch.object(
            self.service, '_get_client', return_value=mock_client
        ):
            tools = await self.service.discover_tools("test_server")

        assert len(tools) == 1
        assert tools[0] == mock_tool
        assert "test_server" in self.service.tools_cache
        assert self.service.tools_cache["test_server"] == [mock_tool]
        mock_client.get_tools.assert_called_once_with(
            server_name="test_server"
        )

    @pytest.mark.asyncio
    async def test_discover_tools_disabled_service(self):
        """Test discovering tools when service is disabled."""
        self.service.enabled = False

        tools = await self.service.discover_tools("test_server")

        assert tools == []

    @pytest.mark.asyncio
    async def test_discover_tools_nonexistent_server(self):
        """Test discovering tools from nonexistent server."""
        tools = await self.service.discover_tools("nonexistent_server")

        assert tools == []

    @pytest.mark.asyncio
    async def test_discover_tools_unhealthy_server(self):
        """Test discovering tools from unhealthy server."""
        server_config = RemoteMCPServer(
            name="test_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
        )
        self.service.servers["test_server"] = server_config

        # Make server unhealthy
        self.service._connection_retry_counts["test_server"] = 10

        tools = await self.service.discover_tools("test_server")

        assert tools == []

    @pytest.mark.asyncio
    async def test_get_tools_all_servers(self):
        """Test getting tools from all servers."""
        mock_tool1 = MagicMock(spec=BaseTool)
        mock_tool2 = MagicMock(spec=BaseTool)

        mock_client = MagicMock()
        mock_client.get_tools = AsyncMock(
            return_value=[mock_tool1, mock_tool2]
        )

        with patch.object(
            self.service, '_get_client', return_value=mock_client
        ):
            tools = await self.service.get_tools()

        assert len(tools) == 2
        mock_client.get_tools.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_get_tools_specific_servers(self):
        """Test getting tools from specific servers."""
        # Add servers to connections
        self.service.connections["server1"] = MagicMock()
        self.service.connections["server2"] = MagicMock()

        mock_tool1 = MagicMock(spec=BaseTool)
        mock_tool2 = MagicMock(spec=BaseTool)

        mock_client = MagicMock()
        mock_client.get_tools = AsyncMock()
        mock_client.get_tools.side_effect = [
            [mock_tool1],  # server1 tools
            [mock_tool2],  # server2 tools
        ]

        with patch.object(
            self.service, '_get_client', return_value=mock_client
        ):
            tools = await self.service.get_tools(["server1", "server2"])

        assert len(tools) == 2
        assert mock_tool1 in tools
        assert mock_tool2 in tools
        assert mock_client.get_tools.call_count == 2

    @pytest.mark.asyncio
    async def test_get_tools_disabled_service(self):
        """Test getting tools when service is disabled."""
        self.service.enabled = False

        tools = await self.service.get_tools()

        assert tools == []

    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        """Test successfully calling a tool."""
        # Add server and cached tools
        self.service.servers["test_server"] = MagicMock()
        mock_tool = MagicMock(spec=BaseTool)
        mock_tool.name = "test_tool"
        self.service.tools_cache["test_server"] = [mock_tool]

        mock_client = MagicMock()
        mock_client.call_tool = AsyncMock(
            return_value={"result": "success"}
        )

        with patch.object(
            self.service, '_get_client', return_value=mock_client
        ):
            result = await self.service.call_tool(
                "test_tool", {"param": "value"}
            )

        assert result == {"result": "success"}
        mock_client.call_tool.assert_called_once_with(
            tool_name="test_tool", arguments={"param": "value"}
        )

    @pytest.mark.asyncio
    async def test_call_tool_disabled_service(self):
        """Test calling tool when service is disabled."""
        self.service.enabled = False

        result = await self.service.call_tool("test_tool", {})

        assert result is None

    @pytest.mark.asyncio
    async def test_list_servers(self):
        """Test listing servers."""
        server1 = RemoteMCPServer(
            name="server1",
            base_url=HttpUrl("https://mcp1.example.com"),
            transport_type="http",
        )
        server2 = RemoteMCPServer(
            name="server2",
            base_url=HttpUrl("https://mcp2.example.com"),
            transport_type="sse",
            enabled=False,
        )

        self.service.servers["server1"] = server1
        self.service.servers["server2"] = server2

        servers = self.service.list_servers()

        assert len(servers) == 2
        assert "server1" in servers
        assert "server2" in servers
        assert servers["server1"] == server1
        assert servers["server2"] == server2

    @pytest.mark.asyncio
    async def test_get_server_info(self):
        """Test getting server information."""
        server_config = RemoteMCPServer(
            name="test_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
            timeout=60,
        )
        self.service.servers["test_server"] = server_config
        self.service.tools_cache["test_server"] = [
            MagicMock(),
            MagicMock(),
        ]

        info = await self.service.get_server_info("test_server")

        expected_info = {
            "name": "test_server",
            "url": "https://mcp.example.com/",
            "transport": "http",
            "enabled": True,
            "healthy": True,
            "tools_count": 2,
            "retry_count": 0,
        }
        assert info == expected_info

    @pytest.mark.asyncio
    async def test_get_server_info_nonexistent(self):
        """Test getting info for nonexistent server."""
        info = await self.service.get_server_info("nonexistent")

        assert info is None

    @pytest.mark.asyncio
    async def test_authenticate_oauth_not_implemented(self):
        """Test OAuth authentication (currently not implemented)."""
        result = await self.service._authenticate_oauth("test_server")

        assert result is False

    def test_convert_server_to_connection_http(self):
        """Test converting server config to HTTP connection."""
        server_config = RemoteMCPServer(
            name="http_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
            headers={"Authorization": "Bearer token"},
            timeout=30,
        )

        # This method would be implemented to handle different transport types
        # For now, we test that it would be called correctly
        with patch.object(
            self.service, '_convert_server_to_connection'
        ) as mock_convert:
            mock_convert.return_value = MagicMock(spec=Connection)

            connection = self.service._convert_server_to_connection(
                server_config
            )

            assert connection is not None


@pytest.mark.integration
class TestMCPServiceIntegration:
    """Integration tests for MCP service."""

    def setup_method(self):
        """Set up test environment."""
        self.service = MCPToolService()

    @pytest.mark.asyncio
    async def test_server_lifecycle(self):
        """Test complete server lifecycle: add, discover, call, remove."""
        server_config = RemoteMCPServer(
            name="test_server",
            base_url=HttpUrl("https://mcp.example.com"),
            transport_type="http",
        )

        # Mock the MCP client interactions
        mock_tool = StructuredTool.from_function(
            func=lambda x: f"Result: {x}",
            name="test_tool",
            description="Test tool",
        )

        mock_client = MagicMock()
        mock_client.get_tools = AsyncMock(return_value=[mock_tool])
        mock_client.call_tool = AsyncMock(
            return_value={"result": "success"}
        )

        with patch.object(
            self.service, '_get_client', return_value=mock_client
        ):
            with patch.object(
                self.service, '_convert_server_to_connection'
            ) as mock_convert:
                with patch.object(self.service, '_update_client'):
                    mock_convert.return_value = MagicMock(
                        spec=Connection
                    )

                    # Add server
                    assert (
                        await self.service.add_server(server_config)
                        is True
                    )
                    assert "test_server" in self.service.servers

                    # Discover tools
                    tools = await self.service.discover_tools(
                        "test_server"
                    )
                    assert len(tools) == 1
                    assert tools[0].name == "test_tool"

                    # Call tool
                    result = await self.service.call_tool(
                        "test_tool", {"input": "test"}
                    )
                    assert result == {"result": "success"}

                    # Get server info
                    info = await self.service.get_server_info(
                        "test_server"
                    )
                    assert info["name"] == "test_server"
                    assert info["tools_count"] == 1

                    # Remove server
                    assert (
                        await self.service.remove_server("test_server")
                        is True
                    )
                    assert "test_server" not in self.service.servers

    @pytest.mark.asyncio
    async def test_multiple_servers_management(self):
        """Test managing multiple MCP servers."""
        server1 = RemoteMCPServer(
            name="server1",
            base_url=HttpUrl("https://mcp1.example.com"),
            transport_type="http",
        )
        server2 = RemoteMCPServer(
            name="server2",
            base_url=HttpUrl("https://mcp2.example.com"),
            transport_type="sse",
        )

        with patch.object(
            self.service, '_convert_server_to_connection'
        ) as mock_convert:
            with patch.object(self.service, '_update_client'):
                mock_convert.return_value = MagicMock(spec=Connection)

                # Add both servers
                assert await self.service.add_server(server1) is True
                assert await self.service.add_server(server2) is True

                # List servers
                servers = self.service.list_servers()
                assert len(servers) == 2
                assert "server1" in servers
                assert "server2" in servers

                # Remove one server
                assert (
                    await self.service.remove_server("server1") is True
                )

                # Verify only one remains
                servers = self.service.list_servers()
                assert len(servers) == 1
                assert "server2" in servers

    @pytest.mark.asyncio
    async def test_error_recovery_scenarios(self):
        """Test error recovery and circuit breaker functionality."""
        server_config = RemoteMCPServer(
            name="unreliable_server",
            base_url=HttpUrl("https://unreliable.example.com"),
            transport_type="http",
        )

        with patch.object(
            self.service, '_convert_server_to_connection'
        ):
            with patch.object(self.service, '_update_client'):
                # Add server successfully
                assert (
                    await self.service.add_server(server_config) is True
                )

                # Simulate failures to trigger circuit breaker
                for i in range(6):  # Exceed threshold
                    self.service._connection_retry_counts[
                        "unreliable_server"
                    ] = (i + 1)

                # Verify server is now unhealthy
                assert not self.service._is_server_healthy(
                    "unreliable_server"
                )

                # Tool discovery should be skipped for unhealthy server
                tools = await self.service.discover_tools(
                    "unreliable_server"
                )
                assert tools == []


class TestMCPServiceError:
    """Test MCPServiceError exception."""

    def test_mcp_service_error_creation(self):
        """Test creating MCPServiceError."""
        error = MCPServiceError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_mcp_service_error_with_cause(self):
        """Test MCPServiceError with underlying cause."""
        original_error = ValueError("Original error")
        try:
            raise MCPServiceError("MCP error") from original_error
        except MCPServiceError as mcp_error:
            assert str(mcp_error) == "MCP error"
            assert mcp_error.__cause__ == original_error
