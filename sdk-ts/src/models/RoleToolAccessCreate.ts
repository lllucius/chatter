/**
 * Generated from OpenAPI schema: RoleToolAccessCreate
 */

export interface RoleToolAccessCreate {
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
}
