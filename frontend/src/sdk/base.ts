/**
 * Mock base API file for testing
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { Configuration } from './configuration';

export class BaseAPI {
    protected configuration: Configuration;
    protected axios: AxiosInstance;

    constructor(configuration: Configuration, axios?: AxiosInstance) {
        this.configuration = configuration;
        this.axios = axios || this.createAxiosInstance();
    }

    protected createAxiosInstance(): AxiosInstance {
        const instance = axios.create({
            baseURL: this.configuration.basePath,
        });

        // Add auth interceptor if access token is available
        if (this.configuration.accessToken) {
            instance.interceptors.request.use((config) => {
                const token = typeof this.configuration.accessToken === 'function' 
                    ? this.configuration.accessToken() 
                    : this.configuration.accessToken;
                
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            });
        }

        return instance;
    }

    protected async request<T = any>(requestConfig: AxiosRequestConfig, options?: any): Promise<AxiosResponse<T>> {
        return this.axios.request<T>({
            ...requestConfig,
            ...options,
        });
    }
}
