/**
 * Generated from OpenAPI schema: Body_list_agents_api_v1_agents__get
 */
import { PaginationRequest } from './PaginationRequest';
import { SortingRequest } from './SortingRequest';

export interface Body_list_agents_api_v1_agents__get {
  pagination?: PaginationRequest;
  sorting?: SortingRequest;
  tags?: string[] | null;
}
