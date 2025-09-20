/**
 * Generated from OpenAPI schema: AnalyticsHealthResponse
 */
export interface AnalyticsHealthResponse {
  /** Health status */
  status: string;
  /** Database connection status */
  database_connected: boolean;
  /** Cache connection status */
  cache_connected: boolean;
  /** Last health check timestamp */
  last_check: string;
  /** Service status details */
  services: Record<string, string>;
}
