/**
 * Generated from OpenAPI schema: PromptStatsResponse
 */
import { PromptResponse } from './PromptResponse';


export interface PromptStatsResponse {
  /** Total number of prompts */
  total_prompts: number;
  /** Prompts by type */
  prompts_by_type: Record<string, number>;
  /** Prompts by category */
  prompts_by_category: Record<string, number>;
  /** Most used prompts */
  most_used_prompts: PromptResponse[];
  /** Recently created prompts */
  recent_prompts: PromptResponse[];
  /** Usage statistics */
  usage_stats: Record<string, unknown>;
}
