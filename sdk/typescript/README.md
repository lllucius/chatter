# Chatter TypeScript SDK

TypeScript SDK for Chatter AI Chatbot API

## Installation

Since this is a local SDK generated from the OpenAPI specification, it's automatically available in your frontend application.

## Usage

```typescript
import {
  Configuration,
  AuthenticationApi,
  ConversationsApi,
  // ... other APIs
} from './sdk';

// Create configuration
const config = new Configuration({
  basePath: 'http://localhost:8000',
  accessToken: () => your_token_here,
});

// Create API instances
const authApi = new AuthenticationApi(config);
const conversationsApi = new ConversationsApi(config);

// Use the APIs
async function example() {
  try {
    const user = await authApi.apiV1AuthMeGet();
    console.log('Current user:', user.data);
  } catch (error) {
    console.error('API error:', error);
  }
}
```

## Features

- **Type Safety**: Full TypeScript support with generated interfaces
- **Axios-based**: Uses Axios HTTP client for all requests
- **OpenAPI Generated**: Automatically generated from the OpenAPI specification
- **Authentication**: Built-in support for JWT token authentication
- **Error Handling**: Proper error handling with typed responses

## Configuration

The SDK uses the `Configuration` class to manage API settings:

```typescript
import { Configuration } from './sdk';

const config = new Configuration({
  basePath: 'http://localhost:8000',  // API base URL
  accessToken: () => localStorage.getItem('auth_token'),  // Token provider function
});
```

## Regeneration

This SDK is automatically generated from the OpenAPI specification. To regenerate:

```bash
cd /path/to/chatter
python -m scripts.sdk.typescript_sdk
```

Or use the combined workflow:

```bash
python scripts/generate_all.py
```

## Development

The SDK is generated as part of the development workflow and should not be manually edited. All changes should be made to the backend API and OpenAPI specification, then the SDK should be regenerated.
