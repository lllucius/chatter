"""Core workflow execution functionality."""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class StepStatus(str, Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    """Status of a workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowError(Exception):
    """Exception raised when workflow execution fails."""
    
    def __init__(self, message: str, step_id: Optional[str] = None):
        super().__init__(message)
        self.step_id = step_id


class WorkflowContext:
    """Context for workflow execution."""
    
    def __init__(self, workflow_id: str, data: Optional[Dict[str, Any]] = None):
        self.workflow_id = workflow_id
        self.data = data or {}
        self.variables: Dict[str, Any] = {}
        self.started_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
    
    def set_variable(self, key: str, value: Any) -> None:
        """Set a variable in the workflow context."""
        self.variables[key] = value
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a variable from the workflow context."""
        return self.variables.get(key, default)


class WorkflowResult:
    """Result of workflow execution."""
    
    def __init__(self, workflow_id: str, status: WorkflowStatus):
        self.workflow_id = workflow_id
        self.status = status
        self.data: Dict[str, Any] = {}
        self.errors: List[WorkflowError] = []
        self.started_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
    
    def add_error(self, error: WorkflowError) -> None:
        """Add an error to the result."""
        self.errors.append(error)
    
    def set_data(self, key: str, value: Any) -> None:
        """Set data in the result."""
        self.data[key] = value


class WorkflowStep:
    """Base class for workflow steps."""
    
    def __init__(self, step_id: str, name: str, description: Optional[str] = None):
        self.step_id = step_id
        self.name = name
        self.description = description
        self.status = StepStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[WorkflowError] = None
        self.dependencies: List[str] = []
    
    async def execute(self, context: WorkflowContext) -> Any:
        """Execute the workflow step."""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.utcnow()
        
        try:
            result = await self._execute_impl(context)
            self.status = StepStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            return result
        except Exception as e:
            self.error = WorkflowError(str(e), self.step_id)
            self.status = StepStatus.FAILED
            self.completed_at = datetime.utcnow()
            raise
    
    async def _execute_impl(self, context: WorkflowContext) -> Any:
        """Implementation of step execution."""
        raise NotImplementedError("Subclasses must implement _execute_impl")


class ConditionalStep(WorkflowStep):
    """A workflow step that executes conditionally."""
    
    def __init__(self, step_id: str, name: str, condition: str, 
                 true_step: WorkflowStep, false_step: Optional[WorkflowStep] = None):
        super().__init__(step_id, name)
        self.condition = condition
        self.true_step = true_step
        self.false_step = false_step
    
    async def _execute_impl(self, context: WorkflowContext) -> Any:
        """Execute conditional logic."""
        # Simple condition evaluation - in practice this would be more sophisticated
        condition_result = eval(self.condition, {}, context.variables)
        
        if condition_result:
            return await self.true_step.execute(context)
        elif self.false_step:
            return await self.false_step.execute(context)
        else:
            self.status = StepStatus.SKIPPED
            return None


class ParallelStep(WorkflowStep):
    """A workflow step that executes multiple steps in parallel."""
    
    def __init__(self, step_id: str, name: str, steps: List[WorkflowStep]):
        super().__init__(step_id, name)
        self.steps = steps
    
    async def _execute_impl(self, context: WorkflowContext) -> List[Any]:
        """Execute steps in parallel."""
        tasks = [step.execute(context) for step in self.steps]
        return await asyncio.gather(*tasks)


class LoopStep(WorkflowStep):
    """A workflow step that loops over a collection."""
    
    def __init__(self, step_id: str, name: str, collection_key: str, 
                 loop_step: WorkflowStep):
        super().__init__(step_id, name)
        self.collection_key = collection_key
        self.loop_step = loop_step
    
    async def _execute_impl(self, context: WorkflowContext) -> List[Any]:
        """Execute step for each item in collection."""
        collection = context.get_variable(self.collection_key, [])
        results = []
        
        for i, item in enumerate(collection):
            # Create a new context for each iteration
            loop_context = WorkflowContext(f"{context.workflow_id}_loop_{i}")
            loop_context.variables.update(context.variables)
            loop_context.set_variable("loop_item", item)
            loop_context.set_variable("loop_index", i)
            
            result = await self.loop_step.execute(loop_context)
            results.append(result)
        
        return results


class WorkflowExecutor:
    """Executor for workflows."""
    
    def __init__(self):
        self.running_workflows: Dict[str, WorkflowContext] = {}
    
    async def execute(self, steps: List[WorkflowStep], 
                     initial_data: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """Execute a workflow."""
        workflow_id = str(uuid4())
        context = WorkflowContext(workflow_id, initial_data)
        result = WorkflowResult(workflow_id, WorkflowStatus.RUNNING)
        
        self.running_workflows[workflow_id] = context
        
        try:
            for step in steps:
                # Check dependencies
                await self._wait_for_dependencies(step, context)
                
                try:
                    step_result = await step.execute(context)
                    result.set_data(step.step_id, step_result)
                except WorkflowError as e:
                    result.add_error(e)
                    result.status = WorkflowStatus.FAILED
                    break
            
            if result.status == WorkflowStatus.RUNNING:
                result.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            error = WorkflowError(str(e))
            result.add_error(error)
            result.status = WorkflowStatus.FAILED
        
        finally:
            result.completed_at = datetime.utcnow()
            context.completed_at = datetime.utcnow()
            del self.running_workflows[workflow_id]
        
        return result
    
    async def _wait_for_dependencies(self, step: WorkflowStep, 
                                   context: WorkflowContext) -> None:
        """Wait for step dependencies to complete."""
        # Simple implementation - in practice this would be more sophisticated
        pass
    
    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow."""
        if workflow_id in self.running_workflows:
            # Implementation would pause execution
            return True
        return False
    
    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        if workflow_id in self.running_workflows:
            # Implementation would resume execution
            return True
        return False
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id in self.running_workflows:
            del self.running_workflows[workflow_id]
            return True
        return False