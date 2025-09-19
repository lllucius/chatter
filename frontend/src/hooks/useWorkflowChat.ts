import { useState, useEffect, useCallback } from 'react';
import { getSDK } from '../services/auth-service';
import { handleError } from '../utils/error-handler';
import { 
  ChatWorkflowConfig, 
  ChatWorkflowRequest, 
  ChatWorkflowTemplate,
  ChatWorkflowTemplatesResponse
} from 'chatter-sdk';

// Re-export types for components
export type { ChatWorkflowConfig, ChatWorkflowRequest, ChatWorkflowTemplate } from 'chatter-sdk';

export const useWorkflowChat = () => {
  const [workflowTemplates, setWorkflowTemplates] = useState<Record<string, ChatWorkflowTemplate>>({});
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [customWorkflowConfig, setCustomWorkflowConfig] = useState<ChatWorkflowConfig>({
    enable_retrieval: false,
    enable_tools: false,
    enable_memory: true,
  });

  // Load available workflow templates
  const loadWorkflowTemplates = useCallback(async () => {
    try {
      console.log('[DEBUG] Getting SDK instance...');
      const sdk = getSDK();
      console.log('[DEBUG] SDK instance:', !!sdk);
      console.log('[DEBUG] SDK workflows:', !!sdk.workflows);
      console.log('[DEBUG] workflows type:', typeof sdk.workflows);
      
      if (sdk.workflows) {
        console.log('[DEBUG] workflows keys:', Object.keys(sdk.workflows));
        console.log('[DEBUG] workflows constructor:', sdk.workflows.constructor?.name);
        console.log('[DEBUG] method exists:', 'getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat' in sdk.workflows);
        console.log('[DEBUG] method type:', typeof sdk.workflows.getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat);
      }
      
      const response = await sdk.workflows.getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat();
      setWorkflowTemplates(response.templates);
    } catch (error) {
      console.error('[DEBUG] Error in loadWorkflowTemplates:', error);
      handleError(error, {
        source: 'useWorkflowChat.loadWorkflowTemplates',
        operation: 'load workflow templates',
      });
    }
  }, []);

  // Load templates on initialization
  useEffect(() => {
    loadWorkflowTemplates();
  }, [loadWorkflowTemplates]);

  // Build workflow request
  const buildWorkflowRequest = useCallback((
    message: string,
    conversationId?: string,
    additionalParams?: Partial<ChatWorkflowRequest>
  ): ChatWorkflowRequest => {
    const request: ChatWorkflowRequest = {
      message,
      conversation_id: conversationId,
      ...additionalParams,
    };

    if (selectedTemplate) {
      // Use pre-built template
      request.workflow_template_name = selectedTemplate;
    } else {
      // Use custom configuration
      request.workflow_config = customWorkflowConfig;
    }

    return request;
  }, [selectedTemplate, customWorkflowConfig]);

  // Send chat message using workflow system
  const sendWorkflowMessage = useCallback(async (
    request: ChatWorkflowRequest,
    streaming: boolean = false
  ) => {
    try {
      if (streaming) {
        // Use streaming workflow endpoint
        return await getSDK().workflows.executeChatWorkflowStreamingApiV1WorkflowsExecuteChatStreaming(request);
      } else {
        // Use non-streaming workflow endpoint
        return await getSDK().workflows.executeChatWorkflowApiV1WorkflowsExecuteChat(request);
      }
    } catch (error) {
      handleError(error, {
        source: 'useWorkflowChat.sendWorkflowMessage',
        operation: 'send workflow message',
      });
      throw error;
    }
  }, []);

  // Update workflow configuration
  const updateWorkflowConfig = useCallback((updates: Partial<ChatWorkflowConfig>) => {
    setCustomWorkflowConfig(prev => ({
      ...prev,
      ...updates,
    }));
  }, []);

  // Reset to template defaults
  const resetToTemplate = useCallback((templateName: string) => {
    const template = workflowTemplates[templateName];
    if (template) {
      setSelectedTemplate(templateName);
      setCustomWorkflowConfig(template.config);
    }
  }, [workflowTemplates]);

  // Get current effective configuration
  const getEffectiveConfig = useCallback((): ChatWorkflowConfig => {
    if (selectedTemplate && workflowTemplates[selectedTemplate]) {
      return workflowTemplates[selectedTemplate].config;
    }
    return customWorkflowConfig;
  }, [selectedTemplate, workflowTemplates, customWorkflowConfig]);

  return {
    // State
    workflowTemplates,
    selectedTemplate,
    customWorkflowConfig,
    
    // Actions
    setSelectedTemplate,
    updateWorkflowConfig,
    resetToTemplate,
    loadWorkflowTemplates,
    
    // Utilities
    buildWorkflowRequest,
    sendWorkflowMessage,
    getEffectiveConfig,
  };
};