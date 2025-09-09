/**
 * Generated from OpenAPI schema: ToolPermissionUpdate
 */

export interface ToolPermissionUpdate {
  access_level?: ToolAccessLevel | null;
  rate_limit_per_hour?: number | null;
  rate_limit_per_day?: number | null;
  allowed_hours?: number[] | null;
  allowed_days?: number[] | null;
  expires_at?: string | null;
}
