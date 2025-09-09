/**
 * Generated from OpenAPI schema: AgentInteractRequest
 */
export interface AgentInteractRequest {
  /** Message to send to the agent */
  message: string;
  /** Conversation ID */
  conversation_id: string;
  /** Additional context */
  context?: Record<string, unknown> | null;
}
