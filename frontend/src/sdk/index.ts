// Main SDK export file for the new swagger-typescript-api generated SDK

// Export HTTP client and related types
export { HttpClient, ContentType, HttpResponse } from './http-client';
export type { RequestParams, FullRequestParams, ApiConfig, QueryParamsType } from './http-client';

// Export all data contracts (types and interfaces)  
export * from './data-contracts';

// Export Configuration class for backwards compatibility
export interface Configuration {
  basePath?: string;
  accessToken?: string | (() => string);
  headers?: Record<string, string>;
}

// Note: We're not exporting the generated API classes because they have syntax issues.
// Instead, our ChatterSDK class implements the API methods directly using HttpClient.