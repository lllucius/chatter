/**
 * Mock configuration file for testing
 */

export interface ConfigurationParameters {
    basePath?: string;
    accessToken?: string | (() => string);
    username?: string;
    password?: string;
}

export class Configuration {
    basePath: string;
    accessToken?: string | (() => string);
    username?: string;
    password?: string;

    constructor(params: ConfigurationParameters = {}) {
        this.basePath = params.basePath || 'http://localhost:8000';
        this.accessToken = params.accessToken;
        this.username = params.username;
        this.password = params.password;
    }
}
