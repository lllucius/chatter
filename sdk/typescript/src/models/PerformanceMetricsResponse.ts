/**
 * Generated from OpenAPI schema: PerformanceMetricsResponse
 */
export interface PerformanceMetricsResponse {
  /** Average response time */
  avg_response_time_ms: number;
  /** Median response time */
  median_response_time_ms: number;
  /** 95th percentile response time */
  p95_response_time_ms: number;
  /** 99th percentile response time */
  p99_response_time_ms: number;
  /** Average requests per minute */
  requests_per_minute: number;
  /** Average tokens per minute */
  tokens_per_minute: number;
  /** Total number of errors */
  total_errors: number;
  /** Error rate percentage */
  error_rate: number;
  /** Errors grouped by type */
  errors_by_type: Record<string, number>;
  /** Performance metrics by model */
  performance_by_model: Record<string, Record<string, number>>;
  /** Performance metrics by provider */
  performance_by_provider: Record<string, Record<string, number>>;
  /** Average database response time */
  database_response_time_ms: number;
  /** Average vector search time */
  vector_search_time_ms: number;
  /** Average embedding generation time */
  embedding_generation_time_ms: number;
}
