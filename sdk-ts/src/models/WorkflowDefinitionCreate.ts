/**
 * Generated from OpenAPI schema: WorkflowDefinitionCreate
 */
import { WorkflowEdge } from './WorkflowEdge';
import { WorkflowNode } from './WorkflowNode';


export interface WorkflowDefinitionCreate {
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
  /** Whether workflow is publicly visible */
  is_public?: boolean;
  /** Workflow tags */
  tags?: string[] | null;
  /** Source template ID if created from template */
  template_id?: string | null;
}
