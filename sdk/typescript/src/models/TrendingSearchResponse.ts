/**
 * Generated from OpenAPI schema: TrendingSearchResponse
 */
export interface TrendingSearchResponse {
  /** Trending search queries */
  trending_queries: string[];
  /** Search volume by query */
  search_volume: Record<string, number>;
  /** Time period for trending data */
  time_period: string;
  /** Search categories */
  categories: Record<string, number>;
}
