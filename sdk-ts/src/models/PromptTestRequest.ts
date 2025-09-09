/**
 * Generated from OpenAPI schema: PromptTestRequest
 */

export interface PromptTestRequest {
  /** Variables to test with */
  variables: Record<string, unknown>;
  /** Only validate, don't render */
  validate_only?: boolean;
  /** Include detailed performance metrics */
  include_performance_metrics?: boolean;
  /** Test timeout in milliseconds */
  timeout_ms?: number;
}
