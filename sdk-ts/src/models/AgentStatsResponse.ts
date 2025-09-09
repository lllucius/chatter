/**
 * Generated from OpenAPI schema: AgentStatsResponse
 */

export interface AgentStatsResponse {
  /** Total number of agents */
  total_agents: number;
  /** Number of active agents */
  active_agents: number;
  /** Agents by type */
  agent_types: Record<string, number>;
  /** Total interactions across all agents */
  total_interactions: number;
}
