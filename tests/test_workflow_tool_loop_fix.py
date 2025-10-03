"""Test to verify tool loop fix in workflow graph builder."""

from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

from chatter.core.workflow_graph_builder import (
    WorkflowGraphBuilder,
    create_simple_workflow_definition,
)


@tool
def get_time() -> str:
    """Get the current date and time."""
    return "2025-10-03T12:00:00"


class TestWorkflowToolLoopFix:
    """Test that tool loop is properly constrained by max_tool_calls."""

    def test_simple_workflow_definition_has_conditional_edges(self):
        """Test that the workflow definition has conditional edges from execute_tools."""
        # Create a simple workflow definition with tools enabled and max_tool_calls=1
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

        # There should be 2 conditional edges from execute_tools
        assert (
            len(execute_tools_edges) == 2
        ), f"Expected 2 edges from execute_tools, got {len(execute_tools_edges)}"

        # Both edges should have conditions
        for edge in execute_tools_edges:
            assert (
                edge.get("condition") is not None
            ), f"Edge to {edge['target']} should have a condition"

        # One edge should go to call_model with condition "tool_calls < 1"
        call_model_edge = next(
            (
                e
                for e in execute_tools_edges
                if e["target"] == "call_model"
            ),
            None,
        )
        assert (
            call_model_edge is not None
        ), "Should have edge to call_model"
        assert call_model_edge["condition"] == "tool_calls < 1"

        # One edge should go to finalize_response with condition "tool_calls >= 1"
        finalize_edge = next(
            (
                e
                for e in execute_tools_edges
                if e["target"] == "finalize_response"
            ),
            None,
        )
        assert (
            finalize_edge is not None
        ), "Should have edge to finalize_response"
        assert finalize_edge["condition"] == "tool_calls >= 1"

    def test_workflow_definition_respects_max_tool_calls(self):
        """Test that max_tool_calls is properly encoded in the condition."""
        # Test with different max_tool_calls values
        for max_calls in [1, 3, 5, 10]:
            definition = create_simple_workflow_definition(
                enable_tools=True,
                max_tool_calls=max_calls,
            )

            # Get edges from execute_tools
            execute_tools_edges = [
                edge
                for edge in definition.edges
                if edge["source"] == "execute_tools"
            ]

            # Check that conditions use the correct max_tool_calls value
            call_model_edge = next(
                (
                    e
                    for e in execute_tools_edges
                    if e["target"] == "call_model"
                ),
                None,
            )
            assert (
                call_model_edge["condition"]
                == f"tool_calls < {max_calls}"
            )

            finalize_edge = next(
                (
                    e
                    for e in execute_tools_edges
                    if e["target"] == "finalize_response"
                ),
                None,
            )
            assert (
                finalize_edge["condition"]
                == f"tool_calls >= {max_calls}"
            )

    def test_no_unconditional_loop_from_execute_tools(self):
        """Test that there's no unconditional edge from execute_tools to call_model."""
        definition = create_simple_workflow_definition(
            enable_tools=True,
            max_tool_calls=1,
        )

        # Get edges from execute_tools
        execute_tools_edges = [
            edge
            for edge in definition.edges
            if edge["source"] == "execute_tools"
        ]

        # Check that NO edge is unconditional
        unconditional_edges = [
            edge
            for edge in execute_tools_edges
            if not edge.get("condition")
        ]

        assert len(unconditional_edges) == 0, (
            f"Found {len(unconditional_edges)} unconditional edges from execute_tools. "
            f"This would create an infinite loop. Edges: {unconditional_edges}"
        )
