/**
 * Generated from OpenAPI schema: WorkflowDefinitionUpdate
 */
import { WorkflowEdge } from './WorkflowEdge';
import { WorkflowNode } from './WorkflowNode';


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
