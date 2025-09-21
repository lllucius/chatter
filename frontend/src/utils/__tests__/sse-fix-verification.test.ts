/**
 * Final verification test that demonstrates the fix for the streaming JSON parsing error
 * This test specifically verifies that the original error scenario is now handled safely
 */

import { describe, it, expect } from 'vitest';
import { parseSSELine } from '../sse-parser';

describe('Streaming JSON Parsing Error Fix Verification', () => {
  it("should prevent the original SyntaxError: Unexpected token 'd' error", () => {
    // This is the exact error scenario that was occurring:
    // SyntaxError: Unexpected token 'd', "data: {"ty"... is not valid JSON

    const problematicSSELine = 'data: {"type":"token","content":"hello"}';

    // BEFORE THE FIX: This would cause the error
    // JSON.parse(problematicSSELine) -> SyntaxError: Unexpected token 'd'
    expect(() => JSON.parse(problematicSSELine)).toThrow(
      /Unexpected token 'd'/
    );

    // AFTER THE FIX: This now works safely
    const result = parseSSELine(problematicSSELine);
    expect(result).toEqual({
      type: 'token',
      content: 'hello',
    });
  });

  it('should handle the exact error pattern from the logs', () => {
    // The error showed: "data: {"ty"... suggesting partial/malformed JSON
    const partialData = 'data: {"ty';

    // The old approach would fail
    expect(() => JSON.parse(partialData)).toThrow();

    // The new approach handles it gracefully
    const result = parseSSELine(partialData);
    expect(result).toBeNull(); // Safely returns null for invalid JSON
  });

  it('should work with all valid SSE event types', () => {
    const testCases = [
      'data: {"type":"start","conversation_id":"123"}',
      'data: {"type":"token","content":"Hello World"}',
      'data: {"type":"complete","metadata":{"total_tokens":5}}',
      'data: {"type":"error","message":"Something went wrong"}',
      'data: [DONE]',
    ];

    for (const sseData of testCases) {
      const result = parseSSELine(sseData);
      expect(result).toBeTruthy();

      if (sseData.includes('[DONE]')) {
        expect(result?.type).toBe('done');
      } else {
        expect(result?.type).toBeDefined();
      }
    }
  });

  it('should handle edge cases that could cause parsing errors', () => {
    const edgeCases = [
      'data: ', // Empty data
      'data: {}', // Empty object
      'data: {"type":}', // Invalid JSON
      'data: "plain string"', // Non-object JSON
      'not-data: {"type":"token"}', // Not an SSE data line
      'data: data: {"type":"nested"}', // Nested data prefix (should be caught)
    ];

    for (const edgeCase of edgeCases) {
      // None of these should throw an error
      expect(() => parseSSELine(edgeCase)).not.toThrow();

      // Handle specific expected results
      const result = parseSSELine(edgeCase);
      if (edgeCase === 'data: {}') {
        expect(result).toEqual({});
      } else if (edgeCase === 'data: ') {
        expect(result).toEqual({ type: 'done' }); // Empty data becomes 'done'
      } else {
        expect(result).toBeNull();
      }
    }
  });
});
