import { describe, it, expect, vi, beforeEach } from 'vitest';
import { configService, loadConfig, getConfig } from '../config-service';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('ConfigService', () => {
  beforeEach(() => {
    // Reset the service state
    (configService as any).config = null;
    (configService as any).loading = false;
    (configService as any).loadPromise = null;
    
    // Clear all mocks
    vi.clearAllMocks();
  });

  it('should load configuration from JSON file successfully', async () => {
    const mockConfig = {
      apiBaseUrl: 'http://test:8000',
      title: 'Test App',
      version: '1.0.0'
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockConfig)
    });

    const config = await loadConfig();

    expect(fetch).toHaveBeenCalledWith('/config.json');
    expect(config).toEqual(mockConfig);
    expect(getConfig()).toEqual(mockConfig);
  });

  it('should use fallback configuration when fetch fails', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const config = await loadConfig();

    expect(config).toEqual({
      apiBaseUrl: 'http://localhost:8000', // fallback
      title: 'Chatter AI Platform',
      version: '0.1.0'
    });
  });

  it('should validate required fields and throw error for missing apiBaseUrl', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ title: 'Test' }) // missing apiBaseUrl
    });

    const config = await loadConfig();

    // Should use fallback when validation fails
    expect(config).toEqual({
      apiBaseUrl: 'http://localhost:8000',
      title: 'Chatter AI Platform', 
      version: '0.1.0'
    });
  });

  it('should cache configuration and not fetch multiple times', async () => {
    const mockConfig = { apiBaseUrl: 'http://test:8000' };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockConfig)
    });

    const config1 = await loadConfig();
    const config2 = await loadConfig();

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(config1).toBe(config2);
  });

  it('should return null when config not loaded', () => {
    expect(getConfig()).toBeNull();
    expect(configService.isLoaded()).toBe(false);
  });

  it('should indicate loading state correctly', async () => {
    mockFetch.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: () => Promise.resolve({ apiBaseUrl: 'http://test:8000' })
      }), 100))
    );

    expect(configService.isLoading()).toBe(false);

    const configPromise = loadConfig();
    expect(configService.isLoading()).toBe(true);

    await configPromise;
    expect(configService.isLoading()).toBe(false);
    expect(configService.isLoaded()).toBe(true);
  });
});