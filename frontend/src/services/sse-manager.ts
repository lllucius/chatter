/**
 * SSE Event Manager Service
 * 
 * Manages Server-Sent Events connection and provides EventEmitter pattern
 * for components to subscribe to specific events.
 */

import { AnySSEEvent, SSEEventListener, SSEEventListeners } from './sse-types';
import { chatterClient } from '../sdk/client';

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
  private eventBuffer: AnySSEEvent[] = [];
  private maxBufferSize = 100; // Buffer up to 100 events during disconnections
  private reconnectTimeouts: Set<NodeJS.Timeout> = new Set();

  /**
   * Connect to the SSE stream using the current authentication from chatterClient
   */
  public connect(): void {
    if (!chatterClient.isAuthenticated()) {
      console.error('SSE: Not authenticated. Please login first.');
      return;
    }

    if (this.isConnected || this.connectionStartTime) {
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

    // Clear all reconnect timeouts
    this.reconnectTimeouts.forEach(timeout => clearTimeout(timeout));
    this.reconnectTimeouts.clear();

    // Clear event buffer to prevent memory leaks
    this.eventBuffer = [];

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
   * Compatibility method for addEventListener (similar to on())
   */
  public addEventListener(eventType: AnySSEEvent['type'] | '*', listener: SSEEventListener): void {
    this.on(eventType, listener);
  }

  /**
   * Compatibility method for removeEventListener (similar to off())
   */
  public removeEventListener(eventType: AnySSEEvent['type'] | '*', listener: SSEEventListener): void {
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
    return this.isConnected ? 'open' : 'closed';
  }

  /**
   * Create the EventSource connection
   */
  private createConnection(): void {
    if (!chatterClient.isAuthenticated()) {
      console.error('SSE: Not authenticated');
      return;
    }

    try {
      // Get token from chatterClient instead of directly from localStorage
      const token = chatterClient.getToken();
      if (!token) {
        console.error('SSE: No authentication token found');
        return;
      }

      // For now, we'll use the standard EventSource and rely on the server
      // to authenticate via cookies or we'll need to implement a custom solution
      const baseURL = chatterClient.getURL() || window.location.origin;
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

    // Extract unified event metadata if available
    const unifiedMetadata = this.extractUnifiedMetadata(event);
    if (unifiedMetadata) {
      console.log('SSE: Unified event metadata:', unifiedMetadata);
    }

    // Route high priority events to special handlers
    if (unifiedMetadata?.priority === 'high' || unifiedMetadata?.priority === 'critical') {
      this.handleHighPriorityEvent(event, unifiedMetadata);
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

    // Emit to category listeners if this is a unified event
    if (unifiedMetadata?.category) {
      this.emitToCategoryListeners(event, unifiedMetadata.category);
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

    return {
      category: event.metadata.category,
      priority: event.metadata.priority,
      source_system: event.metadata.source_system,
      correlation_id: event.metadata.correlation_id,
    };
  }

  /**
   * Handle high priority events with special treatment
   */
  private handleHighPriorityEvent(event: AnySSEEvent, metadata: any): void {
    // Log high priority events
    console.warn('SSE: High priority event received:', {
      type: event.type,
      priority: metadata.priority,
      category: metadata.category,
      timestamp: event.timestamp
    });

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
      new Notification('Critical System Alert', {
        body: `${event.type}: ${event.data.message || 'Critical event occurred'}`,
        icon: '/favicon.ico',
        tag: 'critical-alert'
      });
    }
  }

  /**
   * Emit to category-specific listeners
   */
  private emitToCategoryListeners(event: AnySSEEvent, category: string): void {
    const categoryKey = `category:${category}`;
    if (this.listeners[categoryKey]) {
      this.listeners[categoryKey]!.forEach(listener => {
        try {
          listener(event);
        } catch (error) {
          console.error(`SSE: Error in category listener for ${category}:`, error);
        }
      });
    }
  }

  /**
   * Subscribe to events by category
   */
  public onCategory(category: string, listener: SSEEventListener): () => void {
    const categoryKey = `category:${category}`;
    if (!this.listeners[categoryKey]) {
      this.listeners[categoryKey] = [];
    }
    this.listeners[categoryKey]!.push(listener);

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
    if (this.listeners[categoryKey]) {
      this.listeners[categoryKey] = this.listeners[categoryKey]!.filter(l => l !== listener);
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
      console.warn('SSE: Notifications not supported');
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
}

// Create a singleton instance
export const sseEventManager = new SSEEventManager();
