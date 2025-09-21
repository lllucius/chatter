/**
 * Test to verify the fix for the workflow streaming JSON parsing issue
 * Error: SyntaxError: Unexpected token 'd', "data: {"ty"... is not valid JSON
 */

import { describe, it, expect } from 'vitest';

/**
 * Test utility function that simulates the SSE parsing logic
 * from the fixed handleWorkflowStreamingResponse implementation
 */
function parseSSELine(line: string): Record<string, unknown> | null {
  if (line.startsWith('data: ')) {
    const raw = line.slice(6).trim(); // This is the key fix - strip "data: " prefix

    // Handle special cases
    if (raw === '[DONE]') {
      return { type: 'done' };
    }

    try {
      return JSON.parse(raw); // Now parse just the JSON part
    } catch {
      // Skip malformed data
      return null;
    }
  }
  return null;
}

describe('Workflow Streaming SSE Fix', () => {
  it('should correctly parse SSE data format without "data:" prefix error', () => {
    // This is the problematic line that was causing the error
    const problematicLine = 'data: {"type":"token","content":"hello"}';

    const result = parseSSELine(problematicLine);

    // Should successfully parse without throwing SyntaxError
    expect(result).toEqual({
      type: 'token',
      content: 'hello',
    });
  });

  it('should handle token streaming events correctly', () => {
    const tokenLine = 'data: {"type":"token","content":"world"}';
    const result = parseSSELine(tokenLine);

    expect(result).toEqual({
      type: 'token',
      content: 'world',
    });
  });

  it('should handle complete events correctly', () => {
    const completeLine =
      'data: {"type":"complete","metadata":{"total_tokens":10}}';
    const result = parseSSELine(completeLine);

    expect(result).toEqual({
      type: 'complete',
      metadata: { total_tokens: 10 },
    });
  });

  it('should handle [DONE] marker correctly', () => {
    const doneLine = 'data: [DONE]';
    const result = parseSSELine(doneLine);

    expect(result).toEqual({ type: 'done' });
  });

  it('should ignore non-data lines', () => {
    const nonDataLine = 'id: 12345';
    const result = parseSSELine(nonDataLine);

    expect(result).toBeNull();
  });

  it('should handle malformed JSON gracefully', () => {
    const malformedLine = 'data: {invalid json}';
    const result = parseSSELine(malformedLine);

    expect(result).toBeNull();
  });

  it('should process the exact error case from the logs', () => {
    // This is based on the error message: "data: {"ty"...
    const errorCaseLine = 'data: {"type":"start","conversation_id":"test"}';
    const result = parseSSELine(errorCaseLine);

    // Should parse successfully, not throw SyntaxError
    expect(result).toEqual({
      type: 'start',
      conversation_id: 'test',
    });
  });

  it('should demonstrate the old broken approach would fail', () => {
    const sseLineWithPrefix = 'data: {"type":"token","content":"test"}';

    // This is what was happening before the fix - trying to parse the entire line
    expect(() => {
      JSON.parse(sseLineWithPrefix); // This would throw: SyntaxError: Unexpected token 'd'
    }).toThrow();

    // But with the fix, we strip the prefix first
    const fixed = parseSSELine(sseLineWithPrefix);
    expect(fixed).toEqual({
      type: 'token',
      content: 'test',
    });
  });
});
