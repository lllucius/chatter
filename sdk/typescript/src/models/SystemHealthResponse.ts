/**
 * Generated from OpenAPI schema: SystemHealthResponse
 */
export interface SystemHealthResponse {
  /** Overall system status */
  status: string;
  /** Individual service statuses */
  services: Record<string, string>;
  /** System metrics */
  metrics: Record<string, unknown>;
  /** Health check timestamp */
  timestamp: string;
}
