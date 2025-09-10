/**
 * Generated from OpenAPI schema: AgentHealthResponse
 */
import { AgentStatus } from './AgentStatus';

export interface AgentHealthResponse {
  /** Agent ID */
  agent_id: string;
  /** Agent status */
  status: AgentStatus;
  /** Health status (healthy/unhealthy/unknown) */
  health: string;
  /** Last interaction timestamp */
  last_interaction?: string | null;
  /** Average response time */
  response_time_avg?: number | null;
  /** Error rate percentage */
  error_rate?: number | null;
}
