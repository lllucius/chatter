/**
 * Generated from OpenAPI schema: NodeTypeResponse
 */

export interface NodeTypeResponse {
  /** Node type identifier */
  type: string;
  /** Human-readable name */
  name: string;
  /** Node description */
  description: string;
  /** Node category */
  category: string;
  /** Node properties */
  properties: NodePropertyDefinition[];
  /** Icon name */
  icon?: string | null;
  /** Node color */
  color?: string | null;
}
