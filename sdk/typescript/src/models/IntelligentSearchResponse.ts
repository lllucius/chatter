/**
 * Generated from OpenAPI schema: IntelligentSearchResponse
 */
export interface IntelligentSearchResponse {
  /** Search query */
  query: string;
  /** Search results */
  results: Record<string, unknown>[];
  /** Search suggestions */
  suggestions: string[];
  /** Search analytics */
  analytics: Record<string, unknown>;
  /** Response time in milliseconds */
  response_time_ms: number;
}
