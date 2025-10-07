/**
 * Workflow Service - SDK-based Workflow Operations
 * 
 * This service provides type-safe access to workflow operations using the TypeScript SDK.
 * Replaces the old workflow-api-service.ts with SDK-based implementations.
 */

import { getSDK } from './auth-service';
import { handleError } from '../utils/error-handler';
import type {
  WorkflowExecutionRequest,
  WorkflowExecutionResponse,
  WorkflowDefinitionCreate,
  WorkflowDefinitionUpdate,
  WorkflowDefinitionResponse,
  WorkflowDefinitionsResponse,
  WorkflowValidationResponse,
  WorkflowNode,
  WorkflowEdge,
  WorkflowAnalyticsResponse,
  WorkflowTemplateExecutionRequest,
  Body_execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post,
  WorkflowDeleteResponse,
} from 'chatter-sdk';

// ============================================================================
// Type Definitions (for backward compatibility)
// ============================================================================

export interface ExecutionRequest {
  inputData: Record<string, any>;
  debugMode?: boolean;
}

export interface WorkflowDefinition {
  id?: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  isTemplate?: boolean;
  metadata?: Record<string, any>;
  isPublic?: boolean;
  tags?: string[];
  templateId?: string;
}

// ============================================================================
// Workflow Execution API
// ============================================================================

/**
 * Execute a workflow definition using the SDK
 */
export async function executeWorkflowDefinition(
  workflowId: string,
  request: ExecutionRequest
): Promise<WorkflowExecutionResponse> {
  try {
    const sdk = getSDK();
    const executionRequest: WorkflowExecutionRequest = {
      definition_id: workflowId,
      input_data: request.inputData,
      debug_mode: request.debugMode,
    };
    
    const response = await sdk.workflows.executeWorkflowApiV1WorkflowsDefinitionsWorkflowIdExecute(
      workflowId,
      executionRequest
    );
    
    return response;
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.executeWorkflowDefinition',
      operation: 'workflow execution',
      additionalData: { workflowId },
    });
    throw error;
  }
}

/**
 * Execute a workflow template directly (no temporary definitions!)
 */
export async function executeWorkflowTemplate(
  templateId: string,
  request: ExecutionRequest
): Promise<WorkflowExecutionResponse> {
  try {
    const sdk = getSDK();
    const executionRequest: WorkflowTemplateExecutionRequest = {
      input_data: request.inputData,
      debug_mode: request.debugMode,
    };
    
    const response = await sdk.workflows.executeWorkflowTemplateApiV1WorkflowsTemplatesTemplateIdExecute(
      templateId,
      executionRequest
    );
    
    return response;
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.executeWorkflowTemplate',
      operation: 'template execution',
      additionalData: { templateId },
    });
    throw error;
  }
}

/**
 * Execute a custom workflow from nodes and edges
 */
export async function executeCustomWorkflow(params: {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  message: string;
  provider?: string;
  model?: string;
  conversationId?: string;
}): Promise<{
  response: string;
  metadata: Record<string, any>;
  executionSummary: {
    executionId: string;
    toolCalls: number;
  };
  tokensUsed: number;
  promptTokens: number;
  completionTokens: number;
  cost: number;
}> {
  try {
    const sdk = getSDK();
    const body: Body_execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post = {
      nodes: params.nodes as unknown as Record<string, unknown>[],
      edges: params.edges as unknown as Record<string, unknown>[],
    };
    
    const response = await sdk.workflows.executeCustomWorkflowApiV1WorkflowsDefinitionsCustomExecute(
      body,
      {
        message: params.message,
        provider: params.provider || 'openai',
        model: params.model || 'gpt-4',
        conversationId: params.conversationId,
      }
    );
    
    return response as any;
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.executeCustomWorkflow',
      operation: 'custom workflow execution',
    });
    throw error;
  }
}

// ============================================================================
// Workflow Validation API
// ============================================================================

/**
 * Validate a workflow definition using the SDK
 */
export async function validateWorkflowDefinition(
  workflow: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }
): Promise<WorkflowValidationResponse> {
  try {
    const sdk = getSDK();
    const response = await sdk.workflows.validateWorkflowDefinitionApiV1WorkflowsDefinitionsValidate(
      workflow as any
    );
    
    return response;
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.validateWorkflowDefinition',
      operation: 'workflow validation',
    });
    throw error;
  }
}

/**
 * Validate a workflow template using the SDK
 */
export async function validateWorkflowTemplate(
  template: Record<string, any>
): Promise<WorkflowValidationResponse> {
  try {
    const sdk = getSDK();
    const response = await sdk.workflows.validateWorkflowTemplateApiV1WorkflowsTemplatesValidate({
      template,
    });
    
    return response as unknown as WorkflowValidationResponse;
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.validateWorkflowTemplate',
      operation: 'template validation',
    });
    throw error;
  }
}

// ============================================================================
// Workflow Management API
// ============================================================================

/**
 * Get all workflow definitions using the SDK
 */
export async function listWorkflowDefinitions(): Promise<{
  definitions: WorkflowDefinition[];
  totalCount: number;
}> {
  try {
    const sdk = getSDK();
    const response = await sdk.workflows.listWorkflowDefinitionsApiV1WorkflowsDefinitions();
    
    return {
      definitions: response.definitions as unknown as WorkflowDefinition[],
      totalCount: response.total_count,
    };
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.listWorkflowDefinitions',
      operation: 'list workflows',
    });
    throw error;
  }
}

/**
 * Get a specific workflow definition using the SDK
 */
export async function getWorkflowDefinition(
  workflowId: string
): Promise<WorkflowDefinition> {
  try {
    const sdk = getSDK();
    const response = await sdk.workflows.getWorkflowDefinitionApiV1WorkflowsDefinitionsWorkflowId(workflowId);
    
    return response as unknown as WorkflowDefinition;
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.getWorkflowDefinition',
      operation: 'get workflow',
      additionalData: { workflowId },
    });
    throw error;
  }
}

/**
 * Create a new workflow definition using the SDK
 */
export async function createWorkflowDefinition(
  workflow: Omit<WorkflowDefinition, 'id'>
): Promise<WorkflowDefinition> {
  try {
    const sdk = getSDK();
    const workflowCreate: WorkflowDefinitionCreate = {
      name: workflow.name,
      description: workflow.description || null,
      nodes: workflow.nodes,
      edges: workflow.edges,
      metadata: workflow.metadata || null,
      is_public: workflow.isPublic,
      tags: workflow.tags || null,
      template_id: workflow.templateId || null,
    };
    
    const response = await sdk.workflows.createWorkflowDefinitionApiV1WorkflowsDefinitions(workflowCreate);
    
    return response as unknown as WorkflowDefinition;
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.createWorkflowDefinition',
      operation: 'create workflow',
    });
    throw error;
  }
}

/**
 * Update an existing workflow definition using the SDK
 */
export async function updateWorkflowDefinition(
  workflowId: string,
  workflow: Partial<WorkflowDefinition>
): Promise<WorkflowDefinition> {
  try {
    const sdk = getSDK();
    const workflowUpdate: WorkflowDefinitionUpdate = {
      name: workflow.name,
      description: workflow.description,
      nodes: workflow.nodes,
      edges: workflow.edges,
      metadata: workflow.metadata,
    };
    
    const response = await sdk.workflows.updateWorkflowDefinitionApiV1WorkflowsDefinitionsWorkflowId(
      workflowId,
      workflowUpdate
    );
    
    return response as unknown as WorkflowDefinition;
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.updateWorkflowDefinition',
      operation: 'update workflow',
      additionalData: { workflowId },
    });
    throw error;
  }
}

/**
 * Delete a workflow definition using the SDK
 */
export async function deleteWorkflowDefinition(
  workflowId: string
): Promise<{ message: string }> {
  try {
    const sdk = getSDK();
    const response = await sdk.workflows.deleteWorkflowDefinitionApiV1WorkflowsDefinitionsWorkflowId(workflowId);
    
    return { message: response.message || 'Workflow deleted successfully' };
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.deleteWorkflowDefinition',
      operation: 'delete workflow',
      additionalData: { workflowId },
    });
    throw error;
  }
}

// ============================================================================
// Workflow Analytics API
// ============================================================================

/**
 * Get analytics for a workflow definition using the SDK
 */
export async function getWorkflowAnalytics(
  workflowId: string
): Promise<Record<string, any>> {
  try {
    const sdk = getSDK();
    const response = await sdk.workflows.getWorkflowAnalyticsApiV1WorkflowsDefinitionsWorkflowIdAnalytics(workflowId);
    
    return response as Record<string, any>;
  } catch (error) {
    handleError(error, {
      source: 'WorkflowService.getWorkflowAnalytics',
      operation: 'get workflow analytics',
      additionalData: { workflowId },
    });
    throw error;
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Check if a workflow is valid before execution
 */
export async function isWorkflowValid(
  workflow: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }
): Promise<boolean> {
  try {
    const result = await validateWorkflowDefinition(workflow);
    return result.is_valid;
  } catch (error) {
    console.error('Validation error:', error);
    return false;
  }
}

/**
 * Execute workflow with automatic validation
 */
export async function executeWorkflowWithValidation(
  workflowId: string,
  request: ExecutionRequest,
  workflowData?: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }
): Promise<WorkflowExecutionResponse> {
  // Validate if workflow data is provided
  if (workflowData) {
    const validation = await validateWorkflowDefinition(workflowData);
    if (!validation.is_valid) {
      throw new Error(
        `Workflow validation failed: ${validation.errors.map(e => e.msg).join(', ')}`
      );
    }
  }

  // Execute the workflow
  return executeWorkflowDefinition(workflowId, request);
}

// Export default object with all methods
export default {
  // Execution
  executeWorkflowDefinition,
  executeWorkflowTemplate,
  executeCustomWorkflow,
  executeWorkflowWithValidation,
  
  // Validation
  validateWorkflowDefinition,
  validateWorkflowTemplate,
  isWorkflowValid,
  
  // Management
  listWorkflowDefinitions,
  getWorkflowDefinition,
  createWorkflowDefinition,
  updateWorkflowDefinition,
  deleteWorkflowDefinition,
  
  // Analytics
  getWorkflowAnalytics,
};
