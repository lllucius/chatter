import { useState, useEffect, useCallback } from 'react';

interface UseApiOptions<T> {
  immediate?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string;
  execute: () => Promise<void>;
  reset: () => void;
}

/**
 * Custom hook for handling API calls with loading, error states, and data management
 */
export function useApi<T>(
  apiCall: () => Promise<T>,
  options: UseApiOptions<T> = {}
): UseApiReturn<T> {
  const { immediate = false, onSuccess, onError } = options;
  
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const result = await apiCall();
      setData(result);
      onSuccess?.(result);
    } catch (err: any) {
      const errorMessage = err.message || 'An error occurred';
      setError(errorMessage);
      onError?.(err);
      console.error('API call failed:', err);
    } finally {
      setLoading(false);
    }
  }, [apiCall, onSuccess, onError]);

  const reset = useCallback(() => {
    setData(null);
    setError('');
    setLoading(false);
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
  };
}

/**
 * Custom hook for managing lists with common operations
 */
export function useApiList<T>(
  fetchApiCall: () => Promise<T[]>,
  options: UseApiOptions<T[]> = {}
) {
  const api = useApi(fetchApiCall, options);
  
  const addItem = useCallback((item: T) => {
    if (api.data) {
      api.data.push(item);
    }
  }, [api.data]);

  const removeItem = useCallback((predicate: (item: T) => boolean) => {
    if (api.data) {
      const index = api.data.findIndex(predicate);
      if (index !== -1) {
        api.data.splice(index, 1);
      }
    }
  }, [api.data]);

  const updateItem = useCallback((predicate: (item: T) => boolean, updater: (item: T) => T) => {
    if (api.data) {
      const index = api.data.findIndex(predicate);
      if (index !== -1) {
        api.data[index] = updater(api.data[index]);
      }
    }
  }, []);

  return {
    ...api,
    items: api.data || [],
    addItem,
    removeItem,
    updateItem,
  };
}