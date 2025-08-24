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
  DocumentsApi,
  ProfilesApi,
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
    
    const conversations = await conversationsApi.apiV1ConversationsGet();
    console.log('Conversations:', conversations.data);
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

## API Coverage

This SDK provides TypeScript interfaces and API clients for all Chatter endpoints:

- **Authentication**: Login, register, user management
- **Conversations**: Create, manage, and interact with conversations
- **Documents**: Upload, search, and manage documents
- **Profiles**: Configure LLM profiles and settings
- **Prompts**: Manage prompt templates
- **Agents**: AI agent configuration and management
- **Tool Servers**: MCP tool server integration
- **Analytics**: Usage statistics and metrics
- **Health**: System health monitoring

## Configuration

The SDK uses the `Configuration` class to manage API settings:

```typescript
import { Configuration } from './sdk';

const config = new Configuration({
  basePath: 'http://localhost:8000',  // API base URL
  accessToken: () => localStorage.getItem('auth_token'),  // Token provider function
  // Additional axios configuration can be passed here
});
```

## Error Handling

All API methods return promises that can be handled with try/catch:

```typescript
import { AuthenticationApi } from './sdk';

const authApi = new AuthenticationApi(config);

try {
  const response = await authApi.apiV1AuthLoginPost({
    email: 'user@example.com',
    password: 'password123'
  });
  
  console.log('Login successful:', response.data);
} catch (error) {
  if (error.response?.status === 401) {
    console.error('Invalid credentials');
  } else {
    console.error('Login error:', error.message);
  }
}
```

## Generated Files

This SDK contains the following generated files:

- `api.ts` or `api/` - API client classes
- `models.ts` or `models/` - TypeScript interfaces for all data models
- `configuration.ts` - Configuration management
- `base.ts` - Base API class with common functionality
- `index.ts` - Main export file

## Regeneration

This SDK is automatically generated from the OpenAPI specification. To regenerate:

```bash
cd /path/to/chatter
python scripts/generate_ts.py
```

Or use the combined workflow:

```bash
python scripts/generate_all.py
```

## Development

The SDK is generated as part of the development workflow and should not be manually edited. All changes should be made to the backend API and OpenAPI specification, then the SDK should be regenerated.
