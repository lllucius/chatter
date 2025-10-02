import { describe, it, expect } from 'vitest';
import { format, isValid, parseISO } from 'date-fns';

// Helper function from ConversationsPage
const formatTimestamp = (timestamp: string, formatString: string): string => {
  try {
    const date = parseISO(timestamp);
    if (!isValid(date)) {
      return '--:--';
    }
    return format(date, formatString);
  } catch {
    return '--:--';
  }
};

describe('Date Formatting Safety', () => {
  it('should format valid ISO dates correctly', () => {
    const timestamp = '2024-01-01T12:30:45Z';
    const result = formatTimestamp(timestamp, 'HH:mm:ss');
    
    expect(result).toBe('12:30:45');
    expect(result).not.toBe('--:--');
  });

  it('should handle invalid date strings gracefully', () => {
    const invalidTimestamp = 'not-a-date';
    const result = formatTimestamp(invalidTimestamp, 'HH:mm:ss');
    
    expect(result).toBe('--:--');
  });

  it('should handle empty strings gracefully', () => {
    const result = formatTimestamp('', 'HH:mm:ss');
    
    expect(result).toBe('--:--');
  });

  it('should handle malformed ISO dates gracefully', () => {
    const malformedTimestamp = '2024-13-45T99:99:99Z'; // Invalid month/day/time
    const result = formatTimestamp(malformedTimestamp, 'HH:mm:ss');
    
    expect(result).toBe('--:--');
  });

  it('should work with different format strings', () => {
    const timestamp = '2024-03-15T14:25:30Z';
    
    const timeResult = formatTimestamp(timestamp, 'HH:mm:ss');
    expect(timeResult).toBe('14:25:30');
    
    const dateResult = formatTimestamp(timestamp, 'MMM dd, yyyy');
    expect(dateResult).toBe('Mar 15, 2024');
    
    const fullResult = formatTimestamp(timestamp, 'MMM dd, yyyy HH:mm');
    expect(fullResult).toBe('Mar 15, 2024 14:25');
  });

  it('should handle dates without timezone info', () => {
    const timestamp = '2024-01-01T12:30:45';
    const result = formatTimestamp(timestamp, 'HH:mm:ss');
    
    // parseISO should handle this
    expect(result).not.toBe('--:--');
    expect(result).toMatch(/^\d{2}:\d{2}:\d{2}$/);
  });

  it('should prevent React rendering errors from invalid dates', () => {
    // This test verifies that the function never throws
    const invalidInputs = [
      'invalid',
      '',
      'null',
      '0',
      'undefined',
      '2024-99-99',
      'abc123',
    ];

    invalidInputs.forEach((input) => {
      expect(() => formatTimestamp(input, 'HH:mm:ss')).not.toThrow();
      const result = formatTimestamp(input, 'HH:mm:ss');
      expect(typeof result).toBe('string');
      expect(result).toBe('--:--');
    });
  });
});
