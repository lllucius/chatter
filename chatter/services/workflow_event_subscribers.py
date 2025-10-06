"""Event subscribers for workflow monitoring.

This module provides subscribers that react to workflow events and update
various monitoring systems (database, metrics, logs).

This replaces the fragmented monitoring approach with a unified event-driven system.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select, update

from chatter.models.workflow import WorkflowExecution
from chatter.services.workflow_events import (
    WorkflowEvent,
    WorkflowEventType,
    get_event_bus,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseEventSubscriber:
    """Subscribes to workflow events and updates WorkflowExecution records.
    
    This replaces direct database updates scattered across execution methods.
    """

    def __init__(self, session):
        """Initialize the database subscriber.
        
        Args:
            session: Database session for updates
        """
        self.session = session

    async def handle_started(self, event: WorkflowEvent):
        """Handle workflow started event.
        
        Updates execution record to running status with start time.
        """
        try:
            stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == event.execution_id)
                .values(
                    status="running",
                    started_at=event.timestamp,
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            
            logger.debug(
                f"Updated execution {event.execution_id} to running"
            )
        except Exception as e:
            logger.error(
                f"Failed to update execution started: {e}",
                exc_info=True,
            )
            await self.session.rollback()

    async def handle_completed(self, event: WorkflowEvent):
        """Handle workflow completed event.
        
        Updates execution record with success status and results.
        """
        try:
            stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == event.execution_id)
                .values(
                    status="completed",
                    completed_at=event.timestamp,
                    tokens_used=event.data.get("tokens_used", 0),
                    cost=event.data.get("cost", 0.0),
                    execution_time_ms=event.data.get("execution_time_ms"),
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            
            logger.debug(
                f"Updated execution {event.execution_id} to completed"
            )
        except Exception as e:
            logger.error(
                f"Failed to update execution completed: {e}",
                exc_info=True,
            )
            await self.session.rollback()

    async def handle_failed(self, event: WorkflowEvent):
        """Handle workflow failed event.
        
        Updates execution record with error status and details.
        """
        try:
            stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == event.execution_id)
                .values(
                    status="failed",
                    completed_at=event.timestamp,
                    error_message=event.data.get("error"),
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            
            logger.debug(
                f"Updated execution {event.execution_id} to failed"
            )
        except Exception as e:
            logger.error(
                f"Failed to update execution failed: {e}",
                exc_info=True,
            )
            await self.session.rollback()

    async def handle_token_usage(self, event: WorkflowEvent):
        """Handle token usage event.
        
        Updates execution record with token counts.
        """
        try:
            stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == event.execution_id)
                .values(
                    tokens_used=event.data.get("tokens_used", 0),
                    cost=event.data.get("cost", 0.0),
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            
            logger.debug(
                f"Updated execution {event.execution_id} token usage"
            )
        except Exception as e:
            logger.error(
                f"Failed to update token usage: {e}",
                exc_info=True,
            )
            await self.session.rollback()


class MetricsEventSubscriber:
    """Subscribes to workflow events and tracks real-time metrics.
    
    This replaces MonitoringService metric tracking.
    """

    def __init__(self):
        """Initialize the metrics subscriber."""
        self.metrics: dict[str, Any] = {
            "total_executions": 0,
            "running_executions": 0,
            "completed_executions": 0,
            "failed_executions": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "tool_calls": 0,
        }

    async def handle_any_event(self, event: WorkflowEvent):
        """Track all events for metrics.
        
        Updates in-memory metrics for real-time monitoring.
        """
        try:
            # Track execution lifecycle
            if event.event_type == WorkflowEventType.STARTED:
                self.metrics["total_executions"] += 1
                self.metrics["running_executions"] += 1
                
            elif event.event_type == WorkflowEventType.EXECUTION_COMPLETED:
                self.metrics["running_executions"] -= 1
                self.metrics["completed_executions"] += 1
                self.metrics["total_tokens"] += event.data.get("tokens_used", 0)
                self.metrics["total_cost"] += event.data.get("cost", 0.0)
                
            elif event.event_type == WorkflowEventType.EXECUTION_FAILED:
                self.metrics["running_executions"] -= 1
                self.metrics["failed_executions"] += 1
                
            elif event.event_type == WorkflowEventType.TOOL_CALLED:
                self.metrics["tool_calls"] += 1
                
        except Exception as e:
            logger.error(
                f"Failed to update metrics: {e}",
                exc_info=True,
            )

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics snapshot.
        
        Returns:
            Dictionary of current metrics
        """
        return self.metrics.copy()


class LoggingEventSubscriber:
    """Subscribes to workflow events and creates debug logs.
    
    This replaces PerformanceMonitor debug logging.
    """

    def __init__(self):
        """Initialize the logging subscriber."""
        self.logs: dict[str, list[dict[str, Any]]] = {}

    async def handle_any_event(self, event: WorkflowEvent):
        """Log all events for debugging.
        
        Creates structured debug logs for workflow execution analysis.
        """
        try:
            # Initialize logs for this execution if needed
            if event.execution_id not in self.logs:
                self.logs[event.execution_id] = []

            # Add log entry
            log_entry = {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "data": event.data,
            }
            self.logs[event.execution_id].append(log_entry)

            # Also log to standard logger
            logger.debug(
                f"Workflow event: {event.event_type.value}",
                execution_id=event.execution_id,
                **event.data,
            )
            
        except Exception as e:
            logger.error(
                f"Failed to log event: {e}",
                exc_info=True,
            )

    def get_logs(self, execution_id: str) -> list[dict[str, Any]]:
        """Get logs for a specific execution.
        
        Args:
            execution_id: Execution ID to get logs for
            
        Returns:
            List of log entries for the execution
        """
        return self.logs.get(execution_id, [])

    def clear_logs(self, execution_id: str):
        """Clear logs for a specific execution.
        
        Args:
            execution_id: Execution ID to clear logs for
        """
        if execution_id in self.logs:
            del self.logs[execution_id]


def initialize_event_subscribers(session) -> tuple[DatabaseEventSubscriber, MetricsEventSubscriber, LoggingEventSubscriber]:
    """Initialize all event subscribers and register them with the event bus.
    
    This should be called once at application startup to set up
    the unified monitoring system.
    
    Args:
        session: Database session for database subscriber
        
    Returns:
        Tuple of (database_subscriber, metrics_subscriber, logging_subscriber)
    """
    event_bus = get_event_bus()

    # Database subscriber
    db_subscriber = DatabaseEventSubscriber(session)
    event_bus.subscribe(WorkflowEventType.STARTED, db_subscriber.handle_started)
    event_bus.subscribe(
        WorkflowEventType.EXECUTION_COMPLETED,
        db_subscriber.handle_completed,
    )
    event_bus.subscribe(
        WorkflowEventType.EXECUTION_FAILED,
        db_subscriber.handle_failed,
    )
    event_bus.subscribe(
        WorkflowEventType.TOKEN_USAGE,
        db_subscriber.handle_token_usage,
    )

    # Metrics subscriber (subscribes to all events)
    metrics_subscriber = MetricsEventSubscriber()
    event_bus.subscribe(None, metrics_subscriber.handle_any_event)

    # Logging subscriber (subscribes to all events)
    logging_subscriber = LoggingEventSubscriber()
    event_bus.subscribe(None, logging_subscriber.handle_any_event)

    logger.info("Initialized workflow event subscribers")

    return db_subscriber, metrics_subscriber, logging_subscriber
