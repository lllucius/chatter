/**
 * Generated from OpenAPI schema: ProviderList
 */
import { Provider } from './Provider';


export interface ProviderList {
  providers: Provider[];
  total: number;
  page: number;
  per_page: number;
}
