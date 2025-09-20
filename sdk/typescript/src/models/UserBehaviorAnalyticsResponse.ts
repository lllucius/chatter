/**
 * Generated from OpenAPI schema: UserBehaviorAnalyticsResponse
 */
export interface UserBehaviorAnalyticsResponse {
  /** User ID */
  user_id: string;
  /** Number of sessions */
  session_count: number;
  /** Total page views */
  page_views: number;
  /** Total time spent in minutes */
  time_spent_minutes: number;
  /** Most visited pages */
  most_visited_pages: string[];
  /** User journey data */
  user_journey: Record<string, unknown>[];
  /** Conversion events */
  conversion_events: Record<string, unknown>[];
}
