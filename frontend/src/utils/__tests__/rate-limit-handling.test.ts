import { describe, it, expect, vi, beforeEach } from 'vitest';
import { handleError } from '../error-handler';
import { toastService } from '../../services/toast-service';

// Mock the toast service
vi.mock('../../services/toast-service', () => ({
  toastService: {
    error: vi.fn(),
  },
}));

// Mock console.error to avoid noise in tests
vi.spyOn(console, 'error').mockImplementation(() => {
  // Mock implementation for testing
});

describe('Rate Limit Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should handle rate limit errors with user-friendly message in development', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    const rateLimitError = {
      response: {
        status: 429,
        data: {
          title: 'Too Many Requests',
          detail: 'Rate limit exceeded',
        },
      },
    };

    const mockToastError = vi.mocked(toastService.error);

    // Call handleError with rate limit error
    handleError(
      rateLimitError,
      {
        source: 'test',
        operation: 'test operation',
      },
      {
        showToast: true,
        logToConsole: false,
      }
    );

    // In development mode, should show detailed error
    const expectedMessage =
      'Too many requests. Please wait a moment before trying again.\n\nSource: test\nOperation: test operation';
    expect(mockToastError).toHaveBeenCalledWith(expectedMessage, {
      autoClose: false,
    });

    process.env.NODE_ENV = originalEnv;
  });

  it('should handle regular errors normally', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';

    const normalError = new Error('Regular error message');

    const mockToastError = vi.mocked(toastService.error);

    // Call handleError with normal error
    handleError(
      normalError,
      {
        source: 'test',
        operation: 'test operation',
      },
      {
        showToast: true,
        logToConsole: false,
      }
    );

    // Should show production-style message
    const expectedMessage = 'Regular error message (Error in test)';
    expect(mockToastError).toHaveBeenCalledWith(expectedMessage);

    process.env.NODE_ENV = originalEnv;
  });

  it('should not show toast for rate limit errors in production', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';

    const rateLimitError = {
      response: {
        status: 429,
        data: {
          title: 'Too Many Requests',
          detail: 'Rate limit exceeded',
        },
      },
    };

    const mockToastError = vi.mocked(toastService.error);

    // Call handleError with rate limit error in production
    handleError(
      rateLimitError,
      {
        source: 'test',
        operation: 'test operation',
      },
      {
        showToast: true,
        logToConsole: false,
      }
    );

    // Should NOT show toast for rate limit errors in production
    expect(mockToastError).not.toHaveBeenCalled();

    process.env.NODE_ENV = originalEnv;
  });
});
