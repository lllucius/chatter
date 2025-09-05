"""Workflow execution timeouts and resource limits."""

from __future__ import annotations

import asyncio
import resource
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from chatter.config import settings
from chatter.utils.security_enhanced import get_secure_logger

logger = get_secure_logger(__name__)


@dataclass
class WorkflowLimits:
    """Resource limits for workflow execution."""

    execution_timeout: int
    step_timeout: int
    streaming_timeout: int
    max_tokens: int
    max_memory_mb: int
    max_concurrent: int


@dataclass
class WorkflowResourceUsage:
    """Resource usage tracking for workflows."""

    start_time: float
    tokens_used: int = 0
    memory_used_mb: float = 0.0
    steps_completed: int = 0
    errors_count: int = 0


class WorkflowTimeoutError(Exception):
    """Raised when workflow execution times out."""

    def __init__(self, message: str, timeout_type: str):
        super().__init__(message)
        self.timeout_type = timeout_type


class WorkflowResourceLimitError(Exception):
    """Raised when workflow exceeds resource limits."""

    def __init__(self, message: str, limit_type: str, current_value: Any, limit_value: Any):
        super().__init__(message)
        self.limit_type = limit_type
        self.current_value = current_value
        self.limit_value = limit_value


class WorkflowLimitManager:
    """Manages workflow execution timeouts and resource limits."""

    def __init__(self):
        """Initialize the limit manager."""
        self.active_workflows: dict[str, WorkflowResourceUsage] = {}
        self.user_workflow_counts: dict[str, int] = {}
        
    def get_default_limits(self) -> WorkflowLimits:
        """Get default workflow limits from configuration."""
        return WorkflowLimits(
            execution_timeout=settings.workflow_execution_timeout,
            step_timeout=settings.workflow_step_timeout,
            streaming_timeout=settings.workflow_streaming_timeout,
            max_tokens=settings.workflow_max_tokens,
            max_memory_mb=settings.workflow_max_memory_mb,
            max_concurrent=settings.workflow_max_concurrent,
        )

    def check_concurrent_limit(self, user_id: str, limits: WorkflowLimits) -> None:
        """Check if user has reached concurrent workflow limit."""
        current_count = self.user_workflow_counts.get(user_id, 0)
        if current_count >= limits.max_concurrent:
            raise WorkflowResourceLimitError(
                f"User {user_id} has reached maximum concurrent workflows limit",
                "concurrent_workflows",
                current_count,
                limits.max_concurrent,
            )

    def start_workflow_tracking(
        self, workflow_id: str, user_id: str, limits: WorkflowLimits
    ) -> None:
        """Start tracking resource usage for a workflow."""
        self.check_concurrent_limit(user_id, limits)
        
        self.active_workflows[workflow_id] = WorkflowResourceUsage(
            start_time=time.time()
        )
        self.user_workflow_counts[user_id] = (
            self.user_workflow_counts.get(user_id, 0) + 1
        )
        
        logger.info(
            "Started workflow tracking",
            workflow_id=workflow_id,
            user_id=user_id,
            concurrent_count=self.user_workflow_counts[user_id],
        )

    def end_workflow_tracking(self, workflow_id: str, user_id: str) -> WorkflowResourceUsage:
        """End tracking for a workflow and return final usage."""
        usage = self.active_workflows.pop(workflow_id, None)
        if usage is None:
            logger.warning("Attempted to end tracking for unknown workflow", workflow_id=workflow_id)
            return WorkflowResourceUsage(start_time=time.time())
            
        self.user_workflow_counts[user_id] = max(0, self.user_workflow_counts.get(user_id, 1) - 1)
        
        total_time = time.time() - usage.start_time
        logger.info(
            "Ended workflow tracking",
            workflow_id=workflow_id,
            user_id=user_id,
            total_time_seconds=total_time,
            tokens_used=usage.tokens_used,
            memory_used_mb=usage.memory_used_mb,
            steps_completed=usage.steps_completed,
            errors_count=usage.errors_count,
        )
        
        return usage

    def update_workflow_usage(
        self,
        workflow_id: str,
        tokens_delta: int = 0,
        memory_delta_mb: float = 0.0,
        steps_delta: int = 0,
        errors_delta: int = 0,
    ) -> None:
        """Update resource usage for a workflow."""
        if workflow_id not in self.active_workflows:
            return
            
        usage = self.active_workflows[workflow_id]
        usage.tokens_used += tokens_delta
        usage.memory_used_mb += memory_delta_mb
        usage.steps_completed += steps_delta
        usage.errors_count += errors_delta

    def check_workflow_limits(self, workflow_id: str, limits: WorkflowLimits) -> None:
        """Check if workflow is within resource limits."""
        if workflow_id not in self.active_workflows:
            return
            
        usage = self.active_workflows[workflow_id]
        current_time = time.time()
        
        # Check execution timeout
        elapsed_time = current_time - usage.start_time
        if elapsed_time > limits.execution_timeout:
            raise WorkflowTimeoutError(
                f"Workflow execution timed out after {elapsed_time:.1f} seconds",
                "execution_timeout"
            )
            
        # Check token limit
        if usage.tokens_used > limits.max_tokens:
            raise WorkflowResourceLimitError(
                f"Workflow exceeded token limit",
                "max_tokens",
                usage.tokens_used,
                limits.max_tokens,
            )
            
        # Check memory limit
        if usage.memory_used_mb > limits.max_memory_mb:
            raise WorkflowResourceLimitError(
                f"Workflow exceeded memory limit",
                "max_memory",
                usage.memory_used_mb,
                limits.max_memory_mb,
            )

    @asynccontextmanager
    async def workflow_timeout_context(
        self, workflow_id: str, timeout_seconds: int, timeout_type: str = "operation"
    ):
        """Context manager for operation-level timeouts."""
        try:
            async with asyncio.timeout(timeout_seconds):
                yield
        except asyncio.TimeoutError as e:
            raise WorkflowTimeoutError(
                f"Workflow {timeout_type} timed out after {timeout_seconds} seconds",
                timeout_type
            ) from e

    @asynccontextmanager
    async def step_timeout_context(self, workflow_id: str, limits: WorkflowLimits):
        """Context manager for individual step timeouts."""
        async with self.workflow_timeout_context(
            workflow_id, limits.step_timeout, "step"
        ):
            yield

    def get_current_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            # Get memory usage in KB and convert to MB
            memory_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            # On Linux, ru_maxrss is in KB; on macOS, it's in bytes
            import platform
            if platform.system() == "Darwin":  # macOS
                return memory_kb / (1024 * 1024)
            else:  # Linux
                return memory_kb / 1024
        except Exception:
            return 0.0

    async def monitor_workflow_resources(
        self, workflow_id: str, limits: WorkflowLimits, check_interval: float = 1.0
    ) -> AsyncGenerator[WorkflowResourceUsage, None]:
        """Monitor workflow resource usage in real-time."""
        if workflow_id not in self.active_workflows:
            return
            
        while workflow_id in self.active_workflows:
            try:
                # Update memory usage
                current_memory = self.get_current_memory_usage_mb()
                self.update_workflow_usage(
                    workflow_id, memory_delta_mb=current_memory
                )
                
                # Check limits
                self.check_workflow_limits(workflow_id, limits)
                
                # Yield current usage
                yield self.active_workflows[workflow_id]
                
                await asyncio.sleep(check_interval)
                
            except (WorkflowTimeoutError, WorkflowResourceLimitError):
                # Re-raise limit violations
                raise
            except Exception as e:
                logger.error(
                    "Error monitoring workflow resources",
                    workflow_id=workflow_id,
                    error=str(e),
                )
                await asyncio.sleep(check_interval)

    def get_workflow_stats(self) -> dict[str, Any]:
        """Get current workflow execution statistics."""
        active_count = len(self.active_workflows)
        total_users = len(self.user_workflow_counts)
        
        if active_count > 0:
            current_time = time.time()
            avg_runtime = sum(
                current_time - usage.start_time
                for usage in self.active_workflows.values()
            ) / active_count
            total_tokens = sum(
                usage.tokens_used for usage in self.active_workflows.values()
            )
            total_memory = sum(
                usage.memory_used_mb for usage in self.active_workflows.values()
            )
        else:
            avg_runtime = 0.0
            total_tokens = 0
            total_memory = 0.0
            
        return {
            "active_workflows": active_count,
            "total_users_with_workflows": total_users,
            "average_runtime_seconds": avg_runtime,
            "total_tokens_in_use": total_tokens,
            "total_memory_mb_in_use": total_memory,
            "user_workflow_counts": dict(self.user_workflow_counts),
        }


# Global limit manager instance
workflow_limit_manager = WorkflowLimitManager()