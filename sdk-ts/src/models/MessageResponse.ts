/**
 * Generated from OpenAPI schema: MessageResponse
 */
import { MessageRole } from './MessageRole';


export interface MessageResponse {
  /** Message role */
  role: MessageRole;
  /** Message content */
  content: string;
  /** Message ID */
  id: string;
  /** Conversation ID */
  conversation_id: string;
  /** Message sequence number */
  sequence_number: number;
  /** Prompt tokens used */
  prompt_tokens?: number | null;
  /** Completion tokens used */
  completion_tokens?: number | null;
  /** Total tokens used */
  total_tokens?: number | null;
  /** Model used for generation */
  model_used?: string | null;
  /** Provider used */
  provider_used?: string | null;
  /** Response time in milliseconds */
  response_time_ms?: number | null;
  /** Cost of the message */
  cost?: number | null;
  /** Reason for completion */
  finish_reason?: string | null;
  /** Creation timestamp */
  created_at: string;
}
