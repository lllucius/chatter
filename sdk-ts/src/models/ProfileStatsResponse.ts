/**
 * Generated from OpenAPI schema: ProfileStatsResponse
 */

export interface ProfileStatsResponse {
  /** Total number of profiles */
  total_profiles: number;
  /** Profiles grouped by type */
  profiles_by_type: Record<string, number>;
  /** Profiles grouped by LLM provider */
  profiles_by_provider: Record<string, number>;
  /** Most frequently used profiles */
  most_used_profiles: ProfileResponse[];
  /** Recently created profiles */
  recent_profiles: ProfileResponse[];
  /** Usage statistics */
  usage_stats: Record<string, unknown>;
}
