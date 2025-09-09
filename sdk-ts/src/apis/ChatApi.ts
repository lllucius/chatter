/**
 * Generated API client for Chat
 */
import { AvailableToolsResponse, ChatRequest, ChatResponse, ConversationCreate, ConversationDeleteResponse, ConversationResponse, ConversationSearchResponse, ConversationUpdate, ConversationWithMessages, McpStatusResponse, MessageDeleteResponse, MessageResponse, PerformanceStatsResponse, Record } from '../models/index';
import { BaseAPI, Configuration, RequestOptions } from '../runtime';

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
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<ConversationResponse>(`/api/v1/chat/conversations`, requestOptions);
  }
  /**List Conversations
   * List conversations for the current user.
   */
  public async listConversationsApiV1ChatConversations(options?: RequestOptions): Promise<ConversationSearchResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'limit': options?.limit,
        'offset': options?.offset,
      },
    };

    return this.request<ConversationSearchResponse>(`/api/v1/chat/conversations`, requestOptions);
  }
  /**Get Conversation
   * Get conversation details with optional messages.
   */
  public async getConversationApiV1ChatConversationsConversationId(conversationId: string, options?: RequestOptions): Promise<ConversationWithMessages> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'include_messages': options?.includeMessages,
      },
    };

    return this.request<ConversationWithMessages>(`/api/v1/chat/conversations/${conversationId}`, requestOptions);
  }
  /**Update Conversation
   * Update conversation.
   */
  public async updateConversationApiV1ChatConversationsConversationId(conversationId: string, data: ConversationUpdate): Promise<ConversationResponse> {
    const requestOptions: RequestOptions = {
      method: 'PUT',
      body: data,
    };

    return this.request<ConversationResponse>(`/api/v1/chat/conversations/${conversationId}`, requestOptions);
  }
  /**Delete Conversation
   * Delete conversation.
   */
  public async deleteConversationApiV1ChatConversationsConversationId(conversationId: string): Promise<ConversationDeleteResponse> {
    const requestOptions: RequestOptions = {
      method: 'DELETE',
    };

    return this.request<ConversationDeleteResponse>(`/api/v1/chat/conversations/${conversationId}`, requestOptions);
  }
  /**Get Conversation Messages
   * Get messages from a conversation.
   */
  public async getConversationMessagesApiV1ChatConversationsConversationIdMessages(conversationId: string, options?: RequestOptions): Promise<MessageResponse[]> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'limit': options?.limit,
        'offset': options?.offset,
      },
    };

    return this.request<MessageResponse[]>(`/api/v1/chat/conversations/${conversationId}/messages`, requestOptions);
  }
  /**Delete Message
   * Delete a message from a conversation.
   */
  public async deleteMessageApiV1ChatConversationsConversationIdMessagesMessageId(conversationId: string, messageId: string): Promise<MessageDeleteResponse> {
    const requestOptions: RequestOptions = {
      method: 'DELETE',
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
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<Record<string, unknown>>(`/api/v1/chat/chat`, requestOptions);
  }
  /**Get Available Tools
   * Get list of available MCP tools.
   */
  public async getAvailableToolsApiV1ChatToolsAvailable(): Promise<AvailableToolsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<AvailableToolsResponse>(`/api/v1/chat/tools/available`, requestOptions);
  }
  /**Get Workflow Templates
   * Get available workflow templates.
   */
  public async getWorkflowTemplatesApiV1ChatTemplates(): Promise<chatter__schemas__chat__WorkflowTemplatesResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
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
  public async chatWithTemplateApiV1ChatTemplateTemplateName(templateName: string, data: ChatRequest): Promise<ChatResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<ChatResponse>(`/api/v1/chat/template/${templateName}`, requestOptions);
  }
  /**Get Performance Stats
   * Get workflow performance statistics.
   */
  public async getPerformanceStatsApiV1ChatPerformanceStats(): Promise<PerformanceStatsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<PerformanceStatsResponse>(`/api/v1/chat/performance/stats`, requestOptions);
  }
  /**Get Mcp Status
   * Get MCP service status.
   */
  public async getMcpStatusApiV1ChatMcpStatus(): Promise<McpStatusResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<McpStatusResponse>(`/api/v1/chat/mcp/status`, requestOptions);
  }
}