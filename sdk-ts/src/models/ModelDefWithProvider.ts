/**
 * Generated from OpenAPI schema: ModelDefWithProvider
 */

export interface ModelDefWithProvider {
  /** Model name */
  name: string;
  /** Type of model */
  model_type: ModelType;
  /** Human-readable name */
  display_name: string;
  /** Model description */
  description?: string | null;
  /** Actual model name for API calls */
  model_name: string;
  /** Maximum tokens */
  max_tokens?: number | null;
  /** Context length */
  context_length?: number | null;
  /** Embedding dimensions */
  dimensions?: number | null;
  /** Default chunk size */
  chunk_size?: number | null;
  /** Whether model supports batch operations */
  supports_batch?: boolean;
  /** Maximum batch size */
  max_batch_size?: number | null;
  /** Default configuration */
  default_config?: Record<string, unknown>;
  /** Whether model is active */
  is_active?: boolean;
  /** Whether this is the default model */
  is_default?: boolean;
  id: string;
  provider_id: string;
  created_at: string;
  updated_at: string;
  provider: Provider;
}
