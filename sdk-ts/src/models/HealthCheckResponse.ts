/**
 * Generated from OpenAPI schema: HealthCheckResponse
 */

export interface HealthCheckResponse {
  /** Health status */
  status: HealthStatus;
  /** Service name */
  service: string;
  /** Service version */
  version: string;
  /** Environment */
  environment: string;
}
