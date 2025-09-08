// Main SDK export file for the new swagger-typescript-api generated SDK

// Export the main API class
export { Api } from './Api';

// Export HTTP client and related types
export { HttpClient, ContentType, HttpResponse } from './http-client';
export type { RequestParams, FullRequestParams, ApiConfig, QueryParamsType } from './http-client';

// Export all data contracts (types and interfaces)
export * from './data-contracts';

// For backwards compatibility, create API class aliases that match the old structure
import { Api } from './Api';

export class AuthenticationApi extends Api {}
export class ABTestingApi extends Api {}
export class AgentsApi extends Api {}
export class AnalyticsApi extends Api {}
export class ChatApi extends Api {}
export class DataManagementApi extends Api {}
export class DefaultApi extends Api {}
export class DocumentsApi extends Api {}
export class EventsApi extends Api {}
export class HealthApi extends Api {}
export class JobsApi extends Api {}
export class ModelRegistryApi extends Api {}
export class PluginsApi extends Api {}
export class ProfilesApi extends Api {}
export class PromptsApi extends Api {}
export class ToolServersApi extends Api {}

// Export Configuration class for backwards compatibility
export interface Configuration {
  basePath?: string;
  accessToken?: string | (() => string);
  headers?: Record<string, string>;
}