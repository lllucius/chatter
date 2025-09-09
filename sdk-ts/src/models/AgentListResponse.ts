/**
 * Generated from OpenAPI schema: AgentListResponse
 */
import { AgentResponse } from './AgentResponse';


export interface AgentListResponse {
  /** List of agents */
  agents: AgentResponse[];
  /** Total number of agents */
  total: number;
  /** Current page number */
  page: number;
  /** Number of items per page */
  per_page: number;
  /** Total number of pages */
  total_pages: number;
}
