import React from 'react';
import { render, renderHook, waitFor, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from "vitest";
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
    await new Promise((resolve) => setTimeout(resolve, 100));

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
    await new Promise((resolve) => setTimeout(resolve, 100));

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

    // Manually execute wrapped in act
    await act(async () => {
      await result.current.execute();
    });

    // Wait for the async operation to complete
    await waitFor(() => {
      expect(result.current.data).not.toBe(null);
    });

    // Should have made 1 call
    expect(getCallCount()).toBe(1);
    expect(result.current.data).toEqual({ data: 'result-1' });
    expect(result.current.loading).toBe(false);
  });

  it('should not cause infinite loop with anonymous function and immediate=true', async () => {
    // Track API calls
    let callCount = 0;
    const TestComponent = () => {
      // This simulates the DashboardPage pattern with anonymous function
      const api = useApi(
        () => {
          callCount++;
          return Promise.resolve({ data: `result-${callCount}` });
        },
        { immediate: true }
      );

      return <div>{api.data?.data || 'loading'}</div>;
    };

    await act(async () => {
      render(<TestComponent />);
    });

    // Wait for initial call and any potential loop
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 500));
    });

    // Should only make 1 call, not loop infinitely
    expect(callCount).toBe(1);
  });

  it('should handle DashboardPage-like component pattern correctly', async () => {
    // Simulate the exact pattern from DashboardPage
    let callCount = 0;
    const mockSDK = {
      analytics: {
        getDashboardApiV1AnalyticsDashboard: () => {
          callCount++;
          return Promise.resolve({
            data: {
              conversation_stats: { total_conversations: callCount },
              usage_metrics: { total_tokens: callCount * 100 },
              document_analytics: { total_documents: callCount * 5 },
              system_health: { active_users_today: callCount * 2 },
              performance_metrics: { avg_response_time_ms: 200 },
            },
          });
        },
      },
    };

    const MockDashboardPage = () => {
      // Exact pattern from DashboardPage.tsx line 122-125
      const dashboardApi = useApi(
        () => mockSDK.analytics.getDashboardApiV1AnalyticsDashboard(),
        { immediate: true }
      );

      return (
        <div>
          {dashboardApi.loading && <div>Loading...</div>}
          {dashboardApi.data && (
            <div>
              Conversations:{' '}
              {dashboardApi.data.data.conversation_stats.total_conversations}
            </div>
          )}
        </div>
      );
    };

    await act(async () => {
      render(<MockDashboardPage />);
    });

    // Wait for the component to settle
    await waitFor(
      () => {
        expect(callCount).toBe(1);
      },
      { timeout: 1000 }
    );

    // Wait additional time to ensure no more calls are made
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 500));
    });

    // Should still only be 1 call
    expect(callCount).toBe(1);
  });
});
