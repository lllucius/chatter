"""Integration test for loop node routing in a complete workflow."""

import pytest

from chatter.core.workflow_graph_builder import (
    WorkflowDefinition,
    WorkflowGraphBuilder,
)
from chatter.core.workflow_node_factory import (
    LoopNode,
    WorkflowNodeContext,
)


class TestLoopWorkflowIntegration:
    """Test complete loop workflow scenarios."""

    @pytest.mark.asyncio
    async def test_loop_workflow_with_max_iterations(self):
        """Test that a loop workflow correctly tracks iterations and routing."""
        # Create a simple loop workflow:
        # start -> loop -> body -> loop (continue) -> body -> loop (exit) -> end
        
        definition = WorkflowDefinition()
        definition.add_node("start", "start", {})
        definition.add_node("loop1", "loop", {"max_iterations": 3})
        definition.add_node("body", "variable", {
            "operation": "increment",
            "variable_name": "counter"
        })
        definition.add_node("end", "end", {})
        
        # Edges
        definition.add_edge("start", "loop1")
        definition.add_edge("loop1", "body", "loop_loop1_continue")
        definition.add_edge("loop1", "end", "not loop_loop1_continue")
        definition.add_edge("body", "loop1")
        
        # Test that the workflow builder can handle this definition
        builder = WorkflowGraphBuilder()
        
        # Test iteration 1: should continue
        state: WorkflowNodeContext = {
            "messages": [],
            "metadata": {
                "loop_loop1_continue": True,
                "loop_loop1_iteration": 0,
            },
            "loop_state": {
                "loop1": 1,
            },
            "variables": {
                "counter": 1,
            },
        }
        
        # Should route to body (continue)
        assert builder._evaluate_routing_condition(
            "loop_loop1_continue", state
        ) is True
        assert builder._evaluate_routing_condition(
            "not loop_loop1_continue", state
        ) is False
        
        # Test iteration 2: should continue
        state["metadata"]["loop_loop1_iteration"] = 1
        state["loop_state"]["loop1"] = 2
        state["metadata"]["loop_loop1_continue"] = True
        
        assert builder._evaluate_routing_condition(
            "loop_loop1_continue", state
        ) is True
        
        # Test iteration 3: should exit (reached max)
        state["metadata"]["loop_loop1_iteration"] = 2
        state["loop_state"]["loop1"] = 3
        state["metadata"]["loop_loop1_continue"] = False
        
        # Should route to end (exit)
        assert builder._evaluate_routing_condition(
            "loop_loop1_continue", state
        ) is False
        assert builder._evaluate_routing_condition(
            "not loop_loop1_continue", state
        ) is True

    @pytest.mark.asyncio
    async def test_loop_node_sets_correct_metadata(self):
        """Test that LoopNode correctly sets metadata for routing."""
        loop_node = LoopNode("test_loop", {"max_iterations": 2})
        
        # First iteration
        context: WorkflowNodeContext = {
            "messages": [],
            "metadata": {},
            "loop_state": {},
        }
        
        result = await loop_node.execute(context)
        
        # Check that continue is True (first iteration)
        assert result["metadata"]["loop_test_loop_continue"] is True
        assert result["metadata"]["loop_test_loop_iteration"] == 0
        assert result["loop_state"]["test_loop"] == 1
        
        # Second iteration
        context["loop_state"] = result["loop_state"]
        result = await loop_node.execute(context)
        
        # Check that continue is still True (second iteration)
        assert result["metadata"]["loop_test_loop_continue"] is True
        assert result["metadata"]["loop_test_loop_iteration"] == 1
        assert result["loop_state"]["test_loop"] == 2
        
        # Third iteration (should exit)
        context["loop_state"] = result["loop_state"]
        result = await loop_node.execute(context)
        
        # Check that continue is False (max iterations reached)
        assert result["metadata"]["loop_test_loop_continue"] is False
        assert result["metadata"]["loop_test_loop_iteration"] == 2
        # Loop state should NOT increment when should_continue is False
        assert result["loop_state"]["test_loop"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
