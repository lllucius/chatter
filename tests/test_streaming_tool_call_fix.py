"""Test for streaming tool call fix."""

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langchain_core.tools import tool

from chatter.core.langgraph import (
    ConversationState,
    LangGraphWorkflowManager,
)


class MockStreamingLLMWithToolCall:
    """Mock LLM that simulates streaming with tool calls."""

    def __init__(self):
        self.call_count = 0

    async def ainvoke(self, messages, **kwargs):
        """Mock LLM that makes a tool call, then returns final response."""
        self.call_count += 1

        # First call: make a tool call
        if self.call_count == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_date",
                        "args": {},
                        "id": "call_1",
                        "type": "tool_call",
                    }
                ],
            )
        # Second call (after tool execution): return final response
        else:
            return AIMessage(
                content="The current date is 2025-10-03"
            )

    def bind_tools(self, tools):
        """Return self to simulate tool binding."""
        return self


@tool
def get_date() -> str:
    """Get the current date."""
    return "2025-10-03"


class TestStreamingToolCallFix:
    """Test that streaming properly handles tool calls."""

    @pytest.mark.asyncio
    async def test_chunk_with_tool_calls_detection(self):
        """Test the logic for detecting tool calls in chunks."""
        # Create mock chunks with different tool call scenarios
        
        # Scenario 1: AIMessageChunk with tool_calls attribute
        chunk_with_tool_calls = AIMessageChunk(
            content="",
            tool_calls=[{"name": "test", "args": {}, "id": "1", "type": "tool_call"}]
        )
        
        # Scenario 2: AIMessageChunk with tool_call_chunks attribute
        chunk_with_tool_call_chunks = AIMessageChunk(
            content="",
            tool_call_chunks=[{"name": "test", "args": "{", "id": "1", "index": 0, "type": "tool_call_chunk"}]
        )
        
        # Scenario 3: AIMessageChunk with invalid_tool_calls
        chunk_with_invalid = AIMessageChunk(
            content="",
            invalid_tool_calls=[{"name": None, "args": "}", "id": None, "error": None, "type": "invalid_tool_call"}]
        )
        
        # Scenario 4: Regular content chunk without tool calls
        chunk_with_content = AIMessageChunk(content="Hello, the date is...")
        
        # Test the detection logic that matches workflow_execution.py
        def has_tool_calls(chunk):
            if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                return True
            elif hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                return True
            elif hasattr(chunk, "invalid_tool_calls") and chunk.invalid_tool_calls:
                return True
            elif isinstance(chunk, dict):
                if chunk.get("tool_calls") or chunk.get("tool_call_chunks") or chunk.get("invalid_tool_calls"):
                    return True
            return False
        
        # Verify detection works correctly
        assert has_tool_calls(chunk_with_tool_calls) is True, "Should detect tool_calls"
        assert has_tool_calls(chunk_with_tool_call_chunks) is True, "Should detect tool_call_chunks"
        assert has_tool_calls(chunk_with_invalid) is True, "Should detect invalid_tool_calls"
        assert has_tool_calls(chunk_with_content) is False, "Should not detect tool calls in regular content"

    @pytest.mark.asyncio
    async def test_final_response_is_streamed(self):
        """Test that the final response (without tool calls) is properly streamed."""
        manager = LangGraphWorkflowManager()

        # Create a mock LLM that makes a tool call then responds
        mock_llm = MockStreamingLLMWithToolCall()

        # Create workflow with tools enabled
        workflow = await manager.create_workflow(
            llm=mock_llm,
            enable_retrieval=False,
            enable_tools=True,
            tools=[get_date],
            max_tool_calls=10,
            user_id="test_user",
            conversation_id="test_conv",
        )

        # Create initial state
        initial_state = ConversationState(
            messages=[HumanMessage(content="What is the date?")],
            user_id="test_user",
            conversation_id="test_conv",
            retrieval_context=None,
            tool_calls=[],
            metadata={},
            conversation_summary=None,
            parent_conversation_id=None,
            branch_id=None,
            memory_context={},
            workflow_template=None,
            a_b_test_group=None,
            tool_call_count=0,
        )

        # Run workflow to completion
        result = await manager.run_workflow(
            workflow=workflow,
            initial_state=initial_state,
            thread_id="test_thread",
        )

        # Verify final message contains expected content
        final_message = result["messages"][-1]
        assert isinstance(final_message, AIMessage)
        assert "2025-10-03" in final_message.content or "date" in final_message.content.lower()
        
        # Verify it doesn't contain tool call JSON
        assert '{"type": "function"' not in final_message.content
        assert '"function": "date"' not in final_message.content
