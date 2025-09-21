#!/usr/bin/env python3
"""Manual test script for tool recursion fix."""

import asyncio
import sys
import os

# Add the chatter module to the path
sys.path.insert(0, os.path.abspath('.'))

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

# Import without running complex initialization
from chatter.core.langgraph import ConversationState, LangGraphWorkflowManager


class MockLLM:
    """Mock LLM that always returns tool calls to simulate infinite recursion."""
    
    def __init__(self, max_calls=3):
        self.call_count = 0
        self.max_calls = max_calls
    
    async def ainvoke(self, messages, **kwargs):
        """Mock LLM that keeps calling the same tool."""
        self.call_count += 1
        print(f"LLM call #{self.call_count}")
        
        if self.call_count <= self.max_calls:
            # Return a tool call to simulate the issue
            return AIMessage(
                content="",
                tool_calls=[{
                    "name": "get_time", 
                    "args": {},
                    "id": f"call_{self.call_count}",
                    "type": "tool_call"
                }]
            )
        else:
            # Return a final answer
            return AIMessage(content="The current time is 2025-09-21T17:42:00")
    
    def bind_tools(self, tools):
        """Return self to simulate tool binding."""
        return self


@tool
def get_time() -> str:
    """Get the current time."""
    print("get_time tool called")
    return "2025-09-21T17:42:00"


async def test_tool_recursion_fix():
    """Test that the tool recursion fix works."""
    print("Testing tool recursion fix...")
    
    try:
        manager = LangGraphWorkflowManager()
        
        # Create a mock LLM that always returns tool calls (would cause infinite recursion)
        mock_llm = MockLLM(max_calls=10)  # Would call tool 10 times without fix
        
        print("Creating workflow with max_tool_calls=3...")
        
        # Create workflow with limited tool calls
        workflow = await manager.create_workflow(
            llm=mock_llm,
            mode="tools",
            tools=[get_time],
            max_tool_calls=3,  # Should limit to 3 tool calls
            user_id="test_user",
            conversation_id="test_conv"
        )
        
        print(f"Workflow recursion limit set to: {workflow.recursion_limit}")
        
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
        
        print("Running workflow...")
        
        # Run workflow - it should terminate due to tool call limit
        result = await manager.run_workflow(
            workflow=workflow,
            initial_state=initial_state,
            thread_id="test_thread"
        )
        
        print(f"Workflow completed!")
        print(f"Final tool_call_count: {result.get('tool_call_count', 'not set')}")
        print(f"Total messages: {len(result['messages'])}")
        print(f"LLM was called {mock_llm.call_count} times")
        
        # Count tool messages
        from langchain_core.messages import ToolMessage
        tool_messages = [msg for msg in result["messages"] if isinstance(msg, ToolMessage)]
        print(f"Tool messages: {len(tool_messages)}")
        
        # Check if fix worked
        if result.get("tool_call_count", 0) == 3:
            print("✅ SUCCESS: Tool call limit was enforced!")
        else:
            print(f"❌ FAILED: Expected 3 tool calls, got {result.get('tool_call_count', 0)}")
            
        if mock_llm.call_count <= 5:  # Should be much less than 25
            print("✅ SUCCESS: No infinite recursion!")
        else:
            print(f"❌ FAILED: Too many LLM calls: {mock_llm.call_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_tool_recursion_fix())
    sys.exit(0 if success else 1)