"""External services integration."""

# Conditional imports to avoid dependency issues during testing
try:
    from .ab_testing import ab_test_manager
except ImportError:
    ab_test_manager = None

try:
    from .chat_refactored import RefactoredChatService
except ImportError:
    RefactoredChatService = None

try:
    from .conversation import ConversationService  
except ImportError:
    ConversationService = None

try:
    from .data_management import data_manager
except ImportError:
    data_manager = None

try:
    from .enhanced_streaming import EnhancedStreamingService, enhanced_streaming_service
except ImportError:
    EnhancedStreamingService = None
    enhanced_streaming_service = None

try:
    from .job_queue import job_queue
except ImportError:
    job_queue = None

try:
    from .mcp import mcp_service
except ImportError:
    mcp_service = None

try:
    from .message import MessageService
except ImportError:
    MessageService = None

try:
    from .plugins import plugin_manager
except ImportError:
    plugin_manager = None

try:
    from .sse_events import sse_service
except ImportError:
    sse_service = None

try:
    from .workflow_execution import WorkflowExecutionService
except ImportError:
    WorkflowExecutionService = None

__all__ = [
    "ab_test_manager",
    "ConversationService",
    "data_manager",
    "enhanced_streaming_service",
    "EnhancedStreamingService",
    "job_queue",
    "mcp_service",
    "MessageService", 
    "plugin_manager",
    "RefactoredChatService",
    "sse_service",
    "WorkflowExecutionService",
]
