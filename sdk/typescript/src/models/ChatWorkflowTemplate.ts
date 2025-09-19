/**
 * Generated from OpenAPI schema: ChatWorkflowTemplate
 */
import { ChatWorkflowConfig } from './ChatWorkflowConfig';

export interface ChatWorkflowTemplate {
  /** Template name */
  name: string;
  /** Template description */
  description: string;
  /** Workflow configuration */
  config: ChatWorkflowConfig;
  /** Estimated token usage */
  estimated_tokens?: number | null;
  /** Estimated cost */
  estimated_cost?: number | null;
  /** Complexity score */
  complexity_score?: number;
  /** Use cases */
  use_cases?: string[];
}
