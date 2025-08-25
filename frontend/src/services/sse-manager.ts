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
    this.createConnection();
  }

  /**
   * Disconnect from the SSE stream
   */
  public disconnect(): void {
    this.isManuallyDisconnected = true;
    this.isConnected = false;
    this.reconnectAttempts = 0;

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
      // Since EventSource doesn't support custom headers, we need to use a different approach
      // Let's use a custom fetch-based EventSource implementation or modify our approach
      const token = localStorage.getItem('chatter_token');
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
      const data = line.slice(6); // Remove 'data: ' prefix
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
   * Schedule a reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.isManuallyDisconnected || this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('SSE: Max reconnection attempts reached or manually disconnected');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay);
    
    console.log(`SSE: Scheduling reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      if (!this.isManuallyDisconnected) {
        this.createConnection();
      }
    }, delay);
  }
}

// Create a singleton instance
export const sseEventManager = new SSEEventManager();