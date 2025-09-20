/**
 * Error batching utility to reduce noise from repeated similar errors
 * Groups similar errors together and shows them in batches
 */

import { errorConfig } from './error-config';

export interface BatchedError {
  message: string;
  count: number;
  firstOccurrence: Date;
  lastOccurrence: Date;
  sources: string[];
  samples: unknown[]; // Keep a few examples of the actual errors
}

class ErrorBatcher {
  private batchedErrors = new Map<string, BatchedError>();
  private timers = new Map<string, NodeJS.Timeout>();
  private readonly maxSamples = 3;

  /**
   * Generate a key for grouping similar errors together
   */
  private generateErrorKey(error: unknown, source: string): string {
    let errorType = 'unknown';
    let errorMessage = 'unknown error';

    if (error instanceof Error) {
      errorType = error.constructor.name;
      errorMessage = error.message;
    } else if (error && typeof error === 'object') {
      const errorResponse = error as { response?: { status?: number } };
      if (errorResponse.response?.status) {
        errorType = `HTTP${errorResponse.response.status}`;
      }
      errorMessage = String(error);
    } else {
      errorMessage = String(error);
    }

    // Normalize error message to group similar errors
    const normalizedMessage = errorMessage
      .replace(/\d+/g, 'X') // Replace numbers with X
      .replace(/['"]/g, '') // Remove quotes
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim()
      .toLowerCase();

    return `${errorType}:${normalizedMessage}`;
  }

  /**
   * Add an error to the batch
   */
  public addError(error: unknown, source: string): void {
    const config = errorConfig.getConfig();
    
    if (!config.batchNetworkErrors) {
      // Batching disabled, don't batch errors
      return;
    }

    const key = this.generateErrorKey(error, source);
    const now = new Date();

    if (this.batchedErrors.has(key)) {
      // Update existing batch
      const batch = this.batchedErrors.get(key)!;
      batch.count++;
      batch.lastOccurrence = now;
      
      // Add source if not already included
      if (!batch.sources.includes(source)) {
        batch.sources.push(source);
      }
      
      // Add sample if we don't have too many
      if (batch.samples.length < this.maxSamples) {
        batch.samples.push(error);
      }
    } else {
      // Create new batch
      let message = 'Unknown error';
      if (error instanceof Error) {
        message = error.message;
      } else if (error && typeof error === 'object') {
        const errorResponse = error as { response?: { status?: number; statusText?: string } };
        if (errorResponse.response?.status) {
          message = `HTTP ${errorResponse.response.status}${
            errorResponse.response.statusText ? ` ${errorResponse.response.statusText}` : ''
          }`;
        } else {
          message = JSON.stringify(error);
        }
      } else {
        message = String(error);
      }

      this.batchedErrors.set(key, {
        message,
        count: 1,
        firstOccurrence: now,
        lastOccurrence: now,
        sources: [source],
        samples: [error],
      });

      // Set timer to flush this batch
      const timer = setTimeout(() => {
        this.flushBatch(key);
      }, config.batchWindowMs);
      
      this.timers.set(key, timer);
    }
  }

  /**
   * Flush a specific batch and report it
   */
  private flushBatch(key: string): void {
    const batch = this.batchedErrors.get(key);
    if (!batch) return;

    // Clear timer
    const timer = this.timers.get(key);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(key);
    }

    // Remove from batched errors
    this.batchedErrors.delete(key);

    // Report the batched error
    this.reportBatchedError(batch);
  }

  /**
   * Report a batched error to the console or other logging system
   */
  private reportBatchedError(batch: BatchedError): void {
    const config = errorConfig.getConfig();
    
    if (!config.logToConsole) {
      return;
    }

    const timeSpan = batch.lastOccurrence.getTime() - batch.firstOccurrence.getTime();
    const timeSpanStr = timeSpan > 1000 ? `${Math.round(timeSpan / 1000)}s` : `${timeSpan}ms`;

    if (batch.count === 1) {
      // Single error, log normally
      // eslint-disable-next-line no-console
      console.error(`[Error Batch] ${batch.message}`, batch.samples[0]);
    } else {
      // Multiple errors, log as batch
      // eslint-disable-next-line no-console
      console.warn(
        `[Error Batch] ${batch.message} (${batch.count} occurrences over ${timeSpanStr})`,
        {
          count: batch.count,
          sources: batch.sources,
          timeSpan: timeSpanStr,
          samples: batch.samples,
        }
      );
    }
  }

  /**
   * Flush all pending batches immediately
   */
  public flushAll(): void {
    const keys = Array.from(this.batchedErrors.keys());
    keys.forEach(key => this.flushBatch(key));
  }

  /**
   * Clear all batches without reporting them
   */
  public clear(): void {
    // Clear all timers
    this.timers.forEach(timer => clearTimeout(timer));
    this.timers.clear();
    
    // Clear all batches
    this.batchedErrors.clear();
  }

  /**
   * Get current batch statistics
   */
  public getStats(): { totalBatches: number; totalErrors: number } {
    let totalErrors = 0;
    for (const batch of this.batchedErrors.values()) {
      totalErrors += batch.count;
    }
    
    return {
      totalBatches: this.batchedErrors.size,
      totalErrors,
    };
  }

  /**
   * Check if an error should be batched
   */
  public shouldBatchError(error: unknown): boolean {
    const config = errorConfig.getConfig();
    
    if (!config.batchNetworkErrors) {
      return false;
    }

    // Batch network errors and server errors
    if (error && typeof error === 'object') {
      const errorResponse = error as { response?: { status?: number }; code?: string };
      
      // Batch network errors
      if (errorResponse.code === 'NETWORK_ERROR') {
        return true;
      }
      
      // Batch server errors (5xx)
      const status = errorResponse.response?.status;
      if (status && status >= 500) {
        return true;
      }
      
      // Batch CORS errors
      const errorMessage = (error as Error)?.message || '';
      if (errorMessage.includes('CORS') || errorMessage.includes('Failed to fetch')) {
        return true;
      }
    }

    return false;
  }
}

// Export singleton instance
export const errorBatcher = new ErrorBatcher();

// Convenience functions
export const batchError = (error: unknown, source: string): void => {
  errorBatcher.addError(error, source);
};

export const flushErrorBatches = (): void => {
  errorBatcher.flushAll();
};

export const clearErrorBatches = (): void => {
  errorBatcher.clear();
};

export const getErrorBatchStats = () => {
  return errorBatcher.getStats();
};