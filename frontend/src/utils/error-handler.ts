/**
 * Standardized error handling for the frontend
 * Provides consistent error display with development mode details and production-friendly messages
 */

import { toastService } from '../services/toast-service';

// Error response structure from backend
interface ErrorResponse {
  response?: {
    data?: ProblemDetail | unknown;
    status?: number;
  };
  message?: string;
  stack?: string;
}

// RFC 9457 Problem Detail structure
interface ProblemDetail {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
  [key: string]: unknown;
}

export interface ErrorContext {
  source: string; // Where the error occurred (e.g., 'AuthService.login', 'useApi.execute')
  operation?: string; // What operation was being performed
  userId?: string; // Optional user context
  additionalData?: Record<string, unknown>; // Any additional context
}

export interface ErrorHandlerOptions {
  showToast?: boolean; // Whether to show toast notification (default: true)
  logToConsole?: boolean; // Whether to log to console (default: true in dev)
  rethrow?: boolean; // Whether to rethrow the error (default: false)
  fallbackMessage?: string; // Fallback message if no meaningful error can be extracted
}

/**
 * Standardized error handler that provides consistent error handling across the frontend
 */
class ErrorHandler {
  private isDevelopment(): boolean {
    return process.env.NODE_ENV === 'development';
  }

  /**
   * Check if error is a rate limit error (429)
   */
  private isRateLimitError(error: unknown): boolean {
    if (error && typeof error === 'object') {
      const errorResponse = error as ErrorResponse;
      return errorResponse?.response?.status === 429;
    }
    return false;
  }

  /**
   * Extract a meaningful error message from various error types
   */
  private extractErrorMessage(
    error: unknown,
    fallback: string = 'An unexpected error occurred'
  ): string {
    // Handle string errors
    if (typeof error === 'string') {
      return error;
    }

    // Handle Error objects
    if (error instanceof Error) {
      return error.message || fallback;
    }

    // Handle API error responses with problem details
    if (error && typeof error === 'object') {
      const errorResponse = error as ErrorResponse;

      // Handle rate limiting errors specifically
      if (this.isRateLimitError(error)) {
        return 'Too many requests. Please wait a moment before trying again.';
      }

      // Try to extract problem detail information
      const problemDetail = errorResponse?.response?.data as ProblemDetail;

      if (problemDetail && typeof problemDetail === 'object') {
        // Check for specific error cases and provide better messaging
        const detail = problemDetail.detail || '';

        // Handle duplicate document error specifically
        if (detail.includes('Document with identical content already exists')) {
          return 'This file has already been uploaded. Documents are identified by their content, so uploading the same file again is not allowed. If you need to update the document, please delete the existing one first or upload a modified version.';
        }

        // Priority order: title + detail, detail only, title only
        if (problemDetail.title && problemDetail.detail) {
          return `${problemDetail.title}: ${problemDetail.detail}`;
        }

        if (problemDetail.detail) {
          return problemDetail.detail;
        }

        if (problemDetail.title) {
          return problemDetail.title;
        }
      }

      // Fallback to generic message from error response
      if (errorResponse?.message) {
        return errorResponse.message;
      }
    }

    return fallback;
  }

  /**
   * Extract error stack trace and additional debug information
   */
  private extractErrorDetails(error: unknown, context: ErrorContext): string {
    const details: string[] = [];

    // Add context information
    details.push(`Source: ${context.source}`);
    if (context.operation) {
      details.push(`Operation: ${context.operation}`);
    }
    if (context.userId) {
      details.push(`User: ${context.userId}`);
    }

    // Add timestamp
    details.push(`Timestamp: ${new Date().toISOString()}`);

    // Add error details
    if (error instanceof Error) {
      details.push(`Error Type: ${error.constructor.name}`);
      details.push(`Message: ${error.message}`);
      if (error.stack) {
        details.push(`Stack Trace:\n${error.stack}`);
      }
    } else if (error && typeof error === 'object') {
      details.push(`Error Object: ${JSON.stringify(error, null, 2)}`);
    } else {
      details.push(`Error Value: ${String(error)}`);
    }

    // Add additional context data
    if (context.additionalData) {
      details.push(
        `Additional Data: ${JSON.stringify(context.additionalData, null, 2)}`
      );
    }

    return details.join('\n');
  }

  /**
   * Generate a production-friendly error message with minimal context
   */
  private generateProductionMessage(
    userMessage: string,
    context: ErrorContext
  ): string {
    // In production, show user-friendly message with minimal context for debugging
    return `${userMessage} (Error in ${context.source})`;
  }

  /**
   * Handle an error with standardized processing
   */
  public handleError(
    error: unknown,
    context: ErrorContext,
    options: ErrorHandlerOptions = {}
  ): void {
    const {
      showToast = true,
      logToConsole = this.isDevelopment(),
      rethrow = false,
      fallbackMessage = 'An unexpected error occurred',
    } = options;

    const userMessage = this.extractErrorMessage(error, fallbackMessage);
    const isDev = this.isDevelopment();

    // Log to console if requested
    if (logToConsole) {
      if (isDev) {
        // In development, show full error details
        const errorDetails = this.extractErrorDetails(error, context);
        console.error(`[Error Handler] ${context.source}:`, error);
        console.error('Full Error Details:\n', errorDetails);
      } else {
        // In production, log minimal information
        console.error(`[Error] ${context.source}: ${userMessage}`);
      }
    }

    // Show toast notification if requested
    if (showToast) {
      // Don't show toast for rate limit errors in production to reduce noise
      const isRateLimit = this.isRateLimitError(error);

      if (isDev) {
        // In development, show detailed error in toast
        const devMessage = `${userMessage}\n\nSource: ${context.source}${
          context.operation ? `\nOperation: ${context.operation}` : ''
        }`;
        toastService.error(devMessage, { autoClose: false });
      } else if (!isRateLimit) {
        // In production, show user-friendly message (but skip rate limit errors)
        const prodMessage = this.generateProductionMessage(
          userMessage,
          context
        );
        toastService.error(prodMessage);
      }
    }

    // Rethrow if requested
    if (rethrow) {
      throw error;
    }
  }

  /**
   * Handle an error and return a formatted error response
   * Useful for functions that need to return error information
   */
  public handleErrorWithResult(
    error: unknown,
    context: ErrorContext,
    options: ErrorHandlerOptions = {}
  ): { success: false; error: string; details?: string } {
    const userMessage = this.extractErrorMessage(
      error,
      options.fallbackMessage
    );
    const isDev = this.isDevelopment();

    // Handle the error (logging, toasts, etc.)
    this.handleError(error, context, options);

    // Return structured error response
    return {
      success: false,
      error: userMessage,
      ...(isDev && { details: this.extractErrorDetails(error, context) }),
    };
  }

  /**
   * Create a wrapper function for handling async operations
   */
  public wrapAsync<TArgs extends readonly unknown[], TReturn>(
    fn: (...args: TArgs) => Promise<TReturn>,
    context: ErrorContext,
    options: ErrorHandlerOptions = {}
  ): (...args: TArgs) => Promise<TReturn> {
    return async (...args: TArgs) => {
      try {
        return await fn(...args);
      } catch (error) {
        this.handleError(error, context, { ...options, rethrow: true });
        throw error; // This will never execute but TypeScript needs it
      }
    };
  }

  /**
   * Create a wrapper function for handling sync operations
   */
  public wrapSync<TArgs extends readonly unknown[], TReturn>(
    fn: (...args: TArgs) => TReturn,
    context: ErrorContext,
    options: ErrorHandlerOptions = {}
  ): (...args: TArgs) => TReturn {
    return (...args: TArgs) => {
      try {
        return fn(...args);
      } catch (error) {
        this.handleError(error, context, { ...options, rethrow: true });
        throw error; // This will never execute but TypeScript needs it
      }
    };
  }
}

// Export singleton instance
export const errorHandler = new ErrorHandler();

// Convenience function for handling errors
export const handleError = (
  error: unknown,
  context: ErrorContext,
  options?: ErrorHandlerOptions
): void => {
  errorHandler.handleError(error, context, options);
};

// Convenience function for handling errors with result
export const handleErrorWithResult = (
  error: unknown,
  context: ErrorContext,
  options?: ErrorHandlerOptions
) => {
  return errorHandler.handleErrorWithResult(error, context, options);
};
