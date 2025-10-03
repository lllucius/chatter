"""Tests for builtin tools database integration."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_builtin_server_initialization():
    """Test that builtin tools server is created during initialization."""
    from chatter.models.toolserver import ServerStatus, ToolServer, ToolStatus
    from chatter.services.toolserver import ToolServerService
    from sqlalchemy import select

    # Create a mock session
    mock_session = AsyncMock()
    
    # Mock the execute method to return no existing servers initially
    mock_existing_result = MagicMock()
    mock_existing_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_existing_result
    
    # Track servers and tools added
    added_objects = []
    
    def mock_add(obj):
        added_objects.append(obj)
    
    mock_session.add = mock_add
    mock_session.commit = AsyncMock()
    mock_session.flush = AsyncMock()
    
    # Create service
    service = ToolServerService(mock_session)
    
    # Initialize builtin servers
    await service.initialize_builtin_servers()
    
    # Check that servers were added
    servers = [obj for obj in added_objects if isinstance(obj, ToolServer)]
    assert len(servers) >= 1, "At least one server should be added"
    
    # Check that builtin_tools server exists
    builtin_server = None
    for server in servers:
        if server.name == "builtin_tools":
            builtin_server = server
            break
    
    assert builtin_server is not None, "builtin_tools server should exist"
    assert builtin_server.display_name == "Built-in Tools"
    assert builtin_server.is_builtin is True
    assert builtin_server.status == ServerStatus.DISABLED
    
    # Check that tools were added (ServerTool objects)
    from chatter.models.toolserver import ServerTool
    
    tools = [obj for obj in added_objects if isinstance(obj, ServerTool)]
    assert len(tools) >= 2, "At least 2 tools should be added"
    
    # Check for calculator and get_time tools
    tool_names = {tool.name for tool in tools}
    assert "calculator" in tool_names, "calculator tool should exist"
    assert "get_time" in tool_names, "get_time tool should exist"
    
    # Verify tool properties
    for tool in tools:
        if tool.name in ["calculator", "get_time"]:
            assert tool.status == ToolStatus.ENABLED
            assert tool.is_available is True
            assert tool.description is not None
            assert tool.display_name is not None


@pytest.mark.asyncio
async def test_get_enabled_tools_for_workspace():
    """Test that get_enabled_tools_for_workspace filters by database status."""
    from chatter.core.tool_registry import ToolMetadata, ToolRegistry
    from chatter.models.toolserver import ServerTool, ToolStatus
    from langchain_core.tools import StructuredTool
    
    # Create mock session
    mock_session = AsyncMock()
    
    # Create mock tools in database - one enabled, one disabled
    mock_calculator_tool = MagicMock(spec=ServerTool)
    mock_calculator_tool.name = "calculator"
    mock_calculator_tool.status = ToolStatus.ENABLED
    
    mock_get_time_tool = MagicMock(spec=ServerTool)
    mock_get_time_tool.name = "get_time"
    mock_get_time_tool.status = ToolStatus.DISABLED  # This one is disabled
    
    # Mock the database query to return ALL tools (not just enabled)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        mock_calculator_tool,
        mock_get_time_tool,  # Include the disabled tool in the query result
    ]
    mock_session.execute.return_value = mock_result
    
    # Create a new tool registry and register test tools
    tool_registry = ToolRegistry()
    
    # Register calculator tool
    def calculate(expression: str) -> str:
        """Calculate a mathematical expression."""
        return str(eval(expression))
    
    calculator_tool = StructuredTool.from_function(
        func=calculate,
        name="calculator",
        description="Perform basic mathematical calculations",
    )
    
    calculator_metadata = ToolMetadata(
        name="calculator",
        description="Perform basic mathematical calculations",
        category="builtin",
    )
    
    tool_registry.register_tool(calculator_tool, calculator_metadata)
    
    # Register get_time tool
    def get_time() -> str:
        """Get the current time."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    get_time_tool = StructuredTool.from_function(
        func=get_time,
        name="get_time",
        description="Get the current date and time",
    )
    
    get_time_metadata = ToolMetadata(
        name="get_time",
        description="Get the current date and time",
        category="builtin",
    )
    
    tool_registry.register_tool(get_time_tool, get_time_metadata)
    
    # Get enabled tools
    enabled_tools = await tool_registry.get_enabled_tools_for_workspace(
        workspace_id="test-user",
        user_permissions=[],
        session=mock_session,
    )
    
    # Extract tool names
    tool_names = {
        getattr(tool, 'name', getattr(tool, 'name_', 'unknown'))
        for tool in enabled_tools
    }
    
    # calculator should be included since it's enabled in the database
    assert "calculator" in tool_names
    
    # get_time should be filtered out since it's explicitly disabled
    # If get_time exists in registry but is disabled in database, it should be filtered out
    assert "get_time" not in tool_names


@pytest.mark.asyncio
async def test_tools_not_in_database_are_enabled_by_default():
    """Test that tools registered but not in database are treated as enabled."""
    from chatter.core.tool_registry import ToolMetadata, ToolRegistry
    from chatter.models.toolserver import ServerTool, ToolStatus
    from langchain_core.tools import StructuredTool
    
    # Create mock session that returns empty database (no tools in DB)
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []  # No tools in database
    mock_session.execute.return_value = mock_result
    
    # Create a new tool registry and register a test tool
    tool_registry = ToolRegistry()
    
    def test_function(query: str) -> str:
        """Test function."""
        return f"Result for {query}"
    
    test_tool = StructuredTool.from_function(
        func=test_function,
        name="test_tool",
        description="A test tool",
    )
    
    metadata = ToolMetadata(
        name="test_tool",
        description="A test tool",
        category="test",
    )
    
    tool_registry.register_tool(test_tool, metadata)
    
    # Get enabled tools - should include test_tool even though it's not in database
    enabled_tools = await tool_registry.get_enabled_tools_for_workspace(
        workspace_id="test-user",
        user_permissions=[],
        session=mock_session,
    )
    
    # Extract tool names
    tool_names = {
        getattr(tool, 'name', getattr(tool, 'name_', 'unknown'))
        for tool in enabled_tools
    }
    
    # test_tool should be included since it's not in the database
    # (tools not in database are treated as enabled by default)
    assert "test_tool" in tool_names



def test_builtin_tools_exist():
    """Test that builtin tools are registered in the tool registry."""
    from chatter.core.tool_registry import tool_registry
    
    # Get all tools
    all_tools = tool_registry.list_all_tools()
    
    # Check that builtin tools exist
    tool_names = {name for name in all_tools.keys()}
    
    assert "calculator" in tool_names, "calculator should be registered"
    assert "get_time" in tool_names, "get_time should be registered"
    
    # Check metadata
    calculator_meta = all_tools.get("calculator")
    assert calculator_meta is not None
    assert calculator_meta.category == "builtin"
    
    get_time_meta = all_tools.get("get_time")
    assert get_time_meta is not None
    assert get_time_meta.category == "builtin"


if __name__ == "__main__":
    # Run tests manually for quick validation
    print("Testing builtin server initialization...")
    asyncio.run(test_builtin_server_initialization())
    print("✓ Builtin server initialization test passed")
    
    print("\nTesting get_enabled_tools_for_workspace...")
    asyncio.run(test_get_enabled_tools_for_workspace())
    print("✓ get_enabled_tools_for_workspace test passed")
    
    print("\nTesting builtin tools exist...")
    test_builtin_tools_exist()
    print("✓ Builtin tools exist test passed")
    
    print("\n✅ All tests passed!")
