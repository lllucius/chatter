/**
 * Generated from OpenAPI schema: ConversationCreate
 */
export interface ConversationCreate {
  /** Conversation title */
  title: string;
  /** Conversation description */
  description?: string | null;
  /** Profile ID to use */
  profile_id?: string | null;
  /** System prompt */
  system_prompt?: string | null;
  /** Enable document retrieval */
  enable_retrieval?: boolean;
  /** Temperature setting */
  temperature?: number | null;
  /** Max tokens setting */
  max_tokens?: number | null;
  /** Workflow configuration */
  workflow_config?: Record<string, unknown> | null;
  /** Additional metadata */
  extra_metadata?: Record<string, unknown> | null;
}
