/**
 * Generated from OpenAPI schema: ServerToolsResponse
 */

export interface ServerToolsResponse {
  /** List of server tools */
  tools: ServerToolResponse[];
  /** Total number of tools */
  total_count: number;
  /** Applied limit */
  limit: number;
  /** Applied offset */
  offset: number;
}
