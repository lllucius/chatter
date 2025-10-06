"""Workflow executors implementing different execution strategies.

This module provides executor implementations for different workflow engines,
starting with LangGraph as the primary execution strategy.
"""

from __future__ import annotations

from typing import Any

from chatter.core.langgraph import workflow_manager
from chatter.core.pipeline.base import ExecutionContext, ExecutionResult, Executor
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class LangGraphExecutor(Executor):
    """Execute workflows using LangGraph engine.
    
    This executor wraps the existing LangGraph workflow_manager,
    providing a clean interface for the pipeline architecture.
    
    Example:
        executor = LangGraphExecutor()
        result = await executor.execute(workflow, context)
    """

    async def execute(
        self,
        workflow: Any,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """Execute workflow using LangGraph.
        
        Args:
            workflow: LangGraph workflow/graph to execute
            context: Execution context with state and metadata
            
        Returns:
            ExecutionResult with output and metrics
            
        Raises:
            Exception: If workflow execution fails
        """
        try:
            # Execute using LangGraph workflow_manager
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=context.initial_state,
                thread_id=context.conversation_id or context.workflow_id,
            )

            # Convert to ExecutionResult
            execution_result = ExecutionResult.from_langgraph(result)

            logger.debug(
                f"LangGraph execution completed for workflow {context.workflow_id}"
            )

            return execution_result

        except Exception as e:
            logger.error(
                f"LangGraph execution failed for workflow {context.workflow_id}: {e}",
                exc_info=True,
            )
            raise


class SimpleExecutor(Executor):
    """Simple sequential executor (future implementation).
    
    This executor will provide a lightweight alternative to LangGraph
    for simple workflows that don't need full graph capabilities.
    """

    async def execute(
        self,
        workflow: Any,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """Execute workflow sequentially.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            
        Returns:
            ExecutionResult
            
        Raises:
            NotImplementedError: Not yet implemented
        """
        raise NotImplementedError("SimpleExecutor not yet implemented")


class ParallelExecutor(Executor):
    """Parallel executor for independent workflow steps (future implementation).
    
    This executor will enable parallel execution of independent workflow nodes,
    improving performance for workflows with parallelizable steps.
    """

    async def execute(
        self,
        workflow: Any,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """Execute workflow with parallel steps.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            
        Returns:
            ExecutionResult
            
        Raises:
            NotImplementedError: Not yet implemented
        """
        raise NotImplementedError("ParallelExecutor not yet implemented")
