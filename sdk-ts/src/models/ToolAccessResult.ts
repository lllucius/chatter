/**
 * Generated from OpenAPI schema: ToolAccessResult
 */

export interface ToolAccessResult {
  /** Whether access is allowed */
  allowed: boolean;
  /** Access level */
  access_level: ToolAccessLevel;
  /** Remaining hourly calls */
  rate_limit_remaining_hour?: number | null;
  /** Remaining daily calls */
  rate_limit_remaining_day?: number | null;
  /** Reason if restricted */
  restriction_reason?: string | null;
  /** Permission expiry */
  expires_at?: string | null;
}
