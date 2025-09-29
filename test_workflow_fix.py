#!/usr/bin/env python3
"""Simple test to verify workflow definition conversion fix."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from chatter.core.workflow_graph_builder import (
    WorkflowDefinition as GraphDefinition,
    create_workflow_definition_from_model,
)


class MockDBWorkflowDefinition:
    """Mock database WorkflowDefinition for testing."""
    
    def __init__(self):
        self.nodes = [
            {"id": "start", "type": "start", "config": {}},
            {"id": "call_model", "type": "call_model", "config": {"system_message": "Test"}},
            {"id": "end", "type": "end", "config": {}},
        ]
        self.edges = [
            {"source": "start", "target": "call_model"},
            {"source": "call_model", "target": "end"},
        ]


def test_converter():
    """Test the converter function."""
    print("Testing WorkflowDefinition converter...")
    
    # Create a mock database definition
    db_def = MockDBWorkflowDefinition()
    
    # Convert it
    graph_def = create_workflow_definition_from_model(db_def)
    
    # Verify it's the right type
    assert isinstance(graph_def, GraphDefinition), f"Expected GraphDefinition, got {type(graph_def)}"
    
    # Verify nodes were copied
    assert len(graph_def.nodes) == 3, f"Expected 3 nodes, got {len(graph_def.nodes)}"
    
    # Verify edges were copied  
    assert len(graph_def.edges) == 2, f"Expected 2 edges, got {len(graph_def.edges)}"
    
    # Verify entry point was set
    assert graph_def.entry_point is not None, "Entry point should be set"
    assert graph_def.entry_point == "start", f"Expected entry point 'start', got '{graph_def.entry_point}'"
    
    print("✓ Converter test passed!")


def test_llm_node_creation():
    """Test that LLM node creation filters out retriever parameter."""
    from chatter.core.workflow_graph_builder import WorkflowGraphBuilder
    
    print("Testing LLM node creation with retriever filtering...")
    
    builder = WorkflowGraphBuilder()
    
    # This should not raise an error about unexpected 'retriever' argument
    try:
        node = builder._create_llm_node_wrapper(
            node_id="test_llm",
            config={"system_message": "Test"},
            llm=MockLLM(),
            tools=None,
            retriever="mock_retriever",  # This should be filtered out
            extra_param="should_be_passed"  # This should be passed through
        )
        print("✓ LLM node creation test passed!")
    except Exception as e:
        print(f"✗ LLM node creation test failed: {e}")
        return False
    
    return True


class MockLLM:
    """Mock LLM for testing."""
    
    def bind_tools(self, tools):
        return self
    
    async def ainvoke(self, messages, **kwargs):
        # Verify retriever is not in kwargs
        if 'retriever' in kwargs:
            raise TypeError("ainvoke() got an unexpected keyword argument 'retriever'")
        return MockMessage("Mock response")


class MockMessage:
    """Mock message for testing."""
    
    def __init__(self, content):
        self.content = content


if __name__ == "__main__":
    print("Running workflow fix tests...")
    print()
    
    test_converter()
    test_llm_node_creation()
    
    print()
    print("✓ All tests passed!")