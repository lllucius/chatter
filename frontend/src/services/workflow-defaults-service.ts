/**
 * Service for fetching workflow defaults from profiles, models, and prompts
 */
import { getSDK } from './auth-service';
import { handleError } from '../utils/error-handler';

export interface WorkflowDefaults {
  model_config: {
    provider: string;
    model: string;
    temperature: number;
    max_tokens: number;
    top_p: number;
    frequency_penalty: number;
    presence_penalty: number;
  };
  default_prompt: string;
  node_types: {
    model: {
      systemMessage: string;
      temperature: number;
      maxTokens: number;
      model: string;
      provider: string;
    };
    retrieval: {
      collection: string;
      topK: number;
      threshold: number;
    };
    memory: {
      enabled: boolean;
      window: number;
      memoryType: string;
    };
    loop: {
      maxIterations: number;
      condition: string;
      breakCondition: string;
    };
    conditional: {
      condition: string;
      branches: Record<string, unknown>;
    };
    variable: {
      operation: string;
      variableName: string;
      value: string;
      scope: string;
    };
    errorHandler: {
      retryCount: number;
      fallbackAction: string;
      logErrors: boolean;
    };
    delay: {
      duration: number;
      type: string;
      unit: string;
    };
    tool: {
      tools: unknown[];
      parallel: boolean;
    };
    start: {
      isEntryPoint: boolean;
    };
  };
}

export interface NodeDefaultConfig {
  node_type: string;
  config: Record<string, unknown>;
}

class WorkflowDefaultsService {
  /**
   * Get all workflow defaults from the backend using SDK
   */
  async getWorkflowDefaults(): Promise<WorkflowDefaults> {
    try {
      const sdk = getSDK();
      const response = await sdk.workflows.getWorkflowDefaultsApiV1WorkflowsDefaults();
      return response as WorkflowDefaults;
    } catch (error) {
      handleError(error, {
        source: 'WorkflowDefaultsService.getWorkflowDefaults',
        operation: 'fetch workflow defaults',
      });
      throw new Error(
        'Unable to fetch workflow defaults from server. Please check your connection and try again.'
      );
    }
  }

  /**
   * Get defaults for a specific node type using SDK
   */
  async getNodeDefaults(nodeType: string): Promise<NodeDefaultConfig> {
    try {
      const sdk = getSDK();
      const response = await sdk.workflows.getWorkflowDefaultsApiV1WorkflowsDefaults({
        nodeType,
      });
      return response as NodeDefaultConfig;
    } catch (error) {
      handleError(error, {
        source: 'WorkflowDefaultsService.getNodeDefaults',
        operation: `fetch defaults for ${nodeType} node`,
      });
      throw new Error(
        `Unable to fetch defaults for ${nodeType} node. Please check your connection and try again.`
      );
    }
  }
}

// Export singleton instance
export const workflowDefaultsService = new WorkflowDefaultsService();
