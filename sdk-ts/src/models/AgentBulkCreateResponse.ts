/**
 * Generated from OpenAPI schema: AgentBulkCreateResponse
 */
import { AgentResponse } from './AgentResponse';


export interface AgentBulkCreateResponse {
  /** Successfully created agents */
  created: AgentResponse[];
  /** Failed agent creations with errors */
  failed: Record<string, unknown>[];
  /** Total agents requested */
  total_requested: number;
  /** Total agents successfully created */
  total_created: number;
}
