# SDK Generation with Datetime Serialization Fix

## Overview

The Python SDK generator now automatically applies the datetime serialization fix when generating models from the OpenAPI specification. This ensures that all generated models properly serialize datetime objects to JSON-compatible strings.

## Automatic Fix

When you regenerate the Python SDK using the generation script, the following fix is automatically applied to all model files:

### What Gets Fixed

The generator identifies model files that:
1. Import `datetime` 
2. Have `to_dict()` methods
3. Use `model_dump()` calls

For these files, it automatically adds `mode='json'` to `model_dump()` calls:

```python
# Before (generated code)
_dict = self.model_dump(
    by_alias=True,
    exclude=excluded_fields,
    exclude_none=True,
)

# After (automatically fixed)
_dict = self.model_dump(
    by_alias=True,
    exclude=excluded_fields,
    exclude_none=True,
    mode='json',
)
```

## How to Regenerate the SDK

To regenerate the Python SDK with the datetime fix:

```bash
# Regenerate Python SDK only
python scripts/generate_sdks.py --python

# Regenerate both Python and TypeScript SDKs
python scripts/generate_sdks.py --all

# Regenerate with verbose output
python scripts/generate_sdks.py --python --verbose
```

## Verification

After regeneration, you can verify the fix was applied by:

1. **Check the console output** - Look for the message:
   ```
   ✅ Applied datetime serialization fix
   📝 Processed X model files, applied datetime fix to Y files
   ```

2. **Manually verify** - Check any model file with datetime fields:
   ```bash
   grep -A 10 "mode='json'" sdk/python/chatter_sdk/models/chat_response.py
   ```

3. **Run tests** - The comprehensive test suite validates the fix:
   ```bash
   python -m pytest tests/test_chat_response_datetime_fix.py -v
   ```

## Implementation Details

The automatic fix is implemented in `scripts/sdk/python_sdk.py`:

- **Post-processing step**: Applied after OpenAPI generation but before validation
- **Smart detection**: Only modifies files that need the fix
- **Safe operation**: Preserves existing `mode='json'` parameters
- **Pattern matching**: Uses regex to identify and fix `model_dump()` calls

## Files Affected

The fix typically applies to models with datetime fields, such as:

- `ChatResponse`
- `MessageResponse` 
- `ConversationResponse`
- `DashboardResponse`
- `JobResponse`
- And other models with `created_at`, `updated_at`, or similar datetime fields

## Troubleshooting

If the automatic fix fails:

1. **Check the error messages** in the console output
2. **Verify file permissions** on the SDK output directory
3. **Run with verbose output** to see detailed processing information
4. **Manually apply the fix** if needed using the patterns shown above

## Future Maintenance

This fix is automatically applied every time the SDK is regenerated, so:

- ✅ **No manual intervention needed** after OpenAPI spec changes
- ✅ **Consistent datetime handling** across all generated models  
- ✅ **No risk of regression** when regenerating the SDK
- ✅ **Backward compatible** with existing model usage