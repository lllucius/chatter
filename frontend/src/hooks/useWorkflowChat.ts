import { useState, useCallback, useEffect } from 'react';
import { getSDK } from '../services/auth-service';
import { handleError } from '../utils/error-handler';

// Define workflow config types based on ChatRequest fields
export interface ChatWorkflowConfig extends Record<string, unknown> {
  enable_retrieval?: boolean;
  enable_tools?: boolean;
  enable_memory?: boolean;
  enable_web_search?: boolean;
  llm_config?: {
    temperature?: number;
    max_tokens?: number;
  };
  tool_config?: Record<string, unknown>;
  retrieval_config?: Record<string, unknown>;
}

export interface ChatWorkflowRequest extends Record<string, unknown> {
  message: string;
  conversation_id?: string;
  workflow_config?: Record<string, unknown>;
}

export const useWorkflowChat = () => {
  const [customWorkflowConfig, setCustomWorkflowConfig] =
    useState<ChatWorkflowConfig>(() => {
      // Try to restore the workflow configuration from localStorage
      const saved = localStorage.getItem('chatter_customWorkflowConfig');
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch {
          // If parsing fails, fall through to sync with individual settings
        }
      }

      // If no saved config, initialize from individual settings stored in localStorage
      const enableRetrieval = localStorage.getItem('chatter_enableRetrieval');
      const enableTools = localStorage.getItem('chatter_enableTools');
      const temperature = localStorage.getItem('chatter_temperature');
      const maxTokens = localStorage.getItem('chatter_maxTokens');

      return {
        enable_retrieval: enableRetrieval ? JSON.parse(enableRetrieval) : false,
        enable_tools: enableTools ? JSON.parse(enableTools) : false,
        enable_memory: true,
        enable_web_search: false, // Default to false, can be enabled through UI
        llm_config: {
          temperature: temperature ? parseFloat(temperature) : 0.7,
          max_tokens: maxTokens ? parseInt(maxTokens) : 1000,
        },
      };
    });

  // Build workflow request
  const buildWorkflowRequest = useCallback(
    (
      message: string,
      conversationId?: string,
      additionalParams?: Partial<ChatWorkflowRequest>
    ): ChatWorkflowRequest => {
      const request: ChatWorkflowRequest = {
        message,
        conversation_id: conversationId,
        workflow_config: customWorkflowConfig, // Always use custom configuration
        ...additionalParams,
      };

      return request;
    },
    [customWorkflowConfig]
  );

  // Send chat message using workflow system
  const sendWorkflowMessage = useCallback(
    async (request: ChatWorkflowRequest, streaming: boolean = false) => {
      try {
        if (streaming) {
          // Use streaming workflow endpoint
          return await getSDK().workflows.executeChatWorkflowStreamingApiV1WorkflowsExecuteChatStreaming(
            request
          );
        } else {
          // Use non-streaming workflow endpoint
          return await getSDK().workflows.executeChatWorkflowApiV1WorkflowsExecuteChat(
            request
          );
        }
      } catch (error) {
        handleError(error, {
          source: 'useWorkflowChat.sendWorkflowMessage',
          operation: 'send workflow message',
        });
        throw error;
      }
    },
    []
  );

  // Update workflow configuration
  const updateWorkflowConfig = useCallback(
    (updates: Partial<ChatWorkflowConfig>) => {
      setCustomWorkflowConfig((prev) => ({
        ...prev,
        ...updates,
      }));
    },
    []
  );

  // Persist workflow configuration to localStorage
  useEffect(() => {
    localStorage.setItem(
      'chatter_customWorkflowConfig',
      JSON.stringify(customWorkflowConfig)
    );
  }, [customWorkflowConfig]);

  // Get current effective configuration
  const getEffectiveConfig = useCallback((): ChatWorkflowConfig => {
    return customWorkflowConfig;
  }, [customWorkflowConfig]);

  return {
    // State
    customWorkflowConfig,

    // Actions
    updateWorkflowConfig,

    // Utilities
    buildWorkflowRequest,
    sendWorkflowMessage,
    getEffectiveConfig,
  };
};
