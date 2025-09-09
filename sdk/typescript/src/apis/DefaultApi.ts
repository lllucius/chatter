/**
 * Generated API client for Default
 */
import { BaseAPI, Configuration } from '../runtime';

export class DefaultApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Root
   * Root endpoint.
   */
  public async root(): Promise<Record<string, unknown>> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<Record<string, unknown>>(`/`, requestOptions);
  }
}