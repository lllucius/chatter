# ChatResponse DateTime Serialization Fix

## Issue Description

The Python SDK's `ChatResponse.to_json()` method was failing with a `TypeError: Object of type datetime is not JSON serializable` error when trying to serialize responses containing datetime fields.

## Root Cause

The issue occurred in the `to_dict()` methods of the following SDK models:
- `ChatResponse`
- `MessageResponse` 
- `ConversationResponse`
- And several other models with datetime fields

These methods used `model_dump(exclude_none=True)` without the `mode='json'` parameter, which caused datetime objects to remain as Python datetime objects instead of being converted to JSON-serializable strings.

When `ChatResponse.to_dict()` called the nested objects' `to_dict()` methods, the datetime objects remained unconverted, causing JSON serialization to fail.

## Fix Applied

Added the `mode='json'` parameter to all `model_dump()` calls in the affected models:

```python
# Before (broken)
_dict = self.model_dump(
    by_alias=True,
    exclude=excluded_fields,
    exclude_none=True,
)

# After (fixed)
_dict = self.model_dump(
    by_alias=True,
    exclude=excluded_fields,
    exclude_none=True,
    mode='json',  # This ensures datetime objects are converted to strings
)
```

## Files Modified

- `sdk/python/chatter_sdk/models/chat_response.py`
- `sdk/python/chatter_sdk/models/message_response.py`
- `sdk/python/chatter_sdk/models/conversation_response.py`
- `sdk/python/chatter_sdk/models/dashboard_response.py`
- `sdk/python/chatter_sdk/models/ab_test_analytics_response.py`
- `sdk/python/chatter_sdk/models/embedding_space_with_model.py`
- `sdk/python/chatter_sdk/models/job_response.py`
- `sdk/python/chatter_sdk/models/model_def_with_provider.py`
- `sdk/python/chatter_sdk/models/tool_server_response.py`
- `sdk/python/chatter_sdk/models/workflow_analytics_response.py`

## Testing

Added comprehensive tests in `tests/test_chat_response_datetime_fix.py` that:

1. Reproduce the original issue (datetime objects not being serialized)
2. Validate the fix (datetime objects converted to ISO format strings)
3. Test full JSON serialization and round-trip conversion
4. Ensure all nested datetime fields are properly handled

## Before and After

### Before (Broken)
```python
# This would fail with "Object of type datetime is not JSON serializable"
chat_response = ChatResponse(...)
json_str = chat_response.to_json()  # ❌ TypeError
```

### After (Fixed)
```python
# This now works correctly
chat_response = ChatResponse(...)
json_str = chat_response.to_json()  # ✅ Success

# Datetime fields are properly serialized
parsed = json.loads(json_str)
print(parsed['message']['created_at'])  # "2025-09-17T04:51:42.905505"
```

## Impact

This fix resolves the JSON serialization issue for all ChatResponse objects and ensures datetime fields are consistently serialized as ISO format strings across the SDK.