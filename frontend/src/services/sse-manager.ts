/**
 * SSE Event Manager Service
 * 
 * Manages Server-Sent Events connection and provides EventEmitter pattern
 * for components to subscribe to specific events.
 */

import { AnySSEEvent, SSEEventListener, SSEEventListeners } from './sse-types';
import { chatterSDK } from './chatter-sdk';

export class SSEEventManager {
  private eventSource: EventSource | null = null;
  private listeners: SSEEventListeners = {};
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

  /**
   * Connect to the SSE stream using the current authentication from chatterSDK
   */
  public connect(): void {
    if (!chatterSDK.isAuthenticated()) {
      console.error('SSE: Not authenticated. Please login first.');
      return;
    }

    if (this.eventSource && this.eventSource.readyState !== EventSource.CLOSED) {
      console.log('SSE: Already connected or connecting');
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
    this.isManuallyDisconnected = true;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.stopHealthCheck();

    // Note: With fetch-based approach, we don't have a direct way to cancel
    // The stream will be cancelled when the browser closes the connection
    console.log('SSE: Disconnected');
  }

  /**
   * Subscribe to a specific event type
   */
  public on(eventType: AnySSEEvent['type'] | '*', listener: SSEEventListener): () => void {
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
  public off(eventType: AnySSEEvent['type'] | '*', listener: SSEEventListener): void {
    if (this.listeners[eventType]) {
      this.listeners[eventType] = this.listeners[eventType]!.filter(l => l !== listener);
    }
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
    return this.isConnected ? 'open' : 'closed';
  }

  /**
   * Create the EventSource connection
   */
  private createConnection(): void {
    if (!chatterSDK.isAuthenticated()) {
      console.error('SSE: Not authenticated');
      return;
    }

    try {
      // Get token from chatterSDK instead of directly from localStorage
      const token = chatterSDK.getToken();
      if (!token) {
        console.error('SSE: No authentication token found');
        return;
      }

      // For now, we'll use the standard EventSource and rely on the server
      // to authenticate via cookies or we'll need to implement a custom solution
      const baseURL = (chatterSDK as any).baseURL || window.location.origin;
      const url = `${baseURL}/api/v1/events/stream`;
      console.log('SSE: Connecting to', url);

      // We'll use a custom fetch to handle authentication properly
      this.createAuthenticatedEventSource(url, token);

    } catch (error) {
      console.error('SSE: Failed to create connection:', error);
      if (!this.isManuallyDisconnected) {
        this.scheduleReconnect();
      }
    }
  }

  /**
   * Create an authenticated EventSource using a custom implementation
   */
  private createAuthenticatedEventSource(url: string, token: string): void {
    // For SSE with authentication, we'll use a fetch-based approach
    // that allows us to set custom headers
    this.connectWithFetch(url, token);
  }

  /**
   * Connect using fetch for proper authentication support
   */
  private async connectWithFetch(url: string, token: string): Promise<void> {
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
        },
      });

      if (!response.ok) {
        throw new Error(`SSE: HTTP ${response.status} ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('SSE: No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
      console.log('SSE: Connection opened');

      // Emit connection established event
      this.emitEvent({
        id: `connection_${Date.now()}`,
        type: 'connection.established',
        data: {
          user_id: '',
          connection_id: '',
          established_at: new Date().toISOString()
        },
        timestamp: new Date().toISOString(),
        metadata: {}
      } as AnySSEEvent);

      // Process the stream
      this.processStream(reader, decoder);

    } catch (error) {
      this.isConnected = false;
      console.error('SSE: Connection error', error);
      
      if (!this.isManuallyDisconnected) {
        this.scheduleReconnect();
      }
    }
  }

  /**
   * Process the SSE stream manually
   */
  private async processStream(reader: ReadableStreamDefaultReader<Uint8Array>, decoder: TextDecoder): Promise<void> {
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
      console.error('SSE: Stream processing error:', error);
    } finally {
      this.isConnected = false;
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
      const data = raw.trim();   // Be robust to \r\n endings and whitespace
      try {
        const event = JSON.parse(data) as AnySSEEvent;
        this.emitEvent(event);
      } catch (error) {
        console.error('SSE: Failed to parse event data:', error, data);
      }
    }
    // We can also handle other SSE fields like id:, event:, retry: if needed
  }

  /**
   * Emit an event to all registered listeners
   */
  private emitEvent(event: AnySSEEvent): void {
    console.log('SSE: Received event:', event.type, event.data);

    // Update event tracking
    this.eventCount++;
    this.lastEventTime = Date.now();

    // Basic event validation for security
    if (!this.isValidEvent(event)) {
      console.warn('SSE: Received invalid event, ignoring:', event);
      return;
    }

    // Emit to specific event type listeners
    if (this.listeners[event.type]) {
      this.listeners[event.type]!.forEach(listener => {
        try {
          listener(event);
        } catch (error) {
          console.error(`SSE: Error in event listener for ${event.type}:`, error);
        }
      });
    }

    // Emit to wildcard listeners
    if (this.listeners['*']) {
      this.listeners['*'].forEach(listener => {
        try {
          listener(event);
        } catch (error) {
          console.error('SSE: Error in wildcard event listener:', error);
        }
      });
    }
  }

  /**
   * Validate event structure for security
   */
  private isValidEvent(event: any): boolean {
    // Basic validation to prevent malicious events
    if (!event || typeof event !== 'object') {
      return false;
    }

    // Required fields
    if (!event.id || !event.type || !event.timestamp) {
      return false;
    }

    // Type validation
    if (typeof event.id !== 'string' || typeof event.type !== 'string' || typeof event.timestamp !== 'string') {
      return false;
    }

    // Data should be an object
    if (event.data && typeof event.data !== 'object') {
      return false;
    }

    // Metadata should be an object if present
    if (event.metadata && typeof event.metadata !== 'object') {
      return false;
    }

    return true;
  }

  /**
   * Schedule a reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.isManuallyDisconnected || this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('SSE: Max reconnection attempts reached or manually disconnected');
      return;
    }

    this.reconnectAttempts++;
    
    // Exponential backoff with jitter
    const jitter = Math.random() * 1000; // Add up to 1 second of random delay
    const delay = Math.min(
      this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1) + jitter,
      this.maxReconnectDelay
    );
    
    console.log(`SSE: Scheduling reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      if (!this.isManuallyDisconnected) {
        this.createConnection();
      }
    }, delay);
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
          console.warn('SSE: No events received for 60 seconds, connection may be stale');
          // Could trigger a reconnection here if needed
        }
      }
      
      // Log connection stats periodically
      if (this.connectionStartTime) {
        const connectionDuration = now - this.connectionStartTime;
        console.debug(`SSE: Connection stats - Duration: ${Math.round(connectionDuration / 1000)}s, Events: ${this.eventCount}`);
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
}

// Create a singleton instance
export const sseEventManager = new SSEEventManager();
