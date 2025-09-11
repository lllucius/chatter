/**
 * Backend health check service
 * Provides utilities to check if the backend is available and handle backend unavailable states
 */

export interface BackendHealthStatus {
  available: boolean;
  lastChecked: Date;
  error?: string;
}

class BackendHealthService {
  private healthStatus: BackendHealthStatus = {
    available: true,
    lastChecked: new Date(),
  };

  private healthCheckInterval: NodeJS.Timeout | null = null;
  private readonly CHECK_INTERVAL = 30000; // 30 seconds

  /**
   * Check if the backend is available by making a simple request
   */
  public async checkBackendHealth(): Promise<BackendHealthStatus> {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    
    try {
      // Try a simple health check endpoint
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

      const response = await fetch(`${baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        this.healthStatus = {
          available: true,
          lastChecked: new Date(),
        };
      } else {
        this.healthStatus = {
          available: false,
          lastChecked: new Date(),
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }
    } catch (error: any) {
      this.healthStatus = {
        available: false,
        lastChecked: new Date(),
        error: this.getErrorMessage(error),
      };
    }

    return this.healthStatus;
  }

  /**
   * Get the current health status without making a new request
   */
  public getCurrentHealthStatus(): BackendHealthStatus {
    return { ...this.healthStatus };
  }

  /**
   * Check if an error is likely due to backend unavailability
   */
  public isBackendUnavailableError(error: any): boolean {
    if (!error) return false;

    const errorString = error.toString().toLowerCase();
    const message = error.message?.toLowerCase() || '';
    
    // Network errors that indicate backend is unavailable
    const networkErrorIndicators = [
      'network error',
      'fetch failed',
      'failed to fetch',
      'connection refused',
      'connection error',
      'econnrefused',
      'net::err_connection_refused',
      'net::err_failed',
      'typeerror: failed to fetch',
      'network request failed',
    ];

    return networkErrorIndicators.some(indicator => 
      errorString.includes(indicator) || message.includes(indicator)
    );
  }

  /**
   * Get a user-friendly error message for backend issues
   */
  public getUserFriendlyErrorMessage(error: any): string {
    if (this.isBackendUnavailableError(error)) {
      return 'Backend server is unavailable. Please check if the server is running and try again.';
    }

    // Handle authentication errors
    if (error?.status === 401 || error?.response?.status === 401) {
      return 'Authentication required. Please log in to continue.';
    }

    // Handle forbidden errors
    if (error?.status === 403 || error?.response?.status === 403) {
      return 'Access denied. You do not have permission to perform this action.';
    }

    // Handle not found errors
    if (error?.status === 404 || error?.response?.status === 404) {
      return 'The requested resource was not found.';
    }

    // Handle server errors
    if (error?.status >= 500 || error?.response?.status >= 500) {
      return 'Server error occurred. Please try again later.';
    }

    // Default message
    return error?.message || 'An unexpected error occurred.';
  }

  /**
   * Start periodic health checks
   */
  public startHealthChecks(): void {
    this.stopHealthChecks(); // Clear any existing interval

    // Initial check
    this.checkBackendHealth();

    // Set up periodic checks
    this.healthCheckInterval = setInterval(() => {
      this.checkBackendHealth();
    }, this.CHECK_INTERVAL);
  }

  /**
   * Stop periodic health checks
   */
  public stopHealthChecks(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }

  private getErrorMessage(error: any): string {
    if (error?.message) return error.message;
    if (typeof error === 'string') return error;
    if (error?.code) return `Error code: ${error.code}`;
    return 'Unknown error occurred';
  }
}

// Export singleton instance
export const backendHealthService = new BackendHealthService();

// Helper function for components
export const checkBackendHealth = () => backendHealthService.checkBackendHealth();
export const isBackendUnavailableError = (error: any) => backendHealthService.isBackendUnavailableError(error);
export const getUserFriendlyErrorMessage = (error: any) => backendHealthService.getUserFriendlyErrorMessage(error);