# Fix Summary: workspace_id AttributeError

## Problem
The system was experiencing streaming chat request failures with this error:

```
2025-09-16T14:49:03.879053Z [error] Streaming chat request failed 
[chatter.services.chat] correlation_id=01K59G0AJYD46G093FCZ3KZM68 
error=Basic workflow streaming failed: 'Conversation' object has no attribute 'workspace_id' 
user_id=01K58A9TXQB9VPVJXARP2T14F8
```

## Root Cause
The `UnifiedWorkflowExecutor._get_workflow_config()` method was trying to access `conversation.workspace_id` on line 254, but the `Conversation` model in `chatter/models/conversation.py` does not have a `workspace_id` attribute.

## Solution
**File**: `chatter/core/unified_workflow_executor.py` (line 254)

**Before** (causing AttributeError):
```python
workspace_id = conversation.workspace_id or "default"
```

**After** (fixed):
```python
# Use user_id as workspace_id since the Conversation model doesn't have workspace_id
workspace_id = conversation.user_id or "default"
```

## Rationale
- The `workspace_id` is used to:
  1. Create user-specific document collections (`documents_{workspace_id}`)
  2. Get user-specific tools via `workflow_manager.get_tools(workspace_id)`
- Using `user_id` as the workspace identifier makes perfect sense since each user should have their own workspace
- The fallback to `"default"` handles edge cases where `user_id` might be None or empty

## Additional Improvements

### 1. Created Missing Module
**File**: `chatter/core/workflow_executors.py` (new file)

The tests were importing from `chatter.core.workflow_executors` which didn't exist. Created backward-compatible wrapper classes:
- `PlainWorkflowExecutor`
- `RAGWorkflowExecutor` 
- `ToolsWorkflowExecutor`
- `FullWorkflowExecutor`

These delegate to the `UnifiedWorkflowExecutor` while maintaining the expected interface.

### 2. Fixed Request Mutation
The wrapper classes now copy `ChatRequest` objects instead of mutating them directly, preventing potential side effects.

## Testing
Comprehensive testing confirms:
- ✅ The exact error scenario from the log is resolved
- ✅ Edge cases (None/empty user_id) work correctly
- ✅ Streaming workflow execution works as expected
- ✅ Collection names are generated correctly
- ✅ Backward compatibility is maintained

## Impact
- **Immediate**: Streaming chat requests should no longer fail with workspace_id AttributeError
- **User Experience**: Chat streaming functionality should work reliably
- **System Stability**: Eliminates a common source of workflow execution failures

The fix is minimal, surgical, and maintains all existing functionality while resolving the core issue.