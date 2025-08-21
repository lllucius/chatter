# Enhanced Tool Server Management

This implementation adds comprehensive support for managing multiple tool servers with CRUD APIs, enable/disable functionality, usage tracking, and automated maintenance.

## 🎯 Key Features

### 📊 Analytics & Tracking
- **Real-time Usage Analytics**: Track calls, errors, response times per server and tool
- **Performance Metrics**: Success rates, average response times, P95 percentiles
- **Historical Data**: Time-based filtering for analytics (1h, 24h, 7d, 30d, 90d)
- **Top/Failing Tools**: Automatically identify most used and problematic tools

### 🔧 Management & Control
- **Full CRUD Operations**: Create, read, update, delete tool servers
- **Granular Control**: Enable/disable at server and individual tool level
- **Bulk Operations**: Manage multiple servers simultaneously
- **Configuration Management**: Auto-start, auto-update, failure thresholds

### 🏥 Health & Monitoring
- **Automated Health Checks**: Periodic monitoring with auto-recovery
- **Server Availability**: Real-time status tracking
- **Tool Discovery**: Automatic capability detection and updates
- **Error Handling**: Consecutive failure tracking with auto-disable

### 🔄 Background Tasks
- **Health Monitoring**: Every 5 minutes with auto-restart capability
- **Capability Updates**: Hourly tool discovery and refresh
- **Data Cleanup**: Daily removal of old usage records (90+ days)
- **Graceful Management**: Proper startup/shutdown handling

## 🏗️ Architecture

### Database Models

#### ToolServer
- Stores server configuration (command, args, environment)
- Management settings (auto-start, auto-update, max failures)
- Health tracking (last checks, startup success/errors)
- User attribution for custom servers

#### ServerTool
- Individual tool metadata per server
- Usage statistics (calls, errors, response times)
- Availability status and bypass options
- Schema information for validation

#### ToolUsage
- Detailed usage logs for analytics
- Performance metrics per call
- User and conversation attribution
- Success/failure tracking with error details

### Service Layer

#### ToolServerService
- Database CRUD operations
- Server lifecycle management (start/stop/restart)
- Health checking and monitoring
- Usage tracking and analytics

#### Enhanced MCPToolService
- Integration with database persistence
- Automatic usage tracking on tool calls
- Dynamic server configuration
- Bypass mechanisms for unavailable tools

#### ToolServerScheduler
- Background task coordination
- Automated health monitoring
- Capability refresh scheduling
- Data maintenance and cleanup

## 📡 API Endpoints

### Server Management
```
POST   /api/v1/toolservers/servers              # Create server
GET    /api/v1/toolservers/servers              # List servers
GET    /api/v1/toolservers/servers/{id}         # Get server details
PUT    /api/v1/toolservers/servers/{id}         # Update server
DELETE /api/v1/toolservers/servers/{id}         # Delete server
```

### Server Control
```
POST   /api/v1/toolservers/servers/{id}/start   # Start server
POST   /api/v1/toolservers/servers/{id}/stop    # Stop server
POST   /api/v1/toolservers/servers/{id}/restart # Restart server
POST   /api/v1/toolservers/servers/{id}/enable  # Enable server
POST   /api/v1/toolservers/servers/{id}/disable # Disable server
```

### Tool Management
```
GET    /api/v1/toolservers/servers/{id}/tools   # Get server tools
POST   /api/v1/toolservers/tools/{id}/enable    # Enable tool
POST   /api/v1/toolservers/tools/{id}/disable   # Disable tool
```

### Analytics & Monitoring
```
GET    /api/v1/toolservers/servers/{id}/metrics # Server analytics
GET    /api/v1/toolservers/servers/{id}/health  # Health check
GET    /api/v1/analytics/toolservers            # System-wide analytics
```

### Bulk Operations
```
POST   /api/v1/toolservers/servers/bulk         # Bulk operations
```

## 🚀 Usage Examples

### Creating a Tool Server

```python
from chatter.schemas.toolserver import ToolServerCreate

server_data = ToolServerCreate(
    name="my_calculator",
    display_name="My Calculator Server",
    description="Custom calculator with advanced functions",
    command="python",
    args=["-m", "my_calculator_server"],
    env={"CALC_MODE": "advanced"},
    auto_start=True,
    auto_update=True,
    max_failures=3
)

# Via API
response = requests.post("/api/v1/toolservers/servers", json=server_data.dict())
```

### Getting Analytics

```python
# Server-specific analytics
response = requests.get(f"/api/v1/toolservers/servers/{server_id}/metrics")
metrics = response.json()

print(f"Total calls: {metrics['total_calls']}")
print(f"Success rate: {metrics['success_rate']}")
print(f"Avg response time: {metrics['avg_response_time_ms']}ms")

# System-wide analytics
response = requests.get("/api/v1/analytics/toolservers?period=7d")
analytics = response.json()

print(f"Active servers: {analytics['active_servers']}")
print(f"Total calls this week: {analytics['total_calls_week']}")
```

### Health Monitoring

```python
# Check server health
response = requests.get(f"/api/v1/toolservers/servers/{server_id}/health")
health = response.json()

if not health['is_responsive']:
    # Auto-restart if needed
    requests.post(f"/api/v1/toolservers/servers/{server_id}/restart")
```

### Bulk Operations

```python
from chatter.schemas.toolserver import BulkToolServerOperation

bulk_op = BulkToolServerOperation(
    server_ids=["server1", "server2", "server3"],
    operation="restart",
    parameters={}
)

response = requests.post("/api/v1/toolservers/servers/bulk", json=bulk_op.dict())
result = response.json()

print(f"Successful: {result['successful']}")
print(f"Failed: {result['failed']}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Tool server settings
TOOL_SERVER_HEALTH_CHECK_INTERVAL=300      # Health check interval (seconds)
TOOL_SERVER_AUTO_UPDATE_INTERVAL=3600      # Auto-update interval (seconds) 
TOOL_SERVER_CLEANUP_INTERVAL=86400         # Cleanup interval (seconds)
TOOL_SERVER_USAGE_RETENTION_DAYS=90        # Usage data retention (days)

# MCP settings
MCP_ENABLED=true                            # Enable MCP integration
MCP_SERVERS=filesystem,browser,calculator   # Default servers to load
```

### Built-in Servers

The system automatically initializes these built-in servers:

1. **Filesystem Server**: File system operations
   - Command: `npx -y @modelcontextprotocol/server-filesystem /tmp`
   - Tools: File read/write, directory listing, etc.

2. **Browser Server**: Web browsing and search
   - Command: `npx -y @modelcontextprotocol/server-brave-search`
   - Tools: Web search, page retrieval, etc.
   - Requires: `BRAVE_API_KEY` environment variable

3. **Calculator Server**: Mathematical operations
   - Command: `python -m mcp_math_server`
   - Tools: Basic and advanced calculations

## 🔒 Security & Permissions

### Access Control
- Server creation requires authentication
- User attribution for audit trails
- Built-in servers are system-managed
- Custom servers can be user-specific

### Security Features
- Input validation on all API endpoints
- SQL injection protection via SQLAlchemy
- Environment variable isolation per server
- Resource usage monitoring and limits

### Best Practices
- Use specific user accounts for tool servers
- Limit environment variable access
- Monitor resource usage and set appropriate limits
- Regular security audits of custom servers

## 📈 Performance Optimization

### Database Indexing
- Optimized indexes for common query patterns
- Time-based indexes for analytics queries
- Composite indexes for multi-column lookups

### Caching Strategy
- In-memory caching of frequently accessed servers
- Tool metadata caching with invalidation
- Analytics result caching with TTL

### Background Processing
- Asynchronous usage tracking
- Non-blocking health checks
- Parallel server operations where possible

## 🔍 Monitoring & Observability

### Metrics Available
- Server uptime and availability
- Tool usage patterns and trends
- Error rates and failure modes
- Response time distributions
- Resource utilization patterns

### Logging
- Structured logging with correlation IDs
- Comprehensive error tracking
- Performance timing information
- Audit trails for all operations

### Alerting
- Automated alerts for server failures
- Threshold-based performance warnings
- Usage anomaly detection
- Health check failure notifications

## 🛠️ Development & Testing

### Running Tests
```bash
# Run the comprehensive test suite
python test_toolserver.py

# Run specific test components
python -c "import test_toolserver; test_toolserver.test_api_schemas()"
```

### Database Migrations
```bash
# Apply the tool server migration
alembic upgrade add_tool_server_support

# Revert if needed
alembic downgrade base
```

### Development Setup
```bash
# Install dependencies
pip install -e .

# Start the application
python -m chatter.main

# Access API documentation
curl http://localhost:8000/docs
```

## 🤝 Contributing

When adding new tool servers or modifying existing functionality:

1. Follow the existing patterns for database models
2. Add comprehensive tests for new features
3. Update API documentation for new endpoints
4. Consider performance implications of changes
5. Ensure proper error handling and logging

## 📚 Additional Resources

- [MCP Protocol Documentation](https://github.com/modelcontextprotocol/mcp)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/en/20/orm/)
- [Pydantic Models](https://docs.pydantic.dev/)

This implementation provides a robust foundation for managing tool servers at scale with comprehensive monitoring, analytics, and automation capabilities.