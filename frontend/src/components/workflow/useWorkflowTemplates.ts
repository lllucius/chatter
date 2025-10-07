/**
 * Hook for loading workflow templates from the database
 */
import { useState, useEffect, useMemo } from 'react';
import {
  workflowDefaultsService,
  WorkflowDefaults,
} from '../../services/workflow-defaults-service';
import { WorkflowDefinition } from './WorkflowEditor';
import { getSDK } from '../../services/auth-service';
import { WorkflowTemplateResponse } from 'chatter-sdk';

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: 'basic' | 'advanced' | 'custom';
  workflow: WorkflowDefinition;
  tags: string[];
  createdAt: string;
}

/**
 * Custom hook that provides workflow templates from the database
 */
export const useWorkflowTemplates = () => {
  const [workflowDefaults, setWorkflowDefaults] =
    useState<WorkflowDefaults | null>(null);
  const [dbTemplates, setDbTemplates] = useState<WorkflowTemplateResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load workflow defaults and templates
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Load both defaults and templates in parallel
        const [defaults, templatesResponse] = await Promise.all([
          workflowDefaultsService.getWorkflowDefaults(),
          getSDK().workflows.listWorkflowTemplatesApiV1WorkflowsTemplates(),
        ]);
        setWorkflowDefaults(defaults);
        setDbTemplates(templatesResponse.templates || []);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to load templates'
        );
        console.error('Failed to load workflow templates:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Convert database templates to workflow templates
  const templates = useMemo((): WorkflowTemplate[] => {
    const modelConfig = workflowDefaults?.node_types.model || {
      systemMessage: '',
      temperature: 0.7,
      maxTokens: 1000,
      model: 'gpt-4',
    };

    // Convert database templates to workflow templates with basic structure
    return dbTemplates.map((dbTemplate) => {
      // Determine category based on template category
      let category: 'basic' | 'advanced' | 'custom' = 'custom';
      if (dbTemplate.category) {
        const cat = dbTemplate.category.toLowerCase();
        if (cat === 'general' || cat === 'basic') {
          category = 'basic';
        } else if (cat === 'research' || cat === 'programming' || cat === 'customer_support' || cat === 'data_analysis') {
          category = 'advanced';
        }
      }

      // Create a basic workflow structure from template metadata
      const workflow: WorkflowDefinition = {
        nodes: [
          {
            id: 'start-1',
            type: 'start',
            position: { x: 100, y: 200 },
            data: {
              label: 'Start',
              nodeType: 'start',
              config: { isEntryPoint: true },
            },
          },
          {
            id: 'model-1',
            type: 'model',
            position: { x: 300, y: 200 },
            data: {
              label: dbTemplate.name,
              nodeType: 'model',
              config: {
                ...modelConfig,
                ...dbTemplate.default_params,
              },
            },
          },
        ],
        edges: [
          {
            id: 'e1',
            source: 'start-1',
            target: 'model-1',
            type: 'custom',
            animated: true,
          },
        ],
        metadata: {
          name: dbTemplate.name,
          description: dbTemplate.description,
          version: '1.0.0',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      };

      return {
        id: dbTemplate.id,
        name: dbTemplate.name,
        description: dbTemplate.description,
        category,
        workflow,
        tags: dbTemplate.tags || [],
        createdAt: new Date().toISOString(),
      };
    });
  }, [dbTemplates, workflowDefaults]);

  return {
    templates,
    loading,
    error,
    workflowDefaults,
  };
};
