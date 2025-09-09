/**
 * Generated API client for Analytics
 */
import { ConversationStatsResponse, DashboardResponse, DocumentAnalyticsResponse, PerformanceMetricsResponse, Record, SystemAnalyticsResponse, UsageMetricsResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOptions } from '../runtime';

export class AnalyticsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Get Conversation Stats
   * Get conversation statistics.

Args:
    start_date: Start date for analytics
    end_date: End date for analytics
    period: Predefined period
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Conversation statistics
   */
  public async getConversationStatsApiV1AnalyticsConversations(options?: RequestOptions): Promise<ConversationStatsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
      },
    };

    return this.request<ConversationStatsResponse>(`/api/v1/analytics/conversations`, requestOptions);
  }
  /**Get Usage Metrics
   * Get usage metrics.

Args:
    start_date: Start date for analytics
    end_date: End date for analytics
    period: Predefined period
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Usage metrics
   */
  public async getUsageMetricsApiV1AnalyticsUsage(options?: RequestOptions): Promise<UsageMetricsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
      },
    };

    return this.request<UsageMetricsResponse>(`/api/v1/analytics/usage`, requestOptions);
  }
  /**Get Performance Metrics
   * Get performance metrics.

Args:
    request: Performance metrics request parameters
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Performance metrics
   */
  public async getPerformanceMetricsApiV1AnalyticsPerformance(options?: RequestOptions): Promise<PerformanceMetricsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
      },
    };

    return this.request<PerformanceMetricsResponse>(`/api/v1/analytics/performance`, requestOptions);
  }
  /**Get Document Analytics
   * Get document analytics.

Args:
    request: Document analytics request parameters
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Document analytics
   */
  public async getDocumentAnalyticsApiV1AnalyticsDocuments(options?: RequestOptions): Promise<DocumentAnalyticsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
      },
    };

    return this.request<DocumentAnalyticsResponse>(`/api/v1/analytics/documents`, requestOptions);
  }
  /**Get System Analytics
   * Get system analytics.

Args:
    request: System analytics request parameters
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    System analytics
   */
  public async getSystemAnalyticsApiV1AnalyticsSystem(): Promise<SystemAnalyticsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<SystemAnalyticsResponse>(`/api/v1/analytics/system`, requestOptions);
  }
  /**Get Dashboard
   * Get comprehensive dashboard data.

Args:
    request: Dashboard request parameters
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Complete dashboard data
   */
  public async getDashboardApiV1AnalyticsDashboard(options?: RequestOptions): Promise<DashboardResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
      },
    };

    return this.request<DashboardResponse>(`/api/v1/analytics/dashboard`, requestOptions);
  }
  /**Get Tool Server Analytics
   * Get tool server analytics.

Args:
    request: Tool server analytics request parameters
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Tool server analytics data
   */
  public async getToolServerAnalyticsApiV1AnalyticsToolservers(options?: RequestOptions): Promise<Record<string, unknown>> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
      },
    };

    return this.request<Record<string, unknown>>(`/api/v1/analytics/toolservers`, requestOptions);
  }
  /**Get User Analytics
   * Get per-user analytics.

Args:
    user_id: User ID
    start_date: Start date for analytics
    end_date: End date for analytics
    period: Predefined period
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    User-specific analytics
   */
  public async getUserAnalyticsApiV1AnalyticsUsersUserId(userId: string, options?: RequestOptions): Promise<Record<string, unknown>> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
      },
    };

    return this.request<Record<string, unknown>>(`/api/v1/analytics/users/${userId}`, requestOptions);
  }
  /**Export Analytics
   * Export analytics reports.

Args:
    format: Export format
    metrics: List of metrics to export
    start_date: Start date for analytics
    end_date: End date for analytics
    period: Predefined period
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Exported analytics report
   */
  public async exportAnalyticsApiV1AnalyticsExport(options?: RequestOptions): Promise<Record<string, unknown>> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      headers: options?.headers,
      query: {
        'format': options?.format,
        'metrics': options?.metrics ?? '',
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
      },
    };

    return this.request<Record<string, unknown>>(`/api/v1/analytics/export`, requestOptions);
  }
  /**Get Analytics Health
   * Get analytics system health status.

Returns:
    Health check results for analytics system
   */
  public async getAnalyticsHealthApiV1AnalyticsHealth(): Promise<Record<string, unknown>> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<Record<string, unknown>>(`/api/v1/analytics/health`, requestOptions);
  }
  /**Get Analytics Metrics Summary
   * Get summary of key analytics metrics for monitoring.

Returns:
    Summary of analytics metrics
   */
  public async getAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummary(): Promise<Record<string, unknown>> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<Record<string, unknown>>(`/api/v1/analytics/metrics/summary`, requestOptions);
  }
}