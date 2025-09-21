import { useState, useCallback } from 'react';
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
    useState<ChatWorkflowConfig>({
      enable_retrieval: false,
      enable_tools: false,
      enable_memory: true,
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
