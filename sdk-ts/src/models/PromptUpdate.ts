/**
 * Generated from OpenAPI schema: PromptUpdate
 */

export interface PromptUpdate {
  /** Prompt name */
  name?: string | null;
  /** Prompt description */
  description?: string | null;
  /** Prompt type */
  prompt_type?: PromptType | null;
  /** Prompt category */
  category?: PromptCategory | null;
  /** Prompt content/template */
  content?: string | null;
  /** Template variables */
  variables?: string[] | null;
  /** Template format */
  template_format?: string | null;
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
  is_chain?: boolean | null;
  /** Chain execution steps */
  chain_steps?: Record<string, unknown>[] | null;
  /** Parent prompt ID */
  parent_prompt_id?: string | null;
  /** Whether prompt is public */
  is_public?: boolean | null;
  /** Prompt tags */
  tags?: string[] | null;
  /** Additional metadata */
  extra_metadata?: Record<string, unknown> | null;
}
