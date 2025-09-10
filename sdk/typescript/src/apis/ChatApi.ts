/**
 * Generated API client for Chat
 */
import { AvailableToolsResponse, ChatRequest, ChatResponse, ConversationCreate, ConversationDeleteResponse, ConversationResponse, ConversationSearchResponse, ConversationUpdate, ConversationWithMessages, McpStatusResponse, MessageDeleteResponse, MessageResponse, PerformanceStatsResponse, chatter__schemas__chat__WorkflowTemplatesResponse } from '../models/index';
import { BaseAPI, Configuration, HTTPQuery, HTTPHeaders } from '../runtime';

export class ChatApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Create Conversation
   * Create a new conversation.

Create a new conversation with specified configuration
## Workflow Types

This endpoint supports multiple workflow types through the `workflow` parameter:

### Plain Chat (`plain`)
Basic conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "workflow": "plain"
}
```

### RAG Workflow (`rag`)
Retrieval-Augmented Generation with document search.
```json
{
    "message": "What are the latest sales figures?",
    "workflow": "rag",
    "enable_retrieval": true
}
```

### Tools Workflow (`tools`)
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "workflow": "tools"
}
```

### Full Workflow (`full`)
Combination of RAG and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "workflow": "full",
    "enable_retrieval": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "workflow": "plain",
    "stream": true
}
```

Streaming responses use Server-Sent Events (SSE) format with event types:
- `token`: Content chunks
- `node_start`: Workflow node started
- `node_complete`: Workflow node completed
- `usage`: Final usage statistics
- `error`: Error occurred

## Templates

Use pre-configured templates for common scenarios:
```json
{
    "message": "I need help with my order",
    "workflow_template": "customer_support"
}
```

Available templates:
- `customer_support`: Customer service with knowledge base
- `code_assistant`: Programming help with code tools
- `research_assistant`: Document research and analysis
- `general_chat`: General conversation
- `document_qa`: Document question answering
- `data_analyst`: Data analysis with computation tools

   */
  public async createConversationApiV1ChatConversations(data: ConversationCreate): Promise<ConversationResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<ConversationResponse>(`/api/v1/chat/conversations`, requestOptions);
  }
  /**List Conversations
   * List conversations for the current user.
   */
  public async listConversationsApiV1ChatConversations(options?: { limit?: number; offset?: number; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ConversationSearchResponse> {
    const requestOptions = {
      method: 'GET' as const,
      headers: options?.headers,
      query: {
        'limit': options?.limit,
        'offset': options?.offset,
        ...options?.query
      },
    };

    return this.request<ConversationSearchResponse>(`/api/v1/chat/conversations`, requestOptions);
  }
  /**Get Conversation
   * Get conversation details with optional messages.
   */
  public async getConversationApiV1ChatConversationsConversationId(conversationId: string, options?: { includeMessages?: boolean; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ConversationWithMessages> {
    const requestOptions = {
      method: 'GET' as const,
      headers: options?.headers,
      query: {
        'include_messages': options?.includeMessages,
        ...options?.query
      },
    };

    return this.request<ConversationWithMessages>(`/api/v1/chat/conversations/${conversationId}`, requestOptions);
  }
  /**Update Conversation
   * Update conversation.
   */
  public async updateConversationApiV1ChatConversationsConversationId(conversationId: string, data: ConversationUpdate): Promise<ConversationResponse> {
    const requestOptions = {
      method: 'PUT' as const,
      body: data,
    };

    return this.request<ConversationResponse>(`/api/v1/chat/conversations/${conversationId}`, requestOptions);
  }
  /**Delete Conversation
   * Delete conversation.
   */
  public async deleteConversationApiV1ChatConversationsConversationId(conversationId: string): Promise<ConversationDeleteResponse> {
    const requestOptions = {
      method: 'DELETE' as const,
    };

    return this.request<ConversationDeleteResponse>(`/api/v1/chat/conversations/${conversationId}`, requestOptions);
  }
  /**Get Conversation Messages
   * Get messages from a conversation.
   */
  public async getConversationMessagesApiV1ChatConversationsConversationIdMessages(conversationId: string, options?: { limit?: number; offset?: number; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<MessageResponse[]> {
    const requestOptions = {
      method: 'GET' as const,
      headers: options?.headers,
      query: {
        'limit': options?.limit,
        'offset': options?.offset,
        ...options?.query
      },
    };

    return this.request<MessageResponse[]>(`/api/v1/chat/conversations/${conversationId}/messages`, requestOptions);
  }
  /**Delete Message
   * Delete a message from a conversation.
   */
  public async deleteMessageApiV1ChatConversationsConversationIdMessagesMessageId(conversationId: string, messageId: string): Promise<MessageDeleteResponse> {
    const requestOptions = {
      method: 'DELETE' as const,
    };

    return this.request<MessageDeleteResponse>(`/api/v1/chat/conversations/${conversationId}/messages/${messageId}`, requestOptions);
  }
  /**Chat
   * Unified chat endpoint supporting all workflow types with optional streaming.
## Workflow Types

This endpoint supports multiple workflow types through the `workflow` parameter:

### Plain Chat (`plain`)
Basic conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "workflow": "plain"
}
```

### RAG Workflow (`rag`)
Retrieval-Augmented Generation with document search.
```json
{
    "message": "What are the latest sales figures?",
    "workflow": "rag",
    "enable_retrieval": true
}
```

### Tools Workflow (`tools`)
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "workflow": "tools"
}
```

### Full Workflow (`full`)
Combination of RAG and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "workflow": "full",
    "enable_retrieval": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "workflow": "plain",
    "stream": true
}
```

Streaming responses use Server-Sent Events (SSE) format with event types:
- `token`: Content chunks
- `node_start`: Workflow node started
- `node_complete`: Workflow node completed
- `usage`: Final usage statistics
- `error`: Error occurred

## Templates

Use pre-configured templates for common scenarios:
```json
{
    "message": "I need help with my order",
    "workflow_template": "customer_support"
}
```

Available templates:
- `customer_support`: Customer service with knowledge base
- `code_assistant`: Programming help with code tools
- `research_assistant`: Document research and analysis
- `general_chat`: General conversation
- `document_qa`: Document question answering
- `data_analyst`: Data analysis with computation tools

   */
  public async chatChat(data: ChatRequest): Promise<Record<string, unknown>> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<Record<string, unknown>>(`/api/v1/chat/chat`, requestOptions);
  }
  /**Get Available Tools
   * Get list of available MCP tools.
   */
  public async getAvailableToolsApiV1ChatToolsAvailable(): Promise<AvailableToolsResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<AvailableToolsResponse>(`/api/v1/chat/tools/available`, requestOptions);
  }
  /**Get Workflow Templates
   * Get available workflow templates.
   */
  public async getWorkflowTemplatesApiV1ChatTemplates(): Promise<chatter__schemas__chat__WorkflowTemplatesResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<chatter__schemas__chat__WorkflowTemplatesResponse>(`/api/v1/chat/templates`, requestOptions);
  }
  /**Chat With Template
   * Chat using a specific workflow template.
## Workflow Types

This endpoint supports multiple workflow types through the `workflow` parameter:

### Plain Chat (`plain`)
Basic conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "workflow": "plain"
}
```

### RAG Workflow (`rag`)
Retrieval-Augmented Generation with document search.
```json
{
    "message": "What are the latest sales figures?",
    "workflow": "rag",
    "enable_retrieval": true
}
```

### Tools Workflow (`tools`)
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "workflow": "tools"
}
```

### Full Workflow (`full`)
Combination of RAG and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "workflow": "full",
    "enable_retrieval": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "workflow": "plain",
    "stream": true
}
```

Streaming responses use Server-Sent Events (SSE) format with event types:
- `token`: Content chunks
- `node_start`: Workflow node started
- `node_complete`: Workflow node completed
- `usage`: Final usage statistics
- `error`: Error occurred

## Templates

Use pre-configured templates for common scenarios:
```json
{
    "message": "I need help with my order",
    "workflow_template": "customer_support"
}
```

Available templates:
- `customer_support`: Customer service with knowledge base
- `code_assistant`: Programming help with code tools
- `research_assistant`: Document research and analysis
- `general_chat`: General conversation
- `document_qa`: Document question answering
- `data_analyst`: Data analysis with computation tools

   */
  public async chatChatStreaming(
    data: ChatRequest,
    onChunk: (chunk: any) => void,
    onComplete?: () => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    const url = (this as any).buildURL('/api/v1/chat/chat');
    const headers = { 
      ...this.configuration.headers, 
      'Accept': 'text/event-stream',
      'Cache-Control': 'no-cache'
    };
    
    const init: RequestInit = {
      method: 'POST',
      headers,
      body: JSON.stringify({ ...data, stream: true }),
      credentials: this.configuration.credentials,
    };

    try {
      const response = await fetch(url, init);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('No response body for streaming');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      try {
        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6).trim(); // Remove 'data: ' prefix
              
              if (dataStr === '[DONE]') {
                if (onComplete) onComplete();
                return; // End of stream
              }
              
              if (dataStr) {
                try {
                  const chunk = JSON.parse(dataStr);
                  onChunk(chunk);
                  
                  if (chunk.type === 'end') {
                    if (onComplete) onComplete();
                    return; // End the streaming loop
                  } else if (chunk.type === 'error') {
                    throw new Error(chunk.content || chunk.error || 'Streaming error');
                  }
                } catch (parseError) {
                  console.error('Failed to parse streaming data:', parseError, dataStr);
                }
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Unknown streaming error');
      if (onError) {
        onError(err);
      } else {
        throw err;
      }
    }
  }

  /**Chat With Template
   * Chat using a specific workflow template.
## Workflow Types

This endpoint supports multiple workflow types through the `workflow` parameter:

### Plain Chat (`plain`)
Basic conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "workflow": "plain"
}
```

### RAG Workflow (`rag`)
Retrieval-Augmented Generation with document search.
```json
{
    "message": "What are the latest sales figures?",
    "workflow": "rag",
    "enable_retrieval": true
}
```

### Tools Workflow (`tools`)
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "workflow": "tools"
}
```

### Full Workflow (`full`)
Combination of RAG and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "workflow": "full",
    "enable_retrieval": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "workflow": "plain",
    "stream": true
}
```

Streaming responses use Server-Sent Events (SSE) format with event types:
- `token`: Content chunks
- `node_start`: Workflow node started
- `node_complete`: Workflow node completed
- `usage`: Final usage statistics
- `error`: Error occurred

## Templates

Use pre-configured templates for common scenarios:
```json
{
    "message": "I need help with my order",
    "workflow_template": "customer_support"
}
```

Available templates:
- `customer_support`: Customer service with knowledge base
- `code_assistant`: Programming help with code tools
- `research_assistant`: Document research and analysis
- `general_chat`: General conversation
- `document_qa`: Document question answering
- `data_analyst`: Data analysis with computation tools

   */
  public async chatWithTemplateApiV1ChatTemplateTemplateName(templateName: string, data: ChatRequest): Promise<ChatResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<ChatResponse>(`/api/v1/chat/template/${templateName}`, requestOptions);
  }
  /**Get Performance Stats
   * Get workflow performance statistics.
   */
  public async getPerformanceStatsApiV1ChatPerformanceStats(): Promise<PerformanceStatsResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<PerformanceStatsResponse>(`/api/v1/chat/performance/stats`, requestOptions);
  }
  /**Get Mcp Status
   * Get MCP service status.
   */
  public async getMcpStatusApiV1ChatMcpStatus(): Promise<McpStatusResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<McpStatusResponse>(`/api/v1/chat/mcp/status`, requestOptions);
  }
}