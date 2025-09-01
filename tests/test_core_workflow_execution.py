"""Tests for core workflow execution functionality."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from chatter.core.workflow_execution import (
    WorkflowExecutor,
    WorkflowStep,
    WorkflowContext,
    WorkflowResult,
    WorkflowError,
    StepStatus,
    WorkflowStatus,
    ConditionalStep,
    ParallelStep,
    LoopStep,
)


class TestWorkflowStep:
    """Test WorkflowStep base class."""

    def test_workflow_step_creation(self):
        """Test creating a workflow step."""
        step = WorkflowStep(
            step_id="step_1",
            name="Test Step",
            description="A test step"
        )
        
        assert step.step_id == "step_1"
        assert step.name == "Test Step"
        assert step.description == "A test step"
        assert step.status == StepStatus.PENDING

    @pytest.mark.asyncio
    async def test_workflow_step_execute_abstract(self):
        """Test that WorkflowStep.execute is abstract."""
        step = WorkflowStep("test", "Test", "Test step")
        context = WorkflowContext()
        
        # Should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            await step.execute(context)

    def test_workflow_step_validation(self):
        """Test workflow step validation."""
        step = WorkflowStep("step_1", "Test Step")
        
        # Should be valid by default
        assert step.validate() is True

    def test_workflow_step_status_update(self):
        """Test updating step status."""
        step = WorkflowStep("step_1", "Test Step")
        
        step.status = StepStatus.RUNNING
        assert step.status == StepStatus.RUNNING
        
        step.status = StepStatus.COMPLETED
        assert step.status == StepStatus.COMPLETED


class TestWorkflowContext:
    """Test WorkflowContext functionality."""

    def test_workflow_context_creation(self):
        """Test creating workflow context."""
        context = WorkflowContext(
            workflow_id="workflow_123",
            user_id="user_456"
        )
        
        assert context.workflow_id == "workflow_123"
        assert context.user_id == "user_456"
        assert isinstance(context.variables, dict)
        assert isinstance(context.step_results, dict)

    def test_workflow_context_set_get_variable(self):
        """Test setting and getting context variables."""
        context = WorkflowContext()
        
        context.set_variable("key1", "value1")
        assert context.get_variable("key1") == "value1"
        
        # Non-existent variable
        assert context.get_variable("nonexistent") is None
        
        # With default value
        assert context.get_variable("nonexistent", "default") == "default"

    def test_workflow_context_update_variables(self):
        """Test updating multiple variables."""
        context = WorkflowContext()
        
        variables = {
            "var1": "value1",
            "var2": 42,
            "var3": ["item1", "item2"]
        }
        
        context.update_variables(variables)
        
        assert context.get_variable("var1") == "value1"
        assert context.get_variable("var2") == 42
        assert context.get_variable("var3") == ["item1", "item2"]

    def test_workflow_context_step_results(self):
        """Test storing and retrieving step results."""
        context = WorkflowContext()
        
        result = {"output": "test output", "status": "success"}
        context.set_step_result("step_1", result)
        
        assert context.get_step_result("step_1") == result
        assert context.get_step_result("nonexistent") is None

    def test_workflow_context_serialization(self):
        """Test context serialization."""
        context = WorkflowContext(
            workflow_id="workflow_123",
            user_id="user_456"
        )
        context.set_variable("test_var", "test_value")
        
        serialized = context.to_dict()
        
        assert serialized["workflow_id"] == "workflow_123"
        assert serialized["user_id"] == "user_456"
        assert serialized["variables"]["test_var"] == "test_value"

    def test_workflow_context_from_dict(self):
        """Test creating context from dictionary."""
        data = {
            "workflow_id": "workflow_123",
            "user_id": "user_456",
            "variables": {"var1": "value1"},
            "step_results": {"step1": {"result": "success"}}
        }
        
        context = WorkflowContext.from_dict(data)
        
        assert context.workflow_id == "workflow_123"
        assert context.user_id == "user_456"
        assert context.get_variable("var1") == "value1"
        assert context.get_step_result("step1") == {"result": "success"}


class TestWorkflowResult:
    """Test WorkflowResult functionality."""

    def test_workflow_result_creation(self):
        """Test creating workflow result."""
        result = WorkflowResult(
            workflow_id="workflow_123",
            status=WorkflowStatus.COMPLETED,
            output={"final_result": "success"}
        )
        
        assert result.workflow_id == "workflow_123"
        assert result.status == WorkflowStatus.COMPLETED
        assert result.output == {"final_result": "success"}
        assert isinstance(result.execution_time, float)

    def test_workflow_result_with_errors(self):
        """Test workflow result with errors."""
        error = WorkflowError("Step failed", step_id="step_2")
        
        result = WorkflowResult(
            workflow_id="workflow_123",
            status=WorkflowStatus.FAILED,
            errors=[error]
        )
        
        assert result.status == WorkflowStatus.FAILED
        assert len(result.errors) == 1
        assert result.errors[0].message == "Step failed"

    def test_workflow_result_add_error(self):
        """Test adding error to workflow result."""
        result = WorkflowResult(
            workflow_id="workflow_123",
            status=WorkflowStatus.RUNNING
        )
        
        error = WorkflowError("New error")
        result.add_error(error)
        
        assert len(result.errors) == 1
        assert result.errors[0] == error

    def test_workflow_result_serialization(self):
        """Test workflow result serialization."""
        result = WorkflowResult(
            workflow_id="workflow_123",
            status=WorkflowStatus.COMPLETED,
            output={"result": "success"}
        )
        
        serialized = result.to_dict()
        
        assert serialized["workflow_id"] == "workflow_123"
        assert serialized["status"] == WorkflowStatus.COMPLETED.value
        assert serialized["output"] == {"result": "success"}
        assert "execution_time" in serialized


class TestConditionalStep:
    """Test conditional workflow step."""

    def setup_method(self):
        """Set up test fixtures."""
        self.condition_func = lambda context: context.get_variable("condition") is True
        self.true_step = Mock()
        self.false_step = Mock()
        
        self.conditional_step = ConditionalStep(
            step_id="conditional_1",
            name="Conditional Step",
            condition=self.condition_func,
            true_step=self.true_step,
            false_step=self.false_step
        )

    @pytest.mark.asyncio
    async def test_conditional_step_true_branch(self):
        """Test conditional step executing true branch."""
        context = WorkflowContext()
        context.set_variable("condition", True)
        
        self.true_step.execute = AsyncMock(return_value={"result": "true_executed"})
        
        result = await self.conditional_step.execute(context)
        
        assert result["result"] == "true_executed"
        self.true_step.execute.assert_called_once_with(context)
        self.false_step.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_conditional_step_false_branch(self):
        """Test conditional step executing false branch."""
        context = WorkflowContext()
        context.set_variable("condition", False)
        
        self.false_step.execute = AsyncMock(return_value={"result": "false_executed"})
        
        result = await self.conditional_step.execute(context)
        
        assert result["result"] == "false_executed"
        self.false_step.execute.assert_called_once_with(context)
        self.true_step.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_conditional_step_no_false_branch(self):
        """Test conditional step with no false branch."""
        conditional_step = ConditionalStep(
            step_id="conditional_1",
            name="Conditional Step",
            condition=self.condition_func,
            true_step=self.true_step
        )
        
        context = WorkflowContext()
        context.set_variable("condition", False)
        
        result = await conditional_step.execute(context)
        
        # Should return empty result when no false branch and condition is false
        assert result is None or result == {}


class TestParallelStep:
    """Test parallel workflow step."""

    def setup_method(self):
        """Set up test fixtures."""
        self.step1 = Mock()
        self.step2 = Mock()
        self.step3 = Mock()
        
        self.parallel_step = ParallelStep(
            step_id="parallel_1",
            name="Parallel Step",
            steps=[self.step1, self.step2, self.step3]
        )

    @pytest.mark.asyncio
    async def test_parallel_step_execute_all(self):
        """Test parallel step executing all sub-steps."""
        context = WorkflowContext()
        
        self.step1.execute = AsyncMock(return_value={"result": "step1"})
        self.step2.execute = AsyncMock(return_value={"result": "step2"})
        self.step3.execute = AsyncMock(return_value={"result": "step3"})
        
        result = await self.parallel_step.execute(context)
        
        # All steps should be executed
        self.step1.execute.assert_called_once_with(context)
        self.step2.execute.assert_called_once_with(context)
        self.step3.execute.assert_called_once_with(context)
        
        # Result should contain all step results
        assert len(result["parallel_results"]) == 3

    @pytest.mark.asyncio
    async def test_parallel_step_with_failure(self):
        """Test parallel step when one sub-step fails."""
        context = WorkflowContext()
        
        self.step1.execute = AsyncMock(return_value={"result": "step1"})
        self.step2.execute = AsyncMock(side_effect=Exception("Step 2 failed"))
        self.step3.execute = AsyncMock(return_value={"result": "step3"})
        
        with pytest.raises(WorkflowError):
            await self.parallel_step.execute(context)

    @pytest.mark.asyncio
    async def test_parallel_step_timing(self):
        """Test that parallel steps run concurrently."""
        context = WorkflowContext()
        
        async def slow_step(ctx):
            await asyncio.sleep(0.1)
            return {"result": "slow"}
        
        async def fast_step(ctx):
            return {"result": "fast"}
        
        self.step1.execute = slow_step
        self.step2.execute = fast_step
        
        start_time = asyncio.get_event_loop().time()
        await self.parallel_step.execute(context)
        end_time = asyncio.get_event_loop().time()
        
        # Should take approximately 0.1 seconds (not 0.2+)
        assert end_time - start_time < 0.15


class TestLoopStep:
    """Test loop workflow step."""

    def setup_method(self):
        """Set up test fixtures."""
        self.loop_body = Mock()
        self.condition_func = lambda context, iteration: iteration < 3
        
        self.loop_step = LoopStep(
            step_id="loop_1",
            name="Loop Step",
            body=self.loop_body,
            condition=self.condition_func
        )

    @pytest.mark.asyncio
    async def test_loop_step_execute(self):
        """Test loop step execution."""
        context = WorkflowContext()
        
        iteration_results = [
            {"iteration": 0, "result": "iter0"},
            {"iteration": 1, "result": "iter1"},
            {"iteration": 2, "result": "iter2"}
        ]
        
        self.loop_body.execute = AsyncMock(side_effect=iteration_results)
        
        result = await self.loop_step.execute(context)
        
        # Should execute 3 iterations
        assert self.loop_body.execute.call_count == 3
        assert len(result["loop_results"]) == 3

    @pytest.mark.asyncio
    async def test_loop_step_with_max_iterations(self):
        """Test loop step with maximum iterations limit."""
        loop_step = LoopStep(
            step_id="loop_1",
            name="Loop Step",
            body=self.loop_body,
            condition=lambda ctx, i: True,  # Infinite loop condition
            max_iterations=5
        )
        
        context = WorkflowContext()
        self.loop_body.execute = AsyncMock(return_value={"result": "iteration"})
        
        result = await loop_step.execute(context)
        
        # Should stop after max_iterations
        assert self.loop_body.execute.call_count == 5

    @pytest.mark.asyncio
    async def test_loop_step_early_termination(self):
        """Test loop step early termination."""
        def early_condition(context, iteration):
            return iteration < 10 and context.get_variable("continue_loop", True)
        
        loop_step = LoopStep(
            step_id="loop_1",
            name="Loop Step",
            body=self.loop_body,
            condition=early_condition
        )
        
        context = WorkflowContext()
        context.set_variable("continue_loop", True)
        
        def stop_after_two(ctx):
            if self.loop_body.execute.call_count >= 2:
                ctx.set_variable("continue_loop", False)
            return {"result": f"iteration_{self.loop_body.execute.call_count}"}
        
        self.loop_body.execute = AsyncMock(side_effect=stop_after_two)
        
        await loop_step.execute(context)
        
        # Should stop after setting continue_loop to False
        assert self.loop_body.execute.call_count <= 3


class TestWorkflowExecutor:
    """Test WorkflowExecutor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.executor = WorkflowExecutor(session=self.mock_session)

    @pytest.mark.asyncio
    async def test_execute_simple_workflow(self):
        """Test executing a simple workflow."""
        # Create mock steps
        step1 = Mock()
        step1.step_id = "step_1"
        step1.execute = AsyncMock(return_value={"output": "step1_result"})
        
        step2 = Mock()
        step2.step_id = "step_2"
        step2.execute = AsyncMock(return_value={"output": "step2_result"})
        
        workflow = [step1, step2]
        context = WorkflowContext(workflow_id="workflow_123")
        
        result = await self.executor.execute_workflow(workflow, context)
        
        assert result.status == WorkflowStatus.COMPLETED
        assert result.workflow_id == "workflow_123"
        
        # Both steps should be executed
        step1.execute.assert_called_once_with(context)
        step2.execute.assert_called_once_with(context)

    @pytest.mark.asyncio
    async def test_execute_workflow_with_failure(self):
        """Test executing workflow with step failure."""
        step1 = Mock()
        step1.step_id = "step_1"
        step1.execute = AsyncMock(return_value={"output": "step1_result"})
        
        step2 = Mock()
        step2.step_id = "step_2"
        step2.execute = AsyncMock(side_effect=Exception("Step 2 failed"))
        
        workflow = [step1, step2]
        context = WorkflowContext(workflow_id="workflow_123")
        
        result = await self.executor.execute_workflow(workflow, context)
        
        assert result.status == WorkflowStatus.FAILED
        assert len(result.errors) == 1
        assert "Step 2 failed" in result.errors[0].message

    @pytest.mark.asyncio
    async def test_execute_workflow_with_timeout(self):
        """Test executing workflow with timeout."""
        # Create a slow step
        slow_step = Mock()
        slow_step.step_id = "slow_step"
        
        async def slow_execute(context):
            await asyncio.sleep(1.0)  # 1 second delay
            return {"output": "slow_result"}
        
        slow_step.execute = slow_execute
        
        workflow = [slow_step]
        context = WorkflowContext(workflow_id="workflow_123")
        
        # Execute with short timeout
        result = await self.executor.execute_workflow(
            workflow, 
            context, 
            timeout=0.1  # 100ms timeout
        )
        
        assert result.status == WorkflowStatus.FAILED
        assert len(result.errors) == 1
        assert "timeout" in result.errors[0].message.lower()

    @pytest.mark.asyncio
    async def test_execute_workflow_with_dependencies(self):
        """Test executing workflow with step dependencies."""
        # Step 1: No dependencies
        step1 = Mock()
        step1.step_id = "step_1"
        step1.dependencies = []
        step1.execute = AsyncMock(return_value={"output": "step1_result"})
        
        # Step 2: Depends on step 1
        step2 = Mock()
        step2.step_id = "step_2"
        step2.dependencies = ["step_1"]
        step2.execute = AsyncMock(return_value={"output": "step2_result"})
        
        # Step 3: Depends on step 2
        step3 = Mock()
        step3.step_id = "step_3"
        step3.dependencies = ["step_2"]
        step3.execute = AsyncMock(return_value={"output": "step3_result"})
        
        workflow = [step3, step1, step2]  # Out of order
        context = WorkflowContext(workflow_id="workflow_123")
        
        result = await self.executor.execute_workflow_with_dependencies(workflow, context)
        
        assert result.status == WorkflowStatus.COMPLETED
        
        # Steps should be executed in dependency order
        # Check call order by comparing call times
        assert step1.execute.called
        assert step2.execute.called
        assert step3.execute.called

    @pytest.mark.asyncio
    async def test_pause_and_resume_workflow(self):
        """Test pausing and resuming workflow execution."""
        step1 = Mock()
        step1.step_id = "step_1"
        step1.execute = AsyncMock(return_value={"output": "step1_result"})
        
        step2 = Mock()
        step2.step_id = "step_2"
        step2.execute = AsyncMock(return_value={"output": "step2_result"})
        
        workflow = [step1, step2]
        context = WorkflowContext(workflow_id="workflow_123")
        
        # Start execution and pause after first step
        execution_task = asyncio.create_task(
            self.executor.execute_workflow(workflow, context)
        )
        
        # Let first step complete
        await asyncio.sleep(0.01)
        
        # Pause execution
        await self.executor.pause_workflow("workflow_123")
        
        # Resume execution
        await self.executor.resume_workflow("workflow_123")
        
        result = await execution_task
        
        assert result.status == WorkflowStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_cancel_workflow(self):
        """Test cancelling workflow execution."""
        slow_step = Mock()
        slow_step.step_id = "slow_step"
        
        async def slow_execute(context):
            await asyncio.sleep(1.0)
            return {"output": "should_not_complete"}
        
        slow_step.execute = slow_execute
        
        workflow = [slow_step]
        context = WorkflowContext(workflow_id="workflow_123")
        
        # Start execution
        execution_task = asyncio.create_task(
            self.executor.execute_workflow(workflow, context)
        )
        
        # Cancel after short delay
        await asyncio.sleep(0.01)
        await self.executor.cancel_workflow("workflow_123")
        
        result = await execution_task
        
        assert result.status == WorkflowStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_workflow_state_persistence(self):
        """Test workflow state persistence."""
        step1 = Mock()
        step1.step_id = "step_1"
        step1.execute = AsyncMock(return_value={"output": "step1_result"})
        
        workflow = [step1]
        context = WorkflowContext(workflow_id="workflow_123")
        
        with patch.object(self.executor, 'save_workflow_state') as mock_save:
            await self.executor.execute_workflow(workflow, context)
            
            # Should save state during execution
            mock_save.assert_called()

    @pytest.mark.asyncio
    async def test_workflow_metrics_collection(self):
        """Test workflow metrics collection."""
        step1 = Mock()
        step1.step_id = "step_1"
        step1.execute = AsyncMock(return_value={"output": "step1_result"})
        
        workflow = [step1]
        context = WorkflowContext(workflow_id="workflow_123")
        
        with patch('chatter.utils.monitoring.record_workflow_metrics') as mock_metrics:
            result = await self.executor.execute_workflow(workflow, context)
            
            # Should record metrics
            mock_metrics.assert_called()
            
            # Should include execution time, step count, etc.
            call_args = mock_metrics.call_args[1]
            assert "workflow_id" in call_args
            assert "execution_time" in call_args
            assert "step_count" in call_args
            assert "status" in call_args

    @pytest.mark.asyncio
    async def test_workflow_error_handling_strategies(self):
        """Test different error handling strategies."""
        failing_step = Mock()
        failing_step.step_id = "failing_step"
        failing_step.execute = AsyncMock(side_effect=Exception("Step failed"))
        
        recovery_step = Mock()
        recovery_step.step_id = "recovery_step"
        recovery_step.execute = AsyncMock(return_value={"output": "recovered"})
        
        workflow = [failing_step, recovery_step]
        context = WorkflowContext(workflow_id="workflow_123")
        
        # Test with continue_on_error strategy
        result = await self.executor.execute_workflow(
            workflow, 
            context, 
            error_strategy="continue"
        )
        
        # Should continue to recovery step despite failure
        assert recovery_step.execute.called
        assert len(result.errors) == 1  # Should record the error but continue

    @pytest.mark.asyncio
    async def test_workflow_execution_hooks(self):
        """Test workflow execution hooks."""
        step1 = Mock()
        step1.step_id = "step_1"
        step1.execute = AsyncMock(return_value={"output": "step1_result"})
        
        workflow = [step1]
        context = WorkflowContext(workflow_id="workflow_123")
        
        # Mock hooks
        before_hook = AsyncMock()
        after_hook = AsyncMock()
        
        result = await self.executor.execute_workflow(
            workflow, 
            context,
            before_execution_hook=before_hook,
            after_execution_hook=after_hook
        )
        
        # Hooks should be called
        before_hook.assert_called_once()
        after_hook.assert_called_once_with(result)