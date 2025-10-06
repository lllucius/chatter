"""Pipeline base classes and protocols for workflow execution.

This module provides the core pipeline infrastructure for the Phase 3 redesign,
implementing a middleware-based execution pattern that replaces the procedural
execution flow from Phase 2.

Architecture:
- WorkflowPipeline: Main pipeline orchestrator
- Middleware: Protocol for pluggable execution middleware
- ExecutionResult: Standardized execution result
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


# Type aliases
Next = Callable[..., Awaitable["ExecutionResult"]]


class Middleware(Protocol):
    """Protocol for workflow execution middleware.
    
    Middleware can intercept and modify workflow execution at any stage,
    enabling cross-cutting concerns like monitoring, caching, retry logic,
    validation, and rate limiting.
    
    Example:
        class LoggingMiddleware:
            async def __call__(self, workflow, context, next):
                logger.info(f"Executing workflow: {workflow.id}")
                result = await next(workflow, context)
                logger.info(f"Completed workflow: {workflow.id}")
                return result
    """

    async def __call__(
        self,
        workflow: Any,  # Workflow type
        context: "ExecutionContext",
        next: Next,
    ) -> "ExecutionResult":
        """Process workflow execution.
        
        Args:
            workflow: Workflow to execute
            context: Execution context with state and metadata
            next: Next middleware in the chain
            
        Returns:
            ExecutionResult from the workflow execution
        """
        ...


class Executor(Protocol):
    """Protocol for workflow executors.
    
    Executors implement the actual workflow execution strategy.
    Different executors can use different engines (LangGraph, simple, parallel).
    
    Example:
        class LangGraphExecutor:
            async def execute(self, workflow, context):
                graph = self._build_graph(workflow)
                result = await graph.ainvoke(context.initial_state)
                return ExecutionResult.from_langgraph(result)
    """

    async def execute(
        self,
        workflow: Any,  # Workflow type
        context: "ExecutionContext",
    ) -> "ExecutionResult":
        """Execute workflow using specific strategy.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            
        Returns:
            ExecutionResult with output and metrics
        """
        ...


@dataclass
class ExecutionContext:
    """Execution context containing all workflow state and metadata.
    
    This provides a clean, immutable context object that flows through
    the middleware pipeline, replacing scattered parameters.
    
    Attributes:
        workflow_id: ID of the workflow being executed
        user_id: ID of the user executing the workflow
        conversation_id: ID of the conversation (if applicable)
        initial_state: Initial workflow state
        metadata: Additional metadata (provider, model, etc.)
        variables: Workflow variables
    """

    workflow_id: str
    user_id: str
    conversation_id: str | None
    initial_state: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def builder(cls) -> "ExecutionContextBuilder":
        """Create a builder for ExecutionContext.
        
        Returns:
            ExecutionContextBuilder instance
        """
        return ExecutionContextBuilder()


class ExecutionContextBuilder:
    """Builder for ExecutionContext.
    
    Provides a fluent interface for constructing ExecutionContext objects.
    
    Example:
        context = (
            ExecutionContext.builder()
            .workflow_id("wf_123")
            .user_id("user_456")
            .with_state({"messages": []})
            .with_metadata({"provider": "openai"})
            .build()
        )
    """

    def __init__(self):
        self._workflow_id: str | None = None
        self._user_id: str | None = None
        self._conversation_id: str | None = None
        self._initial_state: dict[str, Any] = {}
        self._metadata: dict[str, Any] = {}
        self._variables: dict[str, Any] = {}

    def workflow_id(self, workflow_id: str) -> "ExecutionContextBuilder":
        """Set workflow ID."""
        self._workflow_id = workflow_id
        return self

    def user_id(self, user_id: str) -> "ExecutionContextBuilder":
        """Set user ID."""
        self._user_id = user_id
        return self

    def conversation_id(
        self, conversation_id: str | None
    ) -> "ExecutionContextBuilder":
        """Set conversation ID."""
        self._conversation_id = conversation_id
        return self

    def with_state(
        self, initial_state: dict[str, Any]
    ) -> "ExecutionContextBuilder":
        """Set initial state."""
        self._initial_state = initial_state
        return self

    def with_metadata(
        self, metadata: dict[str, Any]
    ) -> "ExecutionContextBuilder":
        """Set metadata."""
        self._metadata = metadata
        return self

    def with_variables(
        self, variables: dict[str, Any]
    ) -> "ExecutionContextBuilder":
        """Set variables."""
        self._variables = variables
        return self

    def build(self) -> ExecutionContext:
        """Build ExecutionContext.
        
        Returns:
            ExecutionContext instance
            
        Raises:
            ValueError: If required fields are missing
        """
        if not self._workflow_id:
            raise ValueError("workflow_id is required")
        if not self._user_id:
            raise ValueError("user_id is required")

        return ExecutionContext(
            workflow_id=self._workflow_id,
            user_id=self._user_id,
            conversation_id=self._conversation_id,
            initial_state=self._initial_state,
            metadata=self._metadata,
            variables=self._variables,
        )


@dataclass
class ExecutionResult:
    """Standardized execution result.
    
    Provides a consistent result format across all execution strategies,
    replacing the various dict-based results from Phase 2.
    
    Attributes:
        output: Workflow output data
        state: Final workflow state
        metrics: Execution metrics (tokens, time, cost)
        metadata: Additional result metadata
        errors: Any errors encountered (for partial failures)
    """

    output: dict[str, Any]
    state: dict[str, Any]
    metrics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_langgraph(cls, langgraph_result: dict[str, Any]) -> "ExecutionResult":
        """Create ExecutionResult from LangGraph result.
        
        Args:
            langgraph_result: Result from LangGraph execution
            
        Returns:
            ExecutionResult instance
        """
        # Extract messages and convert to output
        messages = langgraph_result.get("messages", [])
        output = {
            "messages": messages,
            "response": messages[-1].content if messages else "",
        }

        # Extract metrics from usage_metadata
        usage = langgraph_result.get("usage_metadata", {})
        metrics = {
            "tokens_used": usage.get("total_tokens", 0),
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
        }

        return cls(
            output=output,
            state=langgraph_result,
            metrics=metrics,
            metadata={},
        )


class WorkflowPipeline:
    """Pipeline-based workflow execution engine.
    
    Replaces the procedural execution flow with a middleware pipeline,
    enabling flexible, composable workflow execution.
    
    Example:
        pipeline = (
            WorkflowPipeline(LangGraphExecutor())
            .use(MonitoringMiddleware())
            .use(CachingMiddleware())
            .use(RetryMiddleware())
        )
        
        result = await pipeline.execute(workflow, context)
    
    Attributes:
        executor: Workflow executor strategy
        middleware: List of registered middleware
    """

    def __init__(self, executor: Executor):
        """Initialize pipeline with executor.
        
        Args:
            executor: Executor strategy for workflow execution
        """
        self.executor = executor
        self.middleware: list[Middleware] = []

    def use(self, middleware: Middleware) -> "WorkflowPipeline":
        """Add middleware to the pipeline.
        
        Middleware is executed in the order it's added (first added = outermost).
        
        Args:
            middleware: Middleware to add
            
        Returns:
            Self for chaining
        """
        self.middleware.append(middleware)
        return self

    async def execute(
        self,
        workflow: Any,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """Execute workflow through middleware pipeline.
        
        Builds a middleware chain and executes the workflow through it.
        Each middleware can inspect/modify the request and response.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            
        Returns:
            ExecutionResult from workflow execution
        """
        # Base executor function
        async def execute_workflow(wf: Any, ctx: ExecutionContext) -> ExecutionResult:
            return await self.executor.execute(wf, ctx)

        # Build middleware chain (reverse order for correct execution)
        handler = execute_workflow
        for middleware in reversed(self.middleware):
            handler = self._wrap_middleware(middleware, handler)

        # Execute through pipeline
        try:
            result = await handler(workflow, context)
            logger.debug(
                f"Pipeline execution completed for workflow {context.workflow_id}"
            )
            return result
        except Exception as e:
            logger.error(
                f"Pipeline execution failed for workflow {context.workflow_id}: {e}",
                exc_info=True,
            )
            raise

    def _wrap_middleware(
        self,
        middleware: Middleware,
        next_handler: Next,
    ) -> Next:
        """Wrap middleware to create a handler.
        
        Args:
            middleware: Middleware to wrap
            next_handler: Next handler in the chain
            
        Returns:
            Wrapped handler function
        """

        async def handler(workflow: Any, context: ExecutionContext) -> ExecutionResult:
            return await middleware(workflow, context, next_handler)

        return handler
