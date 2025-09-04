#!/usr/bin/env python3
"""
Simple demonstration of the unified event system core functionality.

This script shows the core event handling without requiring full Chatter configuration.
"""

import asyncio
import sys
import os
from datetime import datetime, UTC

# Add the project to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatter.core.events import (
    EventCategory,
    EventPriority,
    UnifiedEvent,
    EventRouter,
    create_realtime_event,
    create_security_event,
    create_audit_event,
    emit_event
)


async def simple_event_demo():
    """Demonstrate core unified event functionality."""
    
    print("🚀 Simple Unified Event System Demo")
    print("=" * 40)
    
    # Create event router
    router = EventRouter()
    
    # Track events received
    events_received = []
    
    def track_all_events(event):
        events_received.append(event)
        print(f"📨 [ALL] {event.event_type} (category: {event.category.value}, priority: {event.priority.value})")
    
    def track_security_events(event):
        print(f"🔒 [SECURITY] {event.event_type} - {event.data}")
    
    def track_high_priority_events(event):
        print(f"🚨 [HIGH PRIORITY] {event.event_type} - Priority: {event.priority.value}")
    
    # Add handlers
    router.add_global_handler(track_all_events)
    router.add_category_handler(EventCategory.SECURITY, track_security_events)
    
    # Add handler for high priority events
    def high_priority_filter(event):
        if event.priority in [EventPriority.HIGH, EventPriority.CRITICAL]:
            track_high_priority_events(event)
    
    router.add_global_handler(high_priority_filter)
    
    print("✅ Event router configured with handlers")
    
    # Create and route different types of events
    print("\n🎯 Creating and routing events...")
    
    # 1. Real-time document event
    print("\n📄 Real-time document event:")
    doc_event = create_realtime_event(
        event_type="document.uploaded",
        data={
            "document_id": "doc_123",
            "filename": "example.pdf",
            "user": "demo_user"
        },
        user_id="user_123"
    )
    
    await router.route_event(doc_event)
    
    # 2. High priority security event
    print("\n🔒 High priority security event:")
    security_event = create_security_event(
        event_type="auth.login_failure",
        data={
            "ip_address": "192.168.1.100",
            "attempts": 5,
            "reason": "brute_force_detected"
        },
        user_id="user_456",
        priority=EventPriority.HIGH
    )
    
    await router.route_event(security_event)
    
    # 3. Critical system alert
    print("\n🚨 Critical system event:")
    critical_event = create_realtime_event(
        event_type="system.alert",
        data={
            "message": "Database connection failed",
            "severity": "critical",
            "affected_services": ["chat", "documents"]
        },
        priority=EventPriority.CRITICAL
    )
    
    await router.route_event(critical_event)
    
    # 4. Normal audit event
    print("\n📊 Audit event:")
    audit_event = create_audit_event(
        event_type="model.delete",
        data={
            "model_id": "model_789",
            "model_name": "GPT-4 Custom",
            "result": "success"
        },
        user_id="admin_123"
    )
    
    await router.route_event(audit_event)
    
    # Show results
    print(f"\n📈 Results:")
    print(f"Total events processed: {len(events_received)}")
    print(f"Event types: {[e.event_type for e in events_received]}")
    print(f"Categories: {[e.category.value for e in events_received]}")
    print(f"Priorities: {[e.priority.value for e in events_received]}")
    
    # Demonstrate event structure
    print(f"\n🔍 Example event structure:")
    sample_event = events_received[0] if events_received else doc_event
    print(f"Event ID: {sample_event.id}")
    print(f"Timestamp: {sample_event.timestamp}")
    print(f"Category: {sample_event.category.value}")
    print(f"Type: {sample_event.event_type}")
    print(f"Priority: {sample_event.priority.value}")
    print(f"User ID: {sample_event.user_id}")
    print(f"Data: {sample_event.data}")
    print(f"Source System: {sample_event.source_system}")
    
    # Show serialization
    print(f"\n📤 Event serialization:")
    event_dict = sample_event.to_dict()
    print(f"As dict: {event_dict}")
    
    # Show deserialization
    recreated_event = UnifiedEvent.from_dict(event_dict)
    print(f"Recreated from dict: {recreated_event.event_type} at {recreated_event.timestamp}")
    
    print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    # Run the demo
    try:
        asyncio.run(simple_event_demo())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()