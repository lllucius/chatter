import { useState, useEffect, useCallback } from 'react';
import { errorHandler } from '../utils/error-handler';
import { toastService } from '../services/toast-service';

interface NetworkStatus {
  isOnline: boolean;
  isConnected: boolean;
  lastConnectedAt?: Date;
  lastDisconnectedAt?: Date;
}

interface UseNetworkOptions {
  onOnline?: () => void;
  onOffline?: () => void;
  pingInterval?: number; // Interval to check connectivity in ms
  pingUrl?: string; // URL to ping for connectivity check
  showToasts?: boolean; // Whether to show toast notifications
}

/**
 * Hook for monitoring network connectivity and handling network-related errors
 */
export function useNetwork(options: UseNetworkOptions = {}) {
  const {
    onOnline,
    onOffline,
    pingInterval = 30000, // 30 seconds
    pingUrl = '/api/health', // Default health check endpoint
    showToasts = true
  } = options;

  const [status, setStatus] = useState<NetworkStatus>({
    isOnline: navigator.onLine,
    isConnected: navigator.onLine,
  });

  /**
   * Check connectivity by attempting to fetch a resource
   */
  const checkConnectivity = useCallback(async (): Promise<boolean> => {
    try {
      // Use a small timeout and no-cache to ensure fresh check
      const response = await fetch(pingUrl, {
        method: 'HEAD',
        cache: 'no-cache',
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });
      return response.ok;
    } catch (error) {
      // Log connectivity check failure but don't show toast for routine checks
      errorHandler.handleError(error, {
        source: 'useNetwork.checkConnectivity',
        operation: 'Network connectivity check',
        additionalData: {
          pingUrl,
          navigatorOnLine: navigator.onLine
        }
      }, {
        showToast: false,
        logToConsole: false // Don't log routine connectivity checks
      });
      return false;
    }
  }, [pingUrl]);

  /**
   * Handle online/offline state changes
   */
  const handleOnline = useCallback(() => {
    const now = new Date();
    setStatus(prev => ({
      ...prev,
      isOnline: true,
      isConnected: true,
      lastConnectedAt: now
    }));

    if (showToasts) {
      toastService.success('Connection restored', { autoClose: 3000 });
    }

    onOnline?.();
  }, [onOnline, showToasts]);

  const handleOffline = useCallback(() => {
    const now = new Date();
    setStatus(prev => ({
      ...prev,
      isOnline: false,
      isConnected: false,
      lastDisconnectedAt: now
    }));

    if (showToasts) {
      toastService.warning('Connection lost. Some features may not work properly.', {
        autoClose: false
      });
    }

    errorHandler.handleError(
      new Error('Network connection lost'),
      {
        source: 'useNetwork.handleOffline',
        operation: 'Network status monitoring'
      },
      {
        showToast: false, // Already showing toast above
        logToConsole: true
      }
    );

    onOffline?.();
  }, [onOffline, showToasts]);

  /**
   * Periodically check connectivity
   */
  const performConnectivityCheck = useCallback(async () => {
    const isConnected = await checkConnectivity();
    const wasConnected = status.isConnected;

    if (isConnected !== wasConnected) {
      const now = new Date();
      setStatus(prev => ({
        ...prev,
        isConnected,
        ...(isConnected 
          ? { lastConnectedAt: now }
          : { lastDisconnectedAt: now }
        )
      }));

      if (isConnected && !wasConnected) {
        // Regained connectivity
        if (showToasts) {
          toastService.success('Server connection restored', { autoClose: 3000 });
        }
        onOnline?.();
      } else if (!isConnected && wasConnected) {
        // Lost connectivity
        if (showToasts) {
          toastService.warning('Cannot reach server. Please check your connection.', {
            autoClose: false
          });
        }
        onOffline?.();
      }
    }
  }, [checkConnectivity, status.isConnected, showToasts, onOnline, onOffline]);

  /**
   * Set up event listeners and periodic checks
   */
  useEffect(() => {
    // Listen for browser online/offline events
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Set up periodic connectivity checks
    const intervalId = setInterval(performConnectivityCheck, pingInterval);

    // Perform initial connectivity check
    performConnectivityCheck();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(intervalId);
    };
  }, [handleOnline, handleOffline, performConnectivityCheck, pingInterval]);

  /**
   * Manually trigger a connectivity check
   */
  const refreshConnectivity = useCallback(async () => {
    await performConnectivityCheck();
  }, [performConnectivityCheck]);

  /**
   * Handle network-related errors with appropriate user feedback
   */
  const handleNetworkError = useCallback((error: unknown, context: string) => {
    const isNetworkError = 
      error instanceof TypeError && error.message.includes('fetch') ||
      error instanceof Error && (
        error.message.includes('network') ||
        error.message.includes('timeout') ||
        error.message.includes('offline')
      );

    if (isNetworkError) {
      errorHandler.handleError(error, {
        source: 'useNetwork.handleNetworkError',
        operation: context,
        additionalData: {
          isOnline: status.isOnline,
          isConnected: status.isConnected,
          lastConnectedAt: status.lastConnectedAt,
          lastDisconnectedAt: status.lastDisconnectedAt
        }
      }, {
        showToast: true,
        logToConsole: true,
        fallbackMessage: 'Network error occurred. Please check your connection and try again.'
      });
    } else {
      // Re-throw non-network errors
      throw error;
    }
  }, [status]);

  return {
    status,
    isOnline: status.isOnline,
    isConnected: status.isConnected,
    refreshConnectivity,
    handleNetworkError,
    checkConnectivity,
  };
}

/**
 * Higher-order function to wrap API calls with network error handling
 */
export function withNetworkErrorHandling<T extends (...args: unknown[]) => Promise<unknown>>(
  fn: T,
  context: string
): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await fn(...args);
    } catch (error) {
      // Check if it's a network-related error
      const isNetworkError = 
        error instanceof TypeError && error.message.includes('fetch') ||
        error instanceof Error && (
          error.message.includes('network') ||
          error.message.includes('timeout') ||
          error.message.includes('ERR_NETWORK') ||
          error.message.includes('ERR_INTERNET_DISCONNECTED')
        );

      if (isNetworkError) {
        errorHandler.handleError(error, {
          source: 'withNetworkErrorHandling',
          operation: context,
          additionalData: {
            isOnline: navigator.onLine,
            userAgent: navigator.userAgent
          }
        }, {
          showToast: true,
          logToConsole: true,
          fallbackMessage: 'Network error occurred. Please check your connection and try again.'
        });
      }

      // Re-throw the error so it can be handled by the calling code
      throw error;
    }
  }) as T;
}