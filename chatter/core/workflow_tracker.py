"""Unified workflow tracking system.

This module provides the WorkflowTracker class that consolidates all workflow
tracking, monitoring, and event emission into a single, unified system.

This replaces the previous fragmented tracking where the same information was
collected and synchronized across:
- PerformanceMonitor (debug logs)
- MonitoringService (runtime metrics)
- UnifiedEvent system (event emission)
- WorkflowExecution database updates

With a single tracker that handles all these concerns in one place.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.events import (
    EventCategory,
    EventPriority,
    UnifiedEvent,
    emit_event,
)
from chatter.core.monitoring import get_monitoring_service
from chatter.core.workflow_execution_context import ExecutionContext
from chatter.core.workflow_execution_result import ExecutionResult
from chatter.core.workflow_performance import PerformanceMonitor
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowTracker:
    """Single tracking system for all workflow execution monitoring.

    This class consolidates:
    1. PerformanceMonitor - Debug logs and performance tracking
    2. MonitoringService - Runtime metrics and workflow tracking
    3. UnifiedEvent - Event emission for workflow lifecycle
    4. WorkflowExecution - Database record updates

    Reducing 12-21 tracking calls per execution to just 2 unified calls:
    - tracker.start(context)
    - tracker.complete(context, result) or tracker.fail(context, error)
    """

    def __init__(
        self,
        session: AsyncSession,
        debug_mode: bool = False,
    ):
        """Initialize the workflow tracker.

        Args:
            session: Database session for execution record updates
            debug_mode: Enable debug logging
        """
        self.session = session
        self.debug_mode = debug_mode

        # Initialize integrated components
        self.performance_monitor = PerformanceMonitor(
            debug_mode=debug_mode
        )

    async def start(self, context: ExecutionContext) -> None:
        """Start tracking a workflow execution.

        This single call replaces:
        - Create/update WorkflowExecution record
        - monitoring.start_workflow_tracking()
        - emit workflow_started event
        - performance_monitor.start_workflow()

        Args:
            context: Execution context with all workflow state
        """
        # 1. Create execution record if definition ID is present
        if context.source_definition_id or context.source_template_id:
            await self._create_execution_record(context)

        # 2. Start monitoring service tracking
        try:
            monitoring = await get_monitoring_service()
            context.workflow_id = monitoring.start_workflow_tracking(
                **context.to_monitoring_config()
            )
        except Exception as e:
            logger.warning(
                f"Failed to start monitoring tracking: {e}"
            )
            context.workflow_id = None

        # 3. Emit workflow_started event
        try:
            await emit_event(
                UnifiedEvent(
                    category=EventCategory.WORKFLOW,
                    event_type="workflow_started",
                    user_id=context.user_id,
                    session_id=context.conversation_id,
                    correlation_id=context.correlation_id,
                    data=context.to_event_data(),
                    priority=EventPriority.NORMAL,
                )
            )
        except Exception as e:
            logger.warning(
                f"Failed to emit workflow_started event: {e}"
            )

        # 4. Start performance monitoring
        self.performance_monitor.start_workflow(context.execution_id)
        self.performance_monitor.log_debug(
            "Workflow execution started",
            data={
                "execution_id": context.execution_id,
                "workflow_type": context.workflow_type.value,
                "user_id": context.user_id,
            },
        )

        logger.info(
            f"Started tracking workflow execution {context.execution_id}",
            workflow_type=context.workflow_type.value,
            user_id=context.user_id,
        )

    async def complete(
        self,
        context: ExecutionContext,
        result: ExecutionResult,
    ) -> None:
        """Mark workflow execution as completed.

        This single call replaces:
        - Update WorkflowExecution record
        - monitoring.update_workflow_metrics()
        - monitoring.finish_workflow_tracking()
        - emit workflow_completed event
        - performance_monitor.end_workflow()

        Args:
            context: Execution context
            result: Execution result with metrics
        """
        # Update result's execution ID if not set
        if not result.execution_id:
            result.execution_id = context.execution_id
        if not result.conversation_id:
            result.conversation_id = context.conversation_id
        if not result.workflow_type:
            result.workflow_type = context.workflow_type.value

        # 1. Update execution record
        if context.source_definition_id or context.source_template_id:
            await self._update_execution_record(
                context, result, status="completed"
            )

        # 2. Update monitoring metrics
        if context.workflow_id:
            try:
                monitoring = await get_monitoring_service()
                monitoring.update_workflow_metrics(
                    workflow_id=context.workflow_id,
                    token_usage={
                        context.config.provider
                        or "unknown": result.tokens_used
                    },
                    tool_calls=result.tool_calls,
                )
                monitoring.finish_workflow_tracking(
                    context.workflow_id
                )
            except Exception as e:
                logger.warning(
                    f"Failed to update monitoring metrics: {e}"
                )

        # 3. Emit workflow_completed event
        try:
            await emit_event(
                UnifiedEvent(
                    category=EventCategory.WORKFLOW,
                    event_type="workflow_completed",
                    user_id=context.user_id,
                    session_id=context.conversation_id,
                    correlation_id=context.correlation_id,
                    data={
                        **context.to_event_data(),
                        **result.to_event_data(),
                    },
                    priority=EventPriority.NORMAL,
                )
            )
        except Exception as e:
            logger.warning(
                f"Failed to emit workflow_completed event: {e}"
            )

        # 4. End performance monitoring
        self.performance_monitor.end_workflow(
            context.execution_id, success=True
        )
        self.performance_monitor.log_debug(
            "Workflow execution completed",
            data={
                "execution_id": context.execution_id,
                "execution_time_ms": result.execution_time_ms,
                "tokens_used": result.tokens_used,
                "cost": result.cost,
            },
        )

        logger.info(
            f"Completed workflow execution {context.execution_id}",
            execution_time_ms=result.execution_time_ms,
            tokens_used=result.tokens_used,
            cost=result.cost,
        )

    async def fail(
        self,
        context: ExecutionContext,
        error: Exception,
    ) -> None:
        """Mark workflow execution as failed.

        This single call replaces:
        - Update WorkflowExecution record with error
        - monitoring.update_workflow_metrics() with error
        - monitoring.finish_workflow_tracking()
        - emit workflow_failed event
        - performance_monitor.end_workflow() with error

        Args:
            context: Execution context
            error: Exception that caused the failure
        """
        error_message = str(error)
        error_type = type(error).__name__

        # 1. Update execution record with failure
        if context.source_definition_id or context.source_template_id:
            await self._update_execution_record(
                context,
                None,
                status="failed",
                error_message=error_message,
            )

        # 2. Update monitoring metrics with error
        if context.workflow_id:
            try:
                monitoring = await get_monitoring_service()
                monitoring.update_workflow_metrics(
                    workflow_id=context.workflow_id,
                    error=error_message,
                )
                monitoring.finish_workflow_tracking(
                    context.workflow_id
                )
            except Exception as e:
                logger.warning(
                    f"Failed to update monitoring metrics: {e}"
                )

        # 3. Emit workflow_failed event
        try:
            await emit_event(
                UnifiedEvent(
                    category=EventCategory.WORKFLOW,
                    event_type="workflow_failed",
                    user_id=context.user_id,
                    session_id=context.conversation_id,
                    correlation_id=context.correlation_id,
                    priority=EventPriority.HIGH,
                    data={
                        **context.to_event_data(),
                        "error": error_message,
                        "error_type": error_type,
                    },
                )
            )
        except Exception as e:
            logger.warning(
                f"Failed to emit workflow_failed event: {e}"
            )

        # 4. End performance monitoring with error
        self.performance_monitor.end_workflow(
            context.execution_id,
            success=False,
            error_type=error_type,
        )
        self.performance_monitor.log_debug(
            "Workflow execution failed",
            data={
                "execution_id": context.execution_id,
                "error": error_message,
                "error_type": error_type,
            },
        )

        logger.error(
            f"Failed workflow execution {context.execution_id}",
            error=error_message,
            error_type=error_type,
        )

    def checkpoint(
        self, message: str, data: dict[str, Any] | None = None
    ) -> None:
        """Log a checkpoint for debugging.

        Args:
            message: Checkpoint message
            data: Optional data to log
        """
        self.performance_monitor.log_debug(message, data=data)

    def get_logs(self) -> list[dict[str, Any]]:
        """Get all debug logs.

        Returns:
            List of debug log entries
        """
        return self.performance_monitor.debug_logs

    async def _create_execution_record(
        self, context: ExecutionContext
    ) -> None:
        """Create workflow execution record in database.

        Args:
            context: Execution context
        """
        try:
            from chatter.services.workflow_management import (
                WorkflowManagementService,
            )

            workflow_service = WorkflowManagementService(
                self.session
            )

            # Create execution record with new Phase 4 signature
            execution = await workflow_service.create_workflow_execution(
                owner_id=context.user_id,
                definition_id=context.source_definition_id,
                template_id=context.source_template_id,
                workflow_type=context.workflow_type.value,
                workflow_config=context.config.workflow_config,
                input_data=context.config.input_data,
            )
            
            # Store execution ID in context for later updates
            context.execution_record_id = execution.id
            
            # Immediately update to running status with started_at timestamp
            await workflow_service.update_workflow_execution(
                execution_id=execution.id,
                owner_id=context.user_id,
                status="running",
                started_at=datetime.now(UTC),
            )

            logger.debug(
                f"Created execution record {execution.id} for {context.execution_id}"
            )
        except Exception as e:
            logger.warning(
                f"Failed to create execution record: {e}"
            )

    async def _update_execution_record(
        self,
        context: ExecutionContext,
        result: ExecutionResult | None,
        status: str,
        error_message: str | None = None,
    ) -> None:
        """Update workflow execution record in database.

        Args:
            context: Execution context
            result: Execution result (None for failures)
            status: Execution status
            error_message: Optional error message
        """
        try:
            from chatter.services.workflow_management import (
                WorkflowManagementService,
            )

            workflow_service = WorkflowManagementService(
                self.session
            )

            # Build update data
            update_data = {
                "status": status,
                "completed_at": datetime.now(UTC),
            }

            if result:
                update_data.update(
                    {
                        "execution_time_ms": result.execution_time_ms,
                        "output_data": result.to_dict(),
                        "tokens_used": result.tokens_used,
                        "cost": result.cost,
                        "execution_log": self.get_logs(),
                    }
                )

            if error_message:
                update_data["error"] = error_message
                update_data["execution_log"] = self.get_logs()

            # Get the execution record ID from context, or fall back to execution_id
            execution_id = getattr(context, 'execution_record_id', context.execution_id)
            
            # Actually update the execution record
            await workflow_service.update_workflow_execution(
                execution_id=execution_id,
                owner_id=context.user_id,
                **update_data
            )

            logger.debug(
                f"Updated execution record {execution_id} for {context.execution_id}"
            )
        except Exception as e:
            logger.warning(
                f"Failed to update execution record: {e}"
            )
