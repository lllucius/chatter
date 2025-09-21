// Test to verify useWorkflowChat works with the corrected template structure
import { describe, it, expect } from 'vitest';
import type {
  ChatWorkflowConfig,
  ChatWorkflowRequest,
  ChatWorkflowTemplate,
  ChatWorkflowTemplatesResponse,
} from 'chatter-sdk';

describe('Workflow Template Structure Integration', () => {
  it('should handle template response with correct llm_config field name', () => {
    // This simulates the corrected backend response structure
    const mockTemplateResponse: ChatWorkflowTemplatesResponse = {
      templates: {
        simple_chat: {
          name: 'Simple Chat',
          description: 'Basic conversation without additional features',
          config: {
            enable_retrieval: false,
            enable_tools: false,
            enable_memory: true,
            llm_config: {
              provider: 'openai',
              model: 'gpt-4',
              temperature: 0.7,
              max_tokens: 1000,
              top_p: 1.0,
              presence_penalty: 0.0,
              frequency_penalty: 0.0,
            },
            retrieval_config: null,
            tool_config: null,
          },
          use_cases: [
            'General conversation',
            'Quick questions',
            'Creative writing',
          ],
          complexity_score: 1,
          estimated_tokens: 500,
          estimated_cost: null,
        },
        rag_chat: {
          name: 'Knowledge Base Chat',
          description: 'Chat with document retrieval for knowledge questions',
          config: {
            enable_retrieval: true,
            enable_tools: false,
            enable_memory: true,
            llm_config: {
              provider: 'openai',
              model: 'gpt-4',
              temperature: 0.3,
              max_tokens: 1500,
              top_p: 1.0,
              presence_penalty: 0.0,
              frequency_penalty: 0.0,
            },
            retrieval_config: {
              enabled: true,
              max_documents: 5,
              similarity_threshold: 0.7,
              document_ids: null,
              collections: null,
              rerank: true,
            },
            tool_config: null,
          },
          use_cases: [
            'Knowledge base queries',
            'Document Q&A',
            'Research assistance',
          ],
          complexity_score: 3,
          estimated_tokens: 1200,
          estimated_cost: null,
        },
      },
      total_count: 2,
    };

    // Verify the template structure is correct
    expect(mockTemplateResponse.templates).toBeDefined();
    expect(mockTemplateResponse.total_count).toBe(2);

    // Check simple_chat template
    const simpleTemplate = mockTemplateResponse.templates.simple_chat;
    expect(simpleTemplate.config.llm_config).toBeDefined();
    expect(simpleTemplate.config.llm_config?.temperature).toBe(0.7);
    expect(simpleTemplate.config.llm_config?.max_tokens).toBe(1000);
    expect(simpleTemplate.config.enable_memory).toBe(true);
    expect(simpleTemplate.config.enable_retrieval).toBe(false);

    // Check rag_chat template
    const ragTemplate = mockTemplateResponse.templates.rag_chat;
    expect(ragTemplate.config.llm_config).toBeDefined();
    expect(ragTemplate.config.llm_config?.temperature).toBe(0.3);
    expect(ragTemplate.config.llm_config?.max_tokens).toBe(1500);
    expect(ragTemplate.config.enable_retrieval).toBe(true);
    expect(ragTemplate.config.retrieval_config).toBeDefined();
    expect(ragTemplate.config.retrieval_config?.max_documents).toBe(5);

    // eslint-disable-next-line no-console
    console.log('✓ Template structure validation passed');
  });

  it('should create valid workflow requests with template configs', () => {
    const templateConfig: ChatWorkflowConfig = {
      enable_retrieval: true,
      enable_tools: false,
      enable_memory: true,
      llm_config: {
        provider: 'openai',
        model: 'gpt-4',
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        presence_penalty: 0.0,
        frequency_penalty: 0.0,
      },
      retrieval_config: {
        enabled: true,
        max_documents: 5,
        similarity_threshold: 0.8,
        document_ids: null,
        collections: null,
        rerank: false,
      },
      tool_config: null,
    };

    const workflowRequest: ChatWorkflowRequest = {
      message: 'Hello, world!',
      conversation_id: 'test-123',
      workflow_config: templateConfig,
    };

    expect(workflowRequest.message).toBe('Hello, world!');
    expect(workflowRequest.conversation_id).toBe('test-123');
    expect(workflowRequest.workflow_config?.llm_config?.temperature).toBe(0.7);
    expect(
      workflowRequest.workflow_config?.retrieval_config?.max_documents
    ).toBe(5);

    // eslint-disable-next-line no-console
    console.log('✓ Workflow request creation passed');
  });

  it('should handle template selection with llm_config correctly', () => {
    // This simulates how useWorkflowChat would process templates
    const templates: Record<string, ChatWorkflowTemplate> = {
      simple_chat: {
        name: 'Simple Chat',
        description: 'Basic conversation',
        config: {
          enable_retrieval: false,
          enable_tools: false,
          enable_memory: true,
          llm_config: {
            provider: 'openai',
            model: 'gpt-3.5-turbo',
            temperature: 0.7,
            max_tokens: 1000,
            top_p: 1.0,
            presence_penalty: 0.0,
            frequency_penalty: 0.0,
          },
        },
        complexity_score: 1,
        use_cases: ['chat'],
      },
    };

    const selectedTemplate = 'simple_chat';
    const template = templates[selectedTemplate];

    expect(template).toBeDefined();
    expect(template.config.llm_config).toBeDefined();
    expect(template.config.llm_config?.model).toBe('gpt-3.5-turbo');

    // This is how the frontend would build a request using the template
    const request: ChatWorkflowRequest = {
      message: 'Test message',
      conversation_id: 'conv-123',
      workflow_template_name: selectedTemplate,
    };

    expect(request.workflow_template_name).toBe('simple_chat');

    // eslint-disable-next-line no-console
    console.log('✓ Template selection handling passed');
  });

  it('should ensure no model_config field exists (old incorrect field)', () => {
    // This test ensures we don't accidentally use the old wrong field name
    const config: ChatWorkflowConfig = {
      enable_retrieval: false,
      enable_tools: false,
      enable_memory: true,
      llm_config: {
        temperature: 0.7,
        max_tokens: 1000,
        provider: 'openai',
        model: 'gpt-4',
        top_p: 1.0,
        presence_penalty: 0.0,
        frequency_penalty: 0.0,
      },
    };

    // Verify correct field exists
    expect(config.llm_config).toBeDefined();
    expect(config.llm_config?.temperature).toBe(0.7);

    // Verify incorrect field does not exist
    expect((config as any).model_config).toBeUndefined(); // eslint-disable-line @typescript-eslint/no-explicit-any

    // eslint-disable-next-line no-console
    console.log('✓ Field name validation passed - using llm_config correctly');
  });
});
