"""Unified workflow event system.

This module provides a unified event-driven system for workflow monitoring,
replacing the previous fragmented approach with 3 overlapping systems:
- MonitoringService (in-memory metrics)
- PerformanceMonitor (debug logs)
- WorkflowExecution (database persistence)

Architecture:
- Single WorkflowEvent type for all workflow events
- WorkflowEventBus for event distribution
- Subscribers for database, metrics, and logging
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Awaitable, Callable

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowEventType(str, Enum):
    """Types of workflow events.
    
    These events cover the entire workflow lifecycle and replace
    multiple monitoring points in the old system.
    """

    # Lifecycle events
    STARTED = "workflow_started"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    
    # Resource loading events
    LLM_LOADED = "llm_loaded"
    TOOLS_LOADED = "tools_loaded"
    RETRIEVER_LOADED = "retriever_loaded"
    
    # Execution events
    NODE_EXECUTED = "node_executed"
    TOOL_CALLED = "tool_called"
    TOKEN_USAGE = "token_usage"
    MESSAGE_SAVED = "message_saved"


@dataclass
class WorkflowEvent:
    """Unified workflow event.
    
    This event type replaces all monitoring calls across the workflow
    execution system, providing a single, consistent event structure.
    """

    event_type: WorkflowEventType
    execution_id: str
    user_id: str
    conversation_id: str | None
    timestamp: datetime
    data: dict[str, Any]

    @classmethod
    def create(
        cls,
        event_type: WorkflowEventType,
        execution_id: str,
        user_id: str,
        conversation_id: str | None = None,
        **data,
    ) -> "WorkflowEvent":
        """Create a workflow event with automatic timestamp."""
        return cls(
            event_type=event_type,
            execution_id=execution_id,
            user_id=user_id,
            conversation_id=conversation_id,
            timestamp=datetime.now(UTC),
            data=data,
        )


# Type alias for event handlers
EventHandler = Callable[[WorkflowEvent], Awaitable[None]]


class WorkflowEventBus:
    """Event bus for workflow events.
    
    This bus distributes events to all registered subscribers,
    replacing direct calls to multiple monitoring systems.
    """

    def __init__(self):
        """Initialize the event bus."""
        self._handlers: dict[WorkflowEventType, list[EventHandler]] = {}
        self._global_handlers: list[EventHandler] = []

    def subscribe(
        self,
        event_type: WorkflowEventType | None,
        handler: EventHandler,
    ):
        """Subscribe to workflow events.
        
        Args:
            event_type: Event type to subscribe to, or None for all events
            handler: Async function to handle events
        """
        if event_type is None:
            # Global handler for all events
            self._global_handlers.append(handler)
        else:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)

    def unsubscribe(
        self,
        event_type: WorkflowEventType | None,
        handler: EventHandler,
    ):
        """Unsubscribe from workflow events.
        
        Args:
            event_type: Event type to unsubscribe from, or None for global
            handler: Handler to remove
        """
        if event_type is None:
            if handler in self._global_handlers:
                self._global_handlers.remove(handler)
        else:
            if event_type in self._handlers and handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)

    async def publish(self, event: WorkflowEvent):
        """Publish workflow event to all subscribers.
        
        This replaces all monitoring calls with a single publish call.
        Events are delivered to both type-specific and global handlers.
        
        Args:
            event: Event to publish
        """
        # Call type-specific handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(
                        f"Error in event handler for {event.event_type}: {e}",
                        exc_info=True,
                    )

        # Call global handlers
        for handler in self._global_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(
                    f"Error in global event handler: {e}",
                    exc_info=True,
                )


# Global event bus instance
_event_bus: WorkflowEventBus | None = None


def get_event_bus() -> WorkflowEventBus:
    """Get the global workflow event bus.
    
    Returns:
        Singleton event bus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = WorkflowEventBus()
    return _event_bus
