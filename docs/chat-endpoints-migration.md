# Chat Endpoints Split - Migration Guide

This document explains the changes made to split the unified `/chat` endpoint into separate streaming and non-streaming endpoints.

## What Changed

### Before (Old API)
- Single `/api/v1/chat/chat` endpoint
- Used `stream: true/false` parameter to control streaming behavior
- Response type depended on the `stream` parameter

### After (New API)
- **Non-streaming**: `/api/v1/chat/chat` endpoint (no stream parameter needed)
- **Streaming**: `/api/v1/chat/streaming` endpoint (always streams)
- The `stream` field in ChatRequest is now deprecated but still accepted for backward compatibility

## API Endpoints

### Non-streaming Chat: `POST /api/v1/chat/chat`
**Request:**
```json
{
  "message": "Hello, how are you?",
  "workflow": "plain"
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

### Streaming Chat: `POST /api/v1/chat/streaming`
**Request:**
```json
{
  "message": "Tell me a story",
  "workflow": "plain"
}
```

**Response:** Server-Sent Events (SSE)
```
data: {"type": "start", "content": "", "correlation_id": "..."}

data: {"type": "token", "content": "Once"}

data: {"type": "token", "content": " upon"}

data: {"type": "token", "content": " a"}

data: {"type": "token", "content": " time..."}

data: {"type": "end", "content": ""}

data: [DONE]
```

## Migration Guide

### Frontend Applications
**Before:**
```javascript
// Old way - using stream parameter
const response = await fetch('/api/v1/chat/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: "Hello",
    workflow: "plain",
    stream: true  // This controlled streaming
  })
});
```

**After:**
```javascript
// New way - use different endpoints
// For streaming:
const response = await fetch('/api/v1/chat/streaming', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({
    message: "Hello",
    workflow: "plain"
    // No stream parameter needed
  })
});

// For non-streaming:
const response = await fetch('/api/v1/chat/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: "Hello",
    workflow: "plain"
    // No stream parameter needed
  })
});
```

### SDK Usage

#### TypeScript SDK
```typescript
import { ChatApi, ChatRequest } from './sdk';

const chatApi = new ChatApi();
const request: ChatRequest = {
  message: "Hello",
  workflow: "plain"
};

// Non-streaming
const response = await chatApi.chatApiV1ChatChatPost({ chatRequest: request });

// Streaming  
const streamResponse = await chatApi.streamingChatApiV1ChatStreamingPost({ 
  chatRequest: request 
});
```

#### Python SDK
```python
from chatter_sdk import ChatApi, ChatRequest

chat_api = ChatApi()
request = ChatRequest(message="Hello", workflow="plain")

# Non-streaming
response = await chat_api.chat_api_v1_chat_chat_post(request)

# Streaming
stream_response = await chat_api.streaming_chat_api_v1_chat_streaming_post(request)
```

## Backward Compatibility

The `stream` field in `ChatRequest` is still accepted but marked as deprecated:
- It will be ignored when using the `/streaming` endpoint (always streams)
- It will be ignored when using the `/chat` endpoint (never streams)
- A deprecation warning is included in the field description

## Benefits of This Change

1. **Clear API Design**: Endpoints have single responsibilities
2. **Better Type Safety**: No conditional response types
3. **Easier Documentation**: Each endpoint has clear input/output contracts
4. **Improved Performance**: No conditional logic in request handling
5. **Future-Proof**: Easier to add endpoint-specific features

## Timeline

- **Current**: Both old and new patterns work
- **Future**: The `stream` parameter may be removed in a future version
- **Recommendation**: Update your code to use the new endpoint pattern