"""Monitoring middleware for workflow pipeline.

This middleware integrates with the unified event system to publish workflow events
during execution, replacing direct monitoring calls.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from chatter.core.pipeline.base import ExecutionContext, ExecutionResult, Middleware
from chatter.services.workflow_events import (
    WorkflowEvent,
    WorkflowEventType,
    get_event_bus,
)
from chatter.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from chatter.core.workflow_node_factory import Workflow

logger = get_logger(__name__)


class MonitoringMiddleware(Middleware):
    """Middleware for workflow monitoring via event system.
    
    This middleware:
    - Publishes workflow lifecycle events (started, completed, failed)
    - Tracks execution time
    - Publishes resource loading events
    - Publishes token usage events
    - Integrates with WorkflowEventBus from Phase 2
    """

    def __init__(self, emit_resource_events: bool = True):
        """Initialize monitoring middleware.
        
        Args:
            emit_resource_events: Whether to emit resource loading events
        """
        self.emit_resource_events = emit_resource_events
        self.event_bus = get_event_bus()

    async def __call__(
        self,
        workflow: Workflow,
        context: ExecutionContext,
        next: Callable,
    ) -> ExecutionResult:
        """Execute with monitoring.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            next: Next middleware in chain
            
        Returns:
            Execution result
        """
        execution_id = context.metadata.get("execution_id", "unknown")
        user_id = context.user_id
        conversation_id = context.conversation_id
        
        start_time = time.time()
        
        try:
            # Emit workflow started event
            await self.event_bus.publish(
                WorkflowEvent.create(
                    event_type=WorkflowEventType.STARTED,
                    execution_id=execution_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    workflow_type=workflow.__class__.__name__,
                    provider=context.metadata.get("provider"),
                    model=context.metadata.get("model"),
                )
            )
            
            # Emit resource loading events if enabled
            if self.emit_resource_events:
                await self._emit_resource_events(
                    execution_id, user_id, conversation_id, context
                )
            
            # Emit execution started event
            await self.event_bus.publish(
                WorkflowEvent.create(
                    event_type=WorkflowEventType.EXECUTION_STARTED,
                    execution_id=execution_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                )
            )
            
            # Execute workflow
            result = await next(workflow, context)
            
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Emit token usage event if available
            if hasattr(result, "tokens_used") and result.tokens_used:
                await self.event_bus.publish(
                    WorkflowEvent.create(
                        event_type=WorkflowEventType.TOKEN_USAGE,
                        execution_id=execution_id,
                        user_id=user_id,
                        conversation_id=conversation_id,
                        tokens_used=result.tokens_used,
                        prompt_tokens=getattr(result, "prompt_tokens", None),
                        completion_tokens=getattr(result, "completion_tokens", None),
                        cost=getattr(result, "cost", 0.0),
                    )
                )
            
            # Emit execution completed event
            await self.event_bus.publish(
                WorkflowEvent.create(
                    event_type=WorkflowEventType.EXECUTION_COMPLETED,
                    execution_id=execution_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    execution_time_ms=execution_time_ms,
                    tokens_used=getattr(result, "tokens_used", 0),
                    cost=getattr(result, "cost", 0.0),
                )
            )
            
            return result
            
        except Exception as e:
            # Emit execution failed event
            await self.event_bus.publish(
                WorkflowEvent.create(
                    event_type=WorkflowEventType.EXECUTION_FAILED,
                    execution_id=execution_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    error=str(e),
                    error_type=type(e).__name__,
                )
            )
            raise
    
    async def _emit_resource_events(
        self,
        execution_id: str,
        user_id: str,
        conversation_id: str | None,
        context: ExecutionContext,
    ):
        """Emit resource loading events.
        
        Args:
            execution_id: Execution ID
            user_id: User ID
            conversation_id: Conversation ID
            context: Execution context
        """
        # LLM loaded event
        if context.metadata.get("provider") and context.metadata.get("model"):
            await self.event_bus.publish(
                WorkflowEvent.create(
                    event_type=WorkflowEventType.LLM_LOADED,
                    execution_id=execution_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    provider=context.metadata.get("provider"),
                    model=context.metadata.get("model"),
                )
            )
        
        # Tools loaded event
        if context.metadata.get("tools_count"):
            await self.event_bus.publish(
                WorkflowEvent.create(
                    event_type=WorkflowEventType.TOOLS_LOADED,
                    execution_id=execution_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    tool_count=context.metadata.get("tools_count"),
                )
            )
        
        # Retriever loaded event
        if context.metadata.get("has_retriever"):
            await self.event_bus.publish(
                WorkflowEvent.create(
                    event_type=WorkflowEventType.RETRIEVER_LOADED,
                    execution_id=execution_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                )
            )
