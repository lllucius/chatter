"""Test that workflow execution results use aggregated usage metadata correctly.

This test verifies the data flow described in the problem statement:
- core.langgraph.run_workflow() aggregates usage_metadata from all nodes
- Returns aggregated values as tokens_used, prompt_tokens, completion_tokens, cost
- All consumers should use these aggregated fields, not raw usage_metadata
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from langchain_core.messages import AIMessage, HumanMessage

from chatter.core.langgraph import LangGraphWorkflowManager


@pytest.mark.asyncio
async def test_run_workflow_returns_aggregated_usage_fields():
    """Verify run_workflow returns aggregated usage metadata as top-level fields."""
    
    # Create a mock workflow that simulates nodes returning usage_metadata
    mock_workflow = MagicMock()
    
    # Simulate astream with stream_mode='values' returning full state at each step
    async def mock_astream(context, config, stream_mode=None):
        # Initial state (no usage_metadata yet)
        yield {
            "messages": [HumanMessage(content="Test")],
        }
        
        # After first node execution with usage_metadata
        yield {
            "messages": [
                HumanMessage(content="Test"),
                AIMessage(content="Response 1")
            ],
            "usage_metadata": {
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
            }
        }
        
        # After second node execution with different usage_metadata
        yield {
            "messages": [
                HumanMessage(content="Test"),
                AIMessage(content="Response 1"),
                AIMessage(content="Response 2"),
            ],
            "usage_metadata": {
                "input_tokens": 75,
                "output_tokens": 25,
                "total_tokens": 100,
            }
        }
    
    mock_workflow.astream = mock_astream
    
    # Create workflow manager and run
    manager = LangGraphWorkflowManager()
    result = await manager.run_workflow(
        workflow=mock_workflow,
        initial_state={"messages": [HumanMessage(content="Test")]},
        thread_id="test123",
    )
    
    # Verify aggregated fields are present in result
    assert "tokens_used" in result, "Result should contain tokens_used"
    assert "prompt_tokens" in result, "Result should contain prompt_tokens"
    assert "completion_tokens" in result, "Result should contain completion_tokens"
    assert "cost" in result, "Result should contain cost"
    
    # Verify aggregated values are correct
    assert result["tokens_used"] == 250, f"Expected 250 total tokens, got {result['tokens_used']}"
    assert result["prompt_tokens"] == 175, f"Expected 175 prompt tokens, got {result['prompt_tokens']}"
    assert result["completion_tokens"] == 75, f"Expected 75 completion tokens, got {result['completion_tokens']}"
    
    # Verify cost calculation
    expected_cost = (175 * 0.00003) + (75 * 0.00006)
    assert abs(result["cost"] - expected_cost) < 0.0001, f"Expected cost {expected_cost}, got {result['cost']}"
    
    print("✓ run_workflow returns aggregated usage fields correctly")


@pytest.mark.asyncio
async def test_workflow_result_separates_aggregated_from_node_metadata():
    """Verify that result contains both aggregated fields AND last node's usage_metadata."""
    
    mock_workflow = MagicMock()
    
    async def mock_astream(context, config, stream_mode=None):
        yield {"messages": [HumanMessage(content="Test")]}
        
        # First node
        yield {
            "messages": [HumanMessage(content="Test"), AIMessage(content="Response 1")],
            "usage_metadata": {
                "input_tokens": 100,
                "output_tokens": 50,
            }
        }
        
        # Second node - this will be in the final state
        yield {
            "messages": [
                HumanMessage(content="Test"),
                AIMessage(content="Response 1"),
                AIMessage(content="Response 2")
            ],
            "usage_metadata": {
                "input_tokens": 75,
                "output_tokens": 25,
            }
        }
    
    mock_workflow.astream = mock_astream
    
    manager = LangGraphWorkflowManager()
    result = await manager.run_workflow(
        workflow=mock_workflow,
        initial_state={"messages": [HumanMessage(content="Test")]},
    )
    
    # Final state should contain the last node's usage_metadata
    assert "usage_metadata" in result
    assert result["usage_metadata"]["input_tokens"] == 75
    assert result["usage_metadata"]["output_tokens"] == 25
    
    # BUT aggregated fields should sum across ALL nodes
    assert result["prompt_tokens"] == 175  # 100 + 75
    assert result["completion_tokens"] == 75  # 50 + 25
    assert result["tokens_used"] == 250  # 150 + 100
    
    print("✓ Result correctly separates aggregated values from last node's usage_metadata")


@pytest.mark.asyncio
async def test_workflow_without_usage_metadata():
    """Verify that workflows without token usage don't include usage fields."""
    
    mock_workflow = MagicMock()
    
    async def mock_astream(context, config, stream_mode=None):
        yield {"messages": [HumanMessage(content="Test")]}
        yield {
            "messages": [HumanMessage(content="Test"), AIMessage(content="Response")],
            # No usage_metadata
        }
    
    mock_workflow.astream = mock_astream
    
    manager = LangGraphWorkflowManager()
    result = await manager.run_workflow(
        workflow=mock_workflow,
        initial_state={"messages": [HumanMessage(content="Test")]},
    )
    
    # When no tokens are used, these fields should not be set
    assert "tokens_used" not in result
    assert "prompt_tokens" not in result
    assert "completion_tokens" not in result
    assert "cost" not in result
    
    print("✓ Workflows without token usage correctly omit usage fields")


@pytest.mark.asyncio
async def test_alternative_token_field_names():
    """Test that run_workflow handles alternative field names (prompt_tokens vs input_tokens)."""
    
    mock_workflow = MagicMock()
    
    async def mock_astream(context, config, stream_mode=None):
        yield {"messages": [HumanMessage(content="Test")]}
        
        # Node using alternative field names
        yield {
            "messages": [HumanMessage(content="Test"), AIMessage(content="Response")],
            "usage_metadata": {
                "prompt_tokens": 200,  # Alternative to input_tokens
                "completion_tokens": 100,  # Alternative to output_tokens
            }
        }
    
    mock_workflow.astream = mock_astream
    
    manager = LangGraphWorkflowManager()
    result = await manager.run_workflow(
        workflow=mock_workflow,
        initial_state={"messages": [HumanMessage(content="Test")]},
    )
    
    # Verify tokens are extracted from alternative field names
    assert result["prompt_tokens"] == 200
    assert result["completion_tokens"] == 100
    assert result["tokens_used"] == 300  # 200 + 100
    
    print("✓ Alternative field names (prompt_tokens, completion_tokens) handled correctly")


@pytest.mark.asyncio  
async def test_duplicate_usage_metadata_not_aggregated():
    """Verify that duplicate usage_metadata is not aggregated twice."""
    
    mock_workflow = MagicMock()
    
    async def mock_astream(context, config, stream_mode=None):
        yield {"messages": [HumanMessage(content="Test")]}
        
        # Same usage_metadata appears twice (shouldn't happen in practice, but test defensively)
        same_metadata = {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
        }
        
        yield {
            "messages": [HumanMessage(content="Test"), AIMessage(content="Response")],
            "usage_metadata": same_metadata
        }
        
        # Duplicate - should be ignored by deduplication logic
        yield {
            "messages": [HumanMessage(content="Test"), AIMessage(content="Response")],
            "usage_metadata": same_metadata
        }
    
    mock_workflow.astream = mock_astream
    
    manager = LangGraphWorkflowManager()
    result = await manager.run_workflow(
        workflow=mock_workflow,
        initial_state={"messages": [HumanMessage(content="Test")]},
    )
    
    # Should only count the metadata once, not twice
    assert result["tokens_used"] == 150, f"Expected 150 tokens (not doubled), got {result['tokens_used']}"
    assert result["prompt_tokens"] == 100
    assert result["completion_tokens"] == 50
    
    print("✓ Duplicate usage_metadata correctly deduplicated")


if __name__ == "__main__":
    import asyncio
    
    async def run_tests():
        await test_run_workflow_returns_aggregated_usage_fields()
        await test_workflow_result_separates_aggregated_from_node_metadata()
        await test_workflow_without_usage_metadata()
        await test_alternative_token_field_names()
        await test_duplicate_usage_metadata_not_aggregated()
        print("\n✅ All usage metadata flow tests passed!")
    
    asyncio.run(run_tests())
