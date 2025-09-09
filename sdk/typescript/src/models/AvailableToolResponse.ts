/**
 * Generated from OpenAPI schema: AvailableToolResponse
 */
export interface AvailableToolResponse {
  /** Tool name */
  name: string;
  /** Tool description */
  description: string;
  /** Tool type (mcp, builtin) */
  type: string;
  /** Tool arguments schema */
  args_schema: Record<string, unknown>;
}
