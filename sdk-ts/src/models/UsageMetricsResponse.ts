/**
 * Generated from OpenAPI schema: UsageMetricsResponse
 */

export interface UsageMetricsResponse {
  /** Total prompt tokens */
  total_prompt_tokens: number;
  /** Total completion tokens */
  total_completion_tokens: number;
  /** Total tokens used */
  total_tokens: number;
  /** Token usage by model */
  tokens_by_model: Record<string, number>;
  /** Token usage by provider */
  tokens_by_provider: Record<string, number>;
  /** Total cost */
  total_cost: number;
  /** Cost by model */
  cost_by_model: Record<string, number>;
  /** Cost by provider */
  cost_by_provider: Record<string, number>;
  /** Daily token usage */
  daily_usage: Record<string, number>;
  /** Daily cost */
  daily_cost: Record<string, number>;
  /** Average response time */
  avg_response_time: number;
  /** Response times by model */
  response_times_by_model: Record<string, number>;
  /** Number of active days */
  active_days: number;
  /** Peak usage hour */
  peak_usage_hour: number;
  /** Average conversations per day */
  conversations_per_day: number;
}
