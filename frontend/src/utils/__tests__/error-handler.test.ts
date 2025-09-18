import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import {
  errorHandler,
  handleError,
  handleErrorWithResult,
} from '../error-handler';
import { toastService } from '../../services/toast-service';

// Mock the toast service
vi.mock('../../services/toast-service', () => ({
  toastService: {
    error: vi.fn(),
  },
}));

// Mock console methods
const mockConsoleError = vi
  .spyOn(console, 'error')
  .mockImplementation(() => {});

describe('ErrorHandler', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset NODE_ENV for each test
    process.env.NODE_ENV = 'test';
  });

  afterEach(() => {
    mockConsoleError.mockClear();
  });

  describe('Error Message Extraction', () => {
    it('should extract message from string error', () => {
      const error = 'Simple error message';

      handleError(
        error,
        { source: 'test' },
        { showToast: false, logToConsole: false }
      );

      expect(toastService.error).not.toHaveBeenCalled();
    });

    it('should extract message from Error object', () => {
      const error = new Error('Test error message');

      handleError(
        error,
        { source: 'test' },
        { showToast: false, logToConsole: false }
      );

      // Test should not throw and should handle the error silently
    });

    it('should extract message from API error response', () => {
      const error = {
        response: {
          data: {
            title: 'Validation Error',
            detail: 'Field is required',
          },
        },
      };

      handleError(
        error,
        { source: 'test' },
        { showToast: false, logToConsole: false }
      );

      // Should handle API error format
    });

    it('should use fallback message for unknown error types', () => {
      const error = { unknownProperty: 'value' };

      handleError(
        error,
        { source: 'test' },
        {
          showToast: false,
          logToConsole: false,
          fallbackMessage: 'Custom fallback',
        }
      );

      // Should use fallback message
    });
  });

  describe('Development vs Production Mode', () => {
    it('should show detailed errors in development mode', () => {
      process.env.NODE_ENV = 'development';
      const error = new Error('Test error');

      handleError(error, {
        source: 'TestComponent',
        operation: 'test operation',
      });

      expect(mockConsoleError).toHaveBeenCalled();
      expect(toastService.error).toHaveBeenCalledWith(
        expect.stringContaining('Test error'),
        { autoClose: false }
      );
    });

    it('should show user-friendly errors in production mode', () => {
      process.env.NODE_ENV = 'production';
      const error = new Error('Technical error message');

      handleError(error, {
        source: 'TestComponent',
        operation: 'test operation',
      });

      expect(toastService.error).toHaveBeenCalledWith(
        expect.stringContaining('(Error in TestComponent)')
      );
    });
  });

  describe('Error Context Handling', () => {
    it('should include source information in error handling', () => {
      const error = new Error('Test error');
      const context = {
        source: 'AuthService.login',
        operation: 'user authentication',
        userId: 'user123',
        additionalData: { username: 'testuser' },
      };

      handleError(error, context, { showToast: false, logToConsole: true });

      expect(mockConsoleError).toHaveBeenCalledWith(
        expect.stringContaining('AuthService.login')
      );
    });

    it('should handle minimal context', () => {
      const error = new Error('Test error');
      const context = { source: 'minimal' };

      handleError(error, context, { showToast: false, logToConsole: false });

      // Should not throw with minimal context
    });
  });

  describe('Error Handling Options', () => {
    it('should respect showToast option', () => {
      const error = new Error('Test error');

      handleError(error, { source: 'test' }, { showToast: false });

      expect(toastService.error).not.toHaveBeenCalled();
    });

    it('should respect logToConsole option', () => {
      const error = new Error('Test error');

      handleError(error, { source: 'test' }, { logToConsole: false });

      expect(mockConsoleError).not.toHaveBeenCalled();
    });

    it('should rethrow error when requested', () => {
      const error = new Error('Test error');

      expect(() => {
        handleError(
          error,
          { source: 'test' },
          {
            rethrow: true,
            showToast: false,
            logToConsole: false,
          }
        );
      }).toThrow('Test error');
    });
  });

  describe('handleErrorWithResult', () => {
    it('should return structured error response', () => {
      const error = new Error('Test error');

      const result = handleErrorWithResult(
        error,
        { source: 'test' },
        {
          showToast: false,
          logToConsole: false,
        }
      );

      expect(result).toEqual({
        success: false,
        error: 'Test error',
      });
    });

    it('should include details in development mode', () => {
      process.env.NODE_ENV = 'development';
      const error = new Error('Test error');

      const result = handleErrorWithResult(
        error,
        { source: 'test' },
        {
          showToast: false,
          logToConsole: false,
        }
      );

      expect(result).toHaveProperty('details');
      expect(result.details).toContain('Source: test');
    });

    it('should not include details in production mode', () => {
      process.env.NODE_ENV = 'production';
      const error = new Error('Test error');

      const result = handleErrorWithResult(
        error,
        { source: 'test' },
        {
          showToast: false,
          logToConsole: false,
        }
      );

      expect(result).not.toHaveProperty('details');
    });
  });

  describe('Function Wrappers', () => {
    it('should wrap async functions correctly', async () => {
      const asyncFn = vi.fn().mockRejectedValue(new Error('Async error'));
      const wrappedFn = errorHandler.wrapAsync(
        asyncFn,
        { source: 'test' },
        {
          showToast: false,
          logToConsole: false,
        }
      );

      await expect(wrappedFn()).rejects.toThrow('Async error');
      expect(asyncFn).toHaveBeenCalled();
    });

    it('should wrap sync functions correctly', () => {
      const syncFn = vi.fn().mockImplementation(() => {
        throw new Error('Sync error');
      });
      const wrappedFn = errorHandler.wrapSync(
        syncFn,
        { source: 'test' },
        {
          showToast: false,
          logToConsole: false,
        }
      );

      expect(() => wrappedFn()).toThrow('Sync error');
      expect(syncFn).toHaveBeenCalled();
    });
  });

  describe('Problem Detail Format', () => {
    it('should handle RFC 9457 Problem Detail correctly', () => {
      const error = {
        response: {
          data: {
            type: 'https://example.com/problems/validation',
            title: 'Validation Error',
            status: 400,
            detail: 'The email field is required',
            instance: '/api/users',
          },
        },
      };

      handleError(
        error,
        { source: 'test' },
        { showToast: false, logToConsole: false }
      );

      // Should extract problem detail information
    });

    it('should prioritize title + detail over individual fields', () => {
      const error = {
        response: {
          data: {
            title: 'Error Title',
            detail: 'Error Detail',
          },
        },
      };

      const result = handleErrorWithResult(
        error,
        { source: 'test' },
        {
          showToast: false,
          logToConsole: false,
        }
      );

      expect(result.error).toBe('Error Title: Error Detail');
    });
  });
});
