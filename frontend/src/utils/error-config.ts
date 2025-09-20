/**
 * Configuration for error handling behavior
 * Allows for different error handling strategies in different environments
 */

// Ensure NodeJS types are available
declare var process: {
  env: {
    NODE_ENV?: string;
  };
};

export interface ErrorConfig {
  // Chrome extension error filtering
  filterExtensionErrors: boolean;
  
  // ResizeObserver error filtering
  filterResizeObserverErrors: boolean;
  
  // Authentication error handling
  showAuthenticationErrors: boolean;
  
  // Network error batching to avoid spam
  batchNetworkErrors: boolean;
  batchWindowMs: number;
  
  // Console logging preferences
  logToConsole: boolean;
  logVerboseDetails: boolean;
  
  // Toast notification preferences
  showToastNotifications: boolean;
  toastAutoCloseMs: number;
  
  // Retry configuration for failed requests
  enableRetry: boolean;
  maxRetries: number;
  retryDelayMs: number;
}

class ErrorConfigManager {
  private config: ErrorConfig;

  constructor() {
    this.config = this.getDefaultConfig();
  }

  private getDefaultConfig(): ErrorConfig {
    const isDevelopment = process.env.NODE_ENV === 'development';
    
    return {
      // Always filter extension errors as they're not actionable by users
      filterExtensionErrors: true,
      
      // Always filter ResizeObserver errors as they're benign
      filterResizeObserverErrors: true,
      
      // Always show authentication errors as they require user action
      showAuthenticationErrors: true,
      
      // Batch network errors in production to reduce noise
      batchNetworkErrors: !isDevelopment,
      batchWindowMs: 5000,
      
      // Log to console in development, minimal in production
      logToConsole: isDevelopment,
      logVerboseDetails: isDevelopment,
      
      // Show toast notifications, but with different behavior per environment
      showToastNotifications: true,
      toastAutoCloseMs: isDevelopment ? 8000 : 4000,
      
      // Enable retry for transient errors
      enableRetry: true,
      maxRetries: 3,
      retryDelayMs: 1000,
    };
  }

  public getConfig(): ErrorConfig {
    return { ...this.config };
  }

  public updateConfig(updates: Partial<ErrorConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  public resetToDefaults(): void {
    this.config = this.getDefaultConfig();
  }

  // Convenience methods for common checks
  public shouldFilterExtensionErrors(): boolean {
    return this.config.filterExtensionErrors;
  }

  public shouldShowAuthErrors(): boolean {
    return this.config.showAuthenticationErrors;
  }

  public shouldLogToConsole(): boolean {
    return this.config.logToConsole;
  }

  public shouldShowToasts(): boolean {
    return this.config.showToastNotifications;
  }

  public getToastAutoCloseMs(): number {
    return this.config.toastAutoCloseMs;
  }

  public shouldBatchNetworkErrors(): boolean {
    return this.config.batchNetworkErrors;
  }

  public getBatchWindowMs(): number {
    return this.config.batchWindowMs;
  }
}

// Export singleton instance
export const errorConfig = new ErrorConfigManager();

// Convenience functions
export const getErrorConfig = (): ErrorConfig => errorConfig.getConfig();
export const updateErrorConfig = (updates: Partial<ErrorConfig>): void => 
  errorConfig.updateConfig(updates);