/**
 * Generated from OpenAPI schema: ProviderCreate
 */
import { ProviderType } from './ProviderType';


export interface ProviderCreate {
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
}
