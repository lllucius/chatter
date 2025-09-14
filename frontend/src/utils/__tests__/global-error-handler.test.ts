import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { globalErrorHandler, initializeGlobalErrorHandling, cleanupGlobalErrorHandling } from '../global-error-handler';
import { errorHandler } from '../error-handler';

// Mock the error handler
vi.mock('../error-handler', () => ({
  errorHandler: {
    handleError: vi.fn(),
  },
}));

// Mock PromiseRejectionEvent for test environment
if (typeof PromiseRejectionEvent === 'undefined') {
  (global as any).PromiseRejectionEvent = class PromiseRejectionEvent extends Event {
    promise: Promise<any>;
    reason: any;
    
    constructor(type: string, options: { promise: Promise<any>; reason: any }) {
      super(type);
      this.promise = options.promise;
      this.reason = options.reason;
    }
    
    preventDefault() {
      // Mock preventDefault
    }
  };
}

describe('GlobalErrorHandler', () => {
  beforeEach(() => {
    // Clean up any existing handlers
    cleanupGlobalErrorHandling();
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanupGlobalErrorHandling();
  });

  describe('Initialization', () => {
    it('should initialize global error handlers', () => {
      expect(globalErrorHandler.isInitialized()).toBe(false);
      
      initializeGlobalErrorHandling();
      
      expect(globalErrorHandler.isInitialized()).toBe(true);
    });

    it('should not initialize twice', () => {
      initializeGlobalErrorHandling();
      expect(globalErrorHandler.isInitialized()).toBe(true);
      
      // Second call should not change anything
      initializeGlobalErrorHandling();
      expect(globalErrorHandler.isInitialized()).toBe(true);
    });

    it('should cleanup global error handlers', () => {
      initializeGlobalErrorHandling();
      expect(globalErrorHandler.isInitialized()).toBe(true);
      
      cleanupGlobalErrorHandling();
      expect(globalErrorHandler.isInitialized()).toBe(false);
    });
  });

  describe('JavaScript Error Handling', () => {
    it('should handle uncaught JavaScript errors', () => {
      initializeGlobalErrorHandling();

      const testError = new Error('Test JavaScript error');
      const errorEvent = new ErrorEvent('error', {
        error: testError,
        message: 'Test JavaScript error',
        filename: 'test.js',
        lineno: 42,
        colno: 10,
      });

      // Dispatch the error event
      window.dispatchEvent(errorEvent);

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        testError,
        expect.objectContaining({
          source: 'GlobalErrorHandler.handleJavaScriptError',
          operation: 'Uncaught JavaScript error',
          additionalData: expect.objectContaining({
            filename: 'test.js',
            lineno: 42,
            colno: 10,
            message: 'Test JavaScript error',
          }),
        }),
        expect.objectContaining({
          showToast: true,
          logToConsole: true,
          fallbackMessage: 'An unexpected error occurred',
        })
      );
    });

    it('should handle error events without error object', () => {
      initializeGlobalErrorHandling();

      const errorEvent = new ErrorEvent('error', {
        message: 'Test error message',
        filename: 'test.js',
        lineno: 42,
        colno: 10,
      });

      window.dispatchEvent(errorEvent);

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          source: 'GlobalErrorHandler.handleJavaScriptError',
          operation: 'Uncaught JavaScript error',
        }),
        expect.any(Object)
      );
    });
  });

  describe('Promise Rejection Handling', () => {
    it('should handle unhandled promise rejections', () => {
      initializeGlobalErrorHandling();

      const testError = new Error('Test promise rejection');
      const rejectionEvent = new PromiseRejectionEvent('unhandledrejection', {
        promise: Promise.reject(testError),
        reason: testError,
      });

      // Mock preventDefault
      const preventDefaultSpy = vi.spyOn(rejectionEvent, 'preventDefault');

      window.dispatchEvent(rejectionEvent);

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        testError,
        expect.objectContaining({
          source: 'GlobalErrorHandler.handleUnhandledRejection',
          operation: 'Unhandled promise rejection',
        }),
        expect.objectContaining({
          showToast: true,
          logToConsole: true,
          fallbackMessage: 'An unexpected error occurred while processing a request',
        })
      );

      expect(preventDefaultSpy).toHaveBeenCalled();
    });

    it('should handle promise rejections with non-error reasons', () => {
      initializeGlobalErrorHandling();

      const rejectionReason = 'String rejection reason';
      const rejectionEvent = new PromiseRejectionEvent('unhandledrejection', {
        promise: Promise.reject(rejectionReason),
        reason: rejectionReason,
      });

      window.dispatchEvent(rejectionEvent);

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        rejectionReason,
        expect.objectContaining({
          source: 'GlobalErrorHandler.handleUnhandledRejection',
          operation: 'Unhandled promise rejection',
        }),
        expect.any(Object)
      );
    });
  });

  describe('Resource Error Handling', () => {
    it('should handle resource loading errors', () => {
      initializeGlobalErrorHandling();

      // Create a mock script element
      const scriptElement = document.createElement('script');
      scriptElement.src = 'https://example.com/test.js';
      document.body.appendChild(scriptElement);

      // Create error event for resource loading
      const errorEvent = new Event('error');
      Object.defineProperty(errorEvent, 'target', {
        value: scriptElement,
        writable: false,
      });

      // Dispatch error event with capture=true (resource errors)
      scriptElement.dispatchEvent(errorEvent);

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          source: 'GlobalErrorHandler.handleResourceError',
          operation: 'Resource loading',
          additionalData: expect.objectContaining({
            resourceType: 'script',
            resourceSrc: 'https://example.com/test.js',
          }),
        }),
        expect.objectContaining({
          showToast: false, // Resource errors don't show toast by default
          logToConsole: true,
        })
      );

      // Cleanup
      document.body.removeChild(scriptElement);
    });

    it('should handle image loading errors', () => {
      initializeGlobalErrorHandling();

      const imgElement = document.createElement('img');
      imgElement.src = 'https://example.com/test.jpg';
      document.body.appendChild(imgElement);

      const errorEvent = new Event('error');
      Object.defineProperty(errorEvent, 'target', {
        value: imgElement,
        writable: false,
      });

      imgElement.dispatchEvent(errorEvent);

      expect(errorHandler.handleError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          source: 'GlobalErrorHandler.handleResourceError',
          operation: 'Resource loading',
          additionalData: expect.objectContaining({
            resourceType: 'img',
            resourceSrc: 'https://example.com/test.jpg',
          }),
        }),
        expect.any(Object)
      );

      document.body.removeChild(imgElement);
    });

    it('should not handle window errors as resource errors', () => {
      initializeGlobalErrorHandling();

      const errorEvent = new Event('error');
      Object.defineProperty(errorEvent, 'target', {
        value: window,
        writable: false,
      });

      // This should not trigger the resource error handler
      window.dispatchEvent(errorEvent);

      // The resource error handler should not be called for window errors
      expect(errorHandler.handleError).not.toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          source: 'GlobalErrorHandler.handleResourceError',
        }),
        expect.anything()
      );
    });
  });

  describe('Event Listener Management', () => {
    it('should add and remove event listeners properly', () => {
      const addEventListenerSpy = vi.spyOn(window, 'addEventListener');
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');

      initializeGlobalErrorHandling();

      expect(addEventListenerSpy).toHaveBeenCalledWith('error', expect.any(Function));
      expect(addEventListenerSpy).toHaveBeenCalledWith('unhandledrejection', expect.any(Function));
      expect(addEventListenerSpy).toHaveBeenCalledWith('error', expect.any(Function), true);

      cleanupGlobalErrorHandling();

      expect(removeEventListenerSpy).toHaveBeenCalledWith('error', expect.any(Function));
      expect(removeEventListenerSpy).toHaveBeenCalledWith('unhandledrejection', expect.any(Function));
      expect(removeEventListenerSpy).toHaveBeenCalledWith('error', expect.any(Function), true);

      addEventListenerSpy.mockRestore();
      removeEventListenerSpy.mockRestore();
    });
  });
});