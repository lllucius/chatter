import { WorkflowDefinition, WorkflowNodeType } from './types';

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
    // Validate workflow before translation
    const validation = this.validateForLangGraph(workflow);
    if (!validation.valid) {
      throw new Error(`Workflow validation failed: ${validation.errors.join(', ')}`);
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
    const retrieverNode = workflow.nodes.find((n: any) => n.type === 'retrieval');
    if (retrieverNode?.data.config) {
      config.retriever = {
        collection: String(retrieverNode.data.config.collection || 'default'),
        top_k: Number(retrieverNode.data.config.topK) || 5,
      };
    }

    // Add memory configuration if present
    const memoryNode = workflow.nodes.find((n: any) => n.type === 'memory');
    if (memoryNode?.data.config) {
      config.memory_window = Number(memoryNode.data.config.window) || 20;
    }

    // Extract system message from model nodes
    const modelNodes = workflow.nodes.filter((n: any) => n.type === 'model');
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
      try {
        const langGraphType = this.mapNodeTypeToLangGraph(
          node.type as WorkflowNodeType
        );

        // Validate node configuration
        this.validateNodeConfig(node.type as WorkflowNodeType, node.data.config);

        return {
          id: node.id,
          type: langGraphType,
          config: node.data.config || {},
        };
      } catch (error) {
        throw new Error(`Failed to translate node ${node.id}: ${(error as Error).message}`);
      }
    });
  }

  /**
   * Validate node configuration based on node type
   */
  private static validateNodeConfig(
    nodeType: WorkflowNodeType,
    config: Record<string, unknown> | undefined
  ): void {
    switch (nodeType) {
      case 'conditional':
        if (!config || !config.condition) {
          throw new Error('Conditional nodes must have a condition defined');
        }
        break;
      case 'tool':
        if (!config || !config.tools || !Array.isArray(config.tools)) {
          throw new Error('Tool nodes must have tools configured');
        }
        break;
      case 'retrieval':
        if (!config || (!config.collection && !config.topK)) {
          throw new Error('Retrieval nodes must have collection or topK configured');
        }
        break;
      case 'loop':
        if (!config || (!config.maxIterations && !config.condition)) {
          throw new Error('Loop nodes must have maxIterations or condition defined');
        }
        if (config.maxIterations && (typeof config.maxIterations !== 'number' || config.maxIterations <= 0)) {
          throw new Error('Loop maxIterations must be a positive number');
        }
        break;
      case 'variable':
        if (!config || !config.variableName || !config.operation) {
          throw new Error('Variable nodes must have variableName and operation defined');
        }
        const validOps = ['set', 'get', 'append', 'increment', 'decrement'];
        if (!validOps.includes(String(config.operation))) {
          throw new Error(`Variable operation must be one of: ${validOps.join(', ')}`);
        }
        break;
      case 'errorHandler':
        if (config && config.retryCount && (typeof config.retryCount !== 'number' || config.retryCount < 0)) {
          throw new Error('Error handler retryCount must be a non-negative number');
        }
        break;
      case 'delay':
        if (!config || !config.duration || typeof config.duration !== 'number') {
          throw new Error('Delay nodes must have a numeric duration defined');
        }
        if (config.duration <= 0) {
          throw new Error('Delay duration must be positive');
        }
        const validDelayTypes = ['fixed', 'random', 'exponential', 'dynamic'];
        if (config.delayType && !validDelayTypes.includes(String(config.delayType))) {
          throw new Error(`Delay type must be one of: ${validDelayTypes.join(', ')}`);
        }
        break;
      case 'memory':
        if (config && config.memoryWindow && (typeof config.memoryWindow !== 'number' || config.memoryWindow <= 0)) {
          throw new Error('Memory window must be a positive number');
        }
        break;
      // Other node types have optional configuration
    }
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
  private static determineWorkflowCapabilities(
    workflow: WorkflowDefinition
  ): { hasRetrieval: boolean; hasTools: boolean } {
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
   * Validate that workflow can be converted to LangGraph
   */
  static validateForLangGraph(workflow: WorkflowDefinition): {
    valid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    // Must have at least one start node
    const startNodes = workflow.nodes.filter((n) => n.type === 'start');
    if (startNodes.length === 0) {
      errors.push('Workflow must have a start node');
    } else if (startNodes.length > 1) {
      errors.push('Workflow can only have one start node for LangGraph');
    }

    // Must have at least one model node
    const modelNodes = workflow.nodes.filter((n) => n.type === 'model');
    if (modelNodes.length === 0) {
      errors.push('Workflow must have at least one model node');
    }

    // Conditional nodes must have conditions
    const conditionalNodes = workflow.nodes.filter(
      (n) => n.type === 'conditional'
    );
    conditionalNodes.forEach((node) => {
      if (!node.data.config?.condition) {
        errors.push(
          `Conditional node "${node.data.label}" must have a condition defined`
        );
      }
    });

    // Loop nodes must have proper configuration
    const loopNodes = workflow.nodes.filter((n) => n.type === 'loop');
    loopNodes.forEach((node) => {
      const config = node.data.config;
      if (!config || (!config.maxIterations && !config.condition)) {
        errors.push(
          `Loop node "${node.data.label}" must have maxIterations or condition defined`
        );
      }
    });

    // Variable nodes must have proper configuration
    const variableNodes = workflow.nodes.filter((n) => n.type === 'variable');
    variableNodes.forEach((node) => {
      const config = node.data.config;
      if (!config || !config.variableName || !config.operation) {
        errors.push(
          `Variable node "${node.data.label}" must have variableName and operation defined`
        );
      }
    });

    // Error handler nodes validation
    const errorNodes = workflow.nodes.filter((n) => n.type === 'errorHandler');
    errorNodes.forEach((node) => {
      const config = node.data.config;
      if (config && config.retryCount && (typeof config.retryCount !== 'number' || config.retryCount < 0)) {
        errors.push(
          `Error handler node "${node.data.label}" retryCount must be a non-negative number`
        );
      }
    });

    // Delay nodes validation  
    const delayNodes = workflow.nodes.filter((n) => n.type === 'delay');
    delayNodes.forEach((node) => {
      const config = node.data.config;
      if (!config || !config.duration || typeof config.duration !== 'number' || config.duration <= 0) {
        errors.push(
          `Delay node "${node.data.label}" must have a positive numeric duration`
        );
      }
    });

    // Check for proper connectivity
    const executionOrder = this.generateExecutionOrder(workflow);
    if (executionOrder.length !== workflow.nodes.length) {
      errors.push('Workflow has cycles or disconnected components');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
