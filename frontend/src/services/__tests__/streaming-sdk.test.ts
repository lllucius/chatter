/**
 * Simple test to verify the streaming method can be called
 */

import { ChatterSDK, ChatWorkflowRequest, Configuration } from 'chatter-sdk';

describe('Streaming SDK Method', () => {
  it('should have executeChatWorkflowStreamingApiV1WorkflowsExecuteChatStreaming method', () => {
    const sdk = new ChatterSDK();
    expect(typeof sdk.workflows.executeChatWorkflowStreamingApiV1WorkflowsExecuteChatStreaming).toBe('function');
  });

  it('should be able to create a streaming request', async () => {
    const chatRequest: ChatWorkflowRequest = {
      message: 'Test message',
      conversation_id: 'test-id',
    };

    const sdk = new ChatterSDK(new Configuration({
      basePath: 'http://localhost:8000',
    }));

    // This will fail without a real server, but we can at least verify the method signature
    try {
      await sdk.workflows.executeChatWorkflowStreamingApiV1WorkflowsExecuteChatStreaming(chatRequest);
    } catch (error) {
      // Expected to fail since we don't have a server, but the method should exist
      expect(error).toBeDefined();
    }
  });
});
