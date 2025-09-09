/**
 * Generated from OpenAPI schema: ModelDefUpdate
 */

export interface ModelDefUpdate {
  display_name?: string | null;
  description?: string | null;
  model_name?: string | null;
  max_tokens?: number | null;
  context_length?: number | null;
  dimensions?: number | null;
  chunk_size?: number | null;
  supports_batch?: boolean | null;
  max_batch_size?: number | null;
  default_config?: Record<string, unknown> | null;
  is_active?: boolean | null;
  is_default?: boolean | null;
}
