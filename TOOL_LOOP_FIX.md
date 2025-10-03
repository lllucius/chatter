# Tool Calling Loop Fix

## Problem
The `get_time` tool was being called repeatedly in a loop when `max_tool_calls=1` was set in the workflow configuration. The error log showed the tool being called 10+ times before finally stopping.

## Root Cause
In the `create_simple_workflow` method in `chatter/core/workflow_graph_builder.py`, there was an **unconditional edge** from `execute_tools` to `call_model`:

```python
# OLD CODE (line 896)
definition.add_edge("execute_tools", "call_model")  # ❌ Unconditional!
definition.add_edge(
    "execute_tools",
    "finalize_response",
    "tool_calls >= " + str(max_tool_calls),
)
```

This created an infinite loop because:
1. LLM calls a tool (e.g., `get_time`)
2. Tool executes and returns result
3. Workflow **always** goes back to `call_model` via the unconditional edge
4. LLM sees the tool result but still has tools available, so it calls the tool again
5. Repeat steps 2-4 indefinitely (or until another limit is hit)

The conditional edge checking `tool_calls >= max_tool_calls` existed, but when both a conditional and unconditional edge exist from the same source, the routing logic evaluates conditionals first. However, if the unconditional edge is present, it becomes the default fallback, creating the loop.

## Solution
Remove the unconditional edge and make **both** edges conditional:

```python
# NEW CODE (lines 900-910)
# Conditional routing from execute_tools based on tool call count
definition.add_edge(
    "execute_tools",
    "call_model",
    "tool_calls < " + str(max_tool_calls),  # ✅ Continue if under limit
)
definition.add_edge(
    "execute_tools",
    "finalize_response",
    "tool_calls >= " + str(max_tool_calls),  # ✅ Finalize if at/over limit
)
```

Now the workflow correctly:
1. LLM calls a tool
2. Tool executes and `tool_call_count` increments to 1
3. Workflow checks: `tool_calls >= max_tool_calls` (1 >= 1) → **TRUE**
4. Routes to `finalize_response` instead of looping back
5. LLM generates final response and ends

## Workflow Graph
```
┌─────────────┐
│ call_model  │
└──────┬──────┘
       │ has_tool_calls
       ▼
┌──────────────────┐
│ execute_tools    │
│ (increments      │
│ tool_call_count) │
└────────┬─────────┘
         │
    ┌────┴────────────────────┐
    │                         │
    │ tool_calls <            │ tool_calls >=
    │ max_tool_calls          │ max_tool_calls
    ▼                         ▼
┌─────────────┐        ┌──────────────────┐
│ call_model  │        │ finalize_response│
│ (loop back) │        │ (generate final) │
└─────────────┘        └────────┬─────────┘
                                │
                                ▼
                              ┌─────┐
                              │ END │
                              └─────┘
```

## Testing
Created comprehensive tests in `tests/test_workflow_tool_loop_fix.py`:
- ✅ Verifies conditional edges exist from execute_tools
- ✅ Validates max_tool_calls values are properly encoded in conditions
- ✅ Confirms no unconditional loops from execute_tools
- ✅ All existing tool recursion tests still pass

## Files Changed
1. `chatter/core/workflow_graph_builder.py` - Fixed the edge routing logic
2. `tests/test_workflow_tool_loop_fix.py` - Added comprehensive tests

## Expected Behavior After Fix
When a user asks "what time is it" with `max_tool_calls=1`:
1. LLM calls `get_time` tool once
2. Tool returns current time
3. Workflow routes to finalize_response
4. LLM generates natural language response
5. User receives answer: "The current time is [timestamp]"

Previously, the tool would be called 10+ times in a loop before stopping.
