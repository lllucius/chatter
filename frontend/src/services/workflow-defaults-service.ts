/**
 * Service for fetching workflow defaults from profiles, models, and prompts
 */
import { authService } from './auth-service';

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
      branches: Record<string, any>;
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
      tools: any[];
      parallel: boolean;
    };
    start: {
      isEntryPoint: boolean;
    };
  };
}

export interface NodeDefaultConfig {
  node_type: string;
  config: Record<string, any>;
}

class WorkflowDefaultsService {
  /**
   * Get all workflow defaults from the backend
   */
  async getWorkflowDefaults(): Promise<WorkflowDefaults> {
    try {
      const token = authService.getToken();

      const response = await fetch('/api/v1/workflows/defaults', {
        method: 'GET',
        headers: {
          ...(token && { Authorization: `Bearer ${token}` }),
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(
          `Failed to fetch workflow defaults: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching workflow defaults:', error);
      // No fallback - throw error to caller
      throw new Error(
        'Unable to fetch workflow defaults from server. Please check your connection and try again.'
      );
    }
  }

  /**
   * Get defaults for a specific node type
   */
  async getNodeDefaults(nodeType: string): Promise<NodeDefaultConfig> {
    try {
      const token = authService.getToken();

      const response = await fetch(
        `/api/v1/workflows/defaults?node_type=${nodeType}`,
        {
          method: 'GET',
          headers: {
            ...(token && { Authorization: `Bearer ${token}` }),
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to fetch node defaults: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error(
        `Error fetching defaults for node type ${nodeType}:`,
        error
      );
      // No fallback - throw error to caller
      throw new Error(
        `Unable to fetch defaults for ${nodeType} node. Please check your connection and try again.`
      );
    }
  }
}

// Export singleton instance
export const workflowDefaultsService = new WorkflowDefaultsService();
