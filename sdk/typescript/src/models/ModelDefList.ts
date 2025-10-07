/**
 * Generated from OpenAPI schema: ModelDefList
 */
import { ModelDefWithProvider } from './ModelDefWithProvider';

export interface ModelDefList {
  models: ModelDefWithProvider[];
  total: number;
  limit: number;
  offset: number;
}
