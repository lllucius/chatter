/**
 * Generated from OpenAPI schema: WorkflowTemplateDirectExecutionRequest
 */
export interface WorkflowTemplateDirectExecutionRequest {
  /** Template data to execute */
  template: Record<string, unknown>;
  /** Input data for execution */
  input_data?: Record<string, unknown> | null;
  /** Enable debug mode */
  debug_mode?: boolean;
}
