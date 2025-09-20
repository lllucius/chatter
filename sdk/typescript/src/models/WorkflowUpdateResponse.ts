/**
 * Generated from OpenAPI schema: WorkflowUpdateResponse
 */
export interface WorkflowUpdateResponse {
  /** Workflow ID */
  workflow_id: string;
  /** Update status */
  status: string;
  /** Update message */
  message: string;
  /** Fields that were updated */
  updated_fields: string[];
}
