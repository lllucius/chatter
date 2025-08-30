import { useMemo, useTransition } from 'react';

/**
 * Hook for managing concurrent updates with React 19's improved startTransition
 * Provides better user experience during heavy operations
 */
export function useConcurrentUpdate() {
  const [isPending, startTransition] = useTransition();

  const startConcurrentUpdate = (callback: () => void) => {
    startTransition(() => {
      callback();
    });
  };

  return {
    isPending,
    startConcurrentUpdate,
  };
}

/**
 * Modern data fetching hook optimized for React 19's concurrent rendering
 * Uses transitions for better perceived performance
 */
export function useConcurrentData<T>(
  fetcher: () => Promise<T>,
  deps: React.DependencyList = []
) {
  const { isPending, startConcurrentUpdate } = useConcurrentUpdate();

  const promise = useMemo(() => {
    return fetcher();
  }, [fetcher, ...deps]);

  // Return promise for Suspense integration
  return { promise, isPending, startConcurrentUpdate };
}

/**
 * Hook for optimizing expensive computations with React 19's concurrent features
 */
export function useConcurrentMemo<T>(
  factory: () => T,
  deps: React.DependencyList
): T {
  return useMemo(() => {
    // In React 19, this computation can be interrupted and resumed
    return factory();
  }, [factory, ...deps]);
}