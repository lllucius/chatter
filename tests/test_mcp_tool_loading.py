"""Test for MCP tool loading in workflow execution."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chatter.core.tool_registry import ToolRegistry, ToolMetadata


class MockMCPTool:
    """Mock MCP tool for testing."""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"MockMCPTool({self.name})"


class MockServerTool:
    """Mock ServerTool model."""

    def __init__(self, name: str, status: str):
        self.name = name
        self.status = status


class MockToolServer:
    """Mock ToolServer model."""

    def __init__(self, name: str, status: str):
        self.name = name
        self.status = status
        self.base_url = "http://localhost:8080"
        self.transport_type = "http"
        self.oauth_client_id = None
        self.oauth_client_secret = None
        self.oauth_token_url = None
        self.oauth_scope = None
        self.headers = None
        self.timeout = 30


class TestMCPToolLoading:
    """Test that MCP tools are loaded in workflow execution."""

    @pytest.mark.asyncio
    async def test_get_enabled_tools_includes_mcp_tools(self):
        """Test that get_enabled_tools_for_workspace includes MCP tools from enabled servers."""
        # Create a fresh registry for this test
        registry = ToolRegistry()

        # Register a built-in tool
        builtin_tool = MagicMock()
        builtin_tool.name = "calculator"
        registry.register_tool(
            builtin_tool,
            ToolMetadata(name="calculator", description="Test calculator", category="builtin")
        )

        # Mock database session and results
        mock_session = AsyncMock()

        # Mock ServerTool query result - calculator is enabled
        mock_server_tools_result = MagicMock()
        mock_server_tools_result.scalars.return_value.all.return_value = [
            MockServerTool("calculator", "enabled")
        ]

        # Mock ToolServer query result - one enabled MCP server
        mock_tool_servers_result = MagicMock()
        mock_tool_servers_result.scalars.return_value.all.return_value = [
            MockToolServer("weather_server", "enabled")
        ]

        # Set up session.execute to return different results for different queries
        async def mock_execute(query):
            # Check if this is a ServerTool or ToolServer query based on the query object
            query_str = str(query)
            if "tool_server" in query_str.lower():
                return mock_tool_servers_result
            else:
                return mock_server_tools_result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        # Mock MCP service to return tools
        mock_mcp_tools = [
            MockMCPTool("weather"),
            MockMCPTool("date")
        ]

        with patch('chatter.services.mcp.mcp_service') as mock_mcp_service:
            # Set up connections attribute as empty dict (server not yet added)
            mock_mcp_service.connections = {}
            mock_mcp_service.add_server = AsyncMock(return_value=True)
            mock_mcp_service.get_tools = AsyncMock(return_value=mock_mcp_tools)

            # Call the method
            tools = await registry.get_enabled_tools_for_workspace(
                workspace_id="test_workspace",
                user_permissions=[],
                session=mock_session
            )

            # Verify add_server was called to add the server
            mock_mcp_service.add_server.assert_called_once()

            # Verify MCP service was called with the enabled server
            mock_mcp_service.get_tools.assert_called_once_with(
                server_names=["weather_server"]
            )

            # Verify both builtin and MCP tools are included
            assert len(tools) == 3, f"Expected 3 tools (1 builtin + 2 MCP), got {len(tools)}"

            # Verify builtin tool is present
            builtin_tools = [t for t in tools if hasattr(t, 'name') and t.name == 'calculator']
            assert len(builtin_tools) == 1, "Built-in calculator tool should be present"

            # Verify MCP tools are present
            mcp_tool_names = {t.name for t in tools if isinstance(t, MockMCPTool)}
            assert "weather" in mcp_tool_names, "MCP weather tool should be present"
            assert "date" in mcp_tool_names, "MCP date tool should be present"

    @pytest.mark.asyncio
    async def test_get_enabled_tools_handles_mcp_failure_gracefully(self):
        """Test that MCP tool loading failures don't break the entire tool loading."""
        registry = ToolRegistry()

        # Register a built-in tool
        builtin_tool = MagicMock()
        builtin_tool.name = "calculator"
        registry.register_tool(
            builtin_tool,
            ToolMetadata(name="calculator", description="Test calculator", category="builtin")
        )

        # Mock database session
        mock_session = AsyncMock()

        # Mock ServerTool query result
        mock_server_tools_result = MagicMock()
        mock_server_tools_result.scalars.return_value.all.return_value = [
            MockServerTool("calculator", "enabled")
        ]

        # Mock ToolServer query result
        mock_tool_servers_result = MagicMock()
        mock_tool_servers_result.scalars.return_value.all.return_value = [
            MockToolServer("broken_server", "enabled")
        ]

        async def mock_execute(query):
            query_str = str(query)
            if "tool_server" in query_str.lower():
                return mock_tool_servers_result
            else:
                return mock_server_tools_result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        # Mock MCP service to raise an exception
        with patch('chatter.services.mcp.mcp_service') as mock_mcp_service:
            mock_mcp_service.get_tools = AsyncMock(
                side_effect=Exception("MCP server connection failed")
            )

            # Call the method - should not raise
            tools = await registry.get_enabled_tools_for_workspace(
                workspace_id="test_workspace",
                user_permissions=[],
                session=mock_session
            )

            # Verify builtin tool is still returned despite MCP failure
            assert len(tools) == 1, "Should still return builtin tools despite MCP failure"
            assert tools[0].name == "calculator"

    @pytest.mark.asyncio
    async def test_get_enabled_tools_without_session_backward_compatible(self):
        """Test that get_enabled_tools_for_workspace works without a session (backward compatible)."""
        registry = ToolRegistry()

        # Register tools
        tool1 = MagicMock()
        tool1.name = "tool1"
        registry.register_tool(
            tool1,
            ToolMetadata(name="tool1", description="Test tool 1", category="builtin")
        )

        # Call without session
        tools = await registry.get_enabled_tools_for_workspace(
            workspace_id="test_workspace",
            user_permissions=[],
            session=None
        )

        # Should return all registry tools
        assert len(tools) == 1
        assert tools[0].name == "tool1"

    @pytest.mark.asyncio
    async def test_get_enabled_tools_reuses_existing_connections(self):
        """Test that get_enabled_tools_for_workspace reuses existing MCP connections."""
        registry = ToolRegistry()

        # Register a built-in tool
        builtin_tool = MagicMock()
        builtin_tool.name = "calculator"
        registry.register_tool(
            builtin_tool,
            ToolMetadata(name="calculator", description="Test calculator", category="builtin")
        )

        # Mock database session
        mock_session = AsyncMock()

        # Mock ServerTool query result
        mock_server_tools_result = MagicMock()
        mock_server_tools_result.scalars.return_value.all.return_value = [
            MockServerTool("calculator", "enabled")
        ]

        # Mock ToolServer query result - one enabled MCP server
        mock_tool_servers_result = MagicMock()
        mock_tool_servers_result.scalars.return_value.all.return_value = [
            MockToolServer("weather_server", "enabled")
        ]

        # Set up session.execute to return different results for different queries
        async def mock_execute(query):
            query_str = str(query)
            if "tool_server" in query_str.lower():
                return mock_tool_servers_result
            else:
                return mock_server_tools_result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        # Mock MCP service to return tools
        mock_mcp_tools = [
            MockMCPTool("weather"),
            MockMCPTool("date")
        ]

        with patch('chatter.services.mcp.mcp_service') as mock_mcp_service:
            # Set up connections attribute with existing server
            mock_mcp_service.connections = {"weather_server": MagicMock()}
            mock_mcp_service.add_server = AsyncMock(return_value=True)
            mock_mcp_service.get_tools = AsyncMock(return_value=mock_mcp_tools)

            # Call the method
            tools = await registry.get_enabled_tools_for_workspace(
                workspace_id="test_workspace",
                user_permissions=[],
                session=mock_session
            )

            # Verify add_server was NOT called since server already exists
            mock_mcp_service.add_server.assert_not_called()

            # Verify MCP service was called with the enabled server
            mock_mcp_service.get_tools.assert_called_once_with(
                server_names=["weather_server"]
            )

            # Verify both builtin and MCP tools are included
            assert len(tools) == 3, f"Expected 3 tools (1 builtin + 2 MCP), got {len(tools)}"

