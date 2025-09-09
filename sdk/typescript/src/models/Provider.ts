/**
 * Generated from OpenAPI schema: Provider
 */
import { ProviderType } from './ProviderType';

export interface Provider {
  /** Unique provider name */
  name: string;
  /** Type of provider */
  provider_type: ProviderType;
  /** Human-readable name */
  display_name: string;
  /** Provider description */
  description?: string | null;
  /** Whether API key is required */
  api_key_required?: boolean;
  /** Base URL for API */
  base_url?: string | null;
  /** Default configuration */
  default_config?: Record<string, unknown>;
  /** Whether provider is active */
  is_active?: boolean;
  /** Whether this is the default provider */
  is_default?: boolean;
  id: string;
  created_at: string;
  updated_at: string;
}
