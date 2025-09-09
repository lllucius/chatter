/**
 * Generated API client for Workflows
 */
import { NodeTypeResponse, WorkflowAnalyticsResponse, WorkflowDefinitionCreate, WorkflowDefinitionResponse, WorkflowDefinitionUpdate, WorkflowDefinitionsResponse, WorkflowExecutionRequest, WorkflowExecutionResponse, WorkflowTemplateCreate, WorkflowTemplateResponse, WorkflowTemplateUpdate, WorkflowValidationResponse, chatter__schemas__workflows__WorkflowTemplatesResponse } from '../models/index';
import { BaseAPI, Configuration } from '../runtime';

export class WorkflowsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**List Workflow Definitions
   * List all workflow definitions for the current user.
   */
  public async listWorkflowDefinitionsApiV1WorkflowsWorkflowsDefinitions(): Promise<WorkflowDefinitionsResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<WorkflowDefinitionsResponse>(`/api/v1/workflows/workflows/definitions`, requestOptions);
  }
  /**Create Workflow Definition
   * Create a new workflow definition.
   */
  public async createWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitions(data: WorkflowDefinitionCreate): Promise<WorkflowDefinitionResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<WorkflowDefinitionResponse>(`/api/v1/workflows/workflows/definitions`, requestOptions);
  }
  /**Get Workflow Definition
   * Get a specific workflow definition.
   */
  public async getWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowId(workflowId: string): Promise<WorkflowDefinitionResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<WorkflowDefinitionResponse>(`/api/v1/workflows/workflows/definitions/${workflowId}`, requestOptions);
  }
  /**Update Workflow Definition
   * Update a workflow definition.
   */
  public async updateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowId(workflowId: string, data: WorkflowDefinitionUpdate): Promise<WorkflowDefinitionResponse> {
    const requestOptions = {
      method: 'PUT' as const,
      body: data,
    };

    return this.request<WorkflowDefinitionResponse>(`/api/v1/workflows/workflows/definitions/${workflowId}`, requestOptions);
  }
  /**Delete Workflow Definition
   * Delete a workflow definition.
   */
  public async deleteWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowId(workflowId: string): Promise<Record<string, unknown>> {
    const requestOptions = {
      method: 'DELETE' as const,
    };

    return this.request<Record<string, unknown>>(`/api/v1/workflows/workflows/definitions/${workflowId}`, requestOptions);
  }
  /**List Workflow Templates
   * List all workflow templates accessible to the current user.
   */
  public async listWorkflowTemplatesApiV1WorkflowsWorkflowsTemplates(): Promise<chatter__schemas__workflows__WorkflowTemplatesResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<chatter__schemas__workflows__WorkflowTemplatesResponse>(`/api/v1/workflows/workflows/templates`, requestOptions);
  }
  /**Create Workflow Template
   * Create a new workflow template.
   */
  public async createWorkflowTemplateApiV1WorkflowsWorkflowsTemplates(data: WorkflowTemplateCreate): Promise<WorkflowTemplateResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<WorkflowTemplateResponse>(`/api/v1/workflows/workflows/templates`, requestOptions);
  }
  /**Update Workflow Template
   * Update a workflow template.
   */
  public async updateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesTemplateId(templateId: string, data: WorkflowTemplateUpdate): Promise<WorkflowTemplateResponse> {
    const requestOptions = {
      method: 'PUT' as const,
      body: data,
    };

    return this.request<WorkflowTemplateResponse>(`/api/v1/workflows/workflows/templates/${templateId}`, requestOptions);
  }
  /**Get Workflow Analytics
   * Get analytics for a specific workflow definition.
   */
  public async getWorkflowAnalyticsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdAnalytics(workflowId: string): Promise<WorkflowAnalyticsResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<WorkflowAnalyticsResponse>(`/api/v1/workflows/workflows/definitions/${workflowId}/analytics`, requestOptions);
  }
  /**Execute Workflow
   * Execute a workflow definition.
   */
  public async executeWorkflowApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecute(workflowId: string, data: WorkflowExecutionRequest): Promise<WorkflowExecutionResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<WorkflowExecutionResponse>(`/api/v1/workflows/workflows/definitions/${workflowId}/execute`, requestOptions);
  }
  /**Validate Workflow Definition
   * Validate a workflow definition.
   */
  public async validateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsValidate(data: WorkflowDefinitionCreate): Promise<WorkflowValidationResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<WorkflowValidationResponse>(`/api/v1/workflows/workflows/definitions/validate`, requestOptions);
  }
  /**Get Supported Node Types
   * Get list of supported workflow node types.
   */
  public async getSupportedNodeTypesApiV1WorkflowsWorkflowsNodeTypes(): Promise<NodeTypeResponse[]> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<NodeTypeResponse[]>(`/api/v1/workflows/workflows/node-types`, requestOptions);
  }
  /**List Workflow Executions
   * List executions for a workflow definition.
   */
  public async listWorkflowExecutionsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutions(workflowId: string): Promise<WorkflowExecutionResponse[]> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<WorkflowExecutionResponse[]>(`/api/v1/workflows/workflows/definitions/${workflowId}/executions`, requestOptions);
  }
}