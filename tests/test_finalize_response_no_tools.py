"""Test to verify finalize_response node does not use tools."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from unittest.mock import AsyncMock, Mock, MagicMock

from chatter.core.workflow_graph_builder import (
    WorkflowGraphBuilder,
    create_simple_workflow_definition,
)
from chatter.core.workflow_node_factory import WorkflowNodeContext


class TestFinalizeResponseNoTools:
    """Test that finalize_response node does not bind tools to LLM."""

    @pytest.mark.asyncio
    async def test_finalize_response_uses_llm_without_tools(self):
        """Test that finalize_response node calls LLM without tools bound."""
        builder = WorkflowGraphBuilder()
        
        # Create mock LLM
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_llm_without_tools = Mock()
        
        # Mock bind_tools to return different LLM instances
        mock_llm.bind_tools = Mock(return_value=mock_llm_with_tools)
        
        # Create ainvoke mocks that return different responses
        mock_llm_with_tools.ainvoke = AsyncMock(
            return_value=AIMessage(content="", tool_calls=[{"name": "get_time", "args": {}, "id": "test"}])
        )
        mock_llm_without_tools.ainvoke = AsyncMock(
            return_value=AIMessage(content="The time is 12:00 PM")
        )
        
        # Create tools list
        mock_tools = [Mock(name="get_time")]
        
        # Create finalize_response node
        config = {"system_message": "Provide a final response based on the tool results."}
        finalize_node = builder._create_llm_node(
            "finalize_response",
            mock_llm_without_tools,  # Use the mock without tools
            mock_tools,
            config
        )
        
        # Create a context
        context: WorkflowNodeContext = {
            "messages": [
                HumanMessage(content="What time is it?"),
                AIMessage(content="", tool_calls=[{"name": "get_time", "args": {}, "id": "tc1"}]),
                ToolMessage(content="tool called", tool_call_id="tc1"),
            ],
            "user_id": "test-user",
            "conversation_id": "test-conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 1,
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
            "usage_metadata": {},
        }
        
        # Execute the node
        result = await finalize_node.execute(context)
        
        # Verify that the LLM without tools was called
        mock_llm_without_tools.ainvoke.assert_called_once()
        
        # Verify the result contains a message
        assert "messages" in result
        assert len(result["messages"]) == 1
        
        # Verify the response is a text response (not tool calls)
        response_message = result["messages"][0]
        assert isinstance(response_message, AIMessage)
        assert response_message.content == "The time is 12:00 PM"
        
    @pytest.mark.asyncio
    async def test_call_model_uses_llm_with_tools(self):
        """Test that call_model node calls LLM with tools bound."""
        builder = WorkflowGraphBuilder()
        
        # Create mock LLM
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        
        # Mock bind_tools to return LLM with tools
        mock_llm.bind_tools = Mock(return_value=mock_llm_with_tools)
        
        # Create ainvoke mock
        mock_llm_with_tools.ainvoke = AsyncMock(
            return_value=AIMessage(content="", tool_calls=[{"name": "get_time", "args": {}, "id": "test"}])
        )
        
        # Create tools list
        mock_tools = [Mock(name="get_time")]
        
        # Create call_model node (not finalize_response)
        config = {"system_message": "You are a helpful assistant."}
        call_model_node = builder._create_llm_node(
            "call_model",
            mock_llm,
            mock_tools,
            config
        )
        
        # Create a context
        context: WorkflowNodeContext = {
            "messages": [
                HumanMessage(content="What time is it?"),
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
        
        # Execute the node
        result = await call_model_node.execute(context)
        
        # Verify that the LLM with tools was called
        mock_llm_with_tools.ainvoke.assert_called_once()
        
        # Verify the result contains a message with tool calls
        assert "messages" in result
        assert len(result["messages"]) == 1
        response_message = result["messages"][0]
        assert isinstance(response_message, AIMessage)
        assert len(response_message.tool_calls) > 0

    @pytest.mark.asyncio
    async def test_finalize_response_prevents_infinite_loop(self):
        """Test that finalize_response prevents infinite tool calling loops."""
        builder = WorkflowGraphBuilder()
        
        # Create mock LLM instances
        mock_llm_without_tools = Mock()
        
        # Mock ainvoke to return a text response (not tool calls)
        mock_llm_without_tools.ainvoke = AsyncMock(
            return_value=AIMessage(
                content="Based on the tool results, the current time is 12:00 PM.",
                response_metadata={"finish_reason": "stop"}
            )
        )
        
        # Create tools list
        mock_tools = [Mock(name="get_time")]
        
        # Create finalize_response node
        config = {"system_message": "Provide a final response based on the tool results."}
        finalize_node = builder._create_llm_node(
            "finalize_response",
            mock_llm_without_tools,
            mock_tools,
            config
        )
        
        # Create a context that simulates multiple tool calls (hitting the limit)
        context: WorkflowNodeContext = {
            "messages": [
                HumanMessage(content="What time is it?"),
                AIMessage(content="", tool_calls=[{"name": "get_time", "args": {}, "id": "tc1"}]),
                ToolMessage(content="tool called", tool_call_id="tc1"),
                AIMessage(content="", tool_calls=[{"name": "get_time", "args": {}, "id": "tc2"}]),
                ToolMessage(content="tool called", tool_call_id="tc2"),
                AIMessage(content="", tool_calls=[{"name": "get_time", "args": {}, "id": "tc3"}]),
                ToolMessage(content="tool called", tool_call_id="tc3"),
            ],
            "user_id": "test-user",
            "conversation_id": "test-conv",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 3,  # At the limit
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
            "usage_metadata": {},
        }
        
        # Execute the finalize_response node
        result = await finalize_node.execute(context)
        
        # Verify the result contains a text message (not tool calls)
        assert "messages" in result
        assert len(result["messages"]) == 1
        
        response_message = result["messages"][0]
        assert isinstance(response_message, AIMessage)
        
        # The critical assertion: finalize_response should NOT have tool_calls
        # This prevents the infinite loop
        assert not hasattr(response_message, 'tool_calls') or len(response_message.tool_calls) == 0, \
            "finalize_response should not call tools - this would cause infinite loop!"
        
        # Verify it has actual content instead
        assert response_message.content, "finalize_response should return text content"
        assert "12:00 PM" in response_message.content, "Response should use the tool results"
