/**
 * Generated from OpenAPI schema: WorkflowTemplatesResponse
 */
import { WorkflowTemplateResponse } from './WorkflowTemplateResponse';

export interface WorkflowTemplatesResponse {
  /** Workflow templates */
  templates: WorkflowTemplateResponse[];
  /** Total number of templates */
  total_count: number;
}
