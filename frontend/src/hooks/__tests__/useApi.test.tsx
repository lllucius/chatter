import React from 'react';
import { render, renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useApi } from '../useApi';

// Mock API function that tracks how many times it's called
const createMockApiCall = () => {
  let callCount = 0;
  const mockApiCall = vi.fn(() => {
    callCount++;
    return Promise.resolve({ data: `result-${callCount}` });
  });
  
  return { mockApiCall, getCallCount: () => callCount };
};

describe('useApi hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should not make repeated calls when immediate is true', async () => {
    const { mockApiCall, getCallCount } = createMockApiCall();
    
    const { result, rerender } = renderHook(() => 
      useApi(mockApiCall, { immediate: true })
    );

    // Wait for initial call
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Initial call should have been made
    expect(getCallCount()).toBe(1);
    expect(result.current.data).toEqual({ data: 'result-1' });

    // Re-render the hook (simulating component re-render)
    rerender();
    rerender();
    rerender();

    // Wait a bit to ensure no additional calls are made
    await new Promise(resolve => setTimeout(resolve, 100));

    // Should still only be 1 call despite multiple re-renders
    expect(getCallCount()).toBe(1);
    expect(mockApiCall).toHaveBeenCalledTimes(1);
  });

  it('should not make initial call when immediate is false', async () => {
    const { mockApiCall, getCallCount } = createMockApiCall();
    
    const { result } = renderHook(() => 
      useApi(mockApiCall, { immediate: false })
    );

    // Wait a bit
    await new Promise(resolve => setTimeout(resolve, 100));

    // No call should have been made
    expect(getCallCount()).toBe(0);
    expect(result.current.data).toBe(null);
    expect(result.current.loading).toBe(false);
  });

  it('should make call when execute is called manually', async () => {
    const { mockApiCall, getCallCount } = createMockApiCall();
    
    const { result } = renderHook(() => 
      useApi(mockApiCall, { immediate: false })
    );

    // Manually execute
    await result.current.execute();

    // Wait for the async operation to complete
    await waitFor(() => {
      expect(result.current.data).not.toBe(null);
    });

    // Should have made 1 call
    expect(getCallCount()).toBe(1);
    expect(result.current.data).toEqual({ data: 'result-1' });
    expect(result.current.loading).toBe(false);
  });
});