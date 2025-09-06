"""Unified event system interface for all event handling in Chatter.

This module provides a unified interface for all event types in the system,
allowing different subsystems to emit and listen to events consistently.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Union
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class EventCategory(str, Enum):
    """High-level categories for all events in the system."""
    
    # Real-time SSE events
    REALTIME = "realtime"
    
    # Security and compliance events
    SECURITY = "security"
    AUDIT = "audit"
    
    # System performance and monitoring
    MONITORING = "monitoring"
    
    # Chat and streaming events
    STREAMING = "streaming"
    
    # A/B testing and analytics
    ANALYTICS = "analytics"
    
    # Application workflow events
    WORKFLOW = "workflow"


class EventPriority(str, Enum):
    """Priority levels for events."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class UnifiedEvent:
    """Base unified event structure that all events should conform to."""
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "category": self.category.value,
            "event_type": self.event_type,
            "data": self.data,
            "metadata": self.metadata,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "priority": self.priority.value,
            "source_system": self.source_system,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnifiedEvent":
        """Create event from dictionary."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif timestamp is None:
            timestamp = datetime.now(UTC)
            
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=timestamp,
            category=EventCategory(data["category"]),
            event_type=data["event_type"],
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            correlation_id=data.get("correlation_id"),
            priority=EventPriority(data.get("priority", EventPriority.NORMAL.value)),
            source_system=data.get("source_system"),
        )


class EventHandler(Protocol):
    """Protocol for event handlers."""
    
    def __call__(self, event: UnifiedEvent) -> None:
        """Handle an event."""
        ...


class EventEmitter(ABC):
    """Abstract base class for event emitters."""
    
    @abstractmethod
    async def emit(self, event: UnifiedEvent) -> bool:
        """Emit an event. Returns True if successful."""
        pass
    
    @abstractmethod
    def add_handler(self, event_type: str, handler: EventHandler) -> str:
        """Add an event handler. Returns handler ID."""
        pass
    
    @abstractmethod
    def remove_handler(self, handler_id: str) -> bool:
        """Remove an event handler. Returns True if successful."""
        pass


class EventRouter:
    """Central event router that coordinates between different event systems."""
    
    def __init__(self):
        self._emitters: Dict[EventCategory, List[EventEmitter]] = {}
        self._global_handlers: List[EventHandler] = []
        self._category_handlers: Dict[EventCategory, List[EventHandler]] = {}
        self._type_handlers: Dict[str, List[EventHandler]] = {}
        
    def register_emitter(self, category: EventCategory, emitter: EventEmitter) -> None:
        """Register an event emitter for a category."""
        if category not in self._emitters:
            self._emitters[category] = []
        self._emitters[category].append(emitter)
        
    def unregister_emitter(self, category: EventCategory, emitter: EventEmitter) -> bool:
        """Unregister an event emitter."""
        if category in self._emitters and emitter in self._emitters[category]:
            self._emitters[category].remove(emitter)
            return True
        return False
    
    def add_global_handler(self, handler: EventHandler) -> str:
        """Add a handler for all events."""
        handler_id = str(uuid.uuid4())
        self._global_handlers.append(handler)
        return handler_id
    
    def add_category_handler(self, category: EventCategory, handler: EventHandler) -> str:
        """Add a handler for a specific category."""
        handler_id = str(uuid.uuid4())
        if category not in self._category_handlers:
            self._category_handlers[category] = []
        self._category_handlers[category].append(handler)
        return handler_id
    
    def add_type_handler(self, event_type: str, handler: EventHandler) -> str:
        """Add a handler for a specific event type."""
        handler_id = str(uuid.uuid4())
        if event_type not in self._type_handlers:
            self._type_handlers[event_type] = []
        self._type_handlers[event_type].append(handler)
        return handler_id
    
    async def route_event(self, event: UnifiedEvent) -> bool:
        """Route an event to appropriate handlers and emitters."""
        success = True
        
        # Call global handlers
        for handler in self._global_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error("Error in global handler", error=str(e), event_id=event.id, event_type=event.event_type)
                success = False
        
        # Call category-specific handlers
        if event.category in self._category_handlers:
            for handler in self._category_handlers[event.category]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error("Error in category handler", error=str(e), event_id=event.id, event_type=event.event_type, category=event.category)
                    success = False
        
        # Call type-specific handlers
        if event.event_type in self._type_handlers:
            for handler in self._type_handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error("Error in type handler", error=str(e), event_id=event.id, event_type=event.event_type)
                    success = False
        
        # Route to category emitters
        if event.category in self._emitters:
            for emitter in self._emitters[event.category]:
                try:
                    emitter_success = await emitter.emit(event)
                    if not emitter_success:
                        success = False
                except Exception as e:
                    logger.error("Error in emitter", error=str(e), event_id=event.id, event_type=event.event_type, category=event.category)
                    success = False
        
        return success


# Global event router instance
event_router = EventRouter()


# Convenience functions for creating events
def create_realtime_event(
    event_type: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    priority: EventPriority = EventPriority.NORMAL,
    **kwargs
) -> UnifiedEvent:
    """Create a real-time SSE event."""
    return UnifiedEvent(
        category=EventCategory.REALTIME,
        event_type=event_type,
        data=data,
        user_id=user_id,
        priority=priority,
        source_system="sse",
        **kwargs
    )


def create_security_event(
    event_type: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    priority: EventPriority = EventPriority.HIGH,
    **kwargs
) -> UnifiedEvent:
    """Create a security monitoring event."""
    return UnifiedEvent(
        category=EventCategory.SECURITY,
        event_type=event_type,
        data=data,
        user_id=user_id,
        priority=priority,
        source_system="monitoring",
        **kwargs
    )


def create_audit_event(
    event_type: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    priority: EventPriority = EventPriority.NORMAL,
    **kwargs
) -> UnifiedEvent:
    """Create an audit logging event."""
    return UnifiedEvent(
        category=EventCategory.AUDIT,
        event_type=event_type,
        data=data,
        user_id=user_id,
        priority=priority,
        source_system="audit",
        **kwargs
    )


def create_streaming_event(
    event_type: str,
    data: Dict[str, Any],
    session_id: Optional[str] = None,
    priority: EventPriority = EventPriority.NORMAL,
    **kwargs
) -> UnifiedEvent:
    """Create a streaming/chat event."""
    return UnifiedEvent(
        category=EventCategory.STREAMING,
        event_type=event_type,
        data=data,
        session_id=session_id,
        priority=priority,
        source_system="streaming",
        **kwargs
    )


def create_analytics_event(
    event_type: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    priority: EventPriority = EventPriority.LOW,
    **kwargs
) -> UnifiedEvent:
    """Create an analytics/A/B testing event."""
    return UnifiedEvent(
        category=EventCategory.ANALYTICS,
        event_type=event_type,
        data=data,
        user_id=user_id,
        priority=priority,
        source_system="analytics",
        **kwargs
    )


async def emit_event(event: UnifiedEvent) -> bool:
    """Emit an event through the global router with enhanced validation."""
    try:
        # Validate event structure
        if not validate_event_structure(event):
            logger.error("Invalid event structure", event_id=event.id, event_type=event.event_type)
            return False
            
        # Route the event
        return await event_router.route_event(event)
        
    except Exception as e:
        logger.error("Failed to emit event", event_id=event.id, event_type=event.event_type, error=str(e))
        return False


def validate_event_structure(event: UnifiedEvent) -> bool:
    """Validate event structure for consistency and security."""
    try:
        # Basic field validation
        if not event.id or not event.event_type or not event.category:
            logger.warning("Event missing required fields", event_id=getattr(event, 'id', None))
            return False
            
        # Validate event type format (should not contain special characters)
        if not event.event_type.replace('.', '').replace('_', '').replace('-', '').isalnum():
            logger.warning("Event type contains invalid characters", event_type=event.event_type)
            return False
            
        # Validate data size (prevent memory issues)
        try:
            import json
            data_size = len(json.dumps(event.data))
            if data_size > 1024 * 1024:  # 1MB limit
                logger.warning("Event data too large", event_id=event.id, size_bytes=data_size)
                return False
        except (TypeError, ValueError) as e:
            logger.warning("Event data not serializable", event_id=event.id, error=str(e))
            return False
            
        # Validate metadata size
        try:
            metadata_size = len(json.dumps(event.metadata))
            if metadata_size > 64 * 1024:  # 64KB limit
                logger.warning("Event metadata too large", event_id=event.id, size_bytes=metadata_size)
                return False
        except (TypeError, ValueError) as e:
            logger.warning("Event metadata not serializable", event_id=event.id, error=str(e))
            return False
            
        return True
        
    except Exception as e:
        logger.error("Error validating event", event_id=getattr(event, 'id', None), error=str(e))
        return False