/**
 * Factory function for creating Chatter SDK instances
 */
import { ChatterSDK } from './client';
import { ChatterConfig } from './types';

/**
 * Create a new Chatter SDK client instance
 */
export function createChatterClient(config?: ChatterConfig): ChatterSDK {
  return new ChatterSDK(config);
}

/**
 * Create a pre-configured Chatter SDK client with common settings
 */
export function createChatterClientWithDefaults(overrides?: Partial<ChatterConfig>): ChatterSDK {
  const defaultConfig: ChatterConfig = {
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    timeout: 30000,
    retries: 3,
  };

  return new ChatterSDK({ ...defaultConfig, ...overrides });
}
