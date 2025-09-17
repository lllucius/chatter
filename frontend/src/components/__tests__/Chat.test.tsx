import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect } from 'vitest';

// Mock chat component
const ChatComponent: React.FC = () => {
  const [messages, setMessages] = React.useState<
    Array<{ id: string; content: string; role: 'user' | 'assistant' }>
  >([]);
  const [input, setInput] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      content: input,
      role: 'user' as const,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    setTimeout(() => {
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        content: `Echo: ${input}`,
        role: 'assistant' as const,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 100);
  };

  return (
    <div data-testid="chat-component">
      <div data-testid="messages-container">
        {messages.map((message) => (
          <div key={message.id} data-testid={`message-${message.role}`}>
            <strong>{message.role}:</strong> {message.content}
          </div>
        ))}
        {isLoading && <div data-testid="loading-indicator">Thinking...</div>}
      </div>
      <div data-testid="input-container">
        <input
          data-testid="message-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
        />
        <button
          data-testid="send-button"
          onClick={sendMessage}
          disabled={!input.trim() || isLoading}
        >
          Send
        </button>
      </div>
    </div>
  );
};

describe('Chat Component', () => {
  it('renders chat interface correctly', () => {
    render(<ChatComponent />);

    expect(screen.getByTestId('chat-component')).toBeInTheDocument();
    expect(screen.getByTestId('messages-container')).toBeInTheDocument();
    expect(screen.getByTestId('input-container')).toBeInTheDocument();
    expect(screen.getByTestId('message-input')).toBeInTheDocument();
    expect(screen.getByTestId('send-button')).toBeInTheDocument();
  });

  it('allows user to type in message input', () => {
    render(<ChatComponent />);

    const input = screen.getByTestId('message-input') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'Hello, world!' } });

    expect(input.value).toBe('Hello, world!');
  });

  it('sends message when send button is clicked', async () => {
    render(<ChatComponent />);

    const input = screen.getByTestId('message-input') as HTMLInputElement;
    const sendButton = screen.getByTestId('send-button');

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    expect(screen.getByTestId('message-user')).toBeInTheDocument();
    expect(screen.getByText(/Test message/)).toBeInTheDocument();
    expect(input.value).toBe('');
  });

  it('sends message when Enter key is pressed', () => {
    render(<ChatComponent />);

    const input = screen.getByTestId('message-input') as HTMLInputElement;

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    expect(screen.getByTestId('message-user')).toBeInTheDocument();
    expect(screen.getByText(/Test message/)).toBeInTheDocument();
  });

  it('shows loading indicator while waiting for response', () => {
    render(<ChatComponent />);

    const input = screen.getByTestId('message-input') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByTestId('send-button'));

    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    expect(screen.getByText('Thinking...')).toBeInTheDocument();
  });

  it('displays assistant response after loading', async () => {
    render(<ChatComponent />);

    const input = screen.getByTestId('message-input') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByTestId('send-button'));

    await waitFor(
      () => {
        expect(screen.getByTestId('message-assistant')).toBeInTheDocument();
      },
      { timeout: 500 }
    );

    expect(screen.getByText(/Echo: Test message/)).toBeInTheDocument();
    expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
  });

  it('disables send button when input is empty', () => {
    render(<ChatComponent />);

    const sendButton = screen.getByTestId('send-button') as HTMLButtonElement;
    expect(sendButton.disabled).toBe(true);
  });

  it('prevents sending empty messages', () => {
    render(<ChatComponent />);

    const input = screen.getByTestId('message-input') as HTMLInputElement;
    const sendButton = screen.getByTestId('send-button');

    fireEvent.change(input, { target: { value: '   ' } });
    fireEvent.click(sendButton);

    expect(screen.queryByTestId('message-user')).not.toBeInTheDocument();
  });
});
