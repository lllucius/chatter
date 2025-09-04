#!/usr/bin/env python3
"""
Example script demonstrating the unified event system in action.

This script shows how different types of events can be emitted and handled
through the consolidated event system.
"""

import asyncio
import sys
import os

# Add the project to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatter.core.unified_events import (
    initialize_event_system,
    shutdown_event_system,
    emit_realtime_event,
    emit_security_event,
    emit_audit_event,
    emit_system_alert,
    get_event_stats,
    unified_event_manager
)
from chatter.core.events import EventCategory, EventPriority, event_router


async def event_demo():
    """Demonstrate the unified event system."""
    
    print("🚀 Starting Unified Event System Demo")
    print("=" * 50)
    
    # Initialize the event system
    print("\n📋 Initializing unified event system...")
    await initialize_event_system()
    
    # Set up some event listeners to show events are being processed
    events_received = []
    
    def track_events(event):
        events_received.append(event)
        print(f"📨 Event received: {event.event_type} (category: {event.category.value}, priority: {event.priority.value})")
    
    # Add a global event handler
    event_router.add_global_handler(track_events)
    
    print("✅ Event system initialized and listeners set up")
    
    # Demo different types of events
    print("\n🎯 Emitting different types of events...")
    
    # 1. Real-time events (like document processing)
    print("\n📄 Emitting document processing events...")
    await emit_realtime_event(
        "document.uploaded",
        {
            "document_id": "doc_123",
            "filename": "example.pdf",
            "size": 1024000,
            "user": "demo_user"
        },
        user_id="user_123"
    )
    
    await emit_realtime_event(
        "document.processing_completed",
        {
            "document_id": "doc_123",
            "status": "success",
            "chunks_created": 25,
            "processing_time": 5.2
        },
        user_id="user_123"
    )
    
    # 2. Security events (like login attempts)
    print("\n🔒 Emitting security events...")
    await emit_security_event(
        "auth.login_failure",
        {
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 Demo Browser",
            "reason": "invalid_password",
            "attempts": 3
        },
        user_id="user_456"
    )
    
    await emit_security_event(
        "suspicious.brute_force",
        {
            "ip_address": "192.168.1.100",
            "failed_attempts": 5,
            "time_window": "5 minutes",
            "blocked": True
        }
    )
    
    # 3. Audit events (like resource operations)
    print("\n📊 Emitting audit events...")
    await emit_audit_event(
        "model.delete",
        {
            "model_id": "model_789",
            "model_name": "GPT-4 Custom",
            "result": "success",
            "admin_user": "admin_123"
        },
        user_id="admin_123"
    )
    
    await emit_audit_event(
        "provider.create",
        {
            "provider_id": "provider_101",
            "provider_name": "Custom OpenAI",
            "result": "success",
            "created_by": "admin_123"
        },
        user_id="admin_123"
    )
    
    # 4. System alerts (high priority)
    print("\n🚨 Emitting system alerts...")
    await emit_system_alert(
        "Database connection pool exhausted",
        severity="critical",
        data={
            "active_connections": 100,
            "max_connections": 100,
            "queued_requests": 25
        }
    )
    
    await emit_system_alert(
        "Backup completed successfully",
        severity="info",
        data={
            "backup_id": "backup_456",
            "size": "2.5GB",
            "duration": "12 minutes"
        }
    )
    
    # Give events time to propagate through the system
    await asyncio.sleep(1)
    
    # Show statistics
    print("\n📈 Event System Statistics:")
    print("-" * 30)
    stats = get_event_stats()
    print(f"Events emitted: {stats['emitted']}")
    print(f"Events processed: {stats['processed']}")
    print(f"Events by category: {stats['by_category']}")
    print(f"Events by priority: {stats['by_priority']}")
    print(f"Top event types:")
    for event_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {event_type}: {count}")
    
    print(f"\n🎯 Total events received by listener: {len(events_received)}")
    
    # Show some cross-system routing examples
    print("\n🔄 Cross-system Event Routing:")
    print("-" * 30)
    security_to_audit = [e for e in events_received if e.event_type.startswith("security.") and e.category == EventCategory.AUDIT]
    high_priority_realtime = [e for e in events_received if e.priority in [EventPriority.HIGH, EventPriority.CRITICAL] and e.category == EventCategory.REALTIME]
    
    print(f"Security events routed to audit: {len(security_to_audit)}")
    print(f"High priority events routed to real-time: {len(high_priority_realtime)}")
    
    # Shutdown
    print("\n🛑 Shutting down event system...")
    await shutdown_event_system()
    print("✅ Demo completed successfully!")


if __name__ == "__main__":
    # Run the demo
    try:
        asyncio.run(event_demo())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()