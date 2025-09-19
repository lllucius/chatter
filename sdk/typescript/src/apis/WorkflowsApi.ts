/**
 * Generated API client for Workflows
 */
import { NodeTypeResponse, WorkflowAnalyticsResponse, WorkflowDefinitionCreate, WorkflowDefinitionResponse, WorkflowDefinitionUpdate, WorkflowDefinitionsResponse, WorkflowExecutionRequest, WorkflowExecutionResponse, WorkflowTemplateCreate, WorkflowTemplateResponse, WorkflowTemplateUpdate, WorkflowValidationResponse, chatter__schemas__workflows__WorkflowTemplatesResponse } from '../models/index';
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
  public async deleteWorkflowDefinitionApiV1WorkflowsDefinitionsWorkflowId(workflowId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/definitions/${workflowId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**List Workflow Templates
   * List all workflow templates accessible to the current user.
   */
  public async listWorkflowTemplatesApiV1WorkflowsTemplates(): Promise<chatter__schemas__workflows__WorkflowTemplatesResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<chatter__schemas__workflows__WorkflowTemplatesResponse>;
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
  public async deleteWorkflowTemplateApiV1WorkflowsTemplatesTemplateId(templateId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/workflows/templates/${templateId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
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
}