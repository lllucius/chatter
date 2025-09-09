import { describe, it, expect, beforeEach } from 'vitest';
import { authService, getSDK } from '../auth-service';

describe('AuthService and ChatterSDK', () => {
  beforeEach(() => {
    // Clear any stored tokens before each test
    localStorage.clear();
  });

  it('should be properly initialized', () => {
    const sdk = getSDK();
    expect(authService).toBeDefined();
    expect(sdk).toBeDefined();
    expect(sdk.auth).toBeDefined();
    expect(sdk.agents).toBeDefined();
    expect(sdk.models).toBeDefined();
    expect(sdk.toolServers).toBeDefined();
    expect(sdk.chat).toBeDefined();
  });

  it('should handle authentication state correctly', () => {
    expect(authService.isAuthenticated()).toBe(false);
    expect(authService.getToken()).toBeNull();
  });

  it('should provide SDK instances', () => {
    const sdk = getSDK();
    expect(sdk).toBeDefined();
    expect(sdk.chat).toBeDefined();
    expect(sdk.auth).toBeDefined();
  });

  it('should provide authentication methods', () => {
    expect(typeof authService.login).toBe('function');
    expect(typeof authService.logout).toBe('function');
    expect(typeof authService.isAuthenticated).toBe('function');
    expect(typeof authService.getToken).toBe('function');
  });
});