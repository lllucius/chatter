/**
 * Generated from OpenAPI schema: PromptListResponse
 */
import { PromptResponse } from './PromptResponse';


export interface PromptListResponse {
  /** List of prompts */
  prompts: PromptResponse[];
  /** Total number of prompts */
  total_count: number;
  /** Requested limit */
  limit: number;
  /** Requested offset */
  offset: number;
}
