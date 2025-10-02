"""Test for workflow conditional evaluation fix.

This test verifies that conditions like "variable enable_retrieval equals false"
work correctly after the fix to _evaluate_single_condition.
"""

from chatter.core.workflow_graph_builder import WorkflowGraphBuilder
from chatter.core.workflow_node_factory import WorkflowNodeContext


class TestConditionalEvaluationFix:
    """Test conditional evaluation with true/false values."""

    def test_enable_retrieval_equals_false(self):
        """Test that 'variable enable_retrieval equals false' works correctly."""
        builder = WorkflowGraphBuilder()

        # State where enable_retrieval is False
        state: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": False,
                    "enable_memory": False,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        # Test condition: variable enable_retrieval equals false
        condition = "variable enable_retrieval equals false"
        result = builder._evaluate_routing_condition(condition, state)
        assert (
            result is True
        ), "Should return True when enable_retrieval is False and condition checks for false"

    def test_enable_retrieval_equals_true(self):
        """Test that 'variable enable_retrieval equals true' works correctly."""
        builder = WorkflowGraphBuilder()

        # State where enable_retrieval is True
        state: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": True,
                    "enable_tools": False,
                    "enable_memory": False,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        # Test condition: variable enable_retrieval equals true
        condition = "variable enable_retrieval equals true"
        result = builder._evaluate_routing_condition(condition, state)
        assert (
            result is True
        ), "Should return True when enable_retrieval is True and condition checks for true"

    def test_enable_retrieval_false_when_checking_true(self):
        """Test that 'variable enable_retrieval equals true' returns False when value is False."""
        builder = WorkflowGraphBuilder()

        # State where enable_retrieval is False
        state: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": False,
                    "enable_memory": False,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        # Test condition: variable enable_retrieval equals true
        condition = "variable enable_retrieval equals true"
        result = builder._evaluate_routing_condition(condition, state)
        assert (
            result is False
        ), "Should return False when enable_retrieval is False but condition checks for true"

    def test_enable_tools_equals_false(self):
        """Test that 'variable enable_tools equals false' works correctly."""
        builder = WorkflowGraphBuilder()

        state: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": False,
                    "enable_memory": False,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        condition = "variable enable_tools equals false"
        result = builder._evaluate_routing_condition(condition, state)
        assert (
            result is True
        ), "Should return True when enable_tools is False and condition checks for false"

    def test_enable_memory_equals_false(self):
        """Test that 'variable enable_memory equals false' works correctly."""
        builder = WorkflowGraphBuilder()

        state: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": False,
                    "enable_memory": False,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        condition = "variable enable_memory equals false"
        result = builder._evaluate_routing_condition(condition, state)
        assert (
            result is True
        ), "Should return True when enable_memory is False and condition checks for false"

    def test_compound_condition_with_false_values(self):
        """Test compound conditions with false values."""
        builder = WorkflowGraphBuilder()

        state: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": False,
                    "enable_memory": False,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        # Test: variable enable_tools equals false AND no_tool_calls
        condition = (
            "variable enable_tools equals false OR no_tool_calls"
        )
        result = builder._evaluate_routing_condition(condition, state)
        assert (
            result is True
        ), "Should return True when either part of OR condition is true"
