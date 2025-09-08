import { describe, it, expect, beforeEach } from 'vitest';
import { chatterSDK } from '../chatter-sdk';

describe('ChatterSDK', () => {
  beforeEach(() => {
    // Clear any stored tokens before each test
    localStorage.clear();
    chatterSDK.clearToken();
  });

  it('should be properly initialized', () => {
    expect(chatterSDK).toBeDefined();
    expect(chatterSDK.auth).toBeDefined();
    expect(chatterSDK.agents).toBeDefined();
    expect(chatterSDK.modelRegistry).toBeDefined();
    expect(chatterSDK.toolServers).toBeDefined();
    expect(chatterSDK.conversations).toBeDefined();
  });

  it('should handle authentication state correctly', () => {
    expect(chatterSDK.isAuthenticated()).toBe(false);
    expect(chatterSDK.getToken()).toBeNull();

    const testToken = 'test-token-123';
    chatterSDK.setToken(testToken);
    
    expect(chatterSDK.isAuthenticated()).toBe(true);
    expect(chatterSDK.getToken()).toBe(testToken);
    expect(localStorage.getItem('chatter_access_token')).toBe(testToken);
  });

  it('should clear authentication correctly', () => {
    const testToken = 'test-token-123';
    chatterSDK.setToken(testToken);
    expect(chatterSDK.isAuthenticated()).toBe(true);

    chatterSDK.clearToken();
    
    expect(chatterSDK.isAuthenticated()).toBe(false);
    expect(chatterSDK.getToken()).toBeNull();
    expect(localStorage.getItem('chatter_access_token')).toBeNull();
  });

  it('should have convenience methods for tool servers', () => {
    expect(typeof chatterSDK.getToolServers).toBe('function');
    expect(typeof chatterSDK.createToolServer).toBe('function');
    expect(typeof chatterSDK.updateToolServer).toBe('function');
    expect(typeof chatterSDK.enableToolServer).toBe('function');
    expect(typeof chatterSDK.disableToolServer).toBe('function');
  });

  it('should have convenience methods for conversations', () => {
    expect(typeof chatterSDK.listConversations).toBe('function');
    expect(typeof chatterSDK.createConversation).toBe('function');
    expect(typeof chatterSDK.deleteConversation).toBe('function');
    expect(typeof chatterSDK.getConversation).toBe('function');
    expect(typeof chatterSDK.updateConversation).toBe('function');
  });

  it('should have conversations object with API methods', () => {
    expect(chatterSDK.conversations).toBeDefined();
    expect(typeof chatterSDK.conversations.listConversationsApiV1ChatConversationsGet).toBe('function');
    expect(typeof chatterSDK.conversations.createConversationApiV1ChatConversationsPost).toBe('function');
    expect(typeof chatterSDK.conversations.deleteConversationApiV1ChatConversationsConversationIdDelete).toBe('function');
    expect(typeof chatterSDK.conversations.getConversationApiV1ChatConversationsConversationIdGet).toBe('function');
  });
});