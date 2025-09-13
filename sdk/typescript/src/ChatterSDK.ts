/* tslint:disable */
/* eslint-disable */
/**
 * Main ChatterSDK class that aggregates all API clients
 */
import { Configuration } from './runtime';
import {
  AbTestingApi,
  AgentsApi,
  AnalyticsApi,
  AuthenticationApi,
  ChatApi,
  ConversationsApi,
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
} from './apis';

export class ChatterSDK {
  private configuration: Configuration;

  public readonly abTesting: AbTestingApi;
  public readonly agents: AgentsApi;
  public readonly analytics: AnalyticsApi;
  public readonly auth: AuthenticationApi;
  public readonly chat: ChatApi;
  public readonly conversations: ConversationsApi;
  public readonly dataManagement: DataManagementApi;
  public readonly default: DefaultApi;
  public readonly documents: DocumentsApi;
  public readonly events: EventsApi;
  public readonly health: HealthApi;
  public readonly jobs: JobsApi;
  public readonly modelRegistry: ModelRegistryApi;
  public readonly plugins: PluginsApi;
  public readonly profiles: ProfilesApi;
  public readonly prompts: PromptsApi;
  public readonly toolServers: ToolServersApi;
  public readonly workflows: WorkflowsApi;

  constructor(configuration?: Configuration) {
    this.configuration = configuration || new Configuration();

    this.abTesting = new AbTestingApi(this.configuration);
    this.agents = new AgentsApi(this.configuration);
    this.analytics = new AnalyticsApi(this.configuration);
    this.auth = new AuthenticationApi(this.configuration);
    this.chat = new ChatApi(this.configuration);
    this.conversations = new ConversationsApi(this.configuration);
    this.dataManagement = new DataManagementApi(this.configuration);
    this.default = new DefaultApi(this.configuration);
    this.documents = new DocumentsApi(this.configuration);
    this.events = new EventsApi(this.configuration);
    this.health = new HealthApi(this.configuration);
    this.jobs = new JobsApi(this.configuration);
    this.modelRegistry = new ModelRegistryApi(this.configuration);
    this.plugins = new PluginsApi(this.configuration);
    this.profiles = new ProfilesApi(this.configuration);
    this.prompts = new PromptsApi(this.configuration);
    this.toolServers = new ToolServersApi(this.configuration);
    this.workflows = new WorkflowsApi(this.configuration);
  }

  /**
   * Create a new SDK instance with the provided configuration merged with the current one
   */
  withConfig(config: Partial<Configuration>): ChatterSDK {
    const newConfig = new Configuration({
      basePath: config.basePath || this.configuration.basePath,
      fetchApi: config.fetchApi || this.configuration.fetchApi,
      middleware: config.middleware || this.configuration.middleware,
      queryParamsStringify: config.queryParamsStringify || this.configuration.queryParamsStringify,
      username: config.username || this.configuration.username,
      password: config.password || this.configuration.password,
      apiKey: config.apiKey || this.configuration.apiKey,
      accessToken: config.accessToken || this.configuration.accessToken,
      headers: { ...this.configuration.headers, ...config.headers },
      credentials: config.credentials || this.configuration.credentials,
    });
    return new ChatterSDK(newConfig);
  }

  /**
   * Create a new SDK instance with authentication
   */
  withAuth(token: string, type: 'bearer' | 'apikey' = 'bearer'): ChatterSDK {
    if (type === 'bearer') {
      return this.withConfig({
        accessToken: () => token,
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } else {
      return this.withConfig({
        apiKey: () => token,
      });
    }
  }
}