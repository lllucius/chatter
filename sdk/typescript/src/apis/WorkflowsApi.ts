/**
 * Generated API client for Workflows
 */
import { Body_execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post, ChatResponse, ChatWorkflowRequest, DetailedWorkflowExecutionResponse, NodeTypeResponse, WorkflowAnalyticsResponse, WorkflowDefinitionCreate, WorkflowDefinitionFromTemplateRequest, WorkflowDefinitionResponse, WorkflowDefinitionUpdate, WorkflowDefinitionsResponse, WorkflowDeleteResponse, WorkflowExecutionRequest, WorkflowExecutionResponse, WorkflowTemplateCreate, WorkflowTemplateResponse, WorkflowTemplateUpdate, WorkflowTemplatesResponse, WorkflowValidationResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

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
  /**Delete Workflow Template
   * Delete a workflow template.
   */
  public async deleteWorkflowTemplateApiV1WorkflowsTemplatesTemplateId(templateId: string): Promise<WorkflowDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates/${templateId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowDeleteResponse>;
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
   * Validate a workflow definition - supports both legacy and modern formats.
   */
  public async validateWorkflowDefinitionApiV1WorkflowsDefinitionsValidate(data: WorkflowDefinitionCreate | Record<string, unknown>): Promise<WorkflowValidationResponse> {
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
  /**Get Workflow Execution Details
   * Get detailed information about a specific workflow execution.
   */
  public async getWorkflowExecutionDetailsApiV1WorkflowsDefinitionsWorkflowIdExecutionsExecutionId(workflowId: string, executionId: string): Promise<DetailedWorkflowExecutionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/${workflowId}/executions/${executionId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<DetailedWorkflowExecutionResponse>;
  }
  /**Get Workflow Execution Logs
   * Get execution logs for a specific workflow execution.
   */
  public async getWorkflowExecutionLogsApiV1WorkflowsDefinitionsWorkflowIdExecutionsExecutionIdLogs(workflowId: string, executionId: string, options?: { logLevel?: string | null; limit?: number; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>[]> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/${workflowId}/executions/${executionId}/logs`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'log_level': options?.logLevel,
        'limit': options?.limit,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>[]>;
  }
  /**Execute Chat Workflow
   * Execute chat using dynamically built workflow.
## Dynamic Workflow Configuration

This endpoint supports dynamic workflow configuration through capability flags:

### Basic Chat
Simple conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "enable_retrieval": false,
    "enable_tools": false
}
```

### Retrieval-Augmented Generation
Document search and retrieval capabilities.
```json
{
    "message": "What are the latest sales figures?",
    "enable_retrieval": true,
    "enable_tools": false
}
```

### Tool-Enhanced Workflow
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "enable_retrieval": false,
    "enable_tools": true
}
```

### Full-Featured Workflow
Combination of retrieval and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "enable_retrieval": true,
    "enable_tools": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "enable_retrieval": false,
    "enable_tools": false,
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
## Dynamic Workflow Configuration

This endpoint supports dynamic workflow configuration through capability flags:

### Basic Chat
Simple conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "enable_retrieval": false,
    "enable_tools": false
}
```

### Retrieval-Augmented Generation
Document search and retrieval capabilities.
```json
{
    "message": "What are the latest sales figures?",
    "enable_retrieval": true,
    "enable_tools": false
}
```

### Tool-Enhanced Workflow
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "enable_retrieval": false,
    "enable_tools": true
}
```

### Full-Featured Workflow
Combination of retrieval and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "enable_retrieval": true,
    "enable_tools": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "enable_retrieval": false,
    "enable_tools": false,
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
  /**Execute Custom Workflow
   * Execute a custom workflow definition using the modern system.
   */
  public async executeCustomWorkflowApiV1WorkflowsDefinitionsCustomExecute(data: Body_execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post, options?: { message?: string; entryPoint?: string | null; provider?: string; model?: string; conversationId?: string | null; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/custom/execute`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      query: {
        'message': options?.message,
        'entry_point': options?.entryPoint,
        'provider': options?.provider,
        'model': options?.model,
        'conversation_id': options?.conversationId,
        ...options?.query
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get Modern Supported Node Types
   * Get supported node types from the modern workflow system.
   */
  public async getModernSupportedNodeTypesApiV1WorkflowsNodeTypesModern(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/node-types/modern`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Configure Memory Settings
   * Configure memory management settings for the user.
   */
  public async configureMemorySettingsApiV1WorkflowsMemoryConfigure(options?: { adaptiveMode?: boolean; baseWindowSize?: number; maxWindowSize?: number; summaryStrategy?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/memory/configure`,
      method: 'POST' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'adaptive_mode': options?.adaptiveMode,
        'base_window_size': options?.baseWindowSize,
        'max_window_size': options?.maxWindowSize,
        'summary_strategy': options?.summaryStrategy,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Configure Tool Settings
   * Configure tool execution settings for the user.
   */
  public async configureToolSettingsApiV1WorkflowsToolsConfigure(options?: { maxTotalCalls?: number; maxConsecutiveCalls?: number; recursionStrategy?: string; enableRecursionDetection?: boolean; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/tools/configure`,
      method: 'POST' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'max_total_calls': options?.maxTotalCalls,
        'max_consecutive_calls': options?.maxConsecutiveCalls,
        'recursion_strategy': options?.recursionStrategy,
        'enable_recursion_detection': options?.enableRecursionDetection,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get Workflow Defaults
   * Get workflow defaults from profiles, models, and prompts.

Args:
    node_type: Optional specific node type to get defaults for
    current_user: Current authenticated user
    defaults_service: Workflow defaults service
    
Returns:
    Dictionary containing default configurations
   */
  public async getWorkflowDefaultsApiV1WorkflowsDefaults(options?: { nodeType?: string | null; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/defaults`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'node_type': options?.nodeType,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
}