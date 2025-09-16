# Workflow Streaming Fix

## Problem
The workflow streaming in `PlainWorkflowExecutor.execute_streaming()` was only receiving `{'manage_memory': None}` events and not processing any other events containing actual LLM responses.

## Root Cause
The streaming logic was only looking for events with a direct `"messages"` key:
```python
async for event in workflow.astream(...):
    if "messages" in event:  # Only matched {'messages': [...]}
        # Process messages
```

However, LangGraph workflows emit events with the structure:
- `{'manage_memory': None}` - Memory management node
- `{'call_model': {'messages': [AIMessage(...)]}}` - LLM response node

## Solution
Updated all workflow executors to look for messages in any node's output:
```python
async for event in workflow.astream(...):
    # Look for messages in any node's output
    messages_found = None
    for node_name, node_output in event.items():
        if isinstance(node_output, dict) and "messages" in node_output:
            messages_found = node_output["messages"]
            break
    
    if messages_found:
        # Process messages from any node
```

## Changes Made
1. **PlainWorkflowExecutor**: Fixed event processing logic
2. **RAGWorkflowExecutor**: Fixed event processing + added proper streaming message setup
3. **ToolsWorkflowExecutor**: Fixed event processing + added proper streaming message setup  
4. **FullWorkflowExecutor**: Fixed event processing + added proper streaming message setup
5. **All executors**: Now use consistent streaming lifecycle (start → tokens → complete)

## Verification
- Created comprehensive tests that reproduce the original issue
- Verified all executors now properly process LangGraph events
- Confirmed streaming now works correctly with real event structures

## Impact
Workflow streaming now correctly processes all LangGraph event types and delivers token chunks to users in real-time.