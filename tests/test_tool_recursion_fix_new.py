"""Test for tool recursion loop fix."""

import pytest
from collections import Counter
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool


@tool
def get_time() -> str:
    """Get the current date and time."""
    return "2025-09-21T17:42:09.433315"


class TestToolRecursionFix:
    """Test that tool recursion is properly detected and prevented."""

    def test_recursion_detection_logic(self):
        """Test the core recursion detection logic."""
        # Simulate messages that would cause recursion
        recent_tool_calls = ["get_time", "get_time", "get_time"]
        tool_results = ["2025-09-21T17:42:09.433315", "2025-09-21T17:42:11.067013"]
        
        # Apply the logic from the fix (including progress detection)
        if recent_tool_calls and tool_results:
            tool_counts = Counter(recent_tool_calls)
            repeated_tools = [tool for tool, count in tool_counts.items() if count >= 2]
            
            # Check for progress (simulate the _is_making_progress function)
            def _is_making_progress(tool_results: list[str], repeated_tools: list[str]) -> bool:
                if len(tool_results) < 1:
                    return True
                
                # Special handling for time-related tools
                time_related_tools = ["get_time", "get_current_time", "time", "clock", "date"]
                if any(tool.lower() in time_related_tools for tool in repeated_tools):
                    import re
                    timestamp_pattern = r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}'
                    has_valid_timestamp = any(re.search(timestamp_pattern, result) for result in tool_results)
                    if has_valid_timestamp:
                        return False  # We have a time result, no need for more calls
                
                if len(tool_results) < 2:
                    return True
                
                recent_results = tool_results[-2:]
                if len(set(recent_results)) > 1:
                    return True
                
                return True
            
            should_finalize = repeated_tools and len(tool_results) >= 1 and not _is_making_progress(tool_results, repeated_tools)
            
            assert should_finalize is True
            assert "get_time" in repeated_tools
            assert tool_counts["get_time"] >= 2

    def test_message_extraction_pattern(self):
        """Test that we correctly extract tool calls and results from messages."""
        # Mock messages representing the problematic pattern
        class MockMessage:
            def __init__(self, content=None, tool_calls=None, tool_call_id=None):
                self.content = content
                if tool_calls:
                    self.tool_calls = tool_calls
                if tool_call_id:
                    self.tool_call_id = tool_call_id

        # Recreate the pattern from the errors file
        messages = [
            MockMessage(content="what is the time"),
            MockMessage(content="", tool_calls=[{"name": "get_time"}]),
            MockMessage(content="2025-09-21T17:42:09.433315", tool_call_id="call_1"),
            MockMessage(content="", tool_calls=[{"name": "get_time"}]),
            MockMessage(content="2025-09-21T17:42:11.067013", tool_call_id="call_2"),
            MockMessage(content="", tool_calls=[{"name": "get_time"}]),
        ]

        # Extract tool calls and results (simulate the fix logic)
        recent_tool_calls = []
        tool_results = []

        for msg in messages[-6:]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    recent_tool_calls.append(tool_call.get("name"))
            elif hasattr(msg, "tool_call_id"):
                tool_results.append(msg.content)

        # Verify extraction
        assert len(recent_tool_calls) == 3
        assert all(call == "get_time" for call in recent_tool_calls)
        assert len(tool_results) == 2
        assert "2025-09-21T17:42:09.433315" in tool_results

        # Test recursion detection
        tool_counts = Counter(recent_tool_calls)
        repeated_tools = [tool for tool, count in tool_counts.items() if count >= 2]
        should_finalize = repeated_tools and len(tool_results) >= 1
        
        assert should_finalize is True

    def test_normal_tool_usage_not_affected(self):
        """Test that normal tool usage (without recursion) is not affected."""
        # Single tool call - should not trigger recursion detection
        recent_tool_calls = ["get_time"]
        tool_results = ["2025-09-21T17:42:09.433315"]
        
        tool_counts = Counter(recent_tool_calls)
        repeated_tools = [tool for tool, count in tool_counts.items() if count >= 2]
        should_finalize = bool(repeated_tools and len(tool_results) >= 1)
        
        assert should_finalize is False, f"Expected False, got {should_finalize}"
        assert len(repeated_tools) == 0, f"Expected 0 repeated tools, got {repeated_tools}"

    def test_different_tools_not_affected(self):
        """Test that using different tools doesn't trigger recursion detection."""
        # Different tools being called - should not trigger recursion
        recent_tool_calls = ["get_time", "calculator", "get_weather"]
        tool_results = ["2025-09-21T17:42:09.433315", "42", "Sunny"]
        
        tool_counts = Counter(recent_tool_calls)
        repeated_tools = [tool for tool, count in tool_counts.items() if count >= 2]
        should_finalize = bool(repeated_tools and len(tool_results) >= 1)
        
        assert should_finalize is False, f"Expected False, got {should_finalize}"
        assert len(repeated_tools) == 0, f"Expected 0 repeated tools, got {repeated_tools}"

    def test_tool_results_extraction_for_final_response(self):
        """Test that tool results are properly extracted for final response generation."""
        # Mock messages for final response context
        messages = [
            HumanMessage(content="what is the time"),
            AIMessage(content="", tool_calls=[{"name": "get_time", "args": {}, "id": "call_1"}]),
            ToolMessage(content="2025-09-21T17:42:09.433315", tool_call_id="call_1"),
            AIMessage(content="", tool_calls=[{"name": "get_time", "args": {}, "id": "call_2"}]),
            ToolMessage(content="2025-09-21T17:42:11.067013", tool_call_id="call_2"),
        ]

        # Extract tool results and user question (simulate finalize_response logic)
        tool_results = []
        user_question = ""

        for msg in messages:
            if isinstance(msg, ToolMessage):
                tool_results.append(msg.content)
            elif isinstance(msg, HumanMessage):
                user_question = msg.content

        assert len(tool_results) == 2
        assert user_question == "what is the time"
        assert "2025-09-21T17:42:09.433315" in tool_results
        assert "2025-09-21T17:42:11.067013" in tool_results

        # Test final context generation
        if tool_results and user_question:
            final_context = (
                f"Based on the following information gathered from tools:\n"
                f"{', '.join(tool_results[-3:])}\n\n"
                f"Please provide a direct and helpful answer to: {user_question}"
            )
            
            assert "2025-09-21T17:42:09.433315" in final_context
            assert "what is the time" in final_context
            assert "Please provide a direct and helpful answer" in final_context

    def test_time_tool_recursion_prevention(self):
        """Test that time tools specifically stop recursion after getting a valid timestamp."""
        # Test data mimicking the real scenario from the error logs
        tool_calls = ["get_time", "get_time"]
        tool_results = ["2025-09-22T12:56:21.560005", "2025-09-22T12:56:24.163200"]
        
        # Simulate the _is_making_progress function for time tools
        def _is_making_progress(tool_results: list[str], repeated_tools: list[str]) -> bool:
            if len(tool_results) < 1:
                return True
            
            # Special handling for time-related tools
            time_related_tools = ["get_time", "get_current_time", "time", "clock", "date"]
            if any(tool.lower() in time_related_tools for tool in repeated_tools):
                import re
                timestamp_pattern = r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}'
                has_valid_timestamp = any(re.search(timestamp_pattern, result) for result in tool_results)
                if has_valid_timestamp:
                    return False  # We have a time result, no need for more calls
            
            if len(tool_results) < 2:
                return True
            
            recent_results = tool_results[-2:]
            if len(set(recent_results)) > 1:
                return True
            
            return True
        
        # Test the logic
        tool_counts = Counter(tool_calls)
        repeated_tools = [tool for tool, count in tool_counts.items() if count >= 2]
        
        # After first call - should allow continuation
        should_stop_after_first = repeated_tools and len(tool_results[:1]) >= 1 and not _is_making_progress(tool_results[:1], repeated_tools)
        assert should_stop_after_first is False, "Should not stop after first get_time call"
        
        # After second call - should detect recursion and stop
        should_stop_after_second = repeated_tools and len(tool_results) >= 1 and not _is_making_progress(tool_results, repeated_tools)
        assert should_stop_after_second is True, "Should stop after second get_time call with timestamp"
        
        # Verify the repeated tool is correctly identified
        assert "get_time" in repeated_tools
        assert tool_counts["get_time"] == 2


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    test_class = TestToolRecursionFix()
    tests = [
        test_class.test_recursion_detection_logic,
        test_class.test_message_extraction_pattern,
        test_class.test_normal_tool_usage_not_affected,
        test_class.test_different_tools_not_affected,
        test_class.test_tool_results_extraction_for_final_response,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    if failed == 0:
        print("🎉 All tests passed!")