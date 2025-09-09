/**
 * Generated from OpenAPI schema: CorrelationTraceResponse
 */

export interface CorrelationTraceResponse {
  /** Correlation ID */
  correlation_id: string;
  /** Number of requests in trace */
  trace_length: number;
  /** List of requests in trace */
  requests: Record<string, unknown>[];
}
