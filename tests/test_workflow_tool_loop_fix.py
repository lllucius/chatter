"""Test to verify tool loop fix uses LLM state with safety limits."""

from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END

from chatter.core.workflow_graph_builder import (
    WorkflowGraphBuilder,
    create_simple_workflow_definition,
)


@tool
def get_time() -> str:
    """Get the current date and time."""
    return "2025-10-03T12:00:00"


class TestWorkflowToolLoopFix:
    """Test that tool loop properly uses LLM state with safety limits."""

    def test_workflow_routes_from_call_model_based_on_llm_state(self):
        """Test that routing decisions are made at call_model based on LLM state."""
        # Create a simple workflow definition with tools enabled and max_tool_calls=1
        definition = create_simple_workflow_definition(
            enable_tools=True,
            max_tool_calls=1,
        )

        # Get edges from call_model node (where the routing decision is made)
        call_model_edges = [
            edge
            for edge in definition.edges
            if edge["source"] == "call_model"
        ]

        # Should have 3 edges from call_model
        assert (
            len(call_model_edges) == 3
        ), f"Expected 3 edges from call_model, got {len(call_model_edges)}"

        # All edges should have conditions (routing based on LLM state and safety limit)
        for edge in call_model_edges:
            assert (
                edge.get("condition") is not None
            ), f"Edge to {edge['target']} should have a condition"

        # One edge should go to execute_tools with condition checking both tool calls and limit
        execute_tools_edge = next(
            (
                e
                for e in call_model_edges
                if e["target"] == "execute_tools"
            ),
            None,
        )
        assert (
            execute_tools_edge is not None
        ), "Should have edge to execute_tools"
        # Should check both has_tool_calls and under the limit
        condition_lower = execute_tools_edge["condition"].lower()
        assert (
            "has_tool_calls" in condition_lower
        ), "Should check if LLM requests tools"
        assert (
            "tool_calls < 1" in execute_tools_edge["condition"]
        ), "Should check safety limit"

        # One edge should go to finalize_response when LLM wants tools but hit limit
        finalize_edge = next(
            (
                e
                for e in call_model_edges
                if e["target"] == "finalize_response"
            ),
            None,
        )
        assert (
            finalize_edge is not None
        ), "Should have edge to finalize_response"
        condition_lower = finalize_edge["condition"].lower()
        assert (
            "has_tool_calls" in condition_lower
        ), "Should check if LLM requests tools"
        assert (
            "tool_calls >= 1" in finalize_edge["condition"]
        ), "Should check safety limit"

        # One edge should go to END when LLM is done (no tool calls)
        end_edge = next(
            (e for e in call_model_edges if e["target"] == END),
            None,
        )
        assert end_edge is not None, "Should have edge to END"
        assert (
            "no_tool_calls" in end_edge["condition"].lower()
        ), "Should check if LLM stopped calling tools"

    def test_execute_tools_always_returns_to_call_model(self):
        """Test that execute_tools always goes back to call_model for LLM decision."""
        definition = create_simple_workflow_definition(
            enable_tools=True,
            max_tool_calls=1,
        )

        # Get edges from execute_tools node
        execute_tools_edges = [
            edge
            for edge in definition.edges
            if edge["source"] == "execute_tools"
        ]

        # Should have exactly 1 edge going back to call_model
        assert (
            len(execute_tools_edges) == 1
        ), f"Expected 1 edge from execute_tools, got {len(execute_tools_edges)}"

        # The edge should go to call_model
        edge = execute_tools_edges[0]
        assert (
            edge["target"] == "call_model"
        ), f"Execute_tools should return to call_model, got {edge['target']}"

        # This edge can be unconditional since routing happens at call_model
        # The LLM will decide whether to continue or stop

    def test_workflow_definition_respects_max_tool_calls(self):
        """Test that max_tool_calls is properly encoded in the condition."""
        # Test with different max_tool_calls values
        for max_calls in [1, 3, 5, 10]:
            definition = create_simple_workflow_definition(
                enable_tools=True,
                max_tool_calls=max_calls,
            )

            # Get edges from call_model
            call_model_edges = [
                edge
                for edge in definition.edges
                if edge["source"] == "call_model"
            ]

            # Check that conditions use the correct max_tool_calls value
            execute_tools_edge = next(
                (
                    e
                    for e in call_model_edges
                    if e["target"] == "execute_tools"
                ),
                None,
            )
            assert (
                f"tool_calls < {max_calls}"
                in execute_tools_edge["condition"]
            ), f"Expected tool_calls < {max_calls}"

            finalize_edge = next(
                (
                    e
                    for e in call_model_edges
                    if e["target"] == "finalize_response"
                ),
                None,
            )
            assert (
                f"tool_calls >= {max_calls}"
                in finalize_edge["condition"]
            ), f"Expected tool_calls >= {max_calls}"

    def test_llm_can_naturally_stop_calling_tools(self):
        """Test that LLM can naturally stop by not returning tool_calls."""
        definition = create_simple_workflow_definition(
            enable_tools=True,
            max_tool_calls=10,  # High limit
        )

        # Get edges from call_model
        call_model_edges = [
            edge
            for edge in definition.edges
            if edge["source"] == "call_model"
        ]

        # Find the edge that handles when LLM stops calling tools
        no_tools_edge = next(
            (e for e in call_model_edges if e["target"] == END),
            None,
        )
        assert (
            no_tools_edge is not None
        ), "Should have natural stop condition"
        assert (
            "no_tool_calls" in no_tools_edge["condition"].lower()
        ), "Should detect when LLM stops requesting tools"

        # This allows LLM to naturally stop before hitting the limit
