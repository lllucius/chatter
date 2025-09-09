/**
 * Generated from OpenAPI schema: PluginHealthCheckResponse
 */

export interface PluginHealthCheckResponse {
  /** Health check summary */
  summary: Record<string, unknown>;
  /** Detailed health check results for each plugin */
  results: Record<string, Record<string, unknown>>;
}
