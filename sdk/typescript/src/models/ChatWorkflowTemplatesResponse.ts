/**
 * Generated from OpenAPI schema: ChatWorkflowTemplatesResponse
 */
import { ChatWorkflowTemplate } from './ChatWorkflowTemplate';

export interface ChatWorkflowTemplatesResponse {
  /** Available templates */
  templates: Record<string, ChatWorkflowTemplate>;
  /** Total template count */
  total_count: number;
}
