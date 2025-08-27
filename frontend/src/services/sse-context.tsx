/**
 * SSE Context Provider
 * 
 * Provides SSE event manager to React components via context
 */

import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback, useMemo } from 'react';
import { sseEventManager } from './sse-manager';
import { AnySSEEvent, SSEEventListener } from './sse-types';
import { chatterSDK } from './chatter-sdk';

interface SSEContextValue {
  isConnected: boolean;
  connectionState: 'connecting' | 'open' | 'closed';
  connect: () => void;
  disconnect: () => void;
  on: (eventType: AnySSEEvent['type'] | '*', listener: SSEEventListener) => () => void;
  off: (eventType: AnySSEEvent['type'] | '*', listener: SSEEventListener) => void;
}

const SSEContext = createContext<SSEContextValue | null>(null);

interface SSEProviderProps {
  children: ReactNode;
  autoConnect?: boolean;
}

export const SSEProvider: React.FC<SSEProviderProps> = ({ children, autoConnect = true }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<'connecting' | 'open' | 'closed'>('closed');

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

  // Auto-connect when authenticated
  useEffect(() => {
    if (autoConnect && chatterSDK.isAuthenticated() && !isConnected) {
      sseEventManager.connect();
    }
  }, [autoConnect, isConnected]);

  const connect = useCallback(() => {
    sseEventManager.connect();
  }, []);

  const disconnect = useCallback(() => {
    sseEventManager.disconnect();
  }, []);

  const on = useCallback((eventType: AnySSEEvent['type'] | '*', listener: SSEEventListener) => {
    return sseEventManager.on(eventType, listener);
  }, []);

  const off = useCallback((eventType: AnySSEEvent['type'] | '*', listener: SSEEventListener) => {
    sseEventManager.off(eventType, listener);
  }, []);

  const value: SSEContextValue = useMemo(() => ({
    isConnected,
    connectionState,
    connect,
    disconnect,
    on,
    off,
  }), [isConnected, connectionState, connect, disconnect, on, off]);

  return (
    <SSEContext.Provider value={value}>
      {children}
    </SSEContext.Provider>
  );
};

export const useSSE = (): SSEContextValue => {
  const context = useContext(SSEContext);
  if (!context) {
    throw new Error('useSSE must be used within an SSEProvider');
  }
  return context;
};

export default SSEProvider;
