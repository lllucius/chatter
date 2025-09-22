/**
 * Generated from OpenAPI schema: WorkflowTemplateResponse
 */
export interface WorkflowTemplateResponse {
  /** Template name */
  name: string;
  /** Template description */
  description: string;
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
  /** Unique node identifier */
  id: string;
  /** Owner user ID */
  owner_id: string;
  /** Base template ID */
  base_template_id?: string | null;
  /** Whether template is built-in */
  is_builtin?: boolean;
  /** Template version */
  version?: number;
  /** Whether this is the latest version */
  is_latest?: boolean;
  /** Average rating */
  rating?: number | null;
  /** Number of ratings */
  rating_count?: number;
  /** Usage count */
  usage_count?: number;
  /** Success rate */
  success_rate?: number | null;
  /** Configuration hash */
  config_hash: string;
  /** Estimated complexity score */
  estimated_complexity?: number | null;
}
