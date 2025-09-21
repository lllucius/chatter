/**
 * Utility functions for parsing Server-Sent Events (SSE) data
 * Provides safe and consistent SSE data parsing across the application
 */

/**
 * Parse a single SSE line and extract the JSON data
 * @param line - The SSE line to parse (e.g., "data: {...}")
 * @returns Parsed JSON object or null if parsing fails or line is invalid
 */
export function parseSSELine(line: string): Record<string, unknown> | null {
  // Only process lines that start with "data: "
  if (!line.startsWith('data: ')) {
    return null;
  }

  // Extract the raw JSON content by removing the "data: " prefix
  const raw = line.slice(6).trim();

  // Handle special SSE markers
  if (raw === '[DONE]' || raw === '') {
    return { type: 'done' };
  }

  try {
    // Additional validation to prevent parsing malformed SSE lines
    if (raw.startsWith('data:')) {
      // eslint-disable-next-line no-console
      console.warn(
        'SSE Parser: Detected nested data: prefix, skipping line:',
        raw
      );
      return null;
    }

    // Ensure we have JSON-like content before attempting to parse
    if (!raw.startsWith('{') && !raw.startsWith('[')) {
      // eslint-disable-next-line no-console
      console.warn(
        'SSE Parser: Line does not appear to contain JSON, skipping:',
        raw
      );
      return null;
    }

    return JSON.parse(raw);
  } catch (error) {
    // eslint-disable-next-line no-console
    console.warn('SSE Parser: Failed to parse JSON:', {
      raw,
      error: (error as Error).message,
      line,
    });
    return null;
  }
}

/**
 * Process multiple SSE lines from a buffer
 * @param lines - Array of SSE lines to process
 * @returns Array of successfully parsed JSON objects
 */
export function parseSSELines(lines: string[]): Record<string, unknown>[] {
  const results: Record<string, unknown>[] = [];

  for (const line of lines) {
    const parsed = parseSSELine(line);
    if (parsed) {
      results.push(parsed);
    }
  }

  return results;
}

/**
 * Safe SSE buffer processing for streaming responses
 * Handles incomplete lines and proper buffering
 * @param buffer - Current buffer content
 * @param newData - New data to add to buffer
 * @returns Object with processed events and updated buffer
 */
export function processSSEBuffer(
  buffer: string,
  newData: string
): {
  events: Record<string, unknown>[];
  updatedBuffer: string;
} {
  // Add new data to buffer
  const updatedBuffer = buffer + newData;

  // Split into lines
  const lines = updatedBuffer.split('\n');

  // Keep the last line in buffer (might be incomplete)
  const remainingBuffer = lines.pop() || '';

  // Process complete lines
  const events = parseSSELines(lines);

  return {
    events,
    updatedBuffer: remainingBuffer,
  };
}
