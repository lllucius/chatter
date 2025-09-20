import { describe, it, expect } from 'vitest';
import { parseSSELine, processSSEBuffer } from '../sse-parser';

describe('SSE Parser Utility', () => {
  it('should parse valid SSE lines correctly', () => {
    const line = 'data: {"type":"token","content":"hello"}';
    const result = parseSSELine(line);
    
    expect(result).toEqual({
      type: 'token',
      content: 'hello'
    });
  });

  it('should handle [DONE] marker correctly', () => {
    const line = 'data: [DONE]';
    const result = parseSSELine(line);
    
    expect(result).toEqual({ type: 'done' });
  });

  it('should reject lines that still have data: prefix', () => {
    const line = 'data: data: {"type":"token"}';
    const result = parseSSELine(line);
    
    expect(result).toBeNull();
  });

  it('should reject non-JSON content', () => {
    const line = 'data: this is not json';
    const result = parseSSELine(line);
    
    expect(result).toBeNull();
  });

  it('should process buffer correctly', () => {
    const buffer = '';
    const data = 'data: {"type":"start"}\n\ndata: {"type":"token","content":"hello"}\n\n';
    
    const result = processSSEBuffer(buffer, data);
    
    expect(result.events).toHaveLength(2);
    expect(result.events[0]).toEqual({ type: 'start' });
    expect(result.events[1]).toEqual({ type: 'token', content: 'hello' });
    expect(result.updatedBuffer).toBe('');
  });

  it('should handle incomplete data in buffer', () => {
    const buffer = '';
    const data = 'data: {"type":"start"}\n\ndata: {"type":"tok';
    
    const result = processSSEBuffer(buffer, data);
    
    expect(result.events).toHaveLength(1);
    expect(result.events[0]).toEqual({ type: 'start' });
    expect(result.updatedBuffer).toBe('data: {"type":"tok');
  });

  it('should prevent the original JSON parsing error', () => {
    // This is the exact scenario that was causing the error
    const problematicLine = 'data: {"type":"token","content":"hello"}';
    
    // This should NOT throw an error
    const result = parseSSELine(problematicLine);
    expect(result).toEqual({
      type: 'token',
      content: 'hello'
    });
    
    // Verify that direct JSON.parse would fail (this is what was happening before)
    expect(() => JSON.parse(problematicLine)).toThrow(/Unexpected token 'd'/);
  });
});