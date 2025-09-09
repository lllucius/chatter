/**
 * Generated from OpenAPI schema: chatter__schemas__chat__WorkflowTemplatesResponse
 */

import { WorkflowTemplateInfo } from './WorkflowTemplateInfo';

export interface chatter__schemas__chat__WorkflowTemplatesResponse {
  /** Available templates */
  templates: Record<string, WorkflowTemplateInfo>;
  /** Total number of templates */
  total_count: number;
}
