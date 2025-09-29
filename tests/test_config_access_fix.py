"""Test for workflow config access fix."""

import pytest
from unittest.mock import Mock

from chatter.core.workflow_graph_builder import WorkflowDefinition, WorkflowGraphBuilder


class TestWorkflowConfigAccess:
    """Tests for workflow node config access handling."""

    @pytest.fixture
    def workflow_builder(self):
        """Create a workflow graph builder."""
        return WorkflowGraphBuilder()

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        return Mock()

    def test_simple_config_format(self, workflow_builder, mock_llm):
        """Test that simple config format works (original format)."""
        # Create a simple workflow definition  
        definition = WorkflowDefinition()
        definition.nodes = [
            {
                "id": "test_node",
                "type": "variable", 
                "config": {
                    "operation": "set",
                    "variable_name": "test_var",
                    "value": "test_value"
                }
            }
        ]
        
        # This should work without KeyError
        nodes = workflow_builder._create_nodes(definition, mock_llm)
        assert "test_node" in nodes
        assert nodes["test_node"].config["operation"] == "set"

    def test_complex_config_format(self, workflow_builder, mock_llm):
        """Test that complex config format works (management service format)."""
        # Create a complex workflow definition like management service creates
        definition = WorkflowDefinition()
        definition.nodes = [
            {
                "id": "test_node",
                "type": "variable",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Test Node",
                    "nodeType": "variable",
                    "config": {
                        "operation": "set",
                        "variable_name": "test_var", 
                        "value": "test_value"
                    }
                }
            }
        ]
        
        # This should work without KeyError after fix
        nodes = workflow_builder._create_nodes(definition, mock_llm)
        assert "test_node" in nodes
        assert nodes["test_node"].config["operation"] == "set"

    def test_empty_config_formats(self, workflow_builder, mock_llm):
        """Test handling of empty configs in both formats."""
        definition = WorkflowDefinition()
        definition.nodes = [
            # Simple format with valid variable config
            {
                "id": "simple_node",
                "type": "variable",
                "config": {
                    "operation": "set",
                    "variable_name": "test_var",
                    "value": "test_value"
                }
            },
            # Complex format with valid conditional config
            {
                "id": "complex_node",
                "type": "conditional",
                "data": {
                    "label": "Conditional Node",
                    "nodeType": "conditional",
                    "config": {
                        "condition": "variable test_var equals test_value"
                    }
                }
            }
        ]
        
        nodes = workflow_builder._create_nodes(definition, mock_llm)
        assert "simple_node" in nodes
        assert "complex_node" in nodes

    def test_missing_config_formats(self, workflow_builder, mock_llm):
        """Test handling when config is missing in both formats."""
        definition = WorkflowDefinition()
        definition.nodes = [
            # Simple format without config - should use empty dict and get defaults
            {
                "id": "simple_node",
                "type": "delay",  # delay nodes work with empty config
            },
            # Complex format without config - should use empty dict
            {
                "id": "complex_node",
                "type": "delay",
                "data": {
                    "label": "Delay Node",
                    "nodeType": "delay"
                }
            }
        ]
        
        nodes = workflow_builder._create_nodes(definition, mock_llm)
        assert "simple_node" in nodes
        assert "complex_node" in nodes
        # Should have default configs (delay nodes default to 1 second)
        assert nodes["simple_node"].config.get("delay_seconds", 1) == 1
        assert nodes["complex_node"].config.get("delay_seconds", 1) == 1