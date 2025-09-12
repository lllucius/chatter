import { useState, useEffect, useCallback, useRef } from 'react';

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
  
  // Use refs to store the current values to avoid dependency issues
  const apiCallRef = useRef(apiCall);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  
  // Update refs when values change
  apiCallRef.current = apiCall;
  onSuccessRef.current = onSuccess;
  onErrorRef.current = onError;

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const result = await apiCallRef.current();
      setData(result);
      onSuccessRef.current?.(result);
    } catch (err: any) {
      const errorMessage = err.message || 'An error occurred';
      setError(errorMessage);
      onErrorRef.current?.(err);
      // Log error for debugging in development
      if (process.env.NODE_ENV === 'development') {
         
        console.error('API call failed:', err);
      }
    } finally {
      setLoading(false);
    }
  }, []); // No dependencies since we use refs

  const reset = useCallback(() => {
    setData(null);
    setError('');
    setLoading(false);
  }, []);

  // Use a ref to track if the immediate call has been made
  const immediateCalledRef = useRef(false);

  useEffect(() => {
    if (immediate && !immediateCalledRef.current) {
      immediateCalledRef.current = true;
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
  }, [api.data]);

  return {
    ...api,
    items: api.data || [],
    addItem,
    removeItem,
    updateItem,
  };
}