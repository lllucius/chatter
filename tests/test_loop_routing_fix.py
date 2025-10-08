"""Tests for loop node routing fix in workflow graph builder."""

import pytest

from chatter.core.workflow_graph_builder import (
    WorkflowDefinition,
    WorkflowGraphBuilder,
)
from chatter.core.workflow_node_factory import WorkflowNodeContext


class TestLoopRouting:
    """Test loop node routing conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.builder = WorkflowGraphBuilder()

    def test_evaluate_loop_continue_condition_true(self):
        """Test that loop_continue condition evaluates to True when set."""
        state: WorkflowNodeContext = {
            "messages": [],
            "metadata": {
                "loop_loop1_continue": True,
            },
        }
        
        result = self.builder._evaluate_routing_condition(
            "loop_loop1_continue", state
        )
        assert result is True

    def test_evaluate_loop_continue_condition_false(self):
        """Test that loop_continue condition evaluates to False when set."""
        state: WorkflowNodeContext = {
            "messages": [],
            "metadata": {
                "loop_loop1_continue": False,
            },
        }
        
        result = self.builder._evaluate_routing_condition(
            "loop_loop1_continue", state
        )
        assert result is False

    def test_evaluate_loop_exit_condition(self):
        """Test that negated loop_continue works for exit path."""
        state: WorkflowNodeContext = {
            "messages": [],
            "metadata": {
                "loop_loop1_continue": False,
            },
        }
        
        # Exit path should be true when continue is false
        result = self.builder._evaluate_routing_condition(
            "not loop_loop1_continue", state
        )
        assert result is True

    def test_evaluate_loop_exit_condition_false(self):
        """Test that negated loop_continue is False when continue is True."""
        state: WorkflowNodeContext = {
            "messages": [],
            "metadata": {
                "loop_loop1_continue": True,
            },
        }
        
        # Exit path should be false when continue is true
        result = self.builder._evaluate_routing_condition(
            "not loop_loop1_continue", state
        )
        assert result is False

    def test_loop_continue_missing_metadata(self):
        """Test that missing loop metadata defaults to False."""
        state: WorkflowNodeContext = {
            "messages": [],
            "metadata": {},
        }
        
        result = self.builder._evaluate_routing_condition(
            "loop_loop1_continue", state
        )
        # Missing metadata should default to False
        assert result is False

    def test_multiple_loop_nodes(self):
        """Test routing with multiple loop nodes."""
        state: WorkflowNodeContext = {
            "messages": [],
            "metadata": {
                "loop_loop1_continue": True,
                "loop_loop2_continue": False,
            },
        }
        
        # First loop should continue
        assert self.builder._evaluate_routing_condition(
            "loop_loop1_continue", state
        ) is True
        
        # Second loop should not continue
        assert self.builder._evaluate_routing_condition(
            "loop_loop2_continue", state
        ) is False
        
        # Exit conditions should be inverted
        assert self.builder._evaluate_routing_condition(
            "not loop_loop1_continue", state
        ) is False
        
        assert self.builder._evaluate_routing_condition(
            "not loop_loop2_continue", state
        ) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
