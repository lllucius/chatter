/**
 * SSE Event Manager Service
 *
 * Manages Server-Sent Events connection and provides EventEmitter pattern
 * for components to subscribe to specific events.
 */
/* eslint-disable no-console */

import { AnySSEEvent, SSEEventListener, SSEEventListeners } from './sse-types';
import { authService } from '../services/auth-service';
import { handleError } from '../utils/error-handler';

export class SSEEventManager {
  private listeners: SSEEventListeners & Record<string, SSEEventListener[]> =
    {};
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private isConnected = false;
  private isManuallyDisconnected = false;
  private connectionStartTime: number | null = null;
  private eventCount = 0;
  private lastEventTime: number | null = null;
  private healthCheckInterval: NodeJS.Timeout | null = null;
  private eventBuffer: AnySSEEvent[] = [];
  private maxBufferSize = 100; // Buffer up to 100 events during disconnections
  private reconnectTimeouts: Set<NodeJS.Timeout> = new Set();

  /**
   * Connect to the SSE stream using the current authentication from authService
   */
  public connect(): void {
    if (!authService.isAuthenticated()) {
      console.error('SSE: Not authenticated. Please login first.');
      return;
    }

    if (this.isConnected || this.connectionStartTime) {
      // Already connected or connecting
      return;
    }

    this.isManuallyDisconnected = false;
    this.connectionStartTime = Date.now();
    this.createConnection();
    this.startHealthCheck();
  }

  /**
   * Disconnect from the SSE stream
   */
  public disconnect(): void {
    // Disconnecting SSE
    this.isManuallyDisconnected = true;
    this.isConnected = false;
    this.connectionStartTime = null;
    this.reconnectAttempts = 0;
    this.stopHealthCheck();

    // Clear all reconnect timeouts
    this.reconnectTimeouts.forEach((timeout) => clearTimeout(timeout));
    this.reconnectTimeouts.clear();

    // Clear event buffer to prevent memory leaks
    this.eventBuffer = [];

    // Note: With fetch-based approach, we don't have a direct way to cancel
    // The stream will be cancelled when the browser closes the connection
  }

  /**
   * Subscribe to a specific event type
   */
  public on(
    eventType: AnySSEEvent['type'] | '*',
    listener: SSEEventListener
  ): () => void {
    if (!this.listeners[eventType]) {
      this.listeners[eventType] = [];
    }
    this.listeners[eventType]!.push(listener);

    // Return unsubscribe function
    return () => {
      this.off(eventType, listener);
    };
  }

  /**
   * Unsubscribe from a specific event type
   */
  public off(
    eventType: AnySSEEvent['type'] | '*',
    listener: SSEEventListener
  ): void {
    if (this.listeners[eventType]) {
      this.listeners[eventType] = this.listeners[eventType]!.filter(
        (l) => l !== listener
      );
    }
  }

  /**
   * Compatibility method for addEventListener (similar to on())
   */
  public addEventListener(
    eventType: AnySSEEvent['type'] | '*',
    listener: SSEEventListener
  ): void {
    this.on(eventType, listener);
  }

  /**
   * Compatibility method for removeEventListener (similar to off())
   */
  public removeEventListener(
    eventType: AnySSEEvent['type'] | '*',
    listener: SSEEventListener
  ): void {
    this.off(eventType, listener);
  }

  /**
   * Check if connected
   */
  public get connected(): boolean {
    return this.isConnected;
  }

  /**
   * Get current connection state
   */
  public getConnectionState(): 'connecting' | 'open' | 'closed' {
    if (this.connectionStartTime && !this.isConnected) {
      return 'connecting';
    }
    return this.isConnected ? 'open' : 'closed';
  }

  /**
   * Create the connection using SDK authentication
   */
  private createConnection(): void {
    if (!authService.isAuthenticated()) {
      console.error('SSE: Not authenticated. Please login first.');
      return;
    }

    console.log(
      'SSE: Connecting to',
      `${authService.getURL()}/api/v1/events/stream`
    );

    try {
      // Use SDK method with automatic authentication and retry
      this.connectWithSDKAuth();
    } catch (error) {
      handleError(
        error,
        {
          source: 'SSEEventManager.createConnection',
          operation: 'SSE connection initialization',
        },
        {
          showToast: false, // Don't show toast for connection failures
          logToConsole: true,
        }
      );
      this.connectionStartTime = null;
      if (!this.isManuallyDisconnected) {
        this.scheduleReconnect();
      }
    }
  }

  /**
   * Connect using SDK authentication with automatic token refresh
   */
  private async connectWithSDKAuth(): Promise<void> {
    try {
      // Use SDK method with automatic authentication handling
      const stream = await authService.executeWithAuth(async (sdk) => {
        return await sdk.events.eventsStreamApiV1EventsStream();
      });

      const reader = stream.getReader();
      const decoder = new TextDecoder();

      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;

      // Emit connection established event
      this.emitEvent({
        id: `connection_${Date.now()}`,
        type: 'connection.established',
        data: {
          user_id: '',
          connection_id: '',
          established_at: new Date().toISOString(),
        },
        timestamp: new Date().toISOString(),
        metadata: {},
      } as AnySSEEvent);

      // Process the stream
      this.processStream(reader, decoder);
    } catch (error) {
      this.isConnected = false;
      this.connectionStartTime = null;

      handleError(
        error,
        {
          source: 'SSEEventManager.connectWithSDKAuth',
          operation: 'SSE stream connection',
        },
        {
          showToast: false, // Don't show toast for connection failures
          logToConsole: true,
        }
      );

      if (!this.isManuallyDisconnected) {
        this.scheduleReconnect();
      }
    }
  }

  /**
   * Process the SSE stream manually
   */
  private async processStream(
    reader: ReadableStreamDefaultReader<Uint8Array>,
    decoder: TextDecoder
  ): Promise<void> {
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          console.log('SSE: Stream ended');
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep the last incomplete line in buffer

        for (const line of lines) {
          this.processSSELine(line);
        }
      }
    } catch (error) {
      handleError(
        error,
        {
          source: 'SSEEventManager.processStream',
          operation: 'SSE stream processing',
        },
        {
          showToast: false, // Don't show toast for stream processing failures
          logToConsole: true,
        }
      );
    } finally {
      this.isConnected = false;
      this.connectionStartTime = null;
      console.log('SSE: Disconnected');
      if (!this.isManuallyDisconnected) {
        this.scheduleReconnect();
      }
    }
  }

  /**
   * Process a single SSE line
   */
  private processSSELine(line: string): void {
    if (line.startsWith('data: ')) {
      const raw = line.slice(6); // Remove 'data: ' prefix
      const data = raw.trim(); // Be robust to \r\n endings and whitespace
      try {
        const event = JSON.parse(data) as AnySSEEvent;
        this.emitEvent(event);
      } catch (error) {
        handleError(
          error,
          {
            source: 'SSEEventManager.processSSELine',
            operation: 'SSE event parsing',
            additionalData: { rawData: data },
          },
          {
            showToast: false, // Don't show toast for parsing failures
            logToConsole: true,
          }
        );
      }
    }
    // We can also handle other SSE fields like id:, event:, retry: if needed
  }

  /**
   * Emit an event to all registered listeners
   */
  private emitEvent(event: AnySSEEvent): void {
    // Update event tracking
    this.eventCount++;
    this.lastEventTime = Date.now();

    // Basic event validation for security
    if (!this.isValidEvent(event)) {
      return;
    }

    // Extract unified event metadata if available
    const unifiedMetadata = this.extractUnifiedMetadata(event);
    // TODO: Process unified metadata when ready

    // Route high priority events to special handlers
    if (
      unifiedMetadata?.priority === 'high' ||
      unifiedMetadata?.priority === 'critical'
    ) {
      this.handleHighPriorityEvent(event, unifiedMetadata);
    }

    // Emit to specific event type listeners
    if (this.listeners[event.type]) {
      this.listeners[event.type]!.forEach((listener) => {
        try {
          listener(event);
        } catch (error) {
          handleError(
            error,
            {
              source: 'SSEEventManager.emitEvent',
              operation: 'specific event listener execution',
              additionalData: { eventType: event.type },
            },
            {
              showToast: false, // Don't show toast for listener failures
              logToConsole: true,
            }
          );
        }
      });
    }

    // Emit to wildcard listeners
    if (this.listeners['*']) {
      this.listeners['*'].forEach((listener) => {
        try {
          listener(event);
        } catch (error) {
          handleError(
            error,
            {
              source: 'SSEEventManager.emitEvent',
              operation: 'wildcard event listener execution',
              additionalData: { eventType: event.type },
            },
            {
              showToast: false, // Don't show toast for listener failures
              logToConsole: true,
            }
          );
        }
      });
    }

    // Emit to category listeners if this is a unified event
    if (unifiedMetadata?.category) {
      this.emitToCategoryListeners(event, unifiedMetadata.category);
    }
  }

  /**
   * Validate event structure for security
   */
  private isValidEvent(event: unknown): event is AnySSEEvent {
    // Basic validation to prevent malicious events
    if (!event || typeof event !== 'object') {
      return false;
    }

    const obj = event as Record<string, unknown>;

    // Required fields
    if (!obj.id || !obj.type || !obj.timestamp) {
      return false;
    }

    // Type validation
    if (
      typeof obj.id !== 'string' ||
      typeof obj.type !== 'string' ||
      typeof obj.timestamp !== 'string'
    ) {
      return false;
    }

    // Data should be an object
    if (obj.data && typeof obj.data !== 'object') {
      return false;
    }

    // Metadata should be an object if present
    if (obj.metadata && typeof obj.metadata !== 'object') {
      return false;
    }

    return true;
  }

  /**
   * Schedule a reconnection attempt
   */
  private scheduleReconnect(): void {
    if (
      this.isManuallyDisconnected ||
      this.reconnectAttempts >= this.maxReconnectAttempts
    ) {
      console.log(
        `SSE: Max reconnection attempts reached (${this.maxReconnectAttempts})`
      );
      return;
    }

    this.reconnectAttempts++;

    // Exponential backoff with jitter
    const jitter = Math.random() * 1000; // Add up to 1 second of random delay
    const delay = Math.min(
      this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1) + jitter,
      this.maxReconnectDelay
    );

    console.log(
      `SSE: Scheduling reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`
    );

    const timeout = setTimeout(() => {
      // Remove this timeout from tracking
      this.reconnectTimeouts.delete(timeout);

      if (!this.isManuallyDisconnected) {
        this.createConnection();
      }
    }, delay);

    // Track timeout for cleanup
    this.reconnectTimeouts.add(timeout);
  }

  /**
   * Start health check to monitor connection health
   */
  private startHealthCheck(): void {
    this.stopHealthCheck(); // Ensure no duplicate intervals

    this.healthCheckInterval = setInterval(() => {
      const now = Date.now();

      // Check if we haven't received events in a while (but only if connected)
      if (this.isConnected && this.lastEventTime) {
        const timeSinceLastEvent = now - this.lastEventTime;
        const healthCheckTimeout = 60000; // 60 seconds

        if (timeSinceLastEvent > healthCheckTimeout) {
          // Could trigger a reconnection here if needed
        }
      }

      // Log connection stats periodically
      if (this.connectionStartTime) {
        // Connection duration tracking for future use
      }
    }, 30000); // Check every 30 seconds
  }

  /**
   * Stop health check
   */
  private stopHealthCheck(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }

  /**
   * Get connection statistics
   */
  public getConnectionStats(): {
    isConnected: boolean;
    connectionDuration: number | null;
    eventCount: number;
    reconnectAttempts: number;
    lastEventTime: number | null;
  } {
    const connectionDuration = this.connectionStartTime
      ? Date.now() - this.connectionStartTime
      : null;

    return {
      isConnected: this.isConnected,
      connectionDuration,
      eventCount: this.eventCount,
      reconnectAttempts: this.reconnectAttempts,
      lastEventTime: this.lastEventTime,
    };
  }

  /**
   * Extract unified event metadata from SSE event
   */
  private extractUnifiedMetadata(event: AnySSEEvent): {
    category?: string;
    priority?: string;
    source_system?: string;
    correlation_id?: string;
  } | null {
    if (!event.metadata) return null;

    const metadata = event.metadata as Record<string, unknown>;
    return {
      category: metadata.category as string | undefined,
      priority: metadata.priority as string | undefined,
      source_system: metadata.source_system as string | undefined,
      correlation_id: metadata.correlation_id as string | undefined,
    };
  }

  /**
   * Handle high priority events with special treatment
   */
  private handleHighPriorityEvent(
    event: AnySSEEvent,
    metadata: Record<string, unknown>
  ): void {
    // Log high priority events - handled by metadata tracking

    // Could trigger notifications, sounds, or other UI feedback
    if (metadata.priority === 'critical') {
      // Show critical alert
      this.showCriticalAlert(event);
    }
  }

  /**
   * Show critical alert for critical priority events
   */
  private showCriticalAlert(event: AnySSEEvent): void {
    // This could integrate with a notification system
    if ('Notification' in window && Notification.permission === 'granted') {
      const eventData = event.data as Record<string, unknown> | undefined;
      const message = eventData?.message as string | undefined;
      new Notification('Critical System Alert', {
        body: `${event.type}: ${message || 'Critical event occurred'}`,
        icon: '/favicon.ico',
        tag: 'critical-alert',
      });
    }
  }

  /**
   * Emit to category-specific listeners
   */
  private emitToCategoryListeners(event: AnySSEEvent, category: string): void {
    const categoryKey = `category:${category}`;
    const listeners = this.listeners[categoryKey] as
      | SSEEventListener[]
      | undefined;
    if (listeners) {
      listeners.forEach((listener: SSEEventListener) => {
        try {
          listener(event);
        } catch (error) {
          handleError(
            error,
            {
              source: 'SSEEventManager.emitToCategoryListeners',
              operation: 'category event listener execution',
              additionalData: { category, eventType: event.type },
            },
            {
              showToast: false, // Don't show toast for listener failures
              logToConsole: true,
            }
          );
        }
      });
    }
  }

  /**
   * Subscribe to events by category
   */
  public onCategory(category: string, listener: SSEEventListener): () => void {
    const categoryKey = `category:${category}`;
    const listenersMap = this.listeners;
    if (!listenersMap[categoryKey]) {
      listenersMap[categoryKey] = [];
    }
    listenersMap[categoryKey].push(listener);

    // Return unsubscribe function
    return () => {
      this.offCategory(category, listener);
    };
  }

  /**
   * Unsubscribe from category events
   */
  public offCategory(category: string, listener: SSEEventListener): void {
    const categoryKey = `category:${category}`;
    const listenersMap = this.listeners;
    if (listenersMap[categoryKey]) {
      listenersMap[categoryKey] = listenersMap[categoryKey].filter(
        (l: SSEEventListener) => l !== listener
      );
    }
  }

  /**
   * Subscribe to high priority events
   */
  public onHighPriority(listener: SSEEventListener): () => void {
    return this.on('*', (event) => {
      const metadata = this.extractUnifiedMetadata(event);
      if (metadata?.priority === 'high' || metadata?.priority === 'critical') {
        listener(event);
      }
    });
  }

  /**
   * Request notification permission for critical alerts
   */
  public async requestNotificationPermission(): Promise<boolean> {
    if (!('Notification' in window)) {
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }

    return false;
  }

  /**
   * Trigger a test event using the SDK
   * This demonstrates how to use SDK for non-streaming event operations
   */
  public async triggerTestEvent(): Promise<boolean> {
    try {
      await authService.executeWithAuth(async (sdk) => {
        return await sdk.events.triggerTestEventApiV1EventsTestEvent();
      });

      // Response processed successfully
      return true;
    } catch (error) {
      handleError(
        error,
        {
          source: 'SSEEventManager.triggerTestEvent',
          operation: 'trigger test event',
        },
        {
          showToast: true, // Show toast for test event failures since it's user-initiated
          logToConsole: true,
          fallbackMessage: 'Failed to trigger test event',
        }
      );
      return false;
    }
  }

  /**
   * Get SSE statistics using the SDK
   */
  public async getSSEStats(): Promise<Record<string, unknown> | null> {
    try {
      const response = await authService.executeWithAuth(async (sdk) => {
        return await sdk.events.getSseStatsApiV1EventsStats();
      });

      return response as unknown as Record<string, unknown>;
    } catch (error) {
      handleError(
        error,
        {
          source: 'SSEEventManager.getSSEStats',
          operation: 'get SSE statistics',
        },
        {
          showToast: false, // Don't show toast for stats failures
          logToConsole: true,
          fallbackMessage: 'Failed to get SSE statistics',
        }
      );
      return null;
    }
  }
}

// Create a singleton instance
export const sseEventManager = new SSEEventManager();
