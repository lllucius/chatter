"""DEPRECATED: This file has been consolidated into chatter.core.events.

All functionality from this module has been moved to the main events module
to eliminate code duplication and over-engineering. 

Please update imports:
- OLD: from chatter.core.unified_events import initialize_event_system
- NEW: from chatter.core.events import initialize_event_system

This file will be removed in a future version.
"""

# Re-export the main functions for backward compatibility
from chatter.core.events import (
    emit_audit_event,
    emit_realtime_event, 
    emit_security_event,
    emit_system_alert,
    get_event_stats,
    initialize_event_system,
    shutdown_event_system,
)

import warnings
warnings.warn(
    "chatter.core.unified_events is deprecated. Use chatter.core.events instead.",
    DeprecationWarning,
    stacklevel=2
)