/**
 * Generated from OpenAPI schema: WorkflowEdge
 */
import { WorkflowEdgeData } from './WorkflowEdgeData';

export interface WorkflowEdge {
  /** Unique edge identifier */
  id: string;
  /** Source node ID */
  source: string;
  /** Target node ID */
  target: string;
  /** Source handle ID */
  sourceHandle?: string | null;
  /** Target handle ID */
  targetHandle?: string | null;
  /** Edge type */
  type?: string | null;
  /** Edge data */
  data?: WorkflowEdgeData | null;
}
