/**
 * Generated from OpenAPI schema: WorkflowTemplateValidationResponse
 */
export interface WorkflowTemplateValidationResponse {
  /** Whether template is valid */
  is_valid: boolean;
  /** Validation errors */
  errors?: string[];
  /** Validation warnings */
  warnings?: string[];
  /** Extracted template information */
  template_info?: Record<string, unknown> | null;
}
