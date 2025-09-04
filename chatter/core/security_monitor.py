"""Security monitoring compatibility module.

This module provides backward compatibility for imports from chatter.core.security_monitor.
The actual implementation is in chatter.core.monitoring, but this module re-exports
the security-related classes and functions for backward compatibility.
"""

# Import the actual implementations from monitoring
from chatter.core.monitoring import (
    SecurityEvent,
    SecurityEventType,
    SecurityEventSeverity,
    MonitoringService,
)

# Re-export for backward compatibility
__all__ = [
    'SecurityEvent',
    'SecurityEventType', 
    'SecurityEventSeverity',
    'MonitoringService',
]

# Add convenient functions that may be expected in a security_monitor module
def get_security_monitor():
    """Get the global monitoring service instance for security monitoring."""
    from chatter.core.monitoring import get_monitoring_service
    return get_monitoring_service()