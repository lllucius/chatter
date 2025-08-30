# Remote Tool Server Implementation Guide

This document describes the new remote tool server implementation that replaces the previous built-in server approach.

## Overview

The tool server system has been completely refactored to support:

- **Remote HTTP/SSE servers only** - No more built-in process-based servers
- **OAuth 2.0 authentication** - Full client credentials flow support
- **Role-based access control** - Fine-grained permissions for tools and servers
- **Enhanced monitoring** - Better health checking and usage tracking

## Architecture Changes

### Before (Built-in Servers)
```
Chatter → Local Process → Tool Execution
         (filesystem, browser, calculator)
```

### After (Remote Servers)
```
Chatter → HTTP/SSE → Remote MCP Server → Tool Execution
         (OAuth)      (any location)
```

## Remote Server Configuration

### Basic HTTP Server
```json
{
  "name": "my_tools",
  "display_name": "My Tool Server",
  "description": "Remote tools for my application",
  "base_url": "https://api.mytools.com",
  "transport_type": "http",
  "timeout": 30,
  "auto_start": true
}
```

### Server with OAuth Authentication
```json
{
  "name": "secure_tools",
  "display_name": "Secure Tool Server", 
  "base_url": "https://secure-api.example.com",
  "transport_type": "http",
  "oauth_config": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "token_url": "https://auth.example.com/oauth/token",
    "scope": "tools:read tools:execute"
  },
  "headers": {
    "X-API-Version": "v1",
    "User-Agent": "Chatter/1.0"
  }
}
```

### Server-Sent Events (SSE) Server
```json
{
  "name": "streaming_tools",
  "display_name": "Streaming Tool Server",
  "base_url": "https://stream-api.example.com", 
  "transport_type": "sse",
  "timeout": 60
}
```

## API Endpoints

### Server Management

#### Create Remote Server
```http
POST /api/v1/toolservers/servers
Content-Type: application/json

{
  "name": "remote_server",
  "display_name": "Remote Server",
  "base_url": "https://api.example.com",
  "transport_type": "http",
  "oauth_config": { ... },
  "auto_start": true
}
```

#### Enable/Disable Server
```http
POST /api/v1/toolservers/servers/{server_id}/enable
POST /api/v1/toolservers/servers/{server_id}/disable
```

#### Refresh Server Tools
```http
POST /api/v1/toolservers/servers/{server_id}/refresh-tools
```

### Access Control

#### Grant Tool Permission
```http
POST /api/v1/toolservers/permissions
Content-Type: application/json

{
  "user_id": "user123",
  "tool_id": "tool456",  // or "server_id" for server-wide access
  "access_level": "execute",
  "rate_limit_per_hour": 100,
  "rate_limit_per_day": 1000,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

#### Create Role Access Rule
```http
POST /api/v1/toolservers/role-access
Content-Type: application/json

{
  "role": "power_user",
  "tool_pattern": "data_*",  // Tools starting with "data_"
  "access_level": "execute",
  "default_rate_limit_per_hour": 50
}
```

#### Check Tool Access
```http
POST /api/v1/toolservers/access-check
Content-Type: application/json

{
  "user_id": "user123",
  "tool_name": "data_processor",
  "server_name": "analytics_server"
}
```

Response:
```json
{
  "allowed": true,
  "access_level": "execute",
  "rate_limit_remaining_hour": 95,
  "rate_limit_remaining_day": 950,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

## Remote Server Requirements

### HTTP Transport

Your remote MCP server must implement these endpoints:

#### Tool Discovery
```http
GET /tools
```
Response:
```json
{
  "tools": [
    {
      "name": "process_data",
      "display_name": "Process Data",
      "description": "Process incoming data",
      "args_schema": {
        "type": "object",
        "properties": {
          "data": {"type": "string"},
          "format": {"type": "string", "enum": ["json", "csv"]}
        }
      }
    }
  ]
}
```

#### Tool Execution
```http
POST /tools/{tool_name}/call
Content-Type: application/json

{
  "arguments": {
    "data": "sample data",
    "format": "json"
  }
}
```

#### Health Check
```http
GET /health
```

### SSE Transport

For Server-Sent Events, implement:

#### Tool Discovery Stream
```http
GET /tools/stream
```
Events:
```
event: tool
data: {"name": "tool1", "description": "Tool 1", ...}

event: tool  
data: {"name": "tool2", "description": "Tool 2", ...}

event: end
data: {}
```

#### Tool Execution Stream
```http
POST /tools/{tool_name}/call
```
Events:
```
event: result
data: {"status": "success", "data": {...}}
```

## OAuth 2.0 Integration

The system supports OAuth 2.0 Client Credentials flow:

1. **Token Request**: Automatically requests access tokens using client credentials
2. **Token Refresh**: Handles token expiration and refresh
3. **Request Authentication**: Adds `Authorization: Bearer {token}` to requests
4. **Error Handling**: Retries on 401 responses with fresh tokens

### OAuth Configuration
```python
oauth_config = OAuthConfig(
    client_id="your_client_id",
    client_secret="your_client_secret", 
    token_url="https://auth.provider.com/oauth/token",
    scope="api:read api:write"  # Optional
)
```

## Role-Based Access Control

### Access Levels
- **none**: No access
- **read**: Can view tool information only
- **execute**: Can view and execute tools
- **admin**: Full tool management access

### User Roles
- **guest**: Limited read access
- **user**: Basic tool execution
- **power_user**: Extended tool access
- **admin**: Server management
- **super_admin**: Full system access

### Permission Priority
1. **Explicit permissions** (highest priority)
2. **Role-based patterns** 
3. **Default deny** (lowest priority)

### Pattern Matching
```python
# Tool patterns
"data_*"      # All tools starting with "data_"
"*_processor" # All tools ending with "_processor"
"analytics"   # Exact match

# Server patterns  
"internal_*"  # All servers starting with "internal_"
"*.company.com" # All servers in company.com domain
```

## Migration from Built-in Servers

### 1. Update Dependencies
```bash
pip install --upgrade "mcp==1.13.0"
```

### 2. Run Database Migration
```bash
alembic upgrade head
```

### 3. Remove Built-in Server Configurations
Remove these from your configuration:
- `mcp_servers` list
- Built-in server commands and arguments

### 4. Add Remote Servers
Use the API or admin interface to add remote servers:

```python
# Previous built-in filesystem server
{
  "command": "npx @modelcontextprotocol/server-filesystem /tmp"
}

# New remote equivalent
{
  "name": "filesystem",
  "base_url": "https://fs-server.mycompany.com",
  "transport_type": "http"
}
```

### 5. Configure Access Control
Set up role-based access for your users:

```python
# Default user access to common tools
{
  "role": "user",
  "tool_pattern": "file_*",
  "access_level": "execute",
  "default_rate_limit_per_hour": 100
}

# Admin access to all tools
{
  "role": "admin", 
  "tool_pattern": "*",
  "access_level": "admin"
}
```

## Security Considerations

### Authentication
- **Always use HTTPS** for remote servers
- **Store OAuth secrets securely** - never in plain text
- **Rotate credentials regularly**
- **Use least privilege principle** for access levels

### Rate Limiting
- **Set appropriate limits** for each user role
- **Monitor usage patterns** to detect abuse
- **Implement gradual backoff** for excessive requests

### Network Security
- **Whitelist server IPs** if possible
- **Use VPN/private networks** for internal tools
- **Implement request signing** for additional security
- **Log all tool executions** for audit trails

## Monitoring and Troubleshooting

### Health Checks
```python
# Manual health check
response = await mcp_service.health_check()
print(response)  # Shows all server statuses

# Server-specific check
health = await tool_server_service.health_check_server(server_id)
```

### Usage Analytics
```python
# Get server metrics
metrics = await tool_server_service.get_server_analytics(server_id)

# Get tool usage
usage = await tool_server_service.get_tool_usage_stats(tool_id)
```

### Common Issues

#### OAuth Token Errors
```python
# Check OAuth configuration
if not server.oauth_client_id:
    print("Missing OAuth client ID")

# Verify token endpoint
response = requests.post(token_url, data={...})
if response.status_code != 200:
    print(f"Token request failed: {response.text}")
```

#### Connection Timeouts
```python
# Increase timeout for slow servers
server_config.timeout = 60  # seconds

# Check network connectivity
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(f"{server.base_url}/health")
```

#### Tool Discovery Issues
```python
# Manually trigger tool discovery
success = await mcp_service.refresh_server_tools(server_name)
if not success:
    print("Tool discovery failed - check server logs")
```

## Examples

See the `examples/` directory for:
- Sample remote server implementations
- OAuth provider setup
- Access control configurations
- Migration scripts

## Support

For questions and issues:
- Check the server logs for detailed error messages
- Verify OAuth credentials and endpoints
- Test remote server connectivity independently
- Review access control rules and permissions