/**
 * Generated API client for Analytics
 */
import { ChartReadyAnalytics, ConversationStatsResponse, DashboardResponse, DocumentAnalyticsResponse, IntegratedDashboardStats, PerformanceMetricsResponse, SystemAnalyticsResponse, UsageMetricsResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

export class AnalyticsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Start Real Time Dashboard
   * Start real-time dashboard updates for the current user.

This endpoint initiates a background task that streams analytics data
to the user via Server-Sent Events (SSE).
   */
  public async startRealTimeDashboardApiV1AnalyticsRealTimeRealTimeDashboardStart(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/real-time/real-time/dashboard/start`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Stop Real Time Dashboard
   * Stop real-time dashboard updates for the current user.
   */
  public async stopRealTimeDashboardApiV1AnalyticsRealTimeRealTimeDashboardStop(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/real-time/real-time/dashboard/stop`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get User Behavior Analytics
   * Get personalized behavior analytics for a user.

Users can only access their own analytics unless they are admin.
   */
  public async getUserBehaviorAnalyticsApiV1AnalyticsRealTimeUserBehaviorUserId(userId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/real-time/user-behavior/${userId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Intelligent Search
   * Perform intelligent semantic search with personalized results.

Args:
    query: Search query string
    search_type: Type of content to search ("documents", "conversations", "prompts")
    limit: Maximum number of results to return
    include_recommendations: Whether to include search recommendations
   */
  public async intelligentSearchApiV1AnalyticsRealTimeSearchIntelligent(options?: { query?: string; searchType?: string; limit?: number; includeRecommendations?: boolean; additionalQuery?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/real-time/search/intelligent`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'query': options?.query,
        'search_type': options?.searchType,
        'limit': options?.limit,
        'include_recommendations': options?.includeRecommendations,
        ...options?.additionalQuery
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get Trending Content
   * Get trending content personalized for the current user.
   */
  public async getTrendingContentApiV1AnalyticsRealTimeSearchTrending(options?: { limit?: number; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/real-time/search/trending`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'limit': options?.limit,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Send Workflow Update
   * Send a real-time workflow update to the user.
   */
  public async sendWorkflowUpdateApiV1AnalyticsRealTimeRealTimeWorkflowWorkflowIdUpdate(workflowId: string, data: Record<string, unknown>, options?: { updateType?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/real-time/real-time/workflow/${workflowId}/update`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      query: {
        'update_type': options?.updateType,
        ...options?.query
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Send System Health Update
   * Send system health update to all admin users.

This endpoint is admin-only and broadcasts health information
to all connected administrators.
   */
  public async sendSystemHealthUpdateApiV1AnalyticsRealTimeRealTimeSystemHealth(data: Record<string, unknown>): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/real-time/real-time/system-health`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Cleanup Inactive Tasks
   * Clean up inactive real-time tasks.

This endpoint is admin-only and performs maintenance on the
real-time analytics service.
   */
  public async cleanupInactiveTasksApiV1AnalyticsRealTimeRealTimeCleanup(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/real-time/real-time/cleanup`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
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
  public async getConversationStatsApiV1AnalyticsConversations(options?: { startDate?: string | null; endDate?: string | null; period?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ConversationStatsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/conversations`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ConversationStatsResponse>;
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
  public async getUsageMetricsApiV1AnalyticsUsage(options?: { startDate?: string | null; endDate?: string | null; period?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<UsageMetricsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/usage`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<UsageMetricsResponse>;
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
  public async getPerformanceMetricsApiV1AnalyticsPerformance(options?: { startDate?: string | null; endDate?: string | null; period?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<PerformanceMetricsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/performance`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PerformanceMetricsResponse>;
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
  public async getDocumentAnalyticsApiV1AnalyticsDocuments(options?: { startDate?: string | null; endDate?: string | null; period?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<DocumentAnalyticsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/documents`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<DocumentAnalyticsResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/system`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<SystemAnalyticsResponse>;
  }
  /**Get Dashboard Chart Data
   * Get chart-ready analytics data for dashboard visualization.

Args:
    start_date: Start date for analytics
    end_date: End date for analytics  
    period: Predefined period
    current_user: Current authenticated user
    analytics_service: Analytics service
    
Returns:
    Chart-ready analytics data
   */
  public async getDashboardChartDataApiV1AnalyticsDashboardChartData(options?: { startDate?: string | null; endDate?: string | null; period?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ChartReadyAnalytics> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/dashboard/chart-data`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ChartReadyAnalytics>;
  }
  /**Get Integrated Dashboard Stats
   * Get integrated dashboard statistics.

Args:
    current_user: Current authenticated user
    analytics_service: Analytics service
    
Returns:
    Integrated dashboard statistics
   */
  public async getIntegratedDashboardStatsApiV1AnalyticsDashboardIntegrated(): Promise<IntegratedDashboardStats> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/dashboard/integrated`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<IntegratedDashboardStats>;
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
  public async getDashboardApiV1AnalyticsDashboard(options?: { startDate?: string | null; endDate?: string | null; period?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<DashboardResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/dashboard`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<DashboardResponse>;
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
  public async getToolServerAnalyticsApiV1AnalyticsToolservers(options?: { startDate?: string | null; endDate?: string | null; period?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/toolservers`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
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
  public async getUserAnalyticsApiV1AnalyticsUsersUserId(userId: string, options?: { startDate?: string | null; endDate?: string | null; period?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/users/${userId}`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
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
  public async exportAnalyticsApiV1AnalyticsExport(options?: { format?: string; metrics?: string[]; startDate?: string | null; endDate?: string | null; period?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/export`,
      method: 'POST' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'format': options?.format,
        'metrics': options?.metrics,
        'start_date': options?.startDate,
        'end_date': options?.endDate,
        'period': options?.period,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get Analytics Health
   * Get analytics system health status.

Returns:
    Health check results for analytics system
   */
  public async getAnalyticsHealthApiV1AnalyticsHealth(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/health`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get Analytics Metrics Summary
   * Get summary of key analytics metrics for monitoring.

Returns:
    Summary of analytics metrics
   */
  public async getAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummary(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/metrics/summary`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Warm Analytics Cache
   * Warm analytics cache to improve performance.

Args:
    force_refresh: Force refresh of existing cache entries
    current_user: Current authenticated user
    cache_warming_service: Cache warming service
    
Returns:
    Cache warming results
   */
  public async warmAnalyticsCacheApiV1AnalyticsCacheWarm(options?: { forceRefresh?: boolean; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/cache/warm`,
      method: 'POST' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'force_refresh': options?.forceRefresh,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get Cache Warming Status
   * Get cache warming status and performance metrics.

Args:
    current_user: Current authenticated user
    cache_warming_service: Cache warming service
    
Returns:
    Cache warming status and metrics
   */
  public async getCacheWarmingStatusApiV1AnalyticsCacheStatus(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/cache/status`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Optimize Cache Performance
   * Analyze and optimize cache performance automatically.

Args:
    current_user: Current authenticated user
    cache_warming_service: Cache warming service
    
Returns:
    Optimization results and recommendations
   */
  public async optimizeCachePerformanceApiV1AnalyticsCacheOptimize(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/cache/optimize`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Invalidate Stale Cache
   * Invalidate stale cache entries to free up memory.

Args:
    max_age_hours: Maximum age in hours for cache entries to keep
    current_user: Current authenticated user
    cache_warming_service: Cache warming service
    
Returns:
    Cache invalidation results
   */
  public async invalidateStaleCacheApiV1AnalyticsCacheInvalidate(options?: { maxAgeHours?: number; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/cache/invalidate`,
      method: 'POST' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'max_age_hours': options?.maxAgeHours,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get Detailed Performance Metrics
   * Get detailed performance metrics for analytics service.

Args:
    current_user: Current authenticated user
    analytics_service: Analytics service
    
Returns:
    Detailed performance metrics
   */
  public async getDetailedPerformanceMetricsApiV1AnalyticsPerformanceDetailed(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/performance/detailed`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get Database Health Metrics
   * Get comprehensive database health metrics for analytics.

Args:
    current_user: Current authenticated user
    db_optimization_service: Database optimization service
    
Returns:
    Database health metrics and recommendations
   */
  public async getDatabaseHealthMetricsApiV1AnalyticsDatabaseHealth(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/database/health`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Analyze Query Performance
   * Analyze performance of analytics database queries.

Args:
    query_type: Specific query type to analyze (optional)
    current_user: Current authenticated user
    db_optimization_service: Database optimization service
    
Returns:
    Query performance analysis and optimization recommendations
   */
  public async analyzeQueryPerformanceApiV1AnalyticsDatabaseAnalyzeQueries(options?: { queryType?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/analytics/database/analyze-queries`,
      method: 'POST' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'query_type': options?.queryType,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
}