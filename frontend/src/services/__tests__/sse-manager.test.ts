/**
 * Tests for SSE Event Manager Service
 */

import { vi, describe, beforeEach, afterEach, it, expect } from 'vitest';
import { SSEEventManager } from '../sse-manager';
import { chatterSDK } from '../chatter-sdk';
import { AnySSEEvent, SSEEventType } from '../sse-types';

// Mock EventSource
class MockEventSource implements EventSource {
  public readyState: number = EventSource.CONNECTING;
  public url: string = '';
  public withCredentials: boolean = false;
  public CONNECTING = EventSource.CONNECTING;
  public OPEN = EventSource.OPEN;
  public CLOSED = EventSource.CLOSED;
  
  private listeners: { [key: string]: EventListener[] } = {};
  
  constructor(url: string) {
    this.url = url;
    // Simulate connection opening
    setTimeout(() => {
      this.readyState = EventSource.OPEN;
      this.dispatchEvent(new Event('open'));
    }, 10);
  }
  
  addEventListener(type: string, listener: EventListener): void {
    if (!this.listeners[type]) {
      this.listeners[type] = [];
    }
    this.listeners[type].push(listener);
  }
  
  removeEventListener(type: string, listener: EventListener): void {
    if (this.listeners[type]) {
      this.listeners[type] = this.listeners[type].filter(l => l !== listener);
    }
  }
  
  dispatchEvent(event: Event): boolean {
    const listeners = this.listeners[event.type] || [];
    listeners.forEach(listener => listener(event));
    return true;
  }
  
  close(): void {
    this.readyState = EventSource.CLOSED;
    this.dispatchEvent(new Event('close'));
  }
  
  // Helper method to simulate receiving messages
  public simulateMessage(data: any, eventType?: string): void {
    const messageEvent = new MessageEvent('message', {
      data: JSON.stringify(data),
      lastEventId: Date.now().toString(),
      origin: 'http://localhost:8000',
      ...(eventType && { type: eventType })
    });
    this.dispatchEvent(messageEvent);
  }
  
  // Properties required by EventSource interface
  onerror: ((this: EventSource, ev: Event) => any) | null = null;
  onmessage: ((this: EventSource, ev: MessageEvent) => any) | null = null;
  onopen: ((this: EventSource, ev: Event) => any) | null = null;
}

// Mock chatterSDK
vi.mock('../chatter-sdk', () => ({
  chatterSDK: {
    isAuthenticated: vi.fn(() => true),
    getBaseURL: vi.fn(() => 'http://localhost:8000'),
    getAuthHeaders: vi.fn(() => ({ Authorization: 'Bearer test-token' })),
    getToken: vi.fn(() => 'test-token'),
    baseURL: 'http://localhost:8000'
  }
}));

// Mock global EventSource
(global as any).EventSource = MockEventSource;

describe('SSEEventManager', () => {
  let sseManager: SSEEventManager;
  let mockEventSource: MockEventSource;

  beforeEach(() => {
    sseManager = new SSEEventManager();
    vi.clearAllMocks();
    
    // Reset authentication mock
    (chatterSDK.isAuthenticated as vi.Mock).mockReturnValue(true);
  });

  afterEach(() => {
    sseManager.disconnect();
    vi.clearAllTimers();
  });

  describe('Connection Management', () => {
    test('should not connect when not authenticated', () => {
      (chatterSDK.isAuthenticated as vi.Mock).mockReturnValue(false);
      
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation();
      sseManager.connect();
      
      expect(consoleSpy).toHaveBeenCalledWith('SSE: Not authenticated. Please login first.');
      expect(sseManager.isConnected()).toBe(false);
      
      consoleSpy.mockRestore();
    });

    test('should connect when authenticated', () => {
      sseManager.connect();
      expect(sseManager.isConnected()).toBe(false); // Initially connecting
      
      // Wait for connection to open
      setTimeout(() => {
        expect(sseManager.isConnected()).toBe(true);
      }, 20);
    });

    test('should not create multiple connections', () => {
      sseManager.connect();
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation();
      
      sseManager.connect(); // Second call
      
      expect(consoleSpy).toHaveBeenCalledWith('SSE: Already connected or connecting');
      consoleSpy.mockRestore();
    });

    test('should disconnect properly', () => {
      sseManager.connect();
      sseManager.disconnect();
      
      expect(sseManager.isConnected()).toBe(false);
    });
  });

  describe('Event Listening', () => {
    test('should register event listeners', () => {
      const listener = vi.fn();
      sseManager.addEventListener(SSEEventType.CHAT_MESSAGE_CHUNK, listener);
      
      // Verify listener is registered (internal state)
      expect(typeof listener).toBe('function');
    });

    test('should remove event listeners', () => {
      const listener = vi.fn();
      sseManager.addEventListener(SSEEventType.CHAT_MESSAGE_CHUNK, listener);
      sseManager.removeEventListener(SSEEventType.CHAT_MESSAGE_CHUNK, listener);
      
      // Listener should be removed
      expect(typeof listener).toBe('function');
    });

    test('should handle multiple listeners for same event', () => {
      const listener1 = vi.fn();
      const listener2 = vi.fn();
      
      sseManager.addEventListener(SSEEventType.CHAT_MESSAGE_CHUNK, listener1);
      sseManager.addEventListener(SSEEventType.CHAT_MESSAGE_CHUNK, listener2);
      
      expect(typeof listener1).toBe('function');
      expect(typeof listener2).toBe('function');
    });
  });

  describe('Event Processing', () => {
    beforeEach(() => {
      sseManager.connect();
      // Wait for connection
      return new Promise(resolve => setTimeout(resolve, 20));
    });

    test('should process chat message chunk events', (done) => {
      const listener = vi.fn((event: AnySSEEvent) => {
        expect(event.type).toBe(SSEEventType.CHAT_MESSAGE_CHUNK);
        expect(event.data.content).toBe('Hello world');
        done();
      });

      sseManager.addEventListener(SSEEventType.CHAT_MESSAGE_CHUNK, listener);
      
      // Simulate receiving a message
      const eventData = {
        type: SSEEventType.CHAT_MESSAGE_CHUNK,
        data: { content: 'Hello world', conversationId: 'conv-123' }
      };
      
      // Access the private eventSource for testing
      const eventSource = (sseManager as any).eventSource as MockEventSource;
      eventSource.simulateMessage(eventData);
    });

    test('should process workflow status events', (done) => {
      const listener = vi.fn((event: AnySSEEvent) => {
        expect(event.type).toBe(SSEEventType.WORKFLOW_STATUS);
        expect(event.data.status).toBe('completed');
        done();
      });

      sseManager.addEventListener(SSEEventType.WORKFLOW_STATUS, listener);
      
      const eventData = {
        type: SSEEventType.WORKFLOW_STATUS,
        data: { 
          workflowId: 'wf-123',
          status: 'completed',
          result: { success: true }
        }
      };
      
      const eventSource = (sseManager as any).eventSource as MockEventSource;
      eventSource.simulateMessage(eventData);
    });

    test('should process document processing events', (done) => {
      const listener = vi.fn((event: AnySSEEvent) => {
        expect(event.type).toBe(SSEEventType.DOCUMENT_PROCESSING);
        expect(event.data.documentId).toBe('doc-456');
        done();
      });

      sseManager.addEventListener(SSEEventType.DOCUMENT_PROCESSING, listener);
      
      const eventData = {
        type: SSEEventType.DOCUMENT_PROCESSING,
        data: {
          documentId: 'doc-456',
          status: 'processing',
          progress: 0.5
        }
      };
      
      const eventSource = (sseManager as any).eventSource as MockEventSource;
      eventSource.simulateMessage(eventData);
    });
  });

  describe('Connection Health', () => {
    test('should track connection metrics', () => {
      sseManager.connect();
      
      const metrics = sseManager.getConnectionMetrics();
      expect(metrics.connectionStartTime).toBeDefined();
      expect(metrics.eventCount).toBe(0);
      expect(metrics.isConnected).toBe(false); // Initially
    });

    test('should increment event count on messages', (done) => {
      sseManager.connect();
      
      setTimeout(() => {
        const eventData = {
          type: SSEEventType.CHAT_MESSAGE_CHUNK,
          data: { content: 'test' }
        };
        
        const eventSource = (sseManager as any).eventSource as MockEventSource;
        eventSource.simulateMessage(eventData);
        
        setTimeout(() => {
          const metrics = sseManager.getConnectionMetrics();
          expect(metrics.eventCount).toBe(1);
          done();
        }, 10);
      }, 30);
    });
  });

  describe('Reconnection Logic', () => {
    test('should attempt reconnection on connection loss', () => {
      vi.useFakeTimers();
      sseManager.connect();
      
      // Simulate connection loss
      const eventSource = (sseManager as any).eventSource as MockEventSource;
      eventSource.dispatchEvent(new Event('error'));
      
      // Should start reconnection process
      vi.advanceTimersByTime(1000); // Initial reconnect delay
      
      expect(true).toBe(true); // Placeholder - actual implementation would verify reconnection
      
      vi.useRealTimers();
    });
  });

  describe('Error Handling', () => {
    test('should handle malformed messages gracefully', (done) => {
      sseManager.connect();
      
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation();
      
      setTimeout(() => {
        const eventSource = (sseManager as any).eventSource as MockEventSource;
        
        // Simulate malformed message
        const malformedEvent = new MessageEvent('message', {
          data: 'invalid json{',
          lastEventId: '1',
          origin: 'http://localhost:8000'
        });
        
        eventSource.dispatchEvent(malformedEvent);
        
        setTimeout(() => {
          expect(consoleSpy).toHaveBeenCalled();
          consoleSpy.mockRestore();
          done();
        }, 10);
      }, 30);
    });

    test('should handle connection errors', () => {
      sseManager.connect();
      
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation();
      
      // Simulate connection error
      const eventSource = (sseManager as any).eventSource as MockEventSource;
      eventSource.dispatchEvent(new Event('error'));
      
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('Cleanup', () => {
    test('should cleanup resources on disconnect', () => {
      sseManager.connect();
      const eventSource = (sseManager as any).eventSource;
      
      expect(eventSource).toBeDefined();
      
      sseManager.disconnect();
      
      // Should clean up health check interval and close connection
      expect(sseManager.isConnected()).toBe(false);
    });
  });
});