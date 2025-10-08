"""Test workflow routing based on finish_reason in response_metadata."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from chatter.core.workflow_graph_builder import WorkflowGraphBuilder
from chatter.core.workflow_node_factory import WorkflowNodeContext


class TestWorkflowFinishReason:
    """Test that workflow properly routes based on finish_reason."""

    def setup_method(self):
        """Set up test fixtures."""
        self.builder = WorkflowGraphBuilder()

    def test_no_tool_calls_condition_with_finish_reason_stop(self):
        """Test that no_tool_calls returns True when finish_reason='stop'."""
        # Create a state with a message that has finish_reason='stop'
        state: WorkflowNodeContext = {
            "messages": [
                AIMessage(
                    content="Here is my final answer",
                    tool_calls=[],
                    response_metadata={"finish_reason": "stop"},
                )
            ],
            "user_id": "test-user",
            "conversation_id": "test-conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
            "usage_metadata": {},
        }

        # Evaluate the no_tool_calls condition
        result = self.builder._evaluate_single_condition(
            "no_tool_calls", state
        )

        # Should return True because finish_reason='stop'
        assert result is True

    def test_no_tool_calls_condition_with_empty_tool_calls(self):
        """Test that no_tool_calls returns True when tool_calls is empty."""
        state: WorkflowNodeContext = {
            "messages": [
                AIMessage(
                    content="Here is my answer",
                    tool_calls=[],
                )
            ],
            "user_id": "test-user",
            "conversation_id": "test-conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
            "usage_metadata": {},
        }

        result = self.builder._evaluate_single_condition(
            "no_tool_calls", state
        )

        # Should return True because tool_calls is empty
        assert result is True

    def test_has_tool_calls_condition_with_finish_reason_stop(self):
        """Test that has_tool_calls returns False when finish_reason='stop'."""
        # Even if tool_calls exist, finish_reason='stop' means we should stop
        state: WorkflowNodeContext = {
            "messages": [
                AIMessage(
                    content="I'm done",
                    tool_calls=[
                        {
                            "name": "some_tool",
                            "args": {"arg": "value"},
                            "id": "call_1",
                        }
                    ],
                    response_metadata={"finish_reason": "stop"},
                )
            ],
            "user_id": "test-user",
            "conversation_id": "test-conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
            "usage_metadata": {},
        }

        result = self.builder._evaluate_single_condition(
            "has_tool_calls", state
        )

        # Should return False because finish_reason='stop' overrides tool_calls
        assert result is False

    def test_has_tool_calls_condition_with_tool_calls(self):
        """Test that has_tool_calls returns True when tool_calls exist and finish_reason is not 'stop'."""
        state: WorkflowNodeContext = {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "get_weather",
                            "args": {"location": "NYC"},
                            "id": "call_1",
                        }
                    ],
                    response_metadata={"finish_reason": "tool_calls"},
                )
            ],
            "user_id": "test-user",
            "conversation_id": "test-conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
            "usage_metadata": {},
        }

        result = self.builder._evaluate_single_condition(
            "has_tool_calls", state
        )

        # Should return True because tool_calls exist and finish_reason != 'stop'
        assert result is True

    def test_has_tool_calls_condition_with_no_response_metadata(self):
        """Test that has_tool_calls works when response_metadata is not present."""
        state: WorkflowNodeContext = {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "get_weather",
                            "args": {"location": "NYC"},
                            "id": "call_1",
                        }
                    ],
                )
            ],
            "user_id": "test-user",
            "conversation_id": "test-conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
            "usage_metadata": {},
        }

        result = self.builder._evaluate_single_condition(
            "has_tool_calls", state
        )

        # Should return True because tool_calls exist (no response_metadata to override)
        assert result is True

    def test_no_tool_calls_with_finish_reason_tool_calls(self):
        """Test that no_tool_calls returns False when finish_reason='tool_calls'."""
        state: WorkflowNodeContext = {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "get_weather",
                            "args": {"location": "NYC"},
                            "id": "call_1",
                        }
                    ],
                    response_metadata={"finish_reason": "tool_calls"},
                )
            ],
            "user_id": "test-user",
            "conversation_id": "test-conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
            "usage_metadata": {},
        }

        result = self.builder._evaluate_single_condition(
            "no_tool_calls", state
        )

        # Should return False because tool_calls exist
        assert result is False
