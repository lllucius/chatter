/**
 * Enhanced API error handler specifically for authentication and authorization issues
 * Provides centralized handling of 401/403 errors and automatic retry logic
 */

import { withRetry, retryStrategies } from './retry';
import { handleError } from './error-handler';

export interface ApiErrorContext {
  endpoint: string;
  method: string;
  operation: string;
  userId?: string;
}

export interface AuthErrorResponse {
  response?: {
    status: number;
    statusText?: string;
    data?: {
      detail?: string;
      title?: string;
    };
  };
  message?: string;
}

/**
 * Check if an error is an authentication error (401)
 */
export function isAuthError(error: unknown): boolean {
  if (error && typeof error === 'object') {
    const authError = error as AuthErrorResponse;
    return authError.response?.status === 401;
  }
  return false;
}

/**
 * Check if an error is an authorization error (403)
 */
export function isAuthzError(error: unknown): boolean {
  if (error && typeof error === 'object') {
    const authzError = error as AuthErrorResponse;
    return authzError.response?.status === 403;
  }
  return false;
}

/**
 * Handle API errors with special treatment for auth errors
 */
export function handleApiError(
  error: unknown,
  context: ApiErrorContext,
  options: {
    showToast?: boolean;
    logToConsole?: boolean;
    rethrow?: boolean;
  } = {}
): void {
  const { showToast = true, logToConsole = true, rethrow = false } = options;

  if (isAuthError(error)) {
    // For 401 errors, provide specific messaging about authentication
    handleError(
      error,
      {
        source: `API.${context.method}.${context.endpoint}`,
        operation: `${context.operation} (Authentication Required)`,
        userId: context.userId,
        additionalData: {
          endpoint: context.endpoint,
          method: context.method,
        },
      },
      {
        showToast,
        logToConsole,
        rethrow,
        fallbackMessage: 'Please log in to access this resource',
      }
    );
  } else if (isAuthzError(error)) {
    // For 403 errors, provide specific messaging about authorization
    handleError(
      error,
      {
        source: `API.${context.method}.${context.endpoint}`,
        operation: `${context.operation} (Access Denied)`,
        userId: context.userId,
        additionalData: {
          endpoint: context.endpoint,
          method: context.method,
        },
      },
      {
        showToast,
        logToConsole,
        rethrow,
        fallbackMessage: 'You do not have permission to access this resource',
      }
    );
  } else {
    // Handle other API errors normally
    handleError(
      error,
      {
        source: `API.${context.method}.${context.endpoint}`,
        operation: context.operation,
        userId: context.userId,
        additionalData: {
          endpoint: context.endpoint,
          method: context.method,
        },
      },
      {
        showToast,
        logToConsole,
        rethrow,
      }
    );
  }
}

/**
 * Wrapper for API calls that automatically handles errors and retries
 * Specifically designed to handle auth errors gracefully
 */
export function withApiErrorHandling<TArgs extends readonly unknown[], TReturn>(
  apiCall: (...args: TArgs) => Promise<TReturn>,
  context: ApiErrorContext,
  options: {
    showToast?: boolean;
    logToConsole?: boolean;
    enableRetry?: boolean;
    retryAuthErrors?: boolean; // Whether to retry auth errors (usually false)
  } = {}
): (...args: TArgs) => Promise<TReturn> {
  const {
    showToast = true,
    logToConsole = true,
    enableRetry = true,
    retryAuthErrors = false,
  } = options;

  const wrappedCall = async (...args: TArgs): Promise<TReturn> => {
    try {
      if (enableRetry) {
        // Use retry logic but exclude auth errors unless specifically enabled
        const retryStrategy = retryAuthErrors
          ? retryStrategies.serverErrorsOnly
          : {
              shouldRetry: (error: unknown, attempt: number) => {
                // Don't retry auth errors as they likely need user intervention
                if (isAuthError(error) || isAuthzError(error)) {
                  return false;
                }
                // Use default retry strategy for other errors
                return retryStrategies.serverErrorsOnly.shouldRetry!(error, attempt);
              },
            };

        return await withRetry(apiCall, retryStrategy)(...args);
      } else {
        return await apiCall(...args);
      }
    } catch (error) {
      handleApiError(
        error,
        context,
        {
          showToast,
          logToConsole,
          rethrow: true, // Always rethrow so calling code can handle it
        }
      );
      throw error; // This will never execute but TypeScript needs it
    }
  };

  return wrappedCall;
}

/**
 * Create a standardized error message for API availability issues
 */
export function createApiUnavailableMessage(endpoint: string): string {
  return `The ${endpoint} service is currently unavailable. Please try again in a moment or check your connection.`;
}

/**
 * Check if an error indicates the API service is unavailable
 */
export function isApiUnavailable(error: unknown): boolean {
  if (error && typeof error === 'object') {
    const apiError = error as AuthErrorResponse;
    
    // Check for specific status codes that indicate service unavailability
    const status = apiError.response?.status;
    if (status === 503 || status === 502 || status === 504) {
      return true;
    }
    
    // Check for network errors that suggest the API is down
    const message = apiError.message || '';
    if (
      message.includes('Failed to fetch') ||
      message.includes('Network Error') ||
      message.includes('ECONNREFUSED') ||
      message.includes('ENOTFOUND')
    ) {
      return true;
    }
  }
  
  return false;
}

/**
 * Utility for handling common API error scenarios in components
 */
export const apiErrorUtils = {
  isAuthError,
  isAuthzError,
  isApiUnavailable,
  handleApiError,
  withApiErrorHandling,
  createApiUnavailableMessage,
  
  // Common error handlers for specific scenarios
  handleDocumentApiError: (error: unknown, operation: string = 'access documents') =>
    handleApiError(error, {
      endpoint: '/api/v1/documents',
      method: 'GET',
      operation,
    }),
    
  handleWorkflowApiError: (error: unknown, operation: string = 'access workflows') =>
    handleApiError(error, {
      endpoint: '/api/v1/workflows',
      method: 'GET', 
      operation,
    }),
};

export default apiErrorUtils;