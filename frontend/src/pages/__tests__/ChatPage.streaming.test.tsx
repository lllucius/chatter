import { describe, it, expect, beforeEach } from 'vitest';
import type { Mock } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ChatPage from '../ChatPage';

// Mock dependencies
vi.mock('../../services/auth-service', () => {
  return {
    getSDK: vi.fn(() => ({
      chat: {
        streamingChatApiV1ChatStreaming: vi.fn(),
        chatChat: vi.fn(),
      },
      profiles: {
        listProfilesApiV1Profiles: vi.fn(() =>
          Promise.resolve({ profiles: [] })
        ),
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
    authService: {
      isAuthenticated: vi.fn(() => true),
    },
  };
});

vi.mock('../../services/toast-service', () => ({
  toastService: {
    success: vi.fn(),
    error: vi.fn(),
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

describe('ChatPage Streaming Functionality', () => {
  let mockStreamingMethod: Mock;

  beforeEach(() => {
    vi.clearAllMocks();

    // Get the streaming method mock from the auth service
    const { getSDK } = require('../../services/auth-service');
    mockStreamingMethod = getSDK().chat.streamingChatApiV1ChatStreaming;
  });

  it('should render the chat page', async () => {
    render(
      <TestWrapper>
        <ChatPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Welcome to Chatter!')).toBeInTheDocument();
    });
  });

  it('should handle streaming response correctly', async () => {
    // Mock a readable stream for streaming response
    const mockChunks = [
      'data: {"type":"start","conversation_id":"test-conv"}\n\n',
      'data: {"type":"token","content":"Hello"}\n\n',
      'data: {"type":"token","content":" there"}\n\n',
      'data: {"type":"complete","metadata":{"total_tokens":5}}\n\n',
      'data: [DONE]\n\n',
    ];

    let chunkIndex = 0;
    const mockStream = new ReadableStream({
      start(controller) {
        function pushChunk() {
          if (chunkIndex < mockChunks.length) {
            const chunk = mockChunks[chunkIndex++];
            controller.enqueue(new TextEncoder().encode(chunk));
            setTimeout(pushChunk, 10); // Simulate streaming delay
          } else {
            controller.close();
          }
        }
        pushChunk();
      },
    });

    mockStreamingMethod.mockResolvedValue(mockStream);

    render(
      <TestWrapper>
        <ChatPage />
      </TestWrapper>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Welcome to Chatter!')).toBeInTheDocument();
    });

    // Enable streaming toggle
    const streamingToggle = screen.getByRole('checkbox');
    fireEvent.click(streamingToggle);

    // Type a message
    const messageInput = screen.getByPlaceholderText(/Type your message here/);
    fireEvent.change(messageInput, {
      target: { value: 'Test streaming message' },
    });

    // Send the message
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);

    // Verify that the streaming method was called
    await waitFor(() => {
      expect(mockStreamingMethod).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Test streaming message',
        })
      );
    });

    // Verify that the message appears in the chat
    await waitFor(
      () => {
        expect(screen.getByText('Test streaming message')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );

    // Wait for the streaming response to be processed
    await waitFor(
      () => {
        expect(screen.getByText('Hello there')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );
  });

  it('should handle streaming errors gracefully', async () => {
    // Mock stream that throws an error
    mockStreamingMethod.mockRejectedValue(new Error('Streaming failed'));

    render(
      <TestWrapper>
        <ChatPage />
      </TestWrapper>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Welcome to Chatter!')).toBeInTheDocument();
    });

    // Enable streaming
    const streamingToggle = screen.getByRole('checkbox');
    fireEvent.click(streamingToggle);

    // Send a message
    const messageInput = screen.getByPlaceholderText(/Type your message here/);
    fireEvent.change(messageInput, { target: { value: 'Test error' } });

    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);

    // Verify error is handled (should show error message)
    await waitFor(
      () => {
        expect(
          screen.getByText(/Sorry, I encountered an error/)
        ).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });
});
