/**
 * Generated from OpenAPI schema: ChartReadyAnalytics
 */
import { ChartDataPoint } from './ChartDataPoint';
import { TimeSeriesDataPoint } from './TimeSeriesDataPoint';

export interface ChartReadyAnalytics {
  /** Daily conversation data for charts */
  conversation_chart_data: TimeSeriesDataPoint[];
  /** Token usage over time for charts */
  token_usage_data: TimeSeriesDataPoint[];
  /** Performance metrics for charts */
  performance_chart_data: ChartDataPoint[];
  /** System health data for charts */
  system_health_data: ChartDataPoint[];
  /** Integration usage data for charts */
  integration_data: ChartDataPoint[];
  /** 24-hour performance breakdown */
  hourly_performance_data: Record<string, unknown>[];
}
