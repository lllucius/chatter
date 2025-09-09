/**
 * Generated from OpenAPI schema: WorkflowNode
 */

export interface WorkflowNode {
  /** Unique node identifier */
  id: string;
  /** Node type */
  type: string;
  /** Node position (x, y) */
  position: Record<string, number>;
  /** Node data */
  data: WorkflowNodeData;
  /** Whether node is selected */
  selected?: boolean | null;
  /** Whether node is being dragged */
  dragging?: boolean | null;
}
