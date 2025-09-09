/**
 * Generated from OpenAPI schema: WorkflowTemplateCreate
 */
export interface WorkflowTemplateCreate {
  /** Template name */
  name: string;
  /** Template description */
  description: string;
  /** Workflow type */
  workflow_type: string;
  /** Template category */
  category?: string;
  /** Default parameters */
  default_params?: Record<string, unknown>;
  /** Required tools */
  required_tools?: string[] | null;
  /** Required retrievers */
  required_retrievers?: string[] | null;
  /** Template tags */
  tags?: string[] | null;
  /** Whether template is public */
  is_public?: boolean;
  /** Source workflow definition ID */
  workflow_definition_id?: string | null;
  /** Base template ID for derivation */
  base_template_id?: string | null;
}
