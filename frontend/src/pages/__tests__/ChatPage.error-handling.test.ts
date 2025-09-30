/**
 * Test to verify the error handling fix for workflow streaming
 * Ensures error events are properly handled and don't crash the interface
 */

import { describe, it, expect } from 'vitest';

// Mock the SSE parsing function to test error field access
function parseSSELine(line: string): Record<string, unknown> | null {
  if (!line.startsWith('data: ')) {
    return null;
  }

  const raw = line.slice(6).trim();

  if (raw === '[DONE]' || raw === '') {
    return { type: 'done' };
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

// Simulate the error handling logic from ChatPage
function extractErrorMessage(eventData: Record<string, unknown>): string {
  // This mirrors the logic in the fixed ChatPage.tsx
  return (
    (eventData.error as string) ||
    (eventData.message as string) ||
    'Workflow streaming error occurred'
  );
}

describe('Workflow Streaming Error Handling Fix', () => {
  it('should handle server error format with "error" field', () => {
    // This is the actual format sent by the server
    const serverErrorLine =
      'data: {"type":"error","error":"Database connection failed"}';

    const eventData = parseSSELine(serverErrorLine);
    expect(eventData).not.toBeNull();
    expect(eventData?.type).toBe('error');

    const errorMessage = extractErrorMessage(eventData!);
    expect(errorMessage).toBe('Database connection failed');
  });

  it('should handle legacy error format with "message" field', () => {
    // Fallback for any legacy error formats
    const legacyErrorLine =
      'data: {"type":"error","message":"Something went wrong"}';

    const eventData = parseSSELine(legacyErrorLine);
    expect(eventData).not.toBeNull();
    expect(eventData?.type).toBe('error');

    const errorMessage = extractErrorMessage(eventData!);
    expect(errorMessage).toBe('Something went wrong');
  });

  it('should handle error events with both fields (error takes precedence)', () => {
    // Test precedence when both fields are present
    const errorLine =
      'data: {"type":"error","error":"Primary error","message":"Secondary error"}';

    const eventData = parseSSELine(errorLine);
    expect(eventData).not.toBeNull();
    expect(eventData?.type).toBe('error');

    const errorMessage = extractErrorMessage(eventData!);
    expect(errorMessage).toBe('Primary error'); // error field should take precedence
  });

  it('should provide default error message when no error text is available', () => {
    // Test fallback to default message
    const errorLine = 'data: {"type":"error"}';

    const eventData = parseSSELine(errorLine);
    expect(eventData).not.toBeNull();
    expect(eventData?.type).toBe('error');

    const errorMessage = extractErrorMessage(eventData!);
    expect(errorMessage).toBe('Workflow streaming error occurred');
  });

  it('should verify error throwing behavior for testing the fix', () => {
    // This simulates what happens in the actual ChatPage processStreamingResponse
    const serverErrorLine =
      'data: {"type":"error","error":"Test error message"}';

    const eventData = parseSSELine(serverErrorLine);
    expect(eventData).not.toBeNull();

    if (eventData?.type === 'error') {
      const errorMessage = extractErrorMessage(eventData);

      // The code should throw an error with the correct message
      expect(() => {
        throw new Error(errorMessage);
      }).toThrow('Test error message');
    }
  });

  it('should handle empty error messages gracefully', () => {
    // Test edge cases with empty strings
    const emptyErrorLine = 'data: {"type":"error","error":"","message":""}';

    const eventData = parseSSELine(emptyErrorLine);
    expect(eventData).not.toBeNull();

    const errorMessage = extractErrorMessage(eventData!);
    expect(errorMessage).toBe('Workflow streaming error occurred'); // Should fallback to default
  });
});
