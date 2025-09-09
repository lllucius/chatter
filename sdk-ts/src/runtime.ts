/**
 * Chatter API TypeScript SDK - Runtime
 * Hand-crafted with full type safety
 */

export type Json = unknown;
export type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'OPTIONS' | 'HEAD';
export type HTTPHeaders = Record<string, string>;
export type HTTPQuery = Record<string, string | number | boolean | null | undefined | Array<string | number | boolean>>;
export type HTTPBody = Json | FormData | URLSearchParams | Blob;

export interface RequestOptions {
  method: HTTPMethod;
  headers?: HTTPHeaders;
  query?: HTTPQuery;
  body?: HTTPBody;
}

export interface Configuration {
  basePath: string;
  headers?: HTTPHeaders;
  credentials?: RequestCredentials;
  middleware?: Middleware[];
}

export interface Middleware {
  pre?(context: RequestContext): Promise<RequestContext | void>;
  post?(context: ResponseContext): Promise<ResponseContext | void>;
}

export interface RequestContext {
  url: string;
  init: RequestInit;
}

export interface ResponseContext {
  url: string;
  response: Response;
}

/**
 * Custom error classes for the SDK
 */
export class ChatterSDKError extends Error {
  constructor(message: string, public cause?: Error) {
    super(message);
    this.name = 'ChatterSDKError';
  }
}

export class ChatterAPIError extends ChatterSDKError {
  constructor(
    message: string,
    public status: number,
    public response: Response,
    public body?: unknown
  ) {
    super(message);
    this.name = 'ChatterAPIError';
  }
}

export class ChatterValidationError extends ChatterSDKError {
  constructor(message: string, public field: string) {
    super(message);
    this.name = 'ChatterValidationError';
  }
}

/**
 * Default configuration
 */
export const DEFAULT_CONFIG: Configuration = {
  basePath: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  credentials: 'same-origin',
  middleware: [],
};

/**
 * Utility functions
 */
export function isBlob(value: unknown): value is Blob {
  return typeof Blob !== 'undefined' && value instanceof Blob;
}

export function isFormData(value: unknown): value is FormData {
  return typeof FormData !== 'undefined' && value instanceof FormData;
}

export function isURLSearchParams(value: unknown): value is URLSearchParams {
  return typeof URLSearchParams !== 'undefined' && value instanceof URLSearchParams;
}

export function querystring(params: HTTPQuery): string {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value === null || value === undefined) {
      return;
    }
    
    if (Array.isArray(value)) {
      value.forEach(v => {
        if (v !== null && v !== undefined) {
          searchParams.append(key, String(v));
        }
      });
    } else {
      searchParams.append(key, String(value));
    }
  });
  
  return searchParams.toString();
}

/**
 * Base API class that all generated API classes extend
 */
export abstract class BaseAPI {
  protected configuration: Configuration;

  constructor(configuration: Configuration = DEFAULT_CONFIG) {
    this.configuration = { ...DEFAULT_CONFIG, ...configuration };
  }

  /**
   * Create a new instance with additional middleware
   */
  public withMiddleware(...middleware: Middleware[]): this {
    const newConfig = {
      ...this.configuration,
      middleware: [...(this.configuration.middleware || []), ...middleware],
    };
    
    return new (this.constructor as new (config: Configuration) => this)(newConfig);
  }

  /**
   * Create a new instance with custom headers
   */
  public withHeaders(headers: HTTPHeaders): this {
    const newConfig = {
      ...this.configuration,
      headers: { ...this.configuration.headers, ...headers },
    };
    
    return new (this.constructor as new (config: Configuration) => this)(newConfig);
  }

  /**
   * Create a new instance with custom base path
   */
  public withBasePath(basePath: string): this {
    const newConfig = {
      ...this.configuration,
      basePath,
    };
    
    return new (this.constructor as new (config: Configuration) => this)(newConfig);
  }

  /**
   * Make an HTTP request
   */
  protected async request<T = unknown>(
    path: string,
    options: RequestOptions
  ): Promise<T> {
    const url = this.buildURL(path, options.query);
    
    let body: BodyInit | undefined;
    const headers = { ...this.configuration.headers, ...options.headers };

    // Handle different body types
    if (options.body !== undefined) {
      if (isFormData(options.body) || isURLSearchParams(options.body) || isBlob(options.body)) {
        body = options.body;
        // Remove Content-Type header for FormData (browser will set it with boundary)
        if (isFormData(options.body)) {
          delete headers['Content-Type'];
        }
      } else {
        body = JSON.stringify(options.body);
      }
    }

    const init: RequestInit = {
      method: options.method,
      headers,
      body,
      credentials: this.configuration.credentials,
    };

    const requestContext: RequestContext = { url, init };

    // Apply pre-middleware
    let context = requestContext;
    if (this.configuration.middleware) {
      for (const middleware of this.configuration.middleware) {
        if (middleware.pre) {
          const result = await middleware.pre(context);
          if (result) {
            context = result;
          }
        }
      }
    }

    // Make the request
    let response: Response;
    try {
      response = await fetch(context.url, context.init);
    } catch (error) {
      throw new ChatterSDKError(
        `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        error instanceof Error ? error : undefined
      );
    }

    const responseContext: ResponseContext = { url: context.url, response };

    // Apply post-middleware
    let finalResponseContext = responseContext;
    if (this.configuration.middleware) {
      for (const middleware of this.configuration.middleware) {
        if (middleware.post) {
          const result = await middleware.post(finalResponseContext);
          if (result) {
            finalResponseContext = result;
          }
        }
      }
    }

    // Handle response
    if (!finalResponseContext.response.ok) {
      let errorBody: unknown;
      try {
        const contentType = finalResponseContext.response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          errorBody = await finalResponseContext.response.json();
        } else {
          errorBody = await finalResponseContext.response.text();
        }
      } catch {
        // Ignore JSON parsing errors for error responses
      }

      throw new ChatterAPIError(
        `HTTP ${finalResponseContext.response.status}: ${finalResponseContext.response.statusText}`,
        finalResponseContext.response.status,
        finalResponseContext.response,
        errorBody
      );
    }

    // Parse response
    const contentType = finalResponseContext.response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await finalResponseContext.response.json();
    }
    
    // For non-JSON responses, return the response text
    const text = await finalResponseContext.response.text();
    return (text as unknown) as T;
  }

  private buildURL(path: string, query?: HTTPQuery): string {
    const base = this.configuration.basePath.replace(/\/$/, '');
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    
    let url = `${base}${normalizedPath}`;
    
    if (query && Object.keys(query).length > 0) {
      const queryString = querystring(query);
      if (queryString) {
        url += `?${queryString}`;
      }
    }
    
    return url;
  }
}

/**
 * Authentication helper functions
 */
export function createBearerTokenMiddleware(token: string): Middleware {
  return {
    pre: async (context) => {
      context.init.headers = {
        ...context.init.headers,
        Authorization: `Bearer ${token}`,
      };
      return context;
    },
  };
}

export function createApiKeyMiddleware(apiKey: string, headerName = 'X-API-Key'): Middleware {
  return {
    pre: async (context) => {
      context.init.headers = {
        ...context.init.headers,
        [headerName]: apiKey,
      };
      return context;
    },
  };
}