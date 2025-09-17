/**
 * SSE Context Provider
 *
 * Provides SSE event manager to React components via context
 */

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
  useCallback,
  useMemo,
} from 'react';
import { sseEventManager } from './sse-manager';
import { AnySSEEvent, SSEEventListener } from './sse-types';
import { authService } from '../services/auth-service';

interface SSEContextValue {
  manager: typeof sseEventManager;
  isConnected: boolean;
  connectionState: 'connecting' | 'open' | 'closed';
  connect: () => void;
  disconnect: () => void;
  on: (
    eventType: AnySSEEvent['type'] | '*',
    listener: SSEEventListener
  ) => () => void;
  off: (
    eventType: AnySSEEvent['type'] | '*',
    listener: SSEEventListener
  ) => void;
  onCategory: (category: string, listener: SSEEventListener) => () => void;
  offCategory: (category: string, listener: SSEEventListener) => void;
  onHighPriority: (listener: SSEEventListener) => () => void;
  requestNotificationPermission: () => Promise<boolean>;
  getConnectionStats: () => Record<string, unknown>;
}

const SSEContext = createContext<SSEContextValue | null>(null);

interface SSEProviderProps {
  children: ReactNode;
  autoConnect?: boolean;
}

export const SSEProvider: React.FC<SSEProviderProps> = ({
  children,
  autoConnect = true,
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<
    'connecting' | 'open' | 'closed'
  >('closed');

  // Monitor connection state
  useEffect(() => {
    const updateConnectionState = () => {
      setIsConnected(sseEventManager.connected);
      setConnectionState(sseEventManager.getConnectionState());
    };

    // Check initial state
    updateConnectionState();

    // Listen for connection events to update state
    const unsubscribe = sseEventManager.on('connection.established', () => {
      updateConnectionState();
    });

    // Poll connection state periodically as backup
    const intervalId = setInterval(updateConnectionState, 5000);

    return () => {
      unsubscribe();
      clearInterval(intervalId);
    };
  }, []);

  // Auto-connect when authenticated and monitor connection state changes
  useEffect(() => {
    if (autoConnect && authService.isAuthenticated()) {
      // Always try to connect if authenticated, regardless of current state
      if (!isConnected && sseEventManager.getConnectionState() === 'closed') {
        console.log('Auto-connecting SSE...');
        sseEventManager.connect();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoConnect]); // Removed isConnected dependency to prevent unnecessary reconnections

  const connect = useCallback(() => {
    sseEventManager.connect();
  }, []);

  const disconnect = useCallback(() => {
    sseEventManager.disconnect();
  }, []);

  const on = useCallback(
    (eventType: AnySSEEvent['type'] | '*', listener: SSEEventListener) => {
      return sseEventManager.on(eventType, listener);
    },
    []
  );

  const off = useCallback(
    (eventType: AnySSEEvent['type'] | '*', listener: SSEEventListener) => {
      sseEventManager.off(eventType, listener);
    },
    []
  );

  const onCategory = useCallback(
    (category: string, listener: SSEEventListener) => {
      return sseEventManager.onCategory(category, listener);
    },
    []
  );

  const offCategory = useCallback(
    (category: string, listener: SSEEventListener) => {
      sseEventManager.offCategory(category, listener);
    },
    []
  );

  const onHighPriority = useCallback((listener: SSEEventListener) => {
    return sseEventManager.onHighPriority(listener);
  }, []);

  const requestNotificationPermission = useCallback(() => {
    return sseEventManager.requestNotificationPermission();
  }, []);

  const getConnectionStats = useCallback(() => {
    return sseEventManager.getConnectionStats();
  }, []);

  const value: SSEContextValue = useMemo(
    () => ({
      manager: sseEventManager,
      isConnected,
      connectionState,
      connect,
      disconnect,
      on,
      off,
      onCategory,
      offCategory,
      onHighPriority,
      requestNotificationPermission,
      getConnectionStats,
    }),
    [
      isConnected,
      connectionState,
      connect,
      disconnect,
      on,
      off,
      onCategory,
      offCategory,
      onHighPriority,
      requestNotificationPermission,
      getConnectionStats,
    ]
  );

  return <SSEContext.Provider value={value}>{children}</SSEContext.Provider>;
};

export const useSSE = (): SSEContextValue => {
  const context = useContext(SSEContext);
  if (!context) {
    throw new Error('useSSE must be used within an SSEProvider');
  }
  return context;
};

export default SSEProvider;
