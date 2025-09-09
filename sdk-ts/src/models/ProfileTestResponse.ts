/**
 * Generated from OpenAPI schema: ProfileTestResponse
 */

export interface ProfileTestResponse {
  /** Profile ID */
  profile_id: string;
  /** Test message sent */
  test_message: string;
  /** Generated response */
  response: string;
  /** Token usage and cost information */
  usage_info: Record<string, unknown>;
  /** Response time in milliseconds */
  response_time_ms: number;
  /** Retrieval results if enabled */
  retrieval_results?: Record<string, unknown>[] | null;
  /** Tools used if enabled */
  tools_used?: string[] | null;
}
