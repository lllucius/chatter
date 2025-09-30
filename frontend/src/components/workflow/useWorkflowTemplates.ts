/**
 * Hook for creating workflow templates with dynamic defaults
 */
import { useState, useEffect, useMemo } from 'react';
import {
  workflowDefaultsService,
  WorkflowDefaults,
} from '../../services/workflow-defaults-service';
import { WorkflowDefinition } from './WorkflowEditor';

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
 * Custom hook that provides workflow templates using dynamic defaults
 */
export const useWorkflowTemplates = () => {
  const [workflowDefaults, setWorkflowDefaults] =
    useState<WorkflowDefaults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load workflow defaults
  useEffect(() => {
    const loadDefaults = async () => {
      setLoading(true);
      setError(null);
      try {
        const defaults = await workflowDefaultsService.getWorkflowDefaults();
        setWorkflowDefaults(defaults);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to load defaults'
        );
        console.error('Failed to load workflow defaults:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDefaults();
  }, []);

  // Generate templates with dynamic defaults
  const templates = useMemo((): WorkflowTemplate[] => {
    const modelConfig = workflowDefaults?.node_types.model || {
      systemMessage: '',
      temperature: 0.7,
      maxTokens: 1000,
      model: 'gpt-4',
    };

    const memoryConfig = workflowDefaults?.node_types.memory || {
      enabled: true,
      window: 20,
    };

    const retrievalConfig = workflowDefaults?.node_types.retrieval || {
      collection: 'docs',
      topK: 5,
    };

    return [
      {
        id: 'basic-chat',
        name: 'Basic Chat',
        description: 'Simple conversational workflow with a single model call',
        category: 'basic',
        tags: ['chat', 'simple'],
        createdAt: new Date().toISOString(),
        workflow: {
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
                label: 'Chat Model',
                nodeType: 'model',
                config: modelConfig,
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
            name: 'Basic Chat',
            description: 'Simple chat workflow',
            version: '1.0.0',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
        },
      },
      {
        id: 'rag-pipeline',
        name: 'RAG Pipeline',
        description:
          'Retrieval-Augmented Generation with memory and error handling',
        category: 'advanced',
        tags: ['rag', 'retrieval', 'memory', 'error-handling'],
        createdAt: new Date().toISOString(),
        workflow: {
          nodes: [
            {
              id: 'start-1',
              type: 'start',
              position: { x: 100, y: 300 },
              data: {
                label: 'Start',
                nodeType: 'start',
                config: { isEntryPoint: true },
              },
            },
            {
              id: 'memory-1',
              type: 'memory',
              position: { x: 280, y: 300 },
              data: {
                label: 'Memory',
                nodeType: 'memory',
                config: memoryConfig,
              },
            },
            {
              id: 'retrieval-1',
              type: 'retrieval',
              position: { x: 460, y: 300 },
              data: {
                label: 'Retrieval',
                nodeType: 'retrieval',
                config: retrievalConfig,
              },
            },
            {
              id: 'model-1',
              type: 'model',
              position: { x: 640, y: 300 },
              data: {
                label: 'RAG Model',
                nodeType: 'model',
                config: {
                  ...modelConfig,
                  temperature: Math.max(
                    0.1,
                    (modelConfig.temperature || 0.7) - 0.4
                  ), // Lower temperature for factual responses
                  maxTokens: Math.max(
                    1000,
                    (modelConfig.maxTokens || 1000) + 500
                  ), // More tokens for detailed responses
                },
              },
            },
            {
              id: 'error-1',
              type: 'errorHandler',
              position: { x: 460, y: 450 },
              data: {
                label: 'Error Handler',
                nodeType: 'errorHandler',
                config: workflowDefaults?.node_types.errorHandler || {
                  retryCount: 2,
                  fallbackAction: 'continue',
                },
              },
            },
          ],
          edges: [
            {
              id: 'e1',
              source: 'start-1',
              target: 'memory-1',
              type: 'custom',
              animated: true,
            },
            {
              id: 'e2',
              source: 'memory-1',
              target: 'retrieval-1',
              type: 'custom',
              animated: true,
            },
            {
              id: 'e3',
              source: 'retrieval-1',
              target: 'model-1',
              type: 'custom',
              animated: true,
            },
            {
              id: 'e4',
              source: 'model-1',
              target: 'error-1',
              type: 'custom',
              animated: true,
            },
          ],
          metadata: {
            name: 'RAG Pipeline',
            description: 'Advanced retrieval workflow',
            version: '1.0.0',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
        },
      },
      {
        id: 'data-processing',
        name: 'Data Processing Pipeline',
        description: 'Batch processing workflow with loops and variables',
        category: 'advanced',
        tags: ['data', 'processing', 'batch', 'loop'],
        createdAt: new Date().toISOString(),
        workflow: {
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
              id: 'variable-1',
              type: 'variable',
              position: { x: 280, y: 200 },
              data: {
                label: 'Initialize Counter',
                nodeType: 'variable',
                config: workflowDefaults?.node_types.variable || {
                  operation: 'set',
                  variableName: 'counter',
                  value: '0',
                },
              },
            },
            {
              id: 'loop-1',
              type: 'loop',
              position: { x: 460, y: 200 },
              data: {
                label: 'Process Loop',
                nodeType: 'loop',
                config: workflowDefaults?.node_types.loop || {
                  maxIterations: 10,
                  condition: 'counter < 10',
                },
              },
            },
            {
              id: 'model-1',
              type: 'model',
              position: { x: 640, y: 120 },
              data: {
                label: 'Process Item',
                nodeType: 'model',
                config: {
                  ...modelConfig,
                  temperature: Math.min(
                    1.0,
                    (modelConfig.temperature || 0.7) - 0.2
                  ), // Slightly lower for processing
                  maxTokens: Math.min(
                    4000,
                    (modelConfig.maxTokens || 1000) - 200
                  ), // Fewer tokens for processing
                },
              },
            },
            {
              id: 'variable-2',
              type: 'variable',
              position: { x: 640, y: 280 },
              data: {
                label: 'Increment Counter',
                nodeType: 'variable',
                config: { operation: 'increment', variableName: 'counter' },
              },
            },
            {
              id: 'conditional-1',
              type: 'conditional',
              position: { x: 820, y: 200 },
              data: {
                label: 'Check Complete',
                nodeType: 'conditional',
                config: workflowDefaults?.node_types.conditional || {
                  condition: 'counter >= 10',
                  branches: {},
                },
              },
            },
          ],
          edges: [
            {
              id: 'e1',
              source: 'start-1',
              target: 'variable-1',
              type: 'custom',
              animated: true,
            },
            {
              id: 'e2',
              source: 'variable-1',
              target: 'loop-1',
              type: 'custom',
              animated: true,
            },
            {
              id: 'e3',
              source: 'loop-1',
              target: 'model-1',
              type: 'custom',
              animated: true,
              sourceHandle: 'continue',
            },
            {
              id: 'e4',
              source: 'model-1',
              target: 'variable-2',
              type: 'custom',
              animated: true,
            },
            {
              id: 'e5',
              source: 'variable-2',
              target: 'conditional-1',
              type: 'custom',
              animated: true,
            },
            {
              id: 'e6',
              source: 'conditional-1',
              target: 'loop-1',
              type: 'custom',
              animated: true,
              sourceHandle: 'false',
            },
          ],
          metadata: {
            name: 'Data Processing Pipeline',
            description: 'Batch processing with loops',
            version: '1.0.0',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
        },
      },
    ];
  }, [workflowDefaults]);

  return {
    templates,
    loading,
    error,
    workflowDefaults,
  };
};
