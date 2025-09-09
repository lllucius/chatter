/**
 * Generated from OpenAPI schema: ServerToolResponse
 */
import { ToolStatus } from './ToolStatus';


export interface ServerToolResponse {
  /** Tool name */
  name: string;
  /** Display name */
  display_name: string;
  /** Tool description */
  description?: string | null;
  /** Tool arguments schema */
  args_schema?: Record<string, unknown> | null;
  /** Bypass when tool is unavailable */
  bypass_when_unavailable?: boolean;
  /** Tool ID */
  id: string;
  /** Server ID */
  server_id: string;
  /** Tool status */
  status: ToolStatus;
  /** Tool availability */
  is_available: boolean;
  /** Total number of calls */
  total_calls: number;
  /** Total number of errors */
  total_errors: number;
  /** Last call timestamp */
  last_called?: string | null;
  /** Last error message */
  last_error?: string | null;
  /** Average response time */
  avg_response_time_ms?: number | null;
  /** Creation timestamp */
  created_at: string;
  /** Last update timestamp */
  updated_at: string;
}
