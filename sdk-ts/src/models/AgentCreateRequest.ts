/**
 * Generated from OpenAPI schema: AgentCreateRequest
 */
import { AgentCapability } from './AgentCapability';
import { AgentType } from './AgentType';

export interface AgentCreateRequest {
  /** Agent name */
  name: string;
  /** Agent description */
  description: string;
  /** Type of agent */
  agent_type: AgentType;
  /** System prompt for the agent */
  system_prompt: string;
  /** Agent personality traits */
  personality_traits?: string[];
  /** Knowledge domains */
  knowledge_domains?: string[];
  /** Response style */
  response_style?: string;
  /** Agent capabilities */
  capabilities?: AgentCapability[];
  /** Available tools */
  available_tools?: string[];
  /** Primary LLM provider */
  primary_llm?: string;
  /** Fallback LLM provider */
  fallback_llm?: string;
  /** Temperature for responses */
  temperature?: number;
  /** Maximum tokens */
  max_tokens?: number;
  /** Maximum conversation length */
  max_conversation_length?: number;
  /** Context window size */
  context_window_size?: number;
  /** Response timeout in seconds */
  response_timeout?: number;
  /** Enable learning from feedback */
  learning_enabled?: boolean;
  /** Weight for feedback learning */
  feedback_weight?: number;
  /** Adaptation threshold */
  adaptation_threshold?: number;
  /** Agent tags */
  tags?: string[];
  /** Additional metadata */
  metadata?: Record<string, unknown>;
}
