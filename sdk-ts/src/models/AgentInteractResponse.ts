/**
 * Generated from OpenAPI schema: AgentInteractResponse
 */

export interface AgentInteractResponse {
  /** Agent ID */
  agent_id: string;
  /** Agent response */
  response: string;
  /** Conversation ID */
  conversation_id: string;
  /** Tools used in response */
  tools_used: string[];
  /** Confidence score */
  confidence_score: number;
  /** Response time in seconds */
  response_time: number;
  /** Response timestamp */
  timestamp: string;
}
