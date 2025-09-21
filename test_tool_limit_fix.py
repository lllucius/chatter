#!/usr/bin/env python3
"""Test script to reproduce and verify the tool call limit fix."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from chatter.core.langgraph import ConversationState, LangGraphWorkflowManager


class MockLLM:
    """Mock LLM that always returns tool calls to simulate infinite recursion."""
    
    def __init__(self, always_call_tool=True):
        self.always_call_tool = always_call_tool
        self.call_count = 0
    
    async def ainvoke(self, messages, **kwargs):
        """Mock LLM that keeps calling the same tool or generates final answer."""
        self.call_count += 1
        
        if self.always_call_tool:
            # Always return a tool call to simulate the recursion issue
            return AIMessage(
                content="",  # Empty content that would cause validation error
                tool_calls=[{
                    "name": "test_tool",
                    "args": {},
                    "id": f"call_{self.call_count}",
                    "type": "tool_call"
                }]
            )
        else:
            # Return a final answer after some tool calls
            return AIMessage(content="The current time is 2025-09-21T17:42:00")
    
    def bind_tools(self, tools):
        """Return self to simulate tool binding."""
        return self


@tool
def test_tool() -> str:
    """A test tool that returns the current time."""
    return "2025-09-21T17:42:00"


async def test_tool_limit_fix():
    """Test that the tool call limit fix generates proper final response."""
    print("Starting test: Tool call limit fix")
    
    manager = LangGraphWorkflowManager()
    
    # Create a mock LLM that always returns tool calls
    mock_llm = MockLLM(always_call_tool=True)
    
    # Create workflow with limited tool calls
    workflow = await manager.create_workflow(
        llm=mock_llm,
        mode="tools",
        tools=[test_tool],
        max_tool_calls=3,  # Limit to 3 tool calls
        user_id="test_user",
        conversation_id="test_conv"
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
        tool_call_count=0
    )
    
    # Run workflow - it should terminate due to tool call limit and generate final response
    try:
        result = await manager.run_workflow(
            workflow=workflow,
            initial_state=initial_state,
            thread_id="test_thread"
        )
        
        print(f"✅ Workflow completed successfully")
        print(f"Tool call count: {result.get('tool_call_count', 'Unknown')}")
        
        # Check the final message
        if result["messages"]:
            last_message = result["messages"][-1]
            print(f"Last message type: {type(last_message).__name__}")
            print(f"Last message content length: {len(last_message.content)}")
            print(f"Last message content: '{last_message.content}'")
            
            # The key test: content should not be empty
            if last_message.content and len(last_message.content.strip()) > 0:
                print("✅ Final message has non-empty content - fix successful!")
                return True
            else:
                print("❌ Final message has empty content - fix failed!")
                return False
        else:
            print("❌ No messages in result")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_tool_limit_fix())
    if success:
        print("\n🎉 Tool call limit fix test PASSED!")
    else:
        print("\n💥 Tool call limit fix test FAILED!")
        exit(1)