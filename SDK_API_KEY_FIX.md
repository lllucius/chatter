# SDK API Key Authentication Fix

## Issue Summary

When using the Chatter Python SDK with an API key, authentication was failing with the following error:

```
AuthenticationError: Authentication credentials required
```

The log messages showed:
```
error_code=AUTHENTICATION_ERROR
status_code=401
www-authenticate: Bearer
```

## Root Cause

The SDK example code (`examples/sdk_temporary_template_example.py`) was incorrectly configuring the API key authentication using:

```python
configuration = Configuration(
    host=base_url,
    api_key={"HTTPBearer": api_key}  # INCORRECT
)
```

However, the `Configuration.auth_settings()` method only checks for the `access_token` parameter, not the `api_key` dictionary. The `api_key` parameter is designed for API key authentication schemes (where the key is passed in a query parameter or custom header), not for Bearer token authentication.

## Solution

The fix is simple: use the `access_token` parameter instead of the `api_key` parameter:

```python
configuration = Configuration(
    host=base_url,
    access_token=api_key  # CORRECT
)
```

This is consistent with the documentation in `docs/API_KEY_AUTHENTICATION.md`, which shows:

```python
configuration = Configuration(
    host="http://localhost:8000"
)
configuration.access_token = "YOUR_API_KEY"
```

## Changes Made

1. **Fixed SDK Example** (`examples/sdk_temporary_template_example.py`):
   - Changed `api_key={"HTTPBearer": api_key}` to `access_token=api_key`

2. **Fixed Documentation** (`EXAMPLES_IMPLEMENTATION_SUMMARY.md`):
   - Updated the code example to use `access_token` instead of `api_key`

3. **Added Test** (`tests/test_sdk_configuration.py`):
   - Created comprehensive tests to verify the correct configuration
   - Documents that `access_token` is the correct parameter
   - Shows that `api_key` dict does not work for bearer authentication

## How It Works

When `access_token` is set in the Configuration:

1. The `Configuration.auth_settings()` method returns:
   ```python
   {
       'CustomHTTPBearer': {
           'type': 'bearer',
           'in': 'header',
           'key': 'Authorization',
           'value': 'Bearer YOUR_API_KEY'
       }
   }
   ```

2. The `ApiClient._apply_auth_params()` method uses this to add the Authorization header:
   ```
   Authorization: Bearer YOUR_API_KEY
   ```

3. The API server validates the API key in the Authorization header and grants access.

## Verification

The fix has been verified by:
- Running the test suite (`tests/test_sdk_configuration.py`)
- Confirming the auth_settings are correctly generated
- Verifying consistency with the official documentation

## Impact

This is a minimal change that only affects:
- One example file
- One documentation file
- Adds one new test file

No changes to the SDK library itself were needed, as the functionality was already correct. Only the usage examples were incorrect.
