"""Adapter to integrate security monitoring with unified event system."""

from typing import Any, Dict, Optional

from chatter.core.events import (
    EventCategory,
    EventEmitter,
    EventHandler,
    EventPriority,
    UnifiedEvent,
    create_security_event,
    emit_event,
    event_router
)
from chatter.core.monitoring import (
    SecurityEvent,
    SecurityEventType,
    SecurityEventSeverity,
    MonitoringService
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class SecurityEventEmitter(EventEmitter):
    """Adapter that integrates security monitoring with unified events."""
    
    def __init__(self, monitoring_service: Optional[MonitoringService] = None):
        self.monitoring_service = monitoring_service
        self._handlers: Dict[str, EventHandler] = {}
    
    async def emit(self, event: UnifiedEvent) -> bool:
        """Process unified event through security monitoring."""
        try:
            # Convert unified event to security event if applicable
            if event.category == EventCategory.SECURITY:
                security_event = self._convert_to_security_event(event)
                
                # Process through monitoring service if available
                if self.monitoring_service and security_event:
                    await self.monitoring_service.record_security_event(security_event)
                    
                logger.debug(
                    "Processed security event",
                    event_id=event.id,
                    event_type=event.event_type,
                    severity=security_event.severity.value if security_event else "unknown"
                )
                
            return True
            
        except Exception as e:
            logger.error(
                "Failed to process security event",
                event_id=event.id,
                event_type=event.event_type,
                error=str(e)
            )
            return False
    
    def add_handler(self, event_type: str, handler: EventHandler) -> str:
        """Add an event handler."""
        handler_id = f"security_handler_{len(self._handlers)}"
        self._handlers[handler_id] = handler
        return handler_id
    
    def remove_handler(self, handler_id: str) -> bool:
        """Remove an event handler."""
        if handler_id in self._handlers:
            del self._handlers[handler_id]
            return True
        return False
    
    def _convert_to_security_event(self, event: UnifiedEvent) -> Optional[SecurityEvent]:
        """Convert unified event to SecurityEvent format."""
        
        # Map unified event types to security event types
        security_type_mapping = {
            # Authentication events
            "auth.login_success": SecurityEventType.LOGIN_SUCCESS,
            "auth.login_failure": SecurityEventType.LOGIN_FAILURE,
            "auth.login_blocked": SecurityEventType.LOGIN_BLOCKED,
            
            # Account events
            "account.locked": SecurityEventType.ACCOUNT_LOCKED,
            "account.created": SecurityEventType.ACCOUNT_CREATED,
            "account.deactivated": SecurityEventType.ACCOUNT_DEACTIVATED,
            
            # Password events
            "password.changed": SecurityEventType.PASSWORD_CHANGED,
            "password.reset_requested": SecurityEventType.PASSWORD_RESET_REQUESTED,
            "password.reset_completed": SecurityEventType.PASSWORD_RESET_COMPLETED,
            
            # Token events
            "token.created": SecurityEventType.TOKEN_CREATED,
            "token.refreshed": SecurityEventType.TOKEN_REFRESHED,
            "token.revoked": SecurityEventType.TOKEN_REVOKED,
            "token.blacklisted": SecurityEventType.TOKEN_BLACKLISTED,
            
            # API key events
            "api_key.created": SecurityEventType.API_KEY_CREATED,
            "api_key.used": SecurityEventType.API_KEY_USED,
            "api_key.revoked": SecurityEventType.API_KEY_REVOKED,
            
            # Suspicious activity
            "suspicious.brute_force": SecurityEventType.BRUTE_FORCE_ATTEMPT,
            "suspicious.anomalous_login": SecurityEventType.ANOMALOUS_LOGIN,
            "suspicious.multiple_failures": SecurityEventType.MULTIPLE_FAILURES,
            "suspicious.ip": SecurityEventType.SUSPICIOUS_IP,
            
            # Rate limiting
            "rate_limit.exceeded": SecurityEventType.RATE_LIMIT_EXCEEDED,
            
            # Security violations
            "security.disposable_email": SecurityEventType.DISPOSABLE_EMAIL_BLOCKED,
            "security.weak_password": SecurityEventType.WEAK_PASSWORD_REJECTED,
            "security.personal_info_password": SecurityEventType.PERSONAL_INFO_PASSWORD,
        }
        
        # Try to map the event type
        security_type = security_type_mapping.get(event.event_type)
        if not security_type:
            # For unmapped security events, log and return None
            logger.warning(
                "Unknown security event type",
                event_type=event.event_type,
                event_id=event.id
            )
            return None
        
        # Map priority to severity
        severity_mapping = {
            EventPriority.LOW: SecurityEventSeverity.LOW,
            EventPriority.NORMAL: SecurityEventSeverity.MEDIUM,
            EventPriority.HIGH: SecurityEventSeverity.HIGH,
            EventPriority.CRITICAL: SecurityEventSeverity.CRITICAL,
        }
        severity = severity_mapping.get(event.priority, SecurityEventSeverity.MEDIUM)
        
        # Extract relevant fields from event data
        details = event.data.copy()
        details.update(event.metadata)
        
        return SecurityEvent(
            event_type=security_type,
            severity=severity,
            user_id=event.user_id,
            ip_address=event.data.get("ip_address"),
            user_agent=event.data.get("user_agent"),
            details=details,
            timestamp=event.timestamp,
            event_id=event.id
        )


class SecurityEventForwarder:
    """Forwards security events from monitoring system to unified events."""
    
    def __init__(self):
        self.security_emitter = SecurityEventEmitter()
    
    def setup_forwarding(self):
        """Set up event forwarding from security monitoring to unified system."""
        
        # Register security emitter
        event_router.register_emitter(EventCategory.SECURITY, self.security_emitter)
        
        logger.info("Set up security event forwarding to unified system")
    
    async def emit_security_event(
        self,
        event_type: str,
        severity: str = "medium",
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        """Emit a security event through the unified system."""
        
        # Map severity to priority
        priority_mapping = {
            "low": EventPriority.LOW,
            "medium": EventPriority.NORMAL,
            "high": EventPriority.HIGH,
            "critical": EventPriority.CRITICAL,
        }
        priority = priority_mapping.get(severity.lower(), EventPriority.NORMAL)
        
        # Prepare data
        data = details or {}
        if ip_address:
            data["ip_address"] = ip_address
        if user_agent:
            data["user_agent"] = user_agent
        
        # Create unified security event
        event = create_security_event(
            event_type=event_type,
            data=data,
            user_id=user_id,
            priority=priority,
            **kwargs
        )
        
        # Emit through unified system
        return await emit_event(event)


# Global forwarder instance
security_forwarder = SecurityEventForwarder()


def setup_security_integration():
    """Set up integration between security monitoring and unified event system."""
    security_forwarder.setup_forwarding()
    logger.info("Security monitoring integration with unified event system is ready")


# Convenience functions for emitting security events
async def emit_login_event(
    success: bool,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    """Emit a login event."""
    event_type = "auth.login_success" if success else "auth.login_failure"
    severity = "medium" if success else "high"
    
    return await security_forwarder.emit_security_event(
        event_type=event_type,
        severity=severity,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details or {},
        **kwargs
    )


async def emit_suspicious_activity(
    activity_type: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    """Emit a suspicious activity event."""
    return await security_forwarder.emit_security_event(
        event_type=f"suspicious.{activity_type}",
        severity="high",
        user_id=user_id,
        ip_address=ip_address,
        details=details or {},
        **kwargs
    )


async def emit_rate_limit_exceeded(
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    endpoint: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    """Emit a rate limit exceeded event."""
    event_details = details or {}
    if endpoint:
        event_details["endpoint"] = endpoint
    
    return await security_forwarder.emit_security_event(
        event_type="rate_limit.exceeded",
        severity="medium",
        user_id=user_id,
        ip_address=ip_address,
        details=event_details,
        **kwargs
    )


async def emit_account_event(
    action: str,
    user_id: str,
    admin_user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    """Emit an account-related security event."""
    event_details = details or {}
    if admin_user_id:
        event_details["admin_user_id"] = admin_user_id
    
    severity = "high" if action in ["locked", "deactivated"] else "medium"
    
    return await security_forwarder.emit_security_event(
        event_type=f"account.{action}",
        severity=severity,
        user_id=user_id,
        details=event_details,
        **kwargs
    )