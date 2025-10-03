"""Test to verify tool loop fix in workflow graph builder."""

import pytest
from unittest.mock import AsyncMock, Mock
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
        assert len(execute_tools_edges) == 2, (
            f"Expected 2 edges from execute_tools, got {len(execute_tools_edges)}"
        )

        # Both edges should have conditions
        for edge in execute_tools_edges:
            assert edge.get("condition") is not None, (
                f"Edge to {edge['target']} should have a condition"
            )

        # One edge should go to call_model with condition "tool_calls < 1"
        call_model_edge = next(
            (e for e in execute_tools_edges if e["target"] == "call_model"),
            None,
        )
        assert call_model_edge is not None, "Should have edge to call_model"
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
        assert finalize_edge is not None, "Should have edge to finalize_response"
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
            assert call_model_edge["condition"] == f"tool_calls < {max_calls}"

            finalize_edge = next(
                (
                    e
                    for e in execute_tools_edges
                    if e["target"] == "finalize_response"
                ),
                None,
            )
            assert finalize_edge["condition"] == f"tool_calls >= {max_calls}"

    @pytest.mark.asyncio
    async def test_workflow_stops_after_max_tool_calls(self):
        """Test that workflow stops calling tools after max_tool_calls is reached."""
        # Create workflow builder
        builder = WorkflowGraphBuilder()

        # Create a mock LLM that always wants to call tools
        mock_llm = Mock()
        
        # First call: LLM requests tool
        first_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "get_time",
                    "args": {},
                    "id": "call_1",
                }
            ],
        )
        
        # Second call after tool result: LLM should not be called again
        # if max_tool_calls=1
        second_response = AIMessage(
            content="The current time is 2025-10-03T12:00:00"
        )
        
        # Mock ainvoke to return these responses
        mock_llm.ainvoke = AsyncMock(side_effect=[first_response, second_response])
        mock_llm.bind_tools = Mock(return_value=mock_llm)

        # Create simple workflow with max_tool_calls=1
        definition = create_simple_workflow_definition(
            enable_tools=True,
            max_tool_calls=1,
        )

        # Build the workflow
        tools = [get_time]
        workflow = await builder.build_workflow(
            definition=definition,
            llm=mock_llm,
            tools=tools,
        )

        # Execute workflow
        from chatter.core.langgraph import LangGraphWorkflowManager
        
        manager = LangGraphWorkflowManager()
        initial_state = {
            "messages": [HumanMessage(content="what time is it")],
            "tool_call_count": 0,
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }

        result = await manager.run_workflow(
            workflow=workflow,
            initial_state=initial_state,
            thread_id="test_thread",
        )

        # Verify that tool_call_count reached 1
        assert result.get("tool_call_count") == 1, (
            f"Expected tool_call_count=1, got {result.get('tool_call_count')}"
        )

        # Verify messages contain the tool call and result
        messages = result.get("messages", [])
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
        assert len(tool_messages) >= 1, "Should have at least one tool message"

        # The final message should be from the LLM (not a tool call)
        final_message = messages[-1]
        assert isinstance(final_message, AIMessage)
        assert not getattr(final_message, "tool_calls", None), (
            "Final message should not have tool calls"
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
            edge for edge in execute_tools_edges if not edge.get("condition")
        ]
        
        assert len(unconditional_edges) == 0, (
            f"Found {len(unconditional_edges)} unconditional edges from execute_tools. "
            f"This would create an infinite loop. Edges: {unconditional_edges}"
        )
