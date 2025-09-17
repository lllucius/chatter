import { useState, useEffect, useCallback } from 'react';
import { getSDK } from '../services/auth-service';
import { handleError } from '../utils/error-handler';

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  workflow: any;
  created_at: string;
  updated_at: string;
}

interface AvailableToolsResponse {
  tools: any[];
}

interface WorkflowExecution {
  id: string;
  workflow_name: string;
  status: string;
  started_at: string;
  completed_at?: string;
  input: any;
  output?: any;
  error?: string;
}

export const useWorkflowData = () => {
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [availableTools, setAvailableTools] =
    useState<AvailableToolsResponse | null>(null);
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
      const response =
        await getSDK().workflows.getAvailableToolsApiV1WorkflowsTools();
      setAvailableTools(response);
    } catch (error) {
      handleError(error, {
        source: 'useWorkflowData.loadAvailableTools',
        operation: 'load available tools',
      });
    }
  }, []);

  const loadExecutions = useCallback(async () => {
    try {
      const response =
        await getSDK().workflows.listWorkflowExecutionsApiV1WorkflowsExecutions();
      setExecutions(response.executions || []);
    } catch (error) {
      handleError(error, {
        source: 'useWorkflowData.loadExecutions',
        operation: 'load workflow executions',
      });
    }
  }, []);

  const createTemplate = useCallback(async (templateData: any) => {
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
  }, []);

  const executeWorkflow = useCallback(
    async (templateId: string, input: any) => {
      try {
        setLoading(true);
        const execution =
          await getSDK().workflows.executeWorkflowApiV1WorkflowsExecute({
            template_id: templateId,
            input: input,
          });
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

  const deleteTemplate = useCallback(async (templateId: string) => {
    try {
      await getSDK().workflows.deleteWorkflowTemplateApiV1WorkflowsTemplatesTemplateId(
        templateId
      );
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
    loadExecutions();
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
    deleteTemplate,
  };
};
