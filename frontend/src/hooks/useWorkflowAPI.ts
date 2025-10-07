/**
 * React Hook for Workflow Operations
 * 
 * Provides easy-to-use React hooks for workflow execution and validation
 * with built-in state management, loading, and error handling.
 */

import { useState, useCallback } from 'react';
import * as WorkflowAPI from '../services/workflow-api-service';
import type {
    WorkflowExecutionResponse,
    WorkflowValidationResponse,
    ExecutionRequest,
    WorkflowNode,
    WorkflowEdge,
} from '../services/workflow-api-service';

// ============================================================================
// Hook: useWorkflowExecution
// ============================================================================

interface UseWorkflowExecutionResult {
    execute: (workflowId: string, request: ExecutionRequest) => Promise<void>;
    result: WorkflowExecutionResponse | null;
    loading: boolean;
    error: string | null;
    reset: () => void;
}

/**
 * Hook for executing workflows with unified execution engine
 * 
 * Example:
 * ```tsx
 * const { execute, result, loading, error } = useWorkflowExecution();
 * 
 * const handleExecute = async () => {
 *   await execute('workflow_123', {
 *     inputData: { query: 'Hello' },
 *     debugMode: false
 *   });
 * };
 * ```
 */
export function useWorkflowExecution(): UseWorkflowExecutionResult {
    const [result, setResult] = useState<WorkflowExecutionResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const execute = useCallback(async (workflowId: string, request: ExecutionRequest) => {
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await WorkflowAPI.executeWorkflowDefinition(workflowId, request);
            setResult(response);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Execution failed';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setResult(null);
        setError(null);
        setLoading(false);
    }, []);

    return { execute, result, loading, error, reset };
}

// ============================================================================
// Hook: useTemplateExecution
// ============================================================================

interface UseTemplateExecutionResult {
    execute: (templateId: string, request: ExecutionRequest) => Promise<void>;
    result: WorkflowExecutionResponse | null;
    loading: boolean;
    error: string | null;
    reset: () => void;
}

/**
 * Hook for executing templates (no temporary definitions!)
 * 
 * Example:
 * ```tsx
 * const { execute, result, loading } = useTemplateExecution();
 * 
 * await execute('template_123', {
 *   inputData: { query: 'What is AI?' }
 * });
 * ```
 */
export function useTemplateExecution(): UseTemplateExecutionResult {
    const [result, setResult] = useState<WorkflowExecutionResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const execute = useCallback(async (templateId: string, request: ExecutionRequest) => {
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await WorkflowAPI.executeWorkflowTemplate(templateId, request);
            setResult(response);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Template execution failed';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setResult(null);
        setError(null);
        setLoading(false);
    }, []);

    return { execute, result, loading, error, reset };
}

// ============================================================================
// Hook: useWorkflowValidation
// ============================================================================

interface UseWorkflowValidationResult {
    validate: (workflow: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }) => Promise<void>;
    validation: WorkflowValidationResponse | null;
    loading: boolean;
    error: string | null;
    isValid: boolean;
    reset: () => void;
}

/**
 * Hook for workflow validation with 4-layer validation
 * 
 * Example:
 * ```tsx
 * const { validate, validation, isValid, loading } = useWorkflowValidation();
 * 
 * await validate({ nodes, edges });
 * 
 * if (isValid) {
 *   console.log('Valid!');
 * } else {
 *   validation.errors.forEach(e => console.error(e.message));
 * }
 * ```
 */
export function useWorkflowValidation(): UseWorkflowValidationResult {
    const [validation, setValidation] = useState<WorkflowValidationResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const validate = useCallback(async (workflow: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }) => {
        setLoading(true);
        setError(null);
        setValidation(null);

        try {
            const response = await WorkflowAPI.validateWorkflowDefinition(workflow);
            setValidation(response);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Validation failed';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setValidation(null);
        setError(null);
        setLoading(false);
    }, []);

    const isValid = validation?.isValid ?? false;

    return { validate, validation, loading, error, isValid, reset };
}

// ============================================================================
// Hook: useWorkflowWithValidation
// ============================================================================

interface UseWorkflowWithValidationResult {
    execute: (
        workflowId: string,
        request: ExecutionRequest,
        workflowData?: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }
    ) => Promise<void>;
    result: WorkflowExecutionResponse | null;
    validation: WorkflowValidationResponse | null;
    loading: boolean;
    error: string | null;
    reset: () => void;
}

/**
 * Hook for workflow execution with automatic validation
 * 
 * Validates the workflow before execution (if workflow data provided)
 * 
 * Example:
 * ```tsx
 * const { execute, result, validation } = useWorkflowWithValidation();
 * 
 * await execute('workflow_123', 
 *   { inputData: { query: 'Hello' } },
 *   { nodes, edges }  // Optional validation
 * );
 * ```
 */
export function useWorkflowWithValidation(): UseWorkflowWithValidationResult {
    const [result, setResult] = useState<WorkflowExecutionResponse | null>(null);
    const [validation, setValidation] = useState<WorkflowValidationResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const execute = useCallback(async (
        workflowId: string,
        request: ExecutionRequest,
        workflowData?: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }
    ) => {
        setLoading(true);
        setError(null);
        setResult(null);
        setValidation(null);

        try {
            const response = await WorkflowAPI.executeWorkflowWithValidation(
                workflowId,
                request,
                workflowData
            );
            setResult(response);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Execution failed';
            setError(errorMessage);
            
            // If error is validation-related, try to get validation details
            if (workflowData && errorMessage.includes('validation')) {
                try {
                    const validationResult = await WorkflowAPI.validateWorkflowDefinition(workflowData);
                    setValidation(validationResult);
                } catch {
                    // Ignore validation fetch error
                }
            }
            
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setResult(null);
        setValidation(null);
        setError(null);
        setLoading(false);
    }, []);

    return { execute, result, validation, loading, error, reset };
}

// ============================================================================
// Hook: useWorkflowDefinitions
// ============================================================================

interface UseWorkflowDefinitionsResult {
    definitions: any[];
    loading: boolean;
    error: string | null;
    refresh: () => Promise<void>;
    createDefinition: (workflow: any) => Promise<any>;
    updateDefinition: (id: string, workflow: any) => Promise<any>;
    deleteDefinition: (id: string) => Promise<void>;
}

/**
 * Hook for managing workflow definitions
 * 
 * Example:
 * ```tsx
 * const { definitions, loading, createDefinition } = useWorkflowDefinitions();
 * 
 * const handleCreate = async () => {
 *   await createDefinition({
 *     name: 'My Workflow',
 *     nodes: [...],
 *     edges: [...]
 *   });
 * };
 * ```
 */
export function useWorkflowDefinitions(): UseWorkflowDefinitionsResult {
    const [definitions, setDefinitions] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const refresh = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await WorkflowAPI.listWorkflowDefinitions();
            setDefinitions(response.definitions || []);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to load workflows';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    }, []);

    const createDefinition = useCallback(async (workflow: any) => {
        setLoading(true);
        setError(null);

        try {
            const created = await WorkflowAPI.createWorkflowDefinition(workflow);
            setDefinitions(prev => [...prev, created]);
            return created;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to create workflow';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const updateDefinition = useCallback(async (id: string, workflow: any) => {
        setLoading(true);
        setError(null);

        try {
            const updated = await WorkflowAPI.updateWorkflowDefinition(id, workflow);
            setDefinitions(prev => prev.map(d => d.id === id ? updated : d));
            return updated;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to update workflow';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const deleteDefinition = useCallback(async (id: string) => {
        setLoading(true);
        setError(null);

        try {
            await WorkflowAPI.deleteWorkflowDefinition(id);
            setDefinitions(prev => prev.filter(d => d.id !== id));
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to delete workflow';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        definitions,
        loading,
        error,
        refresh,
        createDefinition,
        updateDefinition,
        deleteDefinition,
    };
}
