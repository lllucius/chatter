"""Unified event management service that consolidates all event handling."""

import asyncio
from typing import Any, Dict, List, Optional

from chatter.core.events import (
    EventCategory,
    EventPriority,
    UnifiedEvent,
    event_router,
    create_realtime_event,
    create_security_event,
    create_audit_event,
    create_streaming_event,
    create_analytics_event,
    emit_event
)
from chatter.core.sse_adapter import setup_sse_integration, sse_forwarder
from chatter.core.security_adapter import setup_security_integration, security_forwarder
from chatter.core.audit_adapter import setup_audit_integration, audit_forwarder
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class UnifiedEventManager:
    """Central manager for all event handling in the Chatter platform."""
    
    def __init__(self):
        self._initialized = False
        self._event_stats = {
            "emitted": 0,
            "processed": 0,
            "errors": 0,
            "by_category": {},
            "by_type": {},
            "by_priority": {}
        }
        
    async def initialize(self, audit_logger=None, monitoring_service=None):
        """Initialize the unified event management system."""
        
        if self._initialized:
            logger.warning("Unified event manager already initialized")
            return
        
        try:
            # Set up integration adapters
            setup_sse_integration()
            setup_security_integration()
            setup_audit_integration(audit_logger)
            
            # Set up global event monitoring
            self._setup_event_monitoring()
            
            # Set up cross-system event routing
            self._setup_cross_system_routing()
            
            self._initialized = True
            
            logger.info("Unified event management system initialized successfully")
            
            # Emit initialization event
            await self.emit_system_event(
                event_type="system.event_manager_initialized",
                data={
                    "manager": "UnifiedEventManager",
                    "integrations": ["sse", "security", "audit"],
                    "status": "ready"
                }
            )
            
        except Exception as e:
            logger.error("Failed to initialize unified event manager", error=str(e))
            raise
    
    async def shutdown(self):
        """Shutdown the unified event management system."""
        
        if not self._initialized:
            return
        
        try:
            # Emit shutdown event
            await self.emit_system_event(
                event_type="system.event_manager_shutdown",
                data={
                    "manager": "UnifiedEventManager",
                    "stats": self._event_stats
                }
            )
            
            # Clean up resources
            self._initialized = False
            
            logger.info("Unified event management system shutdown complete")
            
        except Exception as e:
            logger.error("Error during event manager shutdown", error=str(e))
    
    def _setup_event_monitoring(self):
        """Set up monitoring for all events."""
        
        def monitor_event(event: UnifiedEvent) -> None:
            """Monitor and track event statistics."""
            try:
                self._event_stats["processed"] += 1
                
                # Track by category
                category = event.category.value
                if category not in self._event_stats["by_category"]:
                    self._event_stats["by_category"][category] = 0
                self._event_stats["by_category"][category] += 1
                
                # Track by type
                event_type = event.event_type
                if event_type not in self._event_stats["by_type"]:
                    self._event_stats["by_type"][event_type] = 0
                self._event_stats["by_type"][event_type] += 1
                
                # Track by priority
                priority = event.priority.value
                if priority not in self._event_stats["by_priority"]:
                    self._event_stats["by_priority"][priority] = 0
                self._event_stats["by_priority"][priority] += 1
                
                # Log high priority events
                if event.priority in [EventPriority.HIGH, EventPriority.CRITICAL]:
                    logger.info(
                        "High priority event processed",
                        event_id=event.id,
                        event_type=event.event_type,
                        category=event.category.value,
                        priority=event.priority.value,
                        user_id=event.user_id
                    )
                
            except Exception as e:
                self._event_stats["errors"] += 1
                logger.error("Error monitoring event", error=str(e))
        
        # Add global event monitor
        event_router.add_global_handler(monitor_event)
        
        logger.debug("Event monitoring set up")
    
    def _setup_cross_system_routing(self):
        """Set up routing between different event systems."""
        
        def route_high_priority_events(event: UnifiedEvent) -> None:
            """Route high priority events to real-time system."""
            if event.priority in [EventPriority.HIGH, EventPriority.CRITICAL]:
                # Convert high priority events to real-time events for immediate delivery
                if event.category != EventCategory.REALTIME:
                    realtime_event = create_realtime_event(
                        event_type=f"{event.category.value}.{event.event_type}",
                        data=event.data,
                        user_id=event.user_id,
                        priority=event.priority,
                        correlation_id=event.correlation_id,
                        session_id=event.session_id,
                        metadata={
                            **event.metadata,
                            "original_category": event.category.value,
                            "routed_for_priority": True
                        }
                    )
                    # Emit asynchronously to avoid blocking
                    asyncio.create_task(emit_event(realtime_event))
        
        def route_security_to_audit(event: UnifiedEvent) -> None:
            """Route security events to audit system for compliance."""
            if event.category == EventCategory.SECURITY:
                audit_event = create_audit_event(
                    event_type=f"security.{event.event_type}",
                    data=event.data,
                    user_id=event.user_id,
                    priority=event.priority,
                    correlation_id=event.correlation_id,
                    session_id=event.session_id,
                    metadata={
                        **event.metadata,
                        "original_security_event_id": event.id,
                        "auto_routed_from_security": True
                    }
                )
                # Emit asynchronously to avoid blocking
                asyncio.create_task(emit_event(audit_event))
        
        # Add routing handlers
        event_router.add_global_handler(route_high_priority_events)
        event_router.add_category_handler(EventCategory.SECURITY, route_security_to_audit)
        
        logger.debug("Cross-system event routing set up")
    
    async def emit_realtime_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        **kwargs
    ) -> bool:
        """Emit a real-time event."""
        self._event_stats["emitted"] += 1
        
        event = create_realtime_event(
            event_type=event_type,
            data=data,
            user_id=user_id,
            priority=priority,
            **kwargs
        )
        
        return await emit_event(event)
    
    async def emit_security_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        priority: EventPriority = EventPriority.HIGH,
        **kwargs
    ) -> bool:
        """Emit a security event."""
        self._event_stats["emitted"] += 1
        
        event = create_security_event(
            event_type=event_type,
            data=data,
            user_id=user_id,
            priority=priority,
            **kwargs
        )
        
        return await emit_event(event)
    
    async def emit_audit_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        **kwargs
    ) -> bool:
        """Emit an audit event."""
        self._event_stats["emitted"] += 1
        
        event = create_audit_event(
            event_type=event_type,
            data=data,
            user_id=user_id,
            priority=priority,
            **kwargs
        )
        
        return await emit_event(event)
    
    async def emit_streaming_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        session_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        **kwargs
    ) -> bool:
        """Emit a streaming event."""
        self._event_stats["emitted"] += 1
        
        event = create_streaming_event(
            event_type=event_type,
            data=data,
            session_id=session_id,
            priority=priority,
            **kwargs
        )
        
        return await emit_event(event)
    
    async def emit_analytics_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        priority: EventPriority = EventPriority.LOW,
        **kwargs
    ) -> bool:
        """Emit an analytics event."""
        self._event_stats["emitted"] += 1
        
        event = create_analytics_event(
            event_type=event_type,
            data=data,
            user_id=user_id,
            priority=priority,
            **kwargs
        )
        
        return await emit_event(event)
    
    async def emit_system_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        **kwargs
    ) -> bool:
        """Emit a system event."""
        return await self.emit_realtime_event(
            event_type=event_type,
            data=data,
            priority=priority,
            **kwargs
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event processing statistics."""
        return self._event_stats.copy()
    
    def is_initialized(self) -> bool:
        """Check if the event manager is initialized."""
        return self._initialized


# Global unified event manager instance
unified_event_manager = UnifiedEventManager()


# Convenience functions that use the global manager
async def emit_realtime_event(
    event_type: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    **kwargs
) -> bool:
    """Emit a real-time event through the unified manager."""
    return await unified_event_manager.emit_realtime_event(
        event_type=event_type,
        data=data,
        user_id=user_id,
        **kwargs
    )


async def emit_security_event(
    event_type: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    **kwargs
) -> bool:
    """Emit a security event through the unified manager."""
    return await unified_event_manager.emit_security_event(
        event_type=event_type,
        data=data,
        user_id=user_id,
        **kwargs
    )


async def emit_audit_event(
    event_type: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    **kwargs
) -> bool:
    """Emit an audit event through the unified manager."""
    return await unified_event_manager.emit_audit_event(
        event_type=event_type,
        data=data,
        user_id=user_id,
        **kwargs
    )


async def emit_system_alert(
    message: str,
    severity: str = "info",
    user_id: Optional[str] = None,
    **kwargs
) -> bool:
    """Emit a system alert."""
    return await unified_event_manager.emit_system_event(
        event_type="system.alert",
        data={
            "message": message,
            "severity": severity,
            **kwargs.get("data", {})
        },
        user_id=user_id,
        priority=EventPriority.HIGH if severity in ["error", "critical"] else EventPriority.NORMAL,
        **{k: v for k, v in kwargs.items() if k != "data"}
    )


async def initialize_event_system(audit_logger=None, monitoring_service=None):
    """Initialize the unified event system."""
    await unified_event_manager.initialize(audit_logger, monitoring_service)


async def shutdown_event_system():
    """Shutdown the unified event system."""
    await unified_event_manager.shutdown()


def get_event_stats() -> Dict[str, Any]:
    """Get event processing statistics."""
    return unified_event_manager.get_stats()