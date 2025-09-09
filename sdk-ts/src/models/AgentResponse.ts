/**
 * Generated from OpenAPI schema: AgentResponse
 */

export interface AgentResponse {
  /** Agent ID */
  id: string;
  /** Agent name */
  name: string;
  /** Agent description */
  description: string;
  /** Type of agent */
  type: AgentType;
  /** Agent status */
  status: AgentStatus;
  /** System message */
  system_message: string;
  /** Agent personality traits */
  personality_traits: string[];
  /** Knowledge domains */
  knowledge_domains: string[];
  /** Response style */
  response_style: string;
  /** Agent capabilities */
  capabilities: AgentCapability[];
  /** Available tools */
  available_tools: string[];
  /** Primary LLM provider */
  primary_llm: string;
  /** Fallback LLM provider */
  fallback_llm: string;
  /** Temperature for responses */
  temperature: number;
  /** Maximum tokens */
  max_tokens: number;
  /** Maximum conversation length */
  max_conversation_length: number;
  /** Context window size */
  context_window_size: number;
  /** Response timeout in seconds */
  response_timeout: number;
  /** Learning enabled */
  learning_enabled: boolean;
  /** Feedback weight */
  feedback_weight: number;
  /** Adaptation threshold */
  adaptation_threshold: number;
  /** Creation timestamp */
  created_at: string;
  /** Last update timestamp */
  updated_at: string;
  /** Creator */
  created_by: string;
  /** Agent tags */
  tags: string[];
  /** Additional metadata */
  metadata: Record<string, unknown>;
}
