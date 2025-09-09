/**
 * Generated from OpenAPI schema: ToolServerResponse
 */

export interface ToolServerResponse {
  /** Server name */
  name: string;
  /** Display name */
  display_name: string;
  /** Server description */
  description?: string | null;
  /** Base URL for the remote server (null for built-in servers) */
  base_url?: string | null;
  /** Transport type: http, sse, stdio, or websocket */
  transport_type?: string;
  /** OAuth configuration if required */
  oauth_config?: OAuthConfigSchema | null;
  /** Additional HTTP headers */
  headers?: Record<string, string> | null;
  /** Request timeout in seconds */
  timeout?: number;
  /** Auto-connect to server on system startup */
  auto_start?: boolean;
  /** Auto-update server capabilities */
  auto_update?: boolean;
  /** Maximum consecutive failures before disabling */
  max_failures?: number;
  /** Server ID */
  id: string;
  /** Server status */
  status: ServerStatus;
  /** Whether server is built-in */
  is_builtin: boolean;
  /** Last health check */
  last_health_check?: string | null;
  /** Last successful startup */
  last_startup_success?: string | null;
  /** Last startup error */
  last_startup_error?: string | null;
  /** Consecutive failure count */
  consecutive_failures: number;
  /** Creation timestamp */
  created_at: string;
  /** Last update timestamp */
  updated_at: string;
  /** Creator user ID */
  created_by?: string | null;
  /** Server tools */
  tools?: ServerToolResponse[];
}
