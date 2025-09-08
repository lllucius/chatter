/* eslint-disable */
/* tslint:disable */
// @ts-nocheck
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

/**
 * VariantAllocation
 * Variant allocation strategies.
 */
export enum VariantAllocation {
  Equal = "equal",
  Weighted = "weighted",
  GradualRollout = "gradual_rollout",
  UserAttribute = "user_attribute",
}

/**
 * UserRole
 * User roles for tool access.
 */
export enum UserRole {
  Guest = "guest",
  User = "user",
  PowerUser = "power_user",
  Admin = "admin",
  SuperAdmin = "super_admin",
}

/**
 * ToolStatus
 * Enumeration for tool status.
 */
export enum ToolStatus {
  Enabled = "enabled",
  Disabled = "disabled",
  Unavailable = "unavailable",
  Error = "error",
}

/**
 * ToolAccessLevel
 * Access levels for tools.
 */
export enum ToolAccessLevel {
  None = "none",
  Read = "read",
  Execute = "execute",
  Admin = "admin",
}

/**
 * TestType
 * Types of A/B tests.
 */
export enum TestType {
  Prompt = "prompt",
  Model = "model",
  Parameter = "parameter",
  Workflow = "workflow",
  Template = "template",
}

/**
 * TestStatus
 * A/B test status.
 */
export enum TestStatus {
  Draft = "draft",
  Running = "running",
  Paused = "paused",
  Completed = "completed",
  Cancelled = "cancelled",
}

/**
 * ServerStatus
 * Enumeration for server status.
 */
export enum ServerStatus {
  Enabled = "enabled",
  Disabled = "disabled",
  Error = "error",
  Starting = "starting",
  Stopping = "stopping",
}

/**
 * ReductionStrategy
 * Dimensionality reduction strategies.
 */
export enum ReductionStrategy {
  None = "none",
  Truncate = "truncate",
  Reducer = "reducer",
}

/**
 * ReadinessStatus
 * Readiness status enumeration.
 */
export enum ReadinessStatus {
  Ready = "ready",
  NotReady = "not_ready",
}

/**
 * ProviderType
 * Types of AI providers.
 */
export enum ProviderType {
  Openai = "openai",
  Anthropic = "anthropic",
  Google = "google",
  Cohere = "cohere",
  Mistral = "mistral",
}

/**
 * PromptType
 * Enumeration for prompt types.
 */
export enum PromptType {
  System = "system",
  User = "user",
  Assistant = "assistant",
  Chain = "chain",
  Template = "template",
}

/**
 * PromptCategory
 * Enumeration for prompt categories.
 */
export enum PromptCategory {
  General = "general",
  Creative = "creative",
  Analytical = "analytical",
  Technical = "technical",
  Educational = "educational",
  Business = "business",
  Coding = "coding",
  Custom = "custom",
}

/**
 * ProfileType
 * Enumeration for profile types.
 */
export enum ProfileType {
  Conversational = "conversational",
  Analytical = "analytical",
  Creative = "creative",
  Technical = "technical",
  Custom = "custom",
}

/**
 * PluginType
 * Types of plugins.
 */
export enum PluginType {
  Tool = "tool",
  Workflow = "workflow",
  Integration = "integration",
  Middleware = "middleware",
  Handler = "handler",
  Extension = "extension",
}

/**
 * PluginStatus
 * Plugin status.
 */
export enum PluginStatus {
  Installed = "installed",
  Active = "active",
  Inactive = "inactive",
  Error = "error",
  Updating = "updating",
}

/**
 * ModelType
 * Types of AI models.
 */
export enum ModelType {
  Llm = "llm",
  Chat = "chat",
  Embedding = "embedding",
}

/**
 * MetricType
 * Types of metrics to track.
 */
export enum MetricType {
  ResponseTime = "response_time",
  UserSatisfaction = "user_satisfaction",
  Accuracy = "accuracy",
  Engagement = "engagement",
  Conversion = "conversion",
  ErrorRate = "error_rate",
  TokenUsage = "token_usage",
  Custom = "custom",
}

/**
 * MessageRole
 * Enumeration for message roles.
 */
export enum MessageRole {
  User = "user",
  Assistant = "assistant",
  System = "system",
  Tool = "tool",
}

/**
 * JobStatus
 * Job execution status.
 */
export enum JobStatus {
  Pending = "pending",
  Running = "running",
  Completed = "completed",
  Failed = "failed",
  Cancelled = "cancelled",
  Retrying = "retrying",
}

/**
 * JobPriority
 * Job priority levels.
 */
export enum JobPriority {
  Low = "low",
  Normal = "normal",
  High = "high",
  Critical = "critical",
}

/**
 * HealthStatus
 * Health status enumeration.
 */
export enum HealthStatus {
  Healthy = "healthy",
  Alive = "alive",
  Unhealthy = "unhealthy",
}

/**
 * ExportScope
 * Data export scope.
 */
export enum ExportScope {
  User = "user",
  Conversation = "conversation",
  Document = "document",
  Analytics = "analytics",
  Full = "full",
  Custom = "custom",
}

/**
 * DocumentType
 * Enumeration for document types.
 */
export enum DocumentType {
  Pdf = "pdf",
  Text = "text",
  Markdown = "markdown",
  Html = "html",
  Doc = "doc",
  Docx = "docx",
  Rtf = "rtf",
  Odt = "odt",
  Csv = "csv",
  Json = "json",
  Xml = "xml",
  Other = "other",
}

/**
 * DocumentStatus
 * Enumeration for document processing status.
 */
export enum DocumentStatus {
  Pending = "pending",
  Processing = "processing",
  Processed = "processed",
  Failed = "failed",
  Archived = "archived",
}

/**
 * DistanceMetric
 * Distance metrics for vector similarity.
 */
export enum DistanceMetric {
  Cosine = "cosine",
  L2 = "l2",
  Ip = "ip",
}

/**
 * DataFormat
 * Supported data formats.
 */
export enum DataFormat {
  Json = "json",
  Csv = "csv",
  Xml = "xml",
  Parquet = "parquet",
  Sql = "sql",
}

/**
 * ConversationStatus
 * Enumeration for conversation status.
 */
export enum ConversationStatus {
  Active = "active",
  Archived = "archived",
  Deleted = "deleted",
}

/**
 * BackupType
 * Types of backups.
 */
export enum BackupType {
  Full = "full",
  Incremental = "incremental",
  Differential = "differential",
}

/**
 * AgentType
 * Types of AI agents.
 */
export enum AgentType {
  Conversational = "conversational",
  TaskOriented = "task_oriented",
  Analytical = "analytical",
  Creative = "creative",
  Research = "research",
  Support = "support",
  Specialist = "specialist",
}

/**
 * AgentStatus
 * Agent status.
 */
export enum AgentStatus {
  Active = "active",
  Inactive = "inactive",
  Training = "training",
  Error = "error",
  Maintenance = "maintenance",
}

/**
 * AgentCapability
 * Agent capabilities.
 */
export enum AgentCapability {
  NaturalLanguage = "natural_language",
  Memory = "memory",
  CodeGeneration = "code_generation",
  ToolUse = "tool_use",
  Analytical = "analytical",
  Creative = "creative",
  Research = "research",
  Support = "support",
}

/**
 * ABTestActionResponse
 * Response schema for test actions (start, pause, complete).
 */
export interface ABTestActionResponse {
  /**
   * Success
   * Whether action was successful
   */
  success: boolean;
  /**
   * Message
   * Action result message
   */
  message: string;
  /**
   * Test Id
   * Test ID
   */
  test_id: string;
  /** New test status */
  new_status: TestStatus;
}

/**
 * ABTestCreateRequest
 * Request schema for creating an A/B test.
 */
export interface ABTestCreateRequest {
  /**
   * Name
   * Test name
   */
  name: string;
  /**
   * Description
   * Test description
   */
  description: string;
  /** Type of test */
  test_type: TestType;
  /** Allocation strategy */
  allocation_strategy: VariantAllocation;
  /**
   * Variants
   * Test variants
   * @minItems 2
   */
  variants: TestVariant[];
  /**
   * Metrics
   * Metrics to track
   * @minItems 1
   */
  metrics: MetricType[];
  /**
   * Duration Days
   * Test duration in days
   * @min 1
   * @max 365
   * @default 7
   */
  duration_days?: number;
  /**
   * Min Sample Size
   * Minimum sample size
   * @min 10
   * @default 100
   */
  min_sample_size?: number;
  /**
   * Confidence Level
   * Statistical confidence level
   * @min 0.5
   * @max 0.99
   * @default 0.95
   */
  confidence_level?: number;
  /**
   * Target Audience
   * Target audience criteria
   */
  target_audience?: Record<string, any> | null;
  /**
   * Traffic Percentage
   * Percentage of traffic to include
   * @min 0.1
   * @max 100
   * @default 100
   */
  traffic_percentage?: number;
  /**
   * Tags
   * Test tags
   */
  tags?: string[];
  /**
   * Metadata
   * Additional metadata
   */
  metadata?: Record<string, any>;
}

/**
 * ABTestDeleteResponse
 * Response schema for test deletion.
 */
export interface ABTestDeleteResponse {
  /**
   * Success
   * Whether deletion was successful
   */
  success: boolean;
  /**
   * Message
   * Deletion result message
   */
  message: string;
}

/**
 * ABTestListResponse
 * Response schema for A/B test list.
 */
export interface ABTestListResponse {
  /**
   * Tests
   * List of tests
   */
  tests: ABTestResponse[];
  /**
   * Total
   * Total number of tests
   */
  total: number;
}

/**
 * ABTestMetricsResponse
 * Response schema for A/B test metrics.
 */
export interface ABTestMetricsResponse {
  /**
   * Test Id
   * Test ID
   */
  test_id: string;
  /**
   * Metrics
   * Current metrics
   */
  metrics: TestMetric[];
  /**
   * Participant Count
   * Current participant count
   */
  participant_count: number;
  /**
   * Last Updated
   * Last metrics update
   * @format date-time
   */
  last_updated: string;
}

/**
 * ABTestResponse
 * Response schema for A/B test data.
 */
export interface ABTestResponse {
  /**
   * Id
   * Test ID
   */
  id: string;
  /**
   * Name
   * Test name
   */
  name: string;
  /**
   * Description
   * Test description
   */
  description: string;
  /** Type of test */
  test_type: TestType;
  /** Test status */
  status: TestStatus;
  /** Allocation strategy */
  allocation_strategy: VariantAllocation;
  /**
   * Variants
   * Test variants
   */
  variants: TestVariant[];
  /**
   * Metrics
   * Metrics being tracked
   */
  metrics: MetricType[];
  /**
   * Duration Days
   * Test duration in days
   */
  duration_days: number;
  /**
   * Min Sample Size
   * Minimum sample size
   */
  min_sample_size: number;
  /**
   * Confidence Level
   * Statistical confidence level
   */
  confidence_level: number;
  /**
   * Target Audience
   * Target audience criteria
   */
  target_audience?: Record<string, any> | null;
  /**
   * Traffic Percentage
   * Percentage of traffic included
   */
  traffic_percentage: number;
  /**
   * Start Date
   * Test start date
   */
  start_date?: string | null;
  /**
   * End Date
   * Test end date
   */
  end_date?: string | null;
  /**
   * Participant Count
   * Number of participants
   * @default 0
   */
  participant_count?: number;
  /**
   * Created At
   * Creation timestamp
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update timestamp
   * @format date-time
   */
  updated_at: string;
  /**
   * Created By
   * Creator
   */
  created_by: string;
  /**
   * Tags
   * Test tags
   */
  tags: string[];
  /**
   * Metadata
   * Additional metadata
   */
  metadata: Record<string, any>;
}

/**
 * ABTestResultsResponse
 * Response schema for A/B test results.
 */
export interface ABTestResultsResponse {
  /**
   * Test Id
   * Test ID
   */
  test_id: string;
  /**
   * Test Name
   * Test name
   */
  test_name: string;
  /** Test status */
  status: TestStatus;
  /**
   * Metrics
   * Metric results by variant
   */
  metrics: TestMetric[];
  /**
   * Statistical Significance
   * Statistical significance by metric
   */
  statistical_significance: Record<string, boolean>;
  /**
   * Confidence Intervals
   * Confidence intervals
   */
  confidence_intervals: Record<string, Record<string, number[]>>;
  /**
   * Winning Variant
   * Recommended winning variant
   */
  winning_variant?: string | null;
  /**
   * Recommendation
   * Action recommendation
   */
  recommendation: string;
  /**
   * Generated At
   * Results generation timestamp
   * @format date-time
   */
  generated_at: string;
  /**
   * Sample Size
   * Total sample size
   */
  sample_size: number;
  /**
   * Duration Days
   * Test duration so far
   */
  duration_days: number;
}

/**
 * ABTestUpdateRequest
 * Request schema for updating an A/B test.
 */
export interface ABTestUpdateRequest {
  /**
   * Name
   * Test name
   */
  name?: string | null;
  /**
   * Description
   * Test description
   */
  description?: string | null;
  /** Test status */
  status?: TestStatus | null;
  /**
   * Duration Days
   * Test duration in days
   */
  duration_days?: number | null;
  /**
   * Min Sample Size
   * Minimum sample size
   */
  min_sample_size?: number | null;
  /**
   * Confidence Level
   * Statistical confidence level
   */
  confidence_level?: number | null;
  /**
   * Traffic Percentage
   * Traffic percentage
   */
  traffic_percentage?: number | null;
  /**
   * Tags
   * Test tags
   */
  tags?: string[] | null;
  /**
   * Metadata
   * Additional metadata
   */
  metadata?: Record<string, any> | null;
}

/**
 * APIKeyCreate
 * Schema for API key creation.
 */
export interface APIKeyCreate {
  /**
   * Name
   * API key name
   * @minLength 1
   * @maxLength 100
   */
  name: string;
}

/**
 * APIKeyResponse
 * Schema for API key response.
 */
export interface APIKeyResponse {
  /**
   * Id
   * User ID
   */
  id: string;
  /**
   * Api Key
   * API key
   */
  api_key: string;
  /**
   * Api Key Name
   * API key name
   */
  api_key_name: string;
}

/**
 * APIKeyRevokeResponse
 * Schema for API key revoke response.
 */
export interface APIKeyRevokeResponse {
  /**
   * Message
   * Success message
   */
  message: string;
}

/**
 * AccountDeactivateResponse
 * Schema for account deactivation response.
 */
export interface AccountDeactivateResponse {
  /**
   * Message
   * Success message
   */
  message: string;
}

/**
 * AgentBulkCreateRequest
 * Request schema for bulk agent creation.
 */
export interface AgentBulkCreateRequest {
  /**
   * Agents
   * List of agents to create (max 10)
   * @maxItems 10
   * @minItems 1
   */
  agents: AgentCreateRequest[];
}

/**
 * AgentBulkCreateResponse
 * Response schema for bulk agent creation.
 */
export interface AgentBulkCreateResponse {
  /**
   * Created
   * Successfully created agents
   */
  created: AgentResponse[];
  /**
   * Failed
   * Failed agent creations with errors
   */
  failed: Record<string, any>[];
  /**
   * Total Requested
   * Total agents requested
   */
  total_requested: number;
  /**
   * Total Created
   * Total agents successfully created
   */
  total_created: number;
}

/**
 * AgentBulkDeleteRequest
 * Request schema for bulk agent deletion.
 */
export interface AgentBulkDeleteRequest {
  /**
   * Agent Ids
   * List of agent IDs to delete (max 50)
   * @maxItems 50
   * @minItems 1
   */
  agent_ids: string[];
}

/**
 * AgentCreateRequest
 * Request schema for creating an agent.
 */
export interface AgentCreateRequest {
  /**
   * Name
   * Agent name
   */
  name: string;
  /**
   * Description
   * Agent description
   */
  description: string;
  /** Type of agent */
  agent_type: AgentType;
  /**
   * System Prompt
   * System prompt for the agent
   */
  system_prompt: string;
  /**
   * Personality Traits
   * Agent personality traits
   */
  personality_traits?: string[];
  /**
   * Knowledge Domains
   * Knowledge domains
   */
  knowledge_domains?: string[];
  /**
   * Response Style
   * Response style
   * @default "professional"
   */
  response_style?: string;
  /**
   * Capabilities
   * Agent capabilities
   */
  capabilities?: AgentCapability[];
  /**
   * Available Tools
   * Available tools
   */
  available_tools?: string[];
  /**
   * Primary Llm
   * Primary LLM provider
   * @default "openai"
   */
  primary_llm?: string;
  /**
   * Fallback Llm
   * Fallback LLM provider
   * @default "anthropic"
   */
  fallback_llm?: string;
  /**
   * Temperature
   * Temperature for responses
   * @min 0
   * @max 2
   * @default 0.7
   */
  temperature?: number;
  /**
   * Max Tokens
   * Maximum tokens
   * @min 1
   * @max 32000
   * @default 4096
   */
  max_tokens?: number;
  /**
   * Max Conversation Length
   * Maximum conversation length
   * @min 1
   * @max 1000
   * @default 50
   */
  max_conversation_length?: number;
  /**
   * Context Window Size
   * Context window size
   * @min 100
   * @max 32000
   * @default 4000
   */
  context_window_size?: number;
  /**
   * Response Timeout
   * Response timeout in seconds
   * @min 1
   * @max 300
   * @default 30
   */
  response_timeout?: number;
  /**
   * Learning Enabled
   * Enable learning from feedback
   * @default true
   */
  learning_enabled?: boolean;
  /**
   * Feedback Weight
   * Weight for feedback learning
   * @min 0
   * @max 1
   * @default 0.1
   */
  feedback_weight?: number;
  /**
   * Adaptation Threshold
   * Adaptation threshold
   * @min 0
   * @max 1
   * @default 0.8
   */
  adaptation_threshold?: number;
  /**
   * Tags
   * Agent tags
   */
  tags?: string[];
  /**
   * Metadata
   * Additional metadata
   */
  metadata?: Record<string, any>;
}

/**
 * AgentDeleteResponse
 * Response schema for agent deletion.
 */
export interface AgentDeleteResponse {
  /**
   * Success
   * Whether deletion was successful
   */
  success: boolean;
  /**
   * Message
   * Deletion result message
   */
  message: string;
}

/**
 * AgentHealthResponse
 * Response schema for agent health check.
 */
export interface AgentHealthResponse {
  /**
   * Agent Id
   * Agent ID
   */
  agent_id: string;
  /** Agent status */
  status: AgentStatus;
  /**
   * Health
   * Health status (healthy/unhealthy/unknown)
   */
  health: string;
  /**
   * Last Interaction
   * Last interaction timestamp
   */
  last_interaction?: string | null;
  /**
   * Response Time Avg
   * Average response time
   */
  response_time_avg?: number | null;
  /**
   * Error Rate
   * Error rate percentage
   */
  error_rate?: number | null;
}

/**
 * AgentInteractRequest
 * Request schema for interacting with an agent.
 */
export interface AgentInteractRequest {
  /**
   * Message
   * Message to send to the agent
   */
  message: string;
  /**
   * Conversation Id
   * Conversation ID
   */
  conversation_id: string;
  /**
   * Context
   * Additional context
   */
  context?: Record<string, any> | null;
}

/**
 * AgentInteractResponse
 * Response schema for agent interaction.
 */
export interface AgentInteractResponse {
  /**
   * Agent Id
   * Agent ID
   */
  agent_id: string;
  /**
   * Response
   * Agent response
   */
  response: string;
  /**
   * Conversation Id
   * Conversation ID
   */
  conversation_id: string;
  /**
   * Tools Used
   * Tools used in response
   */
  tools_used: string[];
  /**
   * Confidence Score
   * Confidence score
   */
  confidence_score: number;
  /**
   * Response Time
   * Response time in seconds
   */
  response_time: number;
  /**
   * Timestamp
   * Response timestamp
   * @format date-time
   */
  timestamp: string;
}

/**
 * AgentListResponse
 * Response schema for agent list.
 */
export interface AgentListResponse {
  /**
   * Agents
   * List of agents
   */
  agents: AgentResponse[];
  /**
   * Total
   * Total number of agents
   */
  total: number;
  /**
   * Page
   * Current page number
   */
  page: number;
  /**
   * Per Page
   * Number of items per page
   */
  per_page: number;
  /**
   * Total Pages
   * Total number of pages
   */
  total_pages: number;
}

/**
 * AgentResponse
 * Response schema for agent data.
 */
export interface AgentResponse {
  /**
   * Id
   * Agent ID
   */
  id: string;
  /**
   * Name
   * Agent name
   */
  name: string;
  /**
   * Description
   * Agent description
   */
  description: string;
  /** Type of agent */
  type: AgentType;
  /** Agent status */
  status: AgentStatus;
  /**
   * System Message
   * System message
   */
  system_message: string;
  /**
   * Personality Traits
   * Agent personality traits
   */
  personality_traits: string[];
  /**
   * Knowledge Domains
   * Knowledge domains
   */
  knowledge_domains: string[];
  /**
   * Response Style
   * Response style
   */
  response_style: string;
  /**
   * Capabilities
   * Agent capabilities
   */
  capabilities: AgentCapability[];
  /**
   * Available Tools
   * Available tools
   */
  available_tools: string[];
  /**
   * Primary Llm
   * Primary LLM provider
   */
  primary_llm: string;
  /**
   * Fallback Llm
   * Fallback LLM provider
   */
  fallback_llm: string;
  /**
   * Temperature
   * Temperature for responses
   */
  temperature: number;
  /**
   * Max Tokens
   * Maximum tokens
   */
  max_tokens: number;
  /**
   * Max Conversation Length
   * Maximum conversation length
   */
  max_conversation_length: number;
  /**
   * Context Window Size
   * Context window size
   */
  context_window_size: number;
  /**
   * Response Timeout
   * Response timeout in seconds
   */
  response_timeout: number;
  /**
   * Learning Enabled
   * Learning enabled
   */
  learning_enabled: boolean;
  /**
   * Feedback Weight
   * Feedback weight
   */
  feedback_weight: number;
  /**
   * Adaptation Threshold
   * Adaptation threshold
   */
  adaptation_threshold: number;
  /**
   * Created At
   * Creation timestamp
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update timestamp
   * @format date-time
   */
  updated_at: string;
  /**
   * Created By
   * Creator
   */
  created_by: string;
  /**
   * Tags
   * Agent tags
   */
  tags: string[];
  /**
   * Metadata
   * Additional metadata
   */
  metadata: Record<string, any>;
}

/**
 * AgentStatsResponse
 * Response schema for agent statistics.
 */
export interface AgentStatsResponse {
  /**
   * Total Agents
   * Total number of agents
   */
  total_agents: number;
  /**
   * Active Agents
   * Number of active agents
   */
  active_agents: number;
  /**
   * Agent Types
   * Agents by type
   */
  agent_types: Record<string, number>;
  /**
   * Total Interactions
   * Total interactions across all agents
   */
  total_interactions: number;
}

/**
 * AgentUpdateRequest
 * Request schema for updating an agent.
 */
export interface AgentUpdateRequest {
  /**
   * Name
   * Agent name
   */
  name?: string | null;
  /**
   * Description
   * Agent description
   */
  description?: string | null;
  /**
   * System Prompt
   * System prompt for the agent
   */
  system_prompt?: string | null;
  /** Agent status */
  status?: AgentStatus | null;
  /**
   * Personality Traits
   * Agent personality traits
   */
  personality_traits?: string[] | null;
  /**
   * Knowledge Domains
   * Knowledge domains
   */
  knowledge_domains?: string[] | null;
  /**
   * Response Style
   * Response style
   */
  response_style?: string | null;
  /**
   * Capabilities
   * Agent capabilities
   */
  capabilities?: AgentCapability[] | null;
  /**
   * Available Tools
   * Available tools
   */
  available_tools?: string[] | null;
  /**
   * Primary Llm
   * Primary LLM provider
   */
  primary_llm?: string | null;
  /**
   * Fallback Llm
   * Fallback LLM provider
   */
  fallback_llm?: string | null;
  /**
   * Temperature
   * Temperature for responses
   */
  temperature?: number | null;
  /**
   * Max Tokens
   * Maximum tokens
   */
  max_tokens?: number | null;
  /**
   * Max Conversation Length
   * Maximum conversation length
   */
  max_conversation_length?: number | null;
  /**
   * Context Window Size
   * Context window size
   */
  context_window_size?: number | null;
  /**
   * Response Timeout
   * Response timeout in seconds
   */
  response_timeout?: number | null;
  /**
   * Learning Enabled
   * Enable learning from feedback
   */
  learning_enabled?: boolean | null;
  /**
   * Feedback Weight
   * Weight for feedback learning
   */
  feedback_weight?: number | null;
  /**
   * Adaptation Threshold
   * Adaptation threshold
   */
  adaptation_threshold?: number | null;
  /**
   * Tags
   * Agent tags
   */
  tags?: string[] | null;
  /**
   * Metadata
   * Additional metadata
   */
  metadata?: Record<string, any> | null;
}

/**
 * AvailableProvidersResponse
 * Schema for available providers response.
 */
export interface AvailableProvidersResponse {
  /**
   * Providers
   * Available LLM providers with their configurations
   */
  providers: Record<string, any>;
  /**
   * Total Providers
   * Total number of available providers
   */
  total_providers: number;
  /**
   * Supported Features
   * Features supported by each provider
   */
  supported_features: Record<string, string[]>;
}

/**
 * AvailableToolResponse
 * Schema for individual available tool.
 */
export interface AvailableToolResponse {
  /**
   * Name
   * Tool name
   */
  name: string;
  /**
   * Description
   * Tool description
   */
  description: string;
  /**
   * Type
   * Tool type (mcp, builtin)
   */
  type: string;
  /**
   * Args Schema
   * Tool arguments schema
   */
  args_schema: Record<string, any>;
}

/**
 * AvailableToolsResponse
 * Schema for available tools response.
 */
export interface AvailableToolsResponse {
  /**
   * Tools
   * Available tools
   */
  tools: AvailableToolResponse[];
}

/**
 * BackupListResponse
 * Response schema for backup list.
 */
export interface BackupListResponse {
  /**
   * Backups
   * List of backups
   */
  backups: BackupResponse[];
  /**
   * Total
   * Total number of backups
   */
  total: number;
}

/**
 * BackupRequest
 * Request schema for creating a backup via API.
 */
export interface BackupRequest {
  /**
   * Backup type
   * @default "full"
   */
  backup_type?: BackupType;
  /**
   * Name
   * Backup name
   */
  name?: string | null;
  /**
   * Description
   * Backup description
   */
  description?: string | null;
  /**
   * Include Files
   * Include uploaded files
   * @default true
   */
  include_files?: boolean;
  /**
   * Include Logs
   * Include system logs
   * @default false
   */
  include_logs?: boolean;
  /**
   * Compress
   * Compress backup
   * @default true
   */
  compress?: boolean;
  /**
   * Encrypt
   * Encrypt backup
   * @default true
   */
  encrypt?: boolean;
  /**
   * Retention Days
   * Backup retention in days
   * @min 1
   * @max 365
   * @default 30
   */
  retention_days?: number;
}

/**
 * BackupResponse
 * Response schema for backup data.
 */
export interface BackupResponse {
  /**
   * Id
   * Backup ID
   */
  id: string;
  /**
   * Name
   * Backup name
   */
  name: string;
  /**
   * Description
   * Backup description
   */
  description?: string | null;
  /** Backup type */
  backup_type: BackupType;
  /**
   * Status
   * Backup status
   */
  status: string;
  /**
   * File Size
   * Backup file size in bytes
   */
  file_size?: number | null;
  /**
   * Compressed Size
   * Compressed size in bytes
   */
  compressed_size?: number | null;
  /**
   * Record Count
   * Number of records backed up
   */
  record_count?: number | null;
  /**
   * Created At
   * Backup creation timestamp
   * @format date-time
   */
  created_at: string;
  /**
   * Completed At
   * Backup completion timestamp
   */
  completed_at?: string | null;
  /**
   * Expires At
   * Backup expiration timestamp
   */
  expires_at?: string | null;
  /**
   * Encrypted
   * Whether backup is encrypted
   */
  encrypted: boolean;
  /**
   * Compressed
   * Whether backup is compressed
   */
  compressed: boolean;
  /**
   * Metadata
   * Backup metadata
   */
  metadata: Record<string, any>;
}

/** Body_list_agents_api_v1_agents__get */
export interface BodyListAgentsApiV1AgentsGet {
  /**
   * Common pagination request schema.
   * @default {"limit":50,"offset":0}
   */
  pagination?: PaginationRequest;
  /**
   * Common sorting request schema.
   * @default {"sort_by":"created_at","sort_order":"desc"}
   */
  sorting?: SortingRequest;
  /** Tags */
  tags?: string[] | null;
}

/** Body_upload_document_api_v1_documents_upload_post */
export interface BodyUploadDocumentApiV1DocumentsUploadPost {
  /**
   * File
   * @format binary
   */
  file: File;
  /** Title */
  title?: string;
  /** Description */
  description?: string;
  /** Tags */
  tags?: string;
  /**
   * Chunk Size
   * @default 1000
   */
  chunk_size?: number;
  /**
   * Chunk Overlap
   * @default 200
   */
  chunk_overlap?: number;
  /**
   * Is Public
   * @default false
   */
  is_public?: boolean;
}

/**
 * BottleneckInfo
 * Schema for bottleneck information.
 */
export interface BottleneckInfo {
  /**
   * Node Id
   * Node ID with bottleneck
   */
  node_id: string;
  /**
   * Node Type
   * Node type
   */
  node_type: string;
  /**
   * Reason
   * Bottleneck reason
   */
  reason: string;
  /**
   * Severity
   * Bottleneck severity (low/medium/high)
   */
  severity: string;
  /**
   * Suggestions
   * Optimization suggestions
   */
  suggestions: string[];
}

/**
 * BulkDeleteResponse
 * Response schema for bulk delete operations.
 */
export interface BulkDeleteResponse {
  /**
   * Total Requested
   * Total number of items requested for deletion
   */
  total_requested: number;
  /**
   * Successful Deletions
   * Number of successful deletions
   */
  successful_deletions: number;
  /**
   * Failed Deletions
   * Number of failed deletions
   */
  failed_deletions: number;
  /**
   * Errors
   * List of error messages for failed deletions
   */
  errors: string[];
}

/**
 * BulkOperationResult
 * Schema for bulk operation results.
 */
export interface BulkOperationResult {
  /**
   * Total Requested
   * Total servers requested
   */
  total_requested: number;
  /**
   * Successful
   * Successfully processed
   */
  successful: number;
  /**
   * Failed
   * Failed to process
   */
  failed: number;
  /**
   * Results
   * Detailed results
   */
  results: Record<string, any>[];
  /**
   * Errors
   * Error messages
   */
  errors?: string[];
}

/**
 * BulkToolServerOperation
 * Schema for bulk operations on tool servers.
 */
export interface BulkToolServerOperation {
  /**
   * Server Ids
   * List of server IDs
   * @minItems 1
   */
  server_ids: string[];
  /**
   * Operation
   * Operation to perform
   */
  operation: string;
  /**
   * Parameters
   * Operation parameters
   */
  parameters?: Record<string, any> | null;
}

/**
 * ChatRequest
 * Schema for chat request.
 */
export interface ChatRequest {
  /**
   * Message
   * User message
   */
  message: string;
  /**
   * Conversation Id
   * Conversation ID for continuing chat
   */
  conversation_id?: string | null;
  /**
   * Profile Id
   * Profile ID to use
   */
  profile_id?: string | null;
  /**
   * Stream
   * Enable streaming response
   * @default false
   */
  stream?: boolean;
  /**
   * Workflow
   * Workflow type: plain, rag, tools, or full (rag + tools)
   * @default "plain"
   */
  workflow?: "plain" | "rag" | "tools" | "full";
  /**
   * Provider
   * Override LLM provider for this request
   */
  provider?: string | null;
  /**
   * Temperature
   * Temperature override
   */
  temperature?: number | null;
  /**
   * Max Tokens
   * Max tokens override
   */
  max_tokens?: number | null;
  /**
   * Context Limit
   * Context limit override
   */
  context_limit?: number | null;
  /**
   * Enable Retrieval
   * Enable retrieval override
   */
  enable_retrieval?: boolean | null;
  /**
   * Document Ids
   * Document IDs to include in context
   */
  document_ids?: string[] | null;
  /**
   * System Prompt Override
   * Override system prompt for this request
   */
  system_prompt_override?: string | null;
  /**
   * Workflow Config
   * Workflow configuration
   */
  workflow_config?: Record<string, any> | null;
  /**
   * Workflow Type
   * Internal workflow type (set by API processing)
   */
  workflow_type?: string | null;
}

/**
 * ChatResponse
 * Schema for chat response.
 */
export interface ChatResponse {
  /**
   * Conversation Id
   * Conversation ID
   */
  conversation_id: string;
  /** Assistant response message */
  message: MessageResponse;
  /** Updated conversation */
  conversation: ConversationResponse;
}

/**
 * ComplexityMetrics
 * Schema for workflow complexity metrics.
 */
export interface ComplexityMetrics {
  /**
   * Score
   * Overall complexity score
   */
  score: number;
  /**
   * Node Count
   * Number of nodes
   */
  node_count: number;
  /**
   * Edge Count
   * Number of edges
   */
  edge_count: number;
  /**
   * Depth
   * Maximum path depth
   */
  depth: number;
  /**
   * Branching Factor
   * Average branching factor
   */
  branching_factor: number;
  /**
   * Loop Complexity
   * Loop complexity score
   * @default 0
   */
  loop_complexity?: number;
  /**
   * Conditional Complexity
   * Conditional complexity score
   * @default 0
   */
  conditional_complexity?: number;
}

/**
 * ConversationCreate
 * Schema for creating a conversation.
 */
export interface ConversationCreate {
  /**
   * Title
   * Conversation title
   */
  title: string;
  /**
   * Description
   * Conversation description
   */
  description?: string | null;
  /**
   * Profile Id
   * Profile ID to use
   */
  profile_id?: string | null;
  /**
   * System Prompt
   * System prompt
   */
  system_prompt?: string | null;
  /**
   * Enable Retrieval
   * Enable document retrieval
   * @default false
   */
  enable_retrieval?: boolean;
  /**
   * Temperature
   * Temperature setting
   */
  temperature?: number | null;
  /**
   * Max Tokens
   * Max tokens setting
   */
  max_tokens?: number | null;
  /**
   * Workflow Config
   * Workflow configuration
   */
  workflow_config?: Record<string, any> | null;
  /**
   * Extra Metadata
   * Additional metadata
   */
  extra_metadata?: Record<string, any> | null;
}

/**
 * ConversationDeleteResponse
 * Schema for conversation delete response.
 */
export interface ConversationDeleteResponse {
  /**
   * Message
   * Success message
   */
  message: string;
}

/**
 * ConversationResponse
 * Schema for conversation response.
 */
export interface ConversationResponse {
  /**
   * Title
   * Conversation title
   */
  title: string;
  /**
   * Description
   * Conversation description
   */
  description?: string | null;
  /**
   * Id
   * Conversation ID
   */
  id: string;
  /**
   * User Id
   * User ID
   */
  user_id: string;
  /**
   * Profile Id
   * Profile ID
   */
  profile_id?: string | null;
  /** Conversation status */
  status: ConversationStatus;
  /**
   * Llm Provider
   * LLM provider
   */
  llm_provider?: string | null;
  /**
   * Llm Model
   * LLM model
   */
  llm_model?: string | null;
  /**
   * Temperature
   * Temperature setting
   */
  temperature?: number | null;
  /**
   * Max Tokens
   * Max tokens setting
   */
  max_tokens?: number | null;
  /**
   * Enable Retrieval
   * Retrieval enabled
   */
  enable_retrieval: boolean;
  /**
   * Message Count
   * Number of messages
   */
  message_count: number;
  /**
   * Total Tokens
   * Total tokens used
   */
  total_tokens: number;
  /**
   * Total Cost
   * Total cost
   */
  total_cost: number;
  /**
   * System Prompt
   * System prompt
   */
  system_prompt?: string | null;
  /**
   * Context Window
   * Context window size
   */
  context_window: number;
  /**
   * Memory Enabled
   * Memory enabled
   */
  memory_enabled: boolean;
  /**
   * Memory Strategy
   * Memory strategy
   */
  memory_strategy?: string | null;
  /**
   * Retrieval Limit
   * Retrieval limit
   */
  retrieval_limit: number;
  /**
   * Retrieval Score Threshold
   * Retrieval score threshold
   */
  retrieval_score_threshold: number;
  /**
   * Tags
   * Conversation tags
   */
  tags?: string[] | null;
  /**
   * Extra Metadata
   * Extra metadata
   */
  extra_metadata?: Record<string, any> | null;
  /**
   * Workflow Config
   * Workflow configuration
   */
  workflow_config?: Record<string, any> | null;
  /**
   * Created At
   * Creation timestamp
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update timestamp
   * @format date-time
   */
  updated_at: string;
  /**
   * Last Message At
   * Last message timestamp
   */
  last_message_at?: string | null;
}

/**
 * ConversationSearchResponse
 * Schema for conversation search response.
 */
export interface ConversationSearchResponse {
  /**
   * Conversations
   * Conversations
   */
  conversations: ConversationResponse[];
  /**
   * Total
   * Total number of conversations
   */
  total: number;
  /**
   * Limit
   * Request limit
   */
  limit: number;
  /**
   * Offset
   * Request offset
   */
  offset: number;
}

/**
 * ConversationStatsResponse
 * Schema for conversation statistics response.
 */
export interface ConversationStatsResponse {
  /**
   * Total Conversations
   * Total number of conversations
   */
  total_conversations: number;
  /**
   * Conversations By Status
   * Conversations grouped by status
   */
  conversations_by_status: Record<string, number>;
  /**
   * Total Messages
   * Total number of messages
   */
  total_messages: number;
  /**
   * Messages By Role
   * Messages grouped by role
   */
  messages_by_role: Record<string, number>;
  /**
   * Avg Messages Per Conversation
   * Average messages per conversation
   */
  avg_messages_per_conversation: number;
  /**
   * Total Tokens Used
   * Total tokens used
   */
  total_tokens_used: number;
  /**
   * Total Cost
   * Total cost incurred
   */
  total_cost: number;
  /**
   * Avg Response Time Ms
   * Average response time in milliseconds
   */
  avg_response_time_ms: number;
  /**
   * Conversations By Date
   * Conversations by date
   */
  conversations_by_date: Record<string, number>;
  /**
   * Most Active Hours
   * Most active hours
   */
  most_active_hours: Record<string, number>;
  /**
   * Popular Models
   * Popular LLM models
   */
  popular_models: Record<string, number>;
  /**
   * Popular Providers
   * Popular LLM providers
   */
  popular_providers: Record<string, number>;
}

/**
 * ConversationUpdate
 * Schema for updating a conversation.
 */
export interface ConversationUpdate {
  /**
   * Title
   * Conversation title
   */
  title?: string | null;
  /**
   * Description
   * Conversation description
   */
  description?: string | null;
  /** Conversation status */
  status?: ConversationStatus | null;
  /**
   * Temperature
   * Temperature setting
   */
  temperature?: number | null;
  /**
   * Max Tokens
   * Max tokens setting
   */
  max_tokens?: number | null;
  /**
   * Workflow Config
   * Workflow configuration
   */
  workflow_config?: Record<string, any> | null;
  /**
   * Extra Metadata
   * Additional metadata
   */
  extra_metadata?: Record<string, any> | null;
}

/**
 * ConversationWithMessages
 * Schema for conversation with messages.
 */
export interface ConversationWithMessages {
  /**
   * Title
   * Conversation title
   */
  title: string;
  /**
   * Description
   * Conversation description
   */
  description?: string | null;
  /**
   * Id
   * Conversation ID
   */
  id: string;
  /**
   * User Id
   * User ID
   */
  user_id: string;
  /**
   * Profile Id
   * Profile ID
   */
  profile_id?: string | null;
  /** Conversation status */
  status: ConversationStatus;
  /**
   * Llm Provider
   * LLM provider
   */
  llm_provider?: string | null;
  /**
   * Llm Model
   * LLM model
   */
  llm_model?: string | null;
  /**
   * Temperature
   * Temperature setting
   */
  temperature?: number | null;
  /**
   * Max Tokens
   * Max tokens setting
   */
  max_tokens?: number | null;
  /**
   * Enable Retrieval
   * Retrieval enabled
   */
  enable_retrieval: boolean;
  /**
   * Message Count
   * Number of messages
   */
  message_count: number;
  /**
   * Total Tokens
   * Total tokens used
   */
  total_tokens: number;
  /**
   * Total Cost
   * Total cost
   */
  total_cost: number;
  /**
   * System Prompt
   * System prompt
   */
  system_prompt?: string | null;
  /**
   * Context Window
   * Context window size
   */
  context_window: number;
  /**
   * Memory Enabled
   * Memory enabled
   */
  memory_enabled: boolean;
  /**
   * Memory Strategy
   * Memory strategy
   */
  memory_strategy?: string | null;
  /**
   * Retrieval Limit
   * Retrieval limit
   */
  retrieval_limit: number;
  /**
   * Retrieval Score Threshold
   * Retrieval score threshold
   */
  retrieval_score_threshold: number;
  /**
   * Tags
   * Conversation tags
   */
  tags?: string[] | null;
  /**
   * Extra Metadata
   * Extra metadata
   */
  extra_metadata?: Record<string, any> | null;
  /**
   * Workflow Config
   * Workflow configuration
   */
  workflow_config?: Record<string, any> | null;
  /**
   * Created At
   * Creation timestamp
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update timestamp
   * @format date-time
   */
  updated_at: string;
  /**
   * Last Message At
   * Last message timestamp
   */
  last_message_at?: string | null;
  /**
   * Messages
   * Conversation messages
   */
  messages?: MessageResponse[];
}

/**
 * CorrelationTraceResponse
 * Schema for correlation trace response.
 */
export interface CorrelationTraceResponse {
  /**
   * Correlation Id
   * Correlation ID
   */
  correlation_id: string;
  /**
   * Trace Length
   * Number of requests in trace
   */
  trace_length: number;
  /**
   * Requests
   * List of requests in trace
   */
  requests: Record<string, any>[];
}

/**
 * DashboardResponse
 * Schema for analytics dashboard response.
 */
export interface DashboardResponse {
  /** Conversation statistics */
  conversation_stats: ConversationStatsResponse;
  /** Usage metrics */
  usage_metrics: UsageMetricsResponse;
  /** Performance metrics */
  performance_metrics: PerformanceMetricsResponse;
  /** Document analytics */
  document_analytics: DocumentAnalyticsResponse;
  /** System health metrics */
  system_health: SystemAnalyticsResponse;
  /**
   * Custom Metrics
   * Custom metrics
   */
  custom_metrics: Record<string, any>[];
  /**
   * Generated At
   * Dashboard generation time
   * @format date-time
   */
  generated_at: string;
}

/**
 * DefaultProvider
 * Schema for setting default provider.
 */
export interface DefaultProvider {
  /** Types of AI models. */
  model_type: ModelType;
}

/**
 * DocumentAnalyticsResponse
 * Schema for document analytics response.
 */
export interface DocumentAnalyticsResponse {
  /**
   * Total Documents
   * Total number of documents
   */
  total_documents: number;
  /**
   * Documents By Status
   * Documents by processing status
   */
  documents_by_status: Record<string, number>;
  /**
   * Documents By Type
   * Documents by file type
   */
  documents_by_type: Record<string, number>;
  /**
   * Avg Processing Time Seconds
   * Average processing time
   */
  avg_processing_time_seconds: number;
  /**
   * Processing Success Rate
   * Processing success rate
   */
  processing_success_rate: number;
  /**
   * Total Chunks
   * Total number of chunks
   */
  total_chunks: number;
  /**
   * Avg Chunks Per Document
   * Average chunks per document
   */
  avg_chunks_per_document: number;
  /**
   * Total Storage Bytes
   * Total storage used
   */
  total_storage_bytes: number;
  /**
   * Avg Document Size Bytes
   * Average document size
   */
  avg_document_size_bytes: number;
  /**
   * Storage By Type
   * Storage usage by document type
   */
  storage_by_type: Record<string, number>;
  /**
   * Total Searches
   * Total number of searches
   */
  total_searches: number;
  /**
   * Avg Search Results
   * Average search results returned
   */
  avg_search_results: number;
  /**
   * Popular Search Terms
   * Popular search terms
   */
  popular_search_terms: Record<string, number>;
  /**
   * Total Views
   * Total document views
   */
  total_views: number;
  /**
   * Most Viewed Documents
   * Most viewed documents
   */
  most_viewed_documents: Record<string, any>[];
  /**
   * Documents By Access Level
   * Documents by access level
   */
  documents_by_access_level: Record<string, number>;
}

/**
 * DocumentChunkResponse
 * Schema for document chunk response.
 */
export interface DocumentChunkResponse {
  /**
   * Id
   * Chunk ID
   */
  id: string;
  /**
   * Document Id
   * Document ID
   */
  document_id: string;
  /**
   * Content
   * Chunk content
   */
  content: string;
  /**
   * Chunk Index
   * Chunk index
   */
  chunk_index: number;
  /**
   * Start Char
   * Start character position
   */
  start_char?: number | null;
  /**
   * End Char
   * End character position
   */
  end_char?: number | null;
  /**
   * Extra Metadata
   * Chunk metadata
   */
  extra_metadata?: Record<string, any> | null;
  /**
   * Token Count
   * Token count
   */
  token_count?: number | null;
  /**
   * Language
   * Detected language
   */
  language?: string | null;
  /**
   * Embedding Model
   * Embedding model used
   */
  embedding_model?: string | null;
  /**
   * Embedding Provider
   * Embedding provider
   */
  embedding_provider?: string | null;
  /**
   * Embedding Created At
   * Embedding creation time
   */
  embedding_created_at?: string | null;
  /**
   * Content Hash
   * Content hash
   */
  content_hash: string;
  /**
   * Created At
   * Creation time
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update time
   * @format date-time
   */
  updated_at: string;
}

/**
 * DocumentChunksResponse
 * Schema for document chunks response with pagination.
 */
export interface DocumentChunksResponse {
  /**
   * Chunks
   * List of document chunks
   */
  chunks: DocumentChunkResponse[];
  /**
   * Total Count
   * Total number of chunks
   */
  total_count: number;
  /**
   * Limit
   * Applied limit
   */
  limit: number;
  /**
   * Offset
   * Applied offset
   */
  offset: number;
}

/**
 * DocumentDeleteResponse
 * Response schema for document deletion.
 */
export interface DocumentDeleteResponse {
  /**
   * Message
   * Deletion result message
   */
  message: string;
}

/**
 * DocumentListResponse
 * Schema for document list response.
 */
export interface DocumentListResponse {
  /**
   * Documents
   * List of documents
   */
  documents: DocumentResponse[];
  /**
   * Total Count
   * Total number of documents
   */
  total_count: number;
  /**
   * Limit
   * Applied limit
   */
  limit: number;
  /**
   * Offset
   * Applied offset
   */
  offset: number;
}

/**
 * DocumentProcessingRequest
 * Schema for document processing request.
 */
export interface DocumentProcessingRequest {
  /**
   * Reprocess
   * Force reprocessing
   * @default false
   */
  reprocess?: boolean;
  /**
   * Chunk Size
   * Override chunk size
   */
  chunk_size?: number | null;
  /**
   * Chunk Overlap
   * Override chunk overlap
   */
  chunk_overlap?: number | null;
  /**
   * Generate Embeddings
   * Generate embeddings for chunks
   * @default true
   */
  generate_embeddings?: boolean;
}

/**
 * DocumentProcessingResponse
 * Schema for document processing response.
 */
export interface DocumentProcessingResponse {
  /**
   * Document Id
   * Document ID
   */
  document_id: string;
  /** Processing status */
  status: DocumentStatus;
  /**
   * Message
   * Status message
   */
  message: string;
  /**
   * Processing Started At
   * Processing start time
   */
  processing_started_at?: string | null;
}

/**
 * DocumentResponse
 * Schema for document response.
 */
export interface DocumentResponse {
  /**
   * Title
   * Document title
   */
  title?: string | null;
  /**
   * Description
   * Document description
   */
  description?: string | null;
  /**
   * Tags
   * Document tags
   */
  tags?: string[] | null;
  /**
   * Extra Metadata
   * Additional metadata
   */
  extra_metadata?: Record<string, any> | null;
  /**
   * Is Public
   * Whether document is public
   * @default false
   */
  is_public?: boolean;
  /**
   * Id
   * Document ID
   */
  id: string;
  /**
   * Owner Id
   * Owner user ID
   */
  owner_id: string;
  /**
   * Filename
   * Document filename
   */
  filename: string;
  /**
   * Original Filename
   * Original filename
   */
  original_filename: string;
  /**
   * File Size
   * File size in bytes
   */
  file_size: number;
  /**
   * File Hash
   * File hash (SHA-256)
   */
  file_hash: string;
  /**
   * Mime Type
   * MIME type
   */
  mime_type: string;
  /** Document type */
  document_type: DocumentType;
  /** Processing status */
  status: DocumentStatus;
  /**
   * Processing Started At
   * Processing start time
   */
  processing_started_at?: string | null;
  /**
   * Processing Completed At
   * Processing completion time
   */
  processing_completed_at?: string | null;
  /**
   * Processing Error
   * Processing error message
   */
  processing_error?: string | null;
  /**
   * Chunk Size
   * Chunk size
   */
  chunk_size: number;
  /**
   * Chunk Overlap
   * Chunk overlap
   */
  chunk_overlap: number;
  /**
   * Chunk Count
   * Number of chunks
   */
  chunk_count: number;
  /**
   * Version
   * Document version
   */
  version: number;
  /**
   * Parent Document Id
   * Parent document ID
   */
  parent_document_id?: string | null;
  /**
   * View Count
   * View count
   */
  view_count: number;
  /**
   * Search Count
   * Search count
   */
  search_count: number;
  /**
   * Last Accessed At
   * Last access time
   */
  last_accessed_at?: string | null;
  /**
   * Created At
   * Creation time
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update time
   * @format date-time
   */
  updated_at: string;
}

/**
 * DocumentSearchRequest
 * Schema for document search request.
 */
export interface DocumentSearchRequest {
  /**
   * Query
   * Search query
   * @minLength 1
   * @maxLength 1000
   */
  query: string;
  /**
   * Limit
   * Maximum number of results
   * @min 1
   * @max 100
   * @default 10
   */
  limit?: number;
  /**
   * Score Threshold
   * Minimum similarity score
   * @min 0
   * @max 1
   * @default 0.5
   */
  score_threshold?: number;
  /**
   * Document Types
   * Filter by document types
   */
  document_types?: DocumentType[] | null;
  /**
   * Tags
   * Filter by tags
   */
  tags?: string[] | null;
  /**
   * Include Content
   * Include document content in results
   * @default false
   */
  include_content?: boolean;
}

/**
 * DocumentSearchResponse
 * Schema for document search response.
 */
export interface DocumentSearchResponse {
  /**
   * Results
   * Search results
   */
  results: DocumentSearchResult[];
  /**
   * Total Results
   * Total number of matching results
   */
  total_results: number;
  /**
   * Query
   * Original search query
   */
  query: string;
  /**
   * Score Threshold
   * Applied score threshold
   */
  score_threshold: number;
}

/**
 * DocumentSearchResult
 * Schema for document search result.
 */
export interface DocumentSearchResult {
  /**
   * Document Id
   * Document ID
   */
  document_id: string;
  /**
   * Chunk Id
   * Chunk ID
   */
  chunk_id: string;
  /**
   * Score
   * Similarity score
   */
  score: number;
  /**
   * Content
   * Matching content
   */
  content: string;
  /**
   * Metadata
   * Chunk metadata
   */
  metadata?: Record<string, any> | null;
  /** Document information */
  document: DocumentResponse;
}

/**
 * DocumentStatsResponse
 * Schema for document statistics response.
 */
export interface DocumentStatsResponse {
  /**
   * Total Documents
   * Total number of documents
   */
  total_documents: number;
  /**
   * Total Chunks
   * Total number of chunks
   */
  total_chunks: number;
  /**
   * Total Size Bytes
   * Total size in bytes
   */
  total_size_bytes: number;
  /**
   * Documents By Status
   * Documents grouped by status
   */
  documents_by_status: Record<string, number>;
  /**
   * Documents By Type
   * Documents grouped by type
   */
  documents_by_type: Record<string, number>;
  /**
   * Processing Stats
   * Processing statistics
   */
  processing_stats: Record<string, any>;
}

/**
 * DocumentUpdate
 * Schema for updating a document.
 */
export interface DocumentUpdate {
  /**
   * Title
   * Document title
   */
  title?: string | null;
  /**
   * Description
   * Document description
   */
  description?: string | null;
  /**
   * Tags
   * Document tags
   */
  tags?: string[] | null;
  /**
   * Extra Metadata
   * Additional metadata
   */
  extra_metadata?: Record<string, any> | null;
  /**
   * Is Public
   * Whether document is public
   */
  is_public?: boolean | null;
}

/**
 * EmbeddingSpaceCreate
 * Schema for creating an embedding space.
 */
export interface EmbeddingSpaceCreate {
  /**
   * Name
   * Unique space name
   * @minLength 1
   * @maxLength 100
   * @pattern ^[a-zA-Z0-9_-]+$
   */
  name: string;
  /**
   * Display Name
   * Human-readable name
   * @minLength 1
   * @maxLength 200
   */
  display_name: string;
  /**
   * Description
   * Space description
   */
  description?: string | null;
  /**
   * Base Dimensions
   * Original model dimensions
   * @exclusiveMin 0
   * @max 10000
   */
  base_dimensions: number;
  /**
   * Effective Dimensions
   * Effective dimensions after reduction
   * @exclusiveMin 0
   * @max 10000
   */
  effective_dimensions: number;
  /**
   * Reduction strategy
   * @default "none"
   */
  reduction_strategy?: ReductionStrategy;
  /**
   * Reducer Path
   * Path to reducer file
   */
  reducer_path?: string | null;
  /**
   * Reducer Version
   * Reducer version/hash
   */
  reducer_version?: string | null;
  /**
   * Normalize Vectors
   * Whether to normalize vectors
   * @default true
   */
  normalize_vectors?: boolean;
  /**
   * Distance metric
   * @default "cosine"
   */
  distance_metric?: DistanceMetric;
  /**
   * Table Name
   * Database table name
   * @minLength 1
   * @maxLength 100
   * @pattern ^[a-zA-Z0-9_]+$
   */
  table_name: string;
  /**
   * Index Type
   * Index type
   * @maxLength 50
   * @default "hnsw"
   */
  index_type?: string;
  /**
   * Index Config
   * Index configuration
   */
  index_config?: Record<string, any>;
  /**
   * Is Active
   * Whether space is active
   * @default true
   */
  is_active?: boolean;
  /**
   * Is Default
   * Whether this is the default space
   * @default false
   */
  is_default?: boolean;
  /**
   * Model Id
   * Model ID
   */
  model_id: string;
}

/**
 * EmbeddingSpaceDefaultResponse
 * Response schema for setting default embedding space.
 */
export interface EmbeddingSpaceDefaultResponse {
  /**
   * Message
   * Operation result message
   */
  message: string;
}

/**
 * EmbeddingSpaceDeleteResponse
 * Response schema for embedding space deletion.
 */
export interface EmbeddingSpaceDeleteResponse {
  /**
   * Message
   * Deletion result message
   */
  message: string;
}

/**
 * EmbeddingSpaceList
 * List of embedding spaces with pagination.
 */
export interface EmbeddingSpaceList {
  /** Spaces */
  spaces: EmbeddingSpaceWithModel[];
  /** Total */
  total: number;
  /** Page */
  page: number;
  /** Per Page */
  per_page: number;
}

/**
 * EmbeddingSpaceUpdate
 * Schema for updating an embedding space.
 */
export interface EmbeddingSpaceUpdate {
  /** Display Name */
  display_name?: string | null;
  /** Description */
  description?: string | null;
  reduction_strategy?: ReductionStrategy | null;
  /** Reducer Path */
  reducer_path?: string | null;
  /** Reducer Version */
  reducer_version?: string | null;
  /** Normalize Vectors */
  normalize_vectors?: boolean | null;
  distance_metric?: DistanceMetric | null;
  /** Index Type */
  index_type?: string | null;
  /** Index Config */
  index_config?: Record<string, any> | null;
  /** Is Active */
  is_active?: boolean | null;
  /** Is Default */
  is_default?: boolean | null;
}

/**
 * EmbeddingSpaceWithModel
 * Embedding space with model and provider information.
 */
export interface EmbeddingSpaceWithModel {
  /**
   * Name
   * Unique space name
   * @minLength 1
   * @maxLength 100
   * @pattern ^[a-zA-Z0-9_-]+$
   */
  name: string;
  /**
   * Display Name
   * Human-readable name
   * @minLength 1
   * @maxLength 200
   */
  display_name: string;
  /**
   * Description
   * Space description
   */
  description?: string | null;
  /**
   * Base Dimensions
   * Original model dimensions
   * @exclusiveMin 0
   * @max 10000
   */
  base_dimensions: number;
  /**
   * Effective Dimensions
   * Effective dimensions after reduction
   * @exclusiveMin 0
   * @max 10000
   */
  effective_dimensions: number;
  /**
   * Reduction strategy
   * @default "none"
   */
  reduction_strategy?: ReductionStrategy;
  /**
   * Reducer Path
   * Path to reducer file
   */
  reducer_path?: string | null;
  /**
   * Reducer Version
   * Reducer version/hash
   */
  reducer_version?: string | null;
  /**
   * Normalize Vectors
   * Whether to normalize vectors
   * @default true
   */
  normalize_vectors?: boolean;
  /**
   * Distance metric
   * @default "cosine"
   */
  distance_metric?: DistanceMetric;
  /**
   * Table Name
   * Database table name
   * @minLength 1
   * @maxLength 100
   * @pattern ^[a-zA-Z0-9_]+$
   */
  table_name: string;
  /**
   * Index Type
   * Index type
   * @maxLength 50
   * @default "hnsw"
   */
  index_type?: string;
  /**
   * Index Config
   * Index configuration
   */
  index_config?: Record<string, any>;
  /**
   * Is Active
   * Whether space is active
   * @default true
   */
  is_active?: boolean;
  /**
   * Is Default
   * Whether this is the default space
   * @default false
   */
  is_default?: boolean;
  /** Id */
  id: string;
  /** Model Id */
  model_id: string;
  /**
   * Created At
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * @format date-time
   */
  updated_at: string;
  /** Model definition with provider information. */
  model: ModelDefWithProvider;
}

/**
 * ExportDataRequest
 * Request schema for data export API.
 */
export interface ExportDataRequest {
  /** Export scope */
  scope: ExportScope;
  /**
   * Export format
   * @default "json"
   */
  format?: DataFormat;
  /**
   * User Id
   * Filter by user ID
   */
  user_id?: string | null;
  /**
   * Conversation Id
   * Filter by conversation ID
   */
  conversation_id?: string | null;
  /**
   * Date From
   * Filter from date
   */
  date_from?: string | null;
  /**
   * Date To
   * Filter to date
   */
  date_to?: string | null;
  /**
   * Include Metadata
   * Include metadata
   * @default true
   */
  include_metadata?: boolean;
  /**
   * Compress
   * Compress export file
   * @default true
   */
  compress?: boolean;
  /**
   * Encrypt
   * Encrypt export file
   * @default false
   */
  encrypt?: boolean;
  /**
   * Custom Query
   * Custom export query
   */
  custom_query?: Record<string, any> | null;
}

/**
 * ExportDataResponse
 * Response schema for data export.
 */
export interface ExportDataResponse {
  /**
   * Export Id
   * Export ID
   */
  export_id: string;
  /**
   * Status
   * Export status
   */
  status: string;
  /**
   * Download Url
   * Download URL when ready
   */
  download_url?: string | null;
  /**
   * File Size
   * File size in bytes
   */
  file_size?: number | null;
  /**
   * Record Count
   * Number of records exported
   */
  record_count?: number | null;
  /**
   * Created At
   * Export creation timestamp
   * @format date-time
   */
  created_at: string;
  /**
   * Completed At
   * Export completion timestamp
   */
  completed_at?: string | null;
  /**
   * Expires At
   * Download link expiration
   */
  expires_at?: string | null;
}

/** HTTPValidationError */
export interface HTTPValidationError {
  /** Detail */
  detail?: ValidationError[];
}

/**
 * HealthCheckResponse
 * Schema for health check response.
 */
export interface HealthCheckResponse {
  /** Health status */
  status: HealthStatus;
  /**
   * Service
   * Service name
   */
  service: string;
  /**
   * Version
   * Service version
   */
  version: string;
  /**
   * Environment
   * Environment
   */
  environment: string;
}

/**
 * JobActionResponse
 * Response schema for job actions.
 */
export interface JobActionResponse {
  /**
   * Success
   * Whether action was successful
   */
  success: boolean;
  /**
   * Message
   * Action result message
   */
  message: string;
  /**
   * Job Id
   * Job ID
   */
  job_id: string;
}

/**
 * JobCreateRequest
 * Request schema for creating a job.
 */
export interface JobCreateRequest {
  /**
   * Name
   * Job name
   */
  name: string;
  /**
   * Function Name
   * Function to execute
   */
  function_name: string;
  /**
   * Args
   * Function arguments
   */
  args?: any[];
  /**
   * Kwargs
   * Function keyword arguments
   */
  kwargs?: Record<string, any>;
  /**
   * Job priority
   * @default "normal"
   */
  priority?: JobPriority;
  /**
   * Max Retries
   * Maximum retry attempts
   * @min 0
   * @max 10
   * @default 3
   */
  max_retries?: number;
  /**
   * Schedule At
   * Schedule job for later execution
   */
  schedule_at?: string | null;
}

/**
 * JobListResponse
 * Response schema for job list.
 */
export interface JobListResponse {
  /**
   * Jobs
   * List of jobs
   */
  jobs: JobResponse[];
  /**
   * Total
   * Total number of jobs
   */
  total: number;
  /**
   * Limit
   * Maximum results per page
   */
  limit: number;
  /**
   * Offset
   * Number of results skipped
   */
  offset: number;
  /**
   * Has More
   * Whether more results exist
   */
  has_more: boolean;
}

/**
 * JobResponse
 * Response schema for job data.
 */
export interface JobResponse {
  /**
   * Id
   * Job ID
   */
  id: string;
  /**
   * Name
   * Job name
   */
  name: string;
  /**
   * Function Name
   * Function name
   */
  function_name: string;
  /** Job priority */
  priority: JobPriority;
  /** Job status */
  status: JobStatus;
  /**
   * Created At
   * Creation timestamp
   * @format date-time
   */
  created_at: string;
  /**
   * Started At
   * Start timestamp
   */
  started_at?: string | null;
  /**
   * Completed At
   * Completion timestamp
   */
  completed_at?: string | null;
  /**
   * Scheduled At
   * Scheduled execution time
   */
  scheduled_at?: string | null;
  /**
   * Retry Count
   * Number of retry attempts
   */
  retry_count: number;
  /**
   * Max Retries
   * Maximum retry attempts
   */
  max_retries: number;
  /**
   * Error Message
   * Error message if failed
   */
  error_message?: string | null;
  /**
   * Result
   * Job result if completed
   */
  result?: null;
  /**
   * Progress
   * Job progress percentage
   * @min 0
   * @max 100
   * @default 0
   */
  progress?: number;
  /**
   * Progress Message
   * Progress message
   */
  progress_message?: string | null;
}

/**
 * JobStatsResponse
 * Response schema for job statistics.
 */
export interface JobStatsResponse {
  /**
   * Total Jobs
   * Total number of jobs
   */
  total_jobs: number;
  /**
   * Pending Jobs
   * Number of pending jobs
   */
  pending_jobs: number;
  /**
   * Running Jobs
   * Number of running jobs
   */
  running_jobs: number;
  /**
   * Completed Jobs
   * Number of completed jobs
   */
  completed_jobs: number;
  /**
   * Failed Jobs
   * Number of failed jobs
   */
  failed_jobs: number;
  /**
   * Queue Size
   * Current queue size
   */
  queue_size: number;
  /**
   * Active Workers
   * Number of active workers
   */
  active_workers: number;
}

/**
 * LogoutResponse
 * Schema for logout response.
 */
export interface LogoutResponse {
  /**
   * Message
   * Success message
   */
  message: string;
}

/**
 * McpStatusResponse
 * Schema for MCP status response.
 */
export interface McpStatusResponse {
  /**
   * Status
   * MCP service status
   */
  status: string;
  /**
   * Servers
   * Connected servers
   */
  servers: Record<string, any>[];
  /**
   * Last Check
   * Last health check time
   */
  last_check?: string | null;
  /**
   * Errors
   * Any error messages
   */
  errors?: string[];
}

/**
 * MessageDeleteResponse
 * Response schema for message deletion.
 */
export interface MessageDeleteResponse {
  /**
   * Message
   * Deletion result message
   */
  message: string;
}

/**
 * MessageResponse
 * Schema for message response.
 */
export interface MessageResponse {
  /** Message role */
  role: MessageRole;
  /**
   * Content
   * Message content
   * @minLength 1
   */
  content: string;
  /**
   * Id
   * Message ID
   */
  id: string;
  /**
   * Conversation Id
   * Conversation ID
   */
  conversation_id: string;
  /**
   * Sequence Number
   * Message sequence number
   */
  sequence_number: number;
  /**
   * Prompt Tokens
   * Prompt tokens used
   */
  prompt_tokens?: number | null;
  /**
   * Completion Tokens
   * Completion tokens used
   */
  completion_tokens?: number | null;
  /**
   * Total Tokens
   * Total tokens used
   */
  total_tokens?: number | null;
  /**
   * Model Used
   * Model used for generation
   */
  model_used?: string | null;
  /**
   * Provider Used
   * Provider used
   */
  provider_used?: string | null;
  /**
   * Response Time Ms
   * Response time in milliseconds
   */
  response_time_ms?: number | null;
  /**
   * Cost
   * Cost of the message
   */
  cost?: number | null;
  /**
   * Finish Reason
   * Reason for completion
   */
  finish_reason?: string | null;
  /**
   * Created At
   * Creation timestamp
   * @format date-time
   */
  created_at: string;
}

/**
 * MetricsResponse
 * Schema for application metrics response.
 */
export interface MetricsResponse {
  /**
   * Timestamp
   * Metrics collection timestamp (ISO 8601)
   */
  timestamp: string;
  /**
   * Service
   * Service name
   */
  service: string;
  /**
   * Version
   * Service version
   */
  version: string;
  /**
   * Environment
   * Environment
   */
  environment: string;
  /**
   * Health
   * Health metrics
   */
  health: Record<string, any>;
  /**
   * Performance
   * Performance statistics
   */
  performance: Record<string, any>;
  /**
   * Endpoints
   * Endpoint statistics
   */
  endpoints: Record<string, any>;
}

/**
 * ModelDefCreate
 * Schema for creating a model definition.
 */
export interface ModelDefCreate {
  /**
   * Name
   * Model name
   * @minLength 1
   * @maxLength 100
   * @pattern ^[a-zA-Z0-9_-]+$
   */
  name: string;
  /** Type of model */
  model_type: ModelType;
  /**
   * Display Name
   * Human-readable name
   * @minLength 1
   * @maxLength 200
   */
  display_name: string;
  /**
   * Description
   * Model description
   */
  description?: string | null;
  /**
   * Model Name
   * Actual model name for API calls
   * @minLength 1
   * @maxLength 200
   */
  model_name: string;
  /**
   * Max Tokens
   * Maximum tokens
   */
  max_tokens?: number | null;
  /**
   * Context Length
   * Context length
   */
  context_length?: number | null;
  /**
   * Dimensions
   * Embedding dimensions
   */
  dimensions?: number | null;
  /**
   * Chunk Size
   * Default chunk size
   */
  chunk_size?: number | null;
  /**
   * Supports Batch
   * Whether model supports batch operations
   * @default false
   */
  supports_batch?: boolean;
  /**
   * Max Batch Size
   * Maximum batch size
   */
  max_batch_size?: number | null;
  /**
   * Default Config
   * Default configuration
   */
  default_config?: Record<string, any>;
  /**
   * Is Active
   * Whether model is active
   * @default true
   */
  is_active?: boolean;
  /**
   * Is Default
   * Whether this is the default model
   * @default false
   */
  is_default?: boolean;
  /**
   * Provider Id
   * Provider ID
   */
  provider_id: string;
}

/**
 * ModelDefList
 * List of model definitions with pagination.
 */
export interface ModelDefList {
  /** Models */
  models: ModelDefWithProvider[];
  /** Total */
  total: number;
  /** Page */
  page: number;
  /** Per Page */
  per_page: number;
}

/**
 * ModelDefUpdate
 * Schema for updating a model definition.
 */
export interface ModelDefUpdate {
  /** Display Name */
  display_name?: string | null;
  /** Description */
  description?: string | null;
  /** Model Name */
  model_name?: string | null;
  /** Max Tokens */
  max_tokens?: number | null;
  /** Context Length */
  context_length?: number | null;
  /** Dimensions */
  dimensions?: number | null;
  /** Chunk Size */
  chunk_size?: number | null;
  /** Supports Batch */
  supports_batch?: boolean | null;
  /** Max Batch Size */
  max_batch_size?: number | null;
  /** Default Config */
  default_config?: Record<string, any> | null;
  /** Is Active */
  is_active?: boolean | null;
  /** Is Default */
  is_default?: boolean | null;
}

/**
 * ModelDefWithProvider
 * Model definition with provider information.
 */
export interface ModelDefWithProvider {
  /**
   * Name
   * Model name
   * @minLength 1
   * @maxLength 100
   * @pattern ^[a-zA-Z0-9_-]+$
   */
  name: string;
  /** Type of model */
  model_type: ModelType;
  /**
   * Display Name
   * Human-readable name
   * @minLength 1
   * @maxLength 200
   */
  display_name: string;
  /**
   * Description
   * Model description
   */
  description?: string | null;
  /**
   * Model Name
   * Actual model name for API calls
   * @minLength 1
   * @maxLength 200
   */
  model_name: string;
  /**
   * Max Tokens
   * Maximum tokens
   */
  max_tokens?: number | null;
  /**
   * Context Length
   * Context length
   */
  context_length?: number | null;
  /**
   * Dimensions
   * Embedding dimensions
   */
  dimensions?: number | null;
  /**
   * Chunk Size
   * Default chunk size
   */
  chunk_size?: number | null;
  /**
   * Supports Batch
   * Whether model supports batch operations
   * @default false
   */
  supports_batch?: boolean;
  /**
   * Max Batch Size
   * Maximum batch size
   */
  max_batch_size?: number | null;
  /**
   * Default Config
   * Default configuration
   */
  default_config?: Record<string, any>;
  /**
   * Is Active
   * Whether model is active
   * @default true
   */
  is_active?: boolean;
  /**
   * Is Default
   * Whether this is the default model
   * @default false
   */
  is_default?: boolean;
  /** Id */
  id: string;
  /** Provider Id */
  provider_id: string;
  /**
   * Created At
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * @format date-time
   */
  updated_at: string;
  /** Full provider schema. */
  provider: Provider;
}

/**
 * ModelDefaultResponse
 * Response schema for setting default model.
 */
export interface ModelDefaultResponse {
  /**
   * Message
   * Operation result message
   */
  message: string;
}

/**
 * ModelDeleteResponse
 * Response schema for model deletion.
 */
export interface ModelDeleteResponse {
  /**
   * Message
   * Deletion result message
   */
  message: string;
}

/**
 * NodePropertyDefinition
 * Schema for node property definition.
 */
export interface NodePropertyDefinition {
  /**
   * Name
   * Property name
   */
  name: string;
  /**
   * Type
   * Property type
   */
  type: string;
  /**
   * Required
   * Whether property is required
   * @default false
   */
  required?: boolean;
  /**
   * Description
   * Property description
   */
  description?: string | null;
  /**
   * Default Value
   * Default value
   */
  default_value?: null;
  /**
   * Options
   * Valid options for select type
   */
  options?: string[] | null;
  /**
   * Min Value
   * Minimum value for numeric types
   */
  min_value?: number | null;
  /**
   * Max Value
   * Maximum value for numeric types
   */
  max_value?: number | null;
}

/**
 * NodeTypeResponse
 * Schema for node type information.
 */
export interface NodeTypeResponse {
  /**
   * Type
   * Node type identifier
   */
  type: string;
  /**
   * Name
   * Human-readable name
   */
  name: string;
  /**
   * Description
   * Node description
   */
  description: string;
  /**
   * Category
   * Node category
   */
  category: string;
  /**
   * Properties
   * Node properties
   */
  properties: NodePropertyDefinition[];
  /**
   * Icon
   * Icon name
   */
  icon?: string | null;
  /**
   * Color
   * Node color
   */
  color?: string | null;
}

/**
 * OAuthConfigSchema
 * OAuth configuration for remote servers.
 */
export interface OAuthConfigSchema {
  /**
   * Client Id
   * OAuth client ID
   */
  client_id: string;
  /**
   * Client Secret
   * OAuth client secret
   */
  client_secret: string;
  /**
   * Token Url
   * OAuth token endpoint URL
   * @format uri
   * @minLength 1
   * @maxLength 2083
   */
  token_url: string;
  /**
   * Scope
   * OAuth scope
   */
  scope?: string | null;
}

/**
 * OptimizationSuggestion
 * Schema for optimization suggestions.
 */
export interface OptimizationSuggestion {
  /**
   * Type
   * Suggestion type
   */
  type: string;
  /**
   * Description
   * Suggestion description
   */
  description: string;
  /**
   * Impact
   * Expected impact (low/medium/high)
   */
  impact: string;
  /**
   * Node Ids
   * Affected node IDs
   */
  node_ids?: string[] | null;
}

/**
 * PaginationRequest
 * Common pagination request schema.
 */
export interface PaginationRequest {
  /**
   * Limit
   * Maximum number of results
   * @min 1
   * @max 100
   * @default 50
   */
  limit?: number;
  /**
   * Offset
   * Number of results to skip
   * @min 0
   * @default 0
   */
  offset?: number;
}

/**
 * PasswordChange
 * Schema for password change.
 */
export interface PasswordChange {
  /**
   * Current Password
   * Current password
   */
  current_password: string;
  /**
   * New Password
   * New password
   * @minLength 8
   * @maxLength 128
   */
  new_password: string;
}

/**
 * PasswordChangeResponse
 * Schema for password change response.
 */
export interface PasswordChangeResponse {
  /**
   * Message
   * Success message
   */
  message: string;
}

/**
 * PasswordResetConfirmResponse
 * Schema for password reset confirmation response.
 */
export interface PasswordResetConfirmResponse {
  /**
   * Message
   * Success message
   */
  message: string;
}

/**
 * PasswordResetRequestResponse
 * Schema for password reset request response.
 */
export interface PasswordResetRequestResponse {
  /**
   * Message
   * Success message
   */
  message: string;
}

/**
 * PerformanceMetricsResponse
 * Schema for performance metrics response.
 */
export interface PerformanceMetricsResponse {
  /**
   * Avg Response Time Ms
   * Average response time
   */
  avg_response_time_ms: number;
  /**
   * Median Response Time Ms
   * Median response time
   */
  median_response_time_ms: number;
  /**
   * P95 Response Time Ms
   * 95th percentile response time
   */
  p95_response_time_ms: number;
  /**
   * P99 Response Time Ms
   * 99th percentile response time
   */
  p99_response_time_ms: number;
  /**
   * Requests Per Minute
   * Average requests per minute
   */
  requests_per_minute: number;
  /**
   * Tokens Per Minute
   * Average tokens per minute
   */
  tokens_per_minute: number;
  /**
   * Total Errors
   * Total number of errors
   */
  total_errors: number;
  /**
   * Error Rate
   * Error rate percentage
   */
  error_rate: number;
  /**
   * Errors By Type
   * Errors grouped by type
   */
  errors_by_type: Record<string, number>;
  /**
   * Performance By Model
   * Performance metrics by model
   */
  performance_by_model: Record<string, Record<string, number>>;
  /**
   * Performance By Provider
   * Performance metrics by provider
   */
  performance_by_provider: Record<string, Record<string, number>>;
  /**
   * Database Response Time Ms
   * Average database response time
   */
  database_response_time_ms: number;
  /**
   * Vector Search Time Ms
   * Average vector search time
   */
  vector_search_time_ms: number;
  /**
   * Embedding Generation Time Ms
   * Average embedding generation time
   */
  embedding_generation_time_ms: number;
}

/**
 * PerformanceStatsResponse
 * Schema for performance statistics response.
 */
export interface PerformanceStatsResponse {
  /**
   * Total Executions
   * Total number of executions
   */
  total_executions: number;
  /**
   * Avg Execution Time Ms
   * Average execution time in milliseconds
   */
  avg_execution_time_ms: number;
  /**
   * Min Execution Time Ms
   * Minimum execution time in milliseconds
   */
  min_execution_time_ms: number;
  /**
   * Max Execution Time Ms
   * Maximum execution time in milliseconds
   */
  max_execution_time_ms: number;
  /**
   * Workflow Types
   * Execution count by workflow type
   */
  workflow_types: Record<string, number>;
  /**
   * Error Counts
   * Error count by type
   */
  error_counts: Record<string, number>;
  /**
   * Cache Stats
   * Cache statistics
   */
  cache_stats: Record<string, any>;
  /**
   * Tool Stats
   * Tool usage statistics
   */
  tool_stats: Record<string, any>;
  /**
   * Timestamp
   * Statistics timestamp
   */
  timestamp: number;
}

/**
 * PluginActionResponse
 * Response schema for plugin actions.
 */
export interface PluginActionResponse {
  /**
   * Success
   * Whether action was successful
   */
  success: boolean;
  /**
   * Message
   * Action result message
   */
  message: string;
  /**
   * Plugin Id
   * Plugin ID
   */
  plugin_id: string;
}

/**
 * PluginDeleteResponse
 * Response schema for plugin deletion.
 */
export interface PluginDeleteResponse {
  /**
   * Success
   * Whether deletion was successful
   */
  success: boolean;
  /**
   * Message
   * Deletion result message
   */
  message: string;
}

/**
 * PluginHealthCheckResponse
 * Response schema for plugin health check.
 */
export interface PluginHealthCheckResponse {
  /**
   * Summary
   * Health check summary
   */
  summary: Record<string, any>;
  /**
   * Results
   * Detailed health check results for each plugin
   */
  results: Record<string, Record<string, any>>;
}

/**
 * PluginInstallRequest
 * Request schema for installing a plugin.
 */
export interface PluginInstallRequest {
  /**
   * Plugin Path
   * Path to plugin file or directory
   */
  plugin_path: string;
  /**
   * Enable On Install
   * Enable plugin after installation
   * @default true
   */
  enable_on_install?: boolean;
}

/**
 * PluginListResponse
 * Response schema for plugin list.
 */
export interface PluginListResponse {
  /**
   * Plugins
   * List of plugins
   */
  plugins: PluginResponse[];
  /**
   * Total
   * Total number of plugins
   */
  total: number;
}

/**
 * PluginResponse
 * Response schema for plugin data.
 */
export interface PluginResponse {
  /**
   * Id
   * Plugin ID
   */
  id: string;
  /**
   * Name
   * Plugin name
   */
  name: string;
  /**
   * Version
   * Plugin version
   */
  version: string;
  /**
   * Description
   * Plugin description
   */
  description: string;
  /**
   * Author
   * Plugin author
   */
  author: string;
  /** Plugin type */
  plugin_type: PluginType;
  /** Plugin status */
  status: PluginStatus;
  /**
   * Entry Point
   * Plugin entry point
   */
  entry_point: string;
  /**
   * Capabilities
   * Plugin capabilities
   */
  capabilities: Record<string, any>[];
  /**
   * Dependencies
   * Plugin dependencies
   */
  dependencies: string[];
  /**
   * Permissions
   * Required permissions
   */
  permissions: string[];
  /**
   * Enabled
   * Whether plugin is enabled
   */
  enabled: boolean;
  /**
   * Error Message
   * Error message if any
   */
  error_message?: string | null;
  /**
   * Installed At
   * Installation timestamp
   * @format date-time
   */
  installed_at: string;
  /**
   * Updated At
   * Last update timestamp
   * @format date-time
   */
  updated_at: string;
  /**
   * Metadata
   * Additional metadata
   */
  metadata: Record<string, any>;
}

/**
 * PluginStatsResponse
 * Response schema for plugin statistics.
 */
export interface PluginStatsResponse {
  /**
   * Total Plugins
   * Total number of plugins
   */
  total_plugins: number;
  /**
   * Active Plugins
   * Number of active plugins
   */
  active_plugins: number;
  /**
   * Inactive Plugins
   * Number of inactive plugins
   */
  inactive_plugins: number;
  /**
   * Plugin Types
   * Plugin count by type
   */
  plugin_types: Record<string, number>;
  /**
   * Plugins Directory
   * Plugin installation directory
   */
  plugins_directory: string;
}

/**
 * PluginUpdateRequest
 * Request schema for updating a plugin.
 */
export interface PluginUpdateRequest {
  /**
   * Enabled
   * Enable/disable plugin
   */
  enabled?: boolean | null;
  /**
   * Configuration
   * Plugin configuration
   */
  configuration?: Record<string, any> | null;
}

/**
 * ProfileCloneRequest
 * Schema for profile clone request.
 */
export interface ProfileCloneRequest {
  /**
   * Name
   * New profile name
   * @minLength 1
   * @maxLength 255
   */
  name: string;
  /**
   * Description
   * New profile description
   */
  description?: string | null;
  /** Modifications to apply to cloned profile */
  modifications?: ProfileUpdate | null;
}

/**
 * ProfileCreate
 * Schema for creating a profile.
 */
export interface ProfileCreate {
  /**
   * Name
   * Profile name
   * @minLength 1
   * @maxLength 255
   */
  name: string;
  /**
   * Description
   * Profile description
   */
  description?: string | null;
  /**
   * Profile type
   * @default "custom"
   */
  profile_type?: ProfileType;
  /**
   * Llm Provider
   * LLM provider (openai, anthropic, etc.)
   * @minLength 1
   * @maxLength 50
   */
  llm_provider: string;
  /**
   * Llm Model
   * LLM model name
   * @minLength 1
   * @maxLength 100
   */
  llm_model: string;
  /**
   * Temperature
   * Temperature for generation
   * @min 0
   * @max 2
   * @default 0.7
   */
  temperature?: number;
  /**
   * Top P
   * Top-p sampling parameter
   */
  top_p?: number | null;
  /**
   * Top K
   * Top-k sampling parameter
   */
  top_k?: number | null;
  /**
   * Max Tokens
   * Maximum tokens to generate
   * @min 1
   * @max 100000
   * @default 4096
   */
  max_tokens?: number;
  /**
   * Presence Penalty
   * Presence penalty
   */
  presence_penalty?: number | null;
  /**
   * Frequency Penalty
   * Frequency penalty
   */
  frequency_penalty?: number | null;
  /**
   * Context Window
   * Context window size
   * @min 1
   * @max 200000
   * @default 4096
   */
  context_window?: number;
  /**
   * System Prompt
   * System prompt template
   */
  system_prompt?: string | null;
  /**
   * Memory Enabled
   * Enable conversation memory
   * @default true
   */
  memory_enabled?: boolean;
  /**
   * Memory Strategy
   * Memory management strategy
   */
  memory_strategy?: string | null;
  /**
   * Enable Retrieval
   * Enable document retrieval
   * @default false
   */
  enable_retrieval?: boolean;
  /**
   * Retrieval Limit
   * Number of documents to retrieve
   * @min 1
   * @max 50
   * @default 5
   */
  retrieval_limit?: number;
  /**
   * Retrieval Score Threshold
   * Minimum retrieval score
   * @min 0
   * @max 1
   * @default 0.7
   */
  retrieval_score_threshold?: number;
  /**
   * Enable Tools
   * Enable tool calling
   * @default false
   */
  enable_tools?: boolean;
  /**
   * Available Tools
   * List of available tools
   */
  available_tools?: string[] | null;
  /**
   * Tool Choice
   * Tool choice strategy
   */
  tool_choice?: string | null;
  /**
   * Content Filter Enabled
   * Enable content filtering
   * @default true
   */
  content_filter_enabled?: boolean;
  /**
   * Safety Level
   * Safety level
   */
  safety_level?: string | null;
  /**
   * Response Format
   * Response format (json, text, markdown)
   */
  response_format?: string | null;
  /**
   * Stream Response
   * Enable streaming responses
   * @default true
   */
  stream_response?: boolean;
  /**
   * Seed
   * Random seed for reproducibility
   */
  seed?: number | null;
  /**
   * Stop Sequences
   * Stop sequences
   */
  stop_sequences?: string[] | null;
  /**
   * Logit Bias
   * Logit bias adjustments
   */
  logit_bias?: Record<string, number> | null;
  /**
   * Embedding Provider
   * Embedding provider
   */
  embedding_provider?: string | null;
  /**
   * Embedding Model
   * Embedding model
   */
  embedding_model?: string | null;
  /**
   * Is Public
   * Whether profile is public
   * @default false
   */
  is_public?: boolean;
  /**
   * Tags
   * Profile tags
   */
  tags?: string[] | null;
  /**
   * Extra Metadata
   * Additional metadata
   */
  extra_metadata?: Record<string, any> | null;
}

/**
 * ProfileDeleteResponse
 * Schema for profile delete response.
 */
export interface ProfileDeleteResponse {
  /**
   * Message
   * Success message
   */
  message: string;
}

/**
 * ProfileListResponse
 * Schema for profile list response.
 */
export interface ProfileListResponse {
  /**
   * Profiles
   * List of profiles
   */
  profiles: ProfileResponse[];
  /**
   * Total Count
   * Total number of profiles
   */
  total_count: number;
  /**
   * Limit
   * Applied limit
   */
  limit: number;
  /**
   * Offset
   * Applied offset
   */
  offset: number;
}

/**
 * ProfileResponse
 * Schema for profile response.
 */
export interface ProfileResponse {
  /**
   * Name
   * Profile name
   * @minLength 1
   * @maxLength 255
   */
  name: string;
  /**
   * Description
   * Profile description
   */
  description?: string | null;
  /**
   * Profile type
   * @default "custom"
   */
  profile_type?: ProfileType;
  /**
   * Llm Provider
   * LLM provider (openai, anthropic, etc.)
   * @minLength 1
   * @maxLength 50
   */
  llm_provider: string;
  /**
   * Llm Model
   * LLM model name
   * @minLength 1
   * @maxLength 100
   */
  llm_model: string;
  /**
   * Temperature
   * Temperature for generation
   * @min 0
   * @max 2
   * @default 0.7
   */
  temperature?: number;
  /**
   * Top P
   * Top-p sampling parameter
   */
  top_p?: number | null;
  /**
   * Top K
   * Top-k sampling parameter
   */
  top_k?: number | null;
  /**
   * Max Tokens
   * Maximum tokens to generate
   * @min 1
   * @max 100000
   * @default 4096
   */
  max_tokens?: number;
  /**
   * Presence Penalty
   * Presence penalty
   */
  presence_penalty?: number | null;
  /**
   * Frequency Penalty
   * Frequency penalty
   */
  frequency_penalty?: number | null;
  /**
   * Context Window
   * Context window size
   * @min 1
   * @max 200000
   * @default 4096
   */
  context_window?: number;
  /**
   * System Prompt
   * System prompt template
   */
  system_prompt?: string | null;
  /**
   * Memory Enabled
   * Enable conversation memory
   * @default true
   */
  memory_enabled?: boolean;
  /**
   * Memory Strategy
   * Memory management strategy
   */
  memory_strategy?: string | null;
  /**
   * Enable Retrieval
   * Enable document retrieval
   * @default false
   */
  enable_retrieval?: boolean;
  /**
   * Retrieval Limit
   * Number of documents to retrieve
   * @min 1
   * @max 50
   * @default 5
   */
  retrieval_limit?: number;
  /**
   * Retrieval Score Threshold
   * Minimum retrieval score
   * @min 0
   * @max 1
   * @default 0.7
   */
  retrieval_score_threshold?: number;
  /**
   * Enable Tools
   * Enable tool calling
   * @default false
   */
  enable_tools?: boolean;
  /**
   * Available Tools
   * List of available tools
   */
  available_tools?: string[] | null;
  /**
   * Tool Choice
   * Tool choice strategy
   */
  tool_choice?: string | null;
  /**
   * Content Filter Enabled
   * Enable content filtering
   * @default true
   */
  content_filter_enabled?: boolean;
  /**
   * Safety Level
   * Safety level
   */
  safety_level?: string | null;
  /**
   * Response Format
   * Response format (json, text, markdown)
   */
  response_format?: string | null;
  /**
   * Stream Response
   * Enable streaming responses
   * @default true
   */
  stream_response?: boolean;
  /**
   * Seed
   * Random seed for reproducibility
   */
  seed?: number | null;
  /**
   * Stop Sequences
   * Stop sequences
   */
  stop_sequences?: string[] | null;
  /**
   * Logit Bias
   * Logit bias adjustments
   */
  logit_bias?: Record<string, number> | null;
  /**
   * Embedding Provider
   * Embedding provider
   */
  embedding_provider?: string | null;
  /**
   * Embedding Model
   * Embedding model
   */
  embedding_model?: string | null;
  /**
   * Is Public
   * Whether profile is public
   * @default false
   */
  is_public?: boolean;
  /**
   * Tags
   * Profile tags
   */
  tags?: string[] | null;
  /**
   * Extra Metadata
   * Additional metadata
   */
  extra_metadata?: Record<string, any> | null;
  /**
   * Id
   * Profile ID
   */
  id: string;
  /**
   * Owner Id
   * Owner user ID
   */
  owner_id: string;
  /**
   * Usage Count
   * Number of times used
   */
  usage_count: number;
  /**
   * Total Tokens Used
   * Total tokens used
   */
  total_tokens_used: number;
  /**
   * Total Cost
   * Total cost incurred
   */
  total_cost: number;
  /**
   * Last Used At
   * Last usage time
   */
  last_used_at?: string | null;
  /**
   * Created At
   * Creation time
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update time
   * @format date-time
   */
  updated_at: string;
}

/**
 * ProfileStatsResponse
 * Schema for profile statistics response.
 */
export interface ProfileStatsResponse {
  /**
   * Total Profiles
   * Total number of profiles
   */
  total_profiles: number;
  /**
   * Profiles By Type
   * Profiles grouped by type
   */
  profiles_by_type: Record<string, number>;
  /**
   * Profiles By Provider
   * Profiles grouped by LLM provider
   */
  profiles_by_provider: Record<string, number>;
  /**
   * Most Used Profiles
   * Most frequently used profiles
   */
  most_used_profiles: ProfileResponse[];
  /**
   * Recent Profiles
   * Recently created profiles
   */
  recent_profiles: ProfileResponse[];
  /**
   * Usage Stats
   * Usage statistics
   */
  usage_stats: Record<string, any>;
}

/**
 * ProfileTestRequest
 * Schema for profile test request.
 */
export interface ProfileTestRequest {
  /**
   * Test Message
   * Test message
   * @minLength 1
   * @maxLength 1000
   */
  test_message: string;
  /**
   * Include Retrieval
   * Include retrieval in test
   * @default false
   */
  include_retrieval?: boolean;
  /**
   * Include Tools
   * Include tools in test
   * @default false
   */
  include_tools?: boolean;
}

/**
 * ProfileTestResponse
 * Schema for profile test response.
 */
export interface ProfileTestResponse {
  /**
   * Profile Id
   * Profile ID
   */
  profile_id: string;
  /**
   * Test Message
   * Test message sent
   */
  test_message: string;
  /**
   * Response
   * Generated response
   */
  response: string;
  /**
   * Usage Info
   * Token usage and cost information
   */
  usage_info: Record<string, any>;
  /**
   * Response Time Ms
   * Response time in milliseconds
   */
  response_time_ms: number;
  /**
   * Retrieval Results
   * Retrieval results if enabled
   */
  retrieval_results?: Record<string, any>[] | null;
  /**
   * Tools Used
   * Tools used if enabled
   */
  tools_used?: string[] | null;
}

/**
 * ProfileUpdate
 * Schema for updating a profile.
 */
export interface ProfileUpdate {
  /**
   * Name
   * Profile name
   */
  name?: string | null;
  /**
   * Description
   * Profile description
   */
  description?: string | null;
  /** Profile type */
  profile_type?: ProfileType | null;
  /**
   * Llm Provider
   * LLM provider
   */
  llm_provider?: string | null;
  /**
   * Llm Model
   * LLM model name
   */
  llm_model?: string | null;
  /**
   * Temperature
   * Temperature
   */
  temperature?: number | null;
  /**
   * Top P
   * Top-p parameter
   */
  top_p?: number | null;
  /**
   * Top K
   * Top-k parameter
   */
  top_k?: number | null;
  /**
   * Max Tokens
   * Maximum tokens
   */
  max_tokens?: number | null;
  /**
   * Presence Penalty
   * Presence penalty
   */
  presence_penalty?: number | null;
  /**
   * Frequency Penalty
   * Frequency penalty
   */
  frequency_penalty?: number | null;
  /**
   * Context Window
   * Context window size
   */
  context_window?: number | null;
  /**
   * System Prompt
   * System prompt template
   */
  system_prompt?: string | null;
  /**
   * Memory Enabled
   * Enable conversation memory
   */
  memory_enabled?: boolean | null;
  /**
   * Memory Strategy
   * Memory management strategy
   */
  memory_strategy?: string | null;
  /**
   * Enable Retrieval
   * Enable document retrieval
   */
  enable_retrieval?: boolean | null;
  /**
   * Retrieval Limit
   * Number of documents to retrieve
   */
  retrieval_limit?: number | null;
  /**
   * Retrieval Score Threshold
   * Minimum retrieval score
   */
  retrieval_score_threshold?: number | null;
  /**
   * Enable Tools
   * Enable tool calling
   */
  enable_tools?: boolean | null;
  /**
   * Available Tools
   * List of available tools
   */
  available_tools?: string[] | null;
  /**
   * Tool Choice
   * Tool choice strategy
   */
  tool_choice?: string | null;
  /**
   * Content Filter Enabled
   * Enable content filtering
   */
  content_filter_enabled?: boolean | null;
  /**
   * Safety Level
   * Safety level
   */
  safety_level?: string | null;
  /**
   * Response Format
   * Response format
   */
  response_format?: string | null;
  /**
   * Stream Response
   * Enable streaming responses
   */
  stream_response?: boolean | null;
  /**
   * Seed
   * Random seed
   */
  seed?: number | null;
  /**
   * Stop Sequences
   * Stop sequences
   */
  stop_sequences?: string[] | null;
  /**
   * Logit Bias
   * Logit bias adjustments
   */
  logit_bias?: Record<string, number> | null;
  /**
   * Embedding Provider
   * Embedding provider
   */
  embedding_provider?: string | null;
  /**
   * Embedding Model
   * Embedding model
   */
  embedding_model?: string | null;
  /**
   * Is Public
   * Whether profile is public
   */
  is_public?: boolean | null;
  /**
   * Tags
   * Profile tags
   */
  tags?: string[] | null;
  /**
   * Extra Metadata
   * Additional metadata
   */
  extra_metadata?: Record<string, any> | null;
}

/**
 * PromptCloneRequest
 * Schema for prompt clone request.
 */
export interface PromptCloneRequest {
  /**
   * Name
   * New prompt name
   * @minLength 1
   * @maxLength 255
   */
  name: string;
  /**
   * Description
   * New prompt description
   */
  description?: string | null;
  /**
   * Modifications
   * Modifications to apply
   */
  modifications?: Record<string, any> | null;
}

/**
 * PromptCreate
 * Schema for creating a prompt.
 */
export interface PromptCreate {
  /**
   * Name
   * Prompt name
   * @minLength 1
   * @maxLength 255
   */
  name: string;
  /**
   * Description
   * Prompt description
   */
  description?: string | null;
  /**
   * Prompt type
   * @default "template"
   */
  prompt_type?: PromptType;
  /**
   * Prompt category
   * @default "general"
   */
  category?: PromptCategory;
  /**
   * Content
   * Prompt content/template
   * @minLength 1
   */
  content: string;
  /**
   * Variables
   * Template variables
   */
  variables?: string[] | null;
  /**
   * Template Format
   * Template format (f-string, jinja2, mustache)
   * @default "f-string"
   */
  template_format?: string;
  /**
   * Input Schema
   * JSON schema for input validation
   */
  input_schema?: Record<string, any> | null;
  /**
   * Output Schema
   * JSON schema for output validation
   */
  output_schema?: Record<string, any> | null;
  /**
   * Max Length
   * Maximum content length
   */
  max_length?: number | null;
  /**
   * Min Length
   * Minimum content length
   */
  min_length?: number | null;
  /**
   * Required Variables
   * Required template variables
   */
  required_variables?: string[] | null;
  /**
   * Examples
   * Usage examples
   */
  examples?: Record<string, any>[] | null;
  /**
   * Test Cases
   * Test cases
   */
  test_cases?: Record<string, any>[] | null;
  /**
   * Suggested Temperature
   * Suggested temperature
   */
  suggested_temperature?: number | null;
  /**
   * Suggested Max Tokens
   * Suggested max tokens
   */
  suggested_max_tokens?: number | null;
  /**
   * Suggested Providers
   * Suggested LLM providers
   */
  suggested_providers?: string[] | null;
  /**
   * Is Chain
   * Whether this is a chain prompt
   * @default false
   */
  is_chain?: boolean;
  /**
   * Chain Steps
   * Chain execution steps
   */
  chain_steps?: Record<string, any>[] | null;
  /**
   * Parent Prompt Id
   * Parent prompt ID for chains
   */
  parent_prompt_id?: string | null;
  /**
   * Is Public
   * Whether prompt is public
   * @default false
   */
  is_public?: boolean;
  /**
   * Tags
   * Prompt tags
   */
  tags?: string[] | null;
  /**
   * Extra Metadata
   * Additional metadata
   */
  extra_metadata?: Record<string, any> | null;
}

/**
 * PromptDeleteResponse
 * Schema for prompt delete response.
 */
export interface PromptDeleteResponse {
  /**
   * Message
   * Success message
   */
  message: string;
}

/**
 * PromptListResponse
 * Schema for prompt list response.
 */
export interface PromptListResponse {
  /**
   * Prompts
   * List of prompts
   */
  prompts: PromptResponse[];
  /**
   * Total Count
   * Total number of prompts
   */
  total_count: number;
  /**
   * Limit
   * Requested limit
   */
  limit: number;
  /**
   * Offset
   * Requested offset
   */
  offset: number;
}

/**
 * PromptResponse
 * Schema for prompt response.
 */
export interface PromptResponse {
  /**
   * Id
   * Prompt ID
   */
  id: string;
  /**
   * Owner Id
   * Owner user ID
   */
  owner_id: string;
  /**
   * Name
   * Prompt name
   */
  name: string;
  /**
   * Description
   * Prompt description
   */
  description?: string | null;
  /** Prompt type */
  prompt_type: PromptType;
  /** Prompt category */
  category: PromptCategory;
  /**
   * Content
   * Prompt content/template
   */
  content: string;
  /**
   * Variables
   * Template variables
   */
  variables?: string[] | null;
  /**
   * Template Format
   * Template format
   */
  template_format: string;
  /**
   * Input Schema
   * Input validation schema
   */
  input_schema?: Record<string, any> | null;
  /**
   * Output Schema
   * Output validation schema
   */
  output_schema?: Record<string, any> | null;
  /**
   * Max Length
   * Maximum content length
   */
  max_length?: number | null;
  /**
   * Min Length
   * Minimum content length
   */
  min_length?: number | null;
  /**
   * Required Variables
   * Required template variables
   */
  required_variables?: string[] | null;
  /**
   * Examples
   * Usage examples
   */
  examples?: Record<string, any>[] | null;
  /**
   * Test Cases
   * Test cases
   */
  test_cases?: Record<string, any>[] | null;
  /**
   * Suggested Temperature
   * Suggested temperature
   */
  suggested_temperature?: number | null;
  /**
   * Suggested Max Tokens
   * Suggested max tokens
   */
  suggested_max_tokens?: number | null;
  /**
   * Suggested Providers
   * Suggested LLM providers
   */
  suggested_providers?: string[] | null;
  /**
   * Is Chain
   * Whether this is a chain prompt
   */
  is_chain: boolean;
  /**
   * Chain Steps
   * Chain execution steps
   */
  chain_steps?: Record<string, any>[] | null;
  /**
   * Parent Prompt Id
   * Parent prompt ID
   */
  parent_prompt_id?: string | null;
  /**
   * Version
   * Prompt version
   */
  version: number;
  /**
   * Is Latest
   * Whether this is the latest version
   */
  is_latest: boolean;
  /**
   * Changelog
   * Version changelog
   */
  changelog?: string | null;
  /**
   * Is Public
   * Whether prompt is public
   */
  is_public: boolean;
  /**
   * Rating
   * Average rating
   */
  rating?: number | null;
  /**
   * Rating Count
   * Number of ratings
   */
  rating_count: number;
  /**
   * Usage Count
   * Usage count
   */
  usage_count: number;
  /**
   * Success Rate
   * Success rate
   */
  success_rate?: number | null;
  /**
   * Avg Response Time Ms
   * Average response time
   */
  avg_response_time_ms?: number | null;
  /**
   * Last Used At
   * Last used timestamp
   */
  last_used_at?: string | null;
  /**
   * Total Tokens Used
   * Total tokens used
   */
  total_tokens_used: number;
  /**
   * Total Cost
   * Total cost
   */
  total_cost: number;
  /**
   * Avg Tokens Per Use
   * Average tokens per use
   */
  avg_tokens_per_use?: number | null;
  /**
   * Tags
   * Prompt tags
   */
  tags?: string[] | null;
  /**
   * Extra Metadata
   * Additional metadata
   */
  extra_metadata?: Record<string, any> | null;
  /**
   * Content Hash
   * Content hash
   */
  content_hash: string;
  /**
   * Estimated Tokens
   * Estimated token count
   */
  estimated_tokens?: number | null;
  /**
   * Language
   * Content language
   */
  language?: string | null;
  /**
   * Created At
   * Creation timestamp
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update timestamp
   * @format date-time
   */
  updated_at: string;
}

/**
 * PromptStatsResponse
 * Schema for prompt statistics response.
 */
export interface PromptStatsResponse {
  /**
   * Total Prompts
   * Total number of prompts
   */
  total_prompts: number;
  /**
   * Prompts By Type
   * Prompts by type
   */
  prompts_by_type: Record<string, number>;
  /**
   * Prompts By Category
   * Prompts by category
   */
  prompts_by_category: Record<string, number>;
  /**
   * Most Used Prompts
   * Most used prompts
   */
  most_used_prompts: PromptResponse[];
  /**
   * Recent Prompts
   * Recently created prompts
   */
  recent_prompts: PromptResponse[];
  /**
   * Usage Stats
   * Usage statistics
   */
  usage_stats: Record<string, any>;
}

/**
 * PromptTestRequest
 * Schema for prompt test request.
 */
export interface PromptTestRequest {
  /**
   * Variables
   * Variables to test with
   */
  variables: Record<string, any>;
  /**
   * Validate Only
   * Only validate, don't render
   * @default false
   */
  validate_only?: boolean;
  /**
   * Include Performance Metrics
   * Include detailed performance metrics
   * @default false
   */
  include_performance_metrics?: boolean;
  /**
   * Timeout Ms
   * Test timeout in milliseconds
   * @min 1000
   * @max 60000
   * @default 30000
   */
  timeout_ms?: number;
}

/**
 * PromptTestResponse
 * Schema for prompt test response.
 */
export interface PromptTestResponse {
  /**
   * Rendered Content
   * Rendered prompt content
   */
  rendered_content?: string | null;
  /**
   * Validation Result
   * Validation results
   */
  validation_result: Record<string, any>;
  /**
   * Estimated Tokens
   * Estimated token count
   */
  estimated_tokens?: number | null;
  /**
   * Test Duration Ms
   * Test execution time
   */
  test_duration_ms: number;
  /**
   * Template Variables Used
   * Template variables actually used
   */
  template_variables_used: string[];
  /**
   * Security Warnings
   * Security warnings if any
   */
  security_warnings?: string[];
  /**
   * Performance Metrics
   * Detailed performance metrics
   */
  performance_metrics?: Record<string, any> | null;
}

/**
 * PromptUpdate
 * Schema for updating a prompt.
 */
export interface PromptUpdate {
  /**
   * Name
   * Prompt name
   */
  name?: string | null;
  /**
   * Description
   * Prompt description
   */
  description?: string | null;
  /** Prompt type */
  prompt_type?: PromptType | null;
  /** Prompt category */
  category?: PromptCategory | null;
  /**
   * Content
   * Prompt content/template
   */
  content?: string | null;
  /**
   * Variables
   * Template variables
   */
  variables?: string[] | null;
  /**
   * Template Format
   * Template format
   */
  template_format?: string | null;
  /**
   * Input Schema
   * Input validation schema
   */
  input_schema?: Record<string, any> | null;
  /**
   * Output Schema
   * Output validation schema
   */
  output_schema?: Record<string, any> | null;
  /**
   * Max Length
   * Maximum content length
   */
  max_length?: number | null;
  /**
   * Min Length
   * Minimum content length
   */
  min_length?: number | null;
  /**
   * Required Variables
   * Required template variables
   */
  required_variables?: string[] | null;
  /**
   * Examples
   * Usage examples
   */
  examples?: Record<string, any>[] | null;
  /**
   * Test Cases
   * Test cases
   */
  test_cases?: Record<string, any>[] | null;
  /**
   * Suggested Temperature
   * Suggested temperature
   */
  suggested_temperature?: number | null;
  /**
   * Suggested Max Tokens
   * Suggested max tokens
   */
  suggested_max_tokens?: number | null;
  /**
   * Suggested Providers
   * Suggested LLM providers
   */
  suggested_providers?: string[] | null;
  /**
   * Is Chain
   * Whether this is a chain prompt
   */
  is_chain?: boolean | null;
  /**
   * Chain Steps
   * Chain execution steps
   */
  chain_steps?: Record<string, any>[] | null;
  /**
   * Parent Prompt Id
   * Parent prompt ID
   */
  parent_prompt_id?: string | null;
  /**
   * Is Public
   * Whether prompt is public
   */
  is_public?: boolean | null;
  /**
   * Tags
   * Prompt tags
   */
  tags?: string[] | null;
  /**
   * Extra Metadata
   * Additional metadata
   */
  extra_metadata?: Record<string, any> | null;
}

/**
 * Provider
 * Full provider schema.
 */
export interface Provider {
  /**
   * Name
   * Unique provider name
   * @minLength 1
   * @maxLength 100
   * @pattern ^[a-zA-Z0-9_-]+$
   */
  name: string;
  /** Type of provider */
  provider_type: ProviderType;
  /**
   * Display Name
   * Human-readable name
   * @minLength 1
   * @maxLength 200
   */
  display_name: string;
  /**
   * Description
   * Provider description
   */
  description?: string | null;
  /**
   * Api Key Required
   * Whether API key is required
   * @default true
   */
  api_key_required?: boolean;
  /**
   * Base Url
   * Base URL for API
   */
  base_url?: string | null;
  /**
   * Default Config
   * Default configuration
   */
  default_config?: Record<string, any>;
  /**
   * Is Active
   * Whether provider is active
   * @default true
   */
  is_active?: boolean;
  /**
   * Is Default
   * Whether this is the default provider
   * @default false
   */
  is_default?: boolean;
  /** Id */
  id: string;
  /**
   * Created At
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * @format date-time
   */
  updated_at: string;
}

/**
 * ProviderCreate
 * Schema for creating a provider.
 */
export interface ProviderCreate {
  /**
   * Name
   * Unique provider name
   * @minLength 1
   * @maxLength 100
   * @pattern ^[a-zA-Z0-9_-]+$
   */
  name: string;
  /** Type of provider */
  provider_type: ProviderType;
  /**
   * Display Name
   * Human-readable name
   * @minLength 1
   * @maxLength 200
   */
  display_name: string;
  /**
   * Description
   * Provider description
   */
  description?: string | null;
  /**
   * Api Key Required
   * Whether API key is required
   * @default true
   */
  api_key_required?: boolean;
  /**
   * Base Url
   * Base URL for API
   */
  base_url?: string | null;
  /**
   * Default Config
   * Default configuration
   */
  default_config?: Record<string, any>;
  /**
   * Is Active
   * Whether provider is active
   * @default true
   */
  is_active?: boolean;
  /**
   * Is Default
   * Whether this is the default provider
   * @default false
   */
  is_default?: boolean;
}

/**
 * ProviderDefaultResponse
 * Response schema for setting default provider.
 */
export interface ProviderDefaultResponse {
  /**
   * Message
   * Operation result message
   */
  message: string;
}

/**
 * ProviderDeleteResponse
 * Response schema for provider deletion.
 */
export interface ProviderDeleteResponse {
  /**
   * Message
   * Deletion result message
   */
  message: string;
}

/**
 * ProviderList
 * List of providers with pagination.
 */
export interface ProviderList {
  /** Providers */
  providers: Provider[];
  /** Total */
  total: number;
  /** Page */
  page: number;
  /** Per Page */
  per_page: number;
}

/**
 * ProviderUpdate
 * Schema for updating a provider.
 */
export interface ProviderUpdate {
  /** Display Name */
  display_name?: string | null;
  /** Description */
  description?: string | null;
  /** Api Key Required */
  api_key_required?: boolean | null;
  /** Base Url */
  base_url?: string | null;
  /** Default Config */
  default_config?: Record<string, any> | null;
  /** Is Active */
  is_active?: boolean | null;
  /** Is Default */
  is_default?: boolean | null;
}

/**
 * ReadinessCheckResponse
 * Schema for readiness check response.
 */
export interface ReadinessCheckResponse {
  /** Readiness status */
  status: ReadinessStatus;
  /**
   * Service
   * Service name
   */
  service: string;
  /**
   * Version
   * Service version
   */
  version: string;
  /**
   * Environment
   * Environment
   */
  environment: string;
  /**
   * Checks
   * Health check results
   */
  checks: Record<string, any>;
}

/**
 * RestoreRequest
 * Request schema for restoring from backup.
 */
export interface RestoreRequest {
  /**
   * Backup Id
   * Backup ID to restore from
   */
  backup_id: string;
  /**
   * Restore Options
   * Restore options
   */
  restore_options?: Record<string, any>;
  /**
   * Create Backup Before Restore
   * Create backup before restore
   * @default true
   */
  create_backup_before_restore?: boolean;
  /**
   * Verify Integrity
   * Verify backup integrity before restore
   * @default true
   */
  verify_integrity?: boolean;
}

/**
 * RestoreResponse
 * Response schema for restore operation.
 */
export interface RestoreResponse {
  /**
   * Restore Id
   * Restore operation ID
   */
  restore_id: string;
  /**
   * Backup Id
   * Source backup ID
   */
  backup_id: string;
  /**
   * Status
   * Restore status
   */
  status: string;
  /**
   * Progress
   * Restore progress percentage
   * @min 0
   * @max 100
   * @default 0
   */
  progress?: number;
  /**
   * Records Restored
   * Number of records restored
   * @default 0
   */
  records_restored?: number;
  /**
   * Started At
   * Restore start timestamp
   * @format date-time
   */
  started_at: string;
  /**
   * Completed At
   * Restore completion timestamp
   */
  completed_at?: string | null;
  /**
   * Error Message
   * Error message if failed
   */
  error_message?: string | null;
}

/**
 * RoleToolAccessCreate
 * Schema for creating role-based tool access.
 */
export interface RoleToolAccessCreate {
  /** User role */
  role: UserRole;
  /**
   * Tool Pattern
   * Tool name pattern
   */
  tool_pattern?: string | null;
  /**
   * Server Pattern
   * Server name pattern
   */
  server_pattern?: string | null;
  /** Access level */
  access_level: ToolAccessLevel;
  /** Default Rate Limit Per Hour */
  default_rate_limit_per_hour?: number | null;
  /** Default Rate Limit Per Day */
  default_rate_limit_per_day?: number | null;
  /** Allowed Hours */
  allowed_hours?: number[] | null;
  /** Allowed Days */
  allowed_days?: number[] | null;
}

/**
 * RoleToolAccessResponse
 * Schema for role-based tool access response.
 */
export interface RoleToolAccessResponse {
  /** User role */
  role: UserRole;
  /**
   * Tool Pattern
   * Tool name pattern
   */
  tool_pattern?: string | null;
  /**
   * Server Pattern
   * Server name pattern
   */
  server_pattern?: string | null;
  /** Access level */
  access_level: ToolAccessLevel;
  /** Default Rate Limit Per Hour */
  default_rate_limit_per_hour?: number | null;
  /** Default Rate Limit Per Day */
  default_rate_limit_per_day?: number | null;
  /** Allowed Hours */
  allowed_hours?: number[] | null;
  /** Allowed Days */
  allowed_days?: number[] | null;
  /**
   * Id
   * Access rule ID
   */
  id: string;
  /**
   * Created By
   * Creator user ID
   */
  created_by: string;
  /**
   * Created At
   * Creation timestamp
   * @format date-time
   */
  created_at: string;
}

/**
 * SSEStatsResponse
 * Response schema for SSE service statistics.
 */
export interface SSEStatsResponse {
  /**
   * Total Connections
   * Total active connections
   */
  total_connections: number;
  /**
   * Your Connections
   * Your active connections
   */
  your_connections: number;
}

/**
 * ServerToolResponse
 * Schema for server tool response.
 */
export interface ServerToolResponse {
  /**
   * Name
   * Tool name
   * @minLength 1
   * @maxLength 100
   */
  name: string;
  /**
   * Display Name
   * Display name
   * @minLength 1
   * @maxLength 200
   */
  display_name: string;
  /**
   * Description
   * Tool description
   */
  description?: string | null;
  /**
   * Args Schema
   * Tool arguments schema
   */
  args_schema?: Record<string, any> | null;
  /**
   * Bypass When Unavailable
   * Bypass when tool is unavailable
   * @default false
   */
  bypass_when_unavailable?: boolean;
  /**
   * Id
   * Tool ID
   */
  id: string;
  /**
   * Server Id
   * Server ID
   */
  server_id: string;
  /** Tool status */
  status: ToolStatus;
  /**
   * Is Available
   * Tool availability
   */
  is_available: boolean;
  /**
   * Total Calls
   * Total number of calls
   */
  total_calls: number;
  /**
   * Total Errors
   * Total number of errors
   */
  total_errors: number;
  /**
   * Last Called
   * Last call timestamp
   */
  last_called?: string | null;
  /**
   * Last Error
   * Last error message
   */
  last_error?: string | null;
  /**
   * Avg Response Time Ms
   * Average response time
   */
  avg_response_time_ms?: number | null;
  /**
   * Created At
   * Creation timestamp
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update timestamp
   * @format date-time
   */
  updated_at: string;
}

/**
 * ServerToolsResponse
 * Schema for server tools response with pagination.
 */
export interface ServerToolsResponse {
  /**
   * Tools
   * List of server tools
   */
  tools: ServerToolResponse[];
  /**
   * Total Count
   * Total number of tools
   */
  total_count: number;
  /**
   * Limit
   * Applied limit
   */
  limit: number;
  /**
   * Offset
   * Applied offset
   */
  offset: number;
}

/**
 * SortingRequest
 * Common sorting request schema.
 */
export interface SortingRequest {
  /**
   * Sort By
   * Sort field
   * @default "created_at"
   */
  sort_by?: string;
  /**
   * Sort Order
   * Sort order
   * @default "desc"
   * @pattern ^(asc|desc)$
   */
  sort_order?: string;
}

/**
 * StorageStatsResponse
 * Response schema for storage statistics.
 */
export interface StorageStatsResponse {
  /**
   * Total Size
   * Total storage used in bytes
   */
  total_size: number;
  /**
   * Database Size
   * Database size in bytes
   */
  database_size: number;
  /**
   * Files Size
   * Uploaded files size in bytes
   */
  files_size: number;
  /**
   * Backups Size
   * Backups size in bytes
   */
  backups_size: number;
  /**
   * Exports Size
   * Exports size in bytes
   */
  exports_size: number;
  /**
   * Total Records
   * Total number of records
   */
  total_records: number;
  /**
   * Total Files
   * Total number of files
   */
  total_files: number;
  /**
   * Total Backups
   * Total number of backups
   */
  total_backups: number;
  /**
   * Storage By Type
   * Storage usage by data type
   */
  storage_by_type: Record<string, number>;
  /**
   * Storage By User
   * Storage usage by user
   */
  storage_by_user: Record<string, number>;
  /**
   * Growth Rate Mb Per Day
   * Storage growth rate in MB per day
   */
  growth_rate_mb_per_day: number;
  /**
   * Projected Size 30 Days
   * Projected size in 30 days
   */
  projected_size_30_days: number;
  /**
   * Last Updated
   * Statistics last updated timestamp
   * @format date-time
   */
  last_updated: string;
}

/**
 * SystemAnalyticsResponse
 * Schema for system analytics response.
 */
export interface SystemAnalyticsResponse {
  /**
   * Total Users
   * Total number of users
   */
  total_users: number;
  /**
   * Active Users Today
   * Active users today
   */
  active_users_today: number;
  /**
   * Active Users Week
   * Active users this week
   */
  active_users_week: number;
  /**
   * Active Users Month
   * Active users this month
   */
  active_users_month: number;
  /**
   * System Uptime Seconds
   * System uptime in seconds
   */
  system_uptime_seconds: number;
  /**
   * Avg Cpu Usage
   * Average CPU usage percentage
   */
  avg_cpu_usage: number;
  /**
   * Avg Memory Usage
   * Average memory usage percentage
   */
  avg_memory_usage: number;
  /**
   * Database Connections
   * Current database connections
   */
  database_connections: number;
  /**
   * Total Api Requests
   * Total API requests
   */
  total_api_requests: number;
  /**
   * Requests Per Endpoint
   * Requests by endpoint
   */
  requests_per_endpoint: Record<string, number>;
  /**
   * Avg Api Response Time
   * Average API response time
   */
  avg_api_response_time: number;
  /**
   * Api Error Rate
   * API error rate
   */
  api_error_rate: number;
  /**
   * Storage Usage Bytes
   * Total storage usage
   */
  storage_usage_bytes: number;
  /**
   * Vector Database Size Bytes
   * Vector database size
   */
  vector_database_size_bytes: number;
  /**
   * Cache Hit Rate
   * Cache hit rate
   */
  cache_hit_rate: number;
}

/**
 * TestEventResponse
 * Response schema for test event.
 */
export interface TestEventResponse {
  /**
   * Message
   * Response message
   */
  message: string;
  /**
   * Event Id
   * Generated event ID
   */
  event_id: string;
}

/**
 * TestMetric
 * Test metric data.
 */
export interface TestMetric {
  /** Type of metric */
  metric_type: MetricType;
  /**
   * Variant Name
   * Variant name
   */
  variant_name: string;
  /**
   * Value
   * Metric value
   */
  value: number;
  /**
   * Sample Size
   * Sample size
   */
  sample_size: number;
  /**
   * Confidence Interval
   * 95% confidence interval
   */
  confidence_interval?: number[] | null;
}

/**
 * TestVariant
 * Test variant definition.
 */
export interface TestVariant {
  /**
   * Name
   * Variant name
   */
  name: string;
  /**
   * Description
   * Variant description
   */
  description: string;
  /**
   * Configuration
   * Variant configuration
   */
  configuration: Record<string, any>;
  /**
   * Weight
   * Variant weight for allocation
   * @min 0
   * @default 1
   */
  weight?: number;
}

/**
 * TokenRefresh
 * Schema for token refresh request.
 */
export interface TokenRefresh {
  /**
   * Refresh Token
   * Refresh token
   */
  refresh_token: string;
}

/**
 * TokenRefreshResponse
 * Schema for token refresh response.
 */
export interface TokenRefreshResponse {
  /**
   * Access Token
   * New access token
   */
  access_token: string;
  /**
   * Refresh Token
   * New refresh token
   */
  refresh_token: string;
  /**
   * Token Type
   * Token type
   * @default "bearer"
   */
  token_type?: string;
  /**
   * Expires In
   * Token expiration time in seconds
   */
  expires_in: number;
}

/**
 * TokenResponse
 * Schema for authentication token response.
 */
export interface TokenResponse {
  /**
   * Access Token
   * JWT access token
   */
  access_token: string;
  /**
   * Refresh Token
   * JWT refresh token
   */
  refresh_token: string;
  /**
   * Token Type
   * Token type
   * @default "bearer"
   */
  token_type?: string;
  /**
   * Expires In
   * Token expiration time in seconds
   */
  expires_in: number;
  /** User information */
  user: UserResponse;
}

/**
 * ToolAccessResult
 * Schema for tool access check result.
 */
export interface ToolAccessResult {
  /**
   * Allowed
   * Whether access is allowed
   */
  allowed: boolean;
  /** Access level */
  access_level: ToolAccessLevel;
  /**
   * Rate Limit Remaining Hour
   * Remaining hourly calls
   */
  rate_limit_remaining_hour?: number | null;
  /**
   * Rate Limit Remaining Day
   * Remaining daily calls
   */
  rate_limit_remaining_day?: number | null;
  /**
   * Restriction Reason
   * Reason if restricted
   */
  restriction_reason?: string | null;
  /**
   * Expires At
   * Permission expiry
   */
  expires_at?: string | null;
}

/**
 * ToolOperationResponse
 * Schema for tool operation response.
 */
export interface ToolOperationResponse {
  /**
   * Success
   * Operation success status
   */
  success: boolean;
  /**
   * Message
   * Operation result message
   */
  message: string;
}

/**
 * ToolPermissionCreate
 * Schema for creating tool permissions.
 */
export interface ToolPermissionCreate {
  /**
   * User Id
   * User ID
   */
  user_id: string;
  /**
   * Tool Id
   * Specific tool ID
   */
  tool_id?: string | null;
  /**
   * Server Id
   * Server ID (for all tools)
   */
  server_id?: string | null;
  /** Access level */
  access_level: ToolAccessLevel;
  /**
   * Rate Limit Per Hour
   * Hourly rate limit
   */
  rate_limit_per_hour?: number | null;
  /**
   * Rate Limit Per Day
   * Daily rate limit
   */
  rate_limit_per_day?: number | null;
  /**
   * Allowed Hours
   * Allowed hours (0-23)
   */
  allowed_hours?: number[] | null;
  /**
   * Allowed Days
   * Allowed weekdays (0-6)
   */
  allowed_days?: number[] | null;
  /**
   * Expires At
   * Permission expiry
   */
  expires_at?: string | null;
}

/**
 * ToolPermissionResponse
 * Schema for tool permission response.
 */
export interface ToolPermissionResponse {
  /**
   * User Id
   * User ID
   */
  user_id: string;
  /**
   * Tool Id
   * Specific tool ID
   */
  tool_id?: string | null;
  /**
   * Server Id
   * Server ID (for all tools)
   */
  server_id?: string | null;
  /** Access level */
  access_level: ToolAccessLevel;
  /**
   * Rate Limit Per Hour
   * Hourly rate limit
   */
  rate_limit_per_hour?: number | null;
  /**
   * Rate Limit Per Day
   * Daily rate limit
   */
  rate_limit_per_day?: number | null;
  /**
   * Allowed Hours
   * Allowed hours (0-23)
   */
  allowed_hours?: number[] | null;
  /**
   * Allowed Days
   * Allowed weekdays (0-6)
   */
  allowed_days?: number[] | null;
  /**
   * Expires At
   * Permission expiry
   */
  expires_at?: string | null;
  /**
   * Id
   * Permission ID
   */
  id: string;
  /**
   * Granted By
   * Granter user ID
   */
  granted_by: string;
  /**
   * Granted At
   * Grant timestamp
   * @format date-time
   */
  granted_at: string;
  /**
   * Usage Count
   * Usage count
   */
  usage_count: number;
  /**
   * Last Used
   * Last used timestamp
   */
  last_used?: string | null;
}

/**
 * ToolPermissionUpdate
 * Schema for updating tool permissions.
 */
export interface ToolPermissionUpdate {
  access_level?: ToolAccessLevel | null;
  /** Rate Limit Per Hour */
  rate_limit_per_hour?: number | null;
  /** Rate Limit Per Day */
  rate_limit_per_day?: number | null;
  /** Allowed Hours */
  allowed_hours?: number[] | null;
  /** Allowed Days */
  allowed_days?: number[] | null;
  /** Expires At */
  expires_at?: string | null;
}

/**
 * ToolServerCreate
 * Schema for creating a tool server.
 */
export interface ToolServerCreate {
  /**
   * Name
   * Server name
   * @minLength 1
   * @maxLength 100
   */
  name: string;
  /**
   * Display Name
   * Display name
   * @minLength 1
   * @maxLength 200
   */
  display_name: string;
  /**
   * Description
   * Server description
   */
  description?: string | null;
  /**
   * Base Url
   * Base URL for the remote server (null for built-in servers)
   */
  base_url?: string | null;
  /**
   * Transport Type
   * Transport type: http, sse, stdio, or websocket
   * @default "http"
   * @pattern ^(http|sse|stdio|websocket)$
   */
  transport_type?: string;
  /** OAuth configuration if required */
  oauth_config?: OAuthConfigSchema | null;
  /**
   * Headers
   * Additional HTTP headers
   */
  headers?: Record<string, string> | null;
  /**
   * Timeout
   * Request timeout in seconds
   * @min 5
   * @max 300
   * @default 30
   */
  timeout?: number;
  /**
   * Auto Start
   * Auto-connect to server on system startup
   * @default true
   */
  auto_start?: boolean;
  /**
   * Auto Update
   * Auto-update server capabilities
   * @default true
   */
  auto_update?: boolean;
  /**
   * Max Failures
   * Maximum consecutive failures before disabling
   * @min 1
   * @max 10
   * @default 3
   */
  max_failures?: number;
}

/**
 * ToolServerDeleteResponse
 * Schema for tool server delete response.
 */
export interface ToolServerDeleteResponse {
  /**
   * Message
   * Success message
   */
  message: string;
}

/**
 * ToolServerHealthCheck
 * Schema for tool server health check.
 */
export interface ToolServerHealthCheck {
  /**
   * Server Id
   * Server ID
   */
  server_id: string;
  /**
   * Server Name
   * Server name
   */
  server_name: string;
  /** Server status */
  status: ServerStatus;
  /**
   * Is Running
   * Whether server is running
   */
  is_running: boolean;
  /**
   * Is Responsive
   * Whether server is responsive
   */
  is_responsive: boolean;
  /**
   * Tools Count
   * Number of available tools
   */
  tools_count: number;
  /**
   * Last Check
   * Last health check time
   * @format date-time
   */
  last_check: string;
  /**
   * Error Message
   * Error message if unhealthy
   */
  error_message?: string | null;
}

/**
 * ToolServerMetrics
 * Schema for tool server metrics.
 */
export interface ToolServerMetrics {
  /**
   * Server Id
   * Server ID
   */
  server_id: string;
  /**
   * Server Name
   * Server name
   */
  server_name: string;
  /** Server status */
  status: ServerStatus;
  /**
   * Total Tools
   * Total number of tools
   */
  total_tools: number;
  /**
   * Enabled Tools
   * Number of enabled tools
   */
  enabled_tools: number;
  /**
   * Total Calls
   * Total tool calls
   */
  total_calls: number;
  /**
   * Total Errors
   * Total errors
   */
  total_errors: number;
  /**
   * Success Rate
   * Success rate
   * @min 0
   * @max 1
   */
  success_rate: number;
  /**
   * Avg Response Time Ms
   * Average response time
   */
  avg_response_time_ms?: number | null;
  /**
   * Last Activity
   * Last activity timestamp
   */
  last_activity?: string | null;
  /**
   * Uptime Percentage
   * Uptime percentage
   */
  uptime_percentage?: number | null;
}

/**
 * ToolServerOperationResponse
 * Schema for tool server operation response.
 */
export interface ToolServerOperationResponse {
  /**
   * Success
   * Operation success status
   */
  success: boolean;
  /**
   * Message
   * Operation result message
   */
  message: string;
}

/**
 * ToolServerResponse
 * Schema for tool server response.
 */
export interface ToolServerResponse {
  /**
   * Name
   * Server name
   * @minLength 1
   * @maxLength 100
   */
  name: string;
  /**
   * Display Name
   * Display name
   * @minLength 1
   * @maxLength 200
   */
  display_name: string;
  /**
   * Description
   * Server description
   */
  description?: string | null;
  /**
   * Base Url
   * Base URL for the remote server (null for built-in servers)
   */
  base_url?: string | null;
  /**
   * Transport Type
   * Transport type: http, sse, stdio, or websocket
   * @default "http"
   * @pattern ^(http|sse|stdio|websocket)$
   */
  transport_type?: string;
  /** OAuth configuration if required */
  oauth_config?: OAuthConfigSchema | null;
  /**
   * Headers
   * Additional HTTP headers
   */
  headers?: Record<string, string> | null;
  /**
   * Timeout
   * Request timeout in seconds
   * @min 5
   * @max 300
   * @default 30
   */
  timeout?: number;
  /**
   * Auto Start
   * Auto-connect to server on system startup
   * @default true
   */
  auto_start?: boolean;
  /**
   * Auto Update
   * Auto-update server capabilities
   * @default true
   */
  auto_update?: boolean;
  /**
   * Max Failures
   * Maximum consecutive failures before disabling
   * @min 1
   * @max 10
   * @default 3
   */
  max_failures?: number;
  /**
   * Id
   * Server ID
   */
  id: string;
  /** Server status */
  status: ServerStatus;
  /**
   * Is Builtin
   * Whether server is built-in
   */
  is_builtin: boolean;
  /**
   * Last Health Check
   * Last health check
   */
  last_health_check?: string | null;
  /**
   * Last Startup Success
   * Last successful startup
   */
  last_startup_success?: string | null;
  /**
   * Last Startup Error
   * Last startup error
   */
  last_startup_error?: string | null;
  /**
   * Consecutive Failures
   * Consecutive failure count
   */
  consecutive_failures: number;
  /**
   * Created At
   * Creation timestamp
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update timestamp
   * @format date-time
   */
  updated_at: string;
  /**
   * Created By
   * Creator user ID
   */
  created_by?: string | null;
  /**
   * Tools
   * Server tools
   */
  tools?: ServerToolResponse[];
}

/**
 * ToolServerUpdate
 * Schema for updating a remote tool server.
 */
export interface ToolServerUpdate {
  /** Display Name */
  display_name?: string | null;
  /** Description */
  description?: string | null;
  /** Base Url */
  base_url?: string | null;
  /** Transport Type */
  transport_type?: string | null;
  oauth_config?: OAuthConfigSchema | null;
  /** Headers */
  headers?: Record<string, string> | null;
  /** Timeout */
  timeout?: number | null;
  /** Auto Start */
  auto_start?: boolean | null;
  /** Auto Update */
  auto_update?: boolean | null;
  /** Max Failures */
  max_failures?: number | null;
}

/**
 * UsageMetricsResponse
 * Schema for usage metrics response.
 */
export interface UsageMetricsResponse {
  /**
   * Total Prompt Tokens
   * Total prompt tokens
   */
  total_prompt_tokens: number;
  /**
   * Total Completion Tokens
   * Total completion tokens
   */
  total_completion_tokens: number;
  /**
   * Total Tokens
   * Total tokens used
   */
  total_tokens: number;
  /**
   * Tokens By Model
   * Token usage by model
   */
  tokens_by_model: Record<string, number>;
  /**
   * Tokens By Provider
   * Token usage by provider
   */
  tokens_by_provider: Record<string, number>;
  /**
   * Total Cost
   * Total cost
   */
  total_cost: number;
  /**
   * Cost By Model
   * Cost by model
   */
  cost_by_model: Record<string, number>;
  /**
   * Cost By Provider
   * Cost by provider
   */
  cost_by_provider: Record<string, number>;
  /**
   * Daily Usage
   * Daily token usage
   */
  daily_usage: Record<string, number>;
  /**
   * Daily Cost
   * Daily cost
   */
  daily_cost: Record<string, number>;
  /**
   * Avg Response Time
   * Average response time
   */
  avg_response_time: number;
  /**
   * Response Times By Model
   * Response times by model
   */
  response_times_by_model: Record<string, number>;
  /**
   * Active Days
   * Number of active days
   */
  active_days: number;
  /**
   * Peak Usage Hour
   * Peak usage hour
   */
  peak_usage_hour: number;
  /**
   * Conversations Per Day
   * Average conversations per day
   */
  conversations_per_day: number;
}

/**
 * UserCreate
 * Schema for user creation (alias for UserRegistration).
 */
export interface UserCreate {
  /**
   * Email
   * User email address
   * @format email
   */
  email: string;
  /**
   * Username
   * Username
   * @minLength 3
   * @maxLength 50
   */
  username: string;
  /**
   * Full Name
   * Full name
   */
  full_name?: string | null;
  /**
   * Bio
   * User bio
   */
  bio?: string | null;
  /**
   * Avatar Url
   * Avatar URL
   */
  avatar_url?: string | null;
  /**
   * Phone Number
   * Phone number
   */
  phone_number?: string | null;
  /**
   * Password
   * Password
   * @minLength 8
   * @maxLength 128
   */
  password: string;
}

/**
 * UserLogin
 * Schema for user login.
 */
export interface UserLogin {
  /**
   * Email
   * User email address
   */
  email?: string | null;
  /**
   * Username
   * Username
   */
  username?: string | null;
  /**
   * Password
   * Password
   */
  password: string;
  /**
   * Remember Me
   * Remember login
   * @default false
   */
  remember_me?: boolean;
}

/**
 * UserResponse
 * Schema for user response.
 */
export interface UserResponse {
  /**
   * Email
   * User email address
   * @format email
   */
  email: string;
  /**
   * Username
   * Username
   * @minLength 3
   * @maxLength 50
   */
  username: string;
  /**
   * Full Name
   * Full name
   */
  full_name?: string | null;
  /**
   * Bio
   * User bio
   */
  bio?: string | null;
  /**
   * Avatar Url
   * Avatar URL
   */
  avatar_url?: string | null;
  /**
   * Phone Number
   * Phone number
   */
  phone_number?: string | null;
  /**
   * Id
   * User ID
   */
  id: string;
  /**
   * Is Active
   * Is user active
   */
  is_active: boolean;
  /**
   * Is Verified
   * Is user email verified
   */
  is_verified: boolean;
  /**
   * Is Superuser
   * Is user a superuser
   */
  is_superuser: boolean;
  /**
   * Default Llm Provider
   * Default LLM provider
   */
  default_llm_provider?: string | null;
  /**
   * Default Profile Id
   * Default profile ID
   */
  default_profile_id?: string | null;
  /**
   * Daily Message Limit
   * Daily message limit
   */
  daily_message_limit?: number | null;
  /**
   * Monthly Message Limit
   * Monthly message limit
   */
  monthly_message_limit?: number | null;
  /**
   * Max File Size Mb
   * Max file size in MB
   */
  max_file_size_mb?: number | null;
  /**
   * Api Key Name
   * API key name
   */
  api_key_name?: string | null;
  /**
   * Created At
   * Account creation date
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * Last update date
   * @format date-time
   */
  updated_at: string;
  /**
   * Last Login At
   * Last login date
   */
  last_login_at?: string | null;
}

/**
 * UserToolAccessCheck
 * Schema for checking user tool access.
 */
export interface UserToolAccessCheck {
  /**
   * User Id
   * User ID
   */
  user_id: string;
  /**
   * Tool Name
   * Tool name
   */
  tool_name: string;
  /**
   * Server Name
   * Server name
   */
  server_name?: string | null;
}

/**
 * UserUpdate
 * Schema for user profile updates.
 */
export interface UserUpdate {
  /**
   * Email
   * User email address
   */
  email?: string | null;
  /**
   * Full Name
   * Full name
   */
  full_name?: string | null;
  /**
   * Bio
   * User bio
   */
  bio?: string | null;
  /**
   * Avatar Url
   * Avatar URL
   */
  avatar_url?: string | null;
  /**
   * Phone Number
   * Phone number
   */
  phone_number?: string | null;
  /**
   * Default Llm Provider
   * Default LLM provider
   */
  default_llm_provider?: string | null;
  /**
   * Default Profile Id
   * Default profile ID
   */
  default_profile_id?: string | null;
}

/** ValidationError */
export interface ValidationError {
  /** Location */
  loc: (string | number)[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
}

/**
 * WorkflowAnalyticsResponse
 * Schema for workflow analytics response.
 */
export interface WorkflowAnalyticsResponse {
  /** Complexity metrics */
  complexity: ComplexityMetrics;
  /**
   * Bottlenecks
   * Identified bottlenecks
   */
  bottlenecks: BottleneckInfo[];
  /**
   * Optimization Suggestions
   * Optimization suggestions
   */
  optimization_suggestions: OptimizationSuggestion[];
  /**
   * Execution Paths
   * Number of possible execution paths
   */
  execution_paths: number;
  /**
   * Estimated Execution Time Ms
   * Estimated execution time
   */
  estimated_execution_time_ms?: number | null;
  /**
   * Risk Factors
   * Identified risk factors
   */
  risk_factors: string[];
  /**
   * Total Execution Time Ms
   * Total execution time
   */
  total_execution_time_ms: number;
  /**
   * Error
   * Error message if failed
   */
  error?: string | null;
  /**
   * Started At
   * Execution start time
   * @format date-time
   */
  started_at: string;
  /**
   * Completed At
   * Execution completion time
   */
  completed_at?: string | null;
}

/**
 * WorkflowDefinitionCreate
 * Schema for creating a workflow definition.
 */
export interface WorkflowDefinitionCreate {
  /**
   * Name
   * Workflow name
   * @minLength 1
   * @maxLength 255
   */
  name: string;
  /**
   * Description
   * Workflow description
   */
  description?: string | null;
  /**
   * Nodes
   * Workflow nodes
   */
  nodes: WorkflowNode[];
  /**
   * Edges
   * Workflow edges
   */
  edges: WorkflowEdge[];
  /**
   * Metadata
   * Additional metadata
   */
  metadata?: Record<string, any> | null;
  /**
   * Is Public
   * Whether workflow is publicly visible
   * @default false
   */
  is_public?: boolean;
  /**
   * Tags
   * Workflow tags
   */
  tags?: string[] | null;
  /**
   * Template Id
   * Source template ID if created from template
   */
  template_id?: string | null;
}

/**
 * WorkflowDefinitionResponse
 * Schema for workflow definition response.
 */
export interface WorkflowDefinitionResponse {
  /**
   * Name
   * Workflow name
   * @minLength 1
   * @maxLength 255
   */
  name: string;
  /**
   * Description
   * Workflow description
   */
  description?: string | null;
  /**
   * Nodes
   * Workflow nodes
   */
  nodes: WorkflowNode[];
  /**
   * Edges
   * Workflow edges
   */
  edges: WorkflowEdge[];
  /**
   * Metadata
   * Additional metadata
   */
  metadata?: Record<string, any> | null;
  /**
   * Is Public
   * Whether workflow is public
   * @default false
   */
  is_public?: boolean;
  /**
   * Tags
   * Workflow tags
   */
  tags?: string[] | null;
  /**
   * Template Id
   * Source template ID if created from template
   */
  template_id?: string | null;
  /**
   * Id
   * Unique node identifier
   */
  id: string;
  /**
   * Owner Id
   * Owner user ID
   */
  owner_id: string;
  /**
   * Version
   * Workflow version
   * @default 1
   */
  version?: number;
}

/**
 * WorkflowDefinitionUpdate
 * Schema for updating a workflow definition.
 */
export interface WorkflowDefinitionUpdate {
  /**
   * Name
   * Workflow name
   */
  name?: string | null;
  /**
   * Description
   * Workflow description
   */
  description?: string | null;
  /**
   * Nodes
   * Workflow nodes
   */
  nodes?: WorkflowNode[] | null;
  /**
   * Edges
   * Workflow edges
   */
  edges?: WorkflowEdge[] | null;
  /**
   * Metadata
   * Additional metadata
   */
  metadata?: Record<string, any> | null;
}

/**
 * WorkflowDefinitionsResponse
 * Schema for workflow definitions list response.
 */
export interface WorkflowDefinitionsResponse {
  /**
   * Definitions
   * Workflow definitions
   */
  definitions: WorkflowDefinitionResponse[];
  /**
   * Total Count
   * Total number of definitions
   */
  total_count: number;
}

/**
 * WorkflowEdge
 * Schema for a workflow edge.
 */
export interface WorkflowEdge {
  /**
   * Id
   * Unique edge identifier
   */
  id: string;
  /**
   * Source
   * Source node ID
   */
  source: string;
  /**
   * Target
   * Target node ID
   */
  target: string;
  /**
   * Sourcehandle
   * Source handle ID
   */
  sourceHandle?: string | null;
  /**
   * Targethandle
   * Target handle ID
   */
  targetHandle?: string | null;
  /**
   * Type
   * Edge type
   * @default "default"
   */
  type?: string | null;
  /** Edge data */
  data?: WorkflowEdgeData | null;
}

/**
 * WorkflowEdgeData
 * Schema for workflow edge data.
 */
export interface WorkflowEdgeData {
  /**
   * Condition
   * Edge condition
   */
  condition?: string | null;
  /**
   * Label
   * Edge label
   */
  label?: string | null;
}

/**
 * WorkflowExecutionRequest
 * Schema for starting a workflow execution.
 */
export interface WorkflowExecutionRequest {
  /**
   * Input Data
   * Execution input data
   */
  input_data?: Record<string, any> | null;
  /**
   * Definition Id
   * Workflow definition ID
   */
  definition_id: string;
}

/**
 * WorkflowExecutionResponse
 * Schema for workflow execution response.
 */
export interface WorkflowExecutionResponse {
  /**
   * Input Data
   * Execution input data
   */
  input_data?: Record<string, any> | null;
  /**
   * Id
   * Execution ID
   */
  id: string;
  /**
   * Definition Id
   * Workflow definition ID
   */
  definition_id: string;
  /**
   * Owner Id
   * Owner user ID
   */
  owner_id: string;
  /**
   * Status
   * Execution status
   */
  status: string;
  /**
   * Started At
   * Execution start time
   */
  started_at?: string | null;
  /**
   * Completed At
   * Execution completion time
   */
  completed_at?: string | null;
  /**
   * Execution Time Ms
   * Execution time in milliseconds
   */
  execution_time_ms?: number | null;
  /**
   * Output Data
   * Execution output data
   */
  output_data?: Record<string, any> | null;
  /**
   * Error Message
   * Error message if failed
   */
  error_message?: string | null;
  /**
   * Tokens Used
   * Total tokens used
   * @default 0
   */
  tokens_used?: number;
  /**
   * Cost
   * Total cost
   * @default 0
   */
  cost?: number;
  /**
   * Created At
   * Creation timestamp
   */
  created_at?: string | null;
  /**
   * Updated At
   * Last update timestamp
   */
  updated_at?: string | null;
}

/**
 * WorkflowNode
 * Schema for a workflow node.
 */
export interface WorkflowNode {
  /**
   * Id
   * Unique node identifier
   */
  id: string;
  /**
   * Type
   * Node type
   */
  type: string;
  /**
   * Position
   * Node position (x, y)
   */
  position: Record<string, number>;
  /** Node data */
  data: WorkflowNodeData;
  /**
   * Selected
   * Whether node is selected
   * @default false
   */
  selected?: boolean | null;
  /**
   * Dragging
   * Whether node is being dragged
   * @default false
   */
  dragging?: boolean | null;
}

/**
 * WorkflowNodeData
 * Schema for workflow node data.
 */
export interface WorkflowNodeData {
  /**
   * Label
   * Node display label
   */
  label: string;
  /**
   * Nodetype
   * Type of the node
   */
  nodeType: string;
  /**
   * Config
   * Node configuration
   */
  config?: Record<string, any> | null;
}

/**
 * WorkflowTemplateCreate
 * Schema for creating a workflow template.
 */
export interface WorkflowTemplateCreate {
  /**
   * Name
   * Template name
   * @minLength 1
   * @maxLength 255
   */
  name: string;
  /**
   * Description
   * Template description
   */
  description: string;
  /**
   * Workflow Type
   * Workflow type
   */
  workflow_type: string;
  /**
   * Category
   * Template category
   * @default "custom"
   */
  category?: string;
  /**
   * Default Params
   * Default parameters
   */
  default_params?: Record<string, any>;
  /**
   * Required Tools
   * Required tools
   */
  required_tools?: string[] | null;
  /**
   * Required Retrievers
   * Required retrievers
   */
  required_retrievers?: string[] | null;
  /**
   * Tags
   * Template tags
   */
  tags?: string[] | null;
  /**
   * Is Public
   * Whether template is public
   * @default false
   */
  is_public?: boolean;
  /**
   * Workflow Definition Id
   * Source workflow definition ID
   */
  workflow_definition_id?: string | null;
  /**
   * Base Template Id
   * Base template ID for derivation
   */
  base_template_id?: string | null;
}

/**
 * WorkflowTemplateInfo
 * Schema for workflow template information.
 */
export interface WorkflowTemplateInfo {
  /**
   * Name
   * Template name
   */
  name: string;
  /**
   * Workflow Type
   * Workflow type
   */
  workflow_type: string;
  /**
   * Description
   * Template description
   */
  description: string;
  /**
   * Required Tools
   * Required tools
   */
  required_tools: string[];
  /**
   * Required Retrievers
   * Required retrievers
   */
  required_retrievers: string[];
  /**
   * Default Params
   * Default parameters
   */
  default_params: Record<string, any>;
}

/**
 * WorkflowTemplateResponse
 * Schema for workflow template response.
 */
export interface WorkflowTemplateResponse {
  /**
   * Name
   * Template name
   * @minLength 1
   * @maxLength 255
   */
  name: string;
  /**
   * Description
   * Template description
   */
  description: string;
  /**
   * Workflow Type
   * Workflow type
   */
  workflow_type: string;
  /**
   * Category
   * Template category
   * @default "custom"
   */
  category?: string;
  /**
   * Default Params
   * Default parameters
   */
  default_params?: Record<string, any>;
  /**
   * Required Tools
   * Required tools
   */
  required_tools?: string[] | null;
  /**
   * Required Retrievers
   * Required retrievers
   */
  required_retrievers?: string[] | null;
  /**
   * Tags
   * Template tags
   */
  tags?: string[] | null;
  /**
   * Is Public
   * Whether template is public
   * @default false
   */
  is_public?: boolean;
  /**
   * Id
   * Unique node identifier
   */
  id: string;
  /**
   * Owner Id
   * Owner user ID
   */
  owner_id: string;
  /**
   * Base Template Id
   * Base template ID
   */
  base_template_id?: string | null;
  /**
   * Is Builtin
   * Whether template is built-in
   * @default false
   */
  is_builtin?: boolean;
  /**
   * Version
   * Template version
   * @default 1
   */
  version?: number;
  /**
   * Is Latest
   * Whether this is the latest version
   * @default true
   */
  is_latest?: boolean;
  /**
   * Rating
   * Average rating
   */
  rating?: number | null;
  /**
   * Rating Count
   * Number of ratings
   * @default 0
   */
  rating_count?: number;
  /**
   * Usage Count
   * Usage count
   * @default 0
   */
  usage_count?: number;
  /**
   * Success Rate
   * Success rate
   */
  success_rate?: number | null;
  /**
   * Config Hash
   * Configuration hash
   */
  config_hash: string;
  /**
   * Estimated Complexity
   * Estimated complexity score
   */
  estimated_complexity?: number | null;
}

/**
 * WorkflowTemplateUpdate
 * Schema for updating a workflow template.
 */
export interface WorkflowTemplateUpdate {
  /**
   * Name
   * Template name
   */
  name?: string | null;
  /**
   * Description
   * Template description
   */
  description?: string | null;
  /**
   * Category
   * Template category
   */
  category?: string | null;
  /**
   * Default Params
   * Default parameters
   */
  default_params?: Record<string, any> | null;
  /**
   * Required Tools
   * Required tools
   */
  required_tools?: string[] | null;
  /**
   * Required Retrievers
   * Required retrievers
   */
  required_retrievers?: string[] | null;
  /**
   * Tags
   * Template tags
   */
  tags?: string[] | null;
  /**
   * Is Public
   * Whether template is public
   */
  is_public?: boolean | null;
}

/**
 * WorkflowValidationResponse
 * Schema for workflow validation response.
 */
export interface WorkflowValidationResponse {
  /**
   * Is Valid
   * Whether workflow is valid
   */
  is_valid: boolean;
  /**
   * Errors
   * Validation errors
   */
  errors: ValidationError[];
  /**
   * Warnings
   * Validation warnings
   */
  warnings: ValidationError[];
  /**
   * Suggestions
   * Validation suggestions
   */
  suggestions: string[];
}

/**
 * WorkflowTemplatesResponse
 * Schema for workflow templates response.
 */
export interface ChatterSchemasChatWorkflowTemplatesResponse {
  /**
   * Templates
   * Available templates
   */
  templates: Record<string, WorkflowTemplateInfo>;
  /**
   * Total Count
   * Total number of templates
   */
  total_count: number;
}

/**
 * WorkflowTemplatesResponse
 * Schema for workflow templates list response.
 */
export interface ChatterSchemasWorkflowsWorkflowTemplatesResponse {
  /**
   * Templates
   * Workflow templates
   */
  templates: WorkflowTemplateResponse[];
  /**
   * Total Count
   * Total number of templates
   */
  total_count: number;
}

export type HealthCheckEndpointHealthzGetData = HealthCheckResponse;

export type ReadinessCheckReadyzGetData = ReadinessCheckResponse;

export type LivenessCheckLiveGetData = HealthCheckResponse;

export type GetMetricsMetricsGetData = MetricsResponse;

export interface GetCorrelationTraceTraceCorrelationIdGetParams {
  /** Correlation Id */
  correlationId: string;
}

export type GetCorrelationTraceTraceCorrelationIdGetData =
  CorrelationTraceResponse;

export type RegisterApiV1AuthRegisterPostData = TokenResponse;

export type LoginApiV1AuthLoginPostData = TokenResponse;

export type RefreshTokenApiV1AuthRefreshPostData = TokenRefreshResponse;

export type GetCurrentUserInfoApiV1AuthMeGetData = UserResponse;

export type UpdateProfileApiV1AuthMePutData = UserResponse;

export type ChangePasswordApiV1AuthChangePasswordPostData =
  PasswordChangeResponse;

export type CreateApiKeyApiV1AuthApiKeyPostData = APIKeyResponse;

export type RevokeApiKeyApiV1AuthApiKeyDeleteData = APIKeyRevokeResponse;

/** Response List Api Keys Api V1 Auth Api Keys Get */
export type ListApiKeysApiV1AuthApiKeysGetData = APIKeyResponse[];

export type LogoutApiV1AuthLogoutPostData = LogoutResponse;

export interface RequestPasswordResetApiV1AuthPasswordResetRequestPostParams {
  /** Email */
  email: string;
}

export type RequestPasswordResetApiV1AuthPasswordResetRequestPostData =
  PasswordResetRequestResponse;

export interface ConfirmPasswordResetApiV1AuthPasswordResetConfirmPostParams {
  /** Token */
  token: string;
  /** New Password */
  new_password: string;
}

export type ConfirmPasswordResetApiV1AuthPasswordResetConfirmPostData =
  PasswordResetConfirmResponse;

export type DeactivateAccountApiV1AuthAccountDeleteData =
  AccountDeactivateResponse;

export type CreateConversationApiV1ChatConversationsPostData =
  ConversationResponse;

export interface ListConversationsApiV1ChatConversationsGetParams {
  /**
   * Limit
   * Number of results per page
   * @min 1
   * @max 100
   * @default 20
   */
  limit?: number;
  /**
   * Offset
   * Number of results to skip
   * @min 0
   * @default 0
   */
  offset?: number;
}

export type ListConversationsApiV1ChatConversationsGetData =
  ConversationSearchResponse;

export interface GetConversationApiV1ChatConversationsConversationIdGetParams {
  /**
   * Include Messages
   * Include messages in response
   * @default true
   */
  include_messages?: boolean;
  /**
   * Conversation Id
   * Conversation ID
   * @minLength 1
   */
  conversationId: string;
}

export type GetConversationApiV1ChatConversationsConversationIdGetData =
  ConversationWithMessages;

export interface UpdateConversationApiV1ChatConversationsConversationIdPutParams {
  /**
   * Conversation Id
   * Conversation ID
   * @minLength 1
   */
  conversationId: string;
}

export type UpdateConversationApiV1ChatConversationsConversationIdPutData =
  ConversationResponse;

export interface DeleteConversationApiV1ChatConversationsConversationIdDeleteParams {
  /**
   * Conversation Id
   * Conversation ID
   * @minLength 1
   */
  conversationId: string;
}

export type DeleteConversationApiV1ChatConversationsConversationIdDeleteData =
  ConversationDeleteResponse;

export interface GetConversationMessagesApiV1ChatConversationsConversationIdMessagesGetParams {
  /**
   * Limit
   * Number of results per page
   * @min 1
   * @max 100
   * @default 50
   */
  limit?: number;
  /**
   * Offset
   * Number of results to skip
   * @min 0
   * @default 0
   */
  offset?: number;
  /**
   * Conversation Id
   * Conversation ID
   * @minLength 1
   */
  conversationId: string;
}

/** Response Get Conversation Messages Api V1 Chat Conversations  Conversation Id  Messages Get */
export type GetConversationMessagesApiV1ChatConversationsConversationIdMessagesGetData =
  MessageResponse[];

export interface DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteParams {
  /**
   * Conversation Id
   * Conversation ID
   * @minLength 1
   */
  conversationId: string;
  /**
   * Message Id
   * Message ID
   * @minLength 1
   */
  messageId: string;
}

export type DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteData =
  MessageDeleteResponse;

/**
 * ChatResponse
 * Schema for chat response.
 */
export interface ChatApiV1ChatChatPostData {
  /**
   * Conversation Id
   * Conversation ID
   */
  conversation_id: string;
  /** Assistant response message */
  message: MessageResponse;
  /** Updated conversation */
  conversation: ConversationResponse;
}

export type GetAvailableToolsApiV1ChatToolsAvailableGetData =
  AvailableToolsResponse;

export type GetWorkflowTemplatesApiV1ChatTemplatesGetData =
  ChatterSchemasChatWorkflowTemplatesResponse;

export interface ChatWithTemplateApiV1ChatTemplateTemplateNamePostParams {
  /** Template Name */
  templateName: string;
}

export type ChatWithTemplateApiV1ChatTemplateTemplateNamePostData =
  ChatResponse;

export type GetPerformanceStatsApiV1ChatPerformanceStatsGetData =
  PerformanceStatsResponse;

export type GetMcpStatusApiV1ChatMcpStatusGetData = McpStatusResponse;

export type UploadDocumentApiV1DocumentsUploadPostData = DocumentResponse;

export interface ListDocumentsApiV1DocumentsGetParams {
  /**
   * Status
   * Filter by status
   */
  status?: DocumentStatus | null;
  /**
   * Document Type
   * Filter by document type
   */
  document_type?: DocumentType | null;
  /**
   * Tags
   * Filter by tags
   */
  tags?: string[] | null;
  /**
   * Owner Id
   * Filter by owner (admin only)
   */
  owner_id?: string | null;
  /**
   * Limit
   * Maximum number of results
   * @min 1
   * @max 100
   * @default 50
   */
  limit?: number;
  /**
   * Offset
   * Number of results to skip
   * @min 0
   * @default 0
   */
  offset?: number;
  /**
   * Sort By
   * Sort field
   * @default "created_at"
   */
  sort_by?: string;
  /**
   * Sort Order
   * Sort order
   * @default "desc"
   * @pattern ^(asc|desc)$
   */
  sort_order?: string;
}

export type ListDocumentsApiV1DocumentsGetData = DocumentListResponse;

export interface GetDocumentApiV1DocumentsDocumentIdGetParams {
  /** Document Id */
  documentId: string;
}

export type GetDocumentApiV1DocumentsDocumentIdGetData = DocumentResponse;

export interface UpdateDocumentApiV1DocumentsDocumentIdPutParams {
  /** Document Id */
  documentId: string;
}

export type UpdateDocumentApiV1DocumentsDocumentIdPutData = DocumentResponse;

export interface DeleteDocumentApiV1DocumentsDocumentIdDeleteParams {
  /** Document Id */
  documentId: string;
}

export type DeleteDocumentApiV1DocumentsDocumentIdDeleteData =
  DocumentDeleteResponse;

export type SearchDocumentsApiV1DocumentsSearchPostData =
  DocumentSearchResponse;

export interface GetDocumentChunksApiV1DocumentsDocumentIdChunksGetParams {
  /**
   * Limit
   * Maximum number of results
   * @min 1
   * @max 100
   * @default 50
   */
  limit?: number;
  /**
   * Offset
   * Number of results to skip
   * @min 0
   * @default 0
   */
  offset?: number;
  /** Document Id */
  documentId: string;
}

export type GetDocumentChunksApiV1DocumentsDocumentIdChunksGetData =
  DocumentChunksResponse;

export interface ProcessDocumentApiV1DocumentsDocumentIdProcessPostParams {
  /** Document Id */
  documentId: string;
}

export type ProcessDocumentApiV1DocumentsDocumentIdProcessPostData =
  DocumentProcessingResponse;

export type GetDocumentStatsApiV1DocumentsStatsOverviewGetData =
  DocumentStatsResponse;

export interface DownloadDocumentApiV1DocumentsDocumentIdDownloadGetParams {
  /** Document Id */
  documentId: string;
}

export type DownloadDocumentApiV1DocumentsDocumentIdDownloadGetData = any;

export interface ReprocessDocumentApiV1DocumentsDocumentIdReprocessPostParams {
  /** Document Id */
  documentId: string;
}

export type ReprocessDocumentApiV1DocumentsDocumentIdReprocessPostData =
  DocumentProcessingResponse;

export type CreateProfileApiV1ProfilesPostData = ProfileResponse;

export interface ListProfilesApiV1ProfilesGetParams {
  /**
   * Profile Type
   * Filter by profile type
   */
  profile_type?: ProfileType | null;
  /**
   * Llm Provider
   * Filter by LLM provider
   */
  llm_provider?: string | null;
  /**
   * Tags
   * Filter by tags
   */
  tags?: string[] | null;
  /**
   * Is Public
   * Filter by public status
   */
  is_public?: boolean | null;
  /**
   * Limit
   * Maximum number of results
   * @min 1
   * @max 100
   * @default 50
   */
  limit?: number;
  /**
   * Offset
   * Number of results to skip
   * @min 0
   * @default 0
   */
  offset?: number;
  /**
   * Sort By
   * Sort field
   * @default "created_at"
   */
  sort_by?: string;
  /**
   * Sort Order
   * Sort order
   * @default "desc"
   * @pattern ^(asc|desc)$
   */
  sort_order?: string;
}

export type ListProfilesApiV1ProfilesGetData = ProfileListResponse;

export interface GetProfileApiV1ProfilesProfileIdGetParams {
  /** Profile Id */
  profileId: string;
}

export type GetProfileApiV1ProfilesProfileIdGetData = ProfileResponse;

export interface UpdateProfileApiV1ProfilesProfileIdPutParams {
  /** Profile Id */
  profileId: string;
}

export type UpdateProfileApiV1ProfilesProfileIdPutData = ProfileResponse;

export interface DeleteProfileApiV1ProfilesProfileIdDeleteParams {
  /** Profile Id */
  profileId: string;
}

export type DeleteProfileApiV1ProfilesProfileIdDeleteData =
  ProfileDeleteResponse;

export interface TestProfileApiV1ProfilesProfileIdTestPostParams {
  /** Profile Id */
  profileId: string;
}

export type TestProfileApiV1ProfilesProfileIdTestPostData = ProfileTestResponse;

export interface CloneProfileApiV1ProfilesProfileIdClonePostParams {
  /** Profile Id */
  profileId: string;
}

export type CloneProfileApiV1ProfilesProfileIdClonePostData = ProfileResponse;

export type GetProfileStatsApiV1ProfilesStatsOverviewGetData =
  ProfileStatsResponse;

export type GetAvailableProvidersApiV1ProfilesProvidersAvailableGetData =
  AvailableProvidersResponse;

export type CreatePromptApiV1PromptsPostData = PromptResponse;

export type GetPromptStatsApiV1PromptsStatsOverviewGetData =
  PromptStatsResponse;

export interface ListPromptsApiV1PromptsGetParams {
  /**
   * Prompt Type
   * Filter by prompt type
   */
  prompt_type?: PromptType | null;
  /**
   * Category
   * Filter by category
   */
  category?: PromptCategory | null;
  /**
   * Tags
   * Filter by tags
   */
  tags?: string[] | null;
  /**
   * Is Public
   * Filter by public status
   */
  is_public?: boolean | null;
  /**
   * Is Chain
   * Filter by chain status
   */
  is_chain?: boolean | null;
  /**
   * Limit
   * Maximum number of results
   * @min 1
   * @max 100
   * @default 50
   */
  limit?: number;
  /**
   * Offset
   * Number of results to skip
   * @min 0
   * @default 0
   */
  offset?: number;
  /**
   * Sort By
   * Sort field
   * @default "created_at"
   */
  sort_by?: string;
  /**
   * Sort Order
   * Sort order
   * @default "desc"
   * @pattern ^(asc|desc)$
   */
  sort_order?: string;
}

export type ListPromptsApiV1PromptsGetData = PromptListResponse;

export interface GetPromptApiV1PromptsPromptIdGetParams {
  /** Prompt Id */
  promptId: string;
}

export type GetPromptApiV1PromptsPromptIdGetData = PromptResponse;

export interface UpdatePromptApiV1PromptsPromptIdPutParams {
  /** Prompt Id */
  promptId: string;
}

export type UpdatePromptApiV1PromptsPromptIdPutData = PromptResponse;

export interface DeletePromptApiV1PromptsPromptIdDeleteParams {
  /** Prompt Id */
  promptId: string;
}

export type DeletePromptApiV1PromptsPromptIdDeleteData = PromptDeleteResponse;

export interface TestPromptApiV1PromptsPromptIdTestPostParams {
  /** Prompt Id */
  promptId: string;
}

export type TestPromptApiV1PromptsPromptIdTestPostData = PromptTestResponse;

export interface ClonePromptApiV1PromptsPromptIdClonePostParams {
  /** Prompt Id */
  promptId: string;
}

export type ClonePromptApiV1PromptsPromptIdClonePostData = PromptResponse;

export interface GetConversationStatsApiV1AnalyticsConversationsGetParams {
  /**
   * Start Date
   * Start date for analytics
   */
  start_date?: string | null;
  /**
   * End Date
   * End date for analytics
   */
  end_date?: string | null;
  /**
   * Period
   * Predefined period (1h, 24h, 7d, 30d, 90d)
   * @default "7d"
   */
  period?: string;
}

export type GetConversationStatsApiV1AnalyticsConversationsGetData =
  ConversationStatsResponse;

export interface GetUsageMetricsApiV1AnalyticsUsageGetParams {
  /**
   * Start Date
   * Start date for analytics
   */
  start_date?: string | null;
  /**
   * End Date
   * End date for analytics
   */
  end_date?: string | null;
  /**
   * Period
   * Predefined period (1h, 24h, 7d, 30d, 90d)
   * @default "7d"
   */
  period?: string;
}

export type GetUsageMetricsApiV1AnalyticsUsageGetData = UsageMetricsResponse;

export interface GetPerformanceMetricsApiV1AnalyticsPerformanceGetParams {
  /**
   * Start Date
   * Start date for analytics
   */
  start_date?: string | null;
  /**
   * End Date
   * End date for analytics
   */
  end_date?: string | null;
  /**
   * Period
   * Predefined period (1h, 24h, 7d, 30d, 90d)
   * @default "7d"
   */
  period?: string;
}

export type GetPerformanceMetricsApiV1AnalyticsPerformanceGetData =
  PerformanceMetricsResponse;

export interface GetDocumentAnalyticsApiV1AnalyticsDocumentsGetParams {
  /**
   * Start Date
   * Start date for analytics
   */
  start_date?: string | null;
  /**
   * End Date
   * End date for analytics
   */
  end_date?: string | null;
  /**
   * Period
   * Predefined period (1h, 24h, 7d, 30d, 90d)
   * @default "7d"
   */
  period?: string;
}

export type GetDocumentAnalyticsApiV1AnalyticsDocumentsGetData =
  DocumentAnalyticsResponse;

export type GetSystemAnalyticsApiV1AnalyticsSystemGetData =
  SystemAnalyticsResponse;

export interface GetDashboardApiV1AnalyticsDashboardGetParams {
  /**
   * Start Date
   * Start date for analytics
   */
  start_date?: string | null;
  /**
   * End Date
   * End date for analytics
   */
  end_date?: string | null;
  /**
   * Period
   * Predefined period (1h, 24h, 7d, 30d, 90d)
   * @default "7d"
   */
  period?: string;
}

export type GetDashboardApiV1AnalyticsDashboardGetData = DashboardResponse;

export interface GetToolServerAnalyticsApiV1AnalyticsToolserversGetParams {
  /**
   * Start Date
   * Start date for analytics
   */
  start_date?: string | null;
  /**
   * End Date
   * End date for analytics
   */
  end_date?: string | null;
  /**
   * Period
   * Predefined period (1h, 24h, 7d, 30d, 90d)
   * @default "7d"
   */
  period?: string;
}

/** Response Get Tool Server Analytics Api V1 Analytics Toolservers Get */
export type GetToolServerAnalyticsApiV1AnalyticsToolserversGetData = Record<
  string,
  any
>;

export interface GetUserAnalyticsApiV1AnalyticsUsersUserIdGetParams {
  /**
   * Start Date
   * Start date for analytics
   */
  start_date?: string | null;
  /**
   * End Date
   * End date for analytics
   */
  end_date?: string | null;
  /**
   * Period
   * Predefined period (1h, 24h, 7d, 30d, 90d)
   * @default "7d"
   */
  period?: string;
  /** User Id */
  userId: string;
}

/** Response Get User Analytics Api V1 Analytics Users  User Id  Get */
export type GetUserAnalyticsApiV1AnalyticsUsersUserIdGetData = Record<
  string,
  any
>;

export interface ExportAnalyticsApiV1AnalyticsExportPostParams {
  /**
   * Format
   * Export format (json, csv, xlsx)
   * @default "json"
   */
  format?: string;
  /**
   * Metrics
   * List of metrics to export
   */
  metrics: string[];
  /**
   * Start Date
   * Start date for analytics
   */
  start_date?: string | null;
  /**
   * End Date
   * End date for analytics
   */
  end_date?: string | null;
  /**
   * Period
   * Predefined period (1h, 24h, 7d, 30d, 90d)
   * @default "7d"
   */
  period?: string;
}

export type ExportAnalyticsApiV1AnalyticsExportPostData = any;

/** Response Get Analytics Health Api V1 Analytics Health Get */
export type GetAnalyticsHealthApiV1AnalyticsHealthGetData = Record<string, any>;

/** Response Get Analytics Metrics Summary Api V1 Analytics Metrics Summary Get */
export type GetAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummaryGetData =
  Record<string, any>;

export type ListWorkflowDefinitionsApiV1WorkflowsWorkflowsDefinitionsGetData =
  WorkflowDefinitionsResponse;

export type CreateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsPostData =
  WorkflowDefinitionResponse;

export interface GetWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdGetParams {
  /**
   * Workflow Id
   * Workflow ID
   * @minLength 1
   */
  workflowId: string;
}

export type GetWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdGetData =
  WorkflowDefinitionResponse;

export interface UpdateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdPutParams {
  /**
   * Workflow Id
   * Workflow ID
   * @minLength 1
   */
  workflowId: string;
}

export type UpdateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdPutData =
  WorkflowDefinitionResponse;

export interface DeleteWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdDeleteParams {
  /**
   * Workflow Id
   * Workflow ID
   * @minLength 1
   */
  workflowId: string;
}

/** Response Delete Workflow Definition Api V1 Workflows Workflows Definitions  Workflow Id  Delete */
export type DeleteWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdDeleteData =
  Record<string, string>;

export type ListWorkflowTemplatesApiV1WorkflowsWorkflowsTemplatesGetData =
  ChatterSchemasWorkflowsWorkflowTemplatesResponse;

export type CreateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesPostData =
  WorkflowTemplateResponse;

export interface UpdateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesTemplateIdPutParams {
  /** Template Id */
  templateId: string;
}

export type UpdateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesTemplateIdPutData =
  WorkflowTemplateResponse;

export interface GetWorkflowAnalyticsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdAnalyticsGetParams {
  /**
   * Workflow Id
   * Workflow ID
   * @minLength 1
   */
  workflowId: string;
}

export type GetWorkflowAnalyticsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdAnalyticsGetData =
  WorkflowAnalyticsResponse;

export interface ExecuteWorkflowApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutePostParams {
  /**
   * Workflow Id
   * Workflow ID
   * @minLength 1
   */
  workflowId: string;
}

export type ExecuteWorkflowApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutePostData =
  WorkflowExecutionResponse;

export type ValidateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsValidatePostData =
  WorkflowValidationResponse;

/** Response Get Supported Node Types Api V1 Workflows Workflows Node Types Get */
export type GetSupportedNodeTypesApiV1WorkflowsWorkflowsNodeTypesGetData =
  NodeTypeResponse[];

export interface ListWorkflowExecutionsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutionsGetParams {
  /**
   * Workflow Id
   * Workflow ID
   * @minLength 1
   */
  workflowId: string;
}

/** Response List Workflow Executions Api V1 Workflows Workflows Definitions  Workflow Id  Executions Get */
export type ListWorkflowExecutionsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutionsGetData =
  WorkflowExecutionResponse[];

export type CreateToolServerApiV1ToolserversServersPostData =
  ToolServerResponse;

export interface ListToolServersApiV1ToolserversServersGetParams {
  /** Status */
  status?: ServerStatus | null;
  /**
   * Include Builtin
   * @default true
   */
  include_builtin?: boolean;
}

/** Response List Tool Servers Api V1 Toolservers Servers Get */
export type ListToolServersApiV1ToolserversServersGetData =
  ToolServerResponse[];

export interface GetToolServerApiV1ToolserversServersServerIdGetParams {
  /** Server Id */
  serverId: string;
}

export type GetToolServerApiV1ToolserversServersServerIdGetData =
  ToolServerResponse;

export interface UpdateToolServerApiV1ToolserversServersServerIdPutParams {
  /** Server Id */
  serverId: string;
}

export type UpdateToolServerApiV1ToolserversServersServerIdPutData =
  ToolServerResponse;

export interface DeleteToolServerApiV1ToolserversServersServerIdDeleteParams {
  /** Server Id */
  serverId: string;
}

export type DeleteToolServerApiV1ToolserversServersServerIdDeleteData =
  ToolServerDeleteResponse;

export interface StartToolServerApiV1ToolserversServersServerIdStartPostParams {
  /** Server Id */
  serverId: string;
}

export type StartToolServerApiV1ToolserversServersServerIdStartPostData =
  ToolServerOperationResponse;

export interface StopToolServerApiV1ToolserversServersServerIdStopPostParams {
  /** Server Id */
  serverId: string;
}

export type StopToolServerApiV1ToolserversServersServerIdStopPostData =
  ToolServerOperationResponse;

export interface RestartToolServerApiV1ToolserversServersServerIdRestartPostParams {
  /** Server Id */
  serverId: string;
}

export type RestartToolServerApiV1ToolserversServersServerIdRestartPostData =
  ToolServerOperationResponse;

export interface EnableToolServerApiV1ToolserversServersServerIdEnablePostParams {
  /** Server Id */
  serverId: string;
}

export type EnableToolServerApiV1ToolserversServersServerIdEnablePostData =
  ToolServerOperationResponse;

export interface DisableToolServerApiV1ToolserversServersServerIdDisablePostParams {
  /** Server Id */
  serverId: string;
}

export type DisableToolServerApiV1ToolserversServersServerIdDisablePostData =
  ToolServerOperationResponse;

export interface GetServerToolsApiV1ToolserversServersServerIdToolsGetParams {
  /**
   * Limit
   * @min 1
   * @max 100
   * @default 50
   */
  limit?: number;
  /**
   * Offset
   * @min 0
   * @default 0
   */
  offset?: number;
  /** Server Id */
  serverId: string;
}

export type GetServerToolsApiV1ToolserversServersServerIdToolsGetData =
  ServerToolsResponse;

export interface EnableToolApiV1ToolserversToolsToolIdEnablePostParams {
  /** Tool Id */
  toolId: string;
}

export type EnableToolApiV1ToolserversToolsToolIdEnablePostData =
  ToolOperationResponse;

export interface DisableToolApiV1ToolserversToolsToolIdDisablePostParams {
  /** Tool Id */
  toolId: string;
}

export type DisableToolApiV1ToolserversToolsToolIdDisablePostData =
  ToolOperationResponse;

export interface GetServerMetricsApiV1ToolserversServersServerIdMetricsGetParams {
  /** Server Id */
  serverId: string;
}

export type GetServerMetricsApiV1ToolserversServersServerIdMetricsGetData =
  ToolServerMetrics;

export interface CheckServerHealthApiV1ToolserversServersServerIdHealthGetParams {
  /** Server Id */
  serverId: string;
}

export type CheckServerHealthApiV1ToolserversServersServerIdHealthGetData =
  ToolServerHealthCheck;

export type BulkServerOperationApiV1ToolserversServersBulkPostData =
  BulkOperationResult;

/** Response List All Tools Api V1 Toolservers Tools All Get */
export type ListAllToolsApiV1ToolserversToolsAllGetData = Record<string, any>[];

export interface TestServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPostParams {
  /** Server Id */
  serverId: string;
}

/** Response Test Server Connectivity Api V1 Toolservers Servers  Server Id  Test Connectivity Post */
export type TestServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPostData =
  Record<string, any>;

export type GrantToolPermissionApiV1ToolserversPermissionsPostData =
  ToolPermissionResponse;

export interface UpdateToolPermissionApiV1ToolserversPermissionsPermissionIdPutParams {
  /** Permission Id */
  permissionId: string;
}

export type UpdateToolPermissionApiV1ToolserversPermissionsPermissionIdPutData =
  ToolPermissionResponse;

export interface RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteParams {
  /** Permission Id */
  permissionId: string;
}

/** Response Revoke Tool Permission Api V1 Toolservers Permissions  Permission Id  Delete */
export type RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteData =
  Record<string, any>;

export interface GetUserPermissionsApiV1ToolserversUsersUserIdPermissionsGetParams {
  /** User Id */
  userId: string;
}

/** Response Get User Permissions Api V1 Toolservers Users  User Id  Permissions Get */
export type GetUserPermissionsApiV1ToolserversUsersUserIdPermissionsGetData =
  ToolPermissionResponse[];

export type CreateRoleAccessRuleApiV1ToolserversRoleAccessPostData =
  RoleToolAccessResponse;

export interface GetRoleAccessRulesApiV1ToolserversRoleAccessGetParams {
  /** Role */
  role?: string | null;
}

/** Response Get Role Access Rules Api V1 Toolservers Role Access Get */
export type GetRoleAccessRulesApiV1ToolserversRoleAccessGetData =
  RoleToolAccessResponse[];

export type CheckToolAccessApiV1ToolserversAccessCheckPostData =
  ToolAccessResult;

export interface RefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPostParams {
  /** Server Id */
  serverId: string;
}

/** Response Refresh Server Tools Api V1 Toolservers Servers  Server Id  Refresh Tools Post */
export type RefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPostData =
  Record<string, any>;

export type CreateAgentApiV1AgentsPostData = AgentResponse;

export interface ListAgentsApiV1AgentsGetParams {
  /** Agent Type */
  agent_type?: AgentType | null;
  /** Status */
  status?: AgentStatus | null;
}

export type ListAgentsApiV1AgentsGetData = AgentListResponse;

/** Response Get Agent Templates Api V1 Agents Templates Get */
export type GetAgentTemplatesApiV1AgentsTemplatesGetData = Record<
  string,
  any
>[];

export type GetAgentStatsApiV1AgentsStatsOverviewGetData = AgentStatsResponse;

export interface GetAgentApiV1AgentsAgentIdGetParams {
  /** Agent Id */
  agentId: string;
}

export type GetAgentApiV1AgentsAgentIdGetData = AgentResponse;

export interface UpdateAgentApiV1AgentsAgentIdPutParams {
  /** Agent Id */
  agentId: string;
}

export type UpdateAgentApiV1AgentsAgentIdPutData = AgentResponse;

export interface DeleteAgentApiV1AgentsAgentIdDeleteParams {
  /** Agent Id */
  agentId: string;
}

export type DeleteAgentApiV1AgentsAgentIdDeleteData = AgentDeleteResponse;

export interface InteractWithAgentApiV1AgentsAgentIdInteractPostParams {
  /** Agent Id */
  agentId: string;
}

export type InteractWithAgentApiV1AgentsAgentIdInteractPostData =
  AgentInteractResponse;

export interface GetAgentHealthApiV1AgentsAgentIdHealthGetParams {
  /** Agent Id */
  agentId: string;
}

export type GetAgentHealthApiV1AgentsAgentIdHealthGetData = AgentHealthResponse;

export type BulkCreateAgentsApiV1AgentsBulkPostData = AgentBulkCreateResponse;

/** Response Bulk Delete Agents Api V1 Agents Bulk Delete */
export type BulkDeleteAgentsApiV1AgentsBulkDeleteData = Record<string, any>;

export type CreateAbTestApiV1AbTestsPostData = ABTestResponse;

/** Tags */
export type ListAbTestsApiV1AbTestsGetPayload = string[] | null;

export interface ListAbTestsApiV1AbTestsGetParams {
  /** Status */
  status?: TestStatus | null;
  /** Test Type */
  test_type?: TestType | null;
}

export type ListAbTestsApiV1AbTestsGetData = ABTestListResponse;

export interface GetAbTestApiV1AbTestsTestIdGetParams {
  /** Test Id */
  testId: string;
}

export type GetAbTestApiV1AbTestsTestIdGetData = ABTestResponse;

export interface UpdateAbTestApiV1AbTestsTestIdPutParams {
  /** Test Id */
  testId: string;
}

export type UpdateAbTestApiV1AbTestsTestIdPutData = ABTestResponse;

export interface DeleteAbTestApiV1AbTestsTestIdDeleteParams {
  /** Test Id */
  testId: string;
}

export type DeleteAbTestApiV1AbTestsTestIdDeleteData = ABTestDeleteResponse;

export interface StartAbTestApiV1AbTestsTestIdStartPostParams {
  /** Test Id */
  testId: string;
}

export type StartAbTestApiV1AbTestsTestIdStartPostData = ABTestActionResponse;

export interface PauseAbTestApiV1AbTestsTestIdPausePostParams {
  /** Test Id */
  testId: string;
}

export type PauseAbTestApiV1AbTestsTestIdPausePostData = ABTestActionResponse;

export interface CompleteAbTestApiV1AbTestsTestIdCompletePostParams {
  /** Test Id */
  testId: string;
}

export type CompleteAbTestApiV1AbTestsTestIdCompletePostData =
  ABTestActionResponse;

export interface GetAbTestResultsApiV1AbTestsTestIdResultsGetParams {
  /** Test Id */
  testId: string;
}

export type GetAbTestResultsApiV1AbTestsTestIdResultsGetData =
  ABTestResultsResponse;

export interface GetAbTestMetricsApiV1AbTestsTestIdMetricsGetParams {
  /** Test Id */
  testId: string;
}

export type GetAbTestMetricsApiV1AbTestsTestIdMetricsGetData =
  ABTestMetricsResponse;

export interface EndAbTestApiV1AbTestsTestIdEndPostParams {
  /** Winner Variant */
  winner_variant: string;
  /** Test Id */
  testId: string;
}

export type EndAbTestApiV1AbTestsTestIdEndPostData = ABTestActionResponse;

export interface GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetParams {
  /** Test Id */
  testId: string;
}

/** Response Get Ab Test Performance Api V1 Ab Tests  Test Id  Performance Get */
export type GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetData = Record<
  string,
  any
>;

export interface GetAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGetParams {
  /** Test Id */
  testId: string;
}

/** Response Get Ab Test Recommendations Api V1 Ab Tests  Test Id  Recommendations Get */
export type GetAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGetData =
  Record<string, any>;

export type EventsStreamApiV1EventsStreamGetData = any;

export type AdminEventsStreamApiV1EventsAdminStreamGetData = any;

export type GetSseStatsApiV1EventsStatsGetData = SSEStatsResponse;

export type TriggerTestEventApiV1EventsTestEventPostData = TestEventResponse;

export type TriggerBroadcastTestApiV1EventsBroadcastTestPostData =
  TestEventResponse;

export type InstallPluginApiV1PluginsInstallPostData = PluginResponse;

export interface ListPluginsApiV1PluginsGetParams {
  /** Plugin Type */
  plugin_type?: PluginType | null;
  /** Status */
  status?: PluginStatus | null;
  /** Enabled */
  enabled?: boolean | null;
}

export type ListPluginsApiV1PluginsGetData = PluginListResponse;

export interface GetPluginApiV1PluginsPluginIdGetParams {
  /** Plugin Id */
  pluginId: string;
}

export type GetPluginApiV1PluginsPluginIdGetData = PluginResponse;

export interface UpdatePluginApiV1PluginsPluginIdPutParams {
  /** Plugin Id */
  pluginId: string;
}

export type UpdatePluginApiV1PluginsPluginIdPutData = PluginResponse;

export interface UninstallPluginApiV1PluginsPluginIdDeleteParams {
  /** Plugin Id */
  pluginId: string;
}

export type UninstallPluginApiV1PluginsPluginIdDeleteData =
  PluginDeleteResponse;

export interface EnablePluginApiV1PluginsPluginIdEnablePostParams {
  /** Plugin Id */
  pluginId: string;
}

export type EnablePluginApiV1PluginsPluginIdEnablePostData =
  PluginActionResponse;

export interface DisablePluginApiV1PluginsPluginIdDisablePostParams {
  /** Plugin Id */
  pluginId: string;
}

export type DisablePluginApiV1PluginsPluginIdDisablePostData =
  PluginActionResponse;

export interface HealthCheckPluginsApiV1PluginsHealthGetParams {
  /**
   * Auto Disable Unhealthy
   * @default false
   */
  auto_disable_unhealthy?: boolean;
}

export type HealthCheckPluginsApiV1PluginsHealthGetData =
  PluginHealthCheckResponse;

export type GetPluginStatsApiV1PluginsStatsGetData = PluginStatsResponse;

export interface CheckPluginDependenciesApiV1PluginsPluginIdDependenciesGetParams {
  /** Plugin Id */
  pluginId: string;
}

/** Response Check Plugin Dependencies Api V1 Plugins  Plugin Id  Dependencies Get */
export type CheckPluginDependenciesApiV1PluginsPluginIdDependenciesGetData =
  Record<string, any>;

/** Plugin Ids */
export type BulkEnablePluginsApiV1PluginsBulkEnablePostPayload = string[];

/** Response Bulk Enable Plugins Api V1 Plugins Bulk Enable Post */
export type BulkEnablePluginsApiV1PluginsBulkEnablePostData = Record<
  string,
  any
>;

/** Plugin Ids */
export type BulkDisablePluginsApiV1PluginsBulkDisablePostPayload = string[];

/** Response Bulk Disable Plugins Api V1 Plugins Bulk Disable Post */
export type BulkDisablePluginsApiV1PluginsBulkDisablePostData = Record<
  string,
  any
>;

export type CreateJobApiV1JobsPostData = JobResponse;

/** Tags */
export type ListJobsApiV1JobsGetPayload = string[] | null;

export interface ListJobsApiV1JobsGetParams {
  /** Status */
  status?: JobStatus | null;
  /** Priority */
  priority?: JobPriority | null;
  /** Function Name */
  function_name?: string | null;
  /** Created After */
  created_after?: string | null;
  /** Created Before */
  created_before?: string | null;
  /** Search */
  search?: string | null;
  /**
   * Limit
   * @min 1
   * @max 100
   * @default 20
   */
  limit?: number;
  /**
   * Offset
   * @min 0
   * @default 0
   */
  offset?: number;
  /**
   * Sort By
   * @default "created_at"
   */
  sort_by?: string;
  /**
   * Sort Order
   * @default "desc"
   * @pattern ^(asc|desc)$
   */
  sort_order?: string;
}

export type ListJobsApiV1JobsGetData = JobListResponse;

export interface GetJobApiV1JobsJobIdGetParams {
  /** Job Id */
  jobId: string;
}

export type GetJobApiV1JobsJobIdGetData = JobResponse;

export interface CancelJobApiV1JobsJobIdCancelPostParams {
  /** Job Id */
  jobId: string;
}

export type CancelJobApiV1JobsJobIdCancelPostData = JobActionResponse;

export type GetJobStatsApiV1JobsStatsOverviewGetData = JobStatsResponse;

export interface CleanupJobsApiV1JobsCleanupPostParams {
  /**
   * Force
   * @default false
   */
  force?: boolean;
}

/** Response Cleanup Jobs Api V1 Jobs Cleanup Post */
export type CleanupJobsApiV1JobsCleanupPostData = Record<string, any>;

export type ExportDataApiV1DataExportPostData = ExportDataResponse;

export type CreateBackupApiV1DataBackupPostData = BackupResponse;

export interface ListBackupsApiV1DataBackupsGetParams {
  /** Backup Type */
  backup_type?: BackupType | null;
  /** Status */
  status?: string | null;
}

export type ListBackupsApiV1DataBackupsGetData = BackupListResponse;

export type RestoreFromBackupApiV1DataRestorePostData = RestoreResponse;

export type GetStorageStatsApiV1DataStatsGetData = StorageStatsResponse;

/** Document Ids */
export type BulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPostPayload =
  string[];

export type BulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPostData =
  BulkDeleteResponse;

/** Conversation Ids */
export type BulkDeleteConversationsApiV1DataBulkDeleteConversationsPostPayload =
  string[];

export type BulkDeleteConversationsApiV1DataBulkDeleteConversationsPostData =
  BulkDeleteResponse;

/** Prompt Ids */
export type BulkDeletePromptsApiV1DataBulkDeletePromptsPostPayload = string[];

export type BulkDeletePromptsApiV1DataBulkDeletePromptsPostData =
  BulkDeleteResponse;

export interface ListProvidersApiV1ModelsProvidersGetParams {
  /**
   * Page
   * Page number
   * @min 1
   * @default 1
   */
  page?: number;
  /**
   * Per Page
   * Items per page
   * @min 1
   * @max 100
   * @default 20
   */
  per_page?: number;
  /**
   * Active Only
   * Show only active providers
   * @default true
   */
  active_only?: boolean;
}

export type ListProvidersApiV1ModelsProvidersGetData = ProviderList;

export type CreateProviderApiV1ModelsProvidersPostData = Provider;

export interface GetProviderApiV1ModelsProvidersProviderIdGetParams {
  /** Provider Id */
  providerId: string;
}

export type GetProviderApiV1ModelsProvidersProviderIdGetData = Provider;

export interface UpdateProviderApiV1ModelsProvidersProviderIdPutParams {
  /** Provider Id */
  providerId: string;
}

export type UpdateProviderApiV1ModelsProvidersProviderIdPutData = Provider;

export interface DeleteProviderApiV1ModelsProvidersProviderIdDeleteParams {
  /** Provider Id */
  providerId: string;
}

export type DeleteProviderApiV1ModelsProvidersProviderIdDeleteData =
  ProviderDeleteResponse;

export interface SetDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPostParams {
  /** Provider Id */
  providerId: string;
}

export type SetDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPostData =
  ProviderDefaultResponse;

export interface ListModelsApiV1ModelsModelsGetParams {
  /**
   * Provider Id
   * Filter by provider ID
   */
  provider_id?: string;
  /** Filter by model type */
  model_type?: ModelType;
  /**
   * Page
   * Page number
   * @min 1
   * @default 1
   */
  page?: number;
  /**
   * Per Page
   * Items per page
   * @min 1
   * @max 100
   * @default 20
   */
  per_page?: number;
  /**
   * Active Only
   * Show only active models
   * @default true
   */
  active_only?: boolean;
}

export type ListModelsApiV1ModelsModelsGetData = ModelDefList;

export type CreateModelApiV1ModelsModelsPostData = ModelDefWithProvider;

export interface GetModelApiV1ModelsModelsModelIdGetParams {
  /** Model Id */
  modelId: string;
}

export type GetModelApiV1ModelsModelsModelIdGetData = ModelDefWithProvider;

export interface UpdateModelApiV1ModelsModelsModelIdPutParams {
  /** Model Id */
  modelId: string;
}

export type UpdateModelApiV1ModelsModelsModelIdPutData = ModelDefWithProvider;

export interface DeleteModelApiV1ModelsModelsModelIdDeleteParams {
  /** Model Id */
  modelId: string;
}

export type DeleteModelApiV1ModelsModelsModelIdDeleteData = ModelDeleteResponse;

export interface SetDefaultModelApiV1ModelsModelsModelIdSetDefaultPostParams {
  /** Model Id */
  modelId: string;
}

export type SetDefaultModelApiV1ModelsModelsModelIdSetDefaultPostData =
  ModelDefaultResponse;

export interface ListEmbeddingSpacesApiV1ModelsEmbeddingSpacesGetParams {
  /**
   * Model Id
   * Filter by model ID
   */
  model_id?: string;
  /**
   * Page
   * Page number
   * @min 1
   * @default 1
   */
  page?: number;
  /**
   * Per Page
   * Items per page
   * @min 1
   * @max 100
   * @default 20
   */
  per_page?: number;
  /**
   * Active Only
   * Show only active spaces
   * @default true
   */
  active_only?: boolean;
}

export type ListEmbeddingSpacesApiV1ModelsEmbeddingSpacesGetData =
  EmbeddingSpaceList;

export type CreateEmbeddingSpaceApiV1ModelsEmbeddingSpacesPostData =
  EmbeddingSpaceWithModel;

export interface GetEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGetParams {
  /** Space Id */
  spaceId: string;
}

export type GetEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGetData =
  EmbeddingSpaceWithModel;

export interface UpdateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPutParams {
  /** Space Id */
  spaceId: string;
}

export type UpdateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPutData =
  EmbeddingSpaceWithModel;

export interface DeleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDeleteParams {
  /** Space Id */
  spaceId: string;
}

export type DeleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDeleteData =
  EmbeddingSpaceDeleteResponse;

export interface SetDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPostParams {
  /** Space Id */
  spaceId: string;
}

export type SetDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPostData =
  EmbeddingSpaceDefaultResponse;

export interface GetDefaultProviderApiV1ModelsDefaultsProviderModelTypeGetParams {
  /** Types of AI models. */
  modelType: ModelType;
}

export type GetDefaultProviderApiV1ModelsDefaultsProviderModelTypeGetData =
  Provider;

export interface GetDefaultModelApiV1ModelsDefaultsModelModelTypeGetParams {
  /** Types of AI models. */
  modelType: ModelType;
}

export type GetDefaultModelApiV1ModelsDefaultsModelModelTypeGetData =
  ModelDefWithProvider;

export type GetDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpaceGetData =
  EmbeddingSpaceWithModel;

export type RootGetData = any;
