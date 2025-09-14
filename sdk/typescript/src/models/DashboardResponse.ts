/**
 * Generated from OpenAPI schema: DashboardResponse
 */
import { ChartReadyAnalytics } from './ChartReadyAnalytics';
import { ConversationStatsResponse } from './ConversationStatsResponse';
import { DocumentAnalyticsResponse } from './DocumentAnalyticsResponse';
import { PerformanceMetricsResponse } from './PerformanceMetricsResponse';
import { SystemAnalyticsResponse } from './SystemAnalyticsResponse';
import { UsageMetricsResponse } from './UsageMetricsResponse';

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
  /** Chart-ready data for frontend visualization */
  chart_data: ChartReadyAnalytics;
  /** Dashboard generation time */
  generated_at: string;
}
