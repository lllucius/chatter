/**
 * Generated from OpenAPI schema: ChatResponse
 */
import { ConversationResponse } from './ConversationResponse';
import { MessageResponse } from './MessageResponse';

export interface ChatResponse {
  /** Conversation ID */
  conversation_id: string;
  /** Assistant response message */
  message: MessageResponse;
  /** Updated conversation */
  conversation: ConversationResponse;
}
