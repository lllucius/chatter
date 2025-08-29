import React, { useState, useEffect } from 'react';

interface UseErrorHandlerOptions {
  onError?: (error: Error) => void;
  resetOnDependencyChange?: boolean;
}

/**
 * Hook for handling errors in functional components
 * Works with the ErrorBoundary component to provide comprehensive error handling
 */
export function useErrorHandler(
  dependencies: unknown[] = [],
  options: UseErrorHandlerOptions = {}
) {
  const [error, setError] = useState<Error | null>(null);
  const { onError, resetOnDependencyChange = true } = options;

  // Reset error when dependencies change
  useEffect(() => {
    if (resetOnDependencyChange && error) {
      setError(null);
    }
  }, dependencies);

  // Call onError callback when error changes
  useEffect(() => {
    if (error && onError) {
      onError(error);
    }
  }, [error, onError]);

  // Throw error to be caught by ErrorBoundary
  if (error) {
    throw error;
  }

  const captureError = (error: Error | string) => {
    const errorObj = typeof error === 'string' ? new Error(error) : error;
    setError(errorObj);
  };

  const resetError = () => {
    setError(null);
  };

  return {
    captureError,
    resetError,
    hasError: !!error,
  };
}

/**
 * HOC that wraps a component with error handling
 */
export function withErrorHandler<P extends object>(
  Component: React.ComponentType<P>,
  fallbackComponent?: React.ComponentType
) {
  return function WithErrorHandlerComponent(props: P) {
    const { captureError } = useErrorHandler();

    try {
      return <Component {...props} />;
    } catch (error) {
      captureError(error as Error);
      
      if (fallbackComponent) {
        const FallbackComponent = fallbackComponent;
        return <FallbackComponent />;
      }
      
      return null;
    }
  };
}

/**
 * Async error handler for promises and async operations
 */
export function useAsyncErrorHandler() {
  const { captureError } = useErrorHandler();

  const handleAsyncError = <T,>(promise: Promise<T>): Promise<T> => {
    return promise.catch((error) => {
      captureError(error);
      throw error; // Re-throw to maintain promise chain behavior
    });
  };

  return { handleAsyncError };
}