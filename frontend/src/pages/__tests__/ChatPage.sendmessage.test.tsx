import { describe, it, expect, vi, beforeEach, Mock } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ChatPage from '../ChatPage';

// Mock dependencies
vi.mock('../../services/auth-service', () => ({
  getSDK: vi.fn(() => ({
    chat: {
      chatChat: vi.fn(),
    },
    profiles: {
      listProfilesApiV1Profiles: vi.fn(() => Promise.resolve({ profiles: [] })),
    },
    prompts: {
      listPromptsApiV1Prompts: vi.fn(() => Promise.resolve({ prompts: [] })),
    },
    documents: {
      listDocumentsApiV1Documents: vi.fn(() =>
        Promise.resolve({ documents: [] })
      ),
    },
    conversations: {
      createConversationApiV1Conversations: vi.fn(() =>
        Promise.resolve({ id: 'test-conv-id' })
      ),
    },
  })),
}));

vi.mock('../../services/toast-service', () => ({
  toastService: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
  },
}));

vi.mock('../../components/RightSidebarContext', () => ({
  useRightSidebar: () => ({
    setPanelContent: vi.fn(),
    clearPanelContent: vi.fn(),
    setTitle: vi.fn(),
    open: false,
    setOpen: vi.fn(),
  }),
}));

// Mock Material-UI components that need special handling
vi.mock('@mui/material', async () => {
  const actual = await vi.importActual('@mui/material');
  return {
    ...actual,
    useTheme: () => ({ palette: { mode: 'light' } }),
  };
});

// Create a wrapper component for context providers
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('ChatPage sendMessage Fix', () => {
  let mockChatChat: Mock;

  beforeEach(() => {
    vi.clearAllMocks();

    // Get the mock SDK
    const { getSDK } = require('../../services/auth-service');
    const mockSDK = getSDK();
    mockChatChat = mockSDK.chat.chatChat;
  });

  it('should handle valid API response correctly', async () => {
    // Mock a valid chat response
    const mockResponse = {
      conversation_id: 'test-conv-id',
      message: {
        id: 'test-msg-id',
        role: 'assistant',
        content: 'Hello! How can I help you?',
        model_used: 'gpt-4',
        total_tokens: 10,
        response_time_ms: 500,
      },
      conversation: {
        id: 'test-conv-id',
        title: 'Test Conversation',
      },
    };

    mockChatChat.mockResolvedValue(mockResponse);

    render(
      <TestWrapper>
        <ChatPage />
      </TestWrapper>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Welcome to Chatter!')).toBeInTheDocument();
    });

    // Disable streaming to test the non-streaming path
    const streamingToggle = screen.getByRole('checkbox');
    if (streamingToggle.checked) {
      fireEvent.click(streamingToggle);
    }

    // Type a message
    const messageInput = screen.getByPlaceholderText(/Type your message here/);
    fireEvent.change(messageInput, {
      target: { value: 'Test message' },
    });

    // Send the message
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);

    // Verify that the correct API method was called
    await waitFor(() => {
      expect(mockChatChat).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Test message',
          stream: false,
        })
      );
    });

    // Verify that the assistant response is displayed
    await waitFor(() => {
      expect(
        screen.getByText('Hello! How can I help you?')
      ).toBeInTheDocument();
    });
  });

  it('should handle invalid API response gracefully', async () => {
    // Mock an invalid response (missing message property)
    const mockResponse = {
      conversation_id: 'test-conv-id',
      // message property is missing!
      conversation: {
        id: 'test-conv-id',
        title: 'Test Conversation',
      },
    };

    mockChatChat.mockResolvedValue(mockResponse);

    render(
      <TestWrapper>
        <ChatPage />
      </TestWrapper>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Welcome to Chatter!')).toBeInTheDocument();
    });

    // Disable streaming to test the non-streaming path
    const streamingToggle = screen.getByRole('checkbox');
    if (streamingToggle.checked) {
      fireEvent.click(streamingToggle);
    }

    // Type a message
    const messageInput = screen.getByPlaceholderText(/Type your message here/);
    fireEvent.change(messageInput, {
      target: { value: 'Test message' },
    });

    // Send the message
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);

    // Verify that the API method was called
    await waitFor(() => {
      expect(mockChatChat).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Test message',
          stream: false,
        })
      );
    });

    // Verify that error handling is triggered (no crash)
    // The component should not crash and should remain functional
    await waitFor(() => {
      expect(screen.getByText('Welcome to Chatter!')).toBeInTheDocument();
    });
  });
});
