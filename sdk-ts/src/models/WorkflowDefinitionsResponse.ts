/**
 * Generated from OpenAPI schema: WorkflowDefinitionsResponse
 */
import { WorkflowDefinitionResponse } from './WorkflowDefinitionResponse';


export interface WorkflowDefinitionsResponse {
  /** Workflow definitions */
  definitions: WorkflowDefinitionResponse[];
  /** Total number of definitions */
  total_count: number;
}
