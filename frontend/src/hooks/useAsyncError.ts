import { useCallback } from 'react';
import {
  errorHandler,
  ErrorContext,
  ErrorHandlerOptions,
} from '../utils/error-handler';

/**
 * Hook for handling async errors in useEffect and other async operations
 * Provides a standardized way to handle errors outside of the useApi hook
 */
export function useAsyncError() {
  /**
   * Handle an async error with standardized error processing
   */
  const handleAsyncError = useCallback(
    (error: unknown, context: ErrorContext, options?: ErrorHandlerOptions) => {
      errorHandler.handleError(error, context, options);
    },
    []
  );

  /**
   * Wrap an async function to automatically handle errors
   */
  const wrapAsyncFunction = useCallback(
    <T extends (...args: unknown[]) => Promise<unknown>>(
      fn: T,
      context: ErrorContext,
      options?: ErrorHandlerOptions
    ): T => {
      return (async (...args: Parameters<T>) => {
        try {
          return await fn(...args);
        } catch (error) {
          handleAsyncError(error, context, options);
          // Don't rethrow by default for useEffect scenarios
          throw error;
        }
      }) as T;
    },
    [handleAsyncError]
  );

  /**
   * Create a safe async function that won't throw errors
   * Instead, it returns an object with success/error information
   */
  const createSafeAsyncFunction = useCallback(
    <T extends (...args: unknown[]) => Promise<unknown>>(
      fn: T,
      context: ErrorContext,
      options?: ErrorHandlerOptions
    ) => {
      return async (
        ...args: Parameters<T>
      ): Promise<{
        success: boolean;
        data?: Awaited<ReturnType<T>>;
        error?: string;
      }> => {
        try {
          const data = await fn(...args);
          return { success: true, data };
        } catch (error) {
          handleAsyncError(error, context, options);
          const errorMessage =
            error instanceof Error ? error.message : 'An error occurred';
          return { success: false, error: errorMessage };
        }
      };
    },
    [handleAsyncError]
  );

  /**
   * Execute an async operation with error handling
   * Useful for one-off async operations in event handlers
   */
  const executeAsync = useCallback(
    async <T>(
      asyncOperation: () => Promise<T>,
      context: ErrorContext,
      options?: ErrorHandlerOptions
    ): Promise<{ success: boolean; data?: T; error?: string }> => {
      try {
        const data = await asyncOperation();
        return { success: true, data };
      } catch (error) {
        handleAsyncError(error, context, options);
        const errorMessage =
          error instanceof Error ? error.message : 'An error occurred';
        return { success: false, error: errorMessage };
      }
    },
    [handleAsyncError]
  );

  return {
    handleAsyncError,
    wrapAsyncFunction,
    createSafeAsyncFunction,
    executeAsync,
  };
}

/**
 * Hook for managing async operations with loading and error states
 * Similar to useApi but for custom async operations
 */
export function useAsyncOperation<T = unknown>() {
  const { handleAsyncError, executeAsync } = useAsyncError();

  /**
   * Execute an async operation with automatic state management
   * Returns a function that can be called to trigger the operation
   */
  const createAsyncOperation = useCallback(
    (
      asyncOperation: () => Promise<T>,
      context: ErrorContext,
      options?: ErrorHandlerOptions & {
        onSuccess?: (data: T) => void;
        onError?: (error: string) => void;
      }
    ) => {
      return async (): Promise<{
        success: boolean;
        data?: T;
        error?: string;
      }> => {
        const result = await executeAsync(asyncOperation, context, options);

        if (result.success && result.data !== undefined) {
          options?.onSuccess?.(result.data);
        } else if (!result.success && result.error) {
          options?.onError?.(result.error);
        }

        return result;
      };
    },
    [executeAsync]
  );

  return {
    handleAsyncError,
    executeAsync,
    createAsyncOperation,
  };
}
