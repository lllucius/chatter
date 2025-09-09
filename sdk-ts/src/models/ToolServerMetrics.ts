/**
 * Generated from OpenAPI schema: ToolServerMetrics
 */
import { ServerStatus } from './ServerStatus';


export interface ToolServerMetrics {
  /** Server ID */
  server_id: string;
  /** Server name */
  server_name: string;
  /** Server status */
  status: ServerStatus;
  /** Total number of tools */
  total_tools: number;
  /** Number of enabled tools */
  enabled_tools: number;
  /** Total tool calls */
  total_calls: number;
  /** Total errors */
  total_errors: number;
  /** Success rate */
  success_rate: number;
  /** Average response time */
  avg_response_time_ms?: number | null;
  /** Last activity timestamp */
  last_activity?: string | null;
  /** Uptime percentage */
  uptime_percentage?: number | null;
}
