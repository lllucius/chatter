/**
 * Generated from OpenAPI schema: AgentBulkCreateRequest
 */
import { AgentCreateRequest } from './AgentCreateRequest';


export interface AgentBulkCreateRequest {
  /** List of agents to create (max 10) */
  agents: AgentCreateRequest[];
}
