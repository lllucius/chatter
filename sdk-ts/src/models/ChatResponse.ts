/**
 * Generated from OpenAPI schema: ChatResponse
 */

export interface ChatResponse {
  /** Conversation ID */
  conversation_id: string;
  /** Assistant response message */
  message: MessageResponse;
  /** Updated conversation */
  conversation: ConversationResponse;
}
