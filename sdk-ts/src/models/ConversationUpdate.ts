/**
 * Generated from OpenAPI schema: ConversationUpdate
 */
import { ConversationStatus } from './ConversationStatus';


export interface ConversationUpdate {
  /** Conversation title */
  title?: string | null;
  /** Conversation description */
  description?: string | null;
  /** Conversation status */
  status?: ConversationStatus | null;
  /** Temperature setting */
  temperature?: number | null;
  /** Max tokens setting */
  max_tokens?: number | null;
  /** Workflow configuration */
  workflow_config?: Record<string, unknown> | null;
  /** Additional metadata */
  extra_metadata?: Record<string, unknown> | null;
}
