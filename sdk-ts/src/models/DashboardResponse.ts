/**
 * Generated from OpenAPI schema: DashboardResponse
 */

export interface DashboardResponse {
  /** Conversation statistics */
  conversation_stats: ConversationStatsResponse;
  /** Usage metrics */
  usage_metrics: UsageMetricsResponse;
  /** Performance metrics */
  performance_metrics: PerformanceMetricsResponse;
  /** Document analytics */
  document_analytics: DocumentAnalyticsResponse;
  /** System health metrics */
  system_health: SystemAnalyticsResponse;
  /** Custom metrics */
  custom_metrics: Record<string, unknown>[];
  /** Dashboard generation time */
  generated_at: string;
}
