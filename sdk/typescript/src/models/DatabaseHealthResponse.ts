/**
 * Generated from OpenAPI schema: DatabaseHealthResponse
 */
export interface DatabaseHealthResponse {
  /** Database connection status */
  connected: boolean;
  /** Database response time in milliseconds */
  response_time_ms: number;
  /** Active database connections */
  active_connections: number;
  /** Query performance metrics */
  query_performance: Record<string, number>;
  /** Database disk usage in MB */
  disk_usage_mb: number;
  /** Last backup timestamp */
  last_backup?: string | null;
}
