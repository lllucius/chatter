import { describe, it, expect, beforeEach } from 'vitest';
import { chatterClient } from '../chatter-sdk';

describe('ChatterSDK', () => {
  beforeEach(() => {
    // Clear any stored tokens before each test
    localStorage.clear();
    chatterClient.clearToken();
  });

  it('should be properly initialized', () => {
    expect(chatterClient).toBeDefined();
    expect(chatterClient.auth).toBeDefined();
    expect(chatterClient.agents).toBeDefined();
    expect(chatterClient.modelRegistry).toBeDefined();
    expect(chatterClient.toolServers).toBeDefined();
    expect(chatterClient.conversations).toBeDefined();
  });

  it('should handle authentication state correctly', () => {
    expect(chatterClient.isAuthenticated()).toBe(false);
    expect(chatterClient.getToken()).toBeNull();

    const testToken = 'test-token-123';
    chatterClient.setToken(testToken);
    
    expect(chatterClient.isAuthenticated()).toBe(true);
    expect(chatterClient.getToken()).toBe(testToken);
    expect(localStorage.getItem('chatter_access_token')).toBe(testToken);
  });

  it('should clear authentication correctly', () => {
    const testToken = 'test-token-123';
    chatterClient.setToken(testToken);
    expect(chatterClient.isAuthenticated()).toBe(true);

    chatterClient.clearToken();
    
    expect(chatterClient.isAuthenticated()).toBe(false);
    expect(chatterClient.getToken()).toBeNull();
    expect(localStorage.getItem('chatter_access_token')).toBeNull();
  });

  it('should have convenience methods for tool servers', () => {
    expect(typeof chatterClient.getToolServers).toBe('function');
    expect(typeof chatterClient.createToolServer).toBe('function');
    expect(typeof chatterClient.updateToolServer).toBe('function');
    expect(typeof chatterClient.enableToolServer).toBe('function');
    expect(typeof chatterClient.disableToolServer).toBe('function');
  });

  it('should have convenience methods for conversations', () => {
    expect(typeof chatterClient.listConversations).toBe('function');
    expect(typeof chatterClient.createConversation).toBe('function');
    expect(typeof chatterClient.deleteConversation).toBe('function');
    expect(typeof chatterClient.getConversation).toBe('function');
    expect(typeof chatterClient.updateConversation).toBe('function');
  });

  it('should have conversations object with API methods', () => {
    expect(chatterClient.conversations).toBeDefined();
    expect(typeof chatterClient.conversations.listConversationsApiV1ChatConversationsGet).toBe('function');
    expect(typeof chatterClient.conversations.createConversationApiV1ChatConversationsPost).toBe('function');
    expect(typeof chatterClient.conversations.deleteConversationApiV1ChatConversationsConversationIdDelete).toBe('function');
    expect(typeof chatterClient.conversations.getConversationApiV1ChatConversationsConversationIdGet).toBe('function');
  });
});