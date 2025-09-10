/**
 * Generated from OpenAPI schema: ConversationStatsResponse
 */
export interface ConversationStatsResponse {
  /** Total number of conversations */
  total_conversations: number;
  /** Conversations grouped by status */
  conversations_by_status: Record<string, number>;
  /** Total number of messages */
  total_messages: number;
  /** Messages grouped by role */
  messages_by_role: Record<string, number>;
  /** Average messages per conversation */
  avg_messages_per_conversation: number;
  /** Total tokens used */
  total_tokens_used: number;
  /** Total cost incurred */
  total_cost: number;
  /** Average response time in milliseconds */
  avg_response_time_ms: number;
  /** Conversations by date */
  conversations_by_date: Record<string, number>;
  /** Most active hours */
  most_active_hours: Record<string, number>;
  /** Popular LLM models */
  popular_models: Record<string, number>;
  /** Popular LLM providers */
  popular_providers: Record<string, number>;
}
