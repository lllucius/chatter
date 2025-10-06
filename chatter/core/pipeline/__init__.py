"""Workflow execution pipeline infrastructure.

This package provides the core pipeline architecture for Phase 3 workflow execution,
implementing a middleware-based pattern that replaces procedural execution.

Key Components:
- WorkflowPipeline: Main pipeline orchestrator
- Middleware: Protocol for pluggable middleware
- Executor: Protocol for execution strategies
- ExecutionContext: Standardized execution context
- ExecutionResult: Standardized execution result
- ExecutorFactory: Factory for creating executors

Example:
    from chatter.core.pipeline import (
        WorkflowPipeline,
        ExecutionContext,
        create_executor,
        ExecutorType,
    )
    from chatter.core.pipeline.middleware import MonitoringMiddleware
    
    # Create executor
    executor = create_executor(ExecutorType.LANGGRAPH)
    
    # Build pipeline
    pipeline = (
        WorkflowPipeline(executor)
        .use(MonitoringMiddleware())
    )
    
    # Create context
    context = ExecutionContext.builder()\\
        .workflow_id("wf_123")\\
        .user_id("user_456")\\
        .with_state(initial_state)\\
        .build()
    
    # Execute
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
from chatter.core.pipeline.executor_factory import (
    ExecutorFactory,
    ExecutorType,
    create_executor,
    create_executor_for_workflow,
    get_executor_factory,
)

__all__ = [
    "WorkflowPipeline",
    "Middleware",
    "Executor",
    "ExecutionContext",
    "ExecutionContextBuilder",
    "ExecutionResult",
    "ExecutorFactory",
    "ExecutorType",
    "create_executor",
    "create_executor_for_workflow",
    "get_executor_factory",
]
