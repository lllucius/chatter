/**
 * Test to reproduce the exact streaming JSON parsing error
 * Based on the error: SyntaxError: Unexpected token 'd', "data: {"ty"... is not valid JSON
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the streaming scenario that's causing the error
describe('Streaming Response Parsing Bug Reproduction', () => {
  it('should identify the source of the JSON parsing error', () => {
    // This is the exact error message from the logs
    const errorPattern = /Unexpected token 'd', "data: \{"ty"/;
    
    // Test what happens if code tries to parse the full SSE line
    const sseLineWithPrefix = 'data: {"type":"token","content":"hello"}';
    
    let caughtError: Error | null = null;
    try {
      // This is what's causing the error - parsing the full line instead of just the JSON
      JSON.parse(sseLineWithPrefix);
    } catch (error) {
      caughtError = error as Error;
    }
    
    expect(caughtError).toBeTruthy();
    expect(caughtError?.message).toMatch(errorPattern);
  });

  it('should verify the correct parsing approach works', () => {
    const sseLineWithPrefix = 'data: {"type":"token","content":"hello"}';
    
    // Correct approach - strip the prefix first
    let parsed: any = null;
    let error: Error | null = null;
    
    try {
      if (sseLineWithPrefix.startsWith('data: ')) {
        const raw = sseLineWithPrefix.slice(6).trim();
        parsed = JSON.parse(raw);
      }
    } catch (e) {
      error = e as Error;
    }
    
    expect(error).toBeNull();
    expect(parsed).toEqual({
      type: 'token',
      content: 'hello'
    });
  });

  it('should test the exact buffer processing scenario that might cause the bug', () => {
    // Simulate what happens in the streaming processing
    const streamChunks = [
      'data: {"type":"start"}\n',
      'data: {"type":"token","content":"hello"}\n'
    ];
    
    let buffer = '';
    const results: any[] = [];
    
    for (const chunk of streamChunks) {
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const raw = line.slice(6).trim();
          
          if (raw && raw !== '[DONE]') {
            try {
              const eventData = JSON.parse(raw);
              results.push(eventData);
            } catch (error) {
              // This should not happen with correct implementation
              throw new Error(`Failed to parse: ${raw}, error: ${(error as Error).message}`);
            }
          }
        }
      }
    }
    
    expect(results).toHaveLength(2);
    expect(results[0]).toEqual({ type: 'start' });
    expect(results[1]).toEqual({ type: 'token', content: 'hello' });
  });

  it('should identify potential race condition in streaming', () => {
    // Test what happens with incomplete/malformed data
    const malformedChunks = [
      'data: {"type":"start"}\n',
      'data: {"ty', // Incomplete JSON that could cause issues
      'pe":"token"}\n'
    ];
    
    let buffer = '';
    const results: any[] = [];
    const errors: string[] = [];
    
    for (const chunk of malformedChunks) {
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const raw = line.slice(6).trim();
          
          if (raw && raw !== '[DONE]') {
            try {
              const eventData = JSON.parse(raw);
              results.push(eventData);
            } catch (error) {
              // This is expected for incomplete JSON
              errors.push(`Failed to parse: ${raw}`);
            }
          }
        }
      }
    }
    
    // Should parse the complete first line
    expect(results).toHaveLength(1);
    expect(results[0]).toEqual({ type: 'start' });
    
    // Should have error for incomplete JSON
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain('{"ty');
    
    // After processing all chunks, buffer should contain the incomplete part
    expect(buffer).toBe('pe":"token"}');
  });

  it('should test if there is any code that might parse the wrong data', () => {
    // This test checks if there's any scenario where the full SSE line
    // (including "data: " prefix) might be passed to JSON.parse
    
    const problematicScenarios = [
      'data: {"type":"token"}',
      'data: {"type":"start","conversation_id":"123"}',
      'data: {"type":"complete","metadata":{"tokens":5}}'
    ];
    
    for (const scenario of problematicScenarios) {
      // This should fail (wrong approach)
      expect(() => JSON.parse(scenario)).toThrow(/Unexpected token 'd'/);
      
      // This should work (correct approach)
      const raw = scenario.slice(6).trim();
      expect(() => JSON.parse(raw)).not.toThrow();
    }
  });
});