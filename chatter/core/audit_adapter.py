"""Adapter to integrate audit logging with unified event system."""

import json
from typing import Any, Dict, Optional

from chatter.core.events import (
    EventCategory,
    EventEmitter,
    EventHandler,
    EventPriority,
    UnifiedEvent,
    create_audit_event,
    emit_event,
    event_router
)
from chatter.utils.audit_logging import (
    AuditEventType,
    AuditResult,
    AuditLogger
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class AuditEventEmitter(EventEmitter):
    """Adapter that integrates audit logging with unified events."""
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.audit_logger = audit_logger
        self._handlers: Dict[str, EventHandler] = {}
    
    async def emit(self, event: UnifiedEvent) -> bool:
        """Process unified event through audit logging."""
        try:
            # Convert and log unified audit events
            if event.category == EventCategory.AUDIT:
                await self._log_audit_event(event)
                
                logger.debug(
                    "Processed audit event",
                    event_id=event.id,
                    event_type=event.event_type
                )
                
            return True
            
        except Exception as e:
            logger.error(
                "Failed to process audit event",
                event_id=event.id,
                event_type=event.event_type,
                error=str(e)
            )
            return False
    
    def add_handler(self, event_type: str, handler: EventHandler) -> str:
        """Add an event handler."""
        handler_id = f"audit_handler_{len(self._handlers)}"
        self._handlers[handler_id] = handler
        return handler_id
    
    def remove_handler(self, handler_id: str) -> bool:
        """Remove an event handler."""
        if handler_id in self._handlers:
            del self._handlers[handler_id]
            return True
        return False
    
    async def _log_audit_event(self, event: UnifiedEvent) -> None:
        """Log unified event through audit logger."""
        
        if not self.audit_logger:
            # If no audit logger provided, just log to regular logger
            logger.info(
                "Audit event",
                event_id=event.id,
                event_type=event.event_type,
                user_id=event.user_id,
                data=event.data,
                metadata=event.metadata
            )
            return
        
        # Map unified event type to audit event type
        audit_type = self._map_to_audit_type(event.event_type)
        if not audit_type:
            logger.warning(
                "Unknown audit event type",
                event_type=event.event_type,
                event_id=event.id
            )
            return
        
        # Determine result from event data or priority
        result = self._determine_result(event)
        
        # Extract audit-specific fields
        request = event.metadata.get("request")
        session_id = event.session_id
        resource_type = event.data.get("resource_type")
        resource_id = event.data.get("resource_id")
        error_message = event.data.get("error") or event.data.get("error_message")
        
        # Prepare details for audit log
        details = {
            "unified_event_id": event.id,
            "category": event.category.value,
            "priority": event.priority.value,
            "source_system": event.source_system,
            "correlation_id": event.correlation_id,
            **event.data,
            **event.metadata
        }
        
        # Remove request object from details to avoid serialization issues
        if "request" in details:
            del details["request"]
        
        # Log the audit event
        await self.audit_logger.log_event(
            event_type=audit_type,
            result=result,
            user_id=event.user_id,
            request=request,
            session_id=session_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            error_message=error_message
        )
    
    def _map_to_audit_type(self, event_type: str) -> Optional[AuditEventType]:
        """Map unified event type to audit event type."""
        
        audit_type_mapping = {
            # Authentication events
            "auth.login": AuditEventType.LOGIN,
            "auth.logout": AuditEventType.LOGOUT,
            "auth.login_failed": AuditEventType.LOGIN_FAILED,
            "auth.token_refresh": AuditEventType.TOKEN_REFRESH,
            
            # Provider operations
            "provider.create": AuditEventType.PROVIDER_CREATE,
            "provider.update": AuditEventType.PROVIDER_UPDATE,
            "provider.delete": AuditEventType.PROVIDER_DELETE,
            "provider.set_default": AuditEventType.PROVIDER_SET_DEFAULT,
            
            # Model operations
            "model.create": AuditEventType.MODEL_CREATE,
            "model.update": AuditEventType.MODEL_UPDATE,
            "model.delete": AuditEventType.MODEL_DELETE,
            "model.set_default": AuditEventType.MODEL_SET_DEFAULT,
            
            # Embedding space operations
            "embedding_space.create": AuditEventType.EMBEDDING_SPACE_CREATE,
            "embedding_space.update": AuditEventType.EMBEDDING_SPACE_UPDATE,
            "embedding_space.delete": AuditEventType.EMBEDDING_SPACE_DELETE,
            "embedding_space.set_default": AuditEventType.EMBEDDING_SPACE_SET_DEFAULT,
            
            # Security events
            "security.rate_limit_exceeded": AuditEventType.RATE_LIMIT_EXCEEDED,
            "security.authorization_failed": AuditEventType.AUTHORIZATION_FAILED,
            "security.validation_failed": AuditEventType.VALIDATION_FAILED,
            "security.suspicious_activity": AuditEventType.SUSPICIOUS_ACTIVITY,
        }
        
        return audit_type_mapping.get(event_type)
    
    def _determine_result(self, event: UnifiedEvent) -> AuditResult:
        """Determine audit result from event data."""
        
        # Check explicit result in data
        if "result" in event.data:
            result_mapping = {
                "success": AuditResult.SUCCESS,
                "failure": AuditResult.FAILURE,
                "error": AuditResult.ERROR,
            }
            return result_mapping.get(event.data["result"], AuditResult.SUCCESS)
        
        # Check for error indicators
        if any(key in event.data for key in ["error", "error_message", "exception"]):
            return AuditResult.ERROR
        
        # Check event type for failure indicators
        if any(keyword in event.event_type for keyword in ["failed", "error", "unauthorized"]):
            return AuditResult.FAILURE
        
        # Default to success
        return AuditResult.SUCCESS


class AuditEventForwarder:
    """Forwards audit events between audit system and unified events."""
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.audit_emitter = AuditEventEmitter(audit_logger)
    
    def setup_forwarding(self):
        """Set up event forwarding for audit events."""
        
        # Register audit emitter
        event_router.register_emitter(EventCategory.AUDIT, self.audit_emitter)
        
        logger.info("Set up audit event forwarding to unified system")
    
    async def emit_audit_event(
        self,
        event_type: str,
        result: str = "success",
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Emit an audit event through the unified system."""
        
        # Map result to priority
        priority_mapping = {
            "success": EventPriority.NORMAL,
            "failure": EventPriority.HIGH,
            "error": EventPriority.HIGH,
        }
        priority = priority_mapping.get(result.lower(), EventPriority.NORMAL)
        
        # Prepare data
        data = details or {}
        data["result"] = result
        if resource_type:
            data["resource_type"] = resource_type
        if resource_id:
            data["resource_id"] = resource_id
        if error_message:
            data["error_message"] = error_message
        
        # Create unified audit event
        event = create_audit_event(
            event_type=event_type,
            data=data,
            user_id=user_id,
            priority=priority,
            **kwargs
        )
        
        # Emit through unified system
        return await emit_event(event)


# Global forwarder instance
audit_forwarder = AuditEventForwarder()


def setup_audit_integration(audit_logger: Optional[AuditLogger] = None):
    """Set up integration between audit logging and unified event system."""
    global audit_forwarder
    
    if audit_logger:
        audit_forwarder = AuditEventForwarder(audit_logger)
    
    audit_forwarder.setup_forwarding()
    logger.info("Audit logging integration with unified event system is ready")


# Convenience functions for emitting audit events
async def emit_authentication_audit(
    action: str,
    success: bool,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    """Emit an authentication audit event."""
    result = "success" if success else "failure"
    
    event_details = details or {}
    if ip_address:
        event_details["ip_address"] = ip_address
    if user_agent:
        event_details["user_agent"] = user_agent
    
    return await audit_forwarder.emit_audit_event(
        event_type=f"auth.{action}",
        result=result,
        user_id=user_id,
        session_id=session_id,
        details=event_details,
        **kwargs
    )


async def emit_resource_audit(
    action: str,
    resource_type: str,
    resource_id: str,
    success: bool,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
    **kwargs
) -> bool:
    """Emit a resource operation audit event."""
    result = "success" if success else "failure"
    
    return await audit_forwarder.emit_audit_event(
        event_type=f"{resource_type}.{action}",
        result=result,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        error_message=error_message,
        **kwargs
    )


async def emit_security_audit(
    event_type: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    """Emit a security-related audit event."""
    event_details = details or {}
    if ip_address:
        event_details["ip_address"] = ip_address
    
    return await audit_forwarder.emit_audit_event(
        event_type=f"security.{event_type}",
        result="failure",  # Security events are typically failures/violations
        user_id=user_id,
        details=event_details,
        **kwargs
    )