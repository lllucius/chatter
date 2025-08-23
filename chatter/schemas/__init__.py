"""Pydantic schemas for API request/response models."""

from chatter.schemas.analytics import *
from chatter.schemas.auth import *
from chatter.schemas.chat import *
from chatter.schemas.common import *
from chatter.schemas.document import *
from chatter.schemas.profile import *
from chatter.schemas.prompt import *
from chatter.schemas.toolserver import *

__all__ = [
    # Common schemas
    "PaginationRequest",
    "SortingRequest",
    "PaginatedRequest",
    "ListRequestBase",
    "GetRequestBase",
    "DeleteRequestBase",

    # Auth schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    "TokenRefresh",
    "PasswordChange",
    "PasswordReset",
    "PasswordResetConfirm",
    "EmailVerification",
    "APIKeyCreate",
    "APIKeyResponse",

    # Chat schemas
    "MessageBase",
    "MessageCreate",
    "MessageResponse",
    "ConversationBase",
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationResponse",
    "ConversationWithMessages",
    "ChatRequest",
    "ChatResponse",
    "StreamingChatChunk",
    "ConversationSearchRequest",
    "ConversationSearchResponse",
    "ConversationGetRequest",
    "ConversationDeleteRequest",
    "ConversationMessagesRequest",
    "AvailableToolsRequest",
    "McpStatusRequest",

    # Document schemas
    "DocumentBase",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentSearchRequest",
    "DocumentSearchResult",
    "DocumentSearchResponse",
    "DocumentListRequest",
    "DocumentListResponse",
    "DocumentChunkResponse",
    "DocumentProcessingRequest",
    "DocumentProcessingResponse",
    "DocumentStatsResponse",
    "DocumentGetRequest",
    "DocumentDeleteRequest",
    "DocumentStatsRequest",

    # Profile schemas
    "ProfileBase",
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    "ProfileListRequest",
    "ProfileListResponse",
    "ProfileStatsResponse",
    "ProfileTestRequest",
    "ProfileTestResponse",
    "ProfileCloneRequest",
    "ProfileImportRequest",
    "ProfileExportResponse",
    "ProfileGetRequest",
    "ProfileDeleteRequest",
    "ProfileStatsRequest",
    "ProfileProvidersRequest",

    # Prompt schemas
    "PromptBase",
    "PromptCreate",
    "PromptUpdate",
    "PromptResponse",
    "PromptListRequest",
    "PromptListResponse",
    "PromptStatsResponse",
    "PromptTestRequest",
    "PromptTestResponse",
    "PromptCloneRequest",
    "PromptGetRequest",
    "PromptDeleteRequest",
    "PromptStatsRequest",

    # Analytics schemas
    "ConversationStatsResponse",
    "UsageMetricsResponse",
    "PerformanceMetricsResponse",
    "DocumentAnalyticsResponse",
    "PromptAnalyticsResponse",
    "ProfileAnalyticsResponse",
    "SystemAnalyticsResponse",
    "AnalyticsTimeRange",
    "AnalyticsExportRequest",
    "AnalyticsExportResponse",
    "DashboardResponse",
    "ConversationStatsRequest",
    "UsageMetricsRequest",
    "PerformanceMetricsRequest",
    "DocumentAnalyticsRequest",
    "SystemAnalyticsRequest",
    "DashboardRequest",
    "ToolServerAnalyticsRequest",

    # Tool server schemas
    "ToolServerBase",
    "ToolServerCreate",
    "ToolServerUpdate",
    "ToolServerResponse",
    "ToolServerStatusUpdate",
    "ServerToolBase",
    "ServerToolUpdate",
    "ServerToolResponse",
    "ToolUsageCreate",
    "ToolUsageResponse",
    "ToolServerMetrics",
    "ToolMetrics",
    "ToolServerAnalytics",
    "ToolServerHealthCheck",
    "BulkToolServerOperation",
    "BulkOperationResult",
]
