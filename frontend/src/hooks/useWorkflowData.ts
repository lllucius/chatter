import { useState, useEffect, useCallback } from 'react';
import { getSDK } from '../services/auth-service';
import { handleError } from '../utils/error-handler';
import {
  WorkflowTemplateResponse,
  ServerToolsResponse,
  WorkflowExecutionResponse,
  WorkflowExecutionRequest,
} from 'chatter-sdk';

// Use the SDK types directly
type WorkflowTemplate = WorkflowTemplateResponse;
type WorkflowExecution = WorkflowExecutionResponse;

export const useWorkflowData = () => {
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [availableTools, setAvailableTools] =
    useState<ServerToolsResponse | null>(null);
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);

  const loadTemplates = useCallback(async () => {
    try {
      setLoading(true);
      const response =
        await getSDK().workflows.listWorkflowTemplatesApiV1WorkflowsTemplates();
      setTemplates(response.templates || []);
    } catch (error) {
      handleError(error, {
        source: 'useWorkflowData.loadTemplates',
        operation: 'load workflow templates',
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const loadAvailableTools = useCallback(async () => {
    try {
      // For now, set available tools to null since there's no direct tools API
      // This prevents the console warning and provides a proper state
      setAvailableTools(null);
    } catch (error) {
      handleError(error, {
        source: 'useWorkflowData.loadAvailableTools',
        operation: 'load available tools',
      });
      setAvailableTools(null);
    }
  }, []);

  const loadExecutions = useCallback(async (workflowId?: string) => {
    try {
      if (!workflowId) {
        // Workflow executions require specific workflow ID
        setExecutions([]);
        return;
      }

      const response =
        await getSDK().workflows.listWorkflowExecutionsApiV1WorkflowsDefinitionsWorkflowIdExecutions(
          workflowId
        );
      setExecutions(response || []);
    } catch (error) {
      handleError(error, {
        source: 'useWorkflowData.loadExecutions',
        operation: 'load workflow executions',
      });
    }
  }, []);

  const createTemplate = useCallback(
    async (templateData: WorkflowTemplateResponse) => {
      try {
        setLoading(true);
        const newTemplate =
          await getSDK().workflows.createWorkflowTemplateApiV1WorkflowsTemplates(
            templateData
          );
        setTemplates((prev) => [newTemplate, ...prev]);
        return newTemplate;
      } catch (error) {
        handleError(error, {
          source: 'useWorkflowData.createTemplate',
          operation: 'create workflow template',
        });
        throw error;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const executeWorkflow = useCallback(
    async (workflowId: string, input: Record<string, unknown>) => {
      try {
        setLoading(true);
        const requestData: WorkflowExecutionRequest = {
          definition_id: workflowId,
          input_data: input,
        };
        const execution =
          await getSDK().workflows.executeWorkflowApiV1WorkflowsDefinitionsWorkflowIdExecute(
            workflowId,
            requestData
          );
        setExecutions((prev) => [execution, ...prev]);
        return execution;
      } catch (error) {
        handleError(error, {
          source: 'useWorkflowData.executeWorkflow',
          operation: 'execute workflow',
        });
        throw error;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const executeTemplate = useCallback(
    async (templateId: string, input: Record<string, unknown>) => {
      try {
        setLoading(true);

        // Step 1: Create a workflow definition from the template
        const createRequest = {
          template_id: templateId,
          user_input: input,
          is_temporary: true,
        };

        const definition =
          await getSDK().workflows.createWorkflowDefinitionFromTemplateApiV1WorkflowsDefinitionsFromTemplate(
            createRequest
          );

        // Step 2: Execute the newly created workflow definition
        const executionRequest: WorkflowExecutionRequest = {
          definition_id: definition.id,
          input_data: input,
        };

        const execution =
          await getSDK().workflows.executeWorkflowApiV1WorkflowsDefinitionsWorkflowIdExecute(
            definition.id,
            executionRequest
          );

        setExecutions((prev) => [execution, ...prev]);
        return execution;
      } catch (error) {
        handleError(error, {
          source: 'useWorkflowData.executeTemplate',
          operation: 'execute workflow template',
        });
        throw error;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteTemplate = useCallback(async (templateId: string) => {
    try {
      // TODO: Implement delete functionality when API is available
      // await getSDK().workflows.deleteWorkflowTemplateApiV1WorkflowsTemplatesTemplateId(
      //   templateId
      // );
      // TODO: Delete workflow template not implemented in API
      setTemplates((prev) => prev.filter((t) => t.id !== templateId));
    } catch (error) {
      handleError(error, {
        source: 'useWorkflowData.deleteTemplate',
        operation: 'delete workflow template',
      });
    }
  }, []);

  // Load data on mount
  useEffect(() => {
    loadTemplates();
    loadAvailableTools();
    loadExecutions(); // Will show warning and set empty array without workflowId
  }, [loadTemplates, loadAvailableTools, loadExecutions]);

  return {
    // Data
    loading,
    templates,
    availableTools,
    executions,
    selectedTemplate,

    // Actions
    setSelectedTemplate,
    loadTemplates,
    loadAvailableTools,
    loadExecutions,
    createTemplate,
    executeWorkflow,
    executeTemplate,
    deleteTemplate,
  };
};
