/**
 * Generated from OpenAPI schema: SystemAnalyticsResponse
 */
export interface SystemAnalyticsResponse {
  /** Total number of users */
  total_users: number;
  /** Active users today */
  active_users_today: number;
  /** Active users this week */
  active_users_week: number;
  /** Active users this month */
  active_users_month: number;
  /** System uptime in seconds */
  system_uptime_seconds: number;
  /** Average CPU usage percentage */
  avg_cpu_usage: number;
  /** Average memory usage percentage */
  avg_memory_usage: number;
  /** Current database connections */
  database_connections: number;
  /** Total API requests */
  total_api_requests: number;
  /** Requests by endpoint */
  requests_per_endpoint: Record<string, number>;
  /** Average API response time */
  avg_api_response_time: number;
  /** API error rate */
  api_error_rate: number;
  /** Total storage usage */
  storage_usage_bytes: number;
  /** Vector database size */
  vector_database_size_bytes: number;
  /** Cache hit rate */
  cache_hit_rate: number;
}
