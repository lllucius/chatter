/**
 * Generated from OpenAPI schema: ProviderUpdate
 */

export interface ProviderUpdate {
  display_name?: string | null;
  description?: string | null;
  api_key_required?: boolean | null;
  base_url?: string | null;
  default_config?: Record<string, unknown> | null;
  is_active?: boolean | null;
  is_default?: boolean | null;
}
