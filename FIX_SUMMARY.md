# Fix Summary: Provider 'None' not found or inactive Error

## Problem
The chat API was failing with the error:
```
Provider 'None' not found or inactive
```

This occurred when chat requests were made without specifying a provider, causing the `ChatRequest.provider` field to be `None`, which was then passed to the LLM service that tried to find a provider literally named "None".

## Root Cause Analysis
1. **ChatRequest Schema**: The `provider` field is optional (`str | None`) with default `None`
2. **Workflow Execution**: Workflow executors pass `chat_request.provider` directly to LLM service methods
3. **LLM Service**: Methods expected non-null provider names and tried to find a provider named "None"
4. **Missing Fallback**: No mechanism to use default provider when None was provided

## Solution Implementation

### 1. Updated LLM Service Method Signatures
- Changed `create_langgraph_workflow(provider_name: str, ...)` to `create_langgraph_workflow(provider_name: str | None, ...)`
- Changed `generate(provider: str, ...)` to `generate(provider: str | None, ...)`

### 2. Added Fallback Logic
In both methods, added logic to use default provider when provider is None or empty:
```python
if provider_name is None or provider_name == "":
    provider = await self.get_default_provider()
else:
    provider = await self.get_provider(provider_name)
```

### 3. Fixed Method Call in Workflow Execution
- Replaced non-existent `generate_completion()` call with correct `generate()` method
- Set provider to `None` to trigger default provider usage

### 4. Comprehensive Edge Case Handling
- Handles both `None` and empty string `""` providers
- Graceful fallback to default provider
- Maintains existing functionality for explicitly specified providers

## Testing
- Created comprehensive validation tests
- Confirmed method signature changes
- Verified fallback logic works correctly
- Integration tests pass successfully

## Impact
- ✅ Chat requests without provider specification now work
- ✅ Existing functionality with explicit providers unchanged
- ✅ Better error messages when no default provider is configured
- ✅ Robust handling of edge cases (None, empty string)

## Files Modified
1. `chatter/services/llm.py` - Added None provider handling
2. `chatter/services/workflow_execution.py` - Fixed method call

The fix ensures the system gracefully falls back to using the configured default provider when no provider is specified in chat requests, eliminating the confusing "Provider 'None' not found" error.