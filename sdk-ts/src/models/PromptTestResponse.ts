/**
 * Generated from OpenAPI schema: PromptTestResponse
 */

export interface PromptTestResponse {
  /** Rendered prompt content */
  rendered_content?: string | null;
  /** Validation results */
  validation_result: Record<string, unknown>;
  /** Estimated token count */
  estimated_tokens?: number | null;
  /** Test execution time */
  test_duration_ms: number;
  /** Template variables actually used */
  template_variables_used: string[];
  /** Security warnings if any */
  security_warnings?: string[];
  /** Detailed performance metrics */
  performance_metrics?: Record<string, unknown> | null;
}
