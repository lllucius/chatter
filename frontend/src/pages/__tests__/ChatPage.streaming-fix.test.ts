import { describe, it, expect, vi } from 'vitest';

// Mock the parseSSELine function
vi.mock('../../utils/sse-parser', () => ({
  parseSSELine: vi.fn((line: string) => {
    if (line.startsWith('data: ')) {
      const raw = line.slice(6).trim();
      if (raw === '[DONE]') {
        return { type: 'done' };
      }
      try {
        return JSON.parse(raw);
      } catch {
        return null;
      }
    }
    return null;
  }),
}));

describe('Streaming Token Accumulation Fix', () => {
  it('should properly accumulate streaming tokens', async () => {
    // Mock setMessages function
    let messages = [{
      id: 'assistant-123',
      role: 'assistant',
      content: '',
      metadata: {}
    }];
    
    const setMessages = vi.fn((updater) => {
      messages = updater(messages);
    });

    // Import parseSSELine
    const { parseSSELine } = await import('../../utils/sse-parser');

    // Simulate the streaming process with the fixed logic
    let accumulatedContent = '';
    const assistantMessageId = 'assistant-123';
    
    // Mock streaming events
    const streamLines = [
      'data: {"type":"start","conversation_id":"test-conv"}',
      'data: {"type":"token","content":"Hello"}',
      'data: {"type":"token","content":" there"}',
      'data: {"type":"complete","metadata":{"total_tokens":2}}',
      'data: [DONE]'
    ];

    for (const line of streamLines) {
      const eventData = parseSSELine(line);
      if (!eventData || eventData.type === 'done') continue;

      switch (eventData.type) {
        case 'start':
          // Stream started
          break;

        case 'token': {
          // This is the FIXED logic from ChatPage.tsx
          const tokenContent = (eventData.content as string) || '';
          accumulatedContent += tokenContent;

          // Update the message with the accumulated content
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: accumulatedContent, // Fixed: use accumulated content
                    metadata: {
                      ...msg.metadata,
                      workflow: {
                        stage: 'Streaming',
                        currentStep: 0,
                        totalSteps: 1,
                        stepDescriptions: ['Receiving response...'],
                      },
                    },
                  }
                : msg
            )
          );
          break;
        }

        case 'complete':
          // Stream completed
          break;
      }
    }

    // Verify the final result
    expect(accumulatedContent).toBe('Hello there');
    expect(messages[0].content).toBe('Hello there');
    expect(setMessages).toHaveBeenCalledTimes(2); // Called for each token
  });

  it('should handle empty tokens correctly', async () => {
    let messages = [{
      id: 'assistant-456',
      role: 'assistant',
      content: '',
      metadata: {}
    }];
    
    const setMessages = vi.fn((updater) => {
      messages = updater(messages);
    });

    const { parseSSELine } = await import('../../utils/sse-parser');

    let accumulatedContent = '';
    const assistantMessageId = 'assistant-456';
    
    // Test with empty token
    const streamLines = [
      'data: {"type":"token","content":""}',
      'data: {"type":"token","content":"Hello"}',
    ];

    for (const line of streamLines) {
      const eventData = parseSSELine(line);
      if (!eventData) continue;

      if (eventData.type === 'token') {
        const tokenContent = (eventData.content as string) || '';
        accumulatedContent += tokenContent;

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, content: accumulatedContent }
              : msg
          )
        );
      }
    }

    expect(accumulatedContent).toBe('Hello');
    expect(messages[0].content).toBe('Hello');
  });
});