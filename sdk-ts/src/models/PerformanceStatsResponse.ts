/**
 * Generated from OpenAPI schema: PerformanceStatsResponse
 */

export interface PerformanceStatsResponse {
  /** Total number of executions */
  total_executions: number;
  /** Average execution time in milliseconds */
  avg_execution_time_ms: number;
  /** Minimum execution time in milliseconds */
  min_execution_time_ms: number;
  /** Maximum execution time in milliseconds */
  max_execution_time_ms: number;
  /** Execution count by workflow type */
  workflow_types: Record<string, number>;
  /** Error count by type */
  error_counts: Record<string, number>;
  /** Cache statistics */
  cache_stats: Record<string, unknown>;
  /** Tool usage statistics */
  tool_stats: Record<string, unknown>;
  /** Statistics timestamp */
  timestamp: number;
}
