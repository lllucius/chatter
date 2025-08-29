import React, { memo, useCallback, useMemo } from 'react';

/**
 * HOC for memoizing components with deep comparison options
 */
export function withMemo<P extends object>(
  Component: React.ComponentType<P>,
  areEqual?: (prevProps: P, nextProps: P) => boolean
) {
  return memo(Component, areEqual);
}

/**
 * Helper for creating stable callback references
 */
export function useStableCallback<T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList
): T {
  return useCallback(callback, deps);
}

/**
 * Helper for creating stable object references
 */
export function useStableObject<T extends object>(
  factory: () => T,
  deps: React.DependencyList
): T {
  return useMemo(factory, deps);
}

/**
 * Custom comparison function for props with nested objects
 */
export function shallowEqual<T extends object>(obj1: T, obj2: T): boolean {
  const keys1 = Object.keys(obj1) as (keyof T)[];
  const keys2 = Object.keys(obj2) as (keyof T)[];

  if (keys1.length !== keys2.length) {
    return false;
  }

  for (const key of keys1) {
    if (obj1[key] !== obj2[key]) {
      return false;
    }
  }

  return true;
}

/**
 * Performance-optimized list item component
 */
interface OptimizedListItemProps {
  id: string | number;
  children: React.ReactNode;
  onClick?: (id: string | number) => void;
  className?: string;
}

export const OptimizedListItem = memo<OptimizedListItemProps>(({ 
  id, 
  children, 
  onClick, 
  className 
}) => {
  const handleClick = useCallback(() => {
    onClick?.(id);
  }, [onClick, id]);

  return (
    <div className={className} onClick={handleClick}>
      {children}
    </div>
  );
}, (prevProps, nextProps) => {
  return (
    prevProps.id === nextProps.id &&
    prevProps.className === nextProps.className &&
    prevProps.onClick === nextProps.onClick
  );
});

OptimizedListItem.displayName = 'OptimizedListItem';

/**
 * Hook for debouncing values to reduce unnecessary re-renders
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);

  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Hook for throttling function calls
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const lastRun = React.useRef(Date.now());

  return useCallback(
    ((...args) => {
      if (Date.now() - lastRun.current >= delay) {
        callback(...args);
        lastRun.current = Date.now();
      }
    }) as T,
    [callback, delay]
  );
}

/**
 * Hook for managing expensive computations
 */
export function useExpensiveComputation<T>(
  computeFn: () => T,
  deps: React.DependencyList,
  shouldCompute: boolean = true
): T | null {
  return useMemo(() => {
    if (!shouldCompute) return null;
    return computeFn();
  }, [...deps, shouldCompute]);
}