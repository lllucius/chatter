/**
 * Generated from OpenAPI schema: WorkflowExecutionRequest
 */
export interface WorkflowExecutionRequest {
  /** Execution input data */
  input_data?: Record<string, unknown> | null;
  /** Workflow definition ID */
  definition_id: string;
  /** Enable debug mode for detailed logging */
  debug_mode?: boolean;
}
