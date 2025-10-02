# Builtin Tools Database Integration - Implementation Summary

## Problem Statement
The builtin MCP tools (calculator and get_time) could not be enabled or disabled because they were not exposed to the user and did not exist in the database.

## Solution Overview
The solution adds builtin tools to the database as ServerTool records associated with a special "builtin_tools" server. This allows users to manage these tools through the existing toolserver API endpoints, just like any other tool.

## Implementation Details

### 1. Database Schema Updates (No migration needed)
The existing `ToolServer` and `ServerTool` models already support what we need. We simply add new records during initialization.

### 2. Modified Files

#### chatter/services/toolserver.py
- **Modified `initialize_builtin_servers()` method**:
  - Added a new "builtin_tools" server entry with embedded tool definitions
  - Removed the old "calculator" server (which was incorrect - it was a server, not a tool container)
  - Created ServerTool records for `calculator` and `get_time` tools
  - Added logic to create tools when server is first initialized
  - Added logic to add missing tools if server already exists (idempotent)

Key changes:
```python
builtin_servers = [
    {
        "name": "builtin_tools",
        "display_name": "Built-in Tools",
        "description": "Core built-in tools (calculator, get_time)",
        "command": None,
        "args": None,
        "env": None,
        "tools": [
            {
                "name": "calculator",
                "display_name": "Calculator",
                "description": "Perform basic mathematical calculations",
            },
            {
                "name": "get_time",
                "display_name": "Get Time",
                "description": "Get the current date and time...",
            },
        ],
    },
    # ... other servers
]
```

#### chatter/core/tool_registry.py
- **Added `get_enabled_tools_for_workspace()` method**:
  - Async method that checks the database for tool status
  - Filters tools based on ToolStatus.ENABLED
  - Maintains backward compatibility (works without session parameter)
  - Uses existing `get_tools_for_workspace()` as base filter

Key changes:
```python
async def get_enabled_tools_for_workspace(
    self,
    workspace_id: str,
    user_permissions: list[str] | None = None,
    session=None,
) -> list[Any]:
    """Get enabled tools for a workspace, checking database status."""
    # Get all tools from registry
    registry_tools = self.get_tools_for_workspace(
        workspace_id, user_permissions
    )
    
    if not session:
        return registry_tools  # Backward compatible
    
    # Get enabled tools from database
    result = await session.execute(
        select(ServerTool).where(
            ServerTool.status == ToolStatus.ENABLED
        )
    )
    enabled_tool_names = {tool.name for tool in result.scalars().all()}
    
    # Filter to only enabled tools
    return [
        tool for tool in registry_tools
        if self._get_tool_name(tool) in enabled_tool_names
    ]
```

#### chatter/services/workflow_execution.py
- **Updated 4 locations** where tools are loaded:
  - Changed from `tool_registry.get_tools_for_workspace()` to `await tool_registry.get_enabled_tools_for_workspace()`
  - Added `session=self.session` parameter to enable database checking
  - Now respects database tool status during workflow execution

### 3. Testing

#### tests/test_builtin_tools_database.py
Created comprehensive test coverage:
- `test_builtin_server_initialization()`: Verifies builtin_tools server and tools are created
- `test_get_enabled_tools_for_workspace()`: Verifies database filtering works
- `test_builtin_tools_exist()`: Verifies tools are in the registry

## How It Works

1. **On Application Startup**:
   - `initialize_builtin_servers()` is called from `main.py`
   - Creates "builtin_tools" server in database (if not exists)
   - Creates ServerTool records for "calculator" and "get_time"
   - Both tools are created with status=ENABLED by default

2. **When Loading Tools for Workflow Execution**:
   - Workflow execution calls `get_enabled_tools_for_workspace()`
   - Method queries database for tools with status=ENABLED
   - Filters in-memory registry tools to only include enabled ones
   - Returns filtered list to workflow

3. **When User Manages Tools**:
   - User can call existing toolserver API endpoints:
     - `GET /api/v1/toolservers/servers` - List servers (includes builtin_tools)
     - `GET /api/v1/toolservers/servers/{server_id}` - Get server with tools
     - `PUT /api/v1/toolservers/servers/{server_id}/tools/{tool_id}/enable` - Enable tool
     - `PUT /api/v1/toolservers/servers/{server_id}/tools/{tool_id}/disable` - Disable tool
   - Changes are persisted to database
   - Next workflow execution will respect new status

## Benefits

1. **User Control**: Users can now enable/disable builtin tools through the UI/API
2. **Consistency**: Builtin tools are managed the same way as other tools
3. **Minimal Changes**: Solution uses existing infrastructure
4. **Backward Compatible**: Tools work with or without database session
5. **Idempotent**: Re-running initialization won't duplicate tools

## Migration Notes

No database migration is required. The changes will take effect on the next application restart when `initialize_builtin_servers()` runs.

Existing installations will automatically:
1. Create the "builtin_tools" server
2. Add "calculator" and "get_time" as ServerTool records
3. Enable both tools by default

## Testing Instructions

1. Start the application
2. Query the toolservers API to see builtin_tools server
3. Disable a builtin tool via API
4. Attempt to use that tool in a conversation
5. Verify the tool is not available
6. Re-enable the tool
7. Verify the tool is available again

## API Examples

### List all tool servers (including builtin)
```bash
GET /api/v1/toolservers/servers?includeBuiltin=true
```

### Get builtin_tools server with tools
```bash
GET /api/v1/toolservers/servers/{builtin_tools_server_id}
```

### Disable calculator tool
```bash
PUT /api/v1/toolservers/servers/{server_id}/tools/{calculator_tool_id}/disable
```

### Enable calculator tool
```bash
PUT /api/v1/toolservers/servers/{server_id}/tools/{calculator_tool_id}/enable
```
