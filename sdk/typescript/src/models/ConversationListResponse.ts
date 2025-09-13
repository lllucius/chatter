/**
 * Generated from OpenAPI schema: ConversationListResponse
 */
import { ConversationResponse } from './ConversationResponse';

export interface ConversationListResponse {
  /** List of conversations */
  conversations: ConversationResponse[];
  /** Total number of conversations */
  total_count: number;
  /** Applied limit */
  limit: number;
  /** Applied offset */
  offset: number;
}
