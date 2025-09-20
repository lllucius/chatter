/**
 * Generated from OpenAPI schema: ToolServerAnalyticsResponse
 */
export interface ToolServerAnalyticsResponse {
  /** Total requests processed */
  total_requests: number;
  /** Successful requests */
  successful_requests: number;
  /** Failed requests */
  failed_requests: number;
  /** Average response time in milliseconds */
  average_response_time_ms: number;
  /** Tool usage statistics */
  tool_usage_stats: Record<string, number>;
  /** Server uptime statistics */
  server_uptime_stats: Record<string, unknown>;
  /** Error distribution by type */
  error_distribution: Record<string, number>;
}
