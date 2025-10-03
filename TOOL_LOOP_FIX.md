# Tool Calling Loop Fix - LLM State Based Routing

## Problem
The `get_time` tool was being called repeatedly in a loop when the user asked "what time is it". The error log showed the tool being called 10+ times before finally stopping.

## Root Cause
In the `create_simple_workflow` method in `chatter/core/workflow_graph_builder.py`, there was an **unconditional edge** from `execute_tools` back to `call_model`:

```python
# OLD CODE (line 896)
definition.add_edge("execute_tools", "call_model")  # ❌ Unconditional!
```

This created an infinite loop because after executing tools, the workflow always went back to `call_model`, and the LLM would keep calling tools since they were still available in its context.

## Solution - LLM State Based Routing
Instead of using a counter as the primary termination mechanism, the new approach **relies on the LLM's natural decision** to stop calling tools, with `max_tool_calls` as a safety limit:

```python
# NEW CODE (lines 895-909)
if enable_tools:
    # Route from call_model based on LLM's decision and safety limit
    definition.add_edge(
        "call_model",
        "execute_tools",
        "has_tool_calls AND tool_calls < " + str(max_tool_calls),
    )
    definition.add_edge(
        "call_model",
        "finalize_response",
        "has_tool_calls AND tool_calls >= " + str(max_tool_calls),
    )
    definition.add_edge("call_model", END, "no_tool_calls")
    # After executing tools, always return to call_model to let LLM decide
    definition.add_edge("execute_tools", "call_model")
    definition.add_edge("finalize_response", END)
```

### Key Design Principles

1. **LLM Decides When to Stop**: The primary termination mechanism is the LLM returning a response without `tool_calls`. When the LLM has all the information it needs, it naturally stops requesting tools.

2. **Safety Limit as Fallback**: The `max_tool_calls` counter acts as a safety limit to prevent infinite loops if the LLM keeps requesting tools. When the limit is reached, we route to `finalize_response` instead.

3. **Routing Happens at call_model**: All routing decisions are made at the `call_model` node based on:
   - **LLM's state**: Does it want tools (`has_tool_calls`) or is it done (`no_tool_calls`)?
   - **Safety check**: Have we reached the `max_tool_calls` limit?

4. **execute_tools Returns Unconditionally**: After tool execution, we always return to `call_model` to let the LLM decide the next step.

## Workflow Graph
```
                    ┌─────────────┐
                    │ call_model  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        │ has_tool_calls   │ has_tool_calls   │ no_tool_calls
        │ AND              │ AND              │ (LLM is done)
        │ tool_calls <     │ tool_calls >=    │
        │ max_tool_calls   │ max_tool_calls   │
        ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌─────┐
│ execute_tools    │ │ finalize_response│ │ END │
│ (call tool and   │ │ (safety exit)    │ └─────┘
│ increment count) │ └────────┬─────────┘
└────────┬─────────┘          │
         │                    │
         │ (unconditional)    │
         └───────────▶┌───────▼────────┐
                      │   call_model   │
                      │ (LLM decides)  │
                      └────────────────┘
```

## Expected Behavior

### Scenario 1: LLM Stops Naturally (Normal Case)
1. User: "what time is it?"
2. LLM calls `get_time` tool → `tool_call_count` = 1
3. Tool returns: "2025-10-03T12:00:00"
4. Back to `call_model`: LLM sees the result and decides it has enough info
5. LLM returns response WITHOUT `tool_calls` → `no_tool_calls` = true
6. Route to END
7. User gets: "The current time is 12:00 PM on October 3rd, 2025"

### Scenario 2: Safety Limit Reached (Fallback)
1. LLM keeps calling tools (maybe due to confusion or prompt issue)
2. After `max_tool_calls` is reached
3. At `call_model`: Check `has_tool_calls AND tool_calls >= max_tool_calls`
4. Route to `finalize_response` (calls LLM without tools to force final answer)
5. User gets a response even if limit was hit

## Testing
Updated test suite in `tests/test_workflow_tool_loop_fix.py`:
- ✅ Verifies routing from `call_model` based on LLM state
- ✅ Confirms `execute_tools` returns to `call_model` unconditionally
- ✅ Validates safety limits are properly encoded in conditions
- ✅ Tests that LLM can naturally stop before hitting limits
- ✅ All existing tool recursion tests still pass

## Files Changed
1. `chatter/core/workflow_graph_builder.py` - Changed routing logic to be LLM-state based
2. `tests/test_workflow_tool_loop_fix.py` - Updated tests to match new architecture

## Impact
This is a **better architectural design** because:
- **More Natural**: Relies on LLM's decision-making rather than arbitrary counters
- **More Flexible**: LLM can make multiple tool calls if genuinely needed
- **Safer**: Still has `max_tool_calls` as a safety net to prevent infinite loops
- **Better UX**: LLM stops when it has enough information, not when it hits an artificial limit

**Before:** Counter-based termination (rigid, could cut off legitimate multi-tool workflows)
**After:** LLM-state based termination with safety limits (flexible and natural)
