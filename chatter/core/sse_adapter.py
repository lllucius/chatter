"""Adapter to integrate existing SSE system with unified event system."""

import asyncio
from typing import Any, Dict, Optional

from chatter.core.events import (
    EventCategory, 
    EventEmitter, 
    EventHandler, 
    UnifiedEvent, 
    event_router
)
from chatter.schemas.events import Event, EventType
from chatter.services.sse_events import sse_service
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class SSEEventEmitter(EventEmitter):
    """Adapter that makes the SSE service work with the unified event system."""
    
    def __init__(self):
        self._handlers: Dict[str, EventHandler] = {}
        
    async def emit(self, event: UnifiedEvent) -> bool:
        """Convert unified event to SSE event and emit it."""
        try:
            # Convert unified event to SSE event format
            sse_event = self._convert_to_sse_event(event)
            
            # Emit through SSE service
            await sse_service.broadcast_event(sse_event)
            
            logger.debug(
                "Successfully emitted SSE event",
                event_id=event.id,
                event_type=event.event_type,
                category=event.category
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to emit SSE event",
                event_id=event.id,
                event_type=event.event_type,
                error=str(e)
            )
            return False
    
    def add_handler(self, event_type: str, handler: EventHandler) -> str:
        """Add an event handler."""
        handler_id = f"sse_handler_{len(self._handlers)}"
        self._handlers[handler_id] = handler
        return handler_id
    
    def remove_handler(self, handler_id: str) -> bool:
        """Remove an event handler."""
        if handler_id in self._handlers:
            del self._handlers[handler_id]
            return True
        return False
    
    def _convert_to_sse_event(self, event: UnifiedEvent) -> Event:
        """Convert a unified event to SSE Event format."""
        # Map unified event types to SSE event types
        sse_event_type = self._map_event_type(event.event_type, event.category)
        
        # Prepare metadata including unified event info
        metadata = event.metadata.copy()
        metadata.update({
            "unified_event_id": event.id,
            "category": event.category.value,
            "priority": event.priority.value,
            "source_system": event.source_system,
        })
        
        if event.correlation_id:
            metadata["correlation_id"] = event.correlation_id
        if event.session_id:
            metadata["session_id"] = event.session_id
        
        return Event(
            id=event.id,
            type=sse_event_type,
            data=event.data,
            timestamp=event.timestamp,
            user_id=event.user_id,
            metadata=metadata
        )
    
    def _map_event_type(self, event_type: str, category: EventCategory) -> EventType:
        """Map unified event type to SSE EventType."""
        
        # Direct mappings for existing SSE event types
        sse_type_mapping = {
            # Document events
            "document.uploaded": EventType.DOCUMENT_UPLOADED,
            "document.processing_started": EventType.DOCUMENT_PROCESSING_STARTED,
            "document.processing_completed": EventType.DOCUMENT_PROCESSING_COMPLETED,
            "document.processing_failed": EventType.DOCUMENT_PROCESSING_FAILED,
            "document.processing_progress": EventType.DOCUMENT_PROCESSING_PROGRESS,
            
            # Backup events
            "backup.started": EventType.BACKUP_STARTED,
            "backup.completed": EventType.BACKUP_COMPLETED,
            "backup.failed": EventType.BACKUP_FAILED,
            "backup.progress": EventType.BACKUP_PROGRESS,
            
            # Job events
            "job.started": EventType.JOB_STARTED,
            "job.completed": EventType.JOB_COMPLETED,
            "job.failed": EventType.JOB_FAILED,
            "job.progress": EventType.JOB_PROGRESS,
            
            # Tool server events
            "tool_server.started": EventType.TOOL_SERVER_STARTED,
            "tool_server.stopped": EventType.TOOL_SERVER_STOPPED,
            "tool_server.health_changed": EventType.TOOL_SERVER_HEALTH_CHANGED,
            "tool_server.error": EventType.TOOL_SERVER_ERROR,
            
            # Chat events
            "conversation.started": EventType.CONVERSATION_STARTED,
            "conversation.ended": EventType.CONVERSATION_ENDED,
            "message.received": EventType.MESSAGE_RECEIVED,
            "message.sent": EventType.MESSAGE_SENT,
            
            # User events
            "user.registered": EventType.USER_REGISTERED,
            "user.updated": EventType.USER_UPDATED,
            "user.connected": EventType.USER_CONNECTED,
            "user.disconnected": EventType.USER_DISCONNECTED,
            "user.status_changed": EventType.USER_STATUS_CHANGED,
            
            # Plugin events
            "plugin.installed": EventType.PLUGIN_INSTALLED,
            "plugin.activated": EventType.PLUGIN_ACTIVATED,
            "plugin.deactivated": EventType.PLUGIN_DEACTIVATED,
            "plugin.error": EventType.PLUGIN_ERROR,
            
            # Agent events
            "agent.created": EventType.AGENT_CREATED,
            "agent.updated": EventType.AGENT_UPDATED,
        }
        
        # Try direct mapping first
        if event_type in sse_type_mapping:
            return sse_type_mapping[event_type]
        
        # Category-based fallback mapping
        if category == EventCategory.SECURITY:
            return EventType.SYSTEM_ALERT
        elif category == EventCategory.MONITORING:
            return EventType.SYSTEM_STATUS
        elif category == EventCategory.AUDIT:
            return EventType.SYSTEM_ALERT
        else:
            # Default fallback
            return EventType.SYSTEM_STATUS


class UnifiedEventToSSEForwarder:
    """Forwards unified events to SSE system for real-time delivery."""
    
    def __init__(self):
        self.sse_emitter = SSEEventEmitter()
        
    def setup_forwarding(self):
        """Set up event forwarding from unified system to SSE."""
        
        # Register SSE emitter for real-time events
        event_router.register_emitter(EventCategory.REALTIME, self.sse_emitter)
        
        # Forward security events to SSE for real-time monitoring
        event_router.add_category_handler(
            EventCategory.SECURITY,
            self._forward_security_event
        )
        
        # Forward critical audit events to SSE
        event_router.add_category_handler(
            EventCategory.AUDIT,
            self._forward_critical_audit_event
        )
        
        logger.info("Set up unified event to SSE forwarding")
    
    def _forward_security_event(self, event: UnifiedEvent) -> None:
        """Forward security events to SSE for real-time alerts."""
        # Convert to real-time event and route through SSE
        realtime_event = UnifiedEvent(
            category=EventCategory.REALTIME,
            event_type=f"security.{event.event_type}",
            data=event.data,
            metadata=event.metadata,
            user_id=event.user_id,
            session_id=event.session_id,
            correlation_id=event.correlation_id,
            priority=event.priority,
            source_system="security_monitor"
        )
        
        # Emit asynchronously
        asyncio.create_task(self.sse_emitter.emit(realtime_event))
    
    def _forward_critical_audit_event(self, event: UnifiedEvent) -> None:
        """Forward critical audit events to SSE for real-time monitoring."""
        # Only forward high priority audit events
        if event.priority.value in ["high", "critical"]:
            realtime_event = UnifiedEvent(
                category=EventCategory.REALTIME,
                event_type=f"audit.{event.event_type}",
                data=event.data,
                metadata=event.metadata,
                user_id=event.user_id,
                session_id=event.session_id,
                correlation_id=event.correlation_id,
                priority=event.priority,
                source_system="audit_logger"
            )
            
            # Emit asynchronously
            asyncio.create_task(self.sse_emitter.emit(realtime_event))


# Global forwarder instance
sse_forwarder = UnifiedEventToSSEForwarder()


def setup_sse_integration():
    """Set up integration between unified event system and SSE."""
    sse_forwarder.setup_forwarding()
    logger.info("SSE integration with unified event system is ready")


# Convenience functions for emitting events that go through SSE
async def emit_realtime_event(
    event_type: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    **kwargs
) -> bool:
    """Emit a real-time event through SSE."""
    from chatter.core.events import create_realtime_event, emit_event
    
    event = create_realtime_event(
        event_type=event_type,
        data=data,
        user_id=user_id,
        **kwargs
    )
    
    return await emit_event(event)


async def emit_system_alert(
    message: str,
    severity: str = "info",
    user_id: Optional[str] = None,
    **kwargs
) -> bool:
    """Emit a system alert through SSE."""
    return await emit_realtime_event(
        event_type="system.alert",
        data={
            "message": message,
            "severity": severity,
            **kwargs.get("data", {})
        },
        user_id=user_id,
        **{k: v for k, v in kwargs.items() if k != "data"}
    )


async def emit_user_event(
    event_type: str,
    user_id: str,
    data: Dict[str, Any],
    **kwargs
) -> bool:
    """Emit a user-specific event through SSE."""
    return await emit_realtime_event(
        event_type=f"user.{event_type}",
        data=data,
        user_id=user_id,
        **kwargs
    )