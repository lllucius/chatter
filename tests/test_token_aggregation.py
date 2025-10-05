"""Test token aggregation across workflow nodes."""

import pytest
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage, HumanMessage

from chatter.core.langgraph import LangGraphWorkflowManager


@pytest.mark.asyncio
async def test_token_aggregation_across_multiple_nodes():
    """Test that tokens are aggregated from all workflow nodes."""
    
    # Create a mock workflow that simulates multiple nodes with token usage
    mock_workflow = MagicMock()
    
    # Simulate astream with stream_mode='values' returning full state at each step
    async def mock_astream(context, config, stream_mode=None):
        # Initial state (no usage_metadata yet)
        yield {
            "messages": [HumanMessage(content="Test")],
        }
        
        # After first node execution
        yield {
            "messages": [
                HumanMessage(content="Test"),
                AIMessage(content="Response from node 1")
            ],
            "usage_metadata": {
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
            }
        }
        
        # After second node execution
        yield {
            "messages": [
                HumanMessage(content="Test"),
                AIMessage(content="Response from node 1"),
                AIMessage(content="Response from node 2"),
            ],
            "usage_metadata": {
                "input_tokens": 75,
                "output_tokens": 25,
                "total_tokens": 100,
            }
        }
        
        # After third node execution
        yield {
            "messages": [
                HumanMessage(content="Test"),
                AIMessage(content="Response from node 1"),
                AIMessage(content="Response from node 2"),
                AIMessage(content="Response from node 3"),
            ],
            "usage_metadata": {
                "input_tokens": 50,
                "output_tokens": 30,
                "total_tokens": 80,
            }
        }
    
    mock_workflow.astream = mock_astream
    
    # Create workflow manager
    manager = LangGraphWorkflowManager()
    
    # Run workflow
    result = await manager.run_workflow(
        workflow=mock_workflow,
        initial_state={"messages": [HumanMessage(content="Test")]},
        thread_id="test123",
    )
    
    # Verify token aggregation
    # Total should be: 150 + 100 + 80 = 330
    # Prompt tokens: 100 + 75 + 50 = 225
    # Completion tokens: 50 + 25 + 30 = 105
    
    assert "tokens_used" in result
    assert result["tokens_used"] == 330, f"Expected 330 tokens, got {result['tokens_used']}"
    
    assert "prompt_tokens" in result
    assert result["prompt_tokens"] == 225, f"Expected 225 prompt tokens, got {result['prompt_tokens']}"
    
    assert "completion_tokens" in result
    assert result["completion_tokens"] == 105, f"Expected 105 completion tokens, got {result['completion_tokens']}"
    
    assert "cost" in result
    # Cost should be: (225 * 0.00003) + (105 * 0.00006) = 0.00675 + 0.0063 = 0.01305
    expected_cost = (225 * 0.00003) + (105 * 0.00006)
    assert abs(result["cost"] - expected_cost) < 0.0001, f"Expected cost {expected_cost}, got {result['cost']}"
    
    # Verify final state has correct messages
    assert len(result["messages"]) == 4, "Final state should have 4 messages"
    
    print(f"✓ Token aggregation successful!")
    print(f"  Tokens used: {result['tokens_used']}")
    print(f"  Prompt tokens: {result['prompt_tokens']}")
    print(f"  Completion tokens: {result['completion_tokens']}")
    print(f"  Cost: ${result['cost']:.6f}")


@pytest.mark.asyncio
async def test_token_aggregation_with_alternative_field_names():
    """Test token aggregation with alternative field names (prompt_tokens, completion_tokens)."""
    
    mock_workflow = MagicMock()
    
    async def mock_astream(context, config, stream_mode=None):
        # Initial state
        yield {"messages": [HumanMessage(content="Test")]}
        
        # Node with alternative field names
        yield {
            "messages": [HumanMessage(content="Test"), AIMessage(content="Response")],
            "usage_metadata": {
                "prompt_tokens": 200,
                "completion_tokens": 100,
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
    # Total should be calculated: 200 + 100 = 300
    assert result["tokens_used"] == 300
    
    print(f"✓ Alternative field names handled correctly!")


@pytest.mark.asyncio 
async def test_no_tokens_returns_zero():
    """Test that workflows without token usage return zero tokens."""
    
    mock_workflow = MagicMock()
    
    async def mock_astream(context, config, stream_mode=None):
        # Initial state
        yield {"messages": [HumanMessage(content="Test")]}
        
        # Node without usage_metadata
        yield {
            "messages": [HumanMessage(content="Test"), AIMessage(content="Response")],
        }
    
    mock_workflow.astream = mock_astream
    
    manager = LangGraphWorkflowManager()
    result = await manager.run_workflow(
        workflow=mock_workflow,
        initial_state={"messages": [HumanMessage(content="Test")]},
    )
    
    # When no tokens are used, these fields should not be set
    assert "tokens_used" not in result
    assert "cost" not in result
    
    print(f"✓ Zero tokens handled correctly!")
