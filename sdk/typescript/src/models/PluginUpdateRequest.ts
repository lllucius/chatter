/**
 * Generated from OpenAPI schema: PluginUpdateRequest
 */
export interface PluginUpdateRequest {
  /** Enable/disable plugin */
  enabled?: boolean | null;
  /** Plugin configuration */
  configuration?: Record<string, unknown> | null;
}
