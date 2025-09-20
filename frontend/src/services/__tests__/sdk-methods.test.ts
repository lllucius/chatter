// Integration test for SDK methods
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ChatterSDK, Configuration } from 'chatter-sdk';

// Mock fetch to simulate API responses
global.fetch = vi.fn();

describe('SDK Method Integration', () => {
  let sdk: ChatterSDK;

  beforeEach(() => {
    vi.clearAllMocks();
    sdk = new ChatterSDK(
      new Configuration({
        basePath: 'http://localhost:8000',
      })
    );
  });

  it('should have all expected API groups', () => {
    expect(sdk.conversations).toBeDefined();
    expect(sdk.workflows).toBeDefined();
    expect(sdk.auth).toBeDefined();
    expect(sdk.agents).toBeDefined();
    expect(sdk.documents).toBeDefined();
    expect(sdk.prompts).toBeDefined();
    expect(sdk.profiles).toBeDefined();
    expect(sdk.health).toBeDefined();
  });

  it('should have conversations API methods', () => {
    expect(typeof sdk.conversations.listConversationsApiV1Conversations).toBe(
      'function'
    );
    expect(typeof sdk.conversations.createConversationApiV1Conversations).toBe(
      'function'
    );
    expect(
      typeof sdk.conversations.getConversationApiV1ConversationsConversationId
    ).toBe('function');
  });

  it('should have workflow API methods', () => {
    expect(
      typeof sdk.workflows.executeChatWorkflowApiV1WorkflowsExecuteChat
    ).toBe('function');
    expect(
      typeof sdk.workflows
        .executeChatWorkflowStreamingApiV1WorkflowsExecuteChatStreaming
    ).toBe('function');
    expect(
      typeof sdk.workflows.getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat
    ).toBe('function');
  });

  it('should have auth API methods', () => {
    expect(typeof sdk.auth.authLogin).toBe('function');
    expect(typeof sdk.auth.authRegister).toBe('function');
    expect(typeof sdk.auth.refreshTokenApiV1AuthRefresh).toBe('function');
  });
});
