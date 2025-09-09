/**
 * Main Chatter SDK Client
 * Hand-crafted TypeScript SDK with full type safety
 */

import {
  AbTestingApi,
  AgentsApi,
  AnalyticsApi,
  AuthenticationApi,
  ChatApi,
  DataManagementApi,
  DefaultApi,
  DocumentsApi,
  EventsApi,
  HealthApi,
  JobsApi,
  ModelRegistryApi,
  PluginsApi,
  ProfilesApi,
  PromptsApi,
  ToolServersApi,
  WorkflowsApi,
} from './apis/index';

import {
  Configuration,
  DEFAULT_CONFIG,
  createBearerTokenMiddleware,
  createApiKeyMiddleware,
  Middleware,
} from './runtime';

/**
 * Configuration options for the Chatter SDK
 */
export interface ChatterSDKOptions {
  /** Base URL for the Chatter API */
  basePath?: string;
  /** Bearer token for authentication */
  bearerToken?: string;
  /** API key for authentication */
  apiKey?: string;
  /** Custom headers to include with requests */
  headers?: Record<string, string>;
  /** Request credentials mode */
  credentials?: RequestCredentials;
  /** Custom middleware */
  middleware?: Middleware[];
}

/**
 * Main Chatter SDK Client
 * 
 * Provides access to all Chatter API endpoints with full type safety.
 * 
 * @example
 * ```typescript
 * // Basic usage
 * const chatter = new ChatterSDK({
 *   basePath: 'https://api.chatter.example.com',
 *   bearerToken: 'your-bearer-token'
 * });
 * 
 * // Chat with the API
 * const response = await chatter.chat.chatChat({
 *   message: 'Hello, how are you?',
 *   workflow: 'plain'
 * });
 * 
 * // List documents
 * const documents = await chatter.documents.listDocuments();
 * 
 * // Create an agent
 * const agent = await chatter.agents.createAgent({
 *   name: 'my-agent',
 *   type: 'assistant',
 *   capabilities: ['chat', 'search']
 * });
 * ```
 */
export class ChatterSDK {
  /** A/B Testing API */
  public readonly abTesting: AbTestingApi;
  /** Agents API */
  public readonly agents: AgentsApi;
  /** Analytics API */
  public readonly analytics: AnalyticsApi;
  /** Authentication API */
  public readonly auth: AuthenticationApi;
  /** Chat API */
  public readonly chat: ChatApi;
  /** Data Management API */
  public readonly dataManagement: DataManagementApi;
  /** Default API */
  public readonly default: DefaultApi;
  /** Documents API */
  public readonly documents: DocumentsApi;
  /** Events API */
  public readonly events: EventsApi;
  /** Health API */
  public readonly health: HealthApi;
  /** Jobs API */
  public readonly jobs: JobsApi;
  /** Model Registry API */
  public readonly models: ModelRegistryApi;
  /** Plugins API */
  public readonly plugins: PluginsApi;
  /** Profiles API */
  public readonly profiles: ProfilesApi;
  /** Prompts API */
  public readonly prompts: PromptsApi;
  /** Tool Servers API */
  public readonly toolServers: ToolServersApi;
  /** Workflows API */
  public readonly workflows: WorkflowsApi;

  private readonly configuration: Configuration;

  constructor(options: ChatterSDKOptions = {}) {
    // Build configuration
    const middleware: Middleware[] = [...(options.middleware || [])];

    // Add authentication middleware
    if (options.bearerToken) {
      middleware.push(createBearerTokenMiddleware(options.bearerToken));
    } else if (options.apiKey) {
      middleware.push(createApiKeyMiddleware(options.apiKey));
    }

    this.configuration = {
      ...DEFAULT_CONFIG,
      basePath: options.basePath || DEFAULT_CONFIG.basePath,
      headers: { ...DEFAULT_CONFIG.headers, ...options.headers },
      credentials: options.credentials || DEFAULT_CONFIG.credentials,
      middleware,
    };

    // Initialize all API clients
    this.abTesting = new AbTestingApi(this.configuration);
    this.agents = new AgentsApi(this.configuration);
    this.analytics = new AnalyticsApi(this.configuration);
    this.auth = new AuthenticationApi(this.configuration);
    this.chat = new ChatApi(this.configuration);
    this.dataManagement = new DataManagementApi(this.configuration);
    this.default = new DefaultApi(this.configuration);
    this.documents = new DocumentsApi(this.configuration);
    this.events = new EventsApi(this.configuration);
    this.health = new HealthApi(this.configuration);
    this.jobs = new JobsApi(this.configuration);
    this.models = new ModelRegistryApi(this.configuration);
    this.plugins = new PluginsApi(this.configuration);
    this.profiles = new ProfilesApi(this.configuration);
    this.prompts = new PromptsApi(this.configuration);
    this.toolServers = new ToolServersApi(this.configuration);
    this.workflows = new WorkflowsApi(this.configuration);
  }

  /**
   * Create a new SDK instance with custom configuration
   */
  public withConfig(options: ChatterSDKOptions): ChatterSDK {
    return new ChatterSDK({ ...this.getOptions(), ...options });
  }

  /**
   * Create a new SDK instance with a different base path
   */
  public withBasePath(basePath: string): ChatterSDK {
    return this.withConfig({ basePath });
  }

  /**
   * Create a new SDK instance with authentication
   */
  public withAuth(token: string, type: 'bearer' | 'apiKey' = 'bearer'): ChatterSDK {
    if (type === 'bearer') {
      return this.withConfig({ bearerToken: token });
    } else {
      return this.withConfig({ apiKey: token });
    }
  }

  /**
   * Create a new SDK instance with custom headers
   */
  public withHeaders(headers: Record<string, string>): ChatterSDK {
    return this.withConfig({ headers });
  }

  /**
   * Create a new SDK instance with additional middleware
   */
  public withMiddleware(...middleware: Middleware[]): ChatterSDK {
    return this.withConfig({ 
      middleware: [...(this.configuration.middleware || []), ...middleware]
    });
  }

  /**
   * Get the current configuration as options
   */
  private getOptions(): ChatterSDKOptions {
    return {
      basePath: this.configuration.basePath,
      headers: { ...this.configuration.headers },
      credentials: this.configuration.credentials,
      middleware: [...(this.configuration.middleware || [])],
    };
  }
}

/**
 * Default export - the main SDK class
 */
export default ChatterSDK;

// Re-export everything for convenience
export * from './models/index';
export * from './apis/index';
export * from './runtime';