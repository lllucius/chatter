/**
 * Generated API client for Default
 */
import { BaseAPI, Configuration, RequestOpts, HTTPMethod } from '../runtime';

export class DefaultApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Root
   * Root endpoint.
   */
  public async root(): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
}