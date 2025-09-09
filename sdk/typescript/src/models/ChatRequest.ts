/**
 * Generated from OpenAPI schema: ChatRequest
 */
export interface ChatRequest {
  /** User message */
  message: string;
  /** Conversation ID for continuing chat */
  conversation_id?: string | null;
  /** Profile ID to use */
  profile_id?: string | null;
  /** Enable streaming response */
  stream?: boolean;
  /** Workflow type: plain, rag, tools, or full (rag + tools) */
  workflow?: "plain" | "rag" | "tools" | "full";
  /** Override LLM provider for this request */
  provider?: string | null;
  /** Temperature override */
  temperature?: number | null;
  /** Max tokens override */
  max_tokens?: number | null;
  /** Context limit override */
  context_limit?: number | null;
  /** Enable retrieval override */
  enable_retrieval?: boolean | null;
  /** Document IDs to include in context */
  document_ids?: string[] | null;
  /** Override system prompt for this request */
  system_prompt_override?: string | null;
  /** Workflow configuration */
  workflow_config?: Record<string, unknown> | null;
  /** Internal workflow type (set by API processing) */
  workflow_type?: string | null;
}
