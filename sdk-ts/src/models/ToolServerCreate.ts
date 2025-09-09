/**
 * Generated from OpenAPI schema: ToolServerCreate
 */
import { OAuthConfigSchema } from './OAuthConfigSchema';


export interface ToolServerCreate {
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
}
