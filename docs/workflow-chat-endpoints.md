# Workflow Chat Endpoints - Usage Guide

This document explains how to use the existing workflow chat endpoints for streaming and non-streaming chat functionality.

## API Endpoints

### Non-streaming Chat: `POST /api/v1/workflows/execute/chat`
Execute chat using dynamically built workflow without streaming.

**Request:**
```json
{
  "message": "Hello, how are you?",
  "enable_retrieval": false,
  "enable_tools": false,
  "enable_memory": true
}
```

**Response:** JSON `ChatResponse`
```json
{
  "conversation_id": "...",
  "message": {
    "id": "...",
    "content": "I'm doing well, thank you!",
    "role": "assistant"
  },
  "conversation": {...}
}
```

### Streaming Chat: `POST /api/v1/workflows/execute/chat/streaming`
Execute chat using dynamically built workflow with Server-Sent Events streaming.

**Request:**
```json
{
  "message": "Tell me a story",
  "enable_retrieval": false,
  "enable_tools": false,
  "enable_memory": true
}
```

**Response:** Server-Sent Events (SSE)
```
data: {"type": "token", "content": "Once"}

data: {"type": "token", "content": " upon"}

data: {"type": "token", "content": " a"}

data: {"type": "done", "content": ""}

data: [DONE]
```

## Usage Examples

### Frontend JavaScript
```javascript
// Non-streaming
const response = await fetch('/api/v1/workflows/execute/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: "Hello",
    enable_retrieval: false,
    enable_tools: false,
    enable_memory: true
  })
});

// Streaming
const response = await fetch('/api/v1/workflows/execute/chat/streaming', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({
    message: "Hello",
    enable_retrieval: false,
    enable_tools: false,
    enable_memory: true
  })
});
```

### TypeScript SDK
```typescript
import { getSDK } from './services/auth-service';

const sdk = getSDK();

// Non-streaming
const response = await sdk.workflows.executeChatWorkflowApiV1WorkflowsExecuteChat(request);

// Streaming
const streamResponse = await sdk.workflows.executeChatWorkflowStreamingApiV1WorkflowsExecuteChatStreaming(request);
```

## Dynamic Workflow Configuration

Both endpoints support dynamic workflow configuration through capability flags:

### Basic Chat
Simple conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "enable_retrieval": false,
    "enable_tools": false,
    "enable_memory": true
}
```

### Retrieval-Augmented Generation
Document search and retrieval capabilities.
```json
{
    "message": "What are the latest sales figures?",
    "enable_retrieval": true,
    "enable_tools": false,
    "enable_memory": true
}
```

### Tool-Enhanced Workflow
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "enable_retrieval": false,
    "enable_tools": true,
    "enable_memory": true
}
```

### Full-Featured Workflow
Combination of retrieval and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "enable_retrieval": true,
    "enable_tools": true,
    "enable_memory": true
}
```