# API Key Authentication

API keys provide a simple and secure way to authenticate API requests without requiring JWT tokens. This is particularly useful for server-to-server communication, CLI tools, and long-running applications.

## Overview

Starting with this update, API keys can be used directly for authentication with any protected endpoint. Previously, you needed to:
1. Authenticate with username/password to get a JWT token
2. Use the JWT token to create an API key
3. Continue using JWT tokens for subsequent requests

Now, once you have an API key, you can use it directly without needing JWT tokens.

## Creating an API Key

First, you need to authenticate with your username/password to create an API key:

```bash
# Step 1: Login to get a JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'

# Response includes access_token
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "user": {...}
# }

# Step 2: Create an API key using the JWT token
curl -X POST http://localhost:8000/api/v1/auth/api-key \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "My API Key"
  }'

# Response includes the API key (save this - it's only shown once!)
# {
#   "id": "01234567-89ab-cdef-0123-456789abcdef",
#   "api_key": "sk_live_abcdef123456...",
#   "api_key_name": "My API Key"
# }
```

## Using API Keys for Authentication

Once you have an API key, you can use it directly in the `Authorization` header with the `Bearer` scheme, just like JWT tokens:

```bash
# Use the API key to access protected endpoints
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_API_KEY"

# Access other protected endpoints
curl -X GET http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer YOUR_API_KEY"

# Upload documents
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@document.pdf"
```

## API Key vs JWT Token Authentication

Both authentication methods work the same way from an API perspective:

| Feature | JWT Token | API Key |
|---------|-----------|---------|
| **Header Format** | `Authorization: Bearer <token>` | `Authorization: Bearer <api_key>` |
| **Expiration** | Yes (configurable, typically 15-60 minutes) | No (valid until revoked) |
| **Use Case** | User sessions, short-lived access | Server-to-server, CLI tools, long-running apps |
| **Creation** | Generated at login | Created via API endpoint |
| **Revocation** | Automatic on logout/expiration | Manual via API endpoint |

## Security Best Practices

1. **Treat API keys like passwords**: Never commit them to version control or share them publicly
2. **Use environment variables**: Store API keys in environment variables, not in code
3. **Rotate regularly**: Periodically revoke old API keys and create new ones
4. **One key per application**: Create separate API keys for different applications/services
5. **Revoke unused keys**: Delete API keys that are no longer needed

## Managing API Keys

### List Your API Keys

```bash
curl -X GET http://localhost:8000/api/v1/auth/api-keys \
  -H "Authorization: Bearer YOUR_API_KEY_OR_JWT_TOKEN"
```

### Revoke an API Key

```bash
curl -X DELETE http://localhost:8000/api/v1/auth/api-key \
  -H "Authorization: Bearer YOUR_API_KEY_OR_JWT_TOKEN"
```

Note: Currently, users can have one API key at a time. Revoking your API key will require you to authenticate with username/password to create a new one.

## Example: Python SDK

```python
from chatter_sdk import Configuration, ApiClient, AuthenticationApi

# Configure API key authentication
configuration = Configuration(
    host="http://localhost:8000"
)
configuration.access_token = "YOUR_API_KEY"

# Use the API
async with ApiClient(configuration) as api_client:
    auth_api = AuthenticationApi(api_client)
    
    # Get current user info
    user = await auth_api.getCurrentUserInfoApiV1AuthMe()
    print(f"Authenticated as: {user.username}")
```

## Example: JavaScript/TypeScript SDK

```typescript
import { Configuration, AuthenticationApi } from '@chatter/sdk';

// Configure API key authentication
const config = new Configuration({
  basePath: 'http://localhost:8000',
  accessToken: 'YOUR_API_KEY'
});

// Use the API
const authApi = new AuthenticationApi(config);

// Get current user info
const user = await authApi.getCurrentUserInfoApiV1AuthMe();
console.log(`Authenticated as: ${user.username}`);
```

## Troubleshooting

### "Invalid token or API key" Error

This error occurs when:
- The API key has been revoked
- The API key is malformed or incorrect
- The user account has been deactivated

**Solution**: Create a new API key by logging in with username/password.

### API Key Not Working Immediately After Creation

API keys should work immediately after creation. If you're experiencing issues:
- Verify you're using the correct API key (copy the entire value)
- Check that the API key wasn't accidentally truncated
- Ensure you're using the `Bearer` scheme in the Authorization header

## Migration Guide

If you have existing code using only JWT tokens, no changes are required. JWT token authentication continues to work as before. To add API key support:

1. Create an API key for your application
2. Replace JWT token refresh logic with API key authentication
3. Store the API key securely (environment variables, secrets manager, etc.)
4. Update your API calls to use the API key instead of JWT tokens

Your existing endpoints and authentication logic remain unchanged - API keys and JWT tokens work interchangeably.
