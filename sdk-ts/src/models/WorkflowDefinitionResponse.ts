/**
 * Generated from OpenAPI schema: WorkflowDefinitionResponse
 */

export interface WorkflowDefinitionResponse {
  /** Workflow name */
  name: string;
  /** Workflow description */
  description?: string | null;
  /** Workflow nodes */
  nodes: WorkflowNode[];
  /** Workflow edges */
  edges: WorkflowEdge[];
  /** Additional metadata */
  metadata?: Record<string, unknown> | null;
  /** Whether workflow is public */
  is_public?: boolean;
  /** Workflow tags */
  tags?: string[] | null;
  /** Source template ID if created from template */
  template_id?: string | null;
  /** Unique node identifier */
  id: string;
  /** Owner user ID */
  owner_id: string;
  /** Workflow version */
  version?: number;
}
