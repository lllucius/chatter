/**
 * Generated from OpenAPI schema: McpStatusResponse
 */
export interface McpStatusResponse {
  /** MCP service status */
  status: string;
  /** Connected servers */
  servers: Record<string, unknown>[];
  /** Last health check time */
  last_check?: string | null;
  /** Any error messages */
  errors?: string[];
}
