/**
 * Generated API client for Chat
 */
import { AvailableToolsResponse, ChatRequest, ChatResponse, McpStatusResponse, PerformanceStatsResponse, chatter__schemas__chat__WorkflowTemplatesResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod } from '../runtime';

export class ChatApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Chat
   * Non-streaming chat endpoint supporting all workflow types.
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
  public async chatChat(data: ChatRequest): Promise<ChatResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/chat/chat`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ChatResponse>;
  }
  /**Streaming Chat
   * Streaming chat endpoint supporting all workflow types.
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
  public async streamingChatApiV1ChatStreaming(data: ChatRequest): Promise<ReadableStream<Uint8Array>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/chat/streaming`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.requestStream(requestContext);
    return response;
  }
  /**Get Available Tools
   * Get list of available MCP tools.
   */
  public async getAvailableToolsApiV1ChatToolsAvailable(): Promise<AvailableToolsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/chat/tools/available`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AvailableToolsResponse>;
  }
  /**Get Workflow Templates
   * Get available workflow templates.
   */
  public async getWorkflowTemplatesApiV1ChatTemplates(): Promise<chatter__schemas__chat__WorkflowTemplatesResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/chat/templates`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<chatter__schemas__chat__WorkflowTemplatesResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/chat/template/${templateName}`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ChatResponse>;
  }
  /**Get Performance Stats
   * Get workflow performance statistics.
   */
  public async getPerformanceStatsApiV1ChatPerformanceStats(): Promise<PerformanceStatsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/chat/performance/stats`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PerformanceStatsResponse>;
  }
  /**Get Mcp Status
   * Get MCP service status.
   */
  public async getMcpStatusApiV1ChatMcpStatus(): Promise<McpStatusResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/chat/mcp/status`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<McpStatusResponse>;
  }
}