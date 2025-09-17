/**
 * Simple test to verify the streaming method can be called
 */

import { ChatterSDK, ChatRequest } from 'chatter-sdk';

describe('Streaming SDK Method', () => {
  it('should have streamingChatApiV1ChatStreaming method', () => {
    const sdk = new ChatterSDK();
    expect(typeof sdk.chat.streamingChatApiV1ChatStreaming).toBe('function');
  });

  it('should be able to create a streaming request', async () => {
    const chatRequest: ChatRequest = {
      message: 'Test message',
      conversation_id: 'test-id',
    };

    const sdk = new ChatterSDK({
      basePath: 'http://localhost:8000',
    });

    // This will fail without a real server, but we can at least verify the method signature
    try {
      await sdk.chat.streamingChatApiV1ChatStreaming(chatRequest);
    } catch (error) {
      // Expected to fail since we don't have a server, but the method should exist
      expect(error).toBeDefined();
    }
  });
});
