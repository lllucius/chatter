"""Tests for workflow execution core functionality."""

import asyncio
from unittest.mock import patch

import pytest

from chatter.core.exceptions import WorkflowExecutionError
from chatter.core.workflow_execution import (
    WorkflowExecutor,
    WorkflowResult,
    WorkflowStep,
)


@pytest.mark.unit
class TestWorkflowExecutor:
    """Test workflow execution core functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.workflow_executor = WorkflowExecutor()

    @pytest.mark.asyncio
    async def test_execute_simple_workflow_success(self):
        """Test successful execution of simple workflow."""
        # Arrange
        workflow_steps = [
            WorkflowStep(
                id="step-1",
                name="Data Input",
                type="input",
                config={"source": "user_input"}
            ),
            WorkflowStep(
                id="step-2",
                name="Process Data",
                type="llm_call",
                config={"model": "gpt-4", "prompt": "Process the input"}
            ),
            WorkflowStep(
                id="step-3",
                name="Format Output",
                type="formatter",
                config={"format": "json"}
            )
        ]

        workflow_config = {
            "id": "simple-workflow",
            "name": "Simple Processing Workflow",
            "steps": workflow_steps
        }

        WorkflowResult(
            workflow_id="simple-workflow",
            status="completed",
            outputs={"formatted_data": {"result": "processed"}},
            execution_time=1.5
        )

        with patch.object(self.workflow_executor, '_execute_step') as mock_execute_step:
            mock_execute_step.side_effect = [
                {"input_data": "user input"},
                {"processed_data": "AI processed result"},
                {"formatted_data": {"result": "processed"}}
            ]

            # Act
            result = await self.workflow_executor.execute_workflow(workflow_config)

            # Assert
            assert result.status == "completed"
            assert "formatted_data" in result.outputs
            assert mock_execute_step.call_count == 3

    @pytest.mark.asyncio
    async def test_execute_workflow_with_conditional_steps(self):
        """Test workflow execution with conditional branching."""
        # Arrange
        workflow_steps = [
            WorkflowStep(
                id="step-1",
                name="Check Condition",
                type="condition",
                config={"condition": "input_length > 100"}
            ),
            WorkflowStep(
                id="step-2a",
                name="Long Text Processing",
                type="llm_call",
                config={"model": "gpt-4"},
                condition="step-1.result == true"
            ),
            WorkflowStep(
                id="step-2b",
                name="Short Text Processing",
                type="llm_call",
                config={"model": "gpt-3.5-turbo"},
                condition="step-1.result == false"
            )
        ]

        workflow_config = {
            "id": "conditional-workflow",
            "steps": workflow_steps
        }

        with patch.object(self.workflow_executor, '_execute_step') as mock_execute_step:
            mock_execute_step.side_effect = [
                {"result": True},  # Condition step
                {"processed_data": "Long text result"}  # Long text processing
            ]

            with patch.object(self.workflow_executor, '_evaluate_condition') as mock_condition:
                mock_condition.side_effect = [True, False]  # First condition true, second false

                # Act
                result = await self.workflow_executor.execute_workflow(workflow_config)

                # Assert
                assert result.status == "completed"
                # Should execute step-1 and step-2a, but not step-2b
                assert mock_execute_step.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_workflow_with_parallel_steps(self):
        """Test workflow execution with parallel steps."""
        # Arrange
        workflow_steps = [
            WorkflowStep(
                id="step-1",
                name="Input",
                type="input",
                config={"source": "user_input"}
            ),
            WorkflowStep(
                id="step-2a",
                name="Process Path A",
                type="llm_call",
                config={"model": "gpt-4"},
                parallel_group="group-1"
            ),
            WorkflowStep(
                id="step-2b",
                name="Process Path B",
                type="llm_call",
                config={"model": "claude-3"},
                parallel_group="group-1"
            ),
            WorkflowStep(
                id="step-3",
                name="Combine Results",
                type="aggregator",
                config={"method": "merge"},
                dependencies=["step-2a", "step-2b"]
            )
        ]

        workflow_config = {
            "id": "parallel-workflow",
            "steps": workflow_steps
        }

        with patch.object(self.workflow_executor, '_execute_step') as mock_execute_step:
            mock_execute_step.side_effect = [
                {"input_data": "user input"},
                {"result_a": "Path A result"},
                {"result_b": "Path B result"},
                {"combined": "Merged results"}
            ]

            with patch.object(self.workflow_executor, '_execute_parallel_steps') as mock_parallel:
                mock_parallel.return_value = [
                    {"result_a": "Path A result"},
                    {"result_b": "Path B result"}
                ]

                # Act
                result = await self.workflow_executor.execute_workflow(workflow_config)

                # Assert
                assert result.status == "completed"
                mock_parallel.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_workflow_step_failure(self):
        """Test workflow execution when a step fails."""
        # Arrange
        workflow_steps = [
            WorkflowStep(
                id="step-1",
                name="Successful Step",
                type="input",
                config={}
            ),
            WorkflowStep(
                id="step-2",
                name="Failing Step",
                type="llm_call",
                config={"model": "gpt-4"}
            )
        ]

        workflow_config = {
            "id": "failing-workflow",
            "steps": workflow_steps
        }

        with patch.object(self.workflow_executor, '_execute_step') as mock_execute_step:
            mock_execute_step.side_effect = [
                {"data": "success"},
                Exception("Step execution failed")
            ]

            # Act & Assert
            with pytest.raises(WorkflowExecutionError) as exc_info:
                await self.workflow_executor.execute_workflow(workflow_config)

            assert "Step execution failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_workflow_with_retry_logic(self):
        """Test workflow execution with retry logic for failed steps."""
        # Arrange
        workflow_steps = [
            WorkflowStep(
                id="step-1",
                name="Retryable Step",
                type="llm_call",
                config={"model": "gpt-4"},
                retry_config={"max_retries": 3, "backoff_factor": 1.5}
            )
        ]

        workflow_config = {
            "id": "retry-workflow",
            "steps": workflow_steps
        }

        with patch.object(self.workflow_executor, '_execute_step') as mock_execute_step:
            # Fail twice, then succeed
            mock_execute_step.side_effect = [
                Exception("Temporary failure"),
                Exception("Another failure"),
                {"result": "success on third try"}
            ]

            # Act
            result = await self.workflow_executor.execute_workflow(workflow_config)

            # Assert
            assert result.status == "completed"
            assert mock_execute_step.call_count == 3

    @pytest.mark.asyncio
    async def test_execute_workflow_timeout(self):
        """Test workflow execution timeout handling."""
        # Arrange
        workflow_config = {
            "id": "timeout-workflow",
            "timeout": 1.0,  # 1 second timeout
            "steps": [
                WorkflowStep(
                    id="slow-step",
                    name="Slow Step",
                    type="llm_call",
                    config={"model": "gpt-4"}
                )
            ]
        }

        async def slow_execution(*args, **kwargs):
            await asyncio.sleep(2.0)  # Longer than timeout
            return {"result": "too slow"}

        with patch.object(self.workflow_executor, '_execute_step', side_effect=slow_execution):
            # Act & Assert
            with pytest.raises(WorkflowExecutionError) as exc_info:
                await self.workflow_executor.execute_workflow(workflow_config)

            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_workflow_state_management(self):
        """Test workflow state management during execution."""
        # Arrange
        workflow_steps = [
            WorkflowStep(
                id="step-1",
                name="State Step 1",
                type="processor",
                config={}
            ),
            WorkflowStep(
                id="step-2",
                name="State Step 2",
                type="processor",
                config={}
            )
        ]

        workflow_config = {
            "id": "state-workflow",
            "steps": workflow_steps
        }

        with patch.object(self.workflow_executor, '_execute_step') as mock_execute_step:
            mock_execute_step.side_effect = [
                {"intermediate_result": "step 1 done"},
                {"final_result": "step 2 done"}
            ]

            with patch.object(self.workflow_executor, '_save_workflow_state') as mock_save_state:
                # Act
                result = await self.workflow_executor.execute_workflow(workflow_config)

                # Assert
                assert result.status == "completed"
                # State should be saved after each step
                assert mock_save_state.call_count >= 2

    @pytest.mark.asyncio
    async def test_workflow_variable_substitution(self):
        """Test variable substitution in workflow steps."""
        # Arrange
        workflow_config = {
            "id": "variable-workflow",
            "variables": {
                "model_name": "gpt-4",
                "temperature": 0.7
            },
            "steps": [
                WorkflowStep(
                    id="step-1",
                    name="Variable Step",
                    type="llm_call",
                    config={
                        "model": "${model_name}",
                        "temperature": "${temperature}"
                    }
                )
            ]
        }

        with patch.object(self.workflow_executor, '_execute_step') as mock_execute_step:
            mock_execute_step.return_value = {"result": "success"}

            # Act
            result = await self.workflow_executor.execute_workflow(workflow_config)

            # Assert
            assert result.status == "completed"
            # Check that variables were substituted in the step config
            called_step = mock_execute_step.call_args[0][0]
            assert called_step.config["model"] == "gpt-4"
            assert called_step.config["temperature"] == 0.7

    @pytest.mark.asyncio
    async def test_workflow_execution_metrics(self):
        """Test workflow execution metrics collection."""
        # Arrange
        workflow_config = {
            "id": "metrics-workflow",
            "collect_metrics": True,
            "steps": [
                WorkflowStep(
                    id="step-1",
                    name="Metrics Step",
                    type="llm_call",
                    config={"model": "gpt-4"}
                )
            ]
        }

        with patch.object(self.workflow_executor, '_execute_step') as mock_execute_step:
            mock_execute_step.return_value = {"result": "success"}

            with patch.object(self.workflow_executor, '_collect_step_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "execution_time": 1.2,
                    "memory_usage": "50MB",
                    "api_calls": 1
                }

                # Act
                result = await self.workflow_executor.execute_workflow(workflow_config)

                # Assert
                assert result.status == "completed"
                assert "metrics" in result.__dict__ or hasattr(result, 'metrics')
                mock_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_workflow_validation_before_execution(self):
        """Test workflow validation before execution."""
        # Arrange
        invalid_workflow_config = {
            "id": "invalid-workflow",
            "steps": [
                WorkflowStep(
                    id="step-1",
                    name="Invalid Step",
                    type="unknown_type",  # Invalid step type
                    config={}
                )
            ]
        }

        with patch.object(self.workflow_executor, '_validate_workflow') as mock_validate:
            mock_validate.side_effect = ValueError("Invalid step type: unknown_type")

            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                await self.workflow_executor.execute_workflow(invalid_workflow_config)

            assert "Invalid step type" in str(exc_info.value)


@pytest.mark.integration
class TestWorkflowExecutorIntegration:
    """Integration tests for workflow executor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.workflow_executor = WorkflowExecutor()

    @pytest.mark.asyncio
    async def test_end_to_end_workflow_execution(self):
        """Test complete end-to-end workflow execution."""
        # Arrange
        workflow_config = {
            "id": "integration-workflow",
            "name": "Integration Test Workflow",
            "description": "Complete workflow for integration testing",
            "steps": [
                WorkflowStep(
                    id="input",
                    name="Input Step",
                    type="input",
                    config={"source": "user_input"}
                ),
                WorkflowStep(
                    id="process",
                    name="Processing Step",
                    type="llm_call",
                    config={"model": "gpt-4", "prompt": "Process the input"}
                ),
                WorkflowStep(
                    id="output",
                    name="Output Step",
                    type="output",
                    config={"format": "json"}
                )
            ]
        }

        # Mock all step executions
        with patch.object(self.workflow_executor, '_execute_step') as mock_execute_step:
            mock_execute_step.side_effect = [
                {"input_data": "integration test input"},
                {"processed_data": "AI processed the integration test input"},
                {"formatted_output": {"result": "integration test complete"}}
            ]

            # Act
            result = await self.workflow_executor.execute_workflow(workflow_config)

            # Assert
            assert result.workflow_id == "integration-workflow"
            assert result.status == "completed"
            assert result.execution_time > 0
            assert "formatted_output" in result.outputs

    @pytest.mark.asyncio
    async def test_complex_workflow_with_all_features(self):
        """Test complex workflow using all features."""
        # Arrange
        complex_workflow = {
            "id": "complex-workflow",
            "name": "Complex Feature Test",
            "variables": {
                "primary_model": "gpt-4",
                "fallback_model": "gpt-3.5-turbo"
            },
            "timeout": 30.0,
            "collect_metrics": True,
            "steps": [
                WorkflowStep(
                    id="input",
                    name="Input Processing",
                    type="input",
                    config={"validation": True}
                ),
                WorkflowStep(
                    id="condition",
                    name="Route Decision",
                    type="condition",
                    config={"condition": "input.complexity > 0.5"}
                ),
                WorkflowStep(
                    id="primary-process",
                    name="Primary Processing",
                    type="llm_call",
                    config={"model": "${primary_model}"},
                    condition="condition.result == true",
                    retry_config={"max_retries": 2}
                ),
                WorkflowStep(
                    id="fallback-process",
                    name="Fallback Processing",
                    type="llm_call",
                    config={"model": "${fallback_model}"},
                    condition="condition.result == false"
                ),
                WorkflowStep(
                    id="combine",
                    name="Combine Results",
                    type="aggregator",
                    config={"method": "merge"},
                    dependencies=["primary-process", "fallback-process"]
                )
            ]
        }

        # Mock all required methods
        with patch.object(self.workflow_executor, '_execute_step') as mock_execute_step:
            mock_execute_step.side_effect = [
                {"complexity": 0.7, "data": "complex input"},
                {"result": True},  # Condition result
                {"processed": "primary processing complete"},
                {"final_result": "workflow complete"}
            ]

            with patch.object(self.workflow_executor, '_evaluate_condition') as mock_condition:
                mock_condition.side_effect = [True, False]

                with patch.object(self.workflow_executor, '_collect_step_metrics') as mock_metrics:
                    mock_metrics.return_value = {"execution_time": 0.5}

                    # Act
                    result = await self.workflow_executor.execute_workflow(complex_workflow)

                    # Assert
                    assert result.status == "completed"
                    assert result.workflow_id == "complex-workflow"
                    # Should execute input, condition, primary-process, and combine steps
                    assert mock_execute_step.call_count == 4


@pytest.mark.unit
class TestWorkflowStepTypes:
    """Test different workflow step types."""

    def setup_method(self):
        """Set up test fixtures."""
        self.workflow_executor = WorkflowExecutor()

    @pytest.mark.asyncio
    async def test_llm_call_step_execution(self):
        """Test LLM call step execution."""
        # Arrange
        llm_step = WorkflowStep(
            id="llm-step",
            name="LLM Call",
            type="llm_call",
            config={
                "model": "gpt-4",
                "prompt": "Analyze the input data",
                "temperature": 0.7,
                "max_tokens": 500
            }
        )

        expected_output = {
            "response": "Analysis complete",
            "tokens_used": 125,
            "model_used": "gpt-4"
        }

        with patch.object(self.workflow_executor, '_call_llm_service') as mock_llm:
            mock_llm.return_value = expected_output

            # Act
            result = await self.workflow_executor._execute_step(llm_step, {"input": "test data"})

            # Assert
            assert result["response"] == "Analysis complete"
            assert result["tokens_used"] == 125
            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_condition_step_execution(self):
        """Test condition step execution."""
        # Arrange
        condition_step = WorkflowStep(
            id="condition-step",
            name="Data Check",
            type="condition",
            config={
                "condition": "input.length > 100",
                "true_path": "detailed_processing",
                "false_path": "simple_processing"
            }
        )

        with patch.object(self.workflow_executor, '_evaluate_condition') as mock_condition:
            mock_condition.return_value = True

            # Act
            result = await self.workflow_executor._execute_step(
                condition_step,
                {"input": {"length": 150, "data": "test"}}
            )

            # Assert
            assert result["result"] is True
            assert result["next_path"] == "detailed_processing"

    @pytest.mark.asyncio
    async def test_aggregator_step_execution(self):
        """Test aggregator step execution."""
        # Arrange
        aggregator_step = WorkflowStep(
            id="aggregator-step",
            name="Result Combiner",
            type="aggregator",
            config={
                "method": "merge",
                "sources": ["step1", "step2"]
            }
        )

        input_data = {
            "step1": {"result": "A", "confidence": 0.9},
            "step2": {"result": "B", "confidence": 0.8}
        }

        with patch.object(self.workflow_executor, '_aggregate_results') as mock_aggregate:
            mock_aggregate.return_value = {
                "combined_result": "A+B",
                "average_confidence": 0.85
            }

            # Act
            result = await self.workflow_executor._execute_step(aggregator_step, input_data)

            # Assert
            assert result["combined_result"] == "A+B"
            assert result["average_confidence"] == 0.85
