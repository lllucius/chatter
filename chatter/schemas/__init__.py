"""Pydantic schemas for API request/response models."""

from chatter.schemas.auth import *
from chatter.schemas.chat import *
from chatter.schemas.document import *
from chatter.schemas.profile import *
from chatter.schemas.analytics import *

__all__ = [
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
]