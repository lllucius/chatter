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
      // Return fallback defaults if API fails
      return this.getFallbackDefaults();
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
      // Return fallback defaults for the specific node type
      return {
        node_type: nodeType,
        config: this.getFallbackNodeConfig(nodeType),
      };
    }
  }

  /**
   * Get fallback defaults when API is unavailable
   */
  private getFallbackDefaults(): WorkflowDefaults {
    return {
      model_config: {
        provider: 'openai',
        model: 'gpt-4',
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
      },
      default_prompt: '',
      node_types: {
        model: {
          systemMessage: '',
          temperature: 0.7,
          maxTokens: 1000,
          model: 'gpt-4',
          provider: 'openai',
        },
        retrieval: {
          collection: '',
          topK: 5,
          threshold: 0.7,
        },
        memory: {
          enabled: true,
          window: 20,
          memoryType: 'conversation',
        },
        loop: {
          maxIterations: 10,
          condition: '',
          breakCondition: '',
        },
        conditional: {
          condition: '',
          branches: {},
        },
        variable: {
          operation: 'set',
          variableName: '',
          value: '',
          scope: 'workflow',
        },
        errorHandler: {
          retryCount: 3,
          fallbackAction: 'continue',
          logErrors: true,
        },
        delay: {
          duration: 1,
          type: 'fixed',
          unit: 'seconds',
        },
        tool: {
          tools: [],
          parallel: false,
        },
        start: {
          isEntryPoint: true,
        },
      },
    };
  }

  /**
   * Get fallback config for a specific node type
   */
  private getFallbackNodeConfig(nodeType: string): Record<string, any> {
    const fallbackDefaults = this.getFallbackDefaults();
    return (
      fallbackDefaults.node_types[
        nodeType as keyof typeof fallbackDefaults.node_types
      ] || {}
    );
  }
}

// Export singleton instance
export const workflowDefaultsService = new WorkflowDefaultsService();
