/**
 * Generated from OpenAPI schema: ProfileUpdate
 */
import { ProfileType } from './ProfileType';


export interface ProfileUpdate {
  /** Profile name */
  name?: string | null;
  /** Profile description */
  description?: string | null;
  /** Profile type */
  profile_type?: ProfileType | null;
  /** LLM provider */
  llm_provider?: string | null;
  /** LLM model name */
  llm_model?: string | null;
  /** Temperature */
  temperature?: number | null;
  /** Top-p parameter */
  top_p?: number | null;
  /** Top-k parameter */
  top_k?: number | null;
  /** Maximum tokens */
  max_tokens?: number | null;
  /** Presence penalty */
  presence_penalty?: number | null;
  /** Frequency penalty */
  frequency_penalty?: number | null;
  /** Context window size */
  context_window?: number | null;
  /** System prompt template */
  system_prompt?: string | null;
  /** Enable conversation memory */
  memory_enabled?: boolean | null;
  /** Memory management strategy */
  memory_strategy?: string | null;
  /** Enable document retrieval */
  enable_retrieval?: boolean | null;
  /** Number of documents to retrieve */
  retrieval_limit?: number | null;
  /** Minimum retrieval score */
  retrieval_score_threshold?: number | null;
  /** Enable tool calling */
  enable_tools?: boolean | null;
  /** List of available tools */
  available_tools?: string[] | null;
  /** Tool choice strategy */
  tool_choice?: string | null;
  /** Enable content filtering */
  content_filter_enabled?: boolean | null;
  /** Safety level */
  safety_level?: string | null;
  /** Response format */
  response_format?: string | null;
  /** Enable streaming responses */
  stream_response?: boolean | null;
  /** Random seed */
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
  is_public?: boolean | null;
  /** Profile tags */
  tags?: string[] | null;
  /** Additional metadata */
  extra_metadata?: Record<string, unknown> | null;
}
