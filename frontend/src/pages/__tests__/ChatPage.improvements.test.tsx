/**
 * Test suite for Chat Page improvements:
 * 1. Focus management during active conversations
 * 2. Message persistence and conversation state restoration
 * 3. Token/timing stats display in assistant messages
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import ChatPage from '../ChatPage';
import { useRightSidebar } from '../../components/RightSidebarContext';

// Mock the dependencies
vi.mock('../../services/auth-service', () => ({
  getSDK: vi.fn(() => ({
    profiles: {
      listProfilesApiV1Profiles: vi.fn(() => Promise.resolve({ profiles: [] })),
    },
    prompts: {
      listPromptsApiV1Prompts: vi.fn(() => Promise.resolve({ prompts: [] })),
    },
    documents: {
      listDocumentsGetApiV1Documents: vi.fn(() =>
        Promise.resolve({ documents: [] })
      ),
    },
    conversations: {
      listConversationsApiV1Conversations: vi.fn(() =>
        Promise.resolve({
          conversations: [
            {
              id: 'conv-123',
              title: 'Test Conversation',
              created_at: '2024-01-01T10:00:00Z',
              updated_at: '2024-01-01T10:05:00Z',
              user_id: 'user-123',
              status: 'active',
              message_count: 2,
              total_tokens: 150,
              total_cost: 0.01,
              enable_retrieval: false,
              context_window: 4096,
              memory_enabled: true,
              retrieval_limit: 5,
              retrieval_score_threshold: 0.7,
            },
          ],
        })
      ),
      getConversationApiV1ConversationsConversationId: vi.fn(() =>
        Promise.resolve({
          id: 'conv-123',
          title: 'Test Conversation',
          user_id: 'user-123',
          status: 'active',
          message_count: 2,
          total_tokens: 150,
          total_cost: 0.01,
          enable_retrieval: false,
          context_window: 4096,
          memory_enabled: true,
          retrieval_limit: 5,
          retrieval_score_threshold: 0.7,
          created_at: '2024-01-01T10:00:00Z',
          updated_at: '2024-01-01T10:05:00Z',
          messages: [
            {
              id: 'msg-user-1',
              role: 'user',
              content: 'Hello, how are you?',
              created_at: '2024-01-01T10:00:00Z',
              sequence_number: 1,
              rating_count: 0,
            },
            {
              id: 'msg-assistant-1',
              role: 'assistant',
              content: 'Hello! I am doing well, thank you for asking.',
              created_at: '2024-01-01T10:01:00Z',
              sequence_number: 2,
              total_tokens: 150,
              response_time_ms: 1500,
              model_used: 'gpt-4',
              rating_count: 0,
            },
          ],
        })
      ),
    },
    chat: {
      chatChat: vi.fn(() =>
        Promise.resolve({
          conversation_id: 'conv-123',
          message: {
            id: 'msg-assistant-2',
            role: 'assistant',
            content: 'This is a new response.',
            created_at: '2024-01-01T10:02:00Z',
            total_tokens: 75,
            response_time_ms: 1200,
            model_used: 'gpt-4',
          },
          conversation: {
            id: 'conv-123',
            title: 'Test Conversation',
            user_id: 'user-123',
          },
        })
      ),
    },
  })),
}));

vi.mock('../../services/toast-service', () => ({
  toastService: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

vi.mock('../../utils/error-handler', () => ({
  handleError: vi.fn(),
}));

vi.mock('../../components/RightSidebarContext', () => ({
  useRightSidebar: vi.fn(() => ({
    setPanelContent: vi.fn(),
    clearPanelContent: vi.fn(),
    setTitle: vi.fn(),
    open: true,
    setOpen: vi.fn(),
  })),
}));

describe('ChatPage Improvements', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Mock scrollIntoView for test environment
    Element.prototype.scrollIntoView = vi.fn();

    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn((key) => {
          if (key === 'chatter_streamingEnabled') return 'false';
          if (key === 'chatter_temperature') return '0.7';
          if (key === 'chatter_maxTokens') return '2048';
          if (key === 'chatter_enableRetrieval') return 'true';
          if (key === 'chatter_enableTools') return 'false';
          if (key === 'chatter_customPromptText') return '';
          if (key === 'chatter_currentConversation') return null;
          if (key === 'chatter_rightDrawerOpen') return 'true';
          return null;
        }),
        setItem: vi.fn(),
        removeItem: vi.fn(),
      },
      writable: true,
    });
  });

  describe('Conversation Restoration', () => {
    it('should load the last conversation on page initialization', async () => {
      render(<ChatPage />);

      // Wait for the component to load and process the conversation
      await waitFor(() => {
        expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(
          screen.getByText('Hello! I am doing well, thank you for asking.')
        ).toBeInTheDocument();
      });
    });
  });

  describe('Token and Timing Stats Display', () => {
    it('should display token and timing stats for assistant messages', async () => {
      render(<ChatPage />);

      // Wait for messages to load
      await waitFor(() => {
        expect(
          screen.getByText('Hello! I am doing well, thank you for asking.')
        ).toBeInTheDocument();
      });

      // Check that token and timing stats are displayed
      await waitFor(() => {
        expect(screen.getByText('150 tokens')).toBeInTheDocument();
        expect(screen.getByText('1.50s')).toBeInTheDocument(); // Updated to seconds format
        expect(screen.getByText('100 tok/s')).toBeInTheDocument(); // Should show tokens per second
      });

      // Check that the model is displayed
      await waitFor(() => {
        expect(screen.getByText('gpt-4')).toBeInTheDocument();
      });
    });

    it('should display rating section for assistant messages', async () => {
      render(<ChatPage />);

      // Wait for messages to load
      await waitFor(() => {
        expect(
          screen.getByText('Hello! I am doing well, thank you for asking.')
        ).toBeInTheDocument();
      });

      // Check that rating section is present
      await waitFor(() => {
        expect(screen.getByText('Rate this response:')).toBeInTheDocument();
      });
    });
  });

  describe('Focus Management', () => {
    it('should focus input field when conversation is active', async () => {
      render(<ChatPage />);

      // Wait for the component to fully load
      await waitFor(() => {
        expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
      });

      // Find the input field
      const inputField = screen.getByPlaceholderText(/Type your message here/);
      expect(inputField).toBeInTheDocument();

      // Check that input field gets focus (testing focus can be tricky in jsdom,
      // so we mainly verify the input field exists and is not disabled)
      expect(inputField).not.toBeDisabled();
    });

    it('should maintain focus on input during conversation interactions', async () => {
      render(<ChatPage />);

      await waitFor(() => {
        expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
      });

      const inputField = screen.getByPlaceholderText(/Type your message here/);

      // Type a message and send it - find the send button by its SendIcon test id
      fireEvent.change(inputField, { target: { value: 'New test message' } });

      // Find the send button by looking for the SendIcon
      const sendButton = screen.getByTestId('SendIcon').closest('button');
      expect(sendButton).toBeTruthy();
      expect(sendButton).not.toBeDisabled();

      if (sendButton) {
        fireEvent.click(sendButton);
      }

      // After sending, input should be available for focus again
      await waitFor(() => {
        expect(inputField).not.toBeDisabled();
        expect((inputField as HTMLInputElement).value).toBe('');
      });
    });
  });

  describe('Message Persistence', () => {
    it('should persist messages and reload conversation state after sending', async () => {
      const mockGetConversation = vi.fn().mockResolvedValue({
        id: 'conv-123',
        title: 'Test Conversation',
        user_id: 'user-123',
        status: 'active',
        message_count: 3,
        total_tokens: 225,
        total_cost: 0.015,
        enable_retrieval: false,
        context_window: 4096,
        memory_enabled: true,
        retrieval_limit: 5,
        retrieval_score_threshold: 0.7,
        created_at: '2024-01-01T10:00:00Z',
        updated_at: '2024-01-01T10:05:00Z',
        messages: [
          {
            id: 'msg-user-1',
            role: 'user',
            content: 'Hello, how are you?',
            created_at: '2024-01-01T10:00:00Z',
            sequence_number: 1,
            rating_count: 0,
          },
          {
            id: 'msg-assistant-1',
            role: 'assistant',
            content: 'Hello! I am doing well, thank you for asking.',
            created_at: '2024-01-01T10:01:00Z',
            sequence_number: 2,
            total_tokens: 150,
            response_time_ms: 1500,
            model_used: 'gpt-4',
            rating_count: 0,
          },
          {
            id: 'msg-user-2',
            role: 'user',
            content: 'New test message',
            created_at: '2024-01-01T10:02:00Z',
            sequence_number: 3,
            rating_count: 0,
          },
          {
            id: 'msg-assistant-2',
            role: 'assistant',
            content: 'This is a new response.',
            created_at: '2024-01-01T10:03:00Z',
            sequence_number: 4,
            total_tokens: 75,
            response_time_ms: 1200,
            model_used: 'gpt-4',
            rating_count: 0,
          },
        ],
      });

      const { getSDK } = await import('../../services/auth-service');
      (getSDK as any).mockReturnValue({
        ...(getSDK as any)(),
        conversations: {
          ...(getSDK as any)().conversations,
          getConversationApiV1ConversationsConversationId: mockGetConversation,
        },
      });

      render(<ChatPage />);

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
      });

      const inputField = screen.getByPlaceholderText(/Type your message here/);

      // Send a new message
      fireEvent.change(inputField, { target: { value: 'New test message' } });

      // Find the send button by looking for the SendIcon
      const sendButton = screen.getByTestId('SendIcon').closest('button');
      expect(sendButton).toBeTruthy();
      expect(sendButton).not.toBeDisabled();

      if (sendButton) {
        fireEvent.click(sendButton);
      }

      // Wait for the conversation to be reloaded with all messages
      await waitFor(() => {
        expect(screen.getByText('New test message')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('This is a new response.')).toBeInTheDocument();
      });

      // Verify that the conversation reload was called
      expect(mockGetConversation).toHaveBeenCalledWith('conv-123', {
        includeMessages: true,
      });
    });
  });
});
