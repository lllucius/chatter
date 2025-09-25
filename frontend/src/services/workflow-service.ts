/**
 * Workflow service for managing workflow definitions, templates, and execution
 * Uses ChatterSDK for API communication
 */
import { ChatterSDK } from 'chatter-sdk';
import { authService } from './auth-service';
import { handleError } from '../utils/error-handler';
import { WorkflowDefinition, WorkflowTemplate, ValidationResult } from '../components/workflow/types';

export interface WorkflowSaveRequest {
  name: string;
  description?: string;
  nodes: any[];
  edges: any[];
  metadata?: Record<string, any>;
  isPublic?: boolean;
  tags?: string[];
}

export interface WorkflowUpdateRequest extends Partial<WorkflowSaveRequest> {
  id: string;
}

export interface WorkflowExecutionRequest {
  workflowId: string;
  inputData?: Record<string, any>;
}

class WorkflowService {
  /**
   * Get authenticated SDK instance
   */
  private async getSDK(): Promise<ChatterSDK> {
    try {
      return await authService.getAuthenticatedSDK();
    } catch (error) {
      throw handleError(error, { 
        source: 'WorkflowService.getAuthenticatedSDK',
        operation: 'Getting authenticated SDK instance'
      });
    }
  }

  /**
   * List all workflow definitions for the current user
   */
  async listWorkflows(): Promise<WorkflowDefinition[]> {
    try {
      const sdk = await this.getSDK();
      const response = await sdk.workflows.listWorkflowDefinitionsApiV1WorkflowsDefinitions();
      
      return response.definitions.map(this.mapApiResponseToWorkflowDefinition);
    } catch (error) {
      throw handleError(error, { 
        source: 'WorkflowService.listWorkflows',
        operation: 'Loading workflow list'
      });
    }
  }

  /**
   * Get a specific workflow definition
   */
  async getWorkflow(workflowId: string): Promise<WorkflowDefinition> {
    try {
      const sdk = await this.getSDK();
      const response = await sdk.workflows.getWorkflowDefinitionApiV1WorkflowsDefinitionsWorkflowId(workflowId);
      
      return this.mapApiResponseToWorkflowDefinition(response);
    } catch (error) {
      throw handleError(error, { 
        source: 'WorkflowService.getWorkflow',
        operation: 'Loading workflow definition'
      });
    }
  }

  /**
   * Create a new workflow definition
   */
  async createWorkflow(request: WorkflowSaveRequest): Promise<WorkflowDefinition> {
    try {
      const sdk = await this.getSDK();
      
      const createRequest = {
        name: request.name,
        description: request.description || '',
        nodes: request.nodes,
        edges: request.edges,
        metadata: request.metadata || {},
        is_public: request.isPublic || false,
        tags: request.tags || [],
      };

      const response = await sdk.workflows.createWorkflowDefinitionApiV1WorkflowsDefinitions(createRequest);
      
      return this.mapApiResponseToWorkflowDefinition(response);
    } catch (error) {
      throw handleError(error, { 
        source: 'WorkflowService.createWorkflow',
        operation: 'Creating workflow definition'
      });
    }
  }

  /**
   * Update an existing workflow definition
   */
  async updateWorkflow(request: WorkflowUpdateRequest): Promise<WorkflowDefinition> {
    try {
      const sdk = await this.getSDK();
      
      const updateRequest = {
        name: request.name,
        description: request.description,
        nodes: request.nodes,
        edges: request.edges,
        metadata: request.metadata,
      };

      // Remove undefined values
      Object.keys(updateRequest).forEach(key => {
        if ((updateRequest as any)[key] === undefined) {
          delete (updateRequest as any)[key];
        }
      });

      const response = await sdk.workflows.updateWorkflowDefinitionApiV1WorkflowsDefinitionsWorkflowId(
        request.id, 
        updateRequest
      );
      
      return this.mapApiResponseToWorkflowDefinition(response);
    } catch (error) {
      throw handleError(error, { 
        source: 'WorkflowService.updateWorkflow',
        operation: 'Updating workflow definition'
      });
    }
  }

  /**
   * Delete a workflow definition
   */
  async deleteWorkflow(workflowId: string): Promise<void> {
    try {
      const sdk = await this.getSDK();
      await sdk.workflows.deleteWorkflowDefinitionApiV1WorkflowsDefinitionsWorkflowId(workflowId);
    } catch (error) {
      throw handleError(error, { 
        source: 'WorkflowService.deleteWorkflow',
        operation: 'Deleting workflow definition'
      });
    }
  }

  /**
   * Validate a workflow definition
   */
  async validateWorkflow(workflow: WorkflowDefinition): Promise<ValidationResult> {
    try {
      const sdk = await this.getSDK();
      
      const validationRequest = {
        nodes: workflow.nodes,
        edges: workflow.edges,
        metadata: workflow.metadata,
      };

      const response = await sdk.workflows.validateWorkflowDefinitionApiV1WorkflowsDefinitionsValidate(validationRequest);
      
      return {
        isValid: response.is_valid,
        errors: (response.errors || []).map(error => ({
          type: 'error' as const,
          nodeId: (error as any).node_id,
          edgeId: (error as any).edge_id,
          message: (error as any).message || 'Validation error',
          code: (error as any).code || 'VALIDATION_ERROR',
          severity: (error as any).severity || 'medium' as const,
        })),
        warnings: (response.warnings || []).map(warning => ({
          type: 'warning' as const,
          nodeId: (warning as any).node_id,
          edgeId: (warning as any).edge_id,
          message: (warning as any).message || 'Validation warning',
          code: (warning as any).code || 'VALIDATION_WARNING',
        })),
        suggestions: (response.suggestions || []).map(suggestion => 
          typeof suggestion === 'string' 
            ? { type: 'suggestion' as const, message: suggestion, action: '' }
            : { 
                type: 'suggestion' as const, 
                message: (suggestion as any).message || 'Suggestion',
                action: (suggestion as any).action || '',
              }
        ),
      };
    } catch (error) {
      // If validation endpoint fails, fall back to client-side validation
      console.warn('Server validation failed, using client-side validation:', error);
      return this.clientSideValidation(workflow);
    }
  }

  /**
   * Execute a workflow
   */
  async executeWorkflow(request: WorkflowExecutionRequest): Promise<any> {
    try {
      const sdk = await this.getSDK();
      
      const executionRequest = {
        definition_id: request.workflowId,
        input_data: request.inputData || {},
      };

      const response = await sdk.workflows.executeWorkflowApiV1WorkflowsDefinitionsWorkflowIdExecute(
        request.workflowId,
        executionRequest
      );
      
      return response;
    } catch (error) {
      throw handleError(error, { 
        source: 'WorkflowService.executeWorkflow',
        operation: 'Executing workflow'
      });
    }
  }

  /**
   * Get workflow analytics
   */
  async getWorkflowAnalytics(workflowId: string): Promise<any> {
    try {
      const sdk = await this.getSDK();
      const response = await sdk.workflows.getWorkflowAnalyticsApiV1WorkflowsDefinitionsWorkflowIdAnalytics(workflowId);
      return response;
    } catch (error) {
      throw handleError(error, { 
        source: 'WorkflowService.getWorkflowAnalytics',
        operation: 'Loading workflow analytics'
      });
    }
  }

  /**
   * Get supported node types
   */
  async getSupportedNodeTypes(): Promise<any[]> {
    try {
      const sdk = await this.getSDK();
      const response = await sdk.workflows.getSupportedNodeTypesApiV1WorkflowsNodeTypes();
      return response;
    } catch (error) {
      // If API fails, return empty array (node types are also defined locally)
      console.warn('Failed to load node types from API:', error);
      return [];
    }
  }

  /**
   * List workflow templates
   */
  async listTemplates(): Promise<any[]> {
    try {
      const sdk = await this.getSDK();
      const response = await sdk.workflows.listWorkflowTemplatesApiV1WorkflowsTemplates();
      return response.templates || [];
    } catch (error) {
      throw handleError(error, { 
        source: 'WorkflowService.listTemplates',
        operation: 'Loading workflow templates'
      });
    }
  }

  /**
   * Create workflow from template
   */
  async createFromTemplate(templateId: string, name?: string): Promise<WorkflowDefinition> {
    try {
      const sdk = await this.getSDK();
      
      const request = {
        template_id: templateId,
        name: name || `Workflow from ${templateId}`,
      };

      const response = await sdk.workflows.createWorkflowDefinitionFromTemplateApiV1WorkflowsDefinitionsFromTemplate(request);
      
      return this.mapApiResponseToWorkflowDefinition(response);
    } catch (error) {
      throw handleError(error, { 
        source: 'WorkflowService.createFromTemplate',
        operation: 'Creating workflow from template'
      });
    }
  }

  /**
   * Map API response to our internal WorkflowDefinition type
   */
  private mapApiResponseToWorkflowDefinition(apiResponse: any): WorkflowDefinition {
    return {
      id: apiResponse.id,
      nodes: apiResponse.nodes || [],
      edges: apiResponse.edges || [],
      metadata: {
        name: apiResponse.name,
        description: apiResponse.description || '',
        version: apiResponse.version?.toString() || '1.0.0',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        tags: apiResponse.tags || [],
        ...apiResponse.metadata,
      },
      version: apiResponse.version?.toString() || '1.0.0',
      variables: {},
      settings: {
        autoSave: true,
        autoSaveInterval: 30000,
        enableValidation: true,
        enableAnalytics: true,
      },
    };
  }

  /**
   * Client-side validation fallback
   */
  private clientSideValidation(workflow: WorkflowDefinition): ValidationResult {
    const errors: any[] = [];
    const warnings: any[] = [];
    const suggestions: any[] = [];

    // Basic validation checks
    if (!workflow.nodes || workflow.nodes.length === 0) {
      errors.push({
        type: 'error',
        message: 'Workflow must have at least one node',
        code: 'NO_NODES',
        severity: 'high',
      });
    }

    // Check for start nodes
    const startNodes = workflow.nodes.filter(node => node.type === 'start');
    if (startNodes.length === 0) {
      errors.push({
        type: 'error',
        message: 'Workflow must have at least one start node',
        code: 'NO_START_NODE',
        severity: 'high',
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      suggestions,
    };
  }
}

// Export singleton instance
export const workflowService = new WorkflowService();
export default workflowService;