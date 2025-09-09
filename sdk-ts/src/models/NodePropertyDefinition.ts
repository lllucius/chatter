/**
 * Generated from OpenAPI schema: NodePropertyDefinition
 */
export interface NodePropertyDefinition {
  /** Property name */
  name: string;
  /** Property type */
  type: string;
  /** Whether property is required */
  required?: boolean;
  /** Property description */
  description?: string | null;
  /** Default value */
  default_value?: Record<string, unknown> | null;
  /** Valid options for select type */
  options?: string[] | null;
  /** Minimum value for numeric types */
  min_value?: number | number | null;
  /** Maximum value for numeric types */
  max_value?: number | number | null;
}
