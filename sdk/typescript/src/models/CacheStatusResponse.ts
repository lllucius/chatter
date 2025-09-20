/**
 * Generated from OpenAPI schema: CacheStatusResponse
 */
export interface CacheStatusResponse {
  /** Cache enabled status */
  cache_enabled: boolean;
  /** Cache hits */
  cache_hits: number;
  /** Cache misses */
  cache_misses: number;
  /** Cache hit rate */
  cache_hit_rate: number;
  /** Number of cached items */
  cached_items_count: number;
  /** Cache size in MB */
  cache_size_mb: number;
  /** Last cache clear timestamp */
  last_cleared?: string | null;
}
