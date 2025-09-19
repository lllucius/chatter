/**
 * Generated from OpenAPI schema: ChatWorkflowConfig
 */
import { ModelConfig } from './ModelConfig';
import { RetrievalConfig } from './RetrievalConfig';
import { ToolConfig } from './ToolConfig';

export interface ChatWorkflowConfig {
  /** Enable document retrieval */
  enable_retrieval?: boolean;
  /** Enable function calling */
  enable_tools?: boolean;
  /** Enable conversation memory */
  enable_memory?: boolean;
  /** Enable web search */
  enable_web_search?: boolean;
  /** Model configuration */
  llm_config?: ModelConfig | null;
  /** Retrieval configuration */
  retrieval_config?: RetrievalConfig | null;
  /** Tool configuration */
  tool_config?: ToolConfig | null;
}
