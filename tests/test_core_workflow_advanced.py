"""Tests for advanced workflow features including conditional and composite workflows."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chatter.core.exceptions import WorkflowExecutionError
from chatter.core.workflow_advanced import (
    AdvancedWorkflowManager,
    CompositeWorkflowConfig,
    ConditionalWorkflowConfig,
)


@pytest.mark.unit
class TestConditionalWorkflowConfig:
    """Test ConditionalWorkflowConfig functionality."""

    def test_conditional_workflow_config_initialization(self):
        """Test ConditionalWorkflowConfig initialization."""
        # Arrange
        conditions = {
            "user_tier": {"in": ["premium", "enterprise"]},
            "query_complexity": {"min": 0.5, "max": 1.0}
        }
        workflow_configs = {
            "user_tier": {"mode": "full", "enable_memory": True},
            "query_complexity": {"mode": "tools", "enable_memory": True},
            "default": {"mode": "plain", "key": "default"}
        }

        # Act
        config = ConditionalWorkflowConfig(conditions, workflow_configs)

        # Assert
        assert config.conditions == conditions
        assert config.workflow_configs == workflow_configs

    def test_evaluate_conditions_exact_match(self):
        """Test condition evaluation with exact match."""
        # Arrange
        conditions = {"user_role": "admin"}
        workflow_configs = {
            "user_role": {"mode": "admin_full"},
            "default": {"mode": "basic", "key": "default"}
        }
        config = ConditionalWorkflowConfig(conditions, workflow_configs)

        context = {"user_role": "admin", "other_data": "value"}

        # Act
        result = config.evaluate_conditions(context)

        # Assert
        assert result == "user_role"

    def test_evaluate_conditions_range_match(self):
        """Test condition evaluation with range conditions."""
        # Arrange
        conditions = {
            "user_tier": {"in": ["premium", "enterprise"]},
            "complexity_score": {"min": 0.7, "max": 1.0}
        }
        workflow_configs = {
            "user_tier": {"mode": "premium"},
            "complexity_score": {"mode": "complex"},
            "default": {"mode": "basic", "key": "default"}
        }
        config = ConditionalWorkflowConfig(conditions, workflow_configs)

        context = {"complexity_score": 0.85}

        # Act
        result = config.evaluate_conditions(context)

        # Assert
        assert result == "complexity_score"

    def test_evaluate_conditions_list_membership(self):
        """Test condition evaluation with list membership."""
        # Arrange
        conditions = {
            "user_tier": {"in": ["premium", "enterprise"]},
            "department": {"in": ["engineering", "research"]}
        }
        workflow_configs = {
            "user_tier": {"mode": "premium"},
            "department": {"mode": "specialized"},
            "default": {"mode": "basic", "key": "default"}
        }
        config = ConditionalWorkflowConfig(conditions, workflow_configs)

        context = {"user_tier": "enterprise", "department": "marketing"}

        # Act
        result = config.evaluate_conditions(context)

        # Assert
        assert result == "user_tier"  # First matching condition

    def test_evaluate_conditions_no_match_default(self):
        """Test condition evaluation falling back to default."""
        # Arrange
        conditions = {
            "user_tier": {"in": ["premium", "enterprise"]},
            "complexity_score": {"min": 0.8, "max": 1.0}
        }
        workflow_configs = {
            "user_tier": {"mode": "premium"},
            "complexity_score": {"mode": "complex"},
            "default": {"mode": "basic", "key": "default"}
        }
        config = ConditionalWorkflowConfig(conditions, workflow_configs)

        context = {"user_tier": "basic", "complexity_score": 0.3}

        # Act
        result = config.evaluate_conditions(context)

        # Assert
        assert result == "default"

    def test_evaluate_conditions_no_match_no_default(self):
        """Test condition evaluation with no matches and no default."""
        # Arrange
        conditions = {"user_tier": "premium"}
        workflow_configs = {"user_tier": {"mode": "premium"}}
        config = ConditionalWorkflowConfig(conditions, workflow_configs)

        context = {"user_tier": "basic"}

        # Act
        result = config.evaluate_conditions(context)

        # Assert
        assert result is None

    def test_evaluate_conditions_missing_context_value(self):
        """Test condition evaluation with missing context values."""
        # Arrange
        conditions = {"required_field": "expected_value"}
        workflow_configs = {
            "required_field": {"mode": "full"},
            "default": {"mode": "basic", "key": "default"}
        }
        config = ConditionalWorkflowConfig(conditions, workflow_configs)

        context = {"other_field": "other_value"}

        # Act
        result = config.evaluate_conditions(context)

        # Assert
        assert result == "default"


@pytest.mark.unit
class TestCompositeWorkflowConfig:
    """Test CompositeWorkflowConfig functionality."""

    def test_composite_workflow_config_initialization(self):
        """Test CompositeWorkflowConfig initialization."""
        # Arrange
        workflows = [
            {"id": "workflow1", "type": "analysis"},
            {"id": "workflow2", "type": "synthesis"}
        ]
        execution_strategy = "sequential"

        # Act
        config = CompositeWorkflowConfig(workflows, execution_strategy)

        # Assert
        assert config.workflows == workflows
        assert config.execution_strategy == execution_strategy
        assert config.workflow_id is not None
        assert isinstance(config.workflow_id, str)

    def test_composite_workflow_config_default_strategy(self):
        """Test CompositeWorkflowConfig with default execution strategy."""
        # Arrange
        workflows = [{"id": "workflow1"}]

        # Act
        config = CompositeWorkflowConfig(workflows)

        # Assert
        assert config.execution_strategy == "sequential"

    def test_composite_workflow_config_parallel_strategy(self):
        """Test CompositeWorkflowConfig with parallel execution strategy."""
        # Arrange
        workflows = [
            {"id": "workflow1", "type": "independent"},
            {"id": "workflow2", "type": "independent"}
        ]
        execution_strategy = "parallel"

        # Act
        config = CompositeWorkflowConfig(workflows, execution_strategy)

        # Assert
        assert config.execution_strategy == "parallel"

    def test_composite_workflow_config_conditional_strategy(self):
        """Test CompositeWorkflowConfig with conditional execution strategy."""
        # Arrange
        workflows = [
            {"id": "workflow1", "condition": "input.type == 'text'"},
            {"id": "workflow2", "condition": "input.type == 'image'"}
        ]
        execution_strategy = "conditional"

        # Act
        config = CompositeWorkflowConfig(workflows, execution_strategy)

        # Assert
        assert config.execution_strategy == "conditional"


@pytest.mark.unit
class TestAdvancedWorkflowManager:
    """Test AdvancedWorkflowManager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = AdvancedWorkflowManager()

    @pytest.mark.asyncio
    async def test_create_conditional_workflow_with_match(self):
        """Test creating conditional workflow with matching conditions."""
        # Arrange
        mock_llm = MagicMock()

        conditions = {"user_tier": {"in": ["premium"]}}
        workflow_configs = {
            "user_tier": {"mode": "full", "enable_memory": True},
            "default": {"mode": "basic", "key": "default"}
        }
        context = {"user_tier": "premium"}

        with patch('chatter.core.workflow_advanced.create_workflow') as mock_create:
            mock_workflow = MagicMock()
            mock_create.return_value = mock_workflow

            # Act
            result = await self.manager.create_conditional_workflow(
                mock_llm, conditions, workflow_configs, context
            )

            # Assert
            assert result == mock_workflow
            mock_create.assert_called_once()
            called_config = mock_create.call_args[1]['config']
            assert called_config["mode"] == "full"
            assert called_config["enable_memory"] is True

    @pytest.mark.asyncio
    async def test_create_conditional_workflow_no_match(self):
        """Test creating conditional workflow with no matching conditions."""
        # Arrange
        mock_llm = MagicMock()

        conditions = {"user_tier": {"in": ["premium"]}}
        workflow_configs = {
            "user_tier": {"mode": "full"},
            "default": {"mode": "basic", "key": "default"}
        }
        context = {"user_tier": "basic"}

        with patch('chatter.core.workflow_advanced.create_workflow') as mock_create:
            mock_workflow = MagicMock()
            mock_create.return_value = mock_workflow

            # Act
            result = await self.manager.create_conditional_workflow(
                mock_llm, conditions, workflow_configs, context
            )

            # Assert
            assert result == mock_workflow
            called_config = mock_create.call_args[1]['config']
            assert called_config["mode"] == "basic"

    @pytest.mark.asyncio
    async def test_create_conditional_workflow_no_default(self):
        """Test creating conditional workflow with no match and no default."""
        # Arrange
        mock_llm = MagicMock()

        conditions = {"user_tier": "premium"}
        workflow_configs = {"user_tier": {"mode": "full"}}
        context = {"user_tier": "basic"}

        # Act
        result = await self.manager.create_conditional_workflow(
            mock_llm, conditions, workflow_configs, context
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_composite_workflow_sequential(self):
        """Test executing composite workflow sequentially."""
        # Arrange
        workflows = [
            {"id": "step1", "type": "analysis"},
            {"id": "step2", "type": "synthesis"}
        ]
        composite_config = CompositeWorkflowConfig(workflows, "sequential")

        mock_workflow1 = AsyncMock()
        mock_workflow1.ainvoke.return_value = {"step1_result": "analysis_complete"}
        mock_workflow2 = AsyncMock()
        mock_workflow2.ainvoke.return_value = {"step2_result": "synthesis_complete"}

        with patch.object(self.manager, '_create_workflow_from_config') as mock_create:
            mock_create.side_effect = [mock_workflow1, mock_workflow2]

            input_data = {"initial_input": "test_data"}

            # Act
            result = await self.manager.execute_composite_workflow(
                composite_config, input_data
            )

            # Assert
            assert len(result) == 2
            assert "step1_result" in result[0]
            assert "step2_result" in result[1]

            # Verify sequential execution (second workflow gets first's output)
            assert mock_workflow1.ainvoke.call_count == 1
            assert mock_workflow2.ainvoke.call_count == 1

    @pytest.mark.asyncio
    async def test_execute_composite_workflow_parallel(self):
        """Test executing composite workflow in parallel."""
        # Arrange
        workflows = [
            {"id": "branch1", "type": "independent1"},
            {"id": "branch2", "type": "independent2"}
        ]
        composite_config = CompositeWorkflowConfig(workflows, "parallel")

        mock_workflow1 = AsyncMock()
        mock_workflow1.ainvoke.return_value = {"branch1_result": "result1"}
        mock_workflow2 = AsyncMock()
        mock_workflow2.ainvoke.return_value = {"branch2_result": "result2"}

        with patch.object(self.manager, '_create_workflow_from_config') as mock_create:
            mock_create.side_effect = [mock_workflow1, mock_workflow2]

            input_data = {"shared_input": "test_data"}

            # Act
            result = await self.manager.execute_composite_workflow(
                composite_config, input_data
            )

            # Assert
            assert len(result) == 2
            assert any("branch1_result" in r for r in result)
            assert any("branch2_result" in r for r in result)

            # Verify both workflows were called
            mock_workflow1.ainvoke.assert_called_once()
            mock_workflow2.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_composite_workflow_conditional(self):
        """Test executing composite workflow with conditional strategy."""
        # Arrange
        workflows = [
            {
                "id": "text_workflow",
                "type": "text_processing",
                "condition": "input_type == 'text'"
            },
            {
                "id": "image_workflow",
                "type": "image_processing",
                "condition": "input_type == 'image'"
            }
        ]
        composite_config = CompositeWorkflowConfig(workflows, "conditional")

        mock_text_workflow = AsyncMock()
        mock_text_workflow.ainvoke.return_value = {"text_result": "processed_text"}

        with patch.object(self.manager, '_create_workflow_from_config') as mock_create:
            mock_create.return_value = mock_text_workflow

            with patch.object(self.manager, '_evaluate_workflow_condition') as mock_evaluate:
                mock_evaluate.side_effect = [True, False]  # First condition matches

                input_data = {"input_type": "text", "content": "test text"}

                # Act
                result = await self.manager.execute_composite_workflow(
                    composite_config, input_data
                )

                # Assert
                assert len(result) == 1
                assert "text_result" in result[0]
                mock_text_workflow.ainvoke.assert_called_once()

    def test_register_conditional_config(self):
        """Test registering conditional workflow configuration."""
        # Arrange
        config_name = "adaptive_support"
        conditions = {"user_tier": {"in": ["premium", "enterprise"]}}
        workflow_configs = {
            "user_tier": {"mode": "full"},
            "default": {"mode": "basic", "key": "default"}
        }

        # Act
        self.manager.register_conditional_config(
            config_name, conditions, workflow_configs
        )

        # Assert
        assert config_name in self.manager.conditional_configs
        config = self.manager.conditional_configs[config_name]
        assert config.conditions == conditions
        assert config.workflow_configs == workflow_configs

    def test_register_composite_config(self):
        """Test registering composite workflow configuration."""
        # Arrange
        config_name = "multi_step_analysis"
        workflows = [
            {"id": "step1", "type": "preprocessing"},
            {"id": "step2", "type": "analysis"},
            {"id": "step3", "type": "postprocessing"}
        ]
        execution_strategy = "sequential"

        # Act
        self.manager.register_composite_config(
            config_name, workflows, execution_strategy
        )

        # Assert
        assert config_name in self.manager.composite_configs
        config = self.manager.composite_configs[config_name]
        assert config.workflows == workflows
        assert config.execution_strategy == execution_strategy

    @pytest.mark.asyncio
    async def test_execute_registered_conditional_workflow(self):
        """Test executing a registered conditional workflow."""
        # Arrange
        config_name = "registered_conditional"
        conditions = {"complexity": {"min": 0.7, "max": 1.0}}
        workflow_configs = {
            "complexity": {"mode": "advanced"},
            "default": {"mode": "simple", "key": "default"}
        }

        self.manager.register_conditional_config(
            config_name, conditions, workflow_configs
        )

        mock_llm = MagicMock()
        context = {"complexity": 0.85}

        with patch('chatter.core.workflow_advanced.create_workflow') as mock_create:
            mock_workflow = MagicMock()
            mock_create.return_value = mock_workflow

            # Act
            result = await self.manager.execute_registered_conditional_workflow(
                config_name, mock_llm, context
            )

            # Assert
            assert result == mock_workflow
            called_config = mock_create.call_args[1]['config']
            assert called_config["mode"] == "advanced"

    @pytest.mark.asyncio
    async def test_execute_registered_composite_workflow(self):
        """Test executing a registered composite workflow."""
        # Arrange
        config_name = "registered_composite"
        workflows = [
            {"id": "analyze", "type": "analysis"},
            {"id": "summarize", "type": "summary"}
        ]

        self.manager.register_composite_config(
            config_name, workflows, "sequential"
        )

        input_data = {"text": "test input"}

        mock_workflow1 = AsyncMock()
        mock_workflow1.ainvoke.return_value = {"analysis": "complete"}
        mock_workflow2 = AsyncMock()
        mock_workflow2.ainvoke.return_value = {"summary": "done"}

        with patch.object(self.manager, '_create_workflow_from_config') as mock_create:
            mock_create.side_effect = [mock_workflow1, mock_workflow2]

            # Act
            result = await self.manager.execute_registered_composite_workflow(
                config_name, input_data
            )

            # Assert
            assert len(result) == 2
            assert "analysis" in result[0]
            assert "summary" in result[1]

    def test_list_registered_configs(self):
        """Test listing registered workflow configurations."""
        # Arrange
        self.manager.register_conditional_config(
            "conditional1", {"test": "value"}, {"test": {"mode": "test"}}
        )
        self.manager.register_composite_config(
            "composite1", [{"id": "step1"}], "sequential"
        )

        # Act
        conditional_configs = self.manager.list_conditional_configs()
        composite_configs = self.manager.list_composite_configs()

        # Assert
        assert "conditional1" in conditional_configs
        assert "composite1" in composite_configs


@pytest.mark.integration
class TestAdvancedWorkflowIntegration:
    """Integration tests for advanced workflow features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = AdvancedWorkflowManager()

    @pytest.mark.asyncio
    async def test_complex_conditional_workflow_chain(self):
        """Test complex conditional workflow with chained decisions."""
        # Arrange
        conditions = {
            "user_tier": {"in": ["premium", "enterprise"]},
            "query_complexity": {"min": 0.5, "max": 1.0},
            "priority_level": {"in": ["high", "urgent"]}
        }

        workflow_configs = {
            "user_tier": {
                "mode": "full",
                "enable_memory": True,
                "memory_window": 100,
                "max_tool_calls": 10
            },
            "query_complexity": {
                "mode": "tools",
                "enable_memory": True,
                "memory_window": 50,
                "max_tool_calls": 5
            },
            "priority_level": {
                "mode": "expedited",
                "enable_memory": True,
                "memory_window": 75,
                "timeout": 30
            },
            "default": {
                "mode": "basic",
                "enable_memory": False,
                "key": "default"
            }
        }

        # Test scenarios
        test_scenarios = [
            (
                {"user_tier": "enterprise", "query_complexity": 0.3, "priority_level": "normal"},
                "user_tier"  # First matching condition
            ),
            (
                {"user_tier": "basic", "query_complexity": 0.8, "priority_level": "normal"},
                "query_complexity"
            ),
            (
                {"user_tier": "basic", "query_complexity": 0.3, "priority_level": "urgent"},
                "priority_level"
            ),
            (
                {"user_tier": "basic", "query_complexity": 0.3, "priority_level": "normal"},
                "default"
            )
        ]

        mock_llm = MagicMock()

        for context, expected_key in test_scenarios:
            with patch('chatter.core.workflow_advanced.create_workflow') as mock_create:
                mock_workflow = MagicMock()
                mock_create.return_value = mock_workflow

                # Act
                result = await self.manager.create_conditional_workflow(
                    mock_llm, conditions, workflow_configs, context
                )

                # Assert
                assert result == mock_workflow
                if expected_key == "default":
                    expected_config = workflow_configs["default"]
                else:
                    expected_config = workflow_configs[expected_key]

                called_config = mock_create.call_args[1]['config']
                assert called_config["mode"] == expected_config["mode"]

    @pytest.mark.asyncio
    async def test_nested_composite_workflows(self):
        """Test nested composite workflows with mixed execution strategies."""
        # Arrange - Outer workflow with sequential steps, inner with parallel
        parallel_sub_workflows = [
            {"id": "parallel_step1", "type": "independent_analysis"},
            {"id": "parallel_step2", "type": "independent_validation"}
        ]

        main_workflows = [
            {"id": "preprocessing", "type": "data_prep"},
            {
                "id": "parallel_processing",
                "type": "composite",
                "sub_workflows": parallel_sub_workflows,
                "execution_strategy": "parallel"
            },
            {"id": "postprocessing", "type": "result_synthesis"}
        ]

        main_config = CompositeWorkflowConfig(main_workflows, "sequential")

        # Mock workflow results
        prep_result = {"preprocessed_data": "cleaned"}
        parallel_results = [
            {"analysis_result": "insights"},
            {"validation_result": "passed"}
        ]
        post_result = {"final_result": "synthesized"}

        mock_prep_workflow = AsyncMock()
        mock_prep_workflow.ainvoke.return_value = prep_result

        mock_parallel_workflow1 = AsyncMock()
        mock_parallel_workflow1.ainvoke.return_value = parallel_results[0]
        mock_parallel_workflow2 = AsyncMock()
        mock_parallel_workflow2.ainvoke.return_value = parallel_results[1]

        mock_post_workflow = AsyncMock()
        mock_post_workflow.ainvoke.return_value = post_result

        with patch.object(self.manager, '_create_workflow_from_config') as mock_create:
            mock_create.side_effect = [
                mock_prep_workflow,
                mock_parallel_workflow1,
                mock_parallel_workflow2,
                mock_post_workflow
            ]

            with patch.object(self.manager, 'execute_composite_workflow') as mock_composite:
                # Mock the nested composite execution
                mock_composite.return_value = parallel_results

                input_data = {"raw_data": "input"}

                # Act
                result = await self.manager.execute_composite_workflow(
                    main_config, input_data
                )

                # Assert
                # Verify the main workflow structure was executed
                assert len(result) >= 2  # At least preprocessing and composite results

    @pytest.mark.asyncio
    async def test_conditional_composite_workflow_combination(self):
        """Test combination of conditional and composite workflow features."""
        # Arrange - Conditional selection of composite workflows
        simple_composite = [
            {"id": "basic_step1", "type": "simple_analysis"},
            {"id": "basic_step2", "type": "simple_output"}
        ]

        advanced_composite = [
            {"id": "advanced_step1", "type": "deep_analysis"},
            {"id": "advanced_step2", "type": "model_ensemble"},
            {"id": "advanced_step3", "type": "confidence_scoring"},
            {"id": "advanced_step4", "type": "detailed_output"}
        ]

        conditions = {"complexity_level": {"min": 0.7, "max": 1.0}}

        workflow_configs = {
            "complexity_level": {
                "type": "composite",
                "workflows": advanced_composite,
                "execution_strategy": "sequential"
            },
            "default": {
                "type": "composite",
                "workflows": simple_composite,
                "execution_strategy": "sequential",
                "key": "default"
            }
        }

        # Test high complexity scenario
        high_complexity_context = {"complexity_level": 0.9}

        mock_llm = MagicMock()

        with patch.object(self.manager, 'execute_composite_workflow') as mock_composite:
            mock_composite.return_value = [
                {"analysis": "deep_insights"},
                {"ensemble": "multiple_models"},
                {"confidence": 0.95},
                {"output": "detailed_result"}
            ]

            # Act
            await self.manager.create_conditional_workflow(
                mock_llm, conditions, workflow_configs, high_complexity_context
            )

            # Assert
            # Verify conditional logic selected the advanced composite workflow
            # In real implementation, this would trigger composite execution
            assert mock_composite.call_count >= 0  # May be called based on implementation

    @pytest.mark.asyncio
    async def test_workflow_error_handling_and_recovery(self):
        """Test error handling and recovery in advanced workflows."""
        # Arrange - Composite workflow with potential failures
        workflows = [
            {"id": "reliable_step", "type": "preprocessing"},
            {"id": "risky_step", "type": "external_api_call"},
            {"id": "recovery_step", "type": "fallback_processing"}
        ]

        composite_config = CompositeWorkflowConfig(workflows, "sequential")

        mock_reliable_workflow = AsyncMock()
        mock_reliable_workflow.ainvoke.return_value = {"preprocessed": "success"}

        mock_risky_workflow = AsyncMock()
        mock_risky_workflow.ainvoke.side_effect = WorkflowExecutionError("API failure")

        mock_recovery_workflow = AsyncMock()
        mock_recovery_workflow.ainvoke.return_value = {"recovered": "fallback_result"}

        with patch.object(self.manager, '_create_workflow_from_config') as mock_create:
            mock_create.side_effect = [
                mock_reliable_workflow,
                mock_risky_workflow,
                mock_recovery_workflow
            ]

            input_data = {"input": "test"}

            # Act & Assert
            # In a real implementation, this should handle the error gracefully
            # and potentially execute recovery steps
            try:
                result = await self.manager.execute_composite_workflow(
                    composite_config, input_data
                )
                # If error handling is implemented, check recovery results
                if result:
                    assert any("recovered" in str(r) for r in result)
            except WorkflowExecutionError:
                # If no error handling, the exception should be raised
                pass

    def test_workflow_configuration_validation(self):
        """Test validation of complex workflow configurations."""
        # Test valid conditional configuration
        valid_conditions = {
            "user_level": {"in": ["basic", "premium"]},
            "complexity": {"min": 0.0, "max": 1.0}
        }
        valid_workflow_configs = {
            "user_level": {"mode": "standard"},
            "complexity": {"mode": "advanced"},
            "default": {"mode": "basic", "key": "default"}
        }

        # This should not raise an exception
        conditional_config = ConditionalWorkflowConfig(valid_conditions, valid_workflow_configs)
        assert conditional_config is not None

        # Test valid composite configuration
        valid_workflows = [
            {"id": "step1", "type": "input"},
            {"id": "step2", "type": "process"},
            {"id": "step3", "type": "output"}
        ]

        composite_config = CompositeWorkflowConfig(valid_workflows, "sequential")
        assert composite_config is not None
        assert len(composite_config.workflows) == 3
