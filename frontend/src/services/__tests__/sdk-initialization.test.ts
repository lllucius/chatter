/**
 * Tests for SDK initialization fix
 * This test verifies that the SDK initialization error is properly handled
 */

import { describe, beforeEach, afterEach, it, expect } from 'vitest';
import { authService, getSDK, isSDKInitialized } from '../auth-service';

// Mock ChatterSDK
vi.mock('chatter-sdk', () => ({
  ChatterSDK: vi.fn().mockImplementation(() => ({
    conversations: {
      listConversationsApiV1Conversations: vi.fn(),
      deleteConversationApiV1ConversationsConversationId: vi.fn(),
    },
    workflows: {
      getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat: vi.fn(),
    },
    withAuth: vi.fn().mockImplementation(() => ({
      conversations: {
        listConversationsApiV1Conversations: vi.fn(),
        deleteConversationApiV1ConversationsConversationId: vi.fn(),
      },
      workflows: {
        getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat: vi.fn(),
      },
    })),
  })),
}));

describe('SDK Initialization Fix', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset the initialized state by setting the private property
    (authService as any).initialized = false;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should throw error when getSDK is called before initialization', () => {
    expect(() => {
      getSDK();
    }).toThrow(
      'SDK not initialized. Please wait for initialization to complete.'
    );
  });

  it('should return SDK after initialization', async () => {
    // Mock the refresh token to avoid network calls
    vi.spyOn(authService as any, 'refreshToken').mockResolvedValue(false);

    await authService.initialize();

    const sdk = getSDK();
    expect(sdk).toBeDefined();
    expect(sdk.conversations).toBeDefined();
  });

  it('should verify SDK has conversations property', async () => {
    // Mock the refresh token to avoid network calls
    vi.spyOn(authService as any, 'refreshToken').mockResolvedValue(false);

    await authService.initialize();

    const sdk = getSDK();
    expect(sdk.conversations).toBeDefined();
    expect(sdk.conversations.listConversationsApiV1Conversations).toBeDefined();
  });

  it('should verify SDK has workflows property', async () => {
    // Mock the refresh token to avoid network calls
    vi.spyOn(authService as any, 'refreshToken').mockResolvedValue(false);

    await authService.initialize();

    const sdk = getSDK();
    expect(sdk.workflows).toBeDefined();
    expect(sdk.workflows.getChatWorkflowTemplatesApiV1WorkflowsTemplatesChat).toBeDefined();
  });

  it('should check initialization status correctly', async () => {
    expect(isSDKInitialized()).toBe(false);

    // Mock the refresh token to avoid network calls
    vi.spyOn(authService as any, 'refreshToken').mockResolvedValue(false);

    await authService.initialize();

    expect(isSDKInitialized()).toBe(true);
  });
});
