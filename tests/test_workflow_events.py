"""Tests for workflow event system."""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch

from chatter.services.workflow_events import (
    WorkflowEvent,
    WorkflowEventBus,
    WorkflowEventType,
    get_event_bus,
)
from chatter.services.workflow_event_subscribers import (
    DatabaseEventSubscriber,
    MetricsEventSubscriber,
    LoggingEventSubscriber,
    initialize_event_subscribers,
)


def test_workflow_event_creation():
    """Test creating workflow events."""
    event = WorkflowEvent.create(
        event_type=WorkflowEventType.STARTED,
        execution_id="exec_123",
        user_id="user_456",
        conversation_id="conv_789",
        provider="openai",
        model="gpt-4",
    )
    
    assert event.event_type == WorkflowEventType.STARTED
    assert event.execution_id == "exec_123"
    assert event.user_id == "user_456"
    assert event.conversation_id == "conv_789"
    assert event.data["provider"] == "openai"
    assert event.data["model"] == "gpt-4"
    assert isinstance(event.timestamp, datetime)


def test_event_bus_subscribe_and_publish():
    """Test event bus subscription and publishing."""
    bus = WorkflowEventBus()
    handler_called = []
    
    async def test_handler(event: WorkflowEvent):
        handler_called.append(event)
    
    # Subscribe to specific event type
    bus.subscribe(WorkflowEventType.STARTED, test_handler)
    
    # Create and publish event
    event = WorkflowEvent.create(
        event_type=WorkflowEventType.STARTED,
        execution_id="exec_123",
        user_id="user_456",
    )
    
    # Run async publish
    import asyncio
    asyncio.run(bus.publish(event))
    
    # Verify handler was called
    assert len(handler_called) == 1
    assert handler_called[0] == event


def test_event_bus_global_subscription():
    """Test global event subscription."""
    bus = WorkflowEventBus()
    handler_called = []
    
    async def global_handler(event: WorkflowEvent):
        handler_called.append(event)
    
    # Subscribe to all events
    bus.subscribe(None, global_handler)
    
    # Publish different event types
    event1 = WorkflowEvent.create(
        event_type=WorkflowEventType.STARTED,
        execution_id="exec_1",
        user_id="user_1",
    )
    event2 = WorkflowEvent.create(
        event_type=WorkflowEventType.EXECUTION_COMPLETED,
        execution_id="exec_2",
        user_id="user_2",
    )
    
    import asyncio
    asyncio.run(bus.publish(event1))
    asyncio.run(bus.publish(event2))
    
    # Verify global handler received both
    assert len(handler_called) == 2
    assert handler_called[0] == event1
    assert handler_called[1] == event2


def test_event_bus_unsubscribe():
    """Test unsubscribing from events."""
    bus = WorkflowEventBus()
    handler_called = []
    
    async def test_handler(event: WorkflowEvent):
        handler_called.append(event)
    
    # Subscribe then unsubscribe
    bus.subscribe(WorkflowEventType.STARTED, test_handler)
    bus.unsubscribe(WorkflowEventType.STARTED, test_handler)
    
    # Publish event
    event = WorkflowEvent.create(
        event_type=WorkflowEventType.STARTED,
        execution_id="exec_123",
        user_id="user_456",
    )
    
    import asyncio
    asyncio.run(bus.publish(event))
    
    # Handler should not be called
    assert len(handler_called) == 0


@pytest.mark.asyncio
async def test_database_subscriber_started():
    """Test database subscriber handles started event."""
    mock_session = MagicMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    
    subscriber = DatabaseEventSubscriber(mock_session)
    
    event = WorkflowEvent.create(
        event_type=WorkflowEventType.STARTED,
        execution_id="exec_123",
        user_id="user_456",
        conversation_id="conv_789",
    )
    
    await subscriber.handle_started(event)
    
    # Verify session methods were called
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_metrics_subscriber():
    """Test metrics subscriber tracks events."""
    subscriber = MetricsEventSubscriber()
    
    # Start event
    start_event = WorkflowEvent.create(
        event_type=WorkflowEventType.STARTED,
        execution_id="exec_123",
        user_id="user_456",
    )
    await subscriber.handle_any_event(start_event)
    
    metrics = subscriber.get_metrics()
    assert metrics["total_executions"] == 1
    assert metrics["running_executions"] == 1
    
    # Completion event
    completion_event = WorkflowEvent.create(
        event_type=WorkflowEventType.EXECUTION_COMPLETED,
        execution_id="exec_123",
        user_id="user_456",
        tokens_used=100,
        cost=0.01,
    )
    await subscriber.handle_any_event(completion_event)
    
    metrics = subscriber.get_metrics()
    assert metrics["running_executions"] == 0
    assert metrics["completed_executions"] == 1
    assert metrics["total_tokens"] == 100
    assert metrics["total_cost"] == 0.01


@pytest.mark.asyncio
async def test_logging_subscriber():
    """Test logging subscriber captures events."""
    subscriber = LoggingEventSubscriber()
    
    event = WorkflowEvent.create(
        event_type=WorkflowEventType.STARTED,
        execution_id="exec_123",
        user_id="user_456",
        provider="openai",
    )
    
    await subscriber.handle_any_event(event)
    
    logs = subscriber.get_logs("exec_123")
    assert len(logs) == 1
    assert logs[0]["event_type"] == "workflow_started"
    assert logs[0]["data"]["provider"] == "openai"


def test_initialize_event_subscribers():
    """Test initializing all event subscribers."""
    mock_session = MagicMock()
    
    db_sub, metrics_sub, logging_sub = initialize_event_subscribers(mock_session)
    
    assert isinstance(db_sub, DatabaseEventSubscriber)
    assert isinstance(metrics_sub, MetricsEventSubscriber)
    assert isinstance(logging_sub, LoggingEventSubscriber)
    
    # Verify subscribers are registered with event bus
    bus = get_event_bus()
    assert len(bus._handlers[WorkflowEventType.STARTED]) >= 1
    assert len(bus._global_handlers) >= 2  # metrics and logging


def test_get_event_bus_singleton():
    """Test get_event_bus returns singleton."""
    bus1 = get_event_bus()
    bus2 = get_event_bus()
    
    assert bus1 is bus2
