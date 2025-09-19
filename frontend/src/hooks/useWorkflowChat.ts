import { useState, useEffect, useCallback } from 'react';
import { getSDK } from '../services/auth-service';
import { handleError } from '../utils/error-handler';

// New workflow-based chat types
export interface ChatWorkflowConfig {
  enable_retrieval: boolean;
  enable_tools: boolean;
  enable_memory: boolean;
  enable_web_search?: boolean;
  llm_config?: {
    provider?: string;
    model?: string;
    temperature: number;
    max_tokens: number;
    top_p?: number;
    presence_penalty?: number;
    frequency_penalty?: number;
  };
  retrieval_config?: {
    enabled: boolean;
    max_documents: number;
    similarity_threshold: number;
    document_ids?: string[];
    collections?: string[];
    rerank: boolean;
  };
  tool_config?: {
    enabled: boolean;
    allowed_tools?: string[];
    max_tool_calls: number;
    parallel_tool_calls: boolean;
    tool_timeout_ms: number;
  };
}

export interface ChatWorkflowRequest {
  message: string;
  conversation_id?: string;
  workflow_config?: ChatWorkflowConfig;
  workflow_definition_id?: string;
  workflow_template_name?: string;
  profile_id?: string;
  provider?: string;
  temperature?: number;
  max_tokens?: number;
  context_limit?: number;
  document_ids?: string[];
  system_prompt_override?: string;
}

export interface ChatWorkflowTemplate {
  name: string;
  description: string;
  config: ChatWorkflowConfig;
  estimated_tokens?: number;
  estimated_cost?: number;
  complexity_score: number;
  use_cases: string[];
}

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
      const response = await getSDK().workflows.getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat();
      setWorkflowTemplates(response.templates);
    } catch (error) {
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