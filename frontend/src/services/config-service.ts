/**
 * Configuration service for loading runtime configuration from JSON file
 * This service loads configuration at startup time before initializing other services
 */

export interface AppConfig {
  apiBaseUrl: string;
  title?: string;
  version?: string;
}

class ConfigService {
  private config: AppConfig | null = null;
  private loading: boolean = false;
  private loadPromise: Promise<AppConfig> | null = null;

  /**
   * Load configuration from the JSON file
   * This method can be called multiple times safely - subsequent calls return the same promise
   */
  async loadConfig(): Promise<AppConfig> {
    // If already loaded, return the cached config
    if (this.config) {
      return this.config;
    }

    // If already loading, return the existing promise
    if (this.loadPromise) {
      return this.loadPromise;
    }

    // Start loading
    this.loading = true;
    this.loadPromise = this.fetchConfig();

    try {
      this.config = await this.loadPromise;
      return this.config;
    } finally {
      this.loading = false;
    }
  }

  private async fetchConfig(): Promise<AppConfig> {
    try {
      const response = await fetch('/config.json');
      
      if (!response.ok) {
        throw new Error(`Failed to load configuration: ${response.status} ${response.statusText}`);
      }

      const config = await response.json();
      
      // Validate required fields
      if (!config.apiBaseUrl) {
        throw new Error('Configuration must include apiBaseUrl');
      }

      return {
        apiBaseUrl: config.apiBaseUrl,
        title: config.title || 'Chatter AI Platform',
        version: config.version || '0.1.0'
      };
    } catch (error) {
      console.error('Failed to load configuration, using fallback:', error);
      
      // Fallback configuration
      return {
        apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
        title: 'Chatter AI Platform',
        version: '0.1.0'
      };
    }
  }

  /**
   * Get the current configuration
   * Returns null if not loaded yet
   */
  getConfig(): AppConfig | null {
    return this.config;
  }

  /**
   * Check if configuration is currently loading
   */
  isLoading(): boolean {
    return this.loading;
  }

  /**
   * Check if configuration has been loaded
   */
  isLoaded(): boolean {
    return this.config !== null;
  }
}

// Export singleton instance
export const configService = new ConfigService();

// Helper function for easy access to configuration
export const getConfig = (): AppConfig | null => configService.getConfig();

// Helper function to load configuration (returns promise)
export const loadConfig = (): Promise<AppConfig> => configService.loadConfig();