/**
 * Generated from OpenAPI schema: MetricsResponse
 */

export interface MetricsResponse {
  /** Metrics collection timestamp (ISO 8601) */
  timestamp: string;
  /** Service name */
  service: string;
  /** Service version */
  version: string;
  /** Environment */
  environment: string;
  /** Health metrics */
  health: Record<string, unknown>;
  /** Performance statistics */
  performance: Record<string, unknown>;
  /** Endpoint statistics */
  endpoints: Record<string, unknown>;
}
