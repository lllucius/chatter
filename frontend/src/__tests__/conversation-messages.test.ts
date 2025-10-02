import { describe, it, expect } from 'vitest';
import type { ConversationWithMessages, MessageResponse } from 'chatter-sdk';
import { ConversationStatus, MessageRole } from 'chatter-sdk';

describe('ConversationWithMessages Type Safety', () => {
  it('should have messages as a required field', () => {
    const mockMessages: MessageResponse[] = [
      {
        id: 'msg-1',
        conversation_id: 'conv-1',
        role: MessageRole.user,
        content: 'Hello',
        sequence_number: 1,
        created_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'msg-2',
        conversation_id: 'conv-1',
        role: MessageRole.assistant,
        content: 'Hi there!',
        sequence_number: 2,
        created_at: '2024-01-01T00:00:01Z',
      },
    ];

    const conversation: ConversationWithMessages = {
      id: 'conv-1',
      title: 'Test Conversation',
      description: 'A test conversation',
      user_id: 'user-1',
      status: ConversationStatus.active,
      enable_retrieval: false,
      message_count: 2,
      total_tokens: 100,
      total_cost: 0.01,
      context_window: 4096,
      memory_enabled: false,
      retrieval_limit: 10,
      retrieval_score_threshold: 0.7,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: mockMessages,
    };

    // Verify messages is always present (not undefined)
    expect(conversation.messages).toBeDefined();
    expect(Array.isArray(conversation.messages)).toBe(true);
    expect(conversation.messages).toHaveLength(2);
  });

  it('should allow empty messages array', () => {
    const conversation: ConversationWithMessages = {
      id: 'conv-2',
      title: 'Empty Conversation',
      description: null,
      user_id: 'user-2',
      status: ConversationStatus.active,
      enable_retrieval: false,
      message_count: 0,
      total_tokens: 0,
      total_cost: 0,
      context_window: 4096,
      memory_enabled: false,
      retrieval_limit: 10,
      retrieval_score_threshold: 0.7,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [],
    };

    // Empty array is valid
    expect(conversation.messages).toBeDefined();
    expect(Array.isArray(conversation.messages)).toBe(true);
    expect(conversation.messages).toHaveLength(0);
  });

  it('should verify messages field structure matches MessageResponse', () => {
    const message: MessageResponse = {
      id: 'msg-test',
      conversation_id: 'conv-test',
      role: MessageRole.user,
      content: 'Test message',
      sequence_number: 1,
      created_at: '2024-01-01T00:00:00Z',
    };

    const conversation: ConversationWithMessages = {
      id: 'conv-test',
      title: 'Type Test',
      description: null,
      user_id: 'user-test',
      status: ConversationStatus.active,
      enable_retrieval: false,
      message_count: 1,
      total_tokens: 50,
      total_cost: 0.001,
      context_window: 4096,
      memory_enabled: false,
      retrieval_limit: 10,
      retrieval_score_threshold: 0.7,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [message],
    };

    // Verify message structure
    expect(conversation.messages[0]).toHaveProperty('id');
    expect(conversation.messages[0]).toHaveProperty('role');
    expect(conversation.messages[0]).toHaveProperty('content');
    expect(conversation.messages[0]).toHaveProperty('created_at');
    expect(conversation.messages[0].role).toBe(MessageRole.user);
    expect(conversation.messages[0].content).toBe('Test message');
  });
});
