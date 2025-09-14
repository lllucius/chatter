/**
 * Global error handlers for uncaught errors and unhandled promise rejections
 * Ensures all errors are captured and processed through the standardized error handler
 */

import { errorHandler } from './error-handler';

class GlobalErrorHandler {
  private initialized = false;

  /**
   * Initialize global error handlers
   * Should be called once during application startup
   */
  public initialize(): void {
    if (this.initialized) {
      return;
    }

    // Handle uncaught JavaScript errors
    window.addEventListener('error', this.handleJavaScriptError);

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', this.handleUnhandledRejection);

    // Handle resource loading errors (images, scripts, etc.)
    window.addEventListener('error', this.handleResourceError, true);

    this.initialized = true;
  }

  /**
   * Clean up global error handlers
   * Useful for testing or when shutting down the application
   */
  public cleanup(): void {
    if (!this.initialized) {
      return;
    }

    window.removeEventListener('error', this.handleJavaScriptError);
    window.removeEventListener('unhandledrejection', this.handleUnhandledRejection);
    window.removeEventListener('error', this.handleResourceError, true);

    this.initialized = false;
  }

  /**
   * Handle uncaught JavaScript errors
   */
  private handleJavaScriptError = (event: ErrorEvent): void => {
    const { error, message, filename, lineno, colno } = event;

    // Filter out benign ResizeObserver errors that don't require user attention
    if (this.isResizeObserverError(message, error)) {
      // Only log in development mode for debugging purposes
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.debug('[Global Error Handler] ResizeObserver loop error (benign):', message);
      }
      return;
    }

    errorHandler.handleError(error || new Error(message), {
      source: 'GlobalErrorHandler.handleJavaScriptError',
      operation: 'Uncaught JavaScript error',
      additionalData: {
        filename,
        lineno,
        colno,
        message,
        url: window.location.href,
        userAgent: navigator.userAgent
      }
    }, {
      showToast: true,
      logToConsole: true,
      fallbackMessage: 'An unexpected error occurred'
    });
  };

  /**
   * Handle unhandled promise rejections
   */
  private handleUnhandledRejection = (event: PromiseRejectionEvent): void => {
    const { reason } = event;

    errorHandler.handleError(reason, {
      source: 'GlobalErrorHandler.handleUnhandledRejection',
      operation: 'Unhandled promise rejection',
      additionalData: {
        url: window.location.href,
        userAgent: navigator.userAgent
      }
    }, {
      showToast: true,
      logToConsole: true,
      fallbackMessage: 'An unexpected error occurred while processing a request'
    });

    // Prevent the default browser console error
    event.preventDefault();
  };

  /**
   * Handle resource loading errors (images, scripts, stylesheets, etc.)
   */
  private handleResourceError = (event: Event): void => {
    const target = event.target as HTMLElement | null;
    
    // Only handle resource loading errors, not JavaScript errors
    // Check if target is an element and not the window
    if (target && target !== (window as unknown as EventTarget) && target !== event.currentTarget) {
      const resourceType = target.tagName?.toLowerCase() || 'unknown';
      const resourceSrc = 
        (target as HTMLImageElement | HTMLScriptElement).src || 
        (target as HTMLLinkElement).href || 
        'unknown';

      errorHandler.handleError(
        new Error(`Failed to load ${resourceType}: ${resourceSrc}`),
        {
          source: 'GlobalErrorHandler.handleResourceError',
          operation: 'Resource loading',
          additionalData: {
            resourceType,
            resourceSrc,
            url: window.location.href
          }
        },
        {
          showToast: false, // Don't show toast for resource errors by default
          logToConsole: true,
          fallbackMessage: `Failed to load ${resourceType}`
        }
      );
    }
  };

  /**
   * Check if global error handlers are initialized
   */
  public isInitialized(): boolean {
    return this.initialized;
  }

  /**
   * Check if an error is a benign ResizeObserver error that should be filtered out
   */
  private isResizeObserverError(message: string, error?: Error): boolean {
    const resizeObserverPattern = /ResizeObserver loop completed with undelivered notifications/i;
    
    // Check both the message and error object for ResizeObserver patterns
    if (message && resizeObserverPattern.test(message)) {
      return true;
    }
    
    if (error && error.message && resizeObserverPattern.test(error.message)) {
      return true;
    }
    
    return false;
  }
}

// Export singleton instance
export const globalErrorHandler = new GlobalErrorHandler();

// Convenience function to initialize global error handling
export const initializeGlobalErrorHandling = (): void => {
  globalErrorHandler.initialize();
};

// Convenience function to cleanup global error handling
export const cleanupGlobalErrorHandling = (): void => {
  globalErrorHandler.cleanup();
};