import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from "vitest";
import { useAsyncError, useAsyncOperation } from '../useAsyncError';
import { errorHandler } from '../../utils/error-handler';

// Mock the error handler
vi.mock('../../utils/error-handler', () => ({
  errorHandler: {
    handleError: vi.fn(),
  },
}));

describe('useAsyncError', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('handleAsyncError', () => {
    it('should call errorHandler.handleError with provided parameters', () => {
      const { result } = renderHook(() => useAsyncError());
      const testError = new Error('Test error');
      const context = {
        source: 'test',
        operation: 'test operation',
      };
      const options = {
        showToast: true,
        logToConsole: false,
      };

      act(() => {
        result.current.handleAsyncError(testError, context, options);
      });

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        testError,
        context,
        options
      );
    });

    it('should work without options parameter', () => {
      const { result } = renderHook(() => useAsyncError());
      const testError = new Error('Test error');
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      act(() => {
        result.current.handleAsyncError(testError, context);
      });

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        testError,
        context,
        undefined
      );
    });
  });

  describe('wrapAsyncFunction', () => {
    it('should execute function successfully when no error occurs', async () => {
      const { result } = renderHook(() => useAsyncError());
      const mockFn = vi.fn().mockResolvedValue('success');
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const wrappedFn = result.current.wrapAsyncFunction(mockFn, context);

      await expect(wrappedFn('arg1', 'arg2')).resolves.toBe('success');
      expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
      expect(errorHandler.handleError).not.toHaveBeenCalled();
    });

    it('should handle errors and rethrow them', async () => {
      const { result } = renderHook(() => useAsyncError());
      const testError = new Error('Test error');
      const mockFn = vi.fn().mockRejectedValue(testError);
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const wrappedFn = result.current.wrapAsyncFunction(mockFn, context);

      await expect(wrappedFn()).rejects.toThrow('Test error');
      expect(errorHandler.handleError).toHaveBeenCalledWith(
        testError,
        context,
        undefined
      );
    });

    it('should pass options to error handler', async () => {
      const { result } = renderHook(() => useAsyncError());
      const testError = new Error('Test error');
      const mockFn = vi.fn().mockRejectedValue(testError);
      const context = {
        source: 'test',
        operation: 'test operation',
      };
      const options = {
        showToast: false,
        logToConsole: true,
      };

      const wrappedFn = result.current.wrapAsyncFunction(
        mockFn,
        context,
        options
      );

      await expect(wrappedFn()).rejects.toThrow('Test error');
      expect(errorHandler.handleError).toHaveBeenCalledWith(
        testError,
        context,
        options
      );
    });
  });

  describe('createSafeAsyncFunction', () => {
    it('should return success result when function executes successfully', async () => {
      const { result } = renderHook(() => useAsyncError());
      const mockFn = vi.fn().mockResolvedValue('success data');
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const safeFn = result.current.createSafeAsyncFunction(mockFn, context);
      const result_data = await safeFn('arg1');

      expect(result_data).toEqual({
        success: true,
        data: 'success data',
      });
      expect(mockFn).toHaveBeenCalledWith('arg1');
      expect(errorHandler.handleError).not.toHaveBeenCalled();
    });

    it('should return error result when function throws', async () => {
      const { result } = renderHook(() => useAsyncError());
      const testError = new Error('Test error');
      const mockFn = vi.fn().mockRejectedValue(testError);
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const safeFn = result.current.createSafeAsyncFunction(mockFn, context);
      const result_data = await safeFn();

      expect(result_data).toEqual({
        success: false,
        error: 'Test error',
      });
      expect(errorHandler.handleError).toHaveBeenCalledWith(
        testError,
        context,
        undefined
      );
    });

    it('should handle non-Error rejections', async () => {
      const { result } = renderHook(() => useAsyncError());
      const mockFn = vi.fn().mockRejectedValue('String error');
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const safeFn = result.current.createSafeAsyncFunction(mockFn, context);
      const result_data = await safeFn();

      expect(result_data).toEqual({
        success: false,
        error: 'An error occurred',
      });
      expect(errorHandler.handleError).toHaveBeenCalledWith(
        'String error',
        context,
        undefined
      );
    });
  });

  describe('executeAsync', () => {
    it('should return success result for successful execution', async () => {
      const { result } = renderHook(() => useAsyncError());
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const result_data = await result.current.executeAsync(
        () => Promise.resolve('success'),
        context
      );

      expect(result_data).toEqual({
        success: true,
        data: 'success',
      });
      expect(errorHandler.handleError).not.toHaveBeenCalled();
    });

    it('should return error result for failed execution', async () => {
      const { result } = renderHook(() => useAsyncError());
      const testError = new Error('Execution failed');
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const result_data = await result.current.executeAsync(
        () => Promise.reject(testError),
        context
      );

      expect(result_data).toEqual({
        success: false,
        error: 'Execution failed',
      });
      expect(errorHandler.handleError).toHaveBeenCalledWith(
        testError,
        context,
        undefined
      );
    });
  });
});

describe('useAsyncOperation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createAsyncOperation', () => {
    it('should execute operation and call onSuccess when successful', async () => {
      const { result } = renderHook(() => useAsyncOperation());
      const onSuccess = vi.fn();
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const operation = result.current.createAsyncOperation(
        () => Promise.resolve('success data'),
        context,
        { onSuccess }
      );

      const result_data = await operation();

      expect(result_data).toEqual({
        success: true,
        data: 'success data',
      });
      expect(onSuccess).toHaveBeenCalledWith('success data');
    });

    it('should execute operation and call onError when failed', async () => {
      const { result } = renderHook(() => useAsyncOperation());
      const onError = vi.fn();
      const testError = new Error('Operation failed');
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const operation = result.current.createAsyncOperation(
        () => Promise.reject(testError),
        context,
        { onError }
      );

      const result_data = await operation();

      expect(result_data).toEqual({
        success: false,
        error: 'Operation failed',
      });
      expect(onError).toHaveBeenCalledWith('Operation failed');
      expect(errorHandler.handleError).toHaveBeenCalledWith(
        testError,
        context,
        expect.any(Object)
      );
    });

    it('should work without callback options', async () => {
      const { result } = renderHook(() => useAsyncOperation());
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const operation = result.current.createAsyncOperation(
        () => Promise.resolve('success data'),
        context
      );

      const result_data = await operation();

      expect(result_data).toEqual({
        success: true,
        data: 'success data',
      });
    });

    it('should not call onSuccess when data is undefined', async () => {
      const { result } = renderHook(() => useAsyncOperation());
      const onSuccess = vi.fn();
      const context = {
        source: 'test',
        operation: 'test operation',
      };

      const operation = result.current.createAsyncOperation(
        () => Promise.resolve(undefined),
        context,
        { onSuccess }
      );

      const result_data = await operation();

      expect(result_data).toEqual({
        success: true,
        data: undefined,
      });
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  describe('handleAsyncError', () => {
    it('should be available from useAsyncOperation', () => {
      const { result } = renderHook(() => useAsyncOperation());

      expect(result.current.handleAsyncError).toBeDefined();
      expect(typeof result.current.handleAsyncError).toBe('function');
    });
  });

  describe('executeAsync', () => {
    it('should be available from useAsyncOperation', () => {
      const { result } = renderHook(() => useAsyncOperation());

      expect(result.current.executeAsync).toBeDefined();
      expect(typeof result.current.executeAsync).toBe('function');
    });
  });
});
