"""Test for workflow conditional evaluation with variable max_tool_calls.

This test verifies that conditions like "tool_calls < variable max_tool_calls"
work correctly after the fix.
"""

from chatter.core.workflow_graph_builder import WorkflowGraphBuilder
from chatter.core.workflow_node_factory import (
    ConditionalNode,
    WorkflowNodeContext,
)


class TestVariableMaxToolCallsConditions:
    """Test conditional evaluation with variable max_tool_calls references."""

    def test_tool_calls_less_than_variable_max_tool_calls(self):
        """Test that 'tool_calls < variable max_tool_calls' works correctly."""
        builder = WorkflowGraphBuilder()

        # State where tool_call_count is 3 and max_tool_calls is 10
        state: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 3,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": True,
                    "enable_memory": False,
                    "max_tool_calls": 10,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        # Test condition: tool_calls < variable max_tool_calls
        condition = "tool_calls < variable max_tool_calls"
        result = builder._evaluate_routing_condition(condition, state)
        assert (
            result is True
        ), "Should return True when tool_call_count (3) < max_tool_calls (10)"

    def test_tool_calls_greater_than_or_equal_variable_max_tool_calls(
        self,
    ):
        """Test that 'tool_calls >= variable max_tool_calls' works correctly."""
        builder = WorkflowGraphBuilder()

        # State where tool_call_count is 10 and max_tool_calls is 10
        state: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 10,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": True,
                    "enable_memory": False,
                    "max_tool_calls": 10,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        # Test condition: tool_calls >= variable max_tool_calls
        condition = "tool_calls >= variable max_tool_calls"
        result = builder._evaluate_routing_condition(condition, state)
        assert (
            result is True
        ), "Should return True when tool_call_count (10) >= max_tool_calls (10)"

    def test_tool_calls_greater_than_variable_max_tool_calls(self):
        """Test that 'tool_calls > variable max_tool_calls' works correctly."""
        builder = WorkflowGraphBuilder()

        # State where tool_call_count is 12 and max_tool_calls is 10
        state: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 12,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": True,
                    "enable_memory": False,
                    "max_tool_calls": 10,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        # Test condition: tool_calls > variable max_tool_calls
        condition = "tool_calls > variable max_tool_calls"
        result = builder._evaluate_routing_condition(condition, state)
        assert (
            result is True
        ), "Should return True when tool_call_count (12) > max_tool_calls (10)"

    def test_tool_calls_less_than_or_equal_variable_max_tool_calls(self):
        """Test that 'tool_calls <= variable max_tool_calls' works correctly."""
        builder = WorkflowGraphBuilder()

        # State where tool_call_count is 8 and max_tool_calls is 10
        state: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 8,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": True,
                    "enable_memory": False,
                    "max_tool_calls": 10,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        # Test condition: tool_calls <= variable max_tool_calls
        condition = "tool_calls <= variable max_tool_calls"
        result = builder._evaluate_routing_condition(condition, state)
        assert (
            result is True
        ), "Should return True when tool_call_count (8) <= max_tool_calls (10)"

    async def test_conditional_node_with_variable_max_tool_calls(self):
        """Test ConditionalNode with variable max_tool_calls condition."""
        # Create conditional node
        node = ConditionalNode(
            "test_conditional",
            {"condition": "tool_calls < variable max_tool_calls"},
        )

        # State where tool_call_count is 5 and max_tool_calls is 10
        context: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 5,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": True,
                    "enable_memory": False,
                    "max_tool_calls": 10,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        # Execute the node
        result = await node.execute(context)

        # Check that the condition was evaluated correctly
        assert (
            "conditional_results" in result
        ), "Should return conditional_results"
        assert (
            result["conditional_results"]["test_conditional"] is True
        ), "Should evaluate to True when tool_call_count (5) < max_tool_calls (10)"

    async def test_conditional_node_with_variable_max_tool_calls_false(
        self,
    ):
        """Test ConditionalNode returns False when threshold is exceeded."""
        # Create conditional node
        node = ConditionalNode(
            "test_conditional",
            {"condition": "tool_calls < variable max_tool_calls"},
        )

        # State where tool_call_count is 12 and max_tool_calls is 10
        context: WorkflowNodeContext = {
            "messages": [],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 12,
            "metadata": {},
            "variables": {
                "capabilities": {
                    "enable_retrieval": False,
                    "enable_tools": True,
                    "enable_memory": False,
                    "max_tool_calls": 10,
                }
            },
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        # Execute the node
        result = await node.execute(context)

        # Check that the condition was evaluated correctly
        assert (
            "conditional_results" in result
        ), "Should return conditional_results"
        assert (
            result["conditional_results"]["test_conditional"] is False
        ), "Should evaluate to False when tool_call_count (12) >= max_tool_calls (10)"
