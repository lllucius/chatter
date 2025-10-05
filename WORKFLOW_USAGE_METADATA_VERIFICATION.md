# Workflow Execution Usage Metadata - Verification Summary

## Issue Statement

"Evaluate workflow execution and ensure that any result that contains usage information are getting that information from the correct source, core.langgraph.run_workflow() returns this information in the 'usage_metadata' dict."

## Investigation Results

### The Correct Source: Aggregated Fields from run_workflow()

`LangGraphWorkflowManager.run_workflow()` is the authoritative source for usage information. It:

1. **Collects** `usage_metadata` from all node executions during workflow streaming
2. **Aggregates** tokens across all nodes (with deduplication)
3. **Returns** aggregated values as **top-level fields** in the result dict:
   - `tokens_used`: Total tokens across all nodes
   - `prompt_tokens`: Total input/prompt tokens  
   - `completion_tokens`: Total output/completion tokens
   - `cost`: Estimated cost based on token usage

### Key Finding: One Bug Fixed

**Bug Found**: Custom workflow endpoint (`execute_custom_workflow`) was NOT including token usage information in its response, even though `run_workflow()` provided this data.

**Status**: ✅ **FIXED** - Added missing fields to response

### All Workflow Execution Paths Verified

#### 1. Template-Based Workflow Execution ✅

**Endpoints**:
- `POST /api/v1/workflows/templates/{template_id}/execute`
- `POST /api/v1/workflows/templates/execute`

**Flow**:
```
execute_workflow_template()
  → execute_workflow_definition()
    → run_workflow()  # Returns aggregated fields
  → saves to WorkflowExecution with tokens_used and cost
  → returns WorkflowExecutionResponse (includes token fields)
```

**Verification**: ✅ Uses `result.get("tokens_used", 0)` and `result.get("cost", 0.0)`

#### 2. Definition-Based Workflow Execution ✅

**Endpoint**: `POST /api/v1/workflows/definitions/{workflow_id}/execute`

**Flow**:
```
execute_workflow()
  → execute_workflow_definition()
    → run_workflow()  # Returns aggregated fields
  → saves to WorkflowExecution with tokens_used and cost
  → returns WorkflowExecutionResponse (includes token fields)
```

**Verification**: ✅ Uses `result.get("tokens_used", 0)` and `result.get("cost", 0.0)`

#### 3. Custom Workflow Execution ✅ (FIXED)

**Endpoint**: `POST /api/v1/workflows/definitions/custom/execute`

**Flow**:
```
execute_custom_workflow()
  → run_workflow()  # Returns aggregated fields
  → returns dict with execution summary
```

**Before Fix**: ❌ Response did NOT include token usage information

**After Fix**: ✅ Response includes:
```python
{
    "response": "...",
    "metadata": {...},
    "execution_summary": {...},
    "tokens_used": result.get("tokens_used", 0),      # ← ADDED
    "prompt_tokens": result.get("prompt_tokens", 0),   # ← ADDED
    "completion_tokens": result.get("completion_tokens", 0),  # ← ADDED
    "cost": result.get("cost", 0.0),                   # ← ADDED
}
```

#### 4. Chat Workflow Execution ✅

**Endpoints**:
- `POST /api/v1/workflows/execute/chat`
- `POST /api/v1/workflows/execute/chat/streaming`

**Flow**:
```
execute_chat_workflow()
  → _execute_chat_workflow_internal()
    → _execute_with_universal_template() or _execute_with_dynamic_workflow()
      → run_workflow()  # Returns aggregated fields
      → extracts result.get("prompt_tokens"), etc.
      → creates Message with token info
      → saves to database
  → returns ChatResponse with MessageResponse (includes token fields)
```

**Verification**: ✅ Uses aggregated fields from `run_workflow()` result

**Streaming Verification**: ✅ Extracts `usage_metadata` from LLM streaming events (on_chat_model_end), which is correct for real-time token reporting

### Streaming vs Non-Streaming

#### Non-Streaming (All Endpoints Above)
- Uses **aggregated fields** from `run_workflow()` result
- Gets total tokens across all workflow nodes
- Correct ✅

#### Streaming (Chat Streaming Only)  
- Extracts `usage_metadata` from **LLM event data** (`on_chat_model_end`)
- Provides real-time per-LLM-call token information
- Does NOT use workflow result (workflow hasn't completed yet)
- Correct ✅

## Changes Made

### 1. Bug Fix: Custom Workflow Endpoint

**File**: `chatter/api/workflows.py`

**Change**: Added usage fields to response

```python
# Added to execute_custom_workflow() return value:
"tokens_used": result.get("tokens_used", 0),
"prompt_tokens": result.get("prompt_tokens", 0),
"completion_tokens": result.get("completion_tokens", 0),
"cost": result.get("cost", 0.0),
```

### 2. Enhanced Documentation

**File**: `chatter/core/langgraph.py`

**Change**: Added comprehensive docstring to `run_workflow()` method explaining:
- How usage_metadata flows through the system
- What fields are returned and their meaning
- Guidance that consumers should use aggregated fields

### 3. New Test Suite

**File**: `tests/test_workflow_usage_metadata_flow.py`

**Tests Added**:
1. `test_run_workflow_returns_aggregated_usage_fields` - Verifies aggregated fields present
2. `test_workflow_result_separates_aggregated_from_node_metadata` - Verifies both exist
3. `test_workflow_without_usage_metadata` - Verifies zero token behavior
4. `test_alternative_token_field_names` - Verifies field name flexibility
5. `test_duplicate_usage_metadata_not_aggregated` - Verifies deduplication

### 4. Architecture Documentation

**File**: `WORKFLOW_USAGE_METADATA_FLOW.md`

**Contents**:
- Complete data flow diagram
- Explanation of aggregation logic
- Streaming vs non-streaming patterns
- Best practices for developers
- Current consumer verification

## Validation Results

### Automated Validation

Created validation script (`/tmp/validate_usage_metadata.py`) that checks:
- ✅ No code incorrectly uses raw `usage_metadata` from workflow results for totals
- ✅ All non-streaming code uses aggregated fields
- ✅ Streaming code correctly uses LLM event metadata

**Result**: All files validated successfully! No issues found.

### Manual Code Review

Reviewed all workflow execution paths:
- ✅ Template execution: Uses aggregated fields
- ✅ Definition execution: Uses aggregated fields  
- ✅ Custom workflow: NOW uses aggregated fields (fixed)
- ✅ Chat workflow: Uses aggregated fields
- ✅ Streaming: Uses LLM event metadata (correct)

## Conclusion

### Summary

✅ **All workflow execution paths now correctly use usage information from the proper source:**

1. **`run_workflow()` is the authoritative source** - It aggregates tokens from all nodes
2. **Consumers use aggregated top-level fields** - `tokens_used`, `prompt_tokens`, `completion_tokens`, `cost`
3. **Bug fixed** - Custom workflow endpoint now includes usage information
4. **Streaming is correct** - Uses real-time LLM event metadata, not workflow result
5. **Documentation added** - Clear guidance for future development

### Files Changed

- `chatter/api/workflows.py` - Fixed custom workflow endpoint
- `chatter/core/langgraph.py` - Enhanced documentation
- `tests/test_workflow_usage_metadata_flow.py` - New comprehensive tests
- `WORKFLOW_USAGE_METADATA_FLOW.md` - Architecture documentation

### Impact

- ✅ Custom workflows now report token usage and cost
- ✅ Consistent usage metadata across all workflow types
- ✅ Clear documentation prevents future errors
- ✅ Tests ensure continued correctness

## No Further Action Required

All workflow execution results are getting usage information from the correct source (`run_workflow()` aggregated fields). The system is working as designed with one bug fixed.
