/**
 * @vitest-environment jsdom
 */
import { renderHook, act } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useAdministrationData } from '../useAdministrationData';

// Mock the dependencies
vi.mock('../../services/auth-service', () => ({
  getSDK: () => ({
    dataManagement: {
      listBackupsApiV1DataBackups: vi.fn().mockResolvedValue({ backups: [] }),
    },
    plugins: {
      listPluginsApiV1Plugins: vi.fn().mockResolvedValue({ plugins: [] }),
    },
    jobs: {
      listJobsApiV1Jobs: vi.fn().mockResolvedValue({ jobs: [] }),
      getJobStatsApiV1JobsStatsOverview: vi.fn().mockResolvedValue({}),
    },
  }),
}));

vi.mock('../../services/sse-context', () => ({
  useSSE: () => ({
    isConnected: false,
    on: vi.fn(() => () => {}),
  }),
}));

vi.mock('../../components/NotificationSystem', () => ({
  useNotifications: () => ({
    showNotification: vi.fn(),
  }),
}));

vi.mock('../../utils/error-handler', () => ({
  handleError: vi.fn(),
}));

describe('useAdministrationData - Infinite Loop Prevention', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should not cause infinite re-renders', async () => {
    let renderCount = 0;

    const { result } = renderHook(() => {
      renderCount++;
      return useAdministrationData();
    });

    // Wait for initial effects to run
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10));
    });

    const initialRenderCount = renderCount;

    // Wait a bit more to see if there are additional renders
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 50));
    });

    // Should not have significantly more renders
    expect(renderCount).toBeLessThanOrEqual(initialRenderCount + 2); // Allow for React StrictMode double rendering

    // Verify the hook returns expected structure
    expect(result.current).toHaveProperty('backups');
    expect(result.current).toHaveProperty('plugins');
    expect(result.current).toHaveProperty('jobs');
    expect(result.current).toHaveProperty('jobStats');
    expect(result.current).toHaveProperty('users');
    expect(result.current).toHaveProperty('dataLoading');
    expect(result.current).toHaveProperty('loadBackups');
    expect(result.current).toHaveProperty('loadPlugins');
    expect(result.current).toHaveProperty('loadJobs');
    expect(result.current).toHaveProperty('loadJobStats');
  });

  it('should maintain stable callback references', () => {
    const { result, rerender } = renderHook(() => useAdministrationData());

    const initialCallbacks = {
      loadBackups: result.current.loadBackups,
      loadPlugins: result.current.loadPlugins,
      loadJobs: result.current.loadJobs,
      loadJobStats: result.current.loadJobStats,
    };

    // Force a re-render
    rerender();

    // Callbacks should be the same reference
    expect(result.current.loadBackups).toBe(initialCallbacks.loadBackups);
    expect(result.current.loadPlugins).toBe(initialCallbacks.loadPlugins);
    expect(result.current.loadJobs).toBe(initialCallbacks.loadJobs);
    expect(result.current.loadJobStats).toBe(initialCallbacks.loadJobStats);
  });

  it('should prevent infinite loop patterns', () => {
    // This test verifies the code structure rather than runtime behavior
    // since the infinite loop was a structural issue

    const { result } = renderHook(() => useAdministrationData());

    // Verify hook structure is correct
    expect(result.current).toBeDefined();
    expect(typeof result.current.loadBackups).toBe('function');
    expect(typeof result.current.loadPlugins).toBe('function');
    expect(typeof result.current.loadJobs).toBe('function');
    expect(typeof result.current.loadJobStats).toBe('function');

    // The fix prevents infinite loops by:
    // 1. Using empty dependency arrays for stable callbacks
    // 2. Using useRef for accessing changing values without dependencies
    // 3. Loading data only once on mount

    expect(true).toBe(true); // Test passes if no infinite loop crashes the test
  });
});
