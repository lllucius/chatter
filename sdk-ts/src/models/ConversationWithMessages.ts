/**
 * Generated from OpenAPI schema: ConversationWithMessages
 */
import { ConversationStatus } from './ConversationStatus';
import { MessageResponse } from './MessageResponse';


export interface ConversationWithMessages {
  /** Conversation title */
  title: string;
  /** Conversation description */
  description?: string | null;
  /** Conversation ID */
  id: string;
  /** User ID */
  user_id: string;
  /** Profile ID */
  profile_id?: string | null;
  /** Conversation status */
  status: ConversationStatus;
  /** LLM provider */
  llm_provider?: string | null;
  /** LLM model */
  llm_model?: string | null;
  /** Temperature setting */
  temperature?: number | null;
  /** Max tokens setting */
  max_tokens?: number | null;
  /** Retrieval enabled */
  enable_retrieval: boolean;
  /** Number of messages */
  message_count: number;
  /** Total tokens used */
  total_tokens: number;
  /** Total cost */
  total_cost: number;
  /** System prompt */
  system_prompt?: string | null;
  /** Context window size */
  context_window: number;
  /** Memory enabled */
  memory_enabled: boolean;
  /** Memory strategy */
  memory_strategy?: string | null;
  /** Retrieval limit */
  retrieval_limit: number;
  /** Retrieval score threshold */
  retrieval_score_threshold: number;
  /** Conversation tags */
  tags?: string[] | null;
  /** Extra metadata */
  extra_metadata?: Record<string, unknown> | null;
  /** Workflow configuration */
  workflow_config?: Record<string, unknown> | null;
  /** Creation timestamp */
  created_at: string;
  /** Last update timestamp */
  updated_at: string;
  /** Last message timestamp */
  last_message_at?: string | null;
  /** Conversation messages */
  messages?: MessageResponse[];
}
