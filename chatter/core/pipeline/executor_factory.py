"""Executor factory for creating workflow executors.

This module provides a factory pattern for creating executors based on
workflow type, configuration, or execution strategy.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

from chatter.core.pipeline.base import Executor
from chatter.core.pipeline.executors import (
    LangGraphExecutor,
    ParallelExecutor,
    SimpleExecutor,
)
from chatter.utils.logging import get_logger

if TYPE_CHECKING:
    from chatter.core.pipeline.base import ExecutionContext

logger = get_logger(__name__)


class ExecutorType(Enum):
    """Executor type enumeration."""

    LANGGRAPH = "langgraph"
    SIMPLE = "simple"
    PARALLEL = "parallel"
    AUTO = "auto"


class ExecutorFactory:
    """Factory for creating workflow executors.
    
    This factory provides:
    - Type-based executor creation
    - Auto-detection of best executor for workflow
    - Configuration-based executor customization
    - Executor registry for custom executors
    
    Example:
        factory = ExecutorFactory()
        executor = factory.create(ExecutorType.LANGGRAPH)
        
        # Or auto-detect
        executor = factory.create_for_workflow(workflow)
    """

    def __init__(self):
        """Initialize executor factory."""
        self._registry: dict[str, type[Executor]] = {
            ExecutorType.LANGGRAPH.value: LangGraphExecutor,
            ExecutorType.SIMPLE.value: SimpleExecutor,
            ExecutorType.PARALLEL.value: ParallelExecutor,
        }
        self._default_executor = ExecutorType.LANGGRAPH

    def create(
        self,
        executor_type: ExecutorType | str = ExecutorType.LANGGRAPH,
        **kwargs: Any,
    ) -> Executor:
        """Create executor by type.
        
        Args:
            executor_type: Type of executor to create
            **kwargs: Additional arguments for executor initialization
            
        Returns:
            Executor instance
            
        Raises:
            ValueError: If executor type is unknown
        """
        # Convert to string if enum
        if isinstance(executor_type, ExecutorType):
            executor_type = executor_type.value
        
        # Auto-detect if requested
        if executor_type == ExecutorType.AUTO.value:
            executor_type = self._default_executor.value
        
        # Get executor class from registry
        executor_class = self._registry.get(executor_type)
        if not executor_class:
            raise ValueError(
                f"Unknown executor type: {executor_type}. "
                f"Available types: {list(self._registry.keys())}"
            )
        
        # Create executor instance
        try:
            executor = executor_class(**kwargs)
            logger.debug(f"Created {executor_type} executor")
            return executor
        except Exception as e:
            logger.error(f"Failed to create {executor_type} executor: {e}")
            raise

    def create_for_workflow(
        self,
        workflow: Any,
        context: ExecutionContext | None = None,
    ) -> Executor:
        """Create best executor for workflow.
        
        Auto-detects the best executor based on workflow characteristics.
        
        Args:
            workflow: Workflow to execute
            context: Optional execution context for hints
            
        Returns:
            Executor instance
        """
        # Analyze workflow to determine best executor
        executor_type = self._detect_executor_type(workflow, context)
        
        # Create executor with appropriate config
        if executor_type == ExecutorType.PARALLEL:
            # Parallel executor with optimized concurrency
            return self.create(
                executor_type,
                max_concurrent=self._estimate_concurrency(workflow),
            )
        else:
            return self.create(executor_type)

    def register(self, name: str, executor_class: type[Executor]):
        """Register a custom executor.
        
        Args:
            name: Name for the executor
            executor_class: Executor class to register
        """
        self._registry[name] = executor_class
        logger.info(f"Registered custom executor: {name}")

    def set_default(self, executor_type: ExecutorType):
        """Set default executor type.
        
        Args:
            executor_type: Default executor type
        """
        self._default_executor = executor_type
        logger.info(f"Set default executor to: {executor_type.value}")

    def _detect_executor_type(
        self,
        workflow: Any,
        context: ExecutionContext | None = None,
    ) -> ExecutorType:
        """Detect best executor type for workflow.
        
        Args:
            workflow: Workflow to analyze
            context: Optional execution context
            
        Returns:
            Recommended executor type
        """
        # Check if LangGraph workflow
        workflow_class_name = workflow.__class__.__name__
        if "StateGraph" in workflow_class_name or "Graph" in workflow_class_name:
            return ExecutorType.LANGGRAPH
        
        # Check for parallel nodes
        nodes = getattr(workflow, "nodes", [])
        if len(nodes) > 3 and self._has_parallel_potential(workflow):
            return ExecutorType.PARALLEL
        
        # Default to simple for lightweight workflows
        if len(nodes) <= 3:
            return ExecutorType.SIMPLE
        
        # Fallback to LangGraph
        return ExecutorType.LANGGRAPH

    def _has_parallel_potential(self, workflow: Any) -> bool:
        """Check if workflow has parallel execution potential.
        
        Args:
            workflow: Workflow to analyze
            
        Returns:
            True if workflow can benefit from parallel execution
        """
        # Simple heuristic: check for independent nodes
        # Future: analyze dependency graph
        nodes = getattr(workflow, "nodes", [])
        
        # If workflow has metadata indicating parallel capability
        if hasattr(workflow, "parallel_capable"):
            return workflow.parallel_capable
        
        # If more than 3 nodes, assume some parallelism possible
        return len(nodes) > 3

    def _estimate_concurrency(self, workflow: Any) -> int:
        """Estimate optimal concurrency for workflow.
        
        Args:
            workflow: Workflow to analyze
            
        Returns:
            Recommended max concurrent tasks
        """
        nodes = getattr(workflow, "nodes", [])
        node_count = len(nodes)
        
        # Cap concurrency based on node count
        if node_count <= 3:
            return 3
        elif node_count <= 10:
            return 5
        else:
            return 10


# Global factory instance
_factory = ExecutorFactory()


def get_executor_factory() -> ExecutorFactory:
    """Get the global executor factory.
    
    Returns:
        ExecutorFactory instance
    """
    return _factory


def create_executor(
    executor_type: ExecutorType | str = ExecutorType.LANGGRAPH,
    **kwargs: Any,
) -> Executor:
    """Create executor using global factory.
    
    Args:
        executor_type: Type of executor to create
        **kwargs: Additional arguments for executor initialization
        
    Returns:
        Executor instance
    """
    return _factory.create(executor_type, **kwargs)


def create_executor_for_workflow(
    workflow: Any,
    context: ExecutionContext | None = None,
) -> Executor:
    """Create best executor for workflow using global factory.
    
    Args:
        workflow: Workflow to execute
        context: Optional execution context
        
    Returns:
        Executor instance
    """
    return _factory.create_for_workflow(workflow, context)
