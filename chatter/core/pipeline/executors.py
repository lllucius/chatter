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
    """Simple sequential executor for lightweight workflows.
    
    This executor provides a lightweight alternative to LangGraph
    for simple workflows that don't need full graph capabilities.
    Executes nodes sequentially without complex routing.
    
    Example:
        executor = SimpleExecutor()
        result = await executor.execute(workflow, context)
    """

    async def execute(
        self,
        workflow: Any,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """Execute workflow sequentially.
        
        Args:
            workflow: Simple workflow with sequential nodes
            context: Execution context
            
        Returns:
            ExecutionResult
            
        Raises:
            ValueError: If workflow structure is invalid
        """
        try:
            state = context.initial_state.copy()
            
            # Get nodes from workflow
            nodes = getattr(workflow, "nodes", [])
            if not nodes:
                raise ValueError("Workflow has no nodes to execute")
            
            # Execute nodes sequentially
            for node in nodes:
                logger.debug(
                    f"Executing node {node.name} for workflow {context.workflow_id}"
                )
                
                # Execute node function
                node_func = getattr(node, "func", None)
                if not node_func:
                    raise ValueError(f"Node {node.name} has no executable function")
                
                # Call node function with state
                state = await node_func(state) if callable(node_func) else state
            
            # Build result
            result = ExecutionResult(
                output={"messages": state.get("messages", [])},
                state=state,
                metrics={
                    "execution_type": "simple_sequential",
                    "nodes_executed": len(nodes),
                },
            )
            
            logger.debug(
                f"Simple execution completed for workflow {context.workflow_id}"
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Simple execution failed for workflow {context.workflow_id}: {e}",
                exc_info=True,
            )
            raise


class ParallelExecutor(Executor):
    """Parallel executor for independent workflow steps.
    
    This executor enables parallel execution of independent workflow nodes,
    improving performance for workflows with parallelizable steps.
    Uses asyncio.gather for concurrent execution.
    
    Example:
        executor = ParallelExecutor(max_concurrent=5)
        result = await executor.execute(workflow, context)
    """

    def __init__(self, max_concurrent: int = 10):
        """Initialize parallel executor.
        
        Args:
            max_concurrent: Maximum number of concurrent executions
        """
        self.max_concurrent = max_concurrent

    async def execute(
        self,
        workflow: Any,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """Execute workflow with parallel steps.
        
        Args:
            workflow: Workflow with parallelizable nodes
            context: Execution context
            
        Returns:
            ExecutionResult
            
        Raises:
            ValueError: If workflow structure is invalid
        """
        import asyncio
        
        try:
            state = context.initial_state.copy()
            
            # Get node groups (nodes that can run in parallel)
            node_groups = self._get_parallel_groups(workflow)
            
            if not node_groups:
                raise ValueError("Workflow has no executable node groups")
            
            # Execute each group
            for group_idx, node_group in enumerate(node_groups):
                logger.debug(
                    f"Executing parallel group {group_idx + 1}/{len(node_groups)} "
                    f"({len(node_group)} nodes) for workflow {context.workflow_id}"
                )
                
                # Execute nodes in parallel
                tasks = []
                for node in node_group:
                    node_func = getattr(node, "func", None)
                    if node_func and callable(node_func):
                        tasks.append(node_func(state.copy()))
                
                # Limit concurrency
                if len(tasks) > self.max_concurrent:
                    # Execute in batches
                    results = []
                    for i in range(0, len(tasks), self.max_concurrent):
                        batch = tasks[i:i + self.max_concurrent]
                        batch_results = await asyncio.gather(*batch)
                        results.extend(batch_results)
                else:
                    # Execute all at once
                    results = await asyncio.gather(*tasks) if tasks else []
                
                # Merge results (simple merge - last result wins)
                for result_state in results:
                    if result_state:
                        state.update(result_state)
            
            # Build result
            result = ExecutionResult(
                output={"messages": state.get("messages", [])},
                state=state,
                metrics={
                    "execution_type": "parallel",
                    "node_groups": len(node_groups),
                    "max_concurrent": self.max_concurrent,
                },
            )
            
            logger.debug(
                f"Parallel execution completed for workflow {context.workflow_id}"
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Parallel execution failed for workflow {context.workflow_id}: {e}",
                exc_info=True,
            )
            raise
    
    def _get_parallel_groups(self, workflow: Any) -> list[list[Any]]:
        """Get groups of nodes that can execute in parallel.
        
        Args:
            workflow: Workflow to analyze
            
        Returns:
            List of node groups (each group can run in parallel)
        """
        nodes = getattr(workflow, "nodes", [])
        if not nodes:
            return []
        
        # Simple strategy: all nodes in one group (assumes independence)
        # Future enhancement: analyze dependencies and create proper groups
        return [nodes]
