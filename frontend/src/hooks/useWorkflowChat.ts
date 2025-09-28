import { useState, useCallback, useEffect } from 'react';
import { getSDK } from '../services/auth-service';
import { handleError } from '../utils/error-handler';
import {
  ChatWorkflowConfig,
  ChatWorkflowRequest,
} from 'chatter-sdk';

// Re-export types for components
export type {
  ChatWorkflowConfig,
  ChatWorkflowRequest,
} from 'chatter-sdk';

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

  // Send chat message using dedicated chat API
  const sendWorkflowMessage = useCallback(
    async (request: ChatWorkflowRequest, streaming: boolean = false) => {
      try {
        if (streaming) {
          // Use streaming chat endpoint
          return await getSDK().chat.streamingChatEndpointApiV1ChatStreaming(
            request
          );
        } else {
          // Use non-streaming chat endpoint
          return await getSDK().chat.chatEndpointApiV1ChatChat(
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
