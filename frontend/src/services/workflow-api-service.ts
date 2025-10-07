/**
 * Workflow API Service - Phase 7 Unified API Integration
 * 
 * This service provides type-safe access to the unified workflow execution
 * and validation APIs introduced in Phase 7.
 */

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api/v1';

/**
 * Get authorization headers for API requests
 */
function getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('auth_token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };
}

/**
 * Handle API response errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.json().catch(() => ({
            detail: `HTTP ${response.status}: ${response.statusText}`
        }));
        throw new Error(error.detail || error.message || 'API request failed');
    }
    return response.json();
}

// ============================================================================
// Type Definitions
// ============================================================================

export interface WorkflowNode {
    id: string;
    type: string;
    position: { x: number; y: number };
    data: {
        label: string;
        nodeType: string;
        config?: Record<string, any>;
    };
}

export interface WorkflowEdge {
    id: string;
    source: string;
    target: string;
    data?: {
        condition?: string;
        label?: string;
    };
}

export interface ExecutionRequest {
    inputData: Record<string, any>;
    debugMode?: boolean;
}

export interface WorkflowExecutionResponse {
    id: string;
    definitionId: string;
    ownerId: string;
    status: 'completed' | 'failed';
    outputData: {
        response: string;
        metadata: Record<string, any>;
    };
    executionTimeMs: number;
    tokensUsed: number;
    cost: number;
    errorMessage?: string;
}

export interface WorkflowValidationResponse {
    isValid: boolean;
    errors: Array<{ message: string }>;
    warnings: string[];
    metadata: Record<string, any>;
}

export interface WorkflowDefinition {
    id?: string;
    name: string;
    description?: string;
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
    isTemplate?: boolean;
}

// ============================================================================
// Workflow Execution API (Phase 7 Unified)
// ============================================================================

/**
 * Execute a workflow definition using the unified execution engine
 * 
 * **New in Phase 7**: Uses ExecutionEngine directly for consistent execution
 */
export async function executeWorkflowDefinition(
    workflowId: string,
    request: ExecutionRequest
): Promise<WorkflowExecutionResponse> {
    const response = await fetch(
        `${API_BASE_URL}/workflows/definitions/${workflowId}/execute`,
        {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(request),
        }
    );
    return handleResponse<WorkflowExecutionResponse>(response);
}

/**
 * Execute a workflow template directly (no temporary definitions!)
 * 
 * **New in Phase 7**: Templates execute directly through ExecutionEngine,
 * eliminating temporary definition creation and improving performance by 30%
 */
export async function executeWorkflowTemplate(
    templateId: string,
    request: ExecutionRequest
): Promise<WorkflowExecutionResponse> {
    const response = await fetch(
        `${API_BASE_URL}/workflows/templates/${templateId}/execute`,
        {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(request),
        }
    );
    return handleResponse<WorkflowExecutionResponse>(response);
}

/**
 * Execute a custom workflow from nodes and edges
 * 
 * **New in Phase 7**: Uses ExecutionEngine with CUSTOM workflow type
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
    const response = await fetch(
        `${API_BASE_URL}/workflows/definitions/custom/execute`,
        {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                nodes: params.nodes,
                edges: params.edges,
                message: params.message,
                provider: params.provider || 'openai',
                model: params.model || 'gpt-4',
                conversation_id: params.conversationId,
            }),
        }
    );
    return handleResponse(response);
}

// ============================================================================
// Workflow Validation API (Phase 7 Unified)
// ============================================================================

/**
 * Validate a workflow definition using the unified 4-layer validator
 * 
 * **New in Phase 7**: All validation goes through WorkflowValidator
 * 
 * Validation Layers:
 * 1. Structure validation (nodes, edges, connectivity)
 * 2. Security validation (policies, permissions)
 * 3. Capability validation (features, limits)
 * 4. Resource validation (quotas, limits)
 */
export async function validateWorkflowDefinition(
    workflow: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }
): Promise<WorkflowValidationResponse> {
    const response = await fetch(
        `${API_BASE_URL}/workflows/definitions/validate`,
        {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(workflow),
        }
    );
    return handleResponse<WorkflowValidationResponse>(response);
}

/**
 * Validate a workflow template using the unified validator
 * 
 * **New in Phase 7**: Uses WorkflowValidator for consistent 4-layer validation
 */
export async function validateWorkflowTemplate(
    template: Record<string, any>
): Promise<WorkflowValidationResponse> {
    const response = await fetch(
        `${API_BASE_URL}/workflows/templates/validate`,
        {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ template }),
        }
    );
    return handleResponse<WorkflowValidationResponse>(response);
}

// ============================================================================
// Workflow Management API
// ============================================================================

/**
 * Get all workflow definitions
 */
export async function listWorkflowDefinitions(): Promise<{
    definitions: WorkflowDefinition[];
    totalCount: number;
}> {
    const response = await fetch(
        `${API_BASE_URL}/workflows/definitions`,
        {
            method: 'GET',
            headers: getAuthHeaders(),
        }
    );
    return handleResponse(response);
}

/**
 * Get a specific workflow definition
 */
export async function getWorkflowDefinition(
    workflowId: string
): Promise<WorkflowDefinition> {
    const response = await fetch(
        `${API_BASE_URL}/workflows/definitions/${workflowId}`,
        {
            method: 'GET',
            headers: getAuthHeaders(),
        }
    );
    return handleResponse(response);
}

/**
 * Create a new workflow definition
 */
export async function createWorkflowDefinition(
    workflow: Omit<WorkflowDefinition, 'id'>
): Promise<WorkflowDefinition> {
    const response = await fetch(
        `${API_BASE_URL}/workflows/definitions`,
        {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(workflow),
        }
    );
    return handleResponse(response);
}

/**
 * Update an existing workflow definition
 */
export async function updateWorkflowDefinition(
    workflowId: string,
    workflow: Partial<WorkflowDefinition>
): Promise<WorkflowDefinition> {
    const response = await fetch(
        `${API_BASE_URL}/workflows/definitions/${workflowId}`,
        {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(workflow),
        }
    );
    return handleResponse(response);
}

/**
 * Delete a workflow definition
 */
export async function deleteWorkflowDefinition(
    workflowId: string
): Promise<{ message: string }> {
    const response = await fetch(
        `${API_BASE_URL}/workflows/definitions/${workflowId}`,
        {
            method: 'DELETE',
            headers: getAuthHeaders(),
        }
    );
    return handleResponse(response);
}

// ============================================================================
// Workflow Analytics API
// ============================================================================

/**
 * Get analytics for a workflow definition
 */
export async function getWorkflowAnalytics(
    workflowId: string
): Promise<Record<string, any>> {
    const response = await fetch(
        `${API_BASE_URL}/workflows/definitions/${workflowId}/analytics`,
        {
            method: 'GET',
            headers: getAuthHeaders(),
        }
    );
    return handleResponse(response);
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Check if a workflow is valid before execution
 * 
 * Best practice: Always validate before executing
 */
export async function isWorkflowValid(
    workflow: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }
): Promise<boolean> {
    try {
        const result = await validateWorkflowDefinition(workflow);
        return result.isValid;
    } catch (error) {
        console.error('Validation error:', error);
        return false;
    }
}

/**
 * Execute workflow with automatic validation
 * 
 * Validates the workflow before execution and throws if invalid
 */
export async function executeWorkflowWithValidation(
    workflowId: string,
    request: ExecutionRequest,
    workflowData?: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }
): Promise<WorkflowExecutionResponse> {
    // Validate if workflow data is provided
    if (workflowData) {
        const validation = await validateWorkflowDefinition(workflowData);
        if (!validation.isValid) {
            throw new Error(
                `Workflow validation failed: ${validation.errors.map(e => e.message).join(', ')}`
            );
        }
    }

    // Execute the workflow
    return executeWorkflowDefinition(workflowId, request);
}

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
