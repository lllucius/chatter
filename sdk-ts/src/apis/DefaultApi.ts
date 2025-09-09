/**
 * Generated API client for Default
 */
import { Record } from '../models/index';
import { BaseAPI, Configuration, RequestOptions } from '../runtime';

export class DefaultApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Root
   * Root endpoint.
   */
  public async root(): Promise<Record<string, unknown>> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<Record<string, unknown>>(`/`, requestOptions);
  }
}