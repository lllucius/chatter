/**
 * Generated from OpenAPI schema: WorkflowTemplateInfo
 */
export interface WorkflowTemplateInfo {
  /** Template name */
  name: string;
  /** Workflow type */
  workflow_type: string;
  /** Template description */
  description: string;
  /** Required tools */
  required_tools: string[];
  /** Required retrievers */
  required_retrievers: string[];
  /** Default parameters */
  default_params: Record<string, unknown>;
}
