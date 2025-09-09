/**
 * Generated from OpenAPI schema: ToolServerHealthCheck
 */
import { ServerStatus } from './ServerStatus';

export interface ToolServerHealthCheck {
  /** Server ID */
  server_id: string;
  /** Server name */
  server_name: string;
  /** Server status */
  status: ServerStatus;
  /** Whether server is running */
  is_running: boolean;
  /** Whether server is responsive */
  is_responsive: boolean;
  /** Number of available tools */
  tools_count: number;
  /** Last health check time */
  last_check: string;
  /** Error message if unhealthy */
  error_message?: string | null;
}
