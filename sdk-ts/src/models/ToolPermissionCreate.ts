/**
 * Generated from OpenAPI schema: ToolPermissionCreate
 */
import { ToolAccessLevel } from './ToolAccessLevel';

export interface ToolPermissionCreate {
  /** User ID */
  user_id: string;
  /** Specific tool ID */
  tool_id?: string | null;
  /** Server ID (for all tools) */
  server_id?: string | null;
  /** Access level */
  access_level: ToolAccessLevel;
  /** Hourly rate limit */
  rate_limit_per_hour?: number | null;
  /** Daily rate limit */
  rate_limit_per_day?: number | null;
  /** Allowed hours (0-23) */
  allowed_hours?: number[] | null;
  /** Allowed weekdays (0-6) */
  allowed_days?: number[] | null;
  /** Permission expiry */
  expires_at?: string | null;
}
