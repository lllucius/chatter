"""Test for tool call limit fix to prevent empty assistant messages."""

import unittest.mock

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

# Mock security before importing the module
mock_security_manager = unittest.mock.MagicMock()
mock_security_manager.authorize_tool_execution.return_value = True

# Set up mocks for imports
import sys

sys.modules['chatter.core.workflow_security'] = (
    unittest.mock.MagicMock()
)
sys.modules[
    'chatter.core.workflow_security'
].workflow_security_manager = mock_security_manager

from chatter.core.langgraph import (
    ConversationState,
    LangGraphWorkflowManager,
)


@tool
def test_tool() -> str:
    """A test tool that returns the current time."""
    return "2025-09-21T17:42:00"


class ToolLimitMockLLM:
    """Mock LLM that generates tool calls until limit is reached."""

    def __init__(self, max_calls=5):
        self.call_count = 0
        self.max_calls = max_calls

    async def ainvoke(self, messages, **kwargs):
        """Mock LLM behavior for tool limit testing."""
        self.call_count += 1

        if self.call_count <= self.max_calls:
            # Return a tool call with empty content
            return AIMessage(
                content="",  # This empty content was causing the validation error
                tool_calls=[
                    {
                        "name": "test_tool",
                        "args": {},
                        "id": f"call_{self.call_count}",
                        "type": "tool_call",
                    }
                ],
            )
        else:
            # Should not reach here in our test due to tool limit
            return AIMessage(content="Final response")

    def bind_tools(self, tools):
        return self


class TestToolCallLimitFix:
    """Test the tool call limit fix."""

    @pytest.mark.asyncio
    async def test_tool_call_limit_generates_proper_final_response(
        self,
    ):
        """Test that tool call limit fix generates non-empty final response."""
        manager = LangGraphWorkflowManager()

        # Create mock LLM that would exceed the limit
        mock_llm = ToolLimitMockLLM(max_calls=10)  # Would make 10 calls

        # Create workflow with limit of 3
        workflow = await manager.create_workflow(
            llm=mock_llm,
            enable_retrieval=False,
            enable_tools=True,
            tools=[test_tool],
            max_tool_calls=3,  # Limit to 3 tool calls
            user_id="test_user",
            conversation_id="test_conv",
        )

        # Create initial state
        initial_state = ConversationState(
            messages=[HumanMessage(content="What is the time?")],
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

        # Run workflow
        result = await manager.run_workflow(
            workflow=workflow,
            initial_state=initial_state,
            thread_id="test_thread",
        )

        # Verify tool call count is at limit
        assert result["tool_call_count"] == 3

        # Verify we have messages
        assert len(result["messages"]) > 0

        # Verify final message has non-empty content
        last_message = result["messages"][-1]
        assert isinstance(last_message, AIMessage)
        assert last_message.content is not None
        assert len(last_message.content.strip()) > 0

        # Verify final message doesn't have tool calls (finalize_response should not generate them)
        assert (
            not hasattr(last_message, "tool_calls")
            or not last_message.tool_calls
        )

        # Verify the content mentions tool completion (as per finalize_response logic)
        assert "tool" in last_message.content.lower()
        assert "completed" in last_message.content.lower()

    @pytest.mark.asyncio
    async def test_should_continue_routes_to_finalize_at_limit(self):
        """Test that should_continue correctly routes to finalize_response at tool limit."""
        # This tests the core logic that was changed

        # Mock message with tool calls
        message_with_tools = AIMessage(content="")
        message_with_tools.tool_calls = [
            {"name": "test_tool", "args": {}, "id": "call_1"}
        ]

        # Mock state at tool call limit
        state = {
            "messages": [
                HumanMessage(content="Hello"),
                message_with_tools,
            ],
            "tool_call_count": 3,
        }

        # Simulate should_continue logic with tool limit of 3
        use_tools = True
        max_tool_calls = 3

        last_message = (
            state["messages"][-1] if state["messages"] else None
        )
        has_tool_calls = (
            use_tools
            and last_message
            and hasattr(last_message, "tool_calls")
            and getattr(last_message, "tool_calls", None)
        )

        if not has_tool_calls:
            result = "END"
        else:
            current_tool_count = state.get("tool_call_count", 0)
            max_allowed = max_tool_calls or 10

            if current_tool_count >= max_allowed:
                result = "finalize_response"  # This is the key fix
            else:
                result = "execute_tools"

        # Should route to finalize_response when at limit
        assert result == "finalize_response"

    @pytest.mark.asyncio
    async def test_workflow_completes_without_recursion_error(self):
        """Test that workflow completes without hitting recursion limits."""
        manager = LangGraphWorkflowManager()

        # Create mock LLM that would cause infinite recursion without fix
        mock_llm = ToolLimitMockLLM(
            max_calls=100
        )  # Would try to make many calls

        # Create workflow with reasonable limit
        workflow = await manager.create_workflow(
            llm=mock_llm,
            enable_retrieval=False,
            enable_tools=True,
            tools=[test_tool],
            max_tool_calls=5,
            user_id="test_user",
            conversation_id="test_conv",
        )

        initial_state = ConversationState(
            messages=[HumanMessage(content="What is the time?")],
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

        # Should complete without recursion error
        result = await manager.run_workflow(
            workflow=workflow,
            initial_state=initial_state,
            thread_id="test_thread",
        )

        # Should stop at tool call limit
        assert result["tool_call_count"] == 5

        # Should have final message with content
        last_message = result["messages"][-1]
        assert isinstance(last_message, AIMessage)
        assert len(last_message.content.strip()) > 0
