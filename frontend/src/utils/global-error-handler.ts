/**
 * Global error handlers for uncaught errors and unhandled promise rejections
 * Ensures all errors are captured and processed through the standardized error handler
 */

import { errorHandler } from './error-handler';
import { errorConfig } from './error-config';

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
    window.addEventListener(
      'unhandledrejection',
      this.handleUnhandledRejection
    );

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
    window.removeEventListener(
      'unhandledrejection',
      this.handleUnhandledRejection
    );
    window.removeEventListener('error', this.handleResourceError, true);

    this.initialized = false;
  }

  /**
   * Handle uncaught JavaScript errors
   */
  private handleJavaScriptError = (event: ErrorEvent): void => {
    const { error, message, filename, lineno, colno } = event;

    // Filter out benign ResizeObserver errors that don't require user attention
    if (errorConfig.shouldFilterExtensionErrors() && this.isResizeObserverError(message, error)) {
      // Only log in development mode for debugging purposes
      if (errorConfig.shouldLogToConsole()) {
        // eslint-disable-next-line no-console
        console.debug(
          '[Global Error Handler] ResizeObserver loop error (benign):',
          message
        );
      }
      return;
    }

    // Filter out Chrome extension errors that don't affect the app
    if (errorConfig.shouldFilterExtensionErrors() && this.isChromeExtensionError(message, error, filename)) {
      // Only log in development mode for debugging purposes
      if (errorConfig.shouldLogToConsole()) {
        // eslint-disable-next-line no-console
        console.debug(
          '[Global Error Handler] Chrome extension error (filtered):',
          message,
          filename
        );
      }
      return;
    }

    errorHandler.handleError(
      error || new Error(message),
      {
        source: 'GlobalErrorHandler.handleJavaScriptError',
        operation: 'Uncaught JavaScript error',
        additionalData: {
          filename,
          lineno,
          colno,
          message,
          url: window.location.href,
          userAgent: navigator.userAgent,
        },
      },
      {
        showToast: errorConfig.shouldShowToasts(),
        logToConsole: errorConfig.shouldLogToConsole(),
        fallbackMessage: 'An unexpected error occurred',
      }
    );
  };

  /**
   * Handle unhandled promise rejections
   */
  private handleUnhandledRejection = (event: PromiseRejectionEvent): void => {
    const { reason } = event;

    errorHandler.handleError(
      reason,
      {
        source: 'GlobalErrorHandler.handleUnhandledRejection',
        operation: 'Unhandled promise rejection',
        additionalData: {
          url: window.location.href,
          userAgent: navigator.userAgent,
        },
      },
      {
        showToast: errorConfig.shouldShowToasts(),
        logToConsole: errorConfig.shouldLogToConsole(),
        fallbackMessage:
          'An unexpected error occurred while processing a request',
      }
    );

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
    if (
      target &&
      target !== (window as unknown as EventTarget) &&
      target !== event.currentTarget
    ) {
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
            url: window.location.href,
          },
        },
        {
          showToast: false, // Don't show toast for resource errors by default
          logToConsole: true,
          fallbackMessage: `Failed to load ${resourceType}`,
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
    const resizeObserverPattern =
      /ResizeObserver loop completed with undelivered notifications/i;

    // Check both the message and error object for ResizeObserver patterns
    if (message && resizeObserverPattern.test(message)) {
      return true;
    }

    if (error && error.message && resizeObserverPattern.test(error.message)) {
      return true;
    }

    return false;
  }

  /**
   * Check if an error is from a Chrome extension that should be filtered out
   */
  private isChromeExtensionError(
    message: string,
    error?: Error,
    filename?: string
  ): boolean {
    // Check for chrome-extension URLs or typical extension error patterns
    const chromeExtensionPatterns = [
      /chrome-extension:\/\//i,
      /moz-extension:\/\//i, // Firefox extensions
      /safari-extension:\/\//i, // Safari extensions
      /edge-extension:\/\//i, // Edge extensions
      /Cannot read properties of undefined \(reading 'isCheckout'\)/i,
      /Cannot read properties of undefined \(reading '[^']*'\).*chrome-extension/i,
      /Unchecked runtime\.lastError/i,
      /A listener indicated an asynchronous response by returning true, but the message channel closed before a response was received/i,
      /message channel closed before a response was received/i,
      /extension.*content.*script/i,
      /content-script\.js/i,
      /background\.js.*extension/i,
      /Error handling response.*chrome-extension/i,
      /Script error.*chrome-extension/i,
      /Loading chunk \d+ failed.*chrome-extension/i,
      /Non-Error promise rejection captured.*chrome-extension/i,
    ];

    // Check filename for extension scripts - more comprehensive check
    if (filename && (
      filename.includes('chrome-extension://') ||
      filename.includes('moz-extension://') ||
      filename.includes('safari-extension://') ||
      filename.includes('edge-extension://') ||
      filename.includes('content-script.js') ||
      filename.includes('background.js')
    )) {
      return true;
    }

    // Check stack trace for extension patterns
    if (error && error.stack) {
      for (const pattern of chromeExtensionPatterns) {
        if (pattern.test(error.stack)) {
          return true;
        }
      }
    }

    // Check message against patterns
    for (const pattern of chromeExtensionPatterns) {
      if (message && pattern.test(message)) {
        return true;
      }
      if (error && error.message && pattern.test(error.message)) {
        return true;
      }
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
