# Chatter TypeScript SDK

A complete, hand-crafted TypeScript SDK for the Chatter API with full type safety and comprehensive coverage of all endpoints.

## Features

- 🎯 **100% Type Safe** - Hand-crafted TypeScript interfaces for all 216+ data models
- 🚀 **Complete API Coverage** - All 147 endpoints across 17 service areas
- 🔧 **Zero Dependencies** - Built with native Fetch API, no external dependencies
- 🛡️ **Robust Error Handling** - Comprehensive error types and handling
- 🔌 **Middleware Support** - Extensible middleware system for custom logic
- 🔐 **Flexible Authentication** - Bearer tokens, API keys, and custom auth
- 📦 **Modern JavaScript** - ES2020+ with CommonJS and ESM builds
- 🎨 **Clean API** - Intuitive method names and organized structure

## Installation

```bash
npm install @chatter/sdk-ts
# or
yarn add @chatter/sdk-ts
# or
pnpm add @chatter/sdk-ts
```

## Quick Start

```typescript
import { ChatterSDK } from '@chatter/sdk-ts';

// Initialize the SDK
const chatter = new ChatterSDK({
  basePath: 'https://api.chatter.example.com',
  bearerToken: 'your-bearer-token'
});

// Start chatting
const response = await chatter.chat.chatChat({
  message: 'Hello, how are you?',
  workflow: 'plain'
});

console.log(response.message.content);
```

## API Structure

The SDK is organized into logical service areas:

```typescript
const chatter = new ChatterSDK();

// Authentication & Users
await chatter.auth.login({ username: 'user', password: 'pass' });
await chatter.auth.logout();

// Chat & Conversations
await chatter.chat.chatChat({ message: 'Hello!', workflow: 'rag' });
await chatter.chat.listConversations();
await chatter.chat.getConversation('conv-id');

// Document Management
await chatter.documents.uploadDocument(formData);
await chatter.documents.listDocuments();
await chatter.documents.searchDocuments({ query: 'AI' });

// AI Agents
await chatter.agents.createAgent({ name: 'Assistant', type: 'chat' });
await chatter.agents.listAgents();
await chatter.agents.interactWithAgent('agent-id', { message: 'Hi!' });

// Workflows & Automation
await chatter.workflows.createDefinition({ name: 'My Workflow' });
await chatter.workflows.executeWorkflow('workflow-id', { input: 'data' });

// Model & Provider Management
await chatter.models.listModels();
await chatter.models.createProvider({ name: 'OpenAI', type: 'openai' });

// Analytics & Monitoring
await chatter.analytics.getDashboard();
await chatter.analytics.getUsageMetrics();

// And much more...
```

## Configuration

### Basic Configuration

```typescript
const chatter = new ChatterSDK({
  basePath: 'https://your-api.com',
  bearerToken: 'your-token',
  headers: {
    'X-Custom-Header': 'value'
  }
});
```

### Authentication

```typescript
// Bearer token
const chatter = new ChatterSDK({
  bearerToken: 'your-bearer-token'
});

// API Key
const chatter = new ChatterSDK({
  apiKey: 'your-api-key'
});

// Dynamic authentication
const authenticatedChatter = chatter.withAuth('new-token', 'bearer');
```

### Middleware

```typescript
import { ChatterSDK, Middleware } from '@chatter/sdk-ts';

// Custom logging middleware
const loggingMiddleware: Middleware = {
  pre: async (context) => {
    console.log('Request:', context.url);
    return context;
  },
  post: async (context) => {
    console.log('Response:', context.response.status);
    return context;
  }
};

const chatter = new ChatterSDK({
  middleware: [loggingMiddleware]
});

// Or add middleware to existing instance
const withLogging = chatter.withMiddleware(loggingMiddleware);
```

## Error Handling

The SDK provides comprehensive error handling with typed error objects:

```typescript
import { ChatterAPIError, ChatterSDKError } from '@chatter/sdk-ts';

try {
  const response = await chatter.chat.chatChat({
    message: 'Hello!',
    workflow: 'invalid-workflow' // This will cause an error
  });
} catch (error) {
  if (error instanceof ChatterAPIError) {
    console.error('API Error:', {
      status: error.status,
      message: error.message,
      body: error.body
    });
  } else if (error instanceof ChatterSDKError) {
    console.error('SDK Error:', error.message);
  } else {
    console.error('Network Error:', error);
  }
}
```

## Type Safety

The SDK provides complete type safety for all operations:

```typescript
// All parameters are typed
const chatRequest: ChatRequest = {
  message: 'Hello!',
  workflow: 'rag', // TypeScript will suggest: 'plain' | 'rag' | 'tools' | 'full'
  temperature: 0.7, // number | null
  max_tokens: 1000 // number | null
};

// Return types are fully typed
const response: ChatResponse = await chatter.chat.chatChat(chatRequest);

// Access nested properties with confidence
const messageContent: string = response.message.content;
const conversationId: string = response.conversation_id;
```

## Advanced Usage

### Custom Configuration per Request

```typescript
// Different base paths for different services
const productionChat = chatter.chat.withBasePath('https://chat-api.com');
const stagingDocs = chatter.documents.withBasePath('https://staging-docs-api.com');

// Custom headers for specific requests
const chatWithHeaders = chatter.chat.withHeaders({
  'X-Priority': 'high'
});
```

### Streaming Responses

```typescript
// For endpoints that support streaming
const streamingResponse = await chatter.chat.chatChat({
  message: 'Tell me a long story',
  stream: true
});

// Handle streaming response (implementation depends on your needs)
```

### Batch Operations

```typescript
// Many endpoints support batch operations
const agents = await chatter.agents.createBulkAgents({
  agents: [
    { name: 'Agent 1', type: 'chat' },
    { name: 'Agent 2', type: 'search' }
  ]
});
```

## API Reference

The SDK covers all Chatter API endpoints:

### Service Areas

- **Authentication** (13 methods) - Login, logout, token management
- **Chat** (13 methods) - Conversations, messages, templates  
- **Documents** (11 methods) - Upload, search, management
- **Agents** (11 methods) - AI agent creation and interaction
- **Workflows** (13 methods) - Workflow definition and execution
- **Models** (21 methods) - LLM and embedding model management
- **Tool Servers** (26 methods) - External tool integration
- **Analytics** (11 methods) - Usage metrics and monitoring
- **A/B Testing** (13 methods) - Experiment management
- **Profiles** (9 methods) - User profile management
- **Prompts** (8 methods) - Prompt template management
- **Jobs** (6 methods) - Background job management
- **Data Management** (8 methods) - Backup and restore
- **Events** (5 methods) - Event tracking
- **Plugins** (12 methods) - Plugin management
- **Health** (5 methods) - System health checks

### Data Models

The SDK includes TypeScript interfaces for 216+ data models, including:

- `ChatRequest`, `ChatResponse` - Chat interactions
- `AgentCreateRequest`, `AgentResponse` - Agent management
- `DocumentResponse`, `DocumentSearchResult` - Document handling
- `WorkflowDefinitionCreate`, `WorkflowExecutionResponse` - Workflows
- And many more...

## Contributing

This SDK is hand-crafted for maximum type safety and usability. If you find any issues or want to contribute improvements:

1. Check the OpenAPI specification for the latest API changes
2. Update the appropriate model or API client files
3. Ensure all types remain accurate and complete
4. Test your changes thoroughly

## License

MIT License - see LICENSE file for details.