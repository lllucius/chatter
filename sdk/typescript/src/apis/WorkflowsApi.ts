/**
 * Generated API client for Workflows
 */
import { Body_execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post, ChatRequest, ChatResponse, DetailedWorkflowExecutionResponse, NodeTypeResponse, WorkflowAnalyticsResponse, WorkflowDefinitionCreate, WorkflowDefinitionFromTemplateRequest, WorkflowDefinitionResponse, WorkflowDefinitionUpdate, WorkflowDefinitionsResponse, WorkflowDeleteResponse, WorkflowExecutionRequest, WorkflowExecutionResponse, WorkflowTemplateCreate, WorkflowTemplateDirectExecutionRequest, WorkflowTemplateExecutionRequest, WorkflowTemplateExportResponse, WorkflowTemplateImportRequest, WorkflowTemplateResponse, WorkflowTemplateUpdate, WorkflowTemplateValidationRequest, WorkflowTemplateValidationResponse, WorkflowTemplatesResponse, WorkflowValidationResponse } from '../models/index';
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
  /**Export Workflow Template
   * Export a workflow template.
   */
  public async exportWorkflowTemplateApiV1WorkflowsTemplatesTemplateIdExport(templateId: string): Promise<WorkflowTemplateExportResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates/${templateId}/export`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowTemplateExportResponse>;
  }
  /**Import Workflow Template
   * Import a workflow template.
   */
  public async importWorkflowTemplateApiV1WorkflowsTemplatesImport(data: WorkflowTemplateImportRequest): Promise<WorkflowTemplateResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates/import`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowTemplateResponse>;
  }
  /**Load Workflow Template
   * Load a workflow template with full details.
   */
  public async loadWorkflowTemplateApiV1WorkflowsTemplatesTemplateIdLoad(templateId: string): Promise<WorkflowTemplateResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates/${templateId}/load`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowTemplateResponse>;
  }
  /**Validate Workflow Template
   * Validate a workflow template using the unified validation orchestrator.
   */
  public async validateWorkflowTemplateApiV1WorkflowsTemplatesValidate(data: WorkflowTemplateValidationRequest): Promise<WorkflowTemplateValidationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates/validate`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowTemplateValidationResponse>;
  }
  /**Execute Workflow Template
   * Execute a workflow template directly using the unified execution engine.

**New in Phase 7**: Templates now execute directly without creating temporary
workflow definitions, reducing database writes by 30%.

**Execution Flow**:
1. Verifies template exists
2. Creates ExecutionRequest with template_id (no temporary definition!)
3. Executes through unified ExecutionEngine
4. Returns standardized WorkflowExecutionResponse

**Key Improvement**: No temporary definitions are created. Templates execute
directly through the ExecutionEngine, completing the Phase 4 optimization.

**Request Body**:
- `input_data`: Input parameters for the template
- `debug_mode`: Enable detailed logging (default: false)

**Response**: Same as workflow definition execution

**Example**:
```python
# Using Python SDK
result = client.workflows.execute_template(
    template_id="template_123",
    input_data={"query": "What is AI?"},
    debug_mode=False
)
print(f"Template executed successfully: {result.id}")
```
   */
  public async executeWorkflowTemplateApiV1WorkflowsTemplatesTemplateIdExecute(templateId: string, data: WorkflowTemplateExecutionRequest): Promise<WorkflowExecutionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates/${templateId}/execute`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowExecutionResponse>;
  }
  /**Execute Temporary Workflow Template
   * Execute a temporary workflow template directly without storing it.

This endpoint allows you to pass template data (nodes/edges) directly and execute it
without persisting the template to the database first.
   */
  public async executeTemporaryWorkflowTemplateApiV1WorkflowsTemplatesExecute(data: WorkflowTemplateDirectExecutionRequest): Promise<WorkflowExecutionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates/execute`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<WorkflowExecutionResponse>;
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
   * Execute a workflow definition using the unified execution engine.

**New in Phase 7**: This endpoint now uses the unified ExecutionEngine for all workflow
execution, providing consistent behavior and better performance.

**Execution Flow**:
1. Verifies workflow definition exists and user has access
2. Creates ExecutionRequest with definition_id and input_data
3. Executes through unified ExecutionEngine
4. Returns standardized WorkflowExecutionResponse

**Request Body**:
- `input_data`: Input parameters for the workflow
- `debug_mode`: Enable detailed logging (default: false)

**Response**:
- `id`: Execution ID for tracking
- `definition_id`: ID of the executed workflow definition
- `status`: Execution status (completed/failed)
- `output_data`: Workflow execution results
- `execution_time_ms`: Execution duration in milliseconds
- `tokens_used`: Total LLM tokens consumed
- `cost`: Execution cost in USD

**Example**:
```python
# Using Python SDK
result = client.workflows.execute_definition(
    workflow_id="def_123",
    input_data={"query": "Hello"},
    debug_mode=False
)
print(f"Execution {result.id} completed in {result.execution_time_ms}ms")
```
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
   * Validate a workflow definition using the unified validation orchestrator.

**New in Phase 7**: All validation now goes through the unified WorkflowValidator,
ensuring consistent validation across all 4 validation layers.

**Validation Layers**:
1. **Structure Validation**: Nodes, edges, connectivity, graph validity
2. **Security Validation**: Security policies, permissions, data access
3. **Capability Validation**: Feature support, capability limits
4. **Resource Validation**: Resource quotas, usage limits

**Request Body**:
- Can be WorkflowDefinitionCreate schema OR raw dict with nodes/edges
- Supports both legacy and modern formats

**Response**:
- `is_valid`: Overall validation result
- `errors`: List of validation errors from all layers
- `warnings`: Non-blocking warnings
- `metadata`: Additional validation details

**Example**:
```python
# Using Python SDK
result = client.workflows.validate_definition({
    "nodes": [...],
    "edges": [...]
})

if result.is_valid:
    print("Workflow is valid!")
else:
    for error in result.errors:
        print(f"Error: {error['message']}")
```
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
  /**List All Workflow Executions
   * List all workflow executions for the current user with pagination.
   */
  public async listAllWorkflowExecutionsApiV1WorkflowsExecutions(options?: { page?: number; pageSize?: number; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/executions`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'page': options?.page,
        'page_size': options?.pageSize,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
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
  public async executeChatWorkflowApiV1WorkflowsExecuteChat(data: ChatRequest): Promise<ChatResponse> {
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
  public async executeChatWorkflowStreamingApiV1WorkflowsExecuteChatStreaming(data: ChatRequest): Promise<ReadableStream<Uint8Array>> {
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
   * Execute a custom workflow definition using the modern unified execution engine.
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