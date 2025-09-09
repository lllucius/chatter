/**
 * Generated from OpenAPI schema: AvailableProvidersResponse
 */
export interface AvailableProvidersResponse {
  /** Available LLM providers with their configurations */
  providers: Record<string, unknown>;
  /** Total number of available providers */
  total_providers: number;
  /** Features supported by each provider */
  supported_features: Record<string, string[]>;
}
