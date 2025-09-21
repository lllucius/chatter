/**
 * Generated from OpenAPI schema: WorkflowDefinitionFromTemplateRequest
 */
export interface WorkflowDefinitionFromTemplateRequest {
  /** Template ID to instantiate */
  template_id: string;
  /** Optional suffix for the definition name */
  name_suffix?: string | null;
  /** User input to merge with template default params */
  user_input?: Record<string, unknown> | null;
  /** Whether this is a temporary definition for execution */
  is_temporary?: boolean;
}
