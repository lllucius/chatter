# Server-Sent Events (SSE) API Documentation

The Chatter platform provides real-time updates through Server-Sent Events (SSE), replacing the previous webhook system. This allows clients to receive live updates about system operations directly through a persistent HTTP connection.

## Overview

The SSE system provides real-time notifications for:
- **Backup Operations**: Start, progress, completion, and failures
- **Background Jobs**: Job status changes and results
- **Tool Servers**: Server start/stop, health changes, errors
- **Document Processing**: Upload, processing progress, completion
- **System Events**: General system alerts and status updates

## Authentication

All SSE endpoints require authentication using a Bearer token:

```
Authorization: Bearer <your_access_token>
```

## API Endpoints

### Stream Events

**GET** `/api/v1/events/stream`

Opens a persistent SSE connection to receive real-time events for the authenticated user.

**Response Format:**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**Event Format:**
```
id: <event_id>
event: <event_type>
data: {"id": "<event_id>", "type": "<event_type>", "data": {...}, "timestamp": "2024-01-01T12:00:00Z", "metadata": {...}}
```

### Admin Stream

**GET** `/api/v1/events/admin/stream`

Opens a persistent SSE connection to receive ALL system events (admin-only).

### Get Statistics

**GET** `/api/v1/events/stats`

Returns current SSE connection statistics.

**Response:**
```json
{
  "total_connections": 10,
  "your_connections": 2
}
```

### Test Events

**POST** `/api/v1/events/test-event`

Triggers a test event for the current user.

**POST** `/api/v1/events/broadcast-test`

Triggers a broadcast test event for all users.

## Event Types

### Backup Events

- `backup.started` - Backup operation started
- `backup.completed` - Backup operation completed successfully  
- `backup.failed` - Backup operation failed
- `backup.progress` - Backup progress update

**Example:**
```json
{
  "id": "event_123",
  "type": "backup.completed", 
  "data": {
    "backup_id": "backup_20240101_120000",
    "backup_path": "/backups/backup_20240101_120000.tar.gz",
    "completed_at": "2024-01-01T12:05:00Z"
  },
  "timestamp": "2024-01-01T12:05:00Z",
  "metadata": {}
}
```

### Job Events

- `job.started` - Background job started
- `job.completed` - Job completed successfully
- `job.failed` - Job failed
- `job.progress` - Job progress update

**Example:**
```json
{
  "id": "event_124", 
  "type": "job.completed",
  "data": {
    "job_id": "job_456",
    "job_name": "document_processing",
    "result": {"processed_documents": 5},
    "completed_at": "2024-01-01T12:10:00Z"
  },
  "timestamp": "2024-01-01T12:10:00Z",
  "metadata": {}
}
```

### Tool Server Events

- `tool_server.started` - Tool server started
- `tool_server.stopped` - Tool server stopped  
- `tool_server.health_changed` - Server health status changed
- `tool_server.error` - Tool server error occurred

**Example:**
```json
{
  "id": "event_125",
  "type": "tool_server.health_changed",
  "data": {
    "server_id": "server_789",
    "server_name": "python-tools",
    "health_status": "healthy",
    "details": {
      "is_running": true,
      "is_responsive": true, 
      "tools_count": 12
    },
    "checked_at": "2024-01-01T12:15:00Z"
  },
  "timestamp": "2024-01-01T12:15:00Z",
  "metadata": {}
}
```

### Document Events

- `document.uploaded` - Document uploaded
- `document.processing_started` - Document processing started
- `document.processing_completed` - Document processing completed
- `document.processing_failed` - Document processing failed
- `document.processing_progress` - Document processing progress

**Example:**
```json
{
  "id": "event_126",
  "type": "document.processing_completed", 
  "data": {
    "document_id": "doc_101",
    "result": {
      "chunks_created": 25,
      "text_length": 5000,
      "processing_time": 3.5
    },
    "completed_at": "2024-01-01T12:20:00Z"
  },
  "timestamp": "2024-01-01T12:20:00Z",
  "user_id": "user_123",
  "metadata": {}
}
```

### System Events

- `system.alert` - System alert or notification
- `system.status` - System status update
- `connection.established` - SSE connection established (initial event)

## Client Implementation

### JavaScript Example

```javascript
// Establish SSE connection
const eventSource = new EventSource('/api/v1/events/stream', {
  headers: {
    'Authorization': 'Bearer ' + accessToken
  }
});

// Handle connection events
eventSource.onopen = function(event) {
  console.log('SSE connection opened');
};

// Handle all events
eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received event:', data);
  handleEvent(data);
};

// Handle specific event types
eventSource.addEventListener('backup.completed', function(event) {
  const data = JSON.parse(event.data);
  showNotification('Backup completed: ' + data.data.backup_id);
});

eventSource.addEventListener('job.failed', function(event) {
  const data = JSON.parse(event.data);
  showError('Job failed: ' + data.data.job_name + ' - ' + data.data.error);
});

// Handle connection errors
eventSource.onerror = function(event) {
  console.error('SSE connection error');
};

// Close connection when done
function cleanup() {
  if (eventSource) {
    eventSource.close();
  }
}
```

### Python Example

```python
import httpx
import json

# Using httpx-sse for Python SSE client
from httpx_sse import connect_sse

async def listen_to_events(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        async with connect_sse(
            client, "GET", "http://localhost:8000/api/v1/events/stream", 
            headers=headers
        ) as event_source:
            async for sse in event_source.aiter_sse():
                event_data = json.loads(sse.data)
                print(f"Received event: {event_data['type']}")
                await handle_event(event_data)

async def handle_event(event_data):
    event_type = event_data["type"]
    data = event_data["data"]
    
    if event_type == "backup.completed":
        print(f"Backup completed: {data['backup_id']}")
    elif event_type == "job.failed":
        print(f"Job failed: {data['job_name']} - {data['error']}")
    # Handle other event types...
```

## Testing

Use the included `sse_test_client.html` file to test the SSE implementation:

1. Open `sse_test_client.html` in your browser
2. Enter your API URL and credentials
3. Connect to the SSE stream
4. Trigger test events to verify functionality
5. Monitor real-time events as they occur

## Migration from Webhooks

The SSE system replaces the previous webhook system with the following advantages:

- **Real-time**: Events are delivered immediately without polling
- **Persistent**: Single connection handles all events
- **User-specific**: Events can be filtered per user automatically
- **No setup**: No need to configure external webhook endpoints
- **Built-in**: Integrated directly into the web application

### Key Differences

| Webhooks | SSE |
|----------|-----|
| Required external endpoint setup | Built-in browser support |
| HTTP POST requests for each event | Persistent HTTP connection |
| Manual retry logic needed | Automatic reconnection |
| No real-time guarantees | Immediate event delivery |
| Complex authentication setup | Uses existing auth tokens |

## Error Handling

- **Connection Lost**: Browsers automatically attempt to reconnect
- **Authentication**: 401 errors indicate invalid/expired tokens
- **Rate Limiting**: Server may close connections if too many events
- **Heartbeat**: Periodic keepalive events maintain connection

## Performance

- **Scalability**: Designed to handle hundreds of concurrent connections
- **Memory**: Connection cleanup prevents memory leaks
- **Bandwidth**: Efficient JSON event format minimizes data transfer
- **Filtering**: User-specific events reduce unnecessary traffic

## Security

- **Authentication**: All endpoints require valid Bearer tokens
- **Authorization**: Users only receive their own events (except admin)
- **CORS**: Proper CORS headers for cross-origin requests
- **Rate Limiting**: Protection against connection abuse