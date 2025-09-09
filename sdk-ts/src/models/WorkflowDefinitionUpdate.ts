/**
 * Generated from OpenAPI schema: WorkflowDefinitionUpdate
 */

export interface WorkflowDefinitionUpdate {
  /** Workflow name */
  name?: string | null;
  /** Workflow description */
  description?: string | null;
  /** Workflow nodes */
  nodes?: WorkflowNode[] | null;
  /** Workflow edges */
  edges?: WorkflowEdge[] | null;
  /** Additional metadata */
  metadata?: Record<string, unknown> | null;
}
