// Test that workflow types and functions work correctly
import { describe, it, expect } from 'vitest';

// Import the types we've updated
import type {
  ChatWorkflowConfig,
  ChatWorkflowRequest,
  ChatWorkflowTemplate,
} from '../../hooks/useWorkflowChat';

describe('SDK Type Integration', () => {
  it('should properly type ChatWorkflowConfig', () => {
    const config: ChatWorkflowConfig = {
      enable_retrieval: true,
      enable_tools: false,
      enable_memory: true,
      llm_config: {
        provider: 'openai',
        model: 'gpt-4',
        temperature: 0.7,
        max_tokens: 2000,
      },
      retrieval_config: {
        enabled: true,
        max_documents: 5,
        similarity_threshold: 0.8,
        rerank: false,
      },
    };

    expect(config.enable_retrieval).toBe(true);
    expect(config.llm_config?.provider).toBe('openai');
    expect(config.retrieval_config?.enabled).toBe(true);
  });

  it('should properly type ChatWorkflowRequest', () => {
    const request: ChatWorkflowRequest = {
      message: 'Hello, world!',
      conversation_id: 'test-123',
      workflow_config: {
        enable_retrieval: false,
        enable_tools: true,
        enable_memory: true,
      },
    };

    expect(request.message).toBe('Hello, world!');
    expect(request.conversation_id).toBe('test-123');
    expect(request.workflow_config?.enable_tools).toBe(true);
  });

  it('should properly type ChatWorkflowTemplate', () => {
    const template: ChatWorkflowTemplate = {
      name: 'Test Template',
      description: 'A test template',
      config: {
        enable_retrieval: true,
        enable_tools: false,
        enable_memory: true,
      },
      estimated_tokens: 1000,
      estimated_cost: 0.02,
      complexity_score: 3,
      use_cases: ['testing', 'development'],
    };

    expect(template.name).toBe('Test Template');
    expect(template.config.enable_retrieval).toBe(true);
    expect(template.complexity_score).toBe(3);
  });
});
