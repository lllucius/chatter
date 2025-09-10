/**
 * Generated from OpenAPI schema: ConversationSearchResponse
 */
import { ConversationResponse } from './ConversationResponse';

export interface ConversationSearchResponse {
  /** Conversations */
  conversations: ConversationResponse[];
  /** Total number of conversations */
  total: number;
  /** Request limit */
  limit: number;
  /** Request offset */
  offset: number;
}
