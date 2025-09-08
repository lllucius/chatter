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


 import type { AxiosRequestConfig, AxiosResponse } from "axios"; 
import { HttpClient, RequestParams, ContentType, HttpResponse } from "./http-client";
import { VariantAllocation, UserRole, ToolStatus, ToolAccessLevel, TestType, TestStatus, ServerStatus, ReductionStrategy, ReadinessStatus, ProviderType, PromptType, PromptCategory, ProfileType, PluginType, PluginStatus, ModelType, MetricType, MessageRole, JobStatus, JobPriority, HealthStatus, ExportScope, DocumentType, DocumentStatus, DistanceMetric, DataFormat, ConversationStatus, BackupType, AgentType, AgentStatus, AgentCapability, ABTestActionResponse, ABTestCreateRequest, ABTestDeleteResponse, ABTestListResponse, ABTestMetricsResponse, ABTestResponse, ABTestResultsResponse, ABTestUpdateRequest, APIKeyCreate, APIKeyResponse, APIKeyRevokeResponse, AccountDeactivateResponse, AgentBulkCreateRequest, AgentBulkCreateResponse, AgentBulkDeleteRequest, AgentCreateRequest, AgentDeleteResponse, AgentHealthResponse, AgentInteractRequest, AgentInteractResponse, AgentListResponse, AgentResponse, AgentStatsResponse, AgentUpdateRequest, AvailableProvidersResponse, AvailableToolResponse, AvailableToolsResponse, BackupListResponse, BackupRequest, BackupResponse, BodyListAgentsApiV1AgentsGet, BodyUploadDocumentApiV1DocumentsUploadPost, BottleneckInfo, BulkDeleteResponse, BulkOperationResult, BulkToolServerOperation, ChatRequest, ChatResponse, ComplexityMetrics, ConversationCreate, ConversationDeleteResponse, ConversationResponse, ConversationSearchResponse, ConversationStatsResponse, ConversationUpdate, ConversationWithMessages, CorrelationTraceResponse, DashboardResponse, DefaultProvider, DocumentAnalyticsResponse, DocumentChunkResponse, DocumentChunksResponse, DocumentDeleteResponse, DocumentListResponse, DocumentProcessingRequest, DocumentProcessingResponse, DocumentResponse, DocumentSearchRequest, DocumentSearchResponse, DocumentSearchResult, DocumentStatsResponse, DocumentUpdate, EmbeddingSpaceCreate, EmbeddingSpaceDefaultResponse, EmbeddingSpaceDeleteResponse, EmbeddingSpaceList, EmbeddingSpaceUpdate, EmbeddingSpaceWithModel, ExportDataRequest, ExportDataResponse, HTTPValidationError, HealthCheckResponse, JobActionResponse, JobCreateRequest, JobListResponse, JobResponse, JobStatsResponse, LogoutResponse, McpStatusResponse, MessageDeleteResponse, MessageResponse, MetricsResponse, ModelDefCreate, ModelDefList, ModelDefUpdate, ModelDefWithProvider, ModelDefaultResponse, ModelDeleteResponse, NodePropertyDefinition, NodeTypeResponse, OAuthConfigSchema, OptimizationSuggestion, PaginationRequest, PasswordChange, PasswordChangeResponse, PasswordResetConfirmResponse, PasswordResetRequestResponse, PerformanceMetricsResponse, PerformanceStatsResponse, PluginActionResponse, PluginDeleteResponse, PluginHealthCheckResponse, PluginInstallRequest, PluginListResponse, PluginResponse, PluginStatsResponse, PluginUpdateRequest, ProfileCloneRequest, ProfileCreate, ProfileDeleteResponse, ProfileListResponse, ProfileResponse, ProfileStatsResponse, ProfileTestRequest, ProfileTestResponse, ProfileUpdate, PromptCloneRequest, PromptCreate, PromptDeleteResponse, PromptListResponse, PromptResponse, PromptStatsResponse, PromptTestRequest, PromptTestResponse, PromptUpdate, Provider, ProviderCreate, ProviderDefaultResponse, ProviderDeleteResponse, ProviderList, ProviderUpdate, ReadinessCheckResponse, RestoreRequest, RestoreResponse, RoleToolAccessCreate, RoleToolAccessResponse, SSEStatsResponse, ServerToolResponse, ServerToolsResponse, SortingRequest, StorageStatsResponse, SystemAnalyticsResponse, TestEventResponse, TestMetric, TestVariant, TokenRefresh, TokenRefreshResponse, TokenResponse, ToolAccessResult, ToolOperationResponse, ToolPermissionCreate, ToolPermissionResponse, ToolPermissionUpdate, ToolServerCreate, ToolServerDeleteResponse, ToolServerHealthCheck, ToolServerMetrics, ToolServerOperationResponse, ToolServerResponse, ToolServerUpdate, UsageMetricsResponse, UserCreate, UserLogin, UserResponse, UserToolAccessCheck, UserUpdate, ValidationError, WorkflowAnalyticsResponse, WorkflowDefinitionCreate, WorkflowDefinitionResponse, WorkflowDefinitionUpdate, WorkflowDefinitionsResponse, WorkflowEdge, WorkflowEdgeData, WorkflowExecutionRequest, WorkflowExecutionResponse, WorkflowNode, WorkflowNodeData, WorkflowTemplateCreate, WorkflowTemplateInfo, WorkflowTemplateResponse, WorkflowTemplateUpdate, WorkflowValidationResponse, ChatterSchemasChatWorkflowTemplatesResponse, ChatterSchemasWorkflowsWorkflowTemplatesResponse, HealthCheckEndpointHealthzGetData, ReadinessCheckReadyzGetData, LivenessCheckLiveGetData, GetMetricsMetricsGetData, GetCorrelationTraceTraceCorrelationIdGetParams, GetCorrelationTraceTraceCorrelationIdGetData, RegisterApiV1AuthRegisterPostData, LoginApiV1AuthLoginPostData, RefreshTokenApiV1AuthRefreshPostData, GetCurrentUserInfoApiV1AuthMeGetData, UpdateProfileApiV1AuthMePutData, ChangePasswordApiV1AuthChangePasswordPostData, CreateApiKeyApiV1AuthApiKeyPostData, RevokeApiKeyApiV1AuthApiKeyDeleteData, ListApiKeysApiV1AuthApiKeysGetData, LogoutApiV1AuthLogoutPostData, RequestPasswordResetApiV1AuthPasswordResetRequestPostParams, RequestPasswordResetApiV1AuthPasswordResetRequestPostData, ConfirmPasswordResetApiV1AuthPasswordResetConfirmPostParams, ConfirmPasswordResetApiV1AuthPasswordResetConfirmPostData, DeactivateAccountApiV1AuthAccountDeleteData, CreateConversationApiV1ChatConversationsPostData, ListConversationsApiV1ChatConversationsGetParams, ListConversationsApiV1ChatConversationsGetData, GetConversationApiV1ChatConversationsConversationIdGetParams, GetConversationApiV1ChatConversationsConversationIdGetData, UpdateConversationApiV1ChatConversationsConversationIdPutParams, UpdateConversationApiV1ChatConversationsConversationIdPutData, DeleteConversationApiV1ChatConversationsConversationIdDeleteParams, DeleteConversationApiV1ChatConversationsConversationIdDeleteData, GetConversationMessagesApiV1ChatConversationsConversationIdMessagesGetParams, GetConversationMessagesApiV1ChatConversationsConversationIdMessagesGetData, DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteParams, DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteData, ChatApiV1ChatChatPostData, GetAvailableToolsApiV1ChatToolsAvailableGetData, GetWorkflowTemplatesApiV1ChatTemplatesGetData, ChatWithTemplateApiV1ChatTemplateTemplateNamePostParams, ChatWithTemplateApiV1ChatTemplateTemplateNamePostData, GetPerformanceStatsApiV1ChatPerformanceStatsGetData, GetMcpStatusApiV1ChatMcpStatusGetData, UploadDocumentApiV1DocumentsUploadPostData, ListDocumentsApiV1DocumentsGetParams, ListDocumentsApiV1DocumentsGetData, GetDocumentApiV1DocumentsDocumentIdGetParams, GetDocumentApiV1DocumentsDocumentIdGetData, UpdateDocumentApiV1DocumentsDocumentIdPutParams, UpdateDocumentApiV1DocumentsDocumentIdPutData, DeleteDocumentApiV1DocumentsDocumentIdDeleteParams, DeleteDocumentApiV1DocumentsDocumentIdDeleteData, SearchDocumentsApiV1DocumentsSearchPostData, GetDocumentChunksApiV1DocumentsDocumentIdChunksGetParams, GetDocumentChunksApiV1DocumentsDocumentIdChunksGetData, ProcessDocumentApiV1DocumentsDocumentIdProcessPostParams, ProcessDocumentApiV1DocumentsDocumentIdProcessPostData, GetDocumentStatsApiV1DocumentsStatsOverviewGetData, DownloadDocumentApiV1DocumentsDocumentIdDownloadGetParams, DownloadDocumentApiV1DocumentsDocumentIdDownloadGetData, ReprocessDocumentApiV1DocumentsDocumentIdReprocessPostParams, ReprocessDocumentApiV1DocumentsDocumentIdReprocessPostData, CreateProfileApiV1ProfilesPostData, ListProfilesApiV1ProfilesGetParams, ListProfilesApiV1ProfilesGetData, GetProfileApiV1ProfilesProfileIdGetParams, GetProfileApiV1ProfilesProfileIdGetData, UpdateProfileApiV1ProfilesProfileIdPutParams, UpdateProfileApiV1ProfilesProfileIdPutData, DeleteProfileApiV1ProfilesProfileIdDeleteParams, DeleteProfileApiV1ProfilesProfileIdDeleteData, TestProfileApiV1ProfilesProfileIdTestPostParams, TestProfileApiV1ProfilesProfileIdTestPostData, CloneProfileApiV1ProfilesProfileIdClonePostParams, CloneProfileApiV1ProfilesProfileIdClonePostData, GetProfileStatsApiV1ProfilesStatsOverviewGetData, GetAvailableProvidersApiV1ProfilesProvidersAvailableGetData, CreatePromptApiV1PromptsPostData, GetPromptStatsApiV1PromptsStatsOverviewGetData, ListPromptsApiV1PromptsGetParams, ListPromptsApiV1PromptsGetData, GetPromptApiV1PromptsPromptIdGetParams, GetPromptApiV1PromptsPromptIdGetData, UpdatePromptApiV1PromptsPromptIdPutParams, UpdatePromptApiV1PromptsPromptIdPutData, DeletePromptApiV1PromptsPromptIdDeleteParams, DeletePromptApiV1PromptsPromptIdDeleteData, TestPromptApiV1PromptsPromptIdTestPostParams, TestPromptApiV1PromptsPromptIdTestPostData, ClonePromptApiV1PromptsPromptIdClonePostParams, ClonePromptApiV1PromptsPromptIdClonePostData, GetConversationStatsApiV1AnalyticsConversationsGetParams, GetConversationStatsApiV1AnalyticsConversationsGetData, GetUsageMetricsApiV1AnalyticsUsageGetParams, GetUsageMetricsApiV1AnalyticsUsageGetData, GetPerformanceMetricsApiV1AnalyticsPerformanceGetParams, GetPerformanceMetricsApiV1AnalyticsPerformanceGetData, GetDocumentAnalyticsApiV1AnalyticsDocumentsGetParams, GetDocumentAnalyticsApiV1AnalyticsDocumentsGetData, GetSystemAnalyticsApiV1AnalyticsSystemGetData, GetDashboardApiV1AnalyticsDashboardGetParams, GetDashboardApiV1AnalyticsDashboardGetData, GetToolServerAnalyticsApiV1AnalyticsToolserversGetParams, GetToolServerAnalyticsApiV1AnalyticsToolserversGetData, GetUserAnalyticsApiV1AnalyticsUsersUserIdGetParams, GetUserAnalyticsApiV1AnalyticsUsersUserIdGetData, ExportAnalyticsApiV1AnalyticsExportPostParams, ExportAnalyticsApiV1AnalyticsExportPostData, GetAnalyticsHealthApiV1AnalyticsHealthGetData, GetAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummaryGetData, ListWorkflowDefinitionsApiV1WorkflowsWorkflowsDefinitionsGetData, CreateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsPostData, GetWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdGetParams, GetWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdGetData, UpdateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdPutParams, UpdateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdPutData, DeleteWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdDeleteParams, DeleteWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdDeleteData, ListWorkflowTemplatesApiV1WorkflowsWorkflowsTemplatesGetData, CreateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesPostData, UpdateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesTemplateIdPutParams, UpdateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesTemplateIdPutData, GetWorkflowAnalyticsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdAnalyticsGetParams, GetWorkflowAnalyticsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdAnalyticsGetData, ExecuteWorkflowApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutePostParams, ExecuteWorkflowApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutePostData, ValidateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsValidatePostData, GetSupportedNodeTypesApiV1WorkflowsWorkflowsNodeTypesGetData, ListWorkflowExecutionsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutionsGetParams, ListWorkflowExecutionsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutionsGetData, CreateToolServerApiV1ToolserversServersPostData, ListToolServersApiV1ToolserversServersGetParams, ListToolServersApiV1ToolserversServersGetData, GetToolServerApiV1ToolserversServersServerIdGetParams, GetToolServerApiV1ToolserversServersServerIdGetData, UpdateToolServerApiV1ToolserversServersServerIdPutParams, UpdateToolServerApiV1ToolserversServersServerIdPutData, DeleteToolServerApiV1ToolserversServersServerIdDeleteParams, DeleteToolServerApiV1ToolserversServersServerIdDeleteData, StartToolServerApiV1ToolserversServersServerIdStartPostParams, StartToolServerApiV1ToolserversServersServerIdStartPostData, StopToolServerApiV1ToolserversServersServerIdStopPostParams, StopToolServerApiV1ToolserversServersServerIdStopPostData, RestartToolServerApiV1ToolserversServersServerIdRestartPostParams, RestartToolServerApiV1ToolserversServersServerIdRestartPostData, EnableToolServerApiV1ToolserversServersServerIdEnablePostParams, EnableToolServerApiV1ToolserversServersServerIdEnablePostData, DisableToolServerApiV1ToolserversServersServerIdDisablePostParams, DisableToolServerApiV1ToolserversServersServerIdDisablePostData, GetServerToolsApiV1ToolserversServersServerIdToolsGetParams, GetServerToolsApiV1ToolserversServersServerIdToolsGetData, EnableToolApiV1ToolserversToolsToolIdEnablePostParams, EnableToolApiV1ToolserversToolsToolIdEnablePostData, DisableToolApiV1ToolserversToolsToolIdDisablePostParams, DisableToolApiV1ToolserversToolsToolIdDisablePostData, GetServerMetricsApiV1ToolserversServersServerIdMetricsGetParams, GetServerMetricsApiV1ToolserversServersServerIdMetricsGetData, CheckServerHealthApiV1ToolserversServersServerIdHealthGetParams, CheckServerHealthApiV1ToolserversServersServerIdHealthGetData, BulkServerOperationApiV1ToolserversServersBulkPostData, ListAllToolsApiV1ToolserversToolsAllGetData, TestServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPostParams, TestServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPostData, GrantToolPermissionApiV1ToolserversPermissionsPostData, UpdateToolPermissionApiV1ToolserversPermissionsPermissionIdPutParams, UpdateToolPermissionApiV1ToolserversPermissionsPermissionIdPutData, RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteParams, RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteData, GetUserPermissionsApiV1ToolserversUsersUserIdPermissionsGetParams, GetUserPermissionsApiV1ToolserversUsersUserIdPermissionsGetData, CreateRoleAccessRuleApiV1ToolserversRoleAccessPostData, GetRoleAccessRulesApiV1ToolserversRoleAccessGetParams, GetRoleAccessRulesApiV1ToolserversRoleAccessGetData, CheckToolAccessApiV1ToolserversAccessCheckPostData, RefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPostParams, RefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPostData, CreateAgentApiV1AgentsPostData, ListAgentsApiV1AgentsGetParams, ListAgentsApiV1AgentsGetData, GetAgentTemplatesApiV1AgentsTemplatesGetData, GetAgentStatsApiV1AgentsStatsOverviewGetData, GetAgentApiV1AgentsAgentIdGetParams, GetAgentApiV1AgentsAgentIdGetData, UpdateAgentApiV1AgentsAgentIdPutParams, UpdateAgentApiV1AgentsAgentIdPutData, DeleteAgentApiV1AgentsAgentIdDeleteParams, DeleteAgentApiV1AgentsAgentIdDeleteData, InteractWithAgentApiV1AgentsAgentIdInteractPostParams, InteractWithAgentApiV1AgentsAgentIdInteractPostData, GetAgentHealthApiV1AgentsAgentIdHealthGetParams, GetAgentHealthApiV1AgentsAgentIdHealthGetData, BulkCreateAgentsApiV1AgentsBulkPostData, BulkDeleteAgentsApiV1AgentsBulkDeleteData, CreateAbTestApiV1AbTestsPostData, ListAbTestsApiV1AbTestsGetPayload, ListAbTestsApiV1AbTestsGetParams, ListAbTestsApiV1AbTestsGetData, GetAbTestApiV1AbTestsTestIdGetParams, GetAbTestApiV1AbTestsTestIdGetData, UpdateAbTestApiV1AbTestsTestIdPutParams, UpdateAbTestApiV1AbTestsTestIdPutData, DeleteAbTestApiV1AbTestsTestIdDeleteParams, DeleteAbTestApiV1AbTestsTestIdDeleteData, StartAbTestApiV1AbTestsTestIdStartPostParams, StartAbTestApiV1AbTestsTestIdStartPostData, PauseAbTestApiV1AbTestsTestIdPausePostParams, PauseAbTestApiV1AbTestsTestIdPausePostData, CompleteAbTestApiV1AbTestsTestIdCompletePostParams, CompleteAbTestApiV1AbTestsTestIdCompletePostData, GetAbTestResultsApiV1AbTestsTestIdResultsGetParams, GetAbTestResultsApiV1AbTestsTestIdResultsGetData, GetAbTestMetricsApiV1AbTestsTestIdMetricsGetParams, GetAbTestMetricsApiV1AbTestsTestIdMetricsGetData, EndAbTestApiV1AbTestsTestIdEndPostParams, EndAbTestApiV1AbTestsTestIdEndPostData, GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetParams, GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetData, GetAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGetParams, GetAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGetData, EventsStreamApiV1EventsStreamGetData, AdminEventsStreamApiV1EventsAdminStreamGetData, GetSseStatsApiV1EventsStatsGetData, TriggerTestEventApiV1EventsTestEventPostData, TriggerBroadcastTestApiV1EventsBroadcastTestPostData, InstallPluginApiV1PluginsInstallPostData, ListPluginsApiV1PluginsGetParams, ListPluginsApiV1PluginsGetData, GetPluginApiV1PluginsPluginIdGetParams, GetPluginApiV1PluginsPluginIdGetData, UpdatePluginApiV1PluginsPluginIdPutParams, UpdatePluginApiV1PluginsPluginIdPutData, UninstallPluginApiV1PluginsPluginIdDeleteParams, UninstallPluginApiV1PluginsPluginIdDeleteData, EnablePluginApiV1PluginsPluginIdEnablePostParams, EnablePluginApiV1PluginsPluginIdEnablePostData, DisablePluginApiV1PluginsPluginIdDisablePostParams, DisablePluginApiV1PluginsPluginIdDisablePostData, HealthCheckPluginsApiV1PluginsHealthGetParams, HealthCheckPluginsApiV1PluginsHealthGetData, GetPluginStatsApiV1PluginsStatsGetData, CheckPluginDependenciesApiV1PluginsPluginIdDependenciesGetParams, CheckPluginDependenciesApiV1PluginsPluginIdDependenciesGetData, BulkEnablePluginsApiV1PluginsBulkEnablePostPayload, BulkEnablePluginsApiV1PluginsBulkEnablePostData, BulkDisablePluginsApiV1PluginsBulkDisablePostPayload, BulkDisablePluginsApiV1PluginsBulkDisablePostData, CreateJobApiV1JobsPostData, ListJobsApiV1JobsGetPayload, ListJobsApiV1JobsGetParams, ListJobsApiV1JobsGetData, GetJobApiV1JobsJobIdGetParams, GetJobApiV1JobsJobIdGetData, CancelJobApiV1JobsJobIdCancelPostParams, CancelJobApiV1JobsJobIdCancelPostData, GetJobStatsApiV1JobsStatsOverviewGetData, CleanupJobsApiV1JobsCleanupPostParams, CleanupJobsApiV1JobsCleanupPostData, ExportDataApiV1DataExportPostData, CreateBackupApiV1DataBackupPostData, ListBackupsApiV1DataBackupsGetParams, ListBackupsApiV1DataBackupsGetData, RestoreFromBackupApiV1DataRestorePostData, GetStorageStatsApiV1DataStatsGetData, BulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPostPayload, BulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPostData, BulkDeleteConversationsApiV1DataBulkDeleteConversationsPostPayload, BulkDeleteConversationsApiV1DataBulkDeleteConversationsPostData, BulkDeletePromptsApiV1DataBulkDeletePromptsPostPayload, BulkDeletePromptsApiV1DataBulkDeletePromptsPostData, ListProvidersApiV1ModelsProvidersGetParams, ListProvidersApiV1ModelsProvidersGetData, CreateProviderApiV1ModelsProvidersPostData, GetProviderApiV1ModelsProvidersProviderIdGetParams, GetProviderApiV1ModelsProvidersProviderIdGetData, UpdateProviderApiV1ModelsProvidersProviderIdPutParams, UpdateProviderApiV1ModelsProvidersProviderIdPutData, DeleteProviderApiV1ModelsProvidersProviderIdDeleteParams, DeleteProviderApiV1ModelsProvidersProviderIdDeleteData, SetDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPostParams, SetDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPostData, ListModelsApiV1ModelsModelsGetParams, ListModelsApiV1ModelsModelsGetData, CreateModelApiV1ModelsModelsPostData, GetModelApiV1ModelsModelsModelIdGetParams, GetModelApiV1ModelsModelsModelIdGetData, UpdateModelApiV1ModelsModelsModelIdPutParams, UpdateModelApiV1ModelsModelsModelIdPutData, DeleteModelApiV1ModelsModelsModelIdDeleteParams, DeleteModelApiV1ModelsModelsModelIdDeleteData, SetDefaultModelApiV1ModelsModelsModelIdSetDefaultPostParams, SetDefaultModelApiV1ModelsModelsModelIdSetDefaultPostData, ListEmbeddingSpacesApiV1ModelsEmbeddingSpacesGetParams, ListEmbeddingSpacesApiV1ModelsEmbeddingSpacesGetData, CreateEmbeddingSpaceApiV1ModelsEmbeddingSpacesPostData, GetEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGetParams, GetEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGetData, UpdateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPutParams, UpdateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPutData, DeleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDeleteParams, DeleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDeleteData, SetDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPostParams, SetDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPostData, GetDefaultProviderApiV1ModelsDefaultsProviderModelTypeGetParams, GetDefaultProviderApiV1ModelsDefaultsProviderModelTypeGetData, GetDefaultModelApiV1ModelsDefaultsModelModelTypeGetParams, GetDefaultModelApiV1ModelsDefaultsModelModelTypeGetData, GetDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpaceGetData, RootGetData } from "./data-contracts"

export class Api<SecurityDataType = unknown> extends HttpClient<SecurityDataType>  {

            /**
 * @description Register a new user with enhanced security validation. Args: user_data: User registration data request: HTTP request for security logging auth_service: Authentication service Returns: User data and authentication tokens
 *
 * @tags Authentication
 * @name RegisterApiV1AuthRegisterPost
 * @summary Register
 * @request POST:/api/v1/auth/register
 */
registerApiV1AuthRegisterPost: (data: UserCreate, params: RequestParams = {}) =>
    this.request<RegisterApiV1AuthRegisterPostData, HTTPValidationError>({
        path: `/api/v1/auth/register`,
        method: 'POST',
                body: data,                type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Authenticate user and return tokens with enhanced security. Args: user_data: User login data request: HTTP request for security logging auth_service: Authentication service Returns: User data and authentication tokens
 *
 * @tags Authentication
 * @name LoginApiV1AuthLoginPost
 * @summary Login
 * @request POST:/api/v1/auth/login
 */
loginApiV1AuthLoginPost: (data: UserLogin, params: RequestParams = {}) =>
    this.request<LoginApiV1AuthLoginPostData, HTTPValidationError>({
        path: `/api/v1/auth/login`,
        method: 'POST',
                body: data,                type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Refresh access token with enhanced security validation. Args: token_data: Refresh token data request: HTTP request for security logging auth_service: Authentication service Returns: New access and refresh tokens
 *
 * @tags Authentication
 * @name RefreshTokenApiV1AuthRefreshPost
 * @summary Refresh Token
 * @request POST:/api/v1/auth/refresh
 */
refreshTokenApiV1AuthRefreshPost: (data: TokenRefresh, params: RequestParams = {}) =>
    this.request<RefreshTokenApiV1AuthRefreshPostData, HTTPValidationError>({
        path: `/api/v1/auth/refresh`,
        method: 'POST',
                body: data,                type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get current user information. Args: current_user: Current authenticated user Returns: Current user data
 *
 * @tags Authentication
 * @name GetCurrentUserInfoApiV1AuthMeGet
 * @summary Get Current User Info
 * @request GET:/api/v1/auth/me
 * @secure
 */
getCurrentUserInfoApiV1AuthMeGet: (params: RequestParams = {}) =>
    this.request<GetCurrentUserInfoApiV1AuthMeGetData, any>({
        path: `/api/v1/auth/me`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update current user profile. Args: user_data: Profile update data current_user: Current authenticated user auth_service: Authentication service Returns: Updated user data
 *
 * @tags Authentication
 * @name UpdateProfileApiV1AuthMePut
 * @summary Update Profile
 * @request PUT:/api/v1/auth/me
 * @secure
 */
updateProfileApiV1AuthMePut: (data: UserUpdate, params: RequestParams = {}) =>
    this.request<UpdateProfileApiV1AuthMePutData, HTTPValidationError>({
        path: `/api/v1/auth/me`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Change user password with enhanced security logging. Args: password_data: Password change data request: HTTP request for security logging current_user: Current authenticated user auth_service: Authentication service Returns: Success message
 *
 * @tags Authentication
 * @name ChangePasswordApiV1AuthChangePasswordPost
 * @summary Change Password
 * @request POST:/api/v1/auth/change-password
 * @secure
 */
changePasswordApiV1AuthChangePasswordPost: (data: PasswordChange, params: RequestParams = {}) =>
    this.request<ChangePasswordApiV1AuthChangePasswordPostData, HTTPValidationError>({
        path: `/api/v1/auth/change-password`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Create API key for current user with enhanced security. Args: key_data: API key creation data request: HTTP request for security logging current_user: Current authenticated user auth_service: Authentication service Returns: Created API key
 *
 * @tags Authentication
 * @name CreateApiKeyApiV1AuthApiKeyPost
 * @summary Create Api Key
 * @request POST:/api/v1/auth/api-key
 * @secure
 */
createApiKeyApiV1AuthApiKeyPost: (data: APIKeyCreate, params: RequestParams = {}) =>
    this.request<CreateApiKeyApiV1AuthApiKeyPostData, HTTPValidationError>({
        path: `/api/v1/auth/api-key`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Revoke current user's API key with security logging. Args: request: HTTP request for security logging current_user: Current authenticated user auth_service: Authentication service Returns: Success message
 *
 * @tags Authentication
 * @name RevokeApiKeyApiV1AuthApiKeyDelete
 * @summary Revoke Api Key
 * @request DELETE:/api/v1/auth/api-key
 * @secure
 */
revokeApiKeyApiV1AuthApiKeyDelete: (params: RequestParams = {}) =>
    this.request<RevokeApiKeyApiV1AuthApiKeyDeleteData, any>({
        path: `/api/v1/auth/api-key`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description List user's API keys. Args: current_user: Current authenticated user auth_service: Authentication service Returns: List of API keys
 *
 * @tags Authentication
 * @name ListApiKeysApiV1AuthApiKeysGet
 * @summary List Api Keys
 * @request GET:/api/v1/auth/api-keys
 * @secure
 */
listApiKeysApiV1AuthApiKeysGet: (params: RequestParams = {}) =>
    this.request<ListApiKeysApiV1AuthApiKeysGetData, any>({
        path: `/api/v1/auth/api-keys`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Logout and revoke current token with enhanced security. Args: request: HTTP request for security logging current_user: Current authenticated user auth_service: Authentication service Returns: Success message
 *
 * @tags Authentication
 * @name LogoutApiV1AuthLogoutPost
 * @summary Logout
 * @request POST:/api/v1/auth/logout
 * @secure
 */
logoutApiV1AuthLogoutPost: (params: RequestParams = {}) =>
    this.request<LogoutApiV1AuthLogoutPostData, any>({
        path: `/api/v1/auth/logout`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Request password reset with enhanced security logging. Args: email: User email request: HTTP request for security logging auth_service: Authentication service Returns: Success message
 *
 * @tags Authentication
 * @name RequestPasswordResetApiV1AuthPasswordResetRequestPost
 * @summary Request Password Reset
 * @request POST:/api/v1/auth/password-reset/request
 */
requestPasswordResetApiV1AuthPasswordResetRequestPost: (query: RequestPasswordResetApiV1AuthPasswordResetRequestPostParams, params: RequestParams = {}) =>
    this.request<RequestPasswordResetApiV1AuthPasswordResetRequestPostData, HTTPValidationError>({
        path: `/api/v1/auth/password-reset/request`,
        method: 'POST',
        query: query,                                format: "json",        ...params,
    }),            /**
 * @description Confirm password reset with enhanced security logging. Args: token: Reset token new_password: New password request: HTTP request for security logging auth_service: Authentication service Returns: Success message
 *
 * @tags Authentication
 * @name ConfirmPasswordResetApiV1AuthPasswordResetConfirmPost
 * @summary Confirm Password Reset
 * @request POST:/api/v1/auth/password-reset/confirm
 */
confirmPasswordResetApiV1AuthPasswordResetConfirmPost: (query: ConfirmPasswordResetApiV1AuthPasswordResetConfirmPostParams, params: RequestParams = {}) =>
    this.request<ConfirmPasswordResetApiV1AuthPasswordResetConfirmPostData, HTTPValidationError>({
        path: `/api/v1/auth/password-reset/confirm`,
        method: 'POST',
        query: query,                                format: "json",        ...params,
    }),            /**
 * @description Deactivate current user account with enhanced security logging. Args: request: HTTP request for security logging current_user: Current authenticated user auth_service: Authentication service Returns: Success message
 *
 * @tags Authentication
 * @name DeactivateAccountApiV1AuthAccountDelete
 * @summary Deactivate Account
 * @request DELETE:/api/v1/auth/account
 * @secure
 */
deactivateAccountApiV1AuthAccountDelete: (params: RequestParams = {}) =>
    this.request<DeactivateAccountApiV1AuthAccountDeleteData, any>({
        path: `/api/v1/auth/account`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create a new conversation. Create a new conversation with specified configuration ## Workflow Types This endpoint supports multiple workflow types through the `workflow` parameter: ### Plain Chat (`plain`) Basic conversation without tools or retrieval. ```json { "message": "Hello, how are you?", "workflow": "plain" } ``` ### RAG Workflow (`rag`) Retrieval-Augmented Generation with document search. ```json { "message": "What are the latest sales figures?", "workflow": "rag", "enable_retrieval": true } ``` ### Tools Workflow (`tools`) Function calling with available tools. ```json { "message": "Calculate the square root of 144", "workflow": "tools" } ``` ### Full Workflow (`full`) Combination of RAG and tools for complex tasks. ```json { "message": "Find recent customer feedback and create a summary report", "workflow": "full", "enable_retrieval": true } ``` ## Streaming Set `stream: true` to receive real-time responses: ```json { "message": "Tell me a story", "workflow": "plain", "stream": true } ``` Streaming responses use Server-Sent Events (SSE) format with event types: - `token`: Content chunks - `node_start`: Workflow node started - `node_complete`: Workflow node completed - `usage`: Final usage statistics - `error`: Error occurred ## Templates Use pre-configured templates for common scenarios: ```json { "message": "I need help with my order", "workflow_template": "customer_support" } ``` Available templates: - `customer_support`: Customer service with knowledge base - `code_assistant`: Programming help with code tools - `research_assistant`: Document research and analysis - `general_chat`: General conversation - `document_qa`: Document question answering - `data_analyst`: Data analysis with computation tools
 *
 * @tags Chat
 * @name CreateConversationApiV1ChatConversationsPost
 * @summary Create Conversation
 * @request POST:/api/v1/chat/conversations
 * @secure
 */
createConversationApiV1ChatConversationsPost: (data: ConversationCreate, params: RequestParams = {}) =>
    this.request<CreateConversationApiV1ChatConversationsPostData, HTTPValidationError>({
        path: `/api/v1/chat/conversations`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List conversations for the current user.
 *
 * @tags Chat
 * @name ListConversationsApiV1ChatConversationsGet
 * @summary List Conversations
 * @request GET:/api/v1/chat/conversations
 * @secure
 */
listConversationsApiV1ChatConversationsGet: (query: ListConversationsApiV1ChatConversationsGetParams, params: RequestParams = {}) =>
    this.request<ListConversationsApiV1ChatConversationsGetData, HTTPValidationError>({
        path: `/api/v1/chat/conversations`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get conversation details with optional messages.
 *
 * @tags Chat
 * @name GetConversationApiV1ChatConversationsConversationIdGet
 * @summary Get Conversation
 * @request GET:/api/v1/chat/conversations/{conversation_id}
 * @secure
 */
getConversationApiV1ChatConversationsConversationIdGet: ({ conversationId, ...query }: GetConversationApiV1ChatConversationsConversationIdGetParams, params: RequestParams = {}) =>
    this.request<GetConversationApiV1ChatConversationsConversationIdGetData, HTTPValidationError>({
        path: `/api/v1/chat/conversations/${conversationId}`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update conversation.
 *
 * @tags Chat
 * @name UpdateConversationApiV1ChatConversationsConversationIdPut
 * @summary Update Conversation
 * @request PUT:/api/v1/chat/conversations/{conversation_id}
 * @secure
 */
updateConversationApiV1ChatConversationsConversationIdPut: ({ conversationId, ...query }: UpdateConversationApiV1ChatConversationsConversationIdPutParams, data: ConversationUpdate, params: RequestParams = {}) =>
    this.request<UpdateConversationApiV1ChatConversationsConversationIdPutData, HTTPValidationError>({
        path: `/api/v1/chat/conversations/${conversationId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete conversation.
 *
 * @tags Chat
 * @name DeleteConversationApiV1ChatConversationsConversationIdDelete
 * @summary Delete Conversation
 * @request DELETE:/api/v1/chat/conversations/{conversation_id}
 * @secure
 */
deleteConversationApiV1ChatConversationsConversationIdDelete: ({ conversationId, ...query }: DeleteConversationApiV1ChatConversationsConversationIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteConversationApiV1ChatConversationsConversationIdDeleteData, HTTPValidationError>({
        path: `/api/v1/chat/conversations/${conversationId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get messages from a conversation.
 *
 * @tags Chat
 * @name GetConversationMessagesApiV1ChatConversationsConversationIdMessagesGet
 * @summary Get Conversation Messages
 * @request GET:/api/v1/chat/conversations/{conversation_id}/messages
 * @secure
 */
getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet: ({ conversationId, ...query }: GetConversationMessagesApiV1ChatConversationsConversationIdMessagesGetParams, params: RequestParams = {}) =>
    this.request<GetConversationMessagesApiV1ChatConversationsConversationIdMessagesGetData, HTTPValidationError>({
        path: `/api/v1/chat/conversations/${conversationId}/messages`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Delete a message from a conversation.
 *
 * @tags Chat
 * @name DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete
 * @summary Delete Message
 * @request DELETE:/api/v1/chat/conversations/{conversation_id}/messages/{message_id}
 * @secure
 */
deleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete: ({ conversationId, messageId, ...query }: DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDeleteData, HTTPValidationError>({
        path: `/api/v1/chat/conversations/${conversationId}/messages/${messageId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Unified chat endpoint supporting all workflow types with optional streaming. ## Workflow Types This endpoint supports multiple workflow types through the `workflow` parameter: ### Plain Chat (`plain`) Basic conversation without tools or retrieval. ```json { "message": "Hello, how are you?", "workflow": "plain" } ``` ### RAG Workflow (`rag`) Retrieval-Augmented Generation with document search. ```json { "message": "What are the latest sales figures?", "workflow": "rag", "enable_retrieval": true } ``` ### Tools Workflow (`tools`) Function calling with available tools. ```json { "message": "Calculate the square root of 144", "workflow": "tools" } ``` ### Full Workflow (`full`) Combination of RAG and tools for complex tasks. ```json { "message": "Find recent customer feedback and create a summary report", "workflow": "full", "enable_retrieval": true } ``` ## Streaming Set `stream: true` to receive real-time responses: ```json { "message": "Tell me a story", "workflow": "plain", "stream": true } ``` Streaming responses use Server-Sent Events (SSE) format with event types: - `token`: Content chunks - `node_start`: Workflow node started - `node_complete`: Workflow node completed - `usage`: Final usage statistics - `error`: Error occurred ## Templates Use pre-configured templates for common scenarios: ```json { "message": "I need help with my order", "workflow_template": "customer_support" } ``` Available templates: - `customer_support`: Customer service with knowledge base - `code_assistant`: Programming help with code tools - `research_assistant`: Document research and analysis - `general_chat`: General conversation - `document_qa`: Document question answering - `data_analyst`: Data analysis with computation tools
 *
 * @tags Chat
 * @name ChatApiV1ChatChatPost
 * @summary Chat
 * @request POST:/api/v1/chat/chat
 * @secure
 */
chatApiV1ChatChatPost: (data: ChatRequest, params: RequestParams = {}) =>
    this.request<ChatApiV1ChatChatPostData, HTTPValidationError>({
        path: `/api/v1/chat/chat`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get list of available MCP tools.
 *
 * @tags Chat
 * @name GetAvailableToolsApiV1ChatToolsAvailableGet
 * @summary Get Available Tools
 * @request GET:/api/v1/chat/tools/available
 * @secure
 */
getAvailableToolsApiV1ChatToolsAvailableGet: (params: RequestParams = {}) =>
    this.request<GetAvailableToolsApiV1ChatToolsAvailableGetData, any>({
        path: `/api/v1/chat/tools/available`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get available workflow templates.
 *
 * @tags Chat
 * @name GetWorkflowTemplatesApiV1ChatTemplatesGet
 * @summary Get Workflow Templates
 * @request GET:/api/v1/chat/templates
 * @secure
 */
getWorkflowTemplatesApiV1ChatTemplatesGet: (params: RequestParams = {}) =>
    this.request<GetWorkflowTemplatesApiV1ChatTemplatesGetData, any>({
        path: `/api/v1/chat/templates`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Chat using a specific workflow template. ## Workflow Types This endpoint supports multiple workflow types through the `workflow` parameter: ### Plain Chat (`plain`) Basic conversation without tools or retrieval. ```json { "message": "Hello, how are you?", "workflow": "plain" } ``` ### RAG Workflow (`rag`) Retrieval-Augmented Generation with document search. ```json { "message": "What are the latest sales figures?", "workflow": "rag", "enable_retrieval": true } ``` ### Tools Workflow (`tools`) Function calling with available tools. ```json { "message": "Calculate the square root of 144", "workflow": "tools" } ``` ### Full Workflow (`full`) Combination of RAG and tools for complex tasks. ```json { "message": "Find recent customer feedback and create a summary report", "workflow": "full", "enable_retrieval": true } ``` ## Streaming Set `stream: true` to receive real-time responses: ```json { "message": "Tell me a story", "workflow": "plain", "stream": true } ``` Streaming responses use Server-Sent Events (SSE) format with event types: - `token`: Content chunks - `node_start`: Workflow node started - `node_complete`: Workflow node completed - `usage`: Final usage statistics - `error`: Error occurred ## Templates Use pre-configured templates for common scenarios: ```json { "message": "I need help with my order", "workflow_template": "customer_support" } ``` Available templates: - `customer_support`: Customer service with knowledge base - `code_assistant`: Programming help with code tools - `research_assistant`: Document research and analysis - `general_chat`: General conversation - `document_qa`: Document question answering - `data_analyst`: Data analysis with computation tools
 *
 * @tags Chat
 * @name ChatWithTemplateApiV1ChatTemplateTemplateNamePost
 * @summary Chat With Template
 * @request POST:/api/v1/chat/template/{template_name}
 * @secure
 */
chatWithTemplateApiV1ChatTemplateTemplateNamePost: ({ templateName, ...query }: ChatWithTemplateApiV1ChatTemplateTemplateNamePostParams, data: ChatRequest, params: RequestParams = {}) =>
    this.request<ChatWithTemplateApiV1ChatTemplateTemplateNamePostData, HTTPValidationError>({
        path: `/api/v1/chat/template/${templateName}`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get workflow performance statistics.
 *
 * @tags Chat
 * @name GetPerformanceStatsApiV1ChatPerformanceStatsGet
 * @summary Get Performance Stats
 * @request GET:/api/v1/chat/performance/stats
 * @secure
 */
getPerformanceStatsApiV1ChatPerformanceStatsGet: (params: RequestParams = {}) =>
    this.request<GetPerformanceStatsApiV1ChatPerformanceStatsGetData, any>({
        path: `/api/v1/chat/performance/stats`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get MCP service status.
 *
 * @tags Chat
 * @name GetMcpStatusApiV1ChatMcpStatusGet
 * @summary Get Mcp Status
 * @request GET:/api/v1/chat/mcp/status
 * @secure
 */
getMcpStatusApiV1ChatMcpStatusGet: (params: RequestParams = {}) =>
    this.request<GetMcpStatusApiV1ChatMcpStatusGetData, any>({
        path: `/api/v1/chat/mcp/status`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Upload a document. Args: file: Document file to upload title: Document title description: Document description tags: Document tags (JSON array string) chunk_size: Text chunk size for processing chunk_overlap: Text chunk overlap is_public: Whether document is public current_user: Current authenticated user document_service: Document service Returns: Created document information
 *
 * @tags Documents
 * @name UploadDocumentApiV1DocumentsUploadPost
 * @summary Upload Document
 * @request POST:/api/v1/documents/upload
 * @secure
 */
uploadDocumentApiV1DocumentsUploadPost: (data: BodyUploadDocumentApiV1DocumentsUploadPost, params: RequestParams = {}) =>
    this.request<UploadDocumentApiV1DocumentsUploadPostData, HTTPValidationError>({
        path: `/api/v1/documents/upload`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.FormData,        format: "json",        ...params,
    }),            /**
 * @description List user's documents. Args: status: Filter by document status document_type: Filter by document type tags: Filter by tags owner_id: Filter by owner (admin only) limit: Maximum number of results offset: Number of results to skip sort_by: Sort field sort_order: Sort order (asc/desc) current_user: Current authenticated user document_service: Document service Returns: List of documents with pagination info
 *
 * @tags Documents
 * @name ListDocumentsApiV1DocumentsGet
 * @summary List Documents
 * @request GET:/api/v1/documents
 * @secure
 */
listDocumentsApiV1DocumentsGet: (query: ListDocumentsApiV1DocumentsGetParams, params: RequestParams = {}) =>
    this.request<ListDocumentsApiV1DocumentsGetData, void>({
        path: `/api/v1/documents`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get document details. Args: document_id: Document ID current_user: Current authenticated user document_service: Document service Returns: Document information
 *
 * @tags Documents
 * @name GetDocumentApiV1DocumentsDocumentIdGet
 * @summary Get Document
 * @request GET:/api/v1/documents/{document_id}
 * @secure
 */
getDocumentApiV1DocumentsDocumentIdGet: ({ documentId, ...query }: GetDocumentApiV1DocumentsDocumentIdGetParams, params: RequestParams = {}) =>
    this.request<GetDocumentApiV1DocumentsDocumentIdGetData, void>({
        path: `/api/v1/documents/${documentId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update document metadata. Args: document_id: Document ID update_data: Update data current_user: Current authenticated user document_service: Document service Returns: Updated document information
 *
 * @tags Documents
 * @name UpdateDocumentApiV1DocumentsDocumentIdPut
 * @summary Update Document
 * @request PUT:/api/v1/documents/{document_id}
 * @secure
 */
updateDocumentApiV1DocumentsDocumentIdPut: ({ documentId, ...query }: UpdateDocumentApiV1DocumentsDocumentIdPutParams, data: DocumentUpdate, params: RequestParams = {}) =>
    this.request<UpdateDocumentApiV1DocumentsDocumentIdPutData, HTTPValidationError>({
        path: `/api/v1/documents/${documentId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete document. Args: document_id: Document ID request: Delete request parameters current_user: Current authenticated user document_service: Document service Returns: Success message
 *
 * @tags Documents
 * @name DeleteDocumentApiV1DocumentsDocumentIdDelete
 * @summary Delete Document
 * @request DELETE:/api/v1/documents/{document_id}
 * @secure
 */
deleteDocumentApiV1DocumentsDocumentIdDelete: ({ documentId, ...query }: DeleteDocumentApiV1DocumentsDocumentIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteDocumentApiV1DocumentsDocumentIdDeleteData, HTTPValidationError>({
        path: `/api/v1/documents/${documentId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Search documents using vector similarity. Args: search_request: Search request current_user: Current authenticated user document_service: Document service Returns: Search results
 *
 * @tags Documents
 * @name SearchDocumentsApiV1DocumentsSearchPost
 * @summary Search Documents
 * @request POST:/api/v1/documents/search
 * @secure
 */
searchDocumentsApiV1DocumentsSearchPost: (data: DocumentSearchRequest, params: RequestParams = {}) =>
    this.request<SearchDocumentsApiV1DocumentsSearchPostData, HTTPValidationError>({
        path: `/api/v1/documents/search`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get document chunks. Args: document_id: Document ID limit: Maximum number of results offset: Number of results to skip current_user: Current authenticated user document_service: Document service Returns: List of document chunks with pagination
 *
 * @tags Documents
 * @name GetDocumentChunksApiV1DocumentsDocumentIdChunksGet
 * @summary Get Document Chunks
 * @request GET:/api/v1/documents/{document_id}/chunks
 * @secure
 */
getDocumentChunksApiV1DocumentsDocumentIdChunksGet: ({ documentId, ...query }: GetDocumentChunksApiV1DocumentsDocumentIdChunksGetParams, params: RequestParams = {}) =>
    this.request<GetDocumentChunksApiV1DocumentsDocumentIdChunksGetData, HTTPValidationError>({
        path: `/api/v1/documents/${documentId}/chunks`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Trigger document processing. Args: document_id: Document ID processing_request: Processing request current_user: Current authenticated user document_service: Document service Returns: Processing status
 *
 * @tags Documents
 * @name ProcessDocumentApiV1DocumentsDocumentIdProcessPost
 * @summary Process Document
 * @request POST:/api/v1/documents/{document_id}/process
 * @secure
 */
processDocumentApiV1DocumentsDocumentIdProcessPost: ({ documentId, ...query }: ProcessDocumentApiV1DocumentsDocumentIdProcessPostParams, data: DocumentProcessingRequest, params: RequestParams = {}) =>
    this.request<ProcessDocumentApiV1DocumentsDocumentIdProcessPostData, HTTPValidationError>({
        path: `/api/v1/documents/${documentId}/process`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get document statistics. Args: current_user: Current authenticated user document_service: Document service Returns: Document statistics
 *
 * @tags Documents
 * @name GetDocumentStatsApiV1DocumentsStatsOverviewGet
 * @summary Get Document Stats
 * @request GET:/api/v1/documents/stats/overview
 * @secure
 */
getDocumentStatsApiV1DocumentsStatsOverviewGet: (params: RequestParams = {}) =>
    this.request<GetDocumentStatsApiV1DocumentsStatsOverviewGetData, any>({
        path: `/api/v1/documents/stats/overview`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Download original document file. Args: document_id: Document ID current_user: Current authenticated user document_service: Document service Returns: File download response
 *
 * @tags Documents
 * @name DownloadDocumentApiV1DocumentsDocumentIdDownloadGet
 * @summary Download Document
 * @request GET:/api/v1/documents/{document_id}/download
 * @secure
 */
downloadDocumentApiV1DocumentsDocumentIdDownloadGet: ({ documentId, ...query }: DownloadDocumentApiV1DocumentsDocumentIdDownloadGetParams, params: RequestParams = {}) =>
    this.request<DownloadDocumentApiV1DocumentsDocumentIdDownloadGetData, HTTPValidationError>({
        path: `/api/v1/documents/${documentId}/download`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Reprocess an existing document. Args: document_id: Document ID current_user: Current authenticated user document_service: Document service Returns: Processing status
 *
 * @tags Documents
 * @name ReprocessDocumentApiV1DocumentsDocumentIdReprocessPost
 * @summary Reprocess Document
 * @request POST:/api/v1/documents/{document_id}/reprocess
 * @secure
 */
reprocessDocumentApiV1DocumentsDocumentIdReprocessPost: ({ documentId, ...query }: ReprocessDocumentApiV1DocumentsDocumentIdReprocessPostParams, params: RequestParams = {}) =>
    this.request<ReprocessDocumentApiV1DocumentsDocumentIdReprocessPostData, HTTPValidationError>({
        path: `/api/v1/documents/${documentId}/reprocess`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create a new LLM profile. Args: profile_data: Profile creation data current_user: Current authenticated user profile_service: Profile service Returns: Created profile information
 *
 * @tags Profiles
 * @name CreateProfileApiV1ProfilesPost
 * @summary Create Profile
 * @request POST:/api/v1/profiles/
 * @secure
 */
createProfileApiV1ProfilesPost: (data: ProfileCreate, params: RequestParams = {}) =>
    this.request<CreateProfileApiV1ProfilesPostData, HTTPValidationError>({
        path: `/api/v1/profiles/`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List user's profiles. Args: profile_type: Filter by profile type llm_provider: Filter by LLM provider tags: Filter by tags is_public: Filter by public status limit: Maximum number of results offset: Number of results to skip sort_by: Sort field sort_order: Sort order (asc/desc) current_user: Current authenticated user profile_service: Profile service Returns: List of profiles with pagination info
 *
 * @tags Profiles
 * @name ListProfilesApiV1ProfilesGet
 * @summary List Profiles
 * @request GET:/api/v1/profiles
 * @secure
 */
listProfilesApiV1ProfilesGet: (query: ListProfilesApiV1ProfilesGetParams, params: RequestParams = {}) =>
    this.request<ListProfilesApiV1ProfilesGetData, HTTPValidationError>({
        path: `/api/v1/profiles`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get profile details. Args: profile_id: Profile ID current_user: Current authenticated user profile_service: Profile service Returns: Profile information
 *
 * @tags Profiles
 * @name GetProfileApiV1ProfilesProfileIdGet
 * @summary Get Profile
 * @request GET:/api/v1/profiles/{profile_id}
 * @secure
 */
getProfileApiV1ProfilesProfileIdGet: ({ profileId, ...query }: GetProfileApiV1ProfilesProfileIdGetParams, params: RequestParams = {}) =>
    this.request<GetProfileApiV1ProfilesProfileIdGetData, HTTPValidationError>({
        path: `/api/v1/profiles/${profileId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update profile. Args: profile_id: Profile ID update_data: Update data current_user: Current authenticated user profile_service: Profile service Returns: Updated profile information
 *
 * @tags Profiles
 * @name UpdateProfileApiV1ProfilesProfileIdPut
 * @summary Update Profile
 * @request PUT:/api/v1/profiles/{profile_id}
 * @secure
 */
updateProfileApiV1ProfilesProfileIdPut: ({ profileId, ...query }: UpdateProfileApiV1ProfilesProfileIdPutParams, data: ProfileUpdate, params: RequestParams = {}) =>
    this.request<UpdateProfileApiV1ProfilesProfileIdPutData, HTTPValidationError>({
        path: `/api/v1/profiles/${profileId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete profile. Args: profile_id: Profile ID request: Delete request parameters current_user: Current authenticated user profile_service: Profile service Returns: Success message
 *
 * @tags Profiles
 * @name DeleteProfileApiV1ProfilesProfileIdDelete
 * @summary Delete Profile
 * @request DELETE:/api/v1/profiles/{profile_id}
 * @secure
 */
deleteProfileApiV1ProfilesProfileIdDelete: ({ profileId, ...query }: DeleteProfileApiV1ProfilesProfileIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteProfileApiV1ProfilesProfileIdDeleteData, HTTPValidationError>({
        path: `/api/v1/profiles/${profileId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Test profile with a sample message. Args: profile_id: Profile ID test_request: Test request current_user: Current authenticated user profile_service: Profile service Returns: Test results
 *
 * @tags Profiles
 * @name TestProfileApiV1ProfilesProfileIdTestPost
 * @summary Test Profile
 * @request POST:/api/v1/profiles/{profile_id}/test
 * @secure
 */
testProfileApiV1ProfilesProfileIdTestPost: ({ profileId, ...query }: TestProfileApiV1ProfilesProfileIdTestPostParams, data: ProfileTestRequest, params: RequestParams = {}) =>
    this.request<TestProfileApiV1ProfilesProfileIdTestPostData, HTTPValidationError>({
        path: `/api/v1/profiles/${profileId}/test`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Clone an existing profile. Args: profile_id: Source profile ID clone_request: Clone request current_user: Current authenticated user profile_service: Profile service Returns: Cloned profile information
 *
 * @tags Profiles
 * @name CloneProfileApiV1ProfilesProfileIdClonePost
 * @summary Clone Profile
 * @request POST:/api/v1/profiles/{profile_id}/clone
 * @secure
 */
cloneProfileApiV1ProfilesProfileIdClonePost: ({ profileId, ...query }: CloneProfileApiV1ProfilesProfileIdClonePostParams, data: ProfileCloneRequest, params: RequestParams = {}) =>
    this.request<CloneProfileApiV1ProfilesProfileIdClonePostData, HTTPValidationError>({
        path: `/api/v1/profiles/${profileId}/clone`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get profile statistics. Args: current_user: Current authenticated user profile_service: Profile service Returns: Profile statistics
 *
 * @tags Profiles
 * @name GetProfileStatsApiV1ProfilesStatsOverviewGet
 * @summary Get Profile Stats
 * @request GET:/api/v1/profiles/stats/overview
 * @secure
 */
getProfileStatsApiV1ProfilesStatsOverviewGet: (params: RequestParams = {}) =>
    this.request<GetProfileStatsApiV1ProfilesStatsOverviewGetData, any>({
        path: `/api/v1/profiles/stats/overview`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get available LLM providers. Args: request: Providers request parameters current_user: Current authenticated user profile_service: Profile service Returns: Available providers information
 *
 * @tags Profiles
 * @name GetAvailableProvidersApiV1ProfilesProvidersAvailableGet
 * @summary Get Available Providers
 * @request GET:/api/v1/profiles/providers/available
 * @secure
 */
getAvailableProvidersApiV1ProfilesProvidersAvailableGet: (params: RequestParams = {}) =>
    this.request<GetAvailableProvidersApiV1ProfilesProvidersAvailableGetData, any>({
        path: `/api/v1/profiles/providers/available`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create a new prompt. Args: prompt_data: Prompt creation data current_user: Current authenticated user prompt_service: Prompt service Returns: Created prompt information
 *
 * @tags Prompts
 * @name CreatePromptApiV1PromptsPost
 * @summary Create Prompt
 * @request POST:/api/v1/prompts/
 * @secure
 */
createPromptApiV1PromptsPost: (data: PromptCreate, params: RequestParams = {}) =>
    this.request<CreatePromptApiV1PromptsPostData, HTTPValidationError>({
        path: `/api/v1/prompts/`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get prompt statistics. Args: current_user: Current authenticated user prompt_service: Prompt service Returns: Prompt statistics
 *
 * @tags Prompts
 * @name GetPromptStatsApiV1PromptsStatsOverviewGet
 * @summary Get Prompt Stats
 * @request GET:/api/v1/prompts/stats/overview
 * @secure
 */
getPromptStatsApiV1PromptsStatsOverviewGet: (params: RequestParams = {}) =>
    this.request<GetPromptStatsApiV1PromptsStatsOverviewGetData, any>({
        path: `/api/v1/prompts/stats/overview`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description List user's prompts. Args: prompt_type: Filter by prompt type category: Filter by category tags: Filter by tags is_public: Filter by public status is_chain: Filter by chain status limit: Maximum number of results offset: Number of results to skip sort_by: Sort field sort_order: Sort order (asc/desc) current_user: Current authenticated user prompt_service: Prompt service Returns: List of prompts with pagination info
 *
 * @tags Prompts
 * @name ListPromptsApiV1PromptsGet
 * @summary List Prompts
 * @request GET:/api/v1/prompts
 * @secure
 */
listPromptsApiV1PromptsGet: (query: ListPromptsApiV1PromptsGetParams, params: RequestParams = {}) =>
    this.request<ListPromptsApiV1PromptsGetData, HTTPValidationError>({
        path: `/api/v1/prompts`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get prompt details. Args: prompt_id: Prompt ID request: Get request parameters current_user: Current authenticated user prompt_service: Prompt service Returns: Prompt information
 *
 * @tags Prompts
 * @name GetPromptApiV1PromptsPromptIdGet
 * @summary Get Prompt
 * @request GET:/api/v1/prompts/{prompt_id}
 * @secure
 */
getPromptApiV1PromptsPromptIdGet: ({ promptId, ...query }: GetPromptApiV1PromptsPromptIdGetParams, params: RequestParams = {}) =>
    this.request<GetPromptApiV1PromptsPromptIdGetData, HTTPValidationError>({
        path: `/api/v1/prompts/${promptId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update prompt. Args: prompt_id: Prompt ID update_data: Update data current_user: Current authenticated user prompt_service: Prompt service Returns: Updated prompt information
 *
 * @tags Prompts
 * @name UpdatePromptApiV1PromptsPromptIdPut
 * @summary Update Prompt
 * @request PUT:/api/v1/prompts/{prompt_id}
 * @secure
 */
updatePromptApiV1PromptsPromptIdPut: ({ promptId, ...query }: UpdatePromptApiV1PromptsPromptIdPutParams, data: PromptUpdate, params: RequestParams = {}) =>
    this.request<UpdatePromptApiV1PromptsPromptIdPutData, HTTPValidationError>({
        path: `/api/v1/prompts/${promptId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete prompt. Args: prompt_id: Prompt ID request: Delete request parameters current_user: Current authenticated user prompt_service: Prompt service Returns: Success message
 *
 * @tags Prompts
 * @name DeletePromptApiV1PromptsPromptIdDelete
 * @summary Delete Prompt
 * @request DELETE:/api/v1/prompts/{prompt_id}
 * @secure
 */
deletePromptApiV1PromptsPromptIdDelete: ({ promptId, ...query }: DeletePromptApiV1PromptsPromptIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeletePromptApiV1PromptsPromptIdDeleteData, HTTPValidationError>({
        path: `/api/v1/prompts/${promptId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Test prompt with given variables. Args: prompt_id: Prompt ID test_request: Test request current_user: Current authenticated user prompt_service: Prompt service Returns: Test results
 *
 * @tags Prompts
 * @name TestPromptApiV1PromptsPromptIdTestPost
 * @summary Test Prompt
 * @request POST:/api/v1/prompts/{prompt_id}/test
 * @secure
 */
testPromptApiV1PromptsPromptIdTestPost: ({ promptId, ...query }: TestPromptApiV1PromptsPromptIdTestPostParams, data: PromptTestRequest, params: RequestParams = {}) =>
    this.request<TestPromptApiV1PromptsPromptIdTestPostData, HTTPValidationError>({
        path: `/api/v1/prompts/${promptId}/test`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Clone an existing prompt. Args: prompt_id: Source prompt ID clone_request: Clone request current_user: Current authenticated user prompt_service: Prompt service Returns: Cloned prompt information
 *
 * @tags Prompts
 * @name ClonePromptApiV1PromptsPromptIdClonePost
 * @summary Clone Prompt
 * @request POST:/api/v1/prompts/{prompt_id}/clone
 * @secure
 */
clonePromptApiV1PromptsPromptIdClonePost: ({ promptId, ...query }: ClonePromptApiV1PromptsPromptIdClonePostParams, data: PromptCloneRequest, params: RequestParams = {}) =>
    this.request<ClonePromptApiV1PromptsPromptIdClonePostData, HTTPValidationError>({
        path: `/api/v1/prompts/${promptId}/clone`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get conversation statistics. Args: start_date: Start date for analytics end_date: End date for analytics period: Predefined period current_user: Current authenticated user analytics_service: Analytics service Returns: Conversation statistics
 *
 * @tags Analytics
 * @name GetConversationStatsApiV1AnalyticsConversationsGet
 * @summary Get Conversation Stats
 * @request GET:/api/v1/analytics/conversations
 * @secure
 */
getConversationStatsApiV1AnalyticsConversationsGet: (query: GetConversationStatsApiV1AnalyticsConversationsGetParams, params: RequestParams = {}) =>
    this.request<GetConversationStatsApiV1AnalyticsConversationsGetData, HTTPValidationError>({
        path: `/api/v1/analytics/conversations`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get usage metrics. Args: start_date: Start date for analytics end_date: End date for analytics period: Predefined period current_user: Current authenticated user analytics_service: Analytics service Returns: Usage metrics
 *
 * @tags Analytics
 * @name GetUsageMetricsApiV1AnalyticsUsageGet
 * @summary Get Usage Metrics
 * @request GET:/api/v1/analytics/usage
 * @secure
 */
getUsageMetricsApiV1AnalyticsUsageGet: (query: GetUsageMetricsApiV1AnalyticsUsageGetParams, params: RequestParams = {}) =>
    this.request<GetUsageMetricsApiV1AnalyticsUsageGetData, HTTPValidationError>({
        path: `/api/v1/analytics/usage`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get performance metrics. Args: request: Performance metrics request parameters current_user: Current authenticated user analytics_service: Analytics service Returns: Performance metrics
 *
 * @tags Analytics
 * @name GetPerformanceMetricsApiV1AnalyticsPerformanceGet
 * @summary Get Performance Metrics
 * @request GET:/api/v1/analytics/performance
 * @secure
 */
getPerformanceMetricsApiV1AnalyticsPerformanceGet: (query: GetPerformanceMetricsApiV1AnalyticsPerformanceGetParams, params: RequestParams = {}) =>
    this.request<GetPerformanceMetricsApiV1AnalyticsPerformanceGetData, HTTPValidationError>({
        path: `/api/v1/analytics/performance`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get document analytics. Args: request: Document analytics request parameters current_user: Current authenticated user analytics_service: Analytics service Returns: Document analytics
 *
 * @tags Analytics
 * @name GetDocumentAnalyticsApiV1AnalyticsDocumentsGet
 * @summary Get Document Analytics
 * @request GET:/api/v1/analytics/documents
 * @secure
 */
getDocumentAnalyticsApiV1AnalyticsDocumentsGet: (query: GetDocumentAnalyticsApiV1AnalyticsDocumentsGetParams, params: RequestParams = {}) =>
    this.request<GetDocumentAnalyticsApiV1AnalyticsDocumentsGetData, HTTPValidationError>({
        path: `/api/v1/analytics/documents`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get system analytics. Args: request: System analytics request parameters current_user: Current authenticated user analytics_service: Analytics service Returns: System analytics
 *
 * @tags Analytics
 * @name GetSystemAnalyticsApiV1AnalyticsSystemGet
 * @summary Get System Analytics
 * @request GET:/api/v1/analytics/system
 * @secure
 */
getSystemAnalyticsApiV1AnalyticsSystemGet: (params: RequestParams = {}) =>
    this.request<GetSystemAnalyticsApiV1AnalyticsSystemGetData, any>({
        path: `/api/v1/analytics/system`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get comprehensive dashboard data. Args: request: Dashboard request parameters current_user: Current authenticated user analytics_service: Analytics service Returns: Complete dashboard data
 *
 * @tags Analytics
 * @name GetDashboardApiV1AnalyticsDashboardGet
 * @summary Get Dashboard
 * @request GET:/api/v1/analytics/dashboard
 * @secure
 */
getDashboardApiV1AnalyticsDashboardGet: (query: GetDashboardApiV1AnalyticsDashboardGetParams, params: RequestParams = {}) =>
    this.request<GetDashboardApiV1AnalyticsDashboardGetData, HTTPValidationError>({
        path: `/api/v1/analytics/dashboard`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get tool server analytics. Args: request: Tool server analytics request parameters current_user: Current authenticated user analytics_service: Analytics service Returns: Tool server analytics data
 *
 * @tags Analytics
 * @name GetToolServerAnalyticsApiV1AnalyticsToolserversGet
 * @summary Get Tool Server Analytics
 * @request GET:/api/v1/analytics/toolservers
 * @secure
 */
getToolServerAnalyticsApiV1AnalyticsToolserversGet: (query: GetToolServerAnalyticsApiV1AnalyticsToolserversGetParams, params: RequestParams = {}) =>
    this.request<GetToolServerAnalyticsApiV1AnalyticsToolserversGetData, HTTPValidationError>({
        path: `/api/v1/analytics/toolservers`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get per-user analytics. Args: user_id: User ID start_date: Start date for analytics end_date: End date for analytics period: Predefined period current_user: Current authenticated user analytics_service: Analytics service Returns: User-specific analytics
 *
 * @tags Analytics
 * @name GetUserAnalyticsApiV1AnalyticsUsersUserIdGet
 * @summary Get User Analytics
 * @request GET:/api/v1/analytics/users/{user_id}
 * @secure
 */
getUserAnalyticsApiV1AnalyticsUsersUserIdGet: ({ userId, ...query }: GetUserAnalyticsApiV1AnalyticsUsersUserIdGetParams, params: RequestParams = {}) =>
    this.request<GetUserAnalyticsApiV1AnalyticsUsersUserIdGetData, HTTPValidationError>({
        path: `/api/v1/analytics/users/${userId}`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Export analytics reports. Args: format: Export format metrics: List of metrics to export start_date: Start date for analytics end_date: End date for analytics period: Predefined period current_user: Current authenticated user analytics_service: Analytics service Returns: Exported analytics report
 *
 * @tags Analytics
 * @name ExportAnalyticsApiV1AnalyticsExportPost
 * @summary Export Analytics
 * @request POST:/api/v1/analytics/export
 * @secure
 */
exportAnalyticsApiV1AnalyticsExportPost: (query: ExportAnalyticsApiV1AnalyticsExportPostParams, params: RequestParams = {}) =>
    this.request<ExportAnalyticsApiV1AnalyticsExportPostData, HTTPValidationError>({
        path: `/api/v1/analytics/export`,
        method: 'POST',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get analytics system health status. Returns: Health check results for analytics system
 *
 * @tags Analytics
 * @name GetAnalyticsHealthApiV1AnalyticsHealthGet
 * @summary Get Analytics Health
 * @request GET:/api/v1/analytics/health
 * @secure
 */
getAnalyticsHealthApiV1AnalyticsHealthGet: (params: RequestParams = {}) =>
    this.request<GetAnalyticsHealthApiV1AnalyticsHealthGetData, any>({
        path: `/api/v1/analytics/health`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get summary of key analytics metrics for monitoring. Returns: Summary of analytics metrics
 *
 * @tags Analytics
 * @name GetAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummaryGet
 * @summary Get Analytics Metrics Summary
 * @request GET:/api/v1/analytics/metrics/summary
 * @secure
 */
getAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummaryGet: (params: RequestParams = {}) =>
    this.request<GetAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummaryGetData, any>({
        path: `/api/v1/analytics/metrics/summary`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description List all workflow definitions for the current user.
 *
 * @tags Workflows, workflows
 * @name ListWorkflowDefinitionsApiV1WorkflowsWorkflowsDefinitionsGet
 * @summary List Workflow Definitions
 * @request GET:/api/v1/workflows/workflows/definitions
 * @secure
 */
listWorkflowDefinitionsApiV1WorkflowsWorkflowsDefinitionsGet: (params: RequestParams = {}) =>
    this.request<ListWorkflowDefinitionsApiV1WorkflowsWorkflowsDefinitionsGetData, any>({
        path: `/api/v1/workflows/workflows/definitions`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create a new workflow definition.
 *
 * @tags Workflows, workflows
 * @name CreateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsPost
 * @summary Create Workflow Definition
 * @request POST:/api/v1/workflows/workflows/definitions
 * @secure
 */
createWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsPost: (data: WorkflowDefinitionCreate, params: RequestParams = {}) =>
    this.request<CreateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsPostData, HTTPValidationError>({
        path: `/api/v1/workflows/workflows/definitions`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get a specific workflow definition.
 *
 * @tags Workflows, workflows
 * @name GetWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdGet
 * @summary Get Workflow Definition
 * @request GET:/api/v1/workflows/workflows/definitions/{workflow_id}
 * @secure
 */
getWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdGet: ({ workflowId, ...query }: GetWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdGetParams, params: RequestParams = {}) =>
    this.request<GetWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdGetData, HTTPValidationError>({
        path: `/api/v1/workflows/workflows/definitions/${workflowId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update a workflow definition.
 *
 * @tags Workflows, workflows
 * @name UpdateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdPut
 * @summary Update Workflow Definition
 * @request PUT:/api/v1/workflows/workflows/definitions/{workflow_id}
 * @secure
 */
updateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdPut: ({ workflowId, ...query }: UpdateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdPutParams, data: WorkflowDefinitionUpdate, params: RequestParams = {}) =>
    this.request<UpdateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdPutData, HTTPValidationError>({
        path: `/api/v1/workflows/workflows/definitions/${workflowId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete a workflow definition.
 *
 * @tags Workflows, workflows
 * @name DeleteWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdDelete
 * @summary Delete Workflow Definition
 * @request DELETE:/api/v1/workflows/workflows/definitions/{workflow_id}
 * @secure
 */
deleteWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdDelete: ({ workflowId, ...query }: DeleteWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsWorkflowIdDeleteData, HTTPValidationError>({
        path: `/api/v1/workflows/workflows/definitions/${workflowId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description List all workflow templates accessible to the current user.
 *
 * @tags Workflows, workflows
 * @name ListWorkflowTemplatesApiV1WorkflowsWorkflowsTemplatesGet
 * @summary List Workflow Templates
 * @request GET:/api/v1/workflows/workflows/templates
 * @secure
 */
listWorkflowTemplatesApiV1WorkflowsWorkflowsTemplatesGet: (params: RequestParams = {}) =>
    this.request<ListWorkflowTemplatesApiV1WorkflowsWorkflowsTemplatesGetData, any>({
        path: `/api/v1/workflows/workflows/templates`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create a new workflow template.
 *
 * @tags Workflows, workflows
 * @name CreateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesPost
 * @summary Create Workflow Template
 * @request POST:/api/v1/workflows/workflows/templates
 * @secure
 */
createWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesPost: (data: WorkflowTemplateCreate, params: RequestParams = {}) =>
    this.request<CreateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesPostData, HTTPValidationError>({
        path: `/api/v1/workflows/workflows/templates`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Update a workflow template.
 *
 * @tags Workflows, workflows
 * @name UpdateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesTemplateIdPut
 * @summary Update Workflow Template
 * @request PUT:/api/v1/workflows/workflows/templates/{template_id}
 * @secure
 */
updateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesTemplateIdPut: ({ templateId, ...query }: UpdateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesTemplateIdPutParams, data: WorkflowTemplateUpdate, params: RequestParams = {}) =>
    this.request<UpdateWorkflowTemplateApiV1WorkflowsWorkflowsTemplatesTemplateIdPutData, HTTPValidationError>({
        path: `/api/v1/workflows/workflows/templates/${templateId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get analytics for a specific workflow definition.
 *
 * @tags Workflows, workflows
 * @name GetWorkflowAnalyticsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdAnalyticsGet
 * @summary Get Workflow Analytics
 * @request GET:/api/v1/workflows/workflows/definitions/{workflow_id}/analytics
 * @secure
 */
getWorkflowAnalyticsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdAnalyticsGet: ({ workflowId, ...query }: GetWorkflowAnalyticsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdAnalyticsGetParams, params: RequestParams = {}) =>
    this.request<GetWorkflowAnalyticsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdAnalyticsGetData, HTTPValidationError>({
        path: `/api/v1/workflows/workflows/definitions/${workflowId}/analytics`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Execute a workflow definition.
 *
 * @tags Workflows, workflows
 * @name ExecuteWorkflowApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutePost
 * @summary Execute Workflow
 * @request POST:/api/v1/workflows/workflows/definitions/{workflow_id}/execute
 * @secure
 */
executeWorkflowApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutePost: ({ workflowId, ...query }: ExecuteWorkflowApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutePostParams, data: WorkflowExecutionRequest, params: RequestParams = {}) =>
    this.request<ExecuteWorkflowApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutePostData, HTTPValidationError>({
        path: `/api/v1/workflows/workflows/definitions/${workflowId}/execute`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Validate a workflow definition.
 *
 * @tags Workflows, workflows
 * @name ValidateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsValidatePost
 * @summary Validate Workflow Definition
 * @request POST:/api/v1/workflows/workflows/definitions/validate
 * @secure
 */
validateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsValidatePost: (data: WorkflowDefinitionCreate, params: RequestParams = {}) =>
    this.request<ValidateWorkflowDefinitionApiV1WorkflowsWorkflowsDefinitionsValidatePostData, HTTPValidationError>({
        path: `/api/v1/workflows/workflows/definitions/validate`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get list of supported workflow node types.
 *
 * @tags Workflows, workflows
 * @name GetSupportedNodeTypesApiV1WorkflowsWorkflowsNodeTypesGet
 * @summary Get Supported Node Types
 * @request GET:/api/v1/workflows/workflows/node-types
 * @secure
 */
getSupportedNodeTypesApiV1WorkflowsWorkflowsNodeTypesGet: (params: RequestParams = {}) =>
    this.request<GetSupportedNodeTypesApiV1WorkflowsWorkflowsNodeTypesGetData, any>({
        path: `/api/v1/workflows/workflows/node-types`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description List executions for a workflow definition.
 *
 * @tags Workflows, workflows
 * @name ListWorkflowExecutionsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutionsGet
 * @summary List Workflow Executions
 * @request GET:/api/v1/workflows/workflows/definitions/{workflow_id}/executions
 * @secure
 */
listWorkflowExecutionsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutionsGet: ({ workflowId, ...query }: ListWorkflowExecutionsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutionsGetParams, params: RequestParams = {}) =>
    this.request<ListWorkflowExecutionsApiV1WorkflowsWorkflowsDefinitionsWorkflowIdExecutionsGetData, HTTPValidationError>({
        path: `/api/v1/workflows/workflows/definitions/${workflowId}/executions`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create a new tool server. Args: server_data: Server creation data current_user: Current authenticated user service: Tool server service Returns: Created server response
 *
 * @tags Tool Servers
 * @name CreateToolServerApiV1ToolserversServersPost
 * @summary Create Tool Server
 * @request POST:/api/v1/toolservers/servers
 * @secure
 */
createToolServerApiV1ToolserversServersPost: (data: ToolServerCreate, params: RequestParams = {}) =>
    this.request<CreateToolServerApiV1ToolserversServersPostData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List tool servers with optional filtering. Args: request: List request with filter parameters current_user: Current authenticated user service: Tool server service Returns: List of server responses
 *
 * @tags Tool Servers
 * @name ListToolServersApiV1ToolserversServersGet
 * @summary List Tool Servers
 * @request GET:/api/v1/toolservers/servers
 * @secure
 */
listToolServersApiV1ToolserversServersGet: (query: ListToolServersApiV1ToolserversServersGetParams, params: RequestParams = {}) =>
    this.request<ListToolServersApiV1ToolserversServersGetData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get a tool server by ID. Args: server_id: Server ID current_user: Current authenticated user service: Tool server service Returns: Server response
 *
 * @tags Tool Servers
 * @name GetToolServerApiV1ToolserversServersServerIdGet
 * @summary Get Tool Server
 * @request GET:/api/v1/toolservers/servers/{server_id}
 * @secure
 */
getToolServerApiV1ToolserversServersServerIdGet: ({ serverId, ...query }: GetToolServerApiV1ToolserversServersServerIdGetParams, params: RequestParams = {}) =>
    this.request<GetToolServerApiV1ToolserversServersServerIdGetData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update a tool server. Args: server_id: Server ID update_data: Update data current_user: Current authenticated user service: Tool server service Returns: Updated server response
 *
 * @tags Tool Servers
 * @name UpdateToolServerApiV1ToolserversServersServerIdPut
 * @summary Update Tool Server
 * @request PUT:/api/v1/toolservers/servers/{server_id}
 * @secure
 */
updateToolServerApiV1ToolserversServersServerIdPut: ({ serverId, ...query }: UpdateToolServerApiV1ToolserversServersServerIdPutParams, data: ToolServerUpdate, params: RequestParams = {}) =>
    this.request<UpdateToolServerApiV1ToolserversServersServerIdPutData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete a tool server. Args: server_id: Server ID current_user: Current authenticated user service: Tool server service Returns: Success message
 *
 * @tags Tool Servers
 * @name DeleteToolServerApiV1ToolserversServersServerIdDelete
 * @summary Delete Tool Server
 * @request DELETE:/api/v1/toolservers/servers/{server_id}
 * @secure
 */
deleteToolServerApiV1ToolserversServersServerIdDelete: ({ serverId, ...query }: DeleteToolServerApiV1ToolserversServersServerIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteToolServerApiV1ToolserversServersServerIdDeleteData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Start a tool server. Args: server_id: Server ID current_user: Current authenticated user service: Tool server service Returns: Operation result
 *
 * @tags Tool Servers
 * @name StartToolServerApiV1ToolserversServersServerIdStartPost
 * @summary Start Tool Server
 * @request POST:/api/v1/toolservers/servers/{server_id}/start
 * @secure
 */
startToolServerApiV1ToolserversServersServerIdStartPost: ({ serverId, ...query }: StartToolServerApiV1ToolserversServersServerIdStartPostParams, params: RequestParams = {}) =>
    this.request<StartToolServerApiV1ToolserversServersServerIdStartPostData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}/start`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Stop a tool server. Args: server_id: Server ID current_user: Current authenticated user service: Tool server service Returns: Operation result
 *
 * @tags Tool Servers
 * @name StopToolServerApiV1ToolserversServersServerIdStopPost
 * @summary Stop Tool Server
 * @request POST:/api/v1/toolservers/servers/{server_id}/stop
 * @secure
 */
stopToolServerApiV1ToolserversServersServerIdStopPost: ({ serverId, ...query }: StopToolServerApiV1ToolserversServersServerIdStopPostParams, params: RequestParams = {}) =>
    this.request<StopToolServerApiV1ToolserversServersServerIdStopPostData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}/stop`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Restart a tool server. Args: server_id: Server ID current_user: Current authenticated user service: Tool server service Returns: Operation result
 *
 * @tags Tool Servers
 * @name RestartToolServerApiV1ToolserversServersServerIdRestartPost
 * @summary Restart Tool Server
 * @request POST:/api/v1/toolservers/servers/{server_id}/restart
 * @secure
 */
restartToolServerApiV1ToolserversServersServerIdRestartPost: ({ serverId, ...query }: RestartToolServerApiV1ToolserversServersServerIdRestartPostParams, params: RequestParams = {}) =>
    this.request<RestartToolServerApiV1ToolserversServersServerIdRestartPostData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}/restart`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Enable a tool server. Args: server_id: Server ID current_user: Current authenticated user service: Tool server service Returns: Operation result
 *
 * @tags Tool Servers
 * @name EnableToolServerApiV1ToolserversServersServerIdEnablePost
 * @summary Enable Tool Server
 * @request POST:/api/v1/toolservers/servers/{server_id}/enable
 * @secure
 */
enableToolServerApiV1ToolserversServersServerIdEnablePost: ({ serverId, ...query }: EnableToolServerApiV1ToolserversServersServerIdEnablePostParams, params: RequestParams = {}) =>
    this.request<EnableToolServerApiV1ToolserversServersServerIdEnablePostData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}/enable`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Disable a tool server. Args: server_id: Server ID current_user: Current authenticated user service: Tool server service Returns: Operation result
 *
 * @tags Tool Servers
 * @name DisableToolServerApiV1ToolserversServersServerIdDisablePost
 * @summary Disable Tool Server
 * @request POST:/api/v1/toolservers/servers/{server_id}/disable
 * @secure
 */
disableToolServerApiV1ToolserversServersServerIdDisablePost: ({ serverId, ...query }: DisableToolServerApiV1ToolserversServersServerIdDisablePostParams, params: RequestParams = {}) =>
    this.request<DisableToolServerApiV1ToolserversServersServerIdDisablePostData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}/disable`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get tools for a specific server. Args: server_id: Server ID request: Server tools request with pagination current_user: Current authenticated user service: Tool server service Returns: List of server tools with pagination
 *
 * @tags Tool Servers
 * @name GetServerToolsApiV1ToolserversServersServerIdToolsGet
 * @summary Get Server Tools
 * @request GET:/api/v1/toolservers/servers/{server_id}/tools
 * @secure
 */
getServerToolsApiV1ToolserversServersServerIdToolsGet: ({ serverId, ...query }: GetServerToolsApiV1ToolserversServersServerIdToolsGetParams, params: RequestParams = {}) =>
    this.request<GetServerToolsApiV1ToolserversServersServerIdToolsGetData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}/tools`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Enable a specific tool. Args: tool_id: Tool ID current_user: Current authenticated user service: Tool server service Returns: Operation result
 *
 * @tags Tool Servers
 * @name EnableToolApiV1ToolserversToolsToolIdEnablePost
 * @summary Enable Tool
 * @request POST:/api/v1/toolservers/tools/{tool_id}/enable
 * @secure
 */
enableToolApiV1ToolserversToolsToolIdEnablePost: ({ toolId, ...query }: EnableToolApiV1ToolserversToolsToolIdEnablePostParams, params: RequestParams = {}) =>
    this.request<EnableToolApiV1ToolserversToolsToolIdEnablePostData, HTTPValidationError>({
        path: `/api/v1/toolservers/tools/${toolId}/enable`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Disable a specific tool. Args: tool_id: Tool ID current_user: Current authenticated user service: Tool server service Returns: Operation result
 *
 * @tags Tool Servers
 * @name DisableToolApiV1ToolserversToolsToolIdDisablePost
 * @summary Disable Tool
 * @request POST:/api/v1/toolservers/tools/{tool_id}/disable
 * @secure
 */
disableToolApiV1ToolserversToolsToolIdDisablePost: ({ toolId, ...query }: DisableToolApiV1ToolserversToolsToolIdDisablePostParams, params: RequestParams = {}) =>
    this.request<DisableToolApiV1ToolserversToolsToolIdDisablePostData, HTTPValidationError>({
        path: `/api/v1/toolservers/tools/${toolId}/disable`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get analytics for a specific server. Args: server_id: Server ID current_user: Current authenticated user service: Tool server service Returns: Server metrics
 *
 * @tags Tool Servers
 * @name GetServerMetricsApiV1ToolserversServersServerIdMetricsGet
 * @summary Get Server Metrics
 * @request GET:/api/v1/toolservers/servers/{server_id}/metrics
 * @secure
 */
getServerMetricsApiV1ToolserversServersServerIdMetricsGet: ({ serverId, ...query }: GetServerMetricsApiV1ToolserversServersServerIdMetricsGetParams, params: RequestParams = {}) =>
    this.request<GetServerMetricsApiV1ToolserversServersServerIdMetricsGetData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}/metrics`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Perform health check on a server. Args: server_id: Server ID current_user: Current authenticated user service: Tool server service Returns: Health check result
 *
 * @tags Tool Servers
 * @name CheckServerHealthApiV1ToolserversServersServerIdHealthGet
 * @summary Check Server Health
 * @request GET:/api/v1/toolservers/servers/{server_id}/health
 * @secure
 */
checkServerHealthApiV1ToolserversServersServerIdHealthGet: ({ serverId, ...query }: CheckServerHealthApiV1ToolserversServersServerIdHealthGetParams, params: RequestParams = {}) =>
    this.request<CheckServerHealthApiV1ToolserversServersServerIdHealthGetData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}/health`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Perform bulk operations on multiple servers. Args: operation_data: Bulk operation data current_user: Current authenticated user service: Tool server service Returns: Bulk operation result
 *
 * @tags Tool Servers
 * @name BulkServerOperationApiV1ToolserversServersBulkPost
 * @summary Bulk Server Operation
 * @request POST:/api/v1/toolservers/servers/bulk
 * @secure
 */
bulkServerOperationApiV1ToolserversServersBulkPost: (data: BulkToolServerOperation, params: RequestParams = {}) =>
    this.request<BulkServerOperationApiV1ToolserversServersBulkPostData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/bulk`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List all tools across all servers. Args: current_user: Current authenticated user tool_server_service: Tool server service Returns: List of all available tools across all servers
 *
 * @tags Tool Servers
 * @name ListAllToolsApiV1ToolserversToolsAllGet
 * @summary List All Tools
 * @request GET:/api/v1/toolservers/tools/all
 * @secure
 */
listAllToolsApiV1ToolserversToolsAllGet: (params: RequestParams = {}) =>
    this.request<ListAllToolsApiV1ToolserversToolsAllGetData, any>({
        path: `/api/v1/toolservers/tools/all`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Test connectivity to an external MCP server. Args: server_id: Tool server ID current_user: Current authenticated user tool_server_service: Tool server service Returns: Connectivity test results
 *
 * @tags Tool Servers
 * @name TestServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPost
 * @summary Test Server Connectivity
 * @request POST:/api/v1/toolservers/servers/{server_id}/test-connectivity
 * @secure
 */
testServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPost: ({ serverId, ...query }: TestServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPostParams, params: RequestParams = {}) =>
    this.request<TestServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPostData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}/test-connectivity`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Grant tool permission to a user. Args: permission_data: Permission data current_user: Current authenticated user access_service: Tool access service Returns: Created permission
 *
 * @tags Tool Servers
 * @name GrantToolPermissionApiV1ToolserversPermissionsPost
 * @summary Grant Tool Permission
 * @request POST:/api/v1/toolservers/permissions
 * @secure
 */
grantToolPermissionApiV1ToolserversPermissionsPost: (data: ToolPermissionCreate, params: RequestParams = {}) =>
    this.request<GrantToolPermissionApiV1ToolserversPermissionsPostData, HTTPValidationError>({
        path: `/api/v1/toolservers/permissions`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Update tool permission. Args: permission_id: Permission ID update_data: Update data current_user: Current authenticated user access_service: Tool access service Returns: Updated permission
 *
 * @tags Tool Servers
 * @name UpdateToolPermissionApiV1ToolserversPermissionsPermissionIdPut
 * @summary Update Tool Permission
 * @request PUT:/api/v1/toolservers/permissions/{permission_id}
 * @secure
 */
updateToolPermissionApiV1ToolserversPermissionsPermissionIdPut: ({ permissionId, ...query }: UpdateToolPermissionApiV1ToolserversPermissionsPermissionIdPutParams, data: ToolPermissionUpdate, params: RequestParams = {}) =>
    this.request<UpdateToolPermissionApiV1ToolserversPermissionsPermissionIdPutData, HTTPValidationError>({
        path: `/api/v1/toolservers/permissions/${permissionId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Revoke tool permission. Args: permission_id: Permission ID current_user: Current authenticated user access_service: Tool access service Returns: Success message
 *
 * @tags Tool Servers
 * @name RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete
 * @summary Revoke Tool Permission
 * @request DELETE:/api/v1/toolservers/permissions/{permission_id}
 * @secure
 */
revokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete: ({ permissionId, ...query }: RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteParams, params: RequestParams = {}) =>
    this.request<RevokeToolPermissionApiV1ToolserversPermissionsPermissionIdDeleteData, HTTPValidationError>({
        path: `/api/v1/toolservers/permissions/${permissionId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get all permissions for a user. Args: user_id: User ID current_user: Current authenticated user access_service: Tool access service Returns: List of user permissions
 *
 * @tags Tool Servers
 * @name GetUserPermissionsApiV1ToolserversUsersUserIdPermissionsGet
 * @summary Get User Permissions
 * @request GET:/api/v1/toolservers/users/{user_id}/permissions
 * @secure
 */
getUserPermissionsApiV1ToolserversUsersUserIdPermissionsGet: ({ userId, ...query }: GetUserPermissionsApiV1ToolserversUsersUserIdPermissionsGetParams, params: RequestParams = {}) =>
    this.request<GetUserPermissionsApiV1ToolserversUsersUserIdPermissionsGetData, HTTPValidationError>({
        path: `/api/v1/toolservers/users/${userId}/permissions`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create role-based access rule. Args: rule_data: Rule data current_user: Current authenticated user access_service: Tool access service Returns: Created rule
 *
 * @tags Tool Servers
 * @name CreateRoleAccessRuleApiV1ToolserversRoleAccessPost
 * @summary Create Role Access Rule
 * @request POST:/api/v1/toolservers/role-access
 * @secure
 */
createRoleAccessRuleApiV1ToolserversRoleAccessPost: (data: RoleToolAccessCreate, params: RequestParams = {}) =>
    this.request<CreateRoleAccessRuleApiV1ToolserversRoleAccessPostData, HTTPValidationError>({
        path: `/api/v1/toolservers/role-access`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get role-based access rules. Args: role: Optional role filter current_user: Current authenticated user access_service: Tool access service Returns: List of access rules
 *
 * @tags Tool Servers
 * @name GetRoleAccessRulesApiV1ToolserversRoleAccessGet
 * @summary Get Role Access Rules
 * @request GET:/api/v1/toolservers/role-access
 * @secure
 */
getRoleAccessRulesApiV1ToolserversRoleAccessGet: (query: GetRoleAccessRulesApiV1ToolserversRoleAccessGetParams, params: RequestParams = {}) =>
    this.request<GetRoleAccessRulesApiV1ToolserversRoleAccessGetData, HTTPValidationError>({
        path: `/api/v1/toolservers/role-access`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Check if user has access to a tool. Args: check_data: Access check data current_user: Current authenticated user access_service: Tool access service Returns: Access check result
 *
 * @tags Tool Servers
 * @name CheckToolAccessApiV1ToolserversAccessCheckPost
 * @summary Check Tool Access
 * @request POST:/api/v1/toolservers/access-check
 * @secure
 */
checkToolAccessApiV1ToolserversAccessCheckPost: (data: UserToolAccessCheck, params: RequestParams = {}) =>
    this.request<CheckToolAccessApiV1ToolserversAccessCheckPostData, HTTPValidationError>({
        path: `/api/v1/toolservers/access-check`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Refresh tools for a remote server. Args: server_id: Server ID current_user: Current authenticated user service: Tool server service Returns: Refresh result
 *
 * @tags Tool Servers
 * @name RefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPost
 * @summary Refresh Server Tools
 * @request POST:/api/v1/toolservers/servers/{server_id}/refresh-tools
 * @secure
 */
refreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPost: ({ serverId, ...query }: RefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPostParams, params: RequestParams = {}) =>
    this.request<RefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPostData, HTTPValidationError>({
        path: `/api/v1/toolservers/servers/${serverId}/refresh-tools`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create a new AI agent with specified configuration and capabilities.
 *
 * @tags Agents, agents
 * @name CreateAgentApiV1AgentsPost
 * @summary Create a new agent
 * @request POST:/api/v1/agents/
 * @secure
 */
createAgentApiV1AgentsPost: (data: AgentCreateRequest, params: RequestParams = {}) =>
    this.request<CreateAgentApiV1AgentsPostData, void | HTTPValidationError>({
        path: `/api/v1/agents/`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List all agents with optional filtering and pagination. Users can only see their own agents.
 *
 * @tags Agents, agents
 * @name ListAgentsApiV1AgentsGet
 * @summary List agents
 * @request GET:/api/v1/agents/
 * @secure
 */
listAgentsApiV1AgentsGet: (query: ListAgentsApiV1AgentsGetParams, data: BodyListAgentsApiV1AgentsGet, params: RequestParams = {}) =>
    this.request<ListAgentsApiV1AgentsGetData, void | HTTPValidationError>({
        path: `/api/v1/agents/`,
        method: 'GET',
        query: query,        body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get predefined agent templates for common use cases.
 *
 * @tags Agents, agents
 * @name GetAgentTemplatesApiV1AgentsTemplatesGet
 * @summary Get agent templates
 * @request GET:/api/v1/agents/templates
 * @secure
 */
getAgentTemplatesApiV1AgentsTemplatesGet: (params: RequestParams = {}) =>
    this.request<GetAgentTemplatesApiV1AgentsTemplatesGetData, void>({
        path: `/api/v1/agents/templates`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get comprehensive statistics about all agents for the current user.
 *
 * @tags Agents, agents
 * @name GetAgentStatsApiV1AgentsStatsOverviewGet
 * @summary Get agent statistics
 * @request GET:/api/v1/agents/stats/overview
 * @secure
 */
getAgentStatsApiV1AgentsStatsOverviewGet: (params: RequestParams = {}) =>
    this.request<GetAgentStatsApiV1AgentsStatsOverviewGetData, void>({
        path: `/api/v1/agents/stats/overview`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get agent by ID. Args: agent_id: Agent ID request: Get request parameters current_user: Current authenticated user agent_manager: Agent manager instance Returns: Agent data
 *
 * @tags Agents, agents
 * @name GetAgentApiV1AgentsAgentIdGet
 * @summary Get Agent
 * @request GET:/api/v1/agents/{agent_id}
 * @secure
 */
getAgentApiV1AgentsAgentIdGet: ({ agentId, ...query }: GetAgentApiV1AgentsAgentIdGetParams, params: RequestParams = {}) =>
    this.request<GetAgentApiV1AgentsAgentIdGetData, void | HTTPValidationError>({
        path: `/api/v1/agents/${agentId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update an agent. Args: agent_id: Agent ID agent_data: Agent update data current_user: Current authenticated user agent_manager: Agent manager instance Returns: Updated agent data
 *
 * @tags Agents, agents
 * @name UpdateAgentApiV1AgentsAgentIdPut
 * @summary Update Agent
 * @request PUT:/api/v1/agents/{agent_id}
 * @secure
 */
updateAgentApiV1AgentsAgentIdPut: ({ agentId, ...query }: UpdateAgentApiV1AgentsAgentIdPutParams, data: AgentUpdateRequest, params: RequestParams = {}) =>
    this.request<UpdateAgentApiV1AgentsAgentIdPutData, void | HTTPValidationError>({
        path: `/api/v1/agents/${agentId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete an agent. Args: agent_id: Agent ID current_user: Current authenticated user agent_manager: Agent manager instance Returns: Deletion result
 *
 * @tags Agents, agents
 * @name DeleteAgentApiV1AgentsAgentIdDelete
 * @summary Delete Agent
 * @request DELETE:/api/v1/agents/{agent_id}
 * @secure
 */
deleteAgentApiV1AgentsAgentIdDelete: ({ agentId, ...query }: DeleteAgentApiV1AgentsAgentIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteAgentApiV1AgentsAgentIdDeleteData, void | HTTPValidationError>({
        path: `/api/v1/agents/${agentId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Send a message to an agent and receive a response. Rate limited per user per agent.
 *
 * @tags Agents, agents
 * @name InteractWithAgentApiV1AgentsAgentIdInteractPost
 * @summary Interact with agent
 * @request POST:/api/v1/agents/{agent_id}/interact
 * @secure
 */
interactWithAgentApiV1AgentsAgentIdInteractPost: ({ agentId, ...query }: InteractWithAgentApiV1AgentsAgentIdInteractPostParams, data: AgentInteractRequest, params: RequestParams = {}) =>
    this.request<InteractWithAgentApiV1AgentsAgentIdInteractPostData, void | HTTPValidationError>({
        path: `/api/v1/agents/${agentId}/interact`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get agent health status. Args: agent_id: Agent ID current_user: Current authenticated user agent_manager: Agent manager instance Returns: Agent health information
 *
 * @tags Agents, agents
 * @name GetAgentHealthApiV1AgentsAgentIdHealthGet
 * @summary Get Agent Health
 * @request GET:/api/v1/agents/{agent_id}/health
 * @secure
 */
getAgentHealthApiV1AgentsAgentIdHealthGet: ({ agentId, ...query }: GetAgentHealthApiV1AgentsAgentIdHealthGetParams, params: RequestParams = {}) =>
    this.request<GetAgentHealthApiV1AgentsAgentIdHealthGetData, void | HTTPValidationError>({
        path: `/api/v1/agents/${agentId}/health`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create multiple agents in bulk. Args: request: Bulk creation request current_user: Current authenticated user agent_manager: Agent manager instance Returns: Bulk creation results
 *
 * @tags Agents, agents
 * @name BulkCreateAgentsApiV1AgentsBulkPost
 * @summary Bulk Create Agents
 * @request POST:/api/v1/agents/bulk
 * @secure
 */
bulkCreateAgentsApiV1AgentsBulkPost: (data: AgentBulkCreateRequest, params: RequestParams = {}) =>
    this.request<BulkCreateAgentsApiV1AgentsBulkPostData, void | HTTPValidationError>({
        path: `/api/v1/agents/bulk`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete multiple agents in bulk. Args: request: Bulk deletion request current_user: Current authenticated user agent_manager: Agent manager instance Returns: Bulk deletion results
 *
 * @tags Agents, agents
 * @name BulkDeleteAgentsApiV1AgentsBulkDelete
 * @summary Bulk Delete Agents
 * @request DELETE:/api/v1/agents/bulk
 * @secure
 */
bulkDeleteAgentsApiV1AgentsBulkDelete: (data: AgentBulkDeleteRequest, params: RequestParams = {}) =>
    this.request<BulkDeleteAgentsApiV1AgentsBulkDeleteData, void | HTTPValidationError>({
        path: `/api/v1/agents/bulk`,
        method: 'DELETE',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Create a new A/B test. Args: test_data: A/B test creation data current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Created test data
 *
 * @tags A/B Testing
 * @name CreateAbTestApiV1AbTestsPost
 * @summary Create Ab Test
 * @request POST:/api/v1/ab-tests/
 * @secure
 */
createAbTestApiV1AbTestsPost: (data: ABTestCreateRequest, params: RequestParams = {}) =>
    this.request<CreateAbTestApiV1AbTestsPostData, HTTPValidationError>({
        path: `/api/v1/ab-tests/`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List A/B tests with optional filtering. Args: request: List request parameters current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: List of A/B tests
 *
 * @tags A/B Testing
 * @name ListAbTestsApiV1AbTestsGet
 * @summary List Ab Tests
 * @request GET:/api/v1/ab-tests/
 * @secure
 */
listAbTestsApiV1AbTestsGet: (query: ListAbTestsApiV1AbTestsGetParams, data: ListAbTestsApiV1AbTestsGetPayload, params: RequestParams = {}) =>
    this.request<ListAbTestsApiV1AbTestsGetData, HTTPValidationError>({
        path: `/api/v1/ab-tests/`,
        method: 'GET',
        query: query,        body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get A/B test by ID. Args: test_id: Test ID current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: A/B test data
 *
 * @tags A/B Testing
 * @name GetAbTestApiV1AbTestsTestIdGet
 * @summary Get Ab Test
 * @request GET:/api/v1/ab-tests/{test_id}
 * @secure
 */
getAbTestApiV1AbTestsTestIdGet: ({ testId, ...query }: GetAbTestApiV1AbTestsTestIdGetParams, params: RequestParams = {}) =>
    this.request<GetAbTestApiV1AbTestsTestIdGetData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update an A/B test. Args: test_id: Test ID test_data: Test update data current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Updated test data
 *
 * @tags A/B Testing
 * @name UpdateAbTestApiV1AbTestsTestIdPut
 * @summary Update Ab Test
 * @request PUT:/api/v1/ab-tests/{test_id}
 * @secure
 */
updateAbTestApiV1AbTestsTestIdPut: ({ testId, ...query }: UpdateAbTestApiV1AbTestsTestIdPutParams, data: ABTestUpdateRequest, params: RequestParams = {}) =>
    this.request<UpdateAbTestApiV1AbTestsTestIdPutData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete an A/B test. Args: test_id: Test ID current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Deletion result
 *
 * @tags A/B Testing
 * @name DeleteAbTestApiV1AbTestsTestIdDelete
 * @summary Delete Ab Test
 * @request DELETE:/api/v1/ab-tests/{test_id}
 * @secure
 */
deleteAbTestApiV1AbTestsTestIdDelete: ({ testId, ...query }: DeleteAbTestApiV1AbTestsTestIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteAbTestApiV1AbTestsTestIdDeleteData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Start an A/B test. Args: test_id: Test ID current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Action result
 *
 * @tags A/B Testing
 * @name StartAbTestApiV1AbTestsTestIdStartPost
 * @summary Start Ab Test
 * @request POST:/api/v1/ab-tests/{test_id}/start
 * @secure
 */
startAbTestApiV1AbTestsTestIdStartPost: ({ testId, ...query }: StartAbTestApiV1AbTestsTestIdStartPostParams, params: RequestParams = {}) =>
    this.request<StartAbTestApiV1AbTestsTestIdStartPostData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}/start`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Pause an A/B test. Args: test_id: Test ID current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Action result
 *
 * @tags A/B Testing
 * @name PauseAbTestApiV1AbTestsTestIdPausePost
 * @summary Pause Ab Test
 * @request POST:/api/v1/ab-tests/{test_id}/pause
 * @secure
 */
pauseAbTestApiV1AbTestsTestIdPausePost: ({ testId, ...query }: PauseAbTestApiV1AbTestsTestIdPausePostParams, params: RequestParams = {}) =>
    this.request<PauseAbTestApiV1AbTestsTestIdPausePostData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}/pause`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Complete an A/B test. Args: test_id: Test ID current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Action result
 *
 * @tags A/B Testing
 * @name CompleteAbTestApiV1AbTestsTestIdCompletePost
 * @summary Complete Ab Test
 * @request POST:/api/v1/ab-tests/{test_id}/complete
 * @secure
 */
completeAbTestApiV1AbTestsTestIdCompletePost: ({ testId, ...query }: CompleteAbTestApiV1AbTestsTestIdCompletePostParams, params: RequestParams = {}) =>
    this.request<CompleteAbTestApiV1AbTestsTestIdCompletePostData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}/complete`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get A/B test results and analysis. Args: test_id: Test ID current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Test results and analysis
 *
 * @tags A/B Testing
 * @name GetAbTestResultsApiV1AbTestsTestIdResultsGet
 * @summary Get Ab Test Results
 * @request GET:/api/v1/ab-tests/{test_id}/results
 * @secure
 */
getAbTestResultsApiV1AbTestsTestIdResultsGet: ({ testId, ...query }: GetAbTestResultsApiV1AbTestsTestIdResultsGetParams, params: RequestParams = {}) =>
    this.request<GetAbTestResultsApiV1AbTestsTestIdResultsGetData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}/results`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get current A/B test metrics. Args: test_id: Test ID current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Current test metrics
 *
 * @tags A/B Testing
 * @name GetAbTestMetricsApiV1AbTestsTestIdMetricsGet
 * @summary Get Ab Test Metrics
 * @request GET:/api/v1/ab-tests/{test_id}/metrics
 * @secure
 */
getAbTestMetricsApiV1AbTestsTestIdMetricsGet: ({ testId, ...query }: GetAbTestMetricsApiV1AbTestsTestIdMetricsGetParams, params: RequestParams = {}) =>
    this.request<GetAbTestMetricsApiV1AbTestsTestIdMetricsGetData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}/metrics`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description End A/B test and declare winner. Args: test_id: A/B test ID winner_variant: Winning variant identifier current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Action response
 *
 * @tags A/B Testing
 * @name EndAbTestApiV1AbTestsTestIdEndPost
 * @summary End Ab Test
 * @request POST:/api/v1/ab-tests/{test_id}/end
 * @secure
 */
endAbTestApiV1AbTestsTestIdEndPost: ({ testId, ...query }: EndAbTestApiV1AbTestsTestIdEndPostParams, params: RequestParams = {}) =>
    this.request<EndAbTestApiV1AbTestsTestIdEndPostData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}/end`,
        method: 'POST',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get A/B test performance results by variant. Args: test_id: A/B test ID current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Performance results per variant
 *
 * @tags A/B Testing
 * @name GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGet
 * @summary Get Ab Test Performance
 * @request GET:/api/v1/ab-tests/{test_id}/performance
 * @secure
 */
getAbTestPerformanceApiV1AbTestsTestIdPerformanceGet: ({ testId, ...query }: GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetParams, params: RequestParams = {}) =>
    this.request<GetAbTestPerformanceApiV1AbTestsTestIdPerformanceGetData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}/performance`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get comprehensive recommendations for an A/B test. Args: test_id: A/B test ID current_user: Current authenticated user ab_test_manager: A/B test manager instance Returns: Recommendations and insights for the test
 *
 * @tags A/B Testing
 * @name GetAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGet
 * @summary Get Ab Test Recommendations
 * @request GET:/api/v1/ab-tests/{test_id}/recommendations
 * @secure
 */
getAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGet: ({ testId, ...query }: GetAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGetParams, params: RequestParams = {}) =>
    this.request<GetAbTestRecommendationsApiV1AbTestsTestIdRecommendationsGetData, HTTPValidationError>({
        path: `/api/v1/ab-tests/${testId}/recommendations`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Stream real-time events via Server-Sent Events. Args: request: FastAPI request object current_user: Current authenticated user Returns: StreamingResponse with SSE format
 *
 * @tags Events
 * @name EventsStreamApiV1EventsStreamGet
 * @summary Events Stream
 * @request GET:/api/v1/events/stream
 * @secure
 */
eventsStreamApiV1EventsStreamGet: (params: RequestParams = {}) =>
    this.request<EventsStreamApiV1EventsStreamGetData, any>({
        path: `/api/v1/events/stream`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Stream all system events for admin users. Args: request: FastAPI request object current_user: Current authenticated admin user Returns: StreamingResponse with SSE format for all events
 *
 * @tags Events
 * @name AdminEventsStreamApiV1EventsAdminStreamGet
 * @summary Admin Events Stream
 * @request GET:/api/v1/events/admin/stream
 * @secure
 */
adminEventsStreamApiV1EventsAdminStreamGet: (params: RequestParams = {}) =>
    this.request<AdminEventsStreamApiV1EventsAdminStreamGetData, any>({
        path: `/api/v1/events/admin/stream`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get SSE service statistics. Args: current_user: Current authenticated admin user Returns: SSE service statistics
 *
 * @tags Events
 * @name GetSseStatsApiV1EventsStatsGet
 * @summary Get Sse Stats
 * @request GET:/api/v1/events/stats
 * @secure
 */
getSseStatsApiV1EventsStatsGet: (params: RequestParams = {}) =>
    this.request<GetSseStatsApiV1EventsStatsGetData, any>({
        path: `/api/v1/events/stats`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Trigger a test event for the current user. Args: current_user: Current authenticated user Returns: Success message with event ID
 *
 * @tags Events
 * @name TriggerTestEventApiV1EventsTestEventPost
 * @summary Trigger Test Event
 * @request POST:/api/v1/events/test-event
 * @secure
 */
triggerTestEventApiV1EventsTestEventPost: (params: RequestParams = {}) =>
    this.request<TriggerTestEventApiV1EventsTestEventPostData, any>({
        path: `/api/v1/events/test-event`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Trigger a broadcast test event for all users. Args: current_user: Current authenticated admin user Returns: Success message with event ID
 *
 * @tags Events
 * @name TriggerBroadcastTestApiV1EventsBroadcastTestPost
 * @summary Trigger Broadcast Test
 * @request POST:/api/v1/events/broadcast-test
 * @secure
 */
triggerBroadcastTestApiV1EventsBroadcastTestPost: (params: RequestParams = {}) =>
    this.request<TriggerBroadcastTestApiV1EventsBroadcastTestPostData, any>({
        path: `/api/v1/events/broadcast-test`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Install a new plugin. Args: install_data: Plugin installation data current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Installed plugin data
 *
 * @tags Plugins
 * @name InstallPluginApiV1PluginsInstallPost
 * @summary Install Plugin
 * @request POST:/api/v1/plugins/install
 * @secure
 */
installPluginApiV1PluginsInstallPost: (data: PluginInstallRequest, params: RequestParams = {}) =>
    this.request<InstallPluginApiV1PluginsInstallPostData, HTTPValidationError>({
        path: `/api/v1/plugins/install`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List installed plugins with optional filtering. Args: request: List request parameters current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: List of installed plugins
 *
 * @tags Plugins
 * @name ListPluginsApiV1PluginsGet
 * @summary List Plugins
 * @request GET:/api/v1/plugins/
 * @secure
 */
listPluginsApiV1PluginsGet: (query: ListPluginsApiV1PluginsGetParams, params: RequestParams = {}) =>
    this.request<ListPluginsApiV1PluginsGetData, HTTPValidationError>({
        path: `/api/v1/plugins/`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get plugin by ID. Args: plugin_id: Plugin ID current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Plugin data
 *
 * @tags Plugins
 * @name GetPluginApiV1PluginsPluginIdGet
 * @summary Get Plugin
 * @request GET:/api/v1/plugins/{plugin_id}
 * @secure
 */
getPluginApiV1PluginsPluginIdGet: ({ pluginId, ...query }: GetPluginApiV1PluginsPluginIdGetParams, params: RequestParams = {}) =>
    this.request<GetPluginApiV1PluginsPluginIdGetData, HTTPValidationError>({
        path: `/api/v1/plugins/${pluginId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update a plugin. Args: plugin_id: Plugin ID update_data: Plugin update data current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Updated plugin data
 *
 * @tags Plugins
 * @name UpdatePluginApiV1PluginsPluginIdPut
 * @summary Update Plugin
 * @request PUT:/api/v1/plugins/{plugin_id}
 * @secure
 */
updatePluginApiV1PluginsPluginIdPut: ({ pluginId, ...query }: UpdatePluginApiV1PluginsPluginIdPutParams, data: PluginUpdateRequest, params: RequestParams = {}) =>
    this.request<UpdatePluginApiV1PluginsPluginIdPutData, HTTPValidationError>({
        path: `/api/v1/plugins/${pluginId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Uninstall a plugin. Args: plugin_id: Plugin ID current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Uninstall result
 *
 * @tags Plugins
 * @name UninstallPluginApiV1PluginsPluginIdDelete
 * @summary Uninstall Plugin
 * @request DELETE:/api/v1/plugins/{plugin_id}
 * @secure
 */
uninstallPluginApiV1PluginsPluginIdDelete: ({ pluginId, ...query }: UninstallPluginApiV1PluginsPluginIdDeleteParams, params: RequestParams = {}) =>
    this.request<UninstallPluginApiV1PluginsPluginIdDeleteData, HTTPValidationError>({
        path: `/api/v1/plugins/${pluginId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Enable a plugin. Args: plugin_id: Plugin ID current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Action result
 *
 * @tags Plugins
 * @name EnablePluginApiV1PluginsPluginIdEnablePost
 * @summary Enable Plugin
 * @request POST:/api/v1/plugins/{plugin_id}/enable
 * @secure
 */
enablePluginApiV1PluginsPluginIdEnablePost: ({ pluginId, ...query }: EnablePluginApiV1PluginsPluginIdEnablePostParams, params: RequestParams = {}) =>
    this.request<EnablePluginApiV1PluginsPluginIdEnablePostData, HTTPValidationError>({
        path: `/api/v1/plugins/${pluginId}/enable`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Disable a plugin. Args: plugin_id: Plugin ID current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Action result
 *
 * @tags Plugins
 * @name DisablePluginApiV1PluginsPluginIdDisablePost
 * @summary Disable Plugin
 * @request POST:/api/v1/plugins/{plugin_id}/disable
 * @secure
 */
disablePluginApiV1PluginsPluginIdDisablePost: ({ pluginId, ...query }: DisablePluginApiV1PluginsPluginIdDisablePostParams, params: RequestParams = {}) =>
    this.request<DisablePluginApiV1PluginsPluginIdDisablePostData, HTTPValidationError>({
        path: `/api/v1/plugins/${pluginId}/disable`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Perform health check on all plugins. Args: auto_disable_unhealthy: Whether to automatically disable unhealthy plugins current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Health check results
 *
 * @tags Plugins
 * @name HealthCheckPluginsApiV1PluginsHealthGet
 * @summary Health Check Plugins
 * @request GET:/api/v1/plugins/health
 * @secure
 */
healthCheckPluginsApiV1PluginsHealthGet: (query: HealthCheckPluginsApiV1PluginsHealthGetParams, params: RequestParams = {}) =>
    this.request<HealthCheckPluginsApiV1PluginsHealthGetData, HTTPValidationError>({
        path: `/api/v1/plugins/health`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get plugin system statistics. Args: current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Plugin system statistics
 *
 * @tags Plugins
 * @name GetPluginStatsApiV1PluginsStatsGet
 * @summary Get Plugin Stats
 * @request GET:/api/v1/plugins/stats
 * @secure
 */
getPluginStatsApiV1PluginsStatsGet: (params: RequestParams = {}) =>
    this.request<GetPluginStatsApiV1PluginsStatsGetData, any>({
        path: `/api/v1/plugins/stats`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Check plugin dependencies. Args: plugin_id: Plugin ID current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Dependency check results
 *
 * @tags Plugins
 * @name CheckPluginDependenciesApiV1PluginsPluginIdDependenciesGet
 * @summary Check Plugin Dependencies
 * @request GET:/api/v1/plugins/{plugin_id}/dependencies
 * @secure
 */
checkPluginDependenciesApiV1PluginsPluginIdDependenciesGet: ({ pluginId, ...query }: CheckPluginDependenciesApiV1PluginsPluginIdDependenciesGetParams, params: RequestParams = {}) =>
    this.request<CheckPluginDependenciesApiV1PluginsPluginIdDependenciesGetData, HTTPValidationError>({
        path: `/api/v1/plugins/${pluginId}/dependencies`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Enable multiple plugins. Args: plugin_ids: List of plugin IDs to enable current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Bulk operation results
 *
 * @tags Plugins
 * @name BulkEnablePluginsApiV1PluginsBulkEnablePost
 * @summary Bulk Enable Plugins
 * @request POST:/api/v1/plugins/bulk/enable
 * @secure
 */
bulkEnablePluginsApiV1PluginsBulkEnablePost: (data: BulkEnablePluginsApiV1PluginsBulkEnablePostPayload, params: RequestParams = {}) =>
    this.request<BulkEnablePluginsApiV1PluginsBulkEnablePostData, HTTPValidationError>({
        path: `/api/v1/plugins/bulk/enable`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Disable multiple plugins. Args: plugin_ids: List of plugin IDs to disable current_user: Current authenticated user plugin_manager: Plugin manager instance Returns: Bulk operation results
 *
 * @tags Plugins
 * @name BulkDisablePluginsApiV1PluginsBulkDisablePost
 * @summary Bulk Disable Plugins
 * @request POST:/api/v1/plugins/bulk/disable
 * @secure
 */
bulkDisablePluginsApiV1PluginsBulkDisablePost: (data: BulkDisablePluginsApiV1PluginsBulkDisablePostPayload, params: RequestParams = {}) =>
    this.request<BulkDisablePluginsApiV1PluginsBulkDisablePostData, HTTPValidationError>({
        path: `/api/v1/plugins/bulk/disable`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Create a new job. Args: job_data: Job creation data current_user: Current authenticated user Returns: Created job data
 *
 * @tags Jobs
 * @name CreateJobApiV1JobsPost
 * @summary Create Job
 * @request POST:/api/v1/jobs/
 * @secure
 */
createJobApiV1JobsPost: (data: JobCreateRequest, params: RequestParams = {}) =>
    this.request<CreateJobApiV1JobsPostData, HTTPValidationError>({
        path: `/api/v1/jobs/`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List jobs with optional filtering and pagination. Args: request: List request parameters current_user: Current authenticated user Returns: List of jobs with pagination info
 *
 * @tags Jobs
 * @name ListJobsApiV1JobsGet
 * @summary List Jobs
 * @request GET:/api/v1/jobs/
 * @secure
 */
listJobsApiV1JobsGet: (query: ListJobsApiV1JobsGetParams, data: ListJobsApiV1JobsGetPayload, params: RequestParams = {}) =>
    this.request<ListJobsApiV1JobsGetData, HTTPValidationError>({
        path: `/api/v1/jobs/`,
        method: 'GET',
        query: query,        body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get job by ID. Args: job_id: Job ID current_user: Current authenticated user Returns: Job data
 *
 * @tags Jobs
 * @name GetJobApiV1JobsJobIdGet
 * @summary Get Job
 * @request GET:/api/v1/jobs/{job_id}
 * @secure
 */
getJobApiV1JobsJobIdGet: ({ jobId, ...query }: GetJobApiV1JobsJobIdGetParams, params: RequestParams = {}) =>
    this.request<GetJobApiV1JobsJobIdGetData, HTTPValidationError>({
        path: `/api/v1/jobs/${jobId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Cancel a job. Args: job_id: Job ID current_user: Current authenticated user Returns: Cancellation result
 *
 * @tags Jobs
 * @name CancelJobApiV1JobsJobIdCancelPost
 * @summary Cancel Job
 * @request POST:/api/v1/jobs/{job_id}/cancel
 * @secure
 */
cancelJobApiV1JobsJobIdCancelPost: ({ jobId, ...query }: CancelJobApiV1JobsJobIdCancelPostParams, params: RequestParams = {}) =>
    this.request<CancelJobApiV1JobsJobIdCancelPostData, HTTPValidationError>({
        path: `/api/v1/jobs/${jobId}/cancel`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get job queue statistics. Args: current_user: Current authenticated user Returns: Job statistics
 *
 * @tags Jobs
 * @name GetJobStatsApiV1JobsStatsOverviewGet
 * @summary Get Job Stats
 * @request GET:/api/v1/jobs/stats/overview
 * @secure
 */
getJobStatsApiV1JobsStatsOverviewGet: (params: RequestParams = {}) =>
    this.request<GetJobStatsApiV1JobsStatsOverviewGetData, any>({
        path: `/api/v1/jobs/stats/overview`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Clean up old completed jobs to free up memory. Note: This is a system-wide cleanup operation that affects all users. Only completed, failed, or cancelled jobs older than 24 hours are removed. Args: force: If True, remove all completed/failed jobs regardless of age current_user: Current authenticated user Returns: Cleanup statistics
 *
 * @tags Jobs
 * @name CleanupJobsApiV1JobsCleanupPost
 * @summary Cleanup Jobs
 * @request POST:/api/v1/jobs/cleanup
 * @secure
 */
cleanupJobsApiV1JobsCleanupPost: (query: CleanupJobsApiV1JobsCleanupPostParams, params: RequestParams = {}) =>
    this.request<CleanupJobsApiV1JobsCleanupPostData, HTTPValidationError>({
        path: `/api/v1/jobs/cleanup`,
        method: 'POST',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Export data in specified format.
 *
 * @tags Data Management
 * @name ExportDataApiV1DataExportPost
 * @summary Export Data
 * @request POST:/api/v1/data/export
 * @secure
 */
exportDataApiV1DataExportPost: (data: ExportDataRequest, params: RequestParams = {}) =>
    this.request<ExportDataApiV1DataExportPostData, HTTPValidationError>({
        path: `/api/v1/data/export`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Create a data backup.
 *
 * @tags Data Management
 * @name CreateBackupApiV1DataBackupPost
 * @summary Create Backup
 * @request POST:/api/v1/data/backup
 * @secure
 */
createBackupApiV1DataBackupPost: (data: BackupRequest, params: RequestParams = {}) =>
    this.request<CreateBackupApiV1DataBackupPostData, HTTPValidationError>({
        path: `/api/v1/data/backup`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List available backups.
 *
 * @tags Data Management
 * @name ListBackupsApiV1DataBackupsGet
 * @summary List Backups
 * @request GET:/api/v1/data/backups
 * @secure
 */
listBackupsApiV1DataBackupsGet: (query: ListBackupsApiV1DataBackupsGetParams, params: RequestParams = {}) =>
    this.request<ListBackupsApiV1DataBackupsGetData, HTTPValidationError>({
        path: `/api/v1/data/backups`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Restore data from a backup.
 *
 * @tags Data Management
 * @name RestoreFromBackupApiV1DataRestorePost
 * @summary Restore From Backup
 * @request POST:/api/v1/data/restore
 * @secure
 */
restoreFromBackupApiV1DataRestorePost: (data: RestoreRequest, params: RequestParams = {}) =>
    this.request<RestoreFromBackupApiV1DataRestorePostData, HTTPValidationError>({
        path: `/api/v1/data/restore`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get storage statistics and usage information.
 *
 * @tags Data Management
 * @name GetStorageStatsApiV1DataStatsGet
 * @summary Get Storage Stats
 * @request GET:/api/v1/data/stats
 * @secure
 */
getStorageStatsApiV1DataStatsGet: (params: RequestParams = {}) =>
    this.request<GetStorageStatsApiV1DataStatsGetData, any>({
        path: `/api/v1/data/stats`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Bulk delete documents.
 *
 * @tags Data Management
 * @name BulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPost
 * @summary Bulk Delete Documents
 * @request POST:/api/v1/data/bulk/delete-documents
 * @secure
 */
bulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPost: (data: BulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPostPayload, params: RequestParams = {}) =>
    this.request<BulkDeleteDocumentsApiV1DataBulkDeleteDocumentsPostData, HTTPValidationError>({
        path: `/api/v1/data/bulk/delete-documents`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Bulk delete conversations.
 *
 * @tags Data Management
 * @name BulkDeleteConversationsApiV1DataBulkDeleteConversationsPost
 * @summary Bulk Delete Conversations
 * @request POST:/api/v1/data/bulk/delete-conversations
 * @secure
 */
bulkDeleteConversationsApiV1DataBulkDeleteConversationsPost: (data: BulkDeleteConversationsApiV1DataBulkDeleteConversationsPostPayload, params: RequestParams = {}) =>
    this.request<BulkDeleteConversationsApiV1DataBulkDeleteConversationsPostData, HTTPValidationError>({
        path: `/api/v1/data/bulk/delete-conversations`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Bulk delete prompts.
 *
 * @tags Data Management
 * @name BulkDeletePromptsApiV1DataBulkDeletePromptsPost
 * @summary Bulk Delete Prompts
 * @request POST:/api/v1/data/bulk/delete-prompts
 * @secure
 */
bulkDeletePromptsApiV1DataBulkDeletePromptsPost: (data: BulkDeletePromptsApiV1DataBulkDeletePromptsPostPayload, params: RequestParams = {}) =>
    this.request<BulkDeletePromptsApiV1DataBulkDeletePromptsPostData, HTTPValidationError>({
        path: `/api/v1/data/bulk/delete-prompts`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List all providers.
 *
 * @tags Model Registry
 * @name ListProvidersApiV1ModelsProvidersGet
 * @summary List Providers
 * @request GET:/api/v1/models/providers
 * @secure
 */
listProvidersApiV1ModelsProvidersGet: (query: ListProvidersApiV1ModelsProvidersGetParams, params: RequestParams = {}) =>
    this.request<ListProvidersApiV1ModelsProvidersGetData, HTTPValidationError>({
        path: `/api/v1/models/providers`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create a new provider.
 *
 * @tags Model Registry
 * @name CreateProviderApiV1ModelsProvidersPost
 * @summary Create Provider
 * @request POST:/api/v1/models/providers
 * @secure
 */
createProviderApiV1ModelsProvidersPost: (data: ProviderCreate, params: RequestParams = {}) =>
    this.request<CreateProviderApiV1ModelsProvidersPostData, HTTPValidationError>({
        path: `/api/v1/models/providers`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get a specific provider.
 *
 * @tags Model Registry
 * @name GetProviderApiV1ModelsProvidersProviderIdGet
 * @summary Get Provider
 * @request GET:/api/v1/models/providers/{provider_id}
 * @secure
 */
getProviderApiV1ModelsProvidersProviderIdGet: ({ providerId, ...query }: GetProviderApiV1ModelsProvidersProviderIdGetParams, params: RequestParams = {}) =>
    this.request<GetProviderApiV1ModelsProvidersProviderIdGetData, HTTPValidationError>({
        path: `/api/v1/models/providers/${providerId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update a provider.
 *
 * @tags Model Registry
 * @name UpdateProviderApiV1ModelsProvidersProviderIdPut
 * @summary Update Provider
 * @request PUT:/api/v1/models/providers/{provider_id}
 * @secure
 */
updateProviderApiV1ModelsProvidersProviderIdPut: ({ providerId, ...query }: UpdateProviderApiV1ModelsProvidersProviderIdPutParams, data: ProviderUpdate, params: RequestParams = {}) =>
    this.request<UpdateProviderApiV1ModelsProvidersProviderIdPutData, HTTPValidationError>({
        path: `/api/v1/models/providers/${providerId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete a provider and all its dependent models and embedding spaces.
 *
 * @tags Model Registry
 * @name DeleteProviderApiV1ModelsProvidersProviderIdDelete
 * @summary Delete Provider
 * @request DELETE:/api/v1/models/providers/{provider_id}
 * @secure
 */
deleteProviderApiV1ModelsProvidersProviderIdDelete: ({ providerId, ...query }: DeleteProviderApiV1ModelsProvidersProviderIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteProviderApiV1ModelsProvidersProviderIdDeleteData, HTTPValidationError>({
        path: `/api/v1/models/providers/${providerId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Set a provider as default for a model type.
 *
 * @tags Model Registry
 * @name SetDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPost
 * @summary Set Default Provider
 * @request POST:/api/v1/models/providers/{provider_id}/set-default
 * @secure
 */
setDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPost: ({ providerId, ...query }: SetDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPostParams, data: DefaultProvider, params: RequestParams = {}) =>
    this.request<SetDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPostData, HTTPValidationError>({
        path: `/api/v1/models/providers/${providerId}/set-default`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description List all model definitions.
 *
 * @tags Model Registry
 * @name ListModelsApiV1ModelsModelsGet
 * @summary List Models
 * @request GET:/api/v1/models/models
 * @secure
 */
listModelsApiV1ModelsModelsGet: (query: ListModelsApiV1ModelsModelsGetParams, params: RequestParams = {}) =>
    this.request<ListModelsApiV1ModelsModelsGetData, HTTPValidationError>({
        path: `/api/v1/models/models`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create a new model definition.
 *
 * @tags Model Registry
 * @name CreateModelApiV1ModelsModelsPost
 * @summary Create Model
 * @request POST:/api/v1/models/models
 * @secure
 */
createModelApiV1ModelsModelsPost: (data: ModelDefCreate, params: RequestParams = {}) =>
    this.request<CreateModelApiV1ModelsModelsPostData, HTTPValidationError>({
        path: `/api/v1/models/models`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get a specific model definition.
 *
 * @tags Model Registry
 * @name GetModelApiV1ModelsModelsModelIdGet
 * @summary Get Model
 * @request GET:/api/v1/models/models/{model_id}
 * @secure
 */
getModelApiV1ModelsModelsModelIdGet: ({ modelId, ...query }: GetModelApiV1ModelsModelsModelIdGetParams, params: RequestParams = {}) =>
    this.request<GetModelApiV1ModelsModelsModelIdGetData, HTTPValidationError>({
        path: `/api/v1/models/models/${modelId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update a model definition.
 *
 * @tags Model Registry
 * @name UpdateModelApiV1ModelsModelsModelIdPut
 * @summary Update Model
 * @request PUT:/api/v1/models/models/{model_id}
 * @secure
 */
updateModelApiV1ModelsModelsModelIdPut: ({ modelId, ...query }: UpdateModelApiV1ModelsModelsModelIdPutParams, data: ModelDefUpdate, params: RequestParams = {}) =>
    this.request<UpdateModelApiV1ModelsModelsModelIdPutData, HTTPValidationError>({
        path: `/api/v1/models/models/${modelId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete a model definition and its dependent embedding spaces.
 *
 * @tags Model Registry
 * @name DeleteModelApiV1ModelsModelsModelIdDelete
 * @summary Delete Model
 * @request DELETE:/api/v1/models/models/{model_id}
 * @secure
 */
deleteModelApiV1ModelsModelsModelIdDelete: ({ modelId, ...query }: DeleteModelApiV1ModelsModelsModelIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteModelApiV1ModelsModelsModelIdDeleteData, HTTPValidationError>({
        path: `/api/v1/models/models/${modelId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Set a model as default for its type.
 *
 * @tags Model Registry
 * @name SetDefaultModelApiV1ModelsModelsModelIdSetDefaultPost
 * @summary Set Default Model
 * @request POST:/api/v1/models/models/{model_id}/set-default
 * @secure
 */
setDefaultModelApiV1ModelsModelsModelIdSetDefaultPost: ({ modelId, ...query }: SetDefaultModelApiV1ModelsModelsModelIdSetDefaultPostParams, params: RequestParams = {}) =>
    this.request<SetDefaultModelApiV1ModelsModelsModelIdSetDefaultPostData, HTTPValidationError>({
        path: `/api/v1/models/models/${modelId}/set-default`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description List all embedding spaces.
 *
 * @tags Model Registry
 * @name ListEmbeddingSpacesApiV1ModelsEmbeddingSpacesGet
 * @summary List Embedding Spaces
 * @request GET:/api/v1/models/embedding-spaces
 * @secure
 */
listEmbeddingSpacesApiV1ModelsEmbeddingSpacesGet: (query: ListEmbeddingSpacesApiV1ModelsEmbeddingSpacesGetParams, params: RequestParams = {}) =>
    this.request<ListEmbeddingSpacesApiV1ModelsEmbeddingSpacesGetData, HTTPValidationError>({
        path: `/api/v1/models/embedding-spaces`,
        method: 'GET',
        query: query,                secure: true,                format: "json",        ...params,
    }),            /**
 * @description Create a new embedding space with backing table and index.
 *
 * @tags Model Registry
 * @name CreateEmbeddingSpaceApiV1ModelsEmbeddingSpacesPost
 * @summary Create Embedding Space
 * @request POST:/api/v1/models/embedding-spaces
 * @secure
 */
createEmbeddingSpaceApiV1ModelsEmbeddingSpacesPost: (data: EmbeddingSpaceCreate, params: RequestParams = {}) =>
    this.request<CreateEmbeddingSpaceApiV1ModelsEmbeddingSpacesPostData, HTTPValidationError>({
        path: `/api/v1/models/embedding-spaces`,
        method: 'POST',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Get a specific embedding space.
 *
 * @tags Model Registry
 * @name GetEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGet
 * @summary Get Embedding Space
 * @request GET:/api/v1/models/embedding-spaces/{space_id}
 * @secure
 */
getEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGet: ({ spaceId, ...query }: GetEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGetParams, params: RequestParams = {}) =>
    this.request<GetEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdGetData, HTTPValidationError>({
        path: `/api/v1/models/embedding-spaces/${spaceId}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Update an embedding space.
 *
 * @tags Model Registry
 * @name UpdateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPut
 * @summary Update Embedding Space
 * @request PUT:/api/v1/models/embedding-spaces/{space_id}
 * @secure
 */
updateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPut: ({ spaceId, ...query }: UpdateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPutParams, data: EmbeddingSpaceUpdate, params: RequestParams = {}) =>
    this.request<UpdateEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdPutData, HTTPValidationError>({
        path: `/api/v1/models/embedding-spaces/${spaceId}`,
        method: 'PUT',
                body: data,        secure: true,        type: ContentType.Json,        format: "json",        ...params,
    }),            /**
 * @description Delete an embedding space (does not drop the table).
 *
 * @tags Model Registry
 * @name DeleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDelete
 * @summary Delete Embedding Space
 * @request DELETE:/api/v1/models/embedding-spaces/{space_id}
 * @secure
 */
deleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDelete: ({ spaceId, ...query }: DeleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDeleteParams, params: RequestParams = {}) =>
    this.request<DeleteEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdDeleteData, HTTPValidationError>({
        path: `/api/v1/models/embedding-spaces/${spaceId}`,
        method: 'DELETE',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Set an embedding space as default.
 *
 * @tags Model Registry
 * @name SetDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPost
 * @summary Set Default Embedding Space
 * @request POST:/api/v1/models/embedding-spaces/{space_id}/set-default
 * @secure
 */
setDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPost: ({ spaceId, ...query }: SetDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPostParams, params: RequestParams = {}) =>
    this.request<SetDefaultEmbeddingSpaceApiV1ModelsEmbeddingSpacesSpaceIdSetDefaultPostData, HTTPValidationError>({
        path: `/api/v1/models/embedding-spaces/${spaceId}/set-default`,
        method: 'POST',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get the default provider for a model type.
 *
 * @tags Model Registry
 * @name GetDefaultProviderApiV1ModelsDefaultsProviderModelTypeGet
 * @summary Get Default Provider
 * @request GET:/api/v1/models/defaults/provider/{model_type}
 * @secure
 */
getDefaultProviderApiV1ModelsDefaultsProviderModelTypeGet: ({ modelType, ...query }: GetDefaultProviderApiV1ModelsDefaultsProviderModelTypeGetParams, params: RequestParams = {}) =>
    this.request<GetDefaultProviderApiV1ModelsDefaultsProviderModelTypeGetData, HTTPValidationError>({
        path: `/api/v1/models/defaults/provider/${modelType}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get the default model for a type.
 *
 * @tags Model Registry
 * @name GetDefaultModelApiV1ModelsDefaultsModelModelTypeGet
 * @summary Get Default Model
 * @request GET:/api/v1/models/defaults/model/{model_type}
 * @secure
 */
getDefaultModelApiV1ModelsDefaultsModelModelTypeGet: ({ modelType, ...query }: GetDefaultModelApiV1ModelsDefaultsModelModelTypeGetParams, params: RequestParams = {}) =>
    this.request<GetDefaultModelApiV1ModelsDefaultsModelModelTypeGetData, HTTPValidationError>({
        path: `/api/v1/models/defaults/model/${modelType}`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),            /**
 * @description Get the default embedding space.
 *
 * @tags Model Registry
 * @name GetDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpaceGet
 * @summary Get Default Embedding Space
 * @request GET:/api/v1/models/defaults/embedding-space
 * @secure
 */
getDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpaceGet: (params: RequestParams = {}) =>
    this.request<GetDefaultEmbeddingSpaceApiV1ModelsDefaultsEmbeddingSpaceGetData, any>({
        path: `/api/v1/models/defaults/embedding-space`,
        method: 'GET',
                        secure: true,                format: "json",        ...params,
    }),    }
