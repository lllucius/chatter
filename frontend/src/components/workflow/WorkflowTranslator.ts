import { WorkflowDefinition, WorkflowNodeType } from './WorkflowEditor';

/**
 * Utility to convert visual workflow definitions to LangGraph-compatible format
 * This bridges the visual editor with the Python LangGraph implementation
 */

export interface LangGraphWorkflowConfig {
  enable_retrieval: boolean;
  enable_tools: boolean;
  system_message?: string;
  enable_memory: boolean;
  memory_window?: number;
  retriever?: {
    collection: string;
    top_k: number;
  };
  tools?: string[];
  nodes: LangGraphNode[];
  edges: LangGraphEdge[];
  entry_point?: string;
}

export interface LangGraphNode {
  id: string;
  type:
    | 'start'
    | 'manage_memory'
    | 'retrieve_context'
    | 'call_model'
    | 'execute_tools'
    | 'conditional'
    | 'loop'
    | 'variable'
    | 'error_handler'
    | 'delay';
  config: Record<string, unknown>;
}

export interface LangGraphEdge {
  from: string;
  to: string;
  condition?: string;
  type: 'regular' | 'conditional';
}

export class WorkflowTranslator {
  /**
   * Convert visual workflow definition to LangGraph configuration
   */
  static toLangGraphConfig(
    workflow: WorkflowDefinition
  ): LangGraphWorkflowConfig {
    // Backend will handle comprehensive validation
    // Only do minimal frontend checks for immediate UX feedback
    if (!workflow.nodes || workflow.nodes.length === 0) {
      throw new Error('Workflow must have at least one node');
    }

    const nodes = this.translateNodes(workflow);
    const edges = this.translateEdges(workflow);

    // Analyze workflow to determine capabilities
    const capabilities = this.determineWorkflowCapabilities(workflow);

    // Extract configuration from nodes
    const config: LangGraphWorkflowConfig = {
      enable_retrieval: capabilities.hasRetrieval,
      enable_tools: capabilities.hasTools,
      enable_memory: this.hasMemoryNode(workflow),
      nodes,
      edges,
      entry_point: this.findEntryPoint(workflow),
    };

    // Add retriever configuration if present
    const retrieverNode = workflow.nodes.find((n) => n.type === 'retrieval');
    if (retrieverNode?.data.config) {
      config.retriever = {
        collection: String(retrieverNode.data.config.collection || 'default'),
        top_k: Number(retrieverNode.data.config.topK) || 5,
      };
    }

    // Add memory configuration if present
    const memoryNode = workflow.nodes.find((n) => n.type === 'memory');
    if (memoryNode?.data.config) {
      config.memory_window = Number(memoryNode.data.config.window) || 20;
    }

    // Extract system message from model nodes
    const modelNodes = workflow.nodes.filter((n) => n.type === 'model');
    if (modelNodes.length > 0 && modelNodes[0].data.config?.systemMessage) {
      config.system_message = String(modelNodes[0].data.config.systemMessage);
    }

    // Extract tools from tool nodes
    const toolNodes = workflow.nodes.filter((n) => n.type === 'tool');
    if (toolNodes.length > 0) {
      const allTools = toolNodes.flatMap(
        (node) => (node.data.config?.tools as string[]) || []
      );
      config.tools = [...new Set(allTools)];
    }

    return config;
  }

  /**
   * Convert workflow nodes to LangGraph node format
   */
  private static translateNodes(workflow: WorkflowDefinition): LangGraphNode[] {
    return workflow.nodes.map((node) => {
      const langGraphType = this.mapNodeTypeToLangGraph(
        node.type as WorkflowNodeType
      );

      // No frontend validation - backend will validate node configurations
      return {
        id: node.id,
        type: langGraphType,
        config: node.data.config || {},
      };
    });
  }

  /**
   * Convert workflow edges to LangGraph edge format
   */
  private static translateEdges(workflow: WorkflowDefinition): LangGraphEdge[] {
    return workflow.edges.map((edge) => ({
      from: edge.source,
      to: edge.target,
      condition: edge.data?.condition,
      type: edge.data?.condition ? 'conditional' : 'regular',
    }));
  }

  /**
   * Map visual node types to LangGraph node types
   */
  private static mapNodeTypeToLangGraph(
    nodeType: string
  ): LangGraphNode['type'] {
    switch (nodeType) {
      case 'start':
        return 'start';
      case 'memory':
        return 'manage_memory';
      case 'retrieval':
        return 'retrieve_context';
      case 'model':
      case 'llm':
        return 'call_model';
      case 'tool':
      case 'tools':
        return 'execute_tools';
      case 'conditional':
        return 'conditional';
      case 'loop':
        return 'loop';
      case 'variable':
        return 'variable';
      case 'error_handler':
      case 'errorHandler':
        return 'error_handler';
      case 'delay':
        return 'delay';
      default:
        throw new Error(`Unsupported node type for LangGraph: ${nodeType}`);
    }
  }

  /**
   * Determine workflow capabilities based on nodes present
   */
  private static determineWorkflowCapabilities(workflow: WorkflowDefinition): {
    hasRetrieval: boolean;
    hasTools: boolean;
  } {
    const hasRetrieval = workflow.nodes.some((n) => n.type === 'retrieval');
    const hasTools = workflow.nodes.some((n) => n.type === 'tool');

    return {
      hasRetrieval,
      hasTools,
    };
  }

  /**
   * Check if workflow has memory management
   */
  private static hasMemoryNode(workflow: WorkflowDefinition): boolean {
    return workflow.nodes.some((n) => n.type === 'memory');
  }

  /**
   * Find the entry point node
   */
  private static findEntryPoint(
    workflow: WorkflowDefinition
  ): string | undefined {
    const startNode = workflow.nodes.find((n) => n.type === 'start');
    return startNode?.id;
  }

  /**
   * Generate execution order based on workflow structure
   */
  static generateExecutionOrder(workflow: WorkflowDefinition): string[] {
    const graph = new Map<string, string[]>();
    const inDegree = new Map<string, number>();

    // Initialize graph
    workflow.nodes.forEach((node) => {
      graph.set(node.id, []);
      inDegree.set(node.id, 0);
    });

    // Build adjacency list and calculate in-degrees
    workflow.edges.forEach((edge) => {
      const neighbors = graph.get(edge.source) || [];
      neighbors.push(edge.target);
      graph.set(edge.source, neighbors);

      inDegree.set(edge.target, (inDegree.get(edge.target) || 0) + 1);
    });

    // Topological sort
    const queue: string[] = [];
    const result: string[] = [];

    // Start with nodes that have no incoming edges
    inDegree.forEach((degree, nodeId) => {
      if (degree === 0) {
        queue.push(nodeId);
      }
    });

    while (queue.length > 0) {
      const current = queue.shift()!;
      result.push(current);

      const neighbors = graph.get(current) || [];
      neighbors.forEach((neighbor) => {
        const newDegree = (inDegree.get(neighbor) || 0) - 1;
        inDegree.set(neighbor, newDegree);

        if (newDegree === 0) {
          queue.push(neighbor);
        }
      });
    }

    return result;
  }

  /**
   * Basic validation for LangGraph conversion.
   * Backend performs comprehensive validation - this is for immediate UX feedback only.
   */
  static validateForLangGraph(workflow: WorkflowDefinition): {
    valid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    // Basic structure check
    if (!workflow.nodes || workflow.nodes.length === 0) {
      errors.push('Workflow must have at least one node');
    }

    // Check for start node (basic UX requirement)
    const startNodes = workflow.nodes.filter((n) => n.type === 'start');
    if (startNodes.length === 0) {
      errors.push('Workflow must have a start node');
    }

    // All other validation (node configs, cycles, connectivity, etc.) 
    // is handled by the backend validation API

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
