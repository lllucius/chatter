/**
 * Generated from OpenAPI schema: ToolConfig
 */
export interface ToolConfig {
  /** Enable tools */
  enabled?: boolean;
  /** Allowed tool names */
  allowed_tools?: string[] | null;
  /** Max tool calls */
  max_tool_calls?: number;
  /** Enable parallel tool calls */
  parallel_tool_calls?: boolean;
  /** Tool timeout in ms */
  tool_timeout_ms?: number;
}
