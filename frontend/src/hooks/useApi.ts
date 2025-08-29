import { useState, useEffect, useCallback, useRef } from 'react';
import { useErrorHandler } from './useErrorHandler';

interface UseApiOptions<T> {
  immediate?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  retryAttempts?: number;
  retryDelay?: number;
  cacheKey?: string;
  cacheTime?: number; // in milliseconds
}

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string;
  execute: () => Promise<void>;
  reset: () => void;
  retry: () => Promise<void>;
  retryCount: number;
}

// Simple in-memory cache
const apiCache = new Map<string, { data: any; timestamp: number; ttl: number }>();

/**
 * Enhanced custom hook for handling API calls with loading, error states, caching, and retry logic
 */
export function useApi<T>(
  apiCall: () => Promise<T>,
  options: UseApiOptions<T> = {}
): UseApiReturn<T> {
  const { 
    immediate = false, 
    onSuccess, 
    onError,
    retryAttempts = 3,
    retryDelay = 1000,
    cacheKey,
    cacheTime = 5 * 60 * 1000, // 5 minutes default
  } = options;
  
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [retryCount, setRetryCount] = useState(0);
  
  const { captureError } = useErrorHandler();
  const abortControllerRef = useRef<AbortController | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const executeWithRetry = useCallback(async (attempt = 0): Promise<void> => {
    try {
      setLoading(true);
      setError('');

      // Check cache first
      if (cacheKey) {
        const cached = apiCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < cached.ttl) {
          setData(cached.data);
          setLoading(false);
          onSuccess?.(cached.data);
          return;
        }
      }

      // Create new abort controller for this request
      abortControllerRef.current = new AbortController();
      
      const result = await apiCall();
      
      if (!mountedRef.current) return;

      setData(result);
      setRetryCount(0);
      onSuccess?.(result);

      // Cache the result
      if (cacheKey) {
        apiCache.set(cacheKey, {
          data: result,
          timestamp: Date.now(),
          ttl: cacheTime,
        });
      }

    } catch (err: any) {
      if (!mountedRef.current) return;

      const errorMessage = err.message || 'An error occurred';
      
      // Check if we should retry
      if (attempt < retryAttempts && !err.name?.includes('Abort')) {
        setRetryCount(attempt + 1);
        setTimeout(() => {
          if (mountedRef.current) {
            executeWithRetry(attempt + 1);
          }
        }, retryDelay * Math.pow(2, attempt)); // Exponential backoff
        return;
      }

      setError(errorMessage);
      setRetryCount(attempt);
      onError?.(err);
      
      // Only capture error for error boundary if it's not a network/abort error
      if (!err.name?.includes('Abort') && !err.name?.includes('Network')) {
        captureError(err);
      }
      
      console.error('API call failed:', err);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [apiCall, onSuccess, onError, retryAttempts, retryDelay, cacheKey, cacheTime, captureError]);

  const execute = useCallback(async () => {
    await executeWithRetry(0);
  }, [executeWithRetry]);

  const retry = useCallback(async () => {
    await executeWithRetry(retryCount);
  }, [executeWithRetry, retryCount]);

  const reset = useCallback(() => {
    setData(null);
    setError('');
    setLoading(false);
    setRetryCount(0);
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    data,
    loading,
    error,
    execute,
    reset,
    retry,
    retryCount,
  };
}

/**
 * Custom hook for managing lists with common operations
 */
export function useApiList<T extends { id: string | number }>(
  fetchApiCall: () => Promise<T[]>,
  options: UseApiOptions<T[]> = {}
) {
  const api = useApi(fetchApiCall, options);

  const addItem = useCallback((newItem: T) => {
    if (api.data) {
      const updatedData = [...api.data, newItem];
      // Update both cache and state
      if (options.cacheKey) {
        apiCache.set(options.cacheKey, {
          data: updatedData,
          timestamp: Date.now(),
          ttl: options.cacheTime || 5 * 60 * 1000,
        });
      }
      // Force update data - we'd need to expose setData for this to work
      // For now, recommend calling execute() after mutations
    }
  }, [api.data, options.cacheKey, options.cacheTime]);

  const removeItem = useCallback((id: string | number) => {
    if (api.data) {
      const updatedData = api.data.filter(item => item.id !== id);
      // Update cache
      if (options.cacheKey) {
        apiCache.set(options.cacheKey, {
          data: updatedData,
          timestamp: Date.now(),
          ttl: options.cacheTime || 5 * 60 * 1000,
        });
      }
    }
  }, [api.data, options.cacheKey, options.cacheTime]);

  const updateItem = useCallback((id: string | number, updates: Partial<T>) => {
    if (api.data) {
      const updatedData = api.data.map(item => 
        item.id === id ? { ...item, ...updates } : item
      );
      // Update cache
      if (options.cacheKey) {
        apiCache.set(options.cacheKey, {
          data: updatedData,
          timestamp: Date.now(),
          ttl: options.cacheTime || 5 * 60 * 1000,
        });
      }
    }
  }, [api.data, options.cacheKey, options.cacheTime]);

  return {
    ...api,
    items: api.data || [],
    addItem,
    removeItem,
    updateItem,
  };
}

/**
 * Hook for debounced API calls (useful for search)
 */
export function useDebouncedApi<T>(
  apiCall: (query: string) => Promise<T>,
  delay: number = 300,
  options: UseApiOptions<T> = {}
) {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      setDebouncedQuery(query);
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [query, delay]);

  const debouncedApiCall = useCallback(() => {
    return debouncedQuery ? apiCall(debouncedQuery) : Promise.resolve(null as T);
  }, [apiCall, debouncedQuery]);

  const api = useApi(debouncedApiCall, {
    ...options,
    immediate: false,
  });

  useEffect(() => {
    if (debouncedQuery) {
      api.execute();
    }
  }, [debouncedQuery, api.execute]);

  return {
    ...api,
    query,
    setQuery,
    debouncedQuery,
  };
}

/**
 * Clear the API cache
 */
export function clearApiCache(key?: string) {
  if (key) {
    apiCache.delete(key);
  } else {
    apiCache.clear();
  }
}