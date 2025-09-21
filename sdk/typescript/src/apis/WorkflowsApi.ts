/**
 * Generated API client for Workflows
 */
import { ChatResponse, ChatWorkflowRequest, NodeTypeResponse, WorkflowAnalyticsResponse, WorkflowDefinitionCreate, WorkflowDefinitionFromTemplateRequest, WorkflowDefinitionResponse, WorkflowDefinitionUpdate, WorkflowDefinitionsResponse, WorkflowDeleteResponse, WorkflowExecutionRequest, WorkflowExecutionResponse, WorkflowTemplateCreate, WorkflowTemplateResponse, WorkflowTemplateUpdate, WorkflowTemplatesResponse, WorkflowValidationResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod } from '../runtime';

export class WorkflowsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**List Workflow Definitions
   * List all workflow definitions for the current user.
   */
  public async listWorkflowDefinitionsApiV1WorkflowsDefinitions(): Promise<WorkflowDefinitionsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowDefinitionsResponse>;
  }
  /**Create Workflow Definition
   * Create a new workflow definition.
   */
  public async createWorkflowDefinitionApiV1WorkflowsDefinitions(data: WorkflowDefinitionCreate): Promise<WorkflowDefinitionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowDefinitionResponse>;
  }
  /**Create Workflow Definition From Template
   * Create a workflow definition from a template.
   */
  public async createWorkflowDefinitionFromTemplateApiV1WorkflowsDefinitionsFromTemplate(data: WorkflowDefinitionFromTemplateRequest): Promise<WorkflowDefinitionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/from-template`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowDefinitionResponse>;
  }
  /**Get Workflow Definition
   * Get a specific workflow definition.
   */
  public async getWorkflowDefinitionApiV1WorkflowsDefinitionsWorkflowId(workflowId: string): Promise<WorkflowDefinitionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/${workflowId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowDefinitionResponse>;
  }
  /**Update Workflow Definition
   * Update a workflow definition.
   */
  public async updateWorkflowDefinitionApiV1WorkflowsDefinitionsWorkflowId(workflowId: string, data: WorkflowDefinitionUpdate): Promise<WorkflowDefinitionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/${workflowId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowDefinitionResponse>;
  }
  /**Delete Workflow Definition
   * Delete a workflow definition.
   */
  public async deleteWorkflowDefinitionApiV1WorkflowsDefinitionsWorkflowId(workflowId: string): Promise<WorkflowDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/${workflowId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowDeleteResponse>;
  }
  /**List Workflow Templates
   * List all workflow templates accessible to the current user.
   */
  public async listWorkflowTemplatesApiV1WorkflowsTemplates(): Promise<WorkflowTemplatesResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowTemplatesResponse>;
  }
  /**Create Workflow Template
   * Create a new workflow template.
   */
  public async createWorkflowTemplateApiV1WorkflowsTemplates(data: WorkflowTemplateCreate): Promise<WorkflowTemplateResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowTemplateResponse>;
  }
  /**Update Workflow Template
   * Update a workflow template.
   */
  public async updateWorkflowTemplateApiV1WorkflowsTemplatesTemplateId(templateId: string, data: WorkflowTemplateUpdate): Promise<WorkflowTemplateResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates/${templateId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowTemplateResponse>;
  }
  /**Get Workflow Analytics
   * Get analytics for a specific workflow definition.
   */
  public async getWorkflowAnalyticsApiV1WorkflowsDefinitionsWorkflowIdAnalytics(workflowId: string): Promise<WorkflowAnalyticsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/${workflowId}/analytics`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowAnalyticsResponse>;
  }
  /**Execute Workflow
   * Execute a workflow definition.
   */
  public async executeWorkflowApiV1WorkflowsDefinitionsWorkflowIdExecute(workflowId: string, data: WorkflowExecutionRequest): Promise<WorkflowExecutionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/${workflowId}/execute`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowExecutionResponse>;
  }
  /**Validate Workflow Definition
   * Validate a workflow definition.
   */
  public async validateWorkflowDefinitionApiV1WorkflowsDefinitionsValidate(data: WorkflowDefinitionCreate): Promise<WorkflowValidationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/validate`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowValidationResponse>;
  }
  /**Get Supported Node Types
   * Get list of supported workflow node types.
   */
  public async getSupportedNodeTypesApiV1WorkflowsNodeTypes(): Promise<NodeTypeResponse[]> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/node-types`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<NodeTypeResponse[]>;
  }
  /**List Workflow Executions
   * List executions for a workflow definition.
   */
  public async listWorkflowExecutionsApiV1WorkflowsDefinitionsWorkflowIdExecutions(workflowId: string): Promise<WorkflowExecutionResponse[]> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/${workflowId}/executions`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowExecutionResponse[]>;
  }
  /**Execute Chat Workflow
   * Execute chat using dynamically built workflow.
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
  public async executeChatWorkflowApiV1WorkflowsExecuteChat(data: ChatWorkflowRequest): Promise<ChatResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/execute/chat`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ChatResponse>;
  }
  /**Execute Chat Workflow Streaming
   * Execute chat using dynamically built workflow with streaming.
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
  public async executeChatWorkflowStreamingApiV1WorkflowsExecuteChatStreaming(data: ChatWorkflowRequest): Promise<ReadableStream<Uint8Array>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/execute/chat/streaming`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.requestStream(requestContext);
    return response;
  }
}