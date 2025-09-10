/**
 * Generated API client for Health
 */
import { CorrelationTraceResponse, HealthCheckResponse, MetricsResponse, ReadinessCheckResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod } from '../runtime';

export class HealthApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Health Check Endpoint
   * Basic health check endpoint.

Returns:
    Health status
   */
  public async healthCheckEndpointHealthz(): Promise<HealthCheckResponse> {
    const requestContext: RequestOpts = {
      path: `/healthz`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<HealthCheckResponse>;
  }
  /**Readiness Check
   * Readiness check endpoint with database connectivity.

This checks that the application is ready to serve traffic by validating
that all external dependencies (database, etc.) are available.

Args:
    session: Database session

Returns:
    Readiness status with detailed checks.
    Returns 200 if ready, 503 if not ready.
   */
  public async readinessCheckReadyz(): Promise<ReadinessCheckResponse> {
    const requestContext: RequestOpts = {
      path: `/readyz`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ReadinessCheckResponse>;
  }
  /**Liveness Check
   * Liveness check endpoint for Kubernetes.

This is a simple liveness probe that checks if the application process
is running and responding. It should NOT check external dependencies.

Returns:
    Health status indicating the application is alive
   */
  public async livenessCheckLive(): Promise<HealthCheckResponse> {
    const requestContext: RequestOpts = {
      path: `/live`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<HealthCheckResponse>;
  }
  /**Get Metrics
   * Get application metrics and monitoring data.

Returns:
    Application metrics including performance and health data
   */
  public async getMetricsMetrics(): Promise<MetricsResponse> {
    const requestContext: RequestOpts = {
      path: `/metrics`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<MetricsResponse>;
  }
  /**Get Correlation Trace
   * Get trace of all requests for a correlation ID.

Args:
    correlation_id: The correlation ID to trace

Returns:
    List of requests associated with the correlation ID
   */
  public async getCorrelationTraceTraceCorrelationId(correlationId: string): Promise<CorrelationTraceResponse> {
    const requestContext: RequestOpts = {
      path: `/trace/${correlationId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<CorrelationTraceResponse>;
  }
}