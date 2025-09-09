/**
 * Generated from OpenAPI schema: ReadinessCheckResponse
 */

export interface ReadinessCheckResponse {
  /** Readiness status */
  status: ReadinessStatus;
  /** Service name */
  service: string;
  /** Service version */
  version: string;
  /** Environment */
  environment: string;
  /** Health check results */
  checks: Record<string, unknown>;
}
