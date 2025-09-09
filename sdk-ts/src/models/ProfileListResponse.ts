/**
 * Generated from OpenAPI schema: ProfileListResponse
 */

export interface ProfileListResponse {
  /** List of profiles */
  profiles: ProfileResponse[];
  /** Total number of profiles */
  total_count: number;
  /** Applied limit */
  limit: number;
  /** Applied offset */
  offset: number;
}
