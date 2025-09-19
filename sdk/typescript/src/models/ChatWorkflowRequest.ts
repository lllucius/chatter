/**
 * Generated from OpenAPI schema: ChatWorkflowRequest
 */
import { ChatWorkflowConfig } from './ChatWorkflowConfig';

export interface ChatWorkflowRequest {
  /** User message */
  message: string;
  /** Conversation ID */
  conversation_id?: string | null;
  /** Dynamic workflow config */
  workflow_config?: ChatWorkflowConfig | null;
  /** Existing workflow definition ID */
  workflow_definition_id?: string | null;
  /** Template name */
  workflow_template_name?: string | null;
  /** Profile ID */
  profile_id?: string | null;
  /** LLM provider */
  provider?: string | null;
  /** Temperature */
  temperature?: number | null;
  /** Max tokens */
  max_tokens?: number | null;
  /** Context limit */
  context_limit?: number | null;
  /** Document IDs */
  document_ids?: string[] | null;
  /** System prompt override */
  system_prompt_override?: string | null;
}
