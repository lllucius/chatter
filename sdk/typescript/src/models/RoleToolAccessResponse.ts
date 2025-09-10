/**
 * Generated from OpenAPI schema: RoleToolAccessResponse
 */
import { ToolAccessLevel } from './ToolAccessLevel';
import { UserRole } from './UserRole';

export interface RoleToolAccessResponse {
  /** User role */
  role: UserRole;
  /** Tool name pattern */
  tool_pattern?: string | null;
  /** Server name pattern */
  server_pattern?: string | null;
  /** Access level */
  access_level: ToolAccessLevel;
  default_rate_limit_per_hour?: number | null;
  default_rate_limit_per_day?: number | null;
  allowed_hours?: number[] | null;
  allowed_days?: number[] | null;
  /** Access rule ID */
  id: string;
  /** Creator user ID */
  created_by: string;
  /** Creation timestamp */
  created_at: string;
}
