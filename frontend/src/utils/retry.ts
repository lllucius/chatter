/**
 * Retry utility for handling transient errors
 * Provides configurable retry logic for API calls and other operations
 */

import { errorConfig } from './error-config';

export interface RetryOptions {
  maxRetries?: number;
  delayMs?: number;
  backoffMultiplier?: number;
  shouldRetry?: (error: unknown, attempt: number) => boolean;
  onRetry?: (error: unknown, attempt: number) => void;
}

export interface RetryResult<T> {
  success: boolean;
  data?: T;
  error?: unknown;
  attempts: number;
}

/**
 * Default function to determine if an error should trigger a retry
 */
function defaultShouldRetry(error: unknown, attempt: number): boolean {
  // Don't retry if we've exceeded max attempts
  const config = errorConfig.getConfig();
  if (attempt >= config.maxRetries) {
    return false;
  }

  // Check if error is retryable
  if (error && typeof error === 'object') {
    const errorResponse = error as { response?: { status?: number }; code?: string };
    
    // Retry for network errors
    if (errorResponse.code === 'NETWORK_ERROR') {
      return true;
    }
    
    // Retry for certain HTTP status codes
    const status = errorResponse.response?.status;
    if (status) {
      // Retry for server errors (5xx) and rate limiting (429)
      if (status >= 500 || status === 429) {
        return true;
      }
      // Don't retry for client errors (4xx) except 429
      if (status >= 400 && status < 500) {
        return false;
      }
    }
    
    // Retry for timeout errors
    const errorMessage = (error as Error)?.message || '';
    if (errorMessage.includes('timeout') || errorMessage.includes('ECONNRESET')) {
      return true;
    }
  }
  
  return false;
}

/**
 * Default retry callback that logs retry attempts
 */
function defaultOnRetry(error: unknown, attempt: number): void {
  if (errorConfig.shouldLogToConsole()) {
    // eslint-disable-next-line no-console
    console.warn(`[Retry] Attempt ${attempt} failed, retrying...`, error);
  }
}

/**
 * Sleep for the specified number of milliseconds
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry an async operation with configurable retry logic
 */
export async function retryAsync<T>(
  operation: () => Promise<T>,
  options: RetryOptions = {}
): Promise<RetryResult<T>> {
  const config = errorConfig.getConfig();
  
  const {
    maxRetries = config.maxRetries,
    delayMs = config.retryDelayMs,
    backoffMultiplier = 2,
    shouldRetry = defaultShouldRetry,
    onRetry = defaultOnRetry,
  } = options;

  let lastError: unknown;
  let attempt = 0;

  while (attempt <= maxRetries) {
    try {
      const result = await operation();
      return {
        success: true,
        data: result,
        attempts: attempt + 1,
      };
    } catch (error) {
      lastError = error;
      attempt++;

      // Check if we should retry
      if (attempt <= maxRetries && shouldRetry(error, attempt)) {
        onRetry(error, attempt);
        
        // Calculate delay with exponential backoff
        const delay = delayMs * Math.pow(backoffMultiplier, attempt - 1);
        await sleep(delay);
        
        continue;
      }

      // Max retries exceeded or error is not retryable
      break;
    }
  }

  return {
    success: false,
    error: lastError,
    attempts: attempt,
  };
}

/**
 * Wrapper for API calls that automatically applies retry logic
 */
export function withRetry<TArgs extends readonly unknown[], TReturn>(
  apiCall: (...args: TArgs) => Promise<TReturn>,
  options: RetryOptions = {}
): (...args: TArgs) => Promise<TReturn> {
  return async (...args: TArgs): Promise<TReturn> => {
    const result = await retryAsync(() => apiCall(...args), options);
    
    if (result.success && result.data !== undefined) {
      return result.data;
    }
    
    // If retry failed, throw the last error
    throw result.error;
  };
}

/**
 * Check if an error is likely to be transient and retryable
 */
export function isTransientError(error: unknown): boolean {
  return defaultShouldRetry(error, 0);
}

/**
 * Create a custom retry strategy for specific error types
 */
export function createRetryStrategy(
  shouldRetryFn: (error: unknown, attempt: number) => boolean,
  onRetryFn?: (error: unknown, attempt: number) => void
): RetryOptions {
  return {
    shouldRetry: shouldRetryFn,
    onRetry: onRetryFn || defaultOnRetry,
  };
}

// Common retry strategies
export const retryStrategies = {
  // Only retry for server errors and network issues
  serverErrorsOnly: createRetryStrategy((error, attempt) => {
    const config = errorConfig.getConfig();
    if (attempt >= config.maxRetries) return false;
    
    if (error && typeof error === 'object') {
      const status = (error as { response?: { status?: number } }).response?.status;
      return status !== undefined && status >= 500;
    }
    return false;
  }),
  
  // Retry for network errors only
  networkErrorsOnly: createRetryStrategy((error, attempt) => {
    const config = errorConfig.getConfig();
    if (attempt >= config.maxRetries) return false;
    
    const errorMessage = (error as Error)?.message || '';
    return (
      errorMessage.includes('Failed to fetch') ||
      errorMessage.includes('Network Error') ||
      errorMessage.includes('ECONNRESET') ||
      (error as { code?: string })?.code === 'NETWORK_ERROR'
    );
  }),
  
  // Never retry - useful for disabling retry for specific calls
  noRetry: createRetryStrategy(() => false),
};