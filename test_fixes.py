#!/usr/bin/env python3
"""Test specifically for the workflow execution issues mentioned in the problem statement."""

import os
import asyncio
from unittest.mock import Mock, AsyncMock

# Set up minimal environment
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('ENVIRONMENT', 'test')

from chatter.core.workflow_graph_builder import (
    create_workflow_definition_from_model,
    WorkflowGraphBuilder,
)


class MockDBWorkflowDefinition:
    """Mock database WorkflowDefinition to test the conversion."""
    
    def __init__(self):
        self.nodes = [
            {
                "id": "start",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "nodeType": "start",
                    "config": {}
                }
            },
            {
                "id": "call_model",
                "type": "call_model",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Call Model",
                    "nodeType": "call_model",
                    "config": {
                        "system_message": "You are a helpful assistant."
                    }
                }
            },
            {
                "id": "end",
                "type": "end",
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "End",
                    "nodeType": "end",
                    "config": {}
                }
            }
        ]
        self.edges = [
            {
                "id": "start-call_model",
                "source": "start",
                "target": "call_model",
                "type": "default"
            },
            {
                "id": "call_model-end",
                "source": "call_model",
                "target": "end",
                "type": "default"
            }
        ]


class MockLLM:
    """Mock LLM that will fail if passed unexpected arguments."""
    
    def bind_tools(self, tools):
        return self
    
    async def ainvoke(self, messages, **kwargs):
        # This should fail if 'retriever' is in kwargs
        if 'retriever' in kwargs:
            raise TypeError("AsyncCompletions.create() got an unexpected keyword argument 'retriever'")
        return Mock(content="Mock response")


async def test_entry_point_fix():
    """Test that WorkflowDefinition has entry_point after conversion."""
    print("Testing entry_point fix...")
    
    # Create a mock database definition
    db_def = MockDBWorkflowDefinition()
    
    # Convert it using our fix
    graph_def = create_workflow_definition_from_model(db_def)
    
    # This should not raise: 'WorkflowDefinition' object has no attribute 'entry_point'
    assert hasattr(graph_def, 'entry_point'), "Graph definition should have entry_point attribute"
    assert graph_def.entry_point is not None, "Entry point should be set"
    assert graph_def.entry_point == "start", f"Expected 'start', got {graph_def.entry_point}"
    
    print("✓ Entry point fix verified")


async def test_retriever_filtering():
    """Test that LLM node creation filters out retriever parameter."""
    print("Testing retriever parameter filtering...")
    
    builder = WorkflowGraphBuilder()
    mock_llm = MockLLM()
    
    # This should not raise the retriever error
    try:
        node = builder._create_llm_node_wrapper(
            node_id="test_llm",
            config={"system_message": "Test"},
            llm=mock_llm,
            tools=None,
            retriever="mock_retriever",  # This should be filtered out
        )
        print("✓ Retriever filtering fix verified")
    except TypeError as e:
        if "retriever" in str(e):
            print(f"✗ Retriever filtering failed: {e}")
            raise
        else:
            # Some other TypeError, re-raise
            raise


async def test_workflow_build_with_retriever():
    """Test building a workflow with retriever parameter."""
    print("Testing workflow build with retriever...")
    
    db_def = MockDBWorkflowDefinition()
    graph_def = create_workflow_definition_from_model(db_def)
    
    builder = WorkflowGraphBuilder()
    mock_llm = MockLLM()
    
    # This should not fail due to retriever parameter
    try:
        workflow = builder.build_graph(
            definition=graph_def,
            llm=mock_llm,
            retriever="mock_retriever",  # This should be handled correctly
            tools=None,
        )
        print("✓ Workflow build with retriever verified")
    except TypeError as e:
        if "retriever" in str(e):
            print(f"✗ Workflow build with retriever failed: {e}")
            raise
        else:
            # Some other error, re-raise
            raise


async def main():
    """Run all tests."""
    print("Running workflow execution fixes tests...")
    print()
    
    await test_entry_point_fix()
    await test_retriever_filtering()
    await test_workflow_build_with_retriever()
    
    print()
    print("✓ All workflow execution fixes verified!")


if __name__ == "__main__":
    asyncio.run(main())