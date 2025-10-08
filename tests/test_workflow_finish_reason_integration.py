"""Integration test to verify workflow properly stops on finish_reason='stop'."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from unittest.mock import AsyncMock, Mock

from chatter.core.workflow_graph_builder import (
    WorkflowGraphBuilder,
    create_simple_workflow_definition,
)
from chatter.core.workflow_node_factory import WorkflowNodeContext


class TestWorkflowFinishReasonIntegration:
    """Integration tests for workflow routing with finish_reason."""

    def setup_method(self):
        """Set up test fixtures."""
        self.builder = WorkflowGraphBuilder()

    def test_workflow_stops_when_llm_returns_finish_reason_stop(self):
        """Test that workflow goes to END when LLM returns finish_reason='stop'."""
        # Create a simple workflow with tools enabled
        definition = create_simple_workflow_definition(
            enable_tools=True,
            max_tool_calls=5,
        )

        # Build the workflow
        builder = WorkflowGraphBuilder()

        # Simulate state after LLM call with finish_reason='stop'
        state: WorkflowNodeContext = {
            "messages": [
                HumanMessage(content="What's the weather?"),
                AIMessage(
                    content="Here is the weather information you requested.",
                    tool_calls=[],  # No tool calls
                    response_metadata={"finish_reason": "stop"},
                ),
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

        # Find the edges from call_model
        call_model_edges = [
            edge
            for edge in definition.edges
            if edge["source"] == "call_model"
        ]

        # Test that has_tool_calls conditions are False
        execute_tools_edge = next(
            (e for e in call_model_edges if e["target"] == "execute_tools"),
            None,
        )
        assert execute_tools_edge is not None
        result1 = builder._evaluate_routing_condition(
            execute_tools_edge["condition"], state
        )
        assert result1 is False, "Should not route to execute_tools when finish_reason='stop'"

        # Test that no_tool_calls condition is True (routes to END)
        end_edge = next(
            (e for e in call_model_edges if e["target"] == "__end__"),
            None,
        )
        assert end_edge is not None
        result2 = builder._evaluate_routing_condition(
            end_edge["condition"], state
        )
        assert result2 is True, "Should route to END when finish_reason='stop'"

    def test_workflow_continues_when_llm_requests_tools(self):
        """Test that workflow goes to execute_tools when LLM requests tools."""
        # Create a simple workflow with tools enabled
        definition = create_simple_workflow_definition(
            enable_tools=True,
            max_tool_calls=5,
        )

        builder = WorkflowGraphBuilder()

        # Simulate state after LLM call requesting tools
        state: WorkflowNodeContext = {
            "messages": [
                HumanMessage(content="What's the weather in NYC?"),
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
                ),
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

        # Find the edges from call_model
        call_model_edges = [
            edge
            for edge in definition.edges
            if edge["source"] == "call_model"
        ]

        # Evaluate conditions to find which edge should be taken
        for edge in call_model_edges:
            condition = edge.get("condition")
            if condition:
                result = builder._evaluate_routing_condition(
                    condition, state
                )
                if result and edge["target"] == "execute_tools":
                    # This is the correct edge - workflow should execute tools
                    assert True
                    return

        # If we get here, no edge was taken to execute_tools, which is wrong
        assert (
            False
        ), "Workflow should have routed to execute_tools when LLM requests tools"

    def test_workflow_finalizes_when_tool_limit_reached_with_finish_reason_stop(
        self,
    ):
        """Test that workflow goes to END even when tool limit is reached if finish_reason='stop'."""
        # Create a simple workflow with tools enabled and low limit
        definition = create_simple_workflow_definition(
            enable_tools=True,
            max_tool_calls=1,
        )

        builder = WorkflowGraphBuilder()

        # Simulate state after reaching tool limit but LLM says stop
        state: WorkflowNodeContext = {
            "messages": [
                HumanMessage(content="What's the weather?"),
                AIMessage(
                    content="I've checked the weather for you.",
                    tool_calls=[],  # No more tool calls
                    response_metadata={"finish_reason": "stop"},
                ),
            ],
            "user_id": "test-user",
            "conversation_id": "test-conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 1,  # Already at limit
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
            "usage_metadata": {},
        }

        # Find the edges from call_model
        call_model_edges = [
            edge
            for edge in definition.edges
            if edge["source"] == "call_model"
        ]

        # Test that has_tool_calls conditions are False (because finish_reason='stop')
        execute_tools_edge = next(
            (e for e in call_model_edges if e["target"] == "execute_tools"),
            None,
        )
        assert execute_tools_edge is not None
        result1 = builder._evaluate_routing_condition(
            execute_tools_edge["condition"], state
        )
        assert result1 is False, "Should not route to execute_tools when finish_reason='stop'"

        finalize_edge = next(
            (e for e in call_model_edges if e["target"] == "finalize_response"),
            None,
        )
        assert finalize_edge is not None
        result2 = builder._evaluate_routing_condition(
            finalize_edge["condition"], state
        )
        assert result2 is False, "Should not route to finalize_response when finish_reason='stop'"

        # Test that no_tool_calls condition is True (routes to END)
        end_edge = next(
            (e for e in call_model_edges if e["target"] == "__end__"),
            None,
        )
        assert end_edge is not None
        result3 = builder._evaluate_routing_condition(
            end_edge["condition"], state
        )
        assert result3 is True, "Should route to END when finish_reason='stop'"

    def test_compound_condition_with_finish_reason(self):
        """Test that compound conditions work correctly with finish_reason."""
        builder = WorkflowGraphBuilder()

        # Test: has_tool_calls AND tool_calls < 5
        # Should be False when finish_reason='stop' even if tool_calls exist
        state: WorkflowNodeContext = {
            "messages": [
                AIMessage(
                    content="Done",
                    tool_calls=[
                        {
                            "name": "some_tool",
                            "args": {},
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

        # Evaluate: has_tool_calls AND tool_calls < 5
        result = builder._evaluate_routing_condition(
            "has_tool_calls AND tool_calls < 5", state
        )

        # Should be False because finish_reason='stop' overrides has_tool_calls
        assert result is False

    def test_no_tool_calls_with_or_logic(self):
        """Test that no_tool_calls correctly uses OR logic with finish_reason."""
        builder = WorkflowGraphBuilder()

        # Case 1: No tool calls but no finish_reason - should be True
        state1: WorkflowNodeContext = {
            "messages": [
                AIMessage(content="Done", tool_calls=[])
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
        result1 = builder._evaluate_single_condition("no_tool_calls", state1)
        assert result1 is True

        # Case 2: Has tool calls but finish_reason='stop' - should be True
        state2: WorkflowNodeContext = {
            "messages": [
                AIMessage(
                    content="Done",
                    tool_calls=[
                        {"name": "tool", "args": {}, "id": "call_1"}
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
        result2 = builder._evaluate_single_condition("no_tool_calls", state2)
        assert result2 is True

        # Case 3: Has tool calls and finish_reason='tool_calls' - should be False
        state3: WorkflowNodeContext = {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {"name": "tool", "args": {}, "id": "call_1"}
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
        result3 = builder._evaluate_single_condition("no_tool_calls", state3)
        assert result3 is False
