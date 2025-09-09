/**
 * Generated from OpenAPI schema: ToolServerUpdate
 */

export interface ToolServerUpdate {
  display_name?: string | null;
  description?: string | null;
  base_url?: string | null;
  transport_type?: string | null;
  oauth_config?: OAuthConfigSchema | null;
  headers?: Record<string, string> | null;
  timeout?: number | null;
  auto_start?: boolean | null;
  auto_update?: boolean | null;
  max_failures?: number | null;
}
