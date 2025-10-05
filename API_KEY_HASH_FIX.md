# API Key Hash Detection Fix

## Problem

Users were experiencing authentication failures with the error:
```
Token verification failed: Not enough segments
Invalid token or API key
```

### Root Cause

The issue occurred when users mistakenly used a **bcrypt hash** (stored in the database) as their API key instead of the **plaintext API key** (which is only shown once during creation).

Example of a bcrypt hash:
```
$2b$12$znG96z4WOna0fQgPIuPqIuec5oqXBMCbnGV2T6GgPxqRmq0rPfH.C
```

When this hash was sent as `Authorization: Bearer <hash>`, the system would:
1. First try to parse it as a JWT token
2. Fail with "Not enough segments" (JWT tokens have 3 segments separated by dots)
3. Try to use it as an API key
4. Fail silently without a helpful error message

## Solution

Added detection and validation at multiple levels:

### 1. Early Detection in `get_current_user` (chatter/core/auth.py)

Added a check at the beginning of authentication to detect bcrypt hashes:

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

### 2. Detection in `verify_api_key_secure` (chatter/utils/security_enhanced.py)

Added a check to prevent bcrypt hashes from being compared:

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

### 3. Fixed `list_api_keys` to Never Expose Hash (chatter/core/auth.py)

The previous implementation was trying to "mask" the bcrypt hash, which could leak parts of it:

**Before:**
```python
masked_key = (
    user.api_key[:8] + "..." + user.api_key[-4:]  # Exposing parts of the hash!
    if len(user.api_key) > 12
    else "***"
)
```

**After:**
```python
# NOTE: user.api_key contains the HASHED key (bcrypt hash), not the plaintext key!
# The plaintext key is only returned once during creation.
# We should NEVER expose any part of the bcrypt hash.
api_keys.append({
    "id": user.id,
    "api_key": "••••••••",  # Never expose the hash or plaintext
    "api_key_name": user.api_key_name,
})
```

## How Users Got the Hash

Users could have obtained the bcrypt hash in several ways:
1. **Direct database access** - Reading the `api_key` column from the `users` table
2. **Previous bug in list endpoint** - The old `list_api_keys` was exposing parts of the hash
3. **Saved the wrong value** - Accidentally saved the hash instead of the plaintext during key creation

## User Experience Improvement

### Before
```
HTTP 401 Unauthorized
detail: "Invalid token or API key"
```

Users had no idea what was wrong.

### After
```
HTTP 401 Unauthorized
detail: "Invalid API key format. You appear to be using a hashed API key instead of the plaintext key. 
        The plaintext API key is only shown once during creation. 
        Please revoke the old key and create a new one."
```

Clear, actionable error message that tells users exactly what to do.

## Testing

Added comprehensive tests in `tests/test_auth_unit.py`:

1. **test_bcrypt_hash_detection** - Verifies that bcrypt hashes are detected and rejected with a helpful error message
2. **test_verify_api_key_secure_detects_hash** - Tests that all bcrypt hash formats ($2a$, $2b$, $2y$) are detected

## Important Notes for Users

### API Key Security Best Practices

1. **Save the plaintext API key immediately** when it's created - it's only shown once!
2. **Never use the database hash** as your API key
3. **If you lose your API key**, revoke it and create a new one:
   ```bash
   # Revoke old key
   curl -X DELETE http://localhost:8000/api/v1/auth/api-key \
     -H "Authorization: Bearer <your-jwt-token>"
   
   # Create new key
   curl -X POST http://localhost:8000/api/v1/auth/api-key \
     -H "Authorization: Bearer <your-jwt-token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "My New API Key"}'
   ```

### How API Keys Work

1. **Creation**: When you create an API key, the system generates a plaintext key (e.g., `chatter_api_1234567890_abc123_xyz789`)
2. **Storage**: The plaintext key is hashed with bcrypt and stored in the database
3. **Return**: The plaintext key is returned **once** in the API response
4. **Authentication**: When you authenticate, you send the plaintext key, and it's verified against the stored hash
5. **Never**: The plaintext key is never stored or retrievable after creation

## Files Changed

- `chatter/core/auth.py` - Added hash detection in `get_current_user` and fixed `list_api_keys`
- `chatter/utils/security_enhanced.py` - Added hash detection in `verify_api_key_secure`
- `tests/test_auth_unit.py` - Added tests for hash detection
- `API_KEY_HASH_FIX.md` - This documentation
