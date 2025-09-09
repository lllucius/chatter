/**
 * Generated from OpenAPI schema: OAuthConfigSchema
 */
export interface OAuthConfigSchema {
  /** OAuth client ID */
  client_id: string;
  /** OAuth client secret */
  client_secret: string;
  /** OAuth token endpoint URL */
  token_url: string;
  /** OAuth scope */
  scope?: string | null;
}
