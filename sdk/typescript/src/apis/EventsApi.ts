/**
 * Generated API client for Events
 */
import { SSEStatsResponse, TestEventResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod } from '../runtime';

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
  public async eventsStreamApiV1EventsStream(): Promise<ReadableStream<Uint8Array>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/events/stream`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.requestStream(requestContext);
    return response;
  }
  /**Admin Events Stream
   * Stream all system events for admin users.

Args:
    request: FastAPI request object
    current_user: Current authenticated admin user

Returns:
    StreamingResponse with SSE format for all events
   */
  public async adminEventsStreamApiV1EventsAdminStream(): Promise<ReadableStream<Uint8Array>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/events/admin/stream`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.requestStream(requestContext);
    return response;
  }
  /**Get Sse Stats
   * Get SSE service statistics.

Args:
    current_user: Current authenticated admin user

Returns:
    SSE service statistics
   */
  public async getSseStatsApiV1EventsStats(): Promise<SSEStatsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/events/stats`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<SSEStatsResponse>;
  }
  /**Trigger Test Event
   * Trigger a test event for the current user.

Args:
    current_user: Current authenticated user

Returns:
    Success message with event ID
   */
  public async triggerTestEventApiV1EventsTestEvent(): Promise<TestEventResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/events/test-event`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<TestEventResponse>;
  }
  /**Trigger Broadcast Test
   * Trigger a broadcast test event for all users.

Args:
    current_user: Current authenticated admin user

Returns:
    Success message with event ID
   */
  public async triggerBroadcastTestApiV1EventsBroadcastTest(): Promise<TestEventResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/events/broadcast-test`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<TestEventResponse>;
  }
}