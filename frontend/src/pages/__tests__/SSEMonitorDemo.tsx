/**
 * Demo component to test SSE Monitor functionality without authentication
 */
import React, { useState } from 'react';
import { Box, Button, Typography } from '@mui/material';
import SSEMonitorPage from '../SSEMonitorPage';
import { AnySSEEvent, SSEEventListener } from '../../services/sse-types';

// Mock SSE Manager for testing
class MockSSEManager {
  private listeners: Map<string, SSEEventListener[]> = new Map();

  addEventListener(eventType: string, listener: SSEEventListener): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType)!.push(listener);
  }

  removeEventListener(eventType: string, listener: SSEEventListener): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  connect(): void {
    console.log('Mock SSE Manager: Connected');
  }

  disconnect(): void {
    console.log('Mock SSE Manager: Disconnected');
  }

  // Method to simulate receiving events for testing
  simulateEvent(event: AnySSEEvent): void {
    const listeners = this.listeners.get('*') || [];
    listeners.forEach((listener) => listener(event));
  }
}

// Mock SSE Context
const mockSSEManager = new MockSSEManager();
const mockSSEContext = {
  manager: mockSSEManager,
  isConnected: true,
};

// Override the useSSE hook for testing
React.createContext = () =>
  ({
    $$typeof: Symbol.for('react.context'),
    Provider: Object.assign(
      ({ children }: { children: React.ReactNode }) => children,
      { $$typeof: Symbol.for('react.provider') }
    ),
    Consumer: Object.assign(() => null, {
      $$typeof: Symbol.for('react.consumer'),
    }),
    displayName: 'MockContext',
  }) as any;

// Mock the useSSE hook
const useSSE = () => mockSSEContext;

const SSEMonitorDemo: React.FC = () => {
  const [eventCount, setEventCount] = useState(0);

  const generateTestEvent = () => {
    const eventTypes = [
      'job.started',
      'job.completed',
      'document.uploaded',
      'system.alert',
      'backup.progress',
    ];
    const categories = ['workflow', 'security', 'monitoring', 'analytics'];
    const priorities = ['low', 'normal', 'high', 'critical'];
    const userIds = ['user-123', 'user-456', 'admin-789'];
    const sourceSystems = ['api-service', 'worker-service', 'backup-service'];

    const randomChoice = <T,>(arr: T[]): T =>
      arr[Math.floor(Math.random() * arr.length)];

    const event: AnySSEEvent = {
      id: `event-${Date.now()}-${eventCount}`,
      type: randomChoice(eventTypes),
      data: {
        message: `Test event ${eventCount + 1}`,
        details: `This is a simulated event for testing purposes`,
        timestamp: new Date().toISOString(),
      },
      timestamp: new Date().toISOString(),
      user_id: Math.random() > 0.3 ? randomChoice(userIds) : undefined,
      metadata: {
        category: randomChoice(categories),
        priority: randomChoice(priorities),
        source_system: randomChoice(sourceSystems),
        correlation_id: `corr-${Math.random().toString(36).substring(7)}`,
      },
    } as unknown as AnySSEEvent;

    mockSSEManager.simulateEvent(event);
    setEventCount((prev) => prev + 1);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h3" gutterBottom>
        SSE Monitor Demo
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        This demo shows the enhanced SSE Monitor with multiple filter types and
        settings persistence.
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Button variant="contained" onClick={generateTestEvent} sx={{ mr: 2 }}>
          Generate Test Event ({eventCount} sent)
        </Button>
        <Button
          variant="outlined"
          onClick={() => {
            for (let i = 0; i < 5; i++) {
              setTimeout(() => generateTestEvent(), i * 200);
            }
          }}
        >
          Generate 5 Events
        </Button>
      </Box>

      {/* Inject the mock context and render SSE Monitor */}
      <SSEMonitorPage />
    </Box>
  );
};

export default SSEMonitorDemo;
