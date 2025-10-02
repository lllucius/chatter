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
  /** Dynamic workflow configuration */
  workflow_config?: Record<string, unknown> | null;
  /** Existing workflow definition ID */
  workflow_definition_id?: string | null;
  /** Workflow template name */
  workflow_template_name?: string | null;
  /** Enable retrieval capabilities */
  enable_retrieval?: boolean;
  /** Enable tool calling capabilities */
  enable_tools?: boolean;
  /** Enable memory capabilities */
  enable_memory?: boolean;
  /** Enable web search capabilities */
  enable_web_search?: boolean;
  /** Override LLM provider for this request */
  provider?: string | null;
  /** Override LLM model for this request */
  model?: string | null;
  /** Temperature override */
  temperature?: number | null;
  /** Max tokens override */
  max_tokens?: number | null;
  /** Context limit override */
  context_limit?: number | null;
  /** Document IDs to include in context */
  document_ids?: string[] | null;
  /** Prompt template ID to use for this request */
  prompt_id?: string | null;
  /** Override system prompt for this request */
  system_prompt_override?: string | null;
  /** Enable backend workflow tracing */
  enable_tracing?: boolean;
}
