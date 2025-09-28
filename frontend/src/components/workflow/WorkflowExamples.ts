import { WorkflowDefinition } from './WorkflowEditor';
import type { Node, Edge } from '@xyflow/react';

// Example workflows that demonstrate different patterns
export const exampleWorkflows: Record<string, WorkflowDefinition> = {
  simple: {
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
        position: { x: 350, y: 200 },
        data: {
          label: 'Chat Model',
          nodeType: 'model',
          config: { temperature: 0.7, maxTokens: 1000 },
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
      name: 'Simple Chat',
      description: 'Basic chat workflow with just a model call',
      version: '1.0.0',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  },

  ragWithTools: {
    nodes: [
      {
        id: 'start-1',
        type: 'start',
        position: { x: 50, y: 200 },
        data: {
          label: 'Start',
          nodeType: 'start',
          config: { isEntryPoint: true },
        },
      },
      {
        id: 'memory-1',
        type: 'memory',
        position: { x: 250, y: 200 },
        data: {
          label: 'Memory Manager',
          nodeType: 'memory',
          config: { enabled: true, window: 20 },
        },
      },
      {
        id: 'retrieval-1',
        type: 'retrieval',
        position: { x: 450, y: 200 },
        data: {
          label: 'Document Retrieval',
          nodeType: 'retrieval',
          config: { collection: 'knowledge_base', topK: 5 },
        },
      },
      {
        id: 'model-1',
        type: 'model',
        position: { x: 650, y: 200 },
        data: {
          label: 'Chat Model',
          nodeType: 'model',
          config: {
            temperature: 0.7,
            maxTokens: 1000,
            systemMessage: 'Use the retrieved context to answer questions.',
          },
        },
      },
      {
        id: 'conditional-1',
        type: 'conditional',
        position: { x: 850, y: 200 },
        data: {
          label: 'Tool Decision',
          nodeType: 'conditional',
          config: {
            condition: 'should_use_tools',
            branches: { true: 'tool-1', false: 'end' },
          },
        },
      },
      {
        id: 'tool-1',
        type: 'tool',
        position: { x: 1050, y: 100 },
        data: {
          label: 'Tool Execution',
          nodeType: 'tool',
          config: { tools: ['web_search', 'calculator'], parallel: false },
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
        target: 'conditional-1',
        type: 'custom',
        animated: true,
      },
      {
        id: 'e5',
        source: 'conditional-1',
        sourceHandle: 'true',
        target: 'tool-1',
        type: 'custom',
        animated: true,
        data: { label: 'needs tools', condition: 'has_tool_calls' },
      },
      {
        id: 'e6',
        source: 'tool-1',
        target: 'model-1',
        type: 'custom',
        animated: true,
        data: { label: 'tool results' },
      },
    ],
    metadata: {
      name: 'RAG with Tools',
      description:
        'Advanced workflow with memory, retrieval, conditional logic, and tool execution',
      version: '1.0.0',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  },

  parallelProcessing: {
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
        id: 'model-1',
        type: 'model',
        position: { x: 350, y: 150 },
        data: {
          label: 'Analysis Model',
          nodeType: 'model',
          config: {
            temperature: 0.3,
            maxTokens: 500,
            systemMessage: 'Analyze the input text.',
          },
        },
      },
      {
        id: 'model-2',
        type: 'model',
        position: { x: 350, y: 350 },
        data: {
          label: 'Summary Model',
          nodeType: 'model',
          config: {
            temperature: 0.5,
            maxTokens: 300,
            systemMessage: 'Summarize the input text.',
          },
        },
      },
      {
        id: 'model-3',
        type: 'model',
        position: { x: 350, y: 550 },
        data: {
          label: 'Sentiment Model',
          nodeType: 'model',
          config: {
            temperature: 0.1,
            maxTokens: 200,
            systemMessage: 'Analyze sentiment of the text.',
          },
        },
      },
      {
        id: 'model-final',
        type: 'model',
        position: { x: 650, y: 350 },
        data: {
          label: 'Combiner Model',
          nodeType: 'model',
          config: {
            temperature: 0.7,
            maxTokens: 800,
            systemMessage: 'Combine all analyses into a comprehensive report.',
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
      {
        id: 'e2',
        source: 'start-1',
        target: 'model-2',
        type: 'custom',
        animated: true,
      },
      {
        id: 'e3',
        source: 'start-1',
        target: 'model-3',
        type: 'custom',
        animated: true,
      },
      {
        id: 'e4',
        source: 'model-1',
        target: 'model-final',
        type: 'custom',
        animated: true,
      },
      {
        id: 'e5',
        source: 'model-2',
        target: 'model-final',
        type: 'custom',
        animated: true,
      },
      {
        id: 'e6',
        source: 'model-3',
        target: 'model-final',
        type: 'custom',
        animated: true,
      },
    ],
    metadata: {
      name: 'Parallel Processing',
      description:
        'Process input through multiple models in parallel then combine results',
      version: '1.0.0',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  },
};

// Workflow validation utilities
export class WorkflowValidator {
  static validate(workflow: WorkflowDefinition): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    // Check basic structure
    if (!workflow.nodes || !Array.isArray(workflow.nodes)) {
      errors.push('Workflow must have a nodes array');
      return { isValid: false, errors };
    }

    if (!workflow.edges || !Array.isArray(workflow.edges)) {
      errors.push('Workflow must have an edges array');
      return { isValid: false, errors };
    }

    // Allow empty workflows for building purposes
    if (workflow.nodes.length === 0) {
      return { isValid: true, errors };
    }

    // Check for entry point
    const hasStartNode = workflow.nodes.some(
      (node: Node) => node.type === 'start'
    );
    if (!hasStartNode) {
      errors.push('Workflow must have at least one start node');
    }

    // Check for isolated nodes (only if there are edges)
    if (workflow.edges.length > 0) {
      const connectedNodes = new Set<string>();

      workflow.edges.forEach((edge: Edge) => {
        connectedNodes.add(edge.source);
        connectedNodes.add(edge.target);
      });

      const isolatedNodes = workflow.nodes.filter(
        (node: Node) => node.type !== 'start' && !connectedNodes.has(node.id)
      );

      if (isolatedNodes.length > 0) {
        errors.push(
          `Isolated nodes found: ${isolatedNodes.map((n: Node) => n.data?.label || n.id).join(', ')}`
        );
      }
    }

    // Check for cycles (basic detection) - only if there are edges
    if (workflow.edges.length > 0 && this.hasCycles(workflow)) {
      errors.push('Workflow contains cycles - ensure proper loop structure');
    }

    // Validate conditional nodes have proper configuration
    const conditionalNodes = workflow.nodes.filter(
      (node: Node) => node.type === 'conditional'
    );
    conditionalNodes.forEach((node: Node) => {
      const config = node.data?.config as Record<string, unknown> | undefined;
      if (!config?.condition) {
        errors.push(`Conditional node "${node.data?.label || node.id}" needs a condition`);
      }
    });

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  private static hasCycles(workflow: WorkflowDefinition): boolean {
    // Simple cycle detection using DFS
    const graph = new Map<string, string[]>();

    // Build adjacency list - only include valid nodes
    const validNodeIds = new Set(workflow.nodes.map((node: Node) => node.id));
    
    workflow.nodes.forEach((node: Node) => {
      graph.set(node.id, []);
    });

    workflow.edges.forEach((edge: Edge) => {
      // Only add edges between valid nodes
      if (validNodeIds.has(edge.source) && validNodeIds.has(edge.target)) {
        const sources = graph.get(edge.source) || [];
        sources.push(edge.target);
        graph.set(edge.source, sources);
      }
    });

    const visited = new Set<string>();
    const visiting = new Set<string>();

    const dfs = (nodeId: string): boolean => {
      if (visiting.has(nodeId)) return true; // Cycle detected
      if (visited.has(nodeId)) return false;

      visiting.add(nodeId);

      const neighbors = graph.get(nodeId) || [];
      for (const neighbor of neighbors) {
        if (dfs(neighbor)) return true;
      }

      visiting.delete(nodeId);
      visited.add(nodeId);
      return false;
    };

    for (const nodeId of graph.keys()) {
      if (!visited.has(nodeId)) {
        if (dfs(nodeId)) return true;
      }
    }

    return false;
  }
}
