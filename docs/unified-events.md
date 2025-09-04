# Unified Event System Documentation

The Chatter platform now features a unified event system that consolidates all event handling into a cohesive, well-structured system while maintaining backward compatibility with existing specialized systems.

## Overview

The unified event system provides:
- **Consistent Event Structure**: All events use the same base `UnifiedEvent` format
- **Event Categories**: Events are organized into logical categories (REALTIME, SECURITY, AUDIT, etc.)
- **Event Priorities**: Events have priorities (LOW, NORMAL, HIGH, CRITICAL) for proper routing
- **Cross-System Integration**: Events can be automatically routed between different subsystems
- **Enhanced Monitoring**: Centralized tracking and statistics for all events
- **Backward Compatibility**: Existing event APIs continue to work unchanged

## Event Categories

The system organizes events into the following categories:

- **`REALTIME`**: Server-sent events for real-time UI updates (document processing, user actions, etc.)
- **`SECURITY`**: Security monitoring events (login failures, suspicious activity, etc.)
- **`AUDIT`**: Compliance and audit logging events (resource operations, administrative actions)
- **`MONITORING`**: System performance and health monitoring events
- **`STREAMING`**: Real-time chat token streaming events
- **`ANALYTICS`**: A/B testing and analytics events
- **`WORKFLOW`**: Workflow execution and state change events

## Event Priorities

Events are assigned priorities that affect how they're processed and routed:

- **`LOW`**: Background analytics, non-critical updates
- **`NORMAL`**: Standard application events, user actions
- **`HIGH`**: Security alerts, important system events
- **`CRITICAL`**: System failures, emergency alerts (auto-routed to real-time)

## Core Components

### UnifiedEvent

The base event structure used throughout the system:

```python
@dataclass
class UnifiedEvent:
    # Event classification (required)
    category: EventCategory
    event_type: str
    
    # Core identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    # Event data
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    # Processing info
    priority: EventPriority = EventPriority.NORMAL
    source_system: Optional[str] = None
```

### EventRouter

Central routing system that dispatches events to appropriate handlers and emitters:

```python
router = EventRouter()

# Add handlers for different scopes
router.add_global_handler(my_handler)                    # All events
router.add_category_handler(EventCategory.SECURITY, security_handler)  # Category-specific
router.add_type_handler("user.login", login_handler)     # Event type-specific

# Route events
await router.route_event(event)
```

### UnifiedEventManager

Central manager that coordinates all event systems:

```python
from chatter.core.unified_events import (
    initialize_event_system,
    emit_realtime_event,
    emit_security_event,
    emit_audit_event,
    get_event_stats
)

# Initialize the system
await initialize_event_system()

# Emit different types of events
await emit_realtime_event("document.uploaded", {"document_id": "123"})
await emit_security_event("auth.login_failure", {"ip": "192.168.1.1"})
await emit_audit_event("model.delete", {"model_id": "456"})
```

## Integration with Existing Systems

### SSE (Server-Sent Events)

The existing SSE system is enhanced to work with unified events:

```python
# Existing SSE events automatically emit through unified system
from chatter.services.sse_events import sse_service

# This now also emits through unified system
await sse_service.trigger_event(
    EventType.DOCUMENT_UPLOADED,
    {"document_id": "123"},
    user_id="user_456"
)
```

### Security Monitoring

Security events are automatically routed to both monitoring and audit systems:

```python
from chatter.core.security_adapter import emit_login_event

# Emits security event + audit event + real-time alert
await emit_login_event(
    success=False,
    user_id="user_123",
    ip_address="192.168.1.1",
    details={"reason": "invalid_password"}
)
```

### Audit Logging

Audit events are automatically stored and can trigger real-time notifications:

```python
from chatter.core.audit_adapter import emit_resource_audit

# Emits audit event + real-time notification for critical operations
await emit_resource_audit(
    action="delete",
    resource_type="model",
    resource_id="model_123",
    success=True,
    user_id="admin_456"
)
```

## Frontend Integration

The frontend SSE manager is enhanced to support unified events:

```typescript
import { useSSE } from './services/sse-context';

function MyComponent() {
  const { on, onCategory, onHighPriority } = useSSE();
  
  useEffect(() => {
    // Listen to specific event types
    const unsubscribe1 = on('document.uploaded', (event) => {
      console.log('Document uploaded:', event);
    });
    
    // Listen to all security events
    const unsubscribe2 = onCategory('security', (event) => {
      console.log('Security event:', event);
    });
    
    // Listen to high priority events
    const unsubscribe3 = onHighPriority((event) => {
      showCriticalAlert(event);
    });
    
    return () => {
      unsubscribe1();
      unsubscribe2();
      unsubscribe3();
    };
  }, [on, onCategory, onHighPriority]);
}
```

## Cross-System Event Routing

The unified system automatically routes events between subsystems:

1. **High Priority → Real-time**: High/critical priority events are automatically converted to real-time events
2. **Security → Audit**: Security events automatically create corresponding audit log entries
3. **Critical → Notifications**: Critical events can trigger browser notifications

## Event Flow Example

When a security event occurs:

```python
# 1. Emit security event
await emit_security_event(
    "auth.login_failure", 
    {"ip": "192.168.1.1", "attempts": 5},
    priority=EventPriority.HIGH
)

# This triggers:
# 2. Security monitoring processes the event
# 3. Audit log entry is automatically created
# 4. High priority triggers real-time SSE event
# 5. Frontend receives real-time notification
# 6. Browser notification shown to administrators
```

## Usage Patterns

### Basic Event Emission

```python
# Real-time user notification
await emit_realtime_event(
    "document.processing_completed",
    {
        "document_id": "doc_123",
        "chunks_created": 25,
        "processing_time": 5.2
    },
    user_id="user_123"
)

# Security alert
await emit_security_event(
    "suspicious.brute_force",
    {
        "ip_address": "192.168.1.100",
        "attempts": 10,
        "blocked": True
    },
    priority=EventPriority.CRITICAL
)

# Audit logging
await emit_audit_event(
    "provider.delete",
    {
        "provider_id": "prov_456",
        "provider_name": "Custom OpenAI",
        "result": "success"
    },
    user_id="admin_789"
)
```

### Event Handling

```python
def handle_document_events(event: UnifiedEvent):
    if event.event_type.startswith("document."):
        print(f"Document event: {event.event_type}")
        # Process document event

def handle_critical_events(event: UnifiedEvent):
    if event.priority == EventPriority.CRITICAL:
        print(f"CRITICAL: {event.event_type}")
        # Send alerts, notifications, etc.

# Register handlers
event_router.add_type_handler("document.*", handle_document_events)
event_router.add_global_handler(handle_critical_events)
```

### Statistics and Monitoring

```python
# Get system-wide event statistics
stats = get_event_stats()
print(f"Total events processed: {stats['processed']}")
print(f"Events by category: {stats['by_category']}")
print(f"High priority events: {stats['by_priority']['high']}")
```

## Configuration

The unified event system respects existing configuration settings and adds new ones:

```python
# SSE Configuration (existing)
sse_queue_maxsize = 100
sse_max_connections_per_user = 5
sse_keepalive_timeout = 30

# Unified Event Configuration (new)
unified_events_enabled = True
cross_system_routing = True
high_priority_notifications = True
```

## Migration Guide

### For Existing Code

No changes are required for existing code. All existing event APIs continue to work:

```python
# This still works exactly as before
from chatter.services.sse_events import trigger_document_uploaded
await trigger_document_uploaded("doc_123", "file.pdf", "user_456")

# But now also benefits from unified system features
```

### For New Code

Use the unified system for new event handling:

```python
# Instead of calling SSE directly
from chatter.core.unified_events import emit_realtime_event
await emit_realtime_event("custom.event", {"data": "value"})

# Instead of separate security handling
from chatter.core.unified_events import emit_security_event
await emit_security_event("custom.security", {"alert": "data"})
```

## Best Practices

1. **Use Appropriate Categories**: Choose the right category for your event type
2. **Set Proper Priorities**: Use HIGH/CRITICAL sparingly for truly important events
3. **Include Relevant Metadata**: Add correlation IDs, session IDs for better tracing
4. **Handle Errors Gracefully**: Event emission should not break application flow
5. **Monitor Event Volume**: Use statistics to monitor system health and performance

## Troubleshooting

### Common Issues

1. **Events Not Appearing**: Check if the unified system is initialized
2. **High Memory Usage**: Monitor event queue sizes and processing rates
3. **Missing Events**: Verify event routing configuration and handler registration
4. **Frontend Not Updating**: Check SSE connection status and event subscriptions

### Debug Information

```python
# Check system status
from chatter.core.unified_events import unified_event_manager
print(f"Initialized: {unified_event_manager.is_initialized()}")
print(f"Stats: {unified_event_manager.get_stats()}")

# Check SSE connection (frontend)
const stats = sseEventManager.getConnectionStats();
console.log('SSE Stats:', stats);
```

The unified event system provides a robust, scalable foundation for all event handling in the Chatter platform while maintaining full backward compatibility with existing systems.