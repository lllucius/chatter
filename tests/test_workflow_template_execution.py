"""Test for workflow template execution functionality."""

import sys
from unittest.mock import AsyncMock, MagicMock

# Add the project root to Python path
sys.path.insert(0, '/home/runner/work/chatter/chatter')


def test_workflow_generation_methods():
    """Test the workflow generation methods without loading the full service."""

    # Import just the methods we need to test
    from chatter.services.workflow_management import (
        WorkflowManagementService,
    )

    # Create a service instance with a mock session
    mock_session = AsyncMock()
    service = WorkflowManagementService(mock_session)

    # Create a mock template
    mock_template = MagicMock()
    mock_template.name = "Test Template"
    mock_template.capabilities = "plain"
    mock_template.default_params = {
        "model": "gpt-4",
        "temperature": 0.7,
        "system_prompt": "You are a helpful assistant.",
    }
    mock_template.required_tools = []

    # Test plain workflow generation
    user_input = {"temperature": 0.9, "max_tokens": 500}
    merged_input = {**mock_template.default_params, **user_input}

    nodes, edges = service._generate_plain_workflow(
        mock_template, merged_input
    )

    # Verify structure
    assert len(nodes) == 3, f"Expected 3 nodes, got {len(nodes)}"
    assert len(edges) == 2, f"Expected 2 edges, got {len(edges)}"

    # Verify nodes
    node_ids = [node['id'] for node in nodes]
    assert 'start' in node_ids
    assert 'llm' in node_ids
    assert 'end' in node_ids

    # Verify LLM node configuration merges correctly
    llm_node = next(node for node in nodes if node['id'] == 'llm')
    llm_config = llm_node['data']['config']

    # User input should override template defaults
    assert (
        llm_config['temperature'] == 0.9
    ), f"Expected 0.9, got {llm_config['temperature']}"
    assert (
        llm_config['max_tokens'] == 500
    ), f"Expected 500, got {llm_config['max_tokens']}"

    # Template defaults should be preserved when not overridden
    assert (
        llm_config['model'] == "gpt-4"
    ), f"Expected gpt-4, got {llm_config['model']}"
    assert llm_config['system_prompt'] == "You are a helpful assistant."

    # Verify edges connect properly
    edge_connections = [
        (edge['source'], edge['target']) for edge in edges
    ]
    assert ('start', 'llm') in edge_connections
    assert ('llm', 'end') in edge_connections

    print("✅ Plain workflow generation test passed")

    # Test RAG workflow generation
    mock_template.capabilities = "rag"
    nodes, edges = service._generate_rag_workflow(
        mock_template, merged_input
    )

    assert (
        len(nodes) == 4
    ), f"Expected 4 nodes for RAG workflow, got {len(nodes)}"
    assert (
        len(edges) == 3
    ), f"Expected 3 edges for RAG workflow, got {len(edges)}"

    node_ids = [node['id'] for node in nodes]
    assert (
        'retrieval' in node_ids
    ), "RAG workflow should have retrieval node"

    print("✅ RAG workflow generation test passed")

    # Test tools workflow generation
    mock_template.capabilities = "tools"
    nodes, edges = service._generate_tools_workflow(
        mock_template, merged_input
    )

    assert (
        len(nodes) == 3
    ), f"Expected 3 nodes for tools workflow, got {len(nodes)}"

    # Verify LLM node has tools enabled
    llm_node = next(node for node in nodes if 'llm' in node['id'])
    assert llm_node['data']['config'].get('enable_tools')

    print("✅ Tools workflow generation test passed")

    # Test full workflow generation
    mock_template.capabilities = "full"
    nodes, edges = service._generate_full_workflow(
        mock_template, merged_input
    )

    assert (
        len(nodes) == 4
    ), f"Expected 4 nodes for full workflow, got {len(nodes)}"
    node_ids = [node['id'] for node in nodes]
    assert (
        'retrieval' in node_ids
    ), "Full workflow should have retrieval"

    # Verify LLM node has both context and tools
    llm_node = next(node for node in nodes if 'llm' in node['id'])
    llm_config = llm_node['data']['config']
    assert llm_config.get('enable_tools')
    assert llm_config.get('use_context')

    print("✅ Full workflow generation test passed")

    return True


if __name__ == "__main__":
    test_workflow_generation_methods()
    print("✅ All workflow generation tests passed!")
