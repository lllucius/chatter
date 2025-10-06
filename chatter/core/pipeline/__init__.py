"""Workflow execution pipeline infrastructure.

This package provides the core pipeline architecture for Phase 3 workflow execution,
implementing a middleware-based pattern that replaces procedural execution.

Key Components:
- WorkflowPipeline: Main pipeline orchestrator
- Middleware: Protocol for pluggable middleware
- Executor: Protocol for execution strategies
- ExecutionContext: Standardized execution context
- ExecutionResult: Standardized execution result

Example:
    from chatter.core.pipeline import WorkflowPipeline, ExecutionContext
    from chatter.core.pipeline.executors import LangGraphExecutor
    from chatter.core.pipeline.middleware import MonitoringMiddleware
    
    pipeline = (
        WorkflowPipeline(LangGraphExecutor())
        .use(MonitoringMiddleware())
    )
    
    context = ExecutionContext.builder()\\
        .workflow_id("wf_123")\\
        .user_id("user_456")\\
        .with_state(initial_state)\\
        .build()
    
    result = await pipeline.execute(workflow, context)
"""

from chatter.core.pipeline.base import (
    ExecutionContext,
    ExecutionContextBuilder,
    ExecutionResult,
    Executor,
    Middleware,
    WorkflowPipeline,
)

__all__ = [
    "WorkflowPipeline",
    "Middleware",
    "Executor",
    "ExecutionContext",
    "ExecutionContextBuilder",
    "ExecutionResult",
]
