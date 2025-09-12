"""Comprehensive tests for the unified event system."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from chatter.core.audit_adapter import (
    setup_audit_integration,
)
from chatter.core.events import (
    EventCategory,
    EventManager,
    EventPriority,
    EventRouter,
    UnifiedEvent,
    create_analytics_event,
    create_audit_event,
    create_realtime_event,
    create_security_event,
    create_streaming_event,
    emit_audit_event,
    emit_realtime_event,
    emit_security_event,
    emit_system_alert,
    get_event_stats,
)
from chatter.core.security_adapter import (
    setup_security_integration,
)


class TestUnifiedEvent:
    """Test unified event data structure."""

    def test_create_unified_event(self):
        """Test creating a unified event."""
        event = UnifiedEvent(
            category=EventCategory.REALTIME,
            event_type="test.event",
            data={"message": "test"},
            user_id="user123",
            priority=EventPriority.HIGH,
        )

        assert event.category == EventCategory.REALTIME
        assert event.event_type == "test.event"
        assert event.data["message"] == "test"
        assert event.user_id == "user123"
        assert event.priority == EventPriority.HIGH
        assert event.id is not None
        assert isinstance(event.timestamp, datetime)

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = UnifiedEvent(
            category=EventCategory.SECURITY,
            event_type="auth.login",
            data={"success": True},
            user_id="user123",
        )

        event_dict = event.to_dict()

        assert event_dict["category"] == "security"
        assert event_dict["event_type"] == "auth.login"
        assert event_dict["data"]["success"] is True
        assert event_dict["user_id"] == "user123"
        assert "timestamp" in event_dict
        assert "id" in event_dict

    def test_event_from_dict(self):
        """Test creating event from dictionary."""
        event_data = {
            "id": "test-id",
            "category": "audit",
            "event_type": "resource.create",
            "data": {"resource_id": "123"},
            "user_id": "user456",
            "priority": "high",
            "timestamp": "2024-01-01T12:00:00+00:00",
        }

        event = UnifiedEvent.from_dict(event_data)

        assert event.id == "test-id"
        assert event.category == EventCategory.AUDIT
        assert event.event_type == "resource.create"
        assert event.data["resource_id"] == "123"
        assert event.user_id == "user456"
        assert event.priority == EventPriority.HIGH


class TestEventCreationFunctions:
    """Test event creation convenience functions."""

    def test_create_realtime_event(self):
        """Test creating real-time event."""
        event = create_realtime_event(
            event_type="document.uploaded",
            data={"document_id": "doc123"},
            user_id="user123",
        )

        assert event.category == EventCategory.REALTIME
        assert event.event_type == "document.uploaded"
        assert event.source_system == "sse"
        assert event.priority == EventPriority.NORMAL

    def test_create_security_event(self):
        """Test creating security event."""
        event = create_security_event(
            event_type="auth.login_failure",
            data={"ip_address": "192.168.1.1"},
            user_id="user123",
        )

        assert event.category == EventCategory.SECURITY
        assert event.event_type == "auth.login_failure"
        assert event.source_system == "monitoring"
        assert event.priority == EventPriority.HIGH

    def test_create_audit_event(self):
        """Test creating audit event."""
        event = create_audit_event(
            event_type="resource.delete",
            data={"resource_id": "res123"},
            user_id="user123",
        )

        assert event.category == EventCategory.AUDIT
        assert event.event_type == "resource.delete"
        assert event.source_system == "audit"
        assert event.priority == EventPriority.NORMAL

    def test_create_streaming_event(self):
        """Test creating streaming event."""
        event = create_streaming_event(
            event_type="token.generated",
            data={"token": "hello"},
            session_id="session123",
        )

        assert event.category == EventCategory.STREAMING
        assert event.event_type == "token.generated"
        assert event.source_system == "streaming"
        assert event.session_id == "session123"

    def test_create_analytics_event(self):
        """Test creating analytics event."""
        event = create_analytics_event(
            event_type="ab_test.conversion",
            data={"test_id": "test123", "variant": "A"},
            user_id="user123",
        )

        assert event.category == EventCategory.ANALYTICS
        assert event.event_type == "ab_test.conversion"
        assert event.source_system == "analytics"
        assert event.priority == EventPriority.LOW


class TestEventRouter:
    """Test event routing functionality."""

    @pytest.fixture
    def router(self):
        """Create a fresh event router for testing."""
        return EventRouter()

    @pytest.fixture
    def mock_emitter(self):
        """Create a mock emitter for testing."""
        emitter = Mock()
        emitter.emit = AsyncMock(return_value=True)
        return emitter

    @pytest.fixture
    def mock_handler(self):
        """Create a mock handler for testing."""
        return Mock()

    def test_register_emitter(self, router, mock_emitter):
        """Test registering an emitter."""
        router.register_emitter(EventCategory.REALTIME, mock_emitter)

        assert EventCategory.REALTIME in router._emitters
        assert mock_emitter in router._emitters[EventCategory.REALTIME]

    def test_add_handlers(self, router, mock_handler):
        """Test adding different types of handlers."""
        global_id = router.add_global_handler(mock_handler)
        category_id = router.add_category_handler(
            EventCategory.SECURITY, mock_handler
        )
        type_id = router.add_type_handler("test.event", mock_handler)

        assert isinstance(global_id, str)
        assert isinstance(category_id, str)
        assert isinstance(type_id, str)
        assert mock_handler in router._global_handlers
        assert (
            mock_handler
            in router._category_handlers[EventCategory.SECURITY]
        )
        assert mock_handler in router._type_handlers["test.event"]

    @pytest.mark.asyncio
    async def test_route_event(
        self, router, mock_emitter, mock_handler
    ):
        """Test routing an event to handlers and emitters."""
        # Set up router
        router.register_emitter(EventCategory.REALTIME, mock_emitter)
        router.add_global_handler(mock_handler)
        router.add_category_handler(
            EventCategory.REALTIME, mock_handler
        )
        router.add_type_handler("test.event", mock_handler)

        # Create and route event
        event = create_realtime_event(
            event_type="test.event", data={"message": "test"}
        )

        success = await router.route_event(event)

        assert success is True
        assert mock_handler.call_count == 3  # global + category + type
        mock_emitter.emit.assert_called_once_with(event)


class TestEventManager:
    """Test the unified event manager."""

    @pytest.fixture
    async def manager(self):
        """Create a fresh event manager for testing."""
        manager = EventManager()
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test manager initialization and shutdown."""
        manager = EventManager()

        assert not manager.is_initialized()

        await manager.initialize()
        assert manager.is_initialized()

        await manager.shutdown()
        # Note: shutdown doesn't change initialized status in current implementation

    @pytest.mark.asyncio
    async def test_emit_different_event_types(self, manager):
        """Test emitting different types of events."""
        # Test emitting various event types
        success1 = await manager.emit_realtime_event(
            "test.realtime", {"message": "realtime test"}
        )

        success2 = await manager.emit_security_event(
            "test.security",
            {"message": "security alert - test threat detected"},
        )

        success3 = await manager.emit_audit_event(
            "test.audit", {"action": "test action"}
        )

        success4 = await manager.emit_streaming_event(
            "test.streaming", {"token": "test"}
        )

        success5 = await manager.emit_analytics_event(
            "test.analytics", {"metric": "test"}
        )

        # All should succeed
        assert all([success1, success2, success3, success4, success5])

        # Check stats - note that security events may generate additional routed events
        stats = manager.get_stats()
        assert (
            stats["emitted"] >= 5
        )  # May be more due to cross-system routing
        assert (
            stats["processed"] >= 5
        )  # May be more due to cross-system routing

    @pytest.mark.asyncio
    async def test_system_alert(self, manager):
        """Test emitting system alerts."""
        success = await manager.emit_system_event(
            "system.test_alert",
            {"message": "Test alert", "severity": "error"},
        )

        assert success is True

        # Check that it was processed
        stats = manager.get_stats()
        assert stats["emitted"] >= 1


class TestEventIntegration:
    """Integration tests for the complete event system."""

    @pytest.mark.asyncio
    async def test_full_event_flow(self):
        """Test complete event flow through all systems."""
        # Initialize a fresh manager
        manager = EventManager()
        await manager.initialize()

        try:
            # Track events received by each system
            received_events = []

            def track_event(event):
                received_events.append(event)

            # Add global handler to track all events
            from chatter.core.events import event_router

            event_router.add_global_handler(track_event)

            # Emit events of different types
            await manager.emit_realtime_event(
                "document.processing_completed",
                {"document_id": "doc123", "status": "completed"},
                user_id="user123",
            )

            await manager.emit_security_event(
                "auth.login_failure",
                {
                    "message": "Login failure from 192.168.1.1",
                    "ip_address": "192.168.1.1",
                    "reason": "invalid_password",
                },
                user_id="user456",
            )

            await manager.emit_audit_event(
                "model.delete",
                {"model_id": "model123", "result": "success"},
                user_id="admin123",
            )

            # Give events time to propagate
            await asyncio.sleep(0.1)

            # Check that events were received and processed
            assert len(received_events) >= 3

            # Check event routing (security events should create audit events)
            event_types = [
                event.event_type for event in received_events
            ]

            # Should have original events
            assert "document.processing_completed" in event_types
            assert "auth.login_failure" in event_types
            assert "model.delete" in event_types

            # Should have routed events
            assert any(
                "security.auth.login_failure" in et
                for et in event_types
            )

            # Check stats
            stats = manager.get_stats()
            assert stats["emitted"] >= 3
            assert stats["processed"] >= 3

        finally:
            await manager.shutdown()

    @pytest.mark.asyncio
    async def test_convenience_functions(self):
        """Test convenience functions work correctly."""
        # Initialize system
        manager = EventManager()
        await manager.initialize()

        try:
            # Test convenience functions
            success1 = await emit_realtime_event(
                "test.convenience", {"message": "test"}
            )

            success2 = await emit_security_event(
                "test.security", {"message": "security test alert"}
            )

            success3 = await emit_audit_event(
                "test.audit", {"action": "test"}
            )

            success4 = await emit_system_alert(
                "Test system alert", severity="error"
            )

            assert all([success1, success2, success3, success4])

        finally:
            await manager.shutdown()


# Integration tests that require minimal setup
class TestMinimalIntegration:
    """Test integration with minimal dependencies."""

    def test_setup_functions(self):
        """Test setup functions don't crash."""
        # These should not raise exceptions
        setup_security_integration()
        setup_audit_integration()

    @pytest.mark.asyncio
    async def test_convenience_without_manager(self):
        """Test convenience functions work without initialized manager."""
        # These should not crash even without initialized manager
        success1 = await emit_realtime_event(
            "test.standalone", {"message": "test"}
        )

        success2 = await emit_system_alert(
            "Test alert", severity="info"
        )

        # They may return False if manager not initialized, but shouldn't crash
        assert isinstance(success1, bool)
        assert isinstance(success2, bool)

    def test_get_stats_without_manager(self):
        """Test getting stats works without initialized manager."""
        stats = get_event_stats()
        assert isinstance(stats, dict)
        assert "emitted" in stats
        assert "processed" in stats
