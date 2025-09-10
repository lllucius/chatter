/**
 * Generated from OpenAPI schema: AgentUpdateRequest
 */
import { AgentCapability } from './AgentCapability';
import { AgentStatus } from './AgentStatus';

export interface AgentUpdateRequest {
  /** Agent name */
  name?: string | null;
  /** Agent description */
  description?: string | null;
  /** System prompt for the agent */
  system_prompt?: string | null;
  /** Agent status */
  status?: AgentStatus | null;
  /** Agent personality traits */
  personality_traits?: string[] | null;
  /** Knowledge domains */
  knowledge_domains?: string[] | null;
  /** Response style */
  response_style?: string | null;
  /** Agent capabilities */
  capabilities?: AgentCapability[] | null;
  /** Available tools */
  available_tools?: string[] | null;
  /** Primary LLM provider */
  primary_llm?: string | null;
  /** Fallback LLM provider */
  fallback_llm?: string | null;
  /** Temperature for responses */
  temperature?: number | null;
  /** Maximum tokens */
  max_tokens?: number | null;
  /** Maximum conversation length */
  max_conversation_length?: number | null;
  /** Context window size */
  context_window_size?: number | null;
  /** Response timeout in seconds */
  response_timeout?: number | null;
  /** Enable learning from feedback */
  learning_enabled?: boolean | null;
  /** Weight for feedback learning */
  feedback_weight?: number | null;
  /** Adaptation threshold */
  adaptation_threshold?: number | null;
  /** Agent tags */
  tags?: string[] | null;
  /** Additional metadata */
  metadata?: Record<string, unknown> | null;
}
