/**
 * Generated from OpenAPI schema: PromptCreate
 */
import { PromptCategory } from './PromptCategory';
import { PromptType } from './PromptType';

export interface PromptCreate {
  /** Prompt name */
  name: string;
  /** Prompt description */
  description?: string | null;
  /** Prompt type */
  prompt_type?: PromptType;
  /** Prompt category */
  category?: PromptCategory;
  /** Prompt content/template */
  content: string;
  /** Template variables */
  variables?: string[] | null;
  /** Template format (f-string, jinja2, mustache) */
  template_format?: string;
  /** JSON schema for input validation */
  input_schema?: Record<string, unknown> | null;
  /** JSON schema for output validation */
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
  is_chain?: boolean;
  /** Chain execution steps */
  chain_steps?: Record<string, unknown>[] | null;
  /** Parent prompt ID for chains */
  parent_prompt_id?: string | null;
  /** Whether prompt is public */
  is_public?: boolean;
  /** Prompt tags */
  tags?: string[] | null;
  /** Additional metadata */
  extra_metadata?: Record<string, unknown> | null;
}
