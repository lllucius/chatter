/**
 * Generated API client for Events
 */
import { SSEStatsResponse, TestEventResponse } from '../models/index';
import { BaseAPI, Configuration } from '../runtime';

export class EventsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Events Stream
   * Stream real-time events via Server-Sent Events.

Args:
    request: FastAPI request object
    current_user: Current authenticated user

Returns:
    StreamingResponse with SSE format
   */
  public async eventsStreamApiV1EventsStream(): Promise<Record<string, unknown>> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<Record<string, unknown>>(`/api/v1/events/stream`, requestOptions);
  }
  /**Admin Events Stream
   * Stream all system events for admin users.

Args:
    request: FastAPI request object
    current_user: Current authenticated admin user

Returns:
    StreamingResponse with SSE format for all events
   */
  public async adminEventsStreamApiV1EventsAdminStream(): Promise<Record<string, unknown>> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<Record<string, unknown>>(`/api/v1/events/admin/stream`, requestOptions);
  }
  /**Get Sse Stats
   * Get SSE service statistics.

Args:
    current_user: Current authenticated admin user

Returns:
    SSE service statistics
   */
  public async getSseStatsApiV1EventsStats(): Promise<SSEStatsResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<SSEStatsResponse>(`/api/v1/events/stats`, requestOptions);
  }
  /**Trigger Test Event
   * Trigger a test event for the current user.

Args:
    current_user: Current authenticated user

Returns:
    Success message with event ID
   */
  public async triggerTestEventApiV1EventsTestEvent(): Promise<TestEventResponse> {
    const requestOptions = {
      method: 'POST' as const,
    };

    return this.request<TestEventResponse>(`/api/v1/events/test-event`, requestOptions);
  }
  /**Trigger Broadcast Test
   * Trigger a broadcast test event for all users.

Args:
    current_user: Current authenticated admin user

Returns:
    Success message with event ID
   */
  public async triggerBroadcastTestApiV1EventsBroadcastTest(): Promise<TestEventResponse> {
    const requestOptions = {
      method: 'POST' as const,
    };

    return this.request<TestEventResponse>(`/api/v1/events/broadcast-test`, requestOptions);
  }
}