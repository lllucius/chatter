"""Test for tool recursion loop fix."""


import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

from chatter.core.langgraph import (
    ConversationState,
    LangGraphWorkflowManager,
)


class MockLLM:
    """Mock LLM that always returns tool calls to simulate infinite recursion."""

    def __init__(self, always_call_tool=True):
        self.always_call_tool = always_call_tool
        self.call_count = 0

    async def ainvoke(self, messages, **kwargs):
        """Mock LLM that keeps calling the same tool."""
        self.call_count += 1

        if self.always_call_tool:
            # Always return a tool call to simulate the recursion issue
            return AIMessage(
                content="",
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
            # Return a final answer after some tool calls
            return AIMessage(
                content="The current time is 2025-09-21T17:42:00"
            )

    def bind_tools(self, tools):
        """Return self to simulate tool binding."""
        return self


@tool
def test_tool() -> str:
    """A test tool that returns the current time."""
    return "2025-09-21T17:42:00"


class TestToolRecursionFix:
    """Test that tool recursion is properly limited."""

    @pytest.mark.asyncio
    async def test_tool_call_limit_prevents_infinite_recursion(self):
        """Test that max_tool_calls parameter prevents infinite recursion."""
        manager = LangGraphWorkflowManager()

        # Create a mock LLM that always returns tool calls
        mock_llm = MockLLM(always_call_tool=True)

        # Create workflow with limited tool calls
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

        # Run workflow - it should terminate due to tool call limit
        result = await manager.run_workflow(
            workflow=workflow,
            initial_state=initial_state,
            thread_id="test_thread",
        )

        # Verify the workflow terminated due to tool call limit
        assert "tool_call_count" in result
        assert (
            result["tool_call_count"] == 3
        )  # Should have made exactly 3 tool calls

        # Should have stopped generating more tool calls
        last_message = result["messages"][-1]
        # The last message should be a ToolMessage from the 3rd tool execution
        # The workflow should have ended before generating another AIMessage with tool calls
        assert len(result["messages"]) > 1

        # Count the number of tool calls made
        tool_messages = [
            msg
            for msg in result["messages"]
            if isinstance(msg, ToolMessage)
        ]
        assert len(tool_messages) == 3  # Exactly 3 tool executions

        # The mock LLM should have been called at least 3 times (initial + after each tool)
        # but should have been stopped before creating infinite recursion
        assert (
            mock_llm.call_count <= 5
        )  # Much less than 25 (the old recursion limit)

    @pytest.mark.asyncio
    async def test_tool_call_count_tracking(self):
        """Test that tool call count is properly tracked in state."""
        manager = LangGraphWorkflowManager()

        # Create a mock LLM that returns 2 tool calls then stops
        call_count = 0

        class LimitedMockLLM:
            def __init__(self):
                self.call_count = 0

            async def ainvoke(self, messages, **kwargs):
                self.call_count += 1
                if self.call_count <= 2:
                    return AIMessage(
                        content="",
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
                    return AIMessage(content="Done")

            def bind_tools(self, tools):
                return self

        mock_llm = LimitedMockLLM()

        # Create workflow
        workflow = await manager.create_workflow(
            llm=mock_llm,
            enable_retrieval=False,
            enable_tools=True,
            tools=[test_tool],
            max_tool_calls=5,  # Higher limit
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

        # Verify tool call count tracking
        assert result["tool_call_count"] == 2

        # Verify correct number of tool messages
        tool_messages = [
            msg
            for msg in result["messages"]
            if isinstance(msg, ToolMessage)
        ]
        assert len(tool_messages) == 2

    @pytest.mark.asyncio
    async def test_recursion_limit_configuration(self):
        """Test that recursion limit is properly configured based on max_tool_calls."""
        manager = LangGraphWorkflowManager()
        mock_llm = MockLLM(always_call_tool=False)

        # Test with max_tool_calls=5
        workflow = await manager.create_workflow(
            llm=mock_llm,
            enable_retrieval=False,
            enable_tools=True,
            tools=[test_tool],
            max_tool_calls=5,
            user_id="test_user",
            conversation_id="test_conv",
        )

        # Check that recursion limit was set correctly
        # Should be 3 * max_tool_calls + 10 = 3 * 5 + 10 = 25
        expected_limit = max(5 * 3 + 10, 25)
        assert workflow.recursion_limit == expected_limit

    @pytest.mark.asyncio
    async def test_default_max_tool_calls(self):
        """Test that default max_tool_calls value is used when not specified."""
        manager = LangGraphWorkflowManager()
        mock_llm = MockLLM(always_call_tool=True)

        # Create workflow without specifying max_tool_calls
        workflow = await manager.create_workflow(
            llm=mock_llm,
            enable_retrieval=False,
            enable_tools=True,
            tools=[test_tool],
            # max_tool_calls not specified, should default to 10
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

        # Should have stopped at default limit of 10
        assert result["tool_call_count"] == 10

        # Verify recursion limit was set based on default
        expected_limit = max(10 * 3 + 10, 25)
        assert workflow.recursion_limit == expected_limit

    @pytest.mark.asyncio
    async def test_missing_tool_call_count_defaults_to_zero(self):
        """Test that missing tool_call_count in state defaults to 0."""
        manager = LangGraphWorkflowManager()
        mock_llm = MockLLM(always_call_tool=True)

        workflow = await manager.create_workflow(
            llm=mock_llm,
            enable_retrieval=False,
            enable_tools=True,
            tools=[test_tool],
            max_tool_calls=2,
            user_id="test_user",
            conversation_id="test_conv",
        )

        # Create initial state WITHOUT tool_call_count field
        initial_state = {
            "messages": [HumanMessage(content="What is the time?")],
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "retrieval_context": None,
            "tool_calls": [],
            "metadata": {},
            "conversation_summary": None,
            "parent_conversation_id": None,
            "branch_id": None,
            "memory_context": {},
            "workflow_template": None,
            "a_b_test_group": None,
            # Note: tool_call_count is missing - should default to 0
        }

        # Run workflow - should still work and respect limit
        result = await manager.run_workflow(
            workflow=workflow,
            initial_state=initial_state,
            thread_id="test_thread",
        )

        # Should have counted from 0 and stopped at limit
        assert result["tool_call_count"] == 2
