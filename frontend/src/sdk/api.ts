/**
 * Mock API file for testing
 * This is a minimal implementation for testing purposes
 */

import { AxiosResponse } from 'axios';
import { BaseAPI } from './base';
import { Configuration } from './configuration';

export interface HealthResponse {
    status: string;
    timestamp: string;
}

export class HealthApi extends BaseAPI {
    /**
     * Health check endpoint
     */
    public async apiV1HealthGet(options?: any): Promise<AxiosResponse<HealthResponse>> {
        const localVarPath = `/api/v1/health`;
        return this.request({
            url: localVarPath,
            method: 'GET',
        }, options);
    }
}

// Export all APIs
export * from './base';
export * from './configuration';
