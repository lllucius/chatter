/**
 * Generated from OpenAPI schema: chatter__schemas__chat__WorkflowTemplatesResponse
 */

export interface chatter__schemas__chat__WorkflowTemplatesResponse {
  /** Available templates */
  templates: Record<string, WorkflowTemplateInfo>;
  /** Total number of templates */
  total_count: number;
}
