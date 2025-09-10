/**
 * Generated from OpenAPI schema: ProfileResponse
 */
import { ProfileType } from './ProfileType';

export interface ProfileResponse {
  /** Profile name */
  name: string;
  /** Profile description */
  description?: string | null;
  /** Profile type */
  profile_type?: ProfileType;
  /** LLM provider (openai, anthropic, etc.) */
  llm_provider: string;
  /** LLM model name */
  llm_model: string;
  /** Temperature for generation */
  temperature?: number;
  /** Top-p sampling parameter */
  top_p?: number | null;
  /** Top-k sampling parameter */
  top_k?: number | null;
  /** Maximum tokens to generate */
  max_tokens?: number;
  /** Presence penalty */
  presence_penalty?: number | null;
  /** Frequency penalty */
  frequency_penalty?: number | null;
  /** Context window size */
  context_window?: number;
  /** System prompt template */
  system_prompt?: string | null;
  /** Enable conversation memory */
  memory_enabled?: boolean;
  /** Memory management strategy */
  memory_strategy?: string | null;
  /** Enable document retrieval */
  enable_retrieval?: boolean;
  /** Number of documents to retrieve */
  retrieval_limit?: number;
  /** Minimum retrieval score */
  retrieval_score_threshold?: number;
  /** Enable tool calling */
  enable_tools?: boolean;
  /** List of available tools */
  available_tools?: string[] | null;
  /** Tool choice strategy */
  tool_choice?: string | null;
  /** Enable content filtering */
  content_filter_enabled?: boolean;
  /** Safety level */
  safety_level?: string | null;
  /** Response format (json, text, markdown) */
  response_format?: string | null;
  /** Enable streaming responses */
  stream_response?: boolean;
  /** Random seed for reproducibility */
  seed?: number | null;
  /** Stop sequences */
  stop_sequences?: string[] | null;
  /** Logit bias adjustments */
  logit_bias?: Record<string, number> | null;
  /** Embedding provider */
  embedding_provider?: string | null;
  /** Embedding model */
  embedding_model?: string | null;
  /** Whether profile is public */
  is_public?: boolean;
  /** Profile tags */
  tags?: string[] | null;
  /** Additional metadata */
  extra_metadata?: Record<string, unknown> | null;
  /** Profile ID */
  id: string;
  /** Owner user ID */
  owner_id: string;
  /** Number of times used */
  usage_count: number;
  /** Total tokens used */
  total_tokens_used: number;
  /** Total cost incurred */
  total_cost: number;
  /** Last usage time */
  last_used_at?: string | null;
  /** Creation time */
  created_at: string;
  /** Last update time */
  updated_at: string;
}
