/**
 * Generated from OpenAPI schema: ModelConfig
 */
export interface ModelConfig {
  /** LLM provider */
  provider?: string | null;
  /** Model name */
  model?: string | null;
  /** Temperature */
  temperature?: number;
  /** Max tokens */
  max_tokens?: number;
  /** Top-p sampling */
  top_p?: number;
  /** Presence penalty */
  presence_penalty?: number;
  /** Frequency penalty */
  frequency_penalty?: number;
}
