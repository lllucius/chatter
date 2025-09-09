/**
 * Generated from OpenAPI schema: WorkflowTemplateUpdate
 */
export interface WorkflowTemplateUpdate {
  /** Template name */
  name?: string | null;
  /** Template description */
  description?: string | null;
  /** Template category */
  category?: string | null;
  /** Default parameters */
  default_params?: Record<string, unknown> | null;
  /** Required tools */
  required_tools?: string[] | null;
  /** Required retrievers */
  required_retrievers?: string[] | null;
  /** Template tags */
  tags?: string[] | null;
  /** Whether template is public */
  is_public?: boolean | null;
}
