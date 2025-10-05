# Fix Summary: API Key Verification Issue

## Problem Statement

Users were experiencing authentication failures when using API keys with the error:

```
Token verification failed: Not enough segments
HTTP 401 Unauthorized
detail: "Invalid token or API key"
```

From the error log:
```
'authorization': 'Bearer $2b$12$znG96z4WOna0fQgPIuPqIuec5oqXBMCbnGV2T6GgPxqRmq0rPfH.C'
```

## Root Cause

Users were sending a **bcrypt hash** (the value stored in the database) instead of the **plaintext API key** (which is only shown once during creation).

The bcrypt hash format starts with `$2a$`, `$2b$`, or `$2y$`, which:
1. Is not a valid JWT token (causes "Not enough segments" error)
2. Cannot be verified as an API key (it's already hashed)
3. Resulted in a generic error message that didn't help users understand the issue

## Solution

### 1. Early Detection in Authentication (chatter/core/auth.py)

Added bcrypt hash detection at the start of `get_current_user()`:

```python
# Detect if someone is mistakenly using a bcrypt hash as the API key
if token.startswith("$2a$") or token.startswith("$2b$") or token.startswith("$2y$"):
    logger.error(
        "Authentication failed: bcrypt hash provided instead of API key",
        hash_prefix=token[:15]
    )
    raise AuthenticationError(
        "Invalid API key format. You appear to be using a hashed API key instead of the plaintext key. "
        "The plaintext API key is only shown once during creation. "
        "Please revoke the old key and create a new one."
    ) from None
```

**Impact**: Users now get a clear, actionable error message explaining exactly what went wrong and how to fix it.

### 2. Secondary Detection in Verification (chatter/utils/security_enhanced.py)

Added bcrypt hash detection in `verify_api_key_secure()`:

```python
# Detect if someone is mistakenly passing a bcrypt hash as the plaintext key
if plain_key.startswith("$2a$") or plain_key.startswith("$2b$") or plain_key.startswith("$2y$"):
    logger.warning(
        "API key verification failed: bcrypt hash provided instead of plaintext key. "
        "The plaintext API key is only shown once during creation. "
        "If you lost it, revoke the old key and create a new one.",
        key_prefix=plain_key[:15]
    )
    return False
```

**Impact**: Prevents wasted verification attempts and provides helpful logging.

### 3. Fixed Hash Exposure in list_api_keys (chatter/core/auth.py)

**Before**: The method was exposing parts of the bcrypt hash:
```python
masked_key = user.api_key[:8] + "..." + user.api_key[-4:]
```

**After**: Never expose any part of the hash:
```python
# NOTE: user.api_key contains the HASHED key, not the plaintext key!
# The plaintext key is only returned once during creation.
# We should NEVER expose any part of the bcrypt hash.
api_keys.append({
    "id": user.id,
    "api_key": "••••••••",  # Never expose the hash or plaintext
    "api_key_name": user.api_key_name,
})
```

**Impact**: Prevents users from accidentally copying parts of the hash.

## Testing

### New Tests Added (tests/test_auth_unit.py)

1. **test_bcrypt_hash_detection**: Verifies that bcrypt hashes are detected and rejected with helpful error messages
2. **test_verify_api_key_secure_detects_hash**: Tests all bcrypt hash formats ($2a$, $2b$, $2y$)

### Manual Testing

Created comprehensive manual tests that verify:
- ✅ Bcrypt hash patterns are correctly detected
- ✅ Valid API keys are not falsely flagged
- ✅ Error messages are helpful and actionable

All tests pass successfully.

## User Experience Improvement

### Before the Fix
```
HTTP 401 Unauthorized
{
  "detail": "Invalid token or API key"
}
```
- Users had no idea what was wrong
- No guidance on how to fix it
- Could lead to security issues if users start sharing database values

### After the Fix
```
HTTP 401 Unauthorized
{
  "detail": "Invalid API key format. You appear to be using a hashed API key instead of the plaintext key. 
            The plaintext API key is only shown once during creation. 
            Please revoke the old key and create a new one."
}
```
- Clear explanation of the problem
- Explains why it happened
- Provides actionable steps to resolve it

## How Users Got the Hash

Users could have obtained the bcrypt hash through:
1. **Direct database access** - Reading the `api_key` column
2. **Previous bug in list endpoint** - Exposed parts of the hash
3. **Saved wrong value during creation** - Confusion during initial setup

## Prevention

The fix prevents this issue through:
1. **Early detection** - Catches the error before any processing
2. **Clear error messages** - Educates users on correct usage
3. **No hash exposure** - list_api_keys never shows the hash
4. **Comprehensive logging** - Helps identify the issue in logs

## Files Changed

1. `chatter/core/auth.py` - Added hash detection in `get_current_user`, fixed `list_api_keys`
2. `chatter/utils/security_enhanced.py` - Added hash detection in `verify_api_key_secure`
3. `tests/test_auth_unit.py` - Added comprehensive tests
4. `API_KEY_HASH_FIX.md` - Detailed documentation

## Migration Guide for Users

If you're experiencing this issue:

1. **Don't try to use the database hash** - It won't work
2. **Revoke your current API key**:
   ```bash
   curl -X DELETE http://localhost:8000/api/v1/auth/api-key \
     -H "Authorization: Bearer <your-jwt-token>"
   ```
3. **Create a new API key**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/api-key \
     -H "Authorization: Bearer <your-jwt-token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "My API Key"}'
   ```
4. **Save the plaintext key immediately** - It's only shown once!
5. **Use the plaintext key** for authentication:
   ```bash
   curl -X GET http://localhost:8000/api/v1/auth/me \
     -H "Authorization: Bearer chatter_api_1234567890_abc123_xyz789"
   ```

## Security Impact

✅ **Positive**: The fix actually improves security by:
- Not exposing any part of the bcrypt hash
- Educating users on proper API key handling
- Preventing confusion that could lead to security issues

❌ **No Breaking Changes**: 
- Valid API keys continue to work exactly as before
- JWT tokens continue to work exactly as before
- Only invalid usage (bcrypt hashes) is now properly rejected

## Conclusion

This fix resolves the authentication issue by:
1. ✅ Detecting when users mistakenly use bcrypt hashes
2. ✅ Providing clear, actionable error messages
3. ✅ Preventing hash exposure in API responses
4. ✅ Maintaining backward compatibility
5. ✅ Improving overall security posture

The solution is minimal, focused, and directly addresses the root cause while improving the user experience.
