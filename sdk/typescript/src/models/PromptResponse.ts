/**
 * Generated from OpenAPI schema: PromptResponse
 */
import { PromptCategory } from './PromptCategory';
import { PromptType } from './PromptType';

export interface PromptResponse {
  /** Prompt ID */
  id: string;
  /** Owner user ID */
  owner_id: string;
  /** Prompt name */
  name: string;
  /** Prompt description */
  description?: string | null;
  /** Prompt type */
  prompt_type: PromptType;
  /** Prompt category */
  category: PromptCategory;
  /** Prompt content/template */
  content: string;
  /** Template variables */
  variables?: string[] | null;
  /** Template format */
  template_format: string;
  /** Input validation schema */
  input_schema?: Record<string, unknown> | null;
  /** Output validation schema */
  output_schema?: Record<string, unknown> | null;
  /** Maximum content length */
  max_length?: number | null;
  /** Minimum content length */
  min_length?: number | null;
  /** Required template variables */
  required_variables?: string[] | null;
  /** Usage examples */
  examples?: Record<string, unknown>[] | null;
  /** Test cases */
  test_cases?: Record<string, unknown>[] | null;
  /** Suggested temperature */
  suggested_temperature?: number | null;
  /** Suggested max tokens */
  suggested_max_tokens?: number | null;
  /** Suggested LLM providers */
  suggested_providers?: string[] | null;
  /** Whether this is a chain prompt */
  is_chain: boolean;
  /** Chain execution steps */
  chain_steps?: Record<string, unknown>[] | null;
  /** Parent prompt ID */
  parent_prompt_id?: string | null;
  /** Prompt version */
  version: number;
  /** Whether this is the latest version */
  is_latest: boolean;
  /** Version changelog */
  changelog?: string | null;
  /** Whether prompt is public */
  is_public: boolean;
  /** Average rating */
  rating?: number | null;
  /** Number of ratings */
  rating_count: number;
  /** Usage count */
  usage_count: number;
  /** Success rate */
  success_rate?: number | null;
  /** Average response time */
  avg_response_time_ms?: number | null;
  /** Last used timestamp */
  last_used_at?: string | null;
  /** Total tokens used */
  total_tokens_used: number;
  /** Total cost */
  total_cost: number;
  /** Average tokens per use */
  avg_tokens_per_use?: number | null;
  /** Prompt tags */
  tags?: string[] | null;
  /** Additional metadata */
  extra_metadata?: Record<string, unknown> | null;
  /** Content hash */
  content_hash: string;
  /** Estimated token count */
  estimated_tokens?: number | null;
  /** Content language */
  language?: string | null;
  /** Creation timestamp */
  created_at: string;
  /** Last update timestamp */
  updated_at: string;
}
